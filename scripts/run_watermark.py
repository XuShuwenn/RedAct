#!/usr/bin/env python3
"""Run watermarking on rewritten trajectories with trigger injection."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Best-effort .env loading; sourced shell vars (for example from .envrc)
# continue to work as usual.
load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from antiskill.src.core.watermarker import (
    ALL_WATERMARKS,
    WatermarkRegistry,
    TriggerHandler,
    WATERMARK_TRIGGERS,
)
from antiskill.src.core.llm_client import LLMClient


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_INPUT_ROOT = PROJECT_ROOT / "trajectory" / "conversations-rewritten"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "trajectory" / "conversations-watermarked"


def _parse_values(values: list[str] | None) -> list[str]:
    items: list[str] = []
    for value in values or []:
        for piece in value.split(","):
            piece = piece.strip()
            if piece:
                items.append(piece)
    return items


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def discover_task_dirs(
    input_root: Path,
    task_dir: Path | None,
    domains: list[str],
    tasks: list[str],
) -> list[tuple[Path, str, str]]:
    """Discover task directories under the rewritten-trajectory root."""
    if task_dir is not None:
        resolved = task_dir.resolve()
        if not resolved.is_dir():
            raise FileNotFoundError(f"Task directory not found: {resolved}")
        return [(resolved, resolved.parent.name, resolved.name)]

    if not input_root.exists():
        return []

    domain_filters = set(domains)
    task_filters = set(tasks)
    discovered: list[tuple[Path, str, str]] = []

    for domain_dir in sorted(path for path in input_root.iterdir() if path.is_dir()):
        if domain_filters and domain_dir.name not in domain_filters:
            continue

        for candidate_task_dir in sorted(path for path in domain_dir.iterdir() if path.is_dir()):
            if task_filters and candidate_task_dir.name not in task_filters:
                continue
            discovered.append((candidate_task_dir, domain_dir.name, candidate_task_dir.name))

    return discovered


def discover_trajectory_files(task_dirs: list[tuple[Path, str, str]]) -> list[tuple[Path, str, str]]:
    """Collect all trajectory files from discovered task directories."""
    traj_files: list[tuple[Path, str, str]] = []
    for task_dir, domain, task_name in task_dirs:
        files = sorted(task_dir.glob("*.json"))
        if not files:
            logger.warning("No trajectory files found in %s", task_dir)
            continue
        traj_files.extend((traj_file, domain, task_name) for traj_file in files)
    return traj_files


def process_file_with_trigger(
    traj_file: Path,
    domain: str,
    task_name: str,
    watermark,
    trigger_handler: TriggerHandler,
    input_root: Path,
    output_root: Path,
) -> tuple[str, bool]:
    """Process a single trajectory file with trigger injection.

    Logic: check() first → if pass, decide trigger → if trigger + inject success, watermarked=True
    If check fails → watermarked=False immediately (no trigger consumed)

    Returns:
        Tuple of (status, was_watermarked)
    """
    rel_input = _display_path(traj_file, input_root)

    try:
        trajectory = json.loads(traj_file.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("  [ERROR] Failed to read %s: %s", rel_input, exc)
        return "failed", False

    # Step 1: check eligibility BEFORE trigger decision
    if not watermark.check(trajectory, task_name=task_name):
        logger.debug("  [SKIP] %s (%s - check returned False)", rel_input, watermark.name)
        out_trajectory = {**trajectory, "watermarked": False}
        out_file = output_root / watermark.name / domain / task_name / traj_file.name
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(out_trajectory, ensure_ascii=False, indent=2), encoding="utf-8")
        return "written", False

    # Step 2: eligible — decide whether to receive trigger
    has_trigger = trigger_handler.should_insert_trigger()
    processed_trajectory = trajectory
    if has_trigger:
        # Inject trigger into first user message
        processed_trajectory = trigger_handler.process_trajectory(
            trajectory, watermark.name, add_trigger=True
        )

    # Step 3: inject watermark only if trigger was added
    was_watermarked = False
    out_trajectory = processed_trajectory

    if has_trigger:
        try:
            watermarked = watermark.inject(processed_trajectory, task_name=task_name)
            if hasattr(watermark, "detect") and watermark.detect(watermarked, task_name=task_name):
                logger.debug("  [VERIFY] %s - watermark detected successfully", rel_input)
                was_watermarked = True
                out_trajectory = watermarked
            elif hasattr(watermark, "detect"):
                logger.warning("  [WARN] %s - watermark injection not detected", rel_input)
        except Exception as exc:
            logger.error("  [ERROR] Failed to apply %s to %s: %s", watermark.name, rel_input, exc)

    out_trajectory = {**out_trajectory, "watermarked": was_watermarked}
    out_file = output_root / watermark.name / domain / task_name / traj_file.name
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(out_trajectory, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.debug("  -> %s (watermarked=%s)", _display_path(out_file, output_root), was_watermarked)
    return "written", was_watermarked


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run watermarking on rewritten trajectories with trigger injection")
    parser.add_argument(
        "watermark",
        nargs="?",
        default="all",
        help="Watermark name (ritual_marker, env_check, cross_check, error_anchoring, or 'all')",
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        default=DEFAULT_INPUT_ROOT,
        help=f"Root directory containing domain/task rewritten trajectories. Default: {DEFAULT_INPUT_ROOT}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Root directory for watermarked outputs. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--task-dir",
        type=Path,
        help="Optional explicit task directory, e.g. trajectory/conversations-rewritten/<domain>/<task_name>",
    )
    parser.add_argument(
        "--domain",
        action="append",
        help="Optional domain filter. Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--task",
        action="append",
        help="Optional task-name filter. Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--ritual-checkpoints",
        action="store_true",
        help="Enable '=== Progress Checkpoint k ===' markers for the ritual_marker watermark.",
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=0.5,
        help="Proportion of trajectories to receive triggers and watermarks (0.0 to 1.0). Default: 0.5",
    )
    parser.add_argument(
        "--no-trigger",
        action="store_true",
        help="Skip trigger injection (for testing watermark injection only).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible trigger sampling. Default: none (random).",
    )
    parser.add_argument(
        "--cross-check-count",
        type=int,
        default=2,
        help="Maximum number of cross_check injections per trajectory. Default: 2.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model name for watermarks that require LLM generation (e.g. error_anchoring). Default: from config.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="LLM base URL for watermarks that require LLM generation. Default: from config.",
    )
    return parser


def build_watermarks(args) -> list:
    """Instantiate requested watermarks with any watermark-specific options."""
    llm_client = None
    if args.model is not None:
        llm_client = LLMClient(model=args.model, base_url=args.base_url)

    if args.watermark == "all":
        watermarks = []
        for cls in ALL_WATERMARKS:
            if cls.__name__ == "TaskStartRitualWatermark":
                watermarks.append(cls(enable_checkpoints=args.ritual_checkpoints))
            elif cls.__name__ == "CrossCheckWatermark":
                watermarks.append(cls(
                    llm_client=llm_client or LLMClient.from_config(),
                    max_checks=args.cross_check_count,
                ))
            elif cls.__name__ == "ErrorAnchoringWatermark":
                watermarks.append(cls(llm_client=llm_client or LLMClient.from_config()))
            else:
                watermarks.append(cls())
        return watermarks

    if args.watermark == "ritual_marker":
        return [WatermarkRegistry.create(args.watermark, enable_checkpoints=args.ritual_checkpoints)]

    if args.watermark == "cross_check":
        return [WatermarkRegistry.create(args.watermark,
            llm_client=llm_client or LLMClient.from_config(),
            max_checks=args.cross_check_count)]

    if args.watermark == "error_anchoring":
        return [WatermarkRegistry.create(args.watermark,
            llm_client=llm_client or LLMClient.from_config())]

    return [WatermarkRegistry.create(args.watermark)]


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not 0.0 <= args.frequency <= 1.0:
        logger.error("Frequency must be between 0.0 and 1.0, got %s", args.frequency)
        return 1

    # Set random seed if provided
    if args.seed is not None:
        import random
        random.seed(args.seed)

    input_root = args.input_root.resolve()
    output_root = args.output_root.resolve()
    task_dir = args.task_dir.resolve() if args.task_dir else None
    domains = _parse_values(args.domain)
    tasks = _parse_values(args.task)

    try:
        task_dirs = discover_task_dirs(input_root, task_dir, domains, tasks)
    except FileNotFoundError as exc:
        logger.error(str(exc))
        return 1

    traj_files = discover_trajectory_files(task_dirs)
    if not traj_files:
        logger.error("No trajectory files found under %s", task_dir or input_root)
        return 1

    logger.info("Found %d trajectory files", len(traj_files))
    logger.info("Input root: %s", input_root)
    logger.info("Output root: %s", output_root)
    logger.info("Trigger frequency: %s", args.frequency)
    if args.no_trigger:
        logger.info("Trigger injection: DISABLED (watermark injection only)")

    try:
        watermarks = build_watermarks(args)
    except KeyError as exc:
        logger.error(str(exc))
        return 1

    overall_failed = 0
    overall_skipped = 0

    for watermark in watermarks:
        logger.info("\n%s", "=" * 60)
        logger.info("Watermark: %s - %s", watermark.name, watermark.description)
        logger.info("Trigger: %s", WATERMARK_TRIGGERS.get(watermark.name, "N/A"))
        logger.info("%s", "=" * 60)

        written = 0
        skipped = 0
        failed = 0
        watermarked_count = 0

        # ── Resume / checkpoint logic ─────────────────────────────────────────
        watermark_output_dir = output_root / watermark.name
        already_done: set[str] = set()
        existing_wm_count = 0

        if watermark_output_dir.exists():
            for fp in watermark_output_dir.rglob("*.json"):
                try:
                    data = json.loads(fp.read_text(encoding="utf-8"))
                    if data.get("watermarked") is True:
                        rel = str(fp.relative_to(watermark_output_dir))
                        already_done.add(rel)
                        existing_wm_count += 1
                except Exception:
                    pass

        logger.info(
            "Output directory: %s  existing watermarked=%d  total=%d",
            watermark_output_dir,
            existing_wm_count,
            len(traj_files),
        )

        if existing_wm_count > 0:
            logger.info(
                "  [RESUME] %d files already watermarked — will not re-process them.",
                existing_wm_count,
            )

        # ── Step 1: count eligible files (pass check) among non-done files ───
        eligible_files: list[tuple[Path, str, str]] = []
        eligible_count = 0

        for traj_file, domain, task_name in traj_files:
            out_file = output_root / watermark.name / domain / task_name / traj_file.name
            rel_path = str(out_file.relative_to(output_root / watermark.name))
            if rel_path in already_done:
                continue
            try:
                trajectory = json.loads(traj_file.read_text(encoding="utf-8"))
                if watermark.check(trajectory, task_name=task_name):
                    eligible_count += 1
                    eligible_files.append((traj_file, domain, task_name))
            except Exception:
                pass

        total_files = len(traj_files)
        target_wm_count = int(args.frequency * total_files) if total_files > 0 else 0
        remaining_target = max(0, target_wm_count - existing_wm_count)

        logger.info(
            "  [ELIGIBLE] %d files pass check() out of %d non-done files; target new watermarked=%d",
            eligible_count,
            len(traj_files) - existing_wm_count,
            remaining_target,
        )

        if remaining_target > 0 and eligible_files:
            logger.info(
                "  [QUOTA] Will assign triggers to exactly %d of %d eligible files.",
                remaining_target,
                eligible_count,
            )

        # ── Step 2: set quota on trigger handler ──────────────────────────────
        trigger_handler = TriggerHandler(frequency=args.frequency)
        if remaining_target > 0 and eligible_count > 0:
            trigger_handler.set_quota(eligible_count, remaining_target)

        # ── Step 3: process only non-done files ──────────────────────────────
        # eligible_files already excludes already_done
        for traj_file, domain, task_name in eligible_files:
            rel_input = _display_path(traj_file, input_root)
            logger.debug("  Processing: %s", rel_input)

            if args.no_trigger:
                try:
                    trajectory = json.loads(traj_file.read_text(encoding="utf-8"))
                    watermarked = watermark.inject(trajectory, task_name=task_name)
                    out_trajectory = {**watermarked, "watermarked": True}
                    out_file = output_root / watermark.name / domain / task_name / traj_file.name
                    out_file.parent.mkdir(parents=True, exist_ok=True)
                    out_file.write_text(json.dumps(out_trajectory, ensure_ascii=False, indent=2), encoding="utf-8")
                    logger.info("  -> %s", _display_path(out_file, output_root))
                    written += 1
                    watermarked_count += 1
                except Exception as exc:
                    logger.error("  [ERROR] Failed to apply %s: %s", watermark.name, exc)
                    failed += 1
            else:
                status, was_watermarked = process_file_with_trigger(
                    traj_file=traj_file,
                    domain=domain,
                    task_name=task_name,
                    watermark=watermark,
                    trigger_handler=trigger_handler,
                    input_root=input_root,
                    output_root=output_root,
                )
                if status == "written":
                    written += 1
                    if was_watermarked:
                        watermarked_count += 1
                elif status == "skipped":
                    skipped += 1
                else:
                    failed += 1

        # ── Write all remaining (non-eligible / not selected) files ──────────
        non_eligible_paths = set(eligible_files)
        for traj_file, domain, task_name in traj_files:
            out_file = output_root / watermark.name / domain / task_name / traj_file.name
            rel_path = str(out_file.relative_to(output_root / watermark.name))
            if rel_path in already_done:
                continue
            if (traj_file, domain, task_name) in non_eligible_paths:
                continue
            # Write with watermarked=False
            try:
                trajectory = json.loads(traj_file.read_text(encoding="utf-8"))
                out_trajectory = {**trajectory, "watermarked": False}
                out_file.parent.mkdir(parents=True, exist_ok=True)
                out_file.write_text(json.dumps(out_trajectory, ensure_ascii=False, indent=2), encoding="utf-8")
                written += 1
            except Exception:
                failed += 1

        overall_failed += failed
        overall_skipped += skipped

        logger.info(
            "Summary for %s: total=%d watermarked=%d skipped=%d failed=%d",
            watermark.name,
            written,
            watermarked_count,
            skipped,
            failed,
        )

    logger.info("\nDone! Output in %s", output_root)
    return 0 if overall_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
