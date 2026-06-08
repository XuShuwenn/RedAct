#!/usr/bin/env python3
"""Standalone trajectory rewriting script (Step 2, independent of extraction).

Reads trajectories from:
    {traj-root}/conversations/{task_name}__{uid}.json

Reads key_info.txt from:
    data/extra_data/{task_name}/key_info.txt

Writes rewritten trajectories to:
    {output-root}/rewritten_conversations/{task_name}__{uid}.json

Run extract_key_information.py first to pre-generate key_info.txt files,
then run this script independently (key_info.txt is maintained by human experts).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_ROOT = PROJECT_ROOT / "data" / "tasks"
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from antiskill.src.core.trajectory_rewriter import TrajectoryRewriter
from antiskill.src.core.llm_client import LLMClient
from antiskill.src.prompts import GENERIC_REWRITER_PROMPT


logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rewrite trajectories using pre-extracted key_info.txt. "
        "Step 2: runs independently after key_info extraction/editing."
    )
    parser.add_argument(
        "--traj-root",
        type=Path,
        default=PROJECT_ROOT / "test_trajectory",
        help="Root directory containing 'conversations/' subdir. "
        "Default: test_trajectory/",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "test_trajectory",
        help="Output root directory. Default: test_trajectory/",
    )
    parser.add_argument(
        "--key-info-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "extra_data",
        help="Root directory containing key_info.txt per task. "
        "Default: data/extra_data/",
    )
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        help="Task name to process (without __uid suffix). Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--task-list",
        nargs="+",
        help="Task names passed directly, or text files containing task names. "
        "Supports repeated values, comma-separated values, and file paths.",
    )
    parser.add_argument(
        "--traj-extension",
        default="json",
        help="Trajectory file extension. Default: json",
    )
    parser.add_argument(
        "--user-truncate-tokens",
        type=int,
        default=500,
        help="Max tokens for truncating user messages. Default: 500",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5",
        help="LLM model name. Default: gpt-5",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LLM temperature. Default: 0.0",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="LLM max tokens. Default: 4096",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="LLM request timeout in seconds. Default: 120",
    )
    parser.add_argument(
        "--max-assistant-per-batch",
        type=int,
        default=5,
        help="Max assistant turns per LLM call. Default: 5",
    )
    parser.add_argument(
        "--rewrite-mode",
        choices=["key_info", "generic"],
        default="key_info",
        help="Rewrite mode. key_info uses task key_info.txt; generic ignores key_info and uses a generic rewriting prompt.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit on planned rewrite items after filtering. Default: 0 means no limit.",
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        default=None,
        help="Read trajectories from a single JSON file (raw_trajectory_2k.json format) "
        "instead of scanning traj-root directory structure. "
        "domain/task_name are read from metadata.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers for rewriting. Default: 1 (sequential).",
    )
    parser.add_argument(
        "--skip-longest-fraction",
        type=float,
        default=0.0,
        help="Skip the longest fraction of planned trajectories by source JSON length before rewriting. "
        "For example, 0.1 skips the longest 10%% of this run's remaining work. Default: 0.0",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned work without calling the LLM.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def parse_task_names(values: list[str] | None) -> list[str]:
    if not values:
        return []
    names: list[str] = []
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if item:
                names.append(item)
    return names


def read_task_list(values: list[str] | None) -> list[str]:
    if not values:
        return []
    names: list[str] = []
    for value in values:
        candidate_path = Path(value)
        if candidate_path.exists() and candidate_path.is_file():
            for line in candidate_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                names.extend(parse_task_names([line]))
            continue
        names.extend(parse_task_names([value]))
    return names


def _match_task_name(embedded_name: str, known_tasks: list[str]) -> str | None:
    """Match an embedded (possibly truncated) task name to a known task name.
    Returns the actual task name or None."""
    # Try exact match first
    if embedded_name in known_tasks:
        return embedded_name

    # Try to find a known task that starts with the embedded_name
    # (handles truncated names like "azure-bgp-oscillation-route-le" -> "azure-bgp-oscillation-route-leak")
    for known in sorted(known_tasks, key=len, reverse=True):
        if known.startswith(embedded_name):
            return known

    return None


def discover_trajectory_files(
    traj_root: Path,
    tasks: list[str],
    extension: str,
    key_info_root: Path,
) -> list[tuple[Path, str, str]]:
    """Find all trajectory files for given task names.
    Returns list of (file_path, task_name, uid).
    task_name is the short name (without __uid).

    Trajectories are expected in: {traj_root}/{domain}/{task_name}/{filename}.json
    Supports both standard ({task_name}__{uid}.json) and claude-code (claude-code-claude-{model}-skills-{task_name}-{uid}.json) formats.
    """
    if not traj_root.exists():
        return []

    # Build known task list from key_info_root for truncated name matching
    known_tasks = [d.name for d in key_info_root.iterdir() if d.is_dir()]

    files: list[tuple[Path, str, str]] = []

    # Walk domain/task_name subdirectories
    for domain_dir in sorted(traj_root.iterdir()):
        if not domain_dir.is_dir():
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            task_from_dir = task_dir.name  # This is the ground-truth task_name from directory structure

            for traj_file in sorted(task_dir.glob(f"*.{extension}")):
                stem = traj_file.stem

                if "__" in stem:
                    # Standard format: use directory name as task_name (ground truth)
                    file_task_name, uid = stem.split("__", 1)
                else:
                    # Claude-code format: need to parse and match
                    # Extract embedded name and uid from filename
                    prefix = "claude-code-claude-"
                    if not stem.startswith(prefix):
                        # Unknown format, skip
                        continue
                    remainder = stem[len(prefix):]
                    skills_idx = remainder.find("-skills-")
                    if skills_idx == -1:
                        continue
                    after_model = remainder[skills_idx + len("-skills-"):]
                    parts = after_model.rsplit("-", 1)
                    if len(parts) != 2:
                        continue
                    embedded_name, uid = parts

                    # Match to known task (handles truncation)
                    matched = _match_task_name(embedded_name, known_tasks)
                    if matched:
                        file_task_name = matched
                    else:
                        # Fallback: use directory name as ground truth
                        file_task_name = task_from_dir

                if tasks and file_task_name not in tasks:
                    continue
                # Preserve relative domain structure for output
                domain_name = domain_dir.name
                files.append((traj_file, file_task_name, uid, domain_name))

    return files


def discover_trajectory_files_from_json(
    input_file: Path,
    tasks: list[str],
) -> list[tuple[Path, str, str, str, dict]]:
    """Read trajectories from a single JSON file (raw_trajectory_2k.json format).

    Returns list of (traj_file, task_name, uid, domain, trajectory_dict).
    The Path is a virtual path (used only for naming).
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    files: list[tuple[Path, str, str, str, dict]] = []
    seen_keys: set[tuple[str, str]] = set()
    for idx, traj in enumerate(data):
        meta = traj.get("metadata", {})
        task_name = meta.get("task_name")
        domain = meta.get("domain", "unknown")
        if not task_name:
            continue
        if tasks and task_name not in tasks:
            continue
        uid = meta.get("task_run_id", f"uid{idx}")
        # task_run_id may be "task_name__uid" or "task_name__task_name__uid"
        # take only the last segment after rsplit
        uid = uid.rsplit("__", 1)[-1]

        # Deduplicate: only keep first occurrence per (task_name, uid)
        key = (task_name, uid)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        filename = f"{task_name}__{uid}.json"
        files.append((Path(filename), task_name, uid, domain, traj))
    return files


def should_skip_existing_output(out_file: Path, output_root: Path) -> bool:
    """Skip only trajectories that were already rewritten successfully.

    Files with status "rewrite_failed" are retried on rerun. Invalid or
    status-less output files are also retried and overwritten.
    """
    if not out_file.exists() or out_file.stat().st_size == 0:
        return False

    rel_path = out_file.relative_to(output_root)
    try:
        existing = json.loads(out_file.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("  [retry] %s (existing output unreadable: %s)", rel_path, e)
        return False

    status = existing.get("status")
    if status == "rewritten":
        logger.info("  [skip] %s (status=rewritten)", rel_path)
        return True

    if status == "rewrite_failed":
        logger.info("  [retry] %s (status=rewrite_failed)", rel_path)
        return False

    logger.info("  [retry] %s (status=%s)", rel_path, status)
    return False


def plan_rewrite_work(
    traj_files: list[tuple[Path, str, str, str]],
    output_root: Path,
    key_info_root: Path,
    require_key_info: bool,
) -> tuple[list[tuple[Path, str, str, Path]], dict[str, int]]:
    """Build the rewrite worklist before making any LLM calls."""
    work_items: list[tuple[Path, str, str, Path]] = []
    stats = {
        "already_rewritten": 0,
        "missing_key_info": 0,
        "empty_key_info": 0,
        "missing_instruction": 0,
    }

    for traj_file, task_name, uid, domain in traj_files:
        out_dir = output_root / domain / task_name
        out_file = out_dir / traj_file.name
        if should_skip_existing_output(out_file, output_root):
            stats["already_rewritten"] += 1
            continue

        if require_key_info:
            ki_file = key_info_root / task_name / "key_info.txt"
            if not ki_file.exists():
                stats["missing_key_info"] += 1
                continue
            if not ki_file.read_text(encoding="utf-8").strip():
                stats["empty_key_info"] += 1
                continue

        instr_file = TASKS_ROOT / task_name / "instruction.md"
        if not instr_file.exists():
            stats["missing_instruction"] += 1
            continue

        work_items.append((traj_file, task_name, domain, out_file))

    return work_items, stats


def plan_rewrite_work_from_json(
    traj_items: list[tuple[Path, str, str, str, dict]],
    output_root: Path,
    key_info_root: Path,
    require_key_info: bool,
) -> tuple[list[tuple[Path, str, str, Path, dict]], dict[str, int]]:
    """Build worklist from JSON-loaded trajectories."""
    work_items: list[tuple[Path, str, str, Path, dict]] = []
    stats = {
        "already_rewritten": 0,
        "missing_key_info": 0,
        "empty_key_info": 0,
        "missing_instruction": 0,
    }

    for traj_file, task_name, uid, domain, traj_dict in traj_items:
        out_dir = output_root / domain / task_name
        out_file = out_dir / traj_file.name
        if should_skip_existing_output(out_file, output_root):
            stats["already_rewritten"] += 1
            continue

        if require_key_info:
            ki_file = key_info_root / task_name / "key_info.txt"
            if not ki_file.exists():
                stats["missing_key_info"] += 1
                continue
            if not ki_file.read_text(encoding="utf-8").strip():
                stats["empty_key_info"] += 1
                continue

        instr_file = TASKS_ROOT / task_name / "instruction.md"
        if not instr_file.exists():
            stats["missing_instruction"] += 1
            continue

        work_items.append((traj_file, task_name, domain, out_file, traj_dict))

    return work_items, stats


def _process_single_work_item(
    item: tuple,
    input_json_mode: bool,
    key_info_root: Path,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    user_truncate_tokens: int,
    max_assistant_per_batch: int,
    rewrite_mode: str,
) -> tuple[str, str, str, bool, str]:
    """Process a single work item. Returns (domain, task_name, out_file_str, success, error_msg).

    Each worker creates its own LLMClient to avoid thread-safety issues.
    """
    if input_json_mode:
        traj_file, task_name, domain, out_file_str, trajectory = item
        out_file = Path(out_file_str)
    else:
        traj_file, task_name, domain, out_file_str = item[:4]
        out_file = Path(out_file_str)
        try:
            with open(traj_file, "r", encoding="utf-8") as f:
                trajectory = json.load(f)
        except Exception as e:
            return domain, task_name, out_file_str, False, f"read failed: {e}"

    if rewrite_mode == "key_info":
        ki_file = key_info_root / task_name / "key_info.txt"
        key_info_content = ki_file.read_text(encoding="utf-8").strip()
        prompt_template = None
    else:
        key_info_content = ""
        prompt_template = GENERIC_REWRITER_PROMPT

    instr_file = TASKS_ROOT / task_name / "instruction.md"
    instruction = instr_file.read_text(encoding="utf-8")

    # Each worker gets its own LLMClient to avoid race conditions
    llm_client = LLMClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    rewriter = TrajectoryRewriter(
        llm_client=llm_client,
        user_truncate_tokens=user_truncate_tokens,
        max_assistant_per_batch=max_assistant_per_batch,
        prompt_template=prompt_template,
    )

    try:
        rewritten = rewriter.rewrite(
            trajectory=trajectory,
            instruction=instruction,
            key_info_list=[key_info_content],
        )
    except Exception as e:
        return domain, task_name, out_file_str, False, f"rewrite failed: {e}"

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(rewritten, f, ensure_ascii=False, indent=2)

    return domain, task_name, out_file_str, True, ""


def _source_length_for_work_item(item: tuple, input_json_mode: bool) -> int:
    """Return an approximate source trajectory length for long-tail filtering.

    We use serialized JSON characters instead of model-specific tokens so the
    filter stays lightweight and works before any tokenizer/model dependency is
    loaded. This is enough to remove the slowest long-context tail.
    """
    if input_json_mode:
        trajectory = item[4]
        return len(json.dumps(trajectory, ensure_ascii=False))

    traj_file = item[0]
    try:
        return traj_file.stat().st_size
    except OSError:
        return 0


def filter_longest_work_items(
    work_items: list[tuple],
    skip_fraction: float,
    input_json_mode: bool,
) -> tuple[list[tuple], list[tuple]]:
    """Drop the longest fraction of planned work items by source length."""
    if skip_fraction <= 0:
        return work_items, []
    if skip_fraction >= 1:
        raise ValueError("--skip-longest-fraction must be smaller than 1.0")
    if not work_items:
        return work_items, []

    ranked = sorted(
        ((item, _source_length_for_work_item(item, input_json_mode)) for item in work_items),
        key=lambda pair: pair[1],
        reverse=True,
    )
    skip_count = int(len(ranked) * skip_fraction)
    if skip_count <= 0:
        return work_items, []

    skipped_ids = {id(item) for item, _length in ranked[:skip_count]}
    filtered = [item for item in work_items if id(item) not in skipped_ids]
    skipped = [item for item, _length in ranked[:skip_count]]
    return filtered, skipped


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    traj_root = args.traj_root.resolve()
    output_root = args.output_root.resolve()
    key_info_root = args.key_info_root.resolve()
    require_key_info = args.rewrite_mode == "key_info"

    requested_tasks = parse_task_names(args.tasks) + read_task_list(args.task_list)

    if args.input_json:
        input_file = args.input_json.resolve()
        logger.info("Reading trajectories from JSON: %s", input_file)
        traj_items = discover_trajectory_files_from_json(input_file, requested_tasks)
        logger.info("Trajectory items found: %d", len(traj_items))
        work_items, plan_stats = plan_rewrite_work_from_json(traj_items, output_root, key_info_root, require_key_info)
        logger.info("Traj root: %s", input_file)
    else:
        if not requested_tasks:
            # Auto-discover all tasks that have trajectories by scanning the directory structure
            discovered_tasks: set[str] = set()
            for domain_dir in sorted(traj_root.iterdir()):
                if not domain_dir.is_dir():
                    continue
                for task_dir in sorted(domain_dir.iterdir()):
                    if task_dir.is_dir():
                        discovered_tasks.add(task_dir.name)
            requested_tasks = sorted(discovered_tasks)
            logger.info("No tasks specified, auto-discovered %d tasks from trajectories", len(requested_tasks))

        traj_files = discover_trajectory_files(traj_root, requested_tasks, args.traj_extension, key_info_root)
        logger.info("Trajectory files found: %d", len(traj_files))
        logger.info("Traj root: %s", traj_root)
        work_items, plan_stats = plan_rewrite_work(traj_files, output_root, key_info_root, require_key_info)
    logger.info("Output root: %s", output_root)
    logger.info("Rewrite mode: %s", args.rewrite_mode)
    logger.info("Key info root: %s", key_info_root)
    work_items, skipped_longest = filter_longest_work_items(
        work_items,
        args.skip_longest_fraction,
        input_json_mode=args.input_json is not None,
    )
    if args.limit:
        work_items = work_items[: args.limit]
    logger.info("Planned rewrites this run: %d", len(work_items))
    if skipped_longest:
        logger.info(
            "Skipped longest %.1f%% of planned trajectories: %d",
            args.skip_longest_fraction * 100,
            len(skipped_longest),
        )
    logger.info("Skipped already rewritten: %d", plan_stats["already_rewritten"])
    if plan_stats["missing_key_info"]:
        logger.info("Skipped missing key_info.txt: %d", plan_stats["missing_key_info"])
    if plan_stats["empty_key_info"]:
        logger.info("Skipped empty key_info.txt: %d", plan_stats["empty_key_info"])
    if plan_stats["missing_instruction"]:
        logger.info("Skipped missing instruction.md: %d", plan_stats["missing_instruction"])

    if args.dry_run:
        for item in work_items:
            traj_file, task, domain, out_file = item[:4]
            if require_key_info:
                ki_file = key_info_root / task / "key_info.txt"
                ki_status = "exists" if ki_file.exists() else "MISSING"
            else:
                ki_status = "not required"
            logger.info("  [dry-run] %s -> %s (key_info: %s)", traj_file.name, task, ki_status)
        return 0

    workers = args.workers
    logger.info("Using %d parallel workers", workers)

    success = 0
    failed = 0
    lock = Lock()

    def log_progress(done, total):
        logger.info("  progress: %d/%d done", done, total)

    if workers == 1:
        # Sequential path: reuse single rewriter
        llm_client = LLMClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
        )
        rewriter = TrajectoryRewriter(
            llm_client=llm_client,
            user_truncate_tokens=args.user_truncate_tokens,
            max_assistant_per_batch=args.max_assistant_per_batch,
            prompt_template=GENERIC_REWRITER_PROMPT if args.rewrite_mode == "generic" else None,
        )
        for idx, item in enumerate(work_items, 1):
            if args.input_json:
                traj_file, task_name, domain, out_file_str, trajectory = item
                out_file = Path(out_file_str)
            else:
                traj_file, task_name, domain, out_file_str = item[:4]
                out_file = Path(out_file_str)
                try:
                    with open(traj_file, "r", encoding="utf-8") as f:
                        trajectory = json.load(f)
                except Exception as e:
                    logger.error("Failed to read %s: %s", traj_file, e)
                    failed += 1
                    continue

            if args.rewrite_mode == "key_info":
                ki_file = key_info_root / task_name / "key_info.txt"
                key_info_content = ki_file.read_text(encoding="utf-8").strip()
                prompt_template = None
            else:
                key_info_content = ""
                prompt_template = GENERIC_REWRITER_PROMPT
            instr_file = TASKS_ROOT / task_name / "instruction.md"
            instruction = instr_file.read_text(encoding="utf-8")

            try:
                rewritten = rewriter.rewrite(
                    trajectory=trajectory,
                    instruction=instruction,
                    key_info_list=[key_info_content],
                )
            except Exception as e:
                logger.error("Rewrite failed for %s: %s", task_name, e)
                failed += 1
                continue

            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(rewritten, f, ensure_ascii=False, indent=2)

            logger.info("  -> %s", out_file.relative_to(output_root))
            success += 1
            if idx % 50 == 0 or idx == len(work_items):
                logger.info("  progress: %d/%d done", idx, len(work_items))
    else:
        total = len(work_items)
        completed = [0]

        def worker_wrapper(item):
            return _process_single_work_item(
                item,
                input_json_mode=args.input_json is not None,
                key_info_root=key_info_root,
                model=args.model,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
                user_truncate_tokens=args.user_truncate_tokens,
                max_assistant_per_batch=args.max_assistant_per_batch,
                rewrite_mode=args.rewrite_mode,
            )

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(worker_wrapper, item): item for item in work_items}
            for future in as_completed(futures):
                domain, task_name, out_file_str, ok, err = future.result()
                with lock:
                    completed[0] += 1
                    done = completed[0]
                    if ok:
                        success += 1
                        logger.info("  -> %s", out_file_str)
                    else:
                        failed += 1
                        logger.error("  [FAIL] %s: %s", out_file_str, err)
                    if done % 50 == 0 or done == total:
                        logger.info("  progress: %d/%d done", done, total)

    logger.info("Done. success=%d failed=%d", success, failed)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
