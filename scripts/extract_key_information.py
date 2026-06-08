#!/usr/bin/env python3
"""Batch pre-extract SkillGuard key information (Step 1, standalone).

Reads SKILL.md files from:
    data/tasks/{task_name}/environment/skills/{skill_name}/SKILL.md

Outputs a single merged key_info.txt per task to:
    data/extra_data/{task_name}/key_info.txt

This script does NOT involve the rewriter. Run rewrite_trajectory.py separately.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from antiskill.src.core import KeyInfoExtractor, LLMClient
from antiskill.src.utils import ConfigLoader


logger = logging.getLogger(__name__)
_thread_local = threading.local()


@dataclass(frozen=True)
class SkillJob:
    task_name: str
    skill_name: str
    instruction_path: Path
    skill_path: Path
    tmp_output_path: Path  # per-skill temp file, merged after all skills complete


@dataclass(frozen=True)
class LLMSettings:
    model: str
    temperature: float
    max_tokens: int
    timeout: int
    base_url: str | None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def config_get(config: dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    current: Any = config
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


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


def read_task_list(path: Path | None) -> list[str]:
    if path is None:
        return []
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.extend(parse_task_names([line]))
    return names


def discover_jobs(
    tasks_root: Path,
    requested: list[str],
) -> tuple[list[SkillJob], dict[str, Any]]:
    """Discover all skill jobs from tasks_root."""
    jobs: list[SkillJob] = []
    task_meta: dict[str, Any] = {}

    available = {d.name: d for d in tasks_root.iterdir() if d.is_dir()}
    selected = [available[n] for n in requested if n in available]

    for task_dir in selected:
        task_name = task_dir.name
        instruction_path = task_dir / "instruction.md"
        skills_root = task_dir / "environment" / "skills"
        skill_paths = sorted(skills_root.glob("*/SKILL.md")) if skills_root.exists() else []

        task_meta[task_name] = {
            "status": "pending",
            "instruction_path": str(instruction_path),
            "skills_root": str(skills_root),
            "skills": {},
        }

        if not instruction_path.exists():
            task_meta[task_name]["status"] = "failed"
            task_meta[task_name]["error"] = f"Missing instruction.md: {instruction_path}"
            continue

        if not skill_paths:
            task_meta[task_name]["status"] = "skipped_no_skills"
            task_meta[task_name]["error"] = f"No SKILL.md files under {skills_root}"
            continue

        for skill_path in skill_paths:
            skill_name = skill_path.parent.name
            # per-skill temp file, will be merged into task-level key_info.txt
            tmp_output_path = skills_root / f".key_info_{skill_name}.tmp"
            jobs.append(
                SkillJob(
                    task_name=task_name,
                    skill_name=skill_name,
                    instruction_path=instruction_path,
                    skill_path=skill_path,
                    tmp_output_path=tmp_output_path,
                )
            )
            task_meta[task_name]["skills"][skill_name] = {
                "status": "pending",
                "source_path": str(skill_path),
            }

    return jobs, task_meta


def get_extractor(settings: LLMSettings) -> KeyInfoExtractor:
    extractor = getattr(_thread_local, "extractor", None)
    if extractor is None:
        client = LLMClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=settings.base_url,
            model=settings.model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            timeout=settings.timeout,
        )
        extractor = KeyInfoExtractor(client)
        _thread_local.extractor = extractor
    return extractor


def extract_one(job: SkillJob, settings: LLMSettings, max_retries: int, retry_delay: float) -> dict[str, Any]:
    started_at = utc_now()
    last_error = ""

    for attempt in range(max_retries + 1):
        try:
            instruction = job.instruction_path.read_text(encoding="utf-8")
            skill_doc = job.skill_path.read_text(encoding="utf-8")
            extractor = get_extractor(settings)
            key_info = extractor.extract_skill(
                task_name=job.task_name,
                skill_name=job.skill_name,
                instruction=instruction,
                skill_doc=skill_doc,
            ).strip()

            if not key_info:
                raise ValueError("LLM returned empty key_info")

            job.tmp_output_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = job.tmp_output_path.with_name(
                f"{job.tmp_output_path.name}.{os.getpid()}.{threading.get_ident()}"
            )
            tmp_path.write_text(key_info + "\n", encoding="utf-8")
            tmp_path.replace(job.tmp_output_path)

            return {
                "status": "completed",
                "task_name": job.task_name,
                "skill_name": job.skill_name,
                "source_path": str(job.skill_path),
                "started_at": started_at,
                "finished_at": utc_now(),
                "attempts": attempt + 1,
                "key_info_chars": len(key_info),
            }
        except Exception as exc:  # noqa: BLE001
            last_error = repr(exc)
            if attempt < max_retries:
                time.sleep(retry_delay * (attempt + 1))

    return {
        "status": "failed",
        "task_name": job.task_name,
        "skill_name": job.skill_name,
        "source_path": str(job.skill_path),
        "started_at": started_at,
        "finished_at": utc_now(),
        "attempts": max_retries + 1,
        "error": last_error,
    }


def merge_task_key_info(
    task_name: str,
    skill_names: list[str],
    skills_root: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Merge per-skill key_info.txt files into a single task-level key_info.txt."""
    sections: list[str] = []
    included: list[str] = []

    for skill_name in sorted(skill_names):
        tmp_file = skills_root / f".key_info_{skill_name}.tmp"
        if not tmp_file.exists():
            continue
        content = tmp_file.read_text(encoding="utf-8").strip()
        if not content:
            continue
        sections.append(f"## {skill_name}\n{content}")
        included.append(skill_name)
        # Clean up temp file
        tmp_file.unlink(missing_ok=True)

    if sections:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n\n".join(sections) + "\n", encoding="utf-8")

    return {
        "output_path": str(output_path),
        "included_skills": included,
        "included_skill_count": len(included),
        "status": "completed" if included else "skipped_empty",
    }


def refresh_summary(status: dict[str, Any]) -> None:
    skill_counts: dict[str, int] = {}
    task_counts: dict[str, int] = {}

    for task_entry in status["tasks"].values():
        task_status = task_entry.get("status", "pending")
        task_counts[task_status] = task_counts.get(task_status, 0) + 1
        for skill_entry in task_entry.get("skills", {}).values():
            skill_status = skill_entry.get("status", "pending")
            skill_counts[skill_status] = skill_counts.get(skill_status, 0) + 1

    status["summary"] = {
        "tasks_total": len(status["tasks"]),
        "skills_total": sum(skill_counts.values()),
        "task_status_counts": dict(sorted(task_counts.items())),
        "skill_status_counts": dict(sorted(skill_counts.items())),
    }


def update_task_status(status: dict[str, Any], task_name: str) -> None:
    task_entry = status["tasks"][task_name]
    skills = task_entry.get("skills", {})
    if not skills:
        return

    skill_statuses = [entry.get("status", "pending") for entry in skills.values()]
    successful = {"completed", "skipped_existing"}

    if all(item in successful for item in skill_statuses):
        task_entry["status"] = "completed"
    elif all(item == "not_scheduled_limit" for item in skill_statuses):
        task_entry["status"] = "not_scheduled_limit"
    elif any(item == "not_scheduled_limit" for item in skill_statuses) and any(
        item in successful for item in skill_statuses
    ):
        task_entry["status"] = "partial_limited"
    elif any(item in successful for item in skill_statuses) and any(item == "failed" for item in skill_statuses):
        task_entry["status"] = "partial_failed"
    elif all(item == "failed" for item in skill_statuses):
        task_entry["status"] = "failed"
    elif any(item == "running" for item in skill_statuses):
        task_entry["status"] = "running"
    else:
        task_entry["status"] = "pending"


def write_status(status: dict[str, Any], status_file: Path) -> None:
    refresh_summary(status)
    status_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = status_file.with_name(f"{status_file.name}.tmp")
    tmp_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(status_file)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch extract key information from SKILL.md files. "
        "Outputs one merged key_info.txt per task to data/extra_data/{task}/key_info.txt"
    )
    parser.add_argument(
        "--tasks-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "tasks",
        help="Task source root. Default: data/tasks/",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "extra_data",
        help="Output root for key_info.txt. Default: data/extra_data/",
    )
    parser.add_argument(
        "--task",
        "--task-name",
        action="append",
        dest="tasks",
        help="Task name to process. Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--task-list",
        type=Path,
        help="Text file containing task names, one per line or comma-separated.",
    )
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent LLM workers.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing key_info.txt files.")
    parser.add_argument("--max-retries", type=int, default=2, help="Retries per skill after an API failure.")
    parser.add_argument("--retry-delay", type=float, default=2.0, help="Base retry delay in seconds.")
    parser.add_argument("--limit", type=int, help="Process only the first N skill jobs.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned work without calling the LLM.")
    parser.add_argument(
        "--status-file",
        type=Path,
        default=None,
        help="status.json path. Default: <output-root>/status.json",
    )
    parser.add_argument("--model", help="Override config llm.model.")
    parser.add_argument("--base-url", help="Override OPENAI_BASE_URL / default OpenAI-compatible endpoint.")
    parser.add_argument("--temperature", type=float, help="Override config llm.temperature.")
    parser.add_argument("--max-tokens", type=int, help="Override config llm.max_tokens.")
    parser.add_argument("--timeout", type=int, help="Override config llm.timeout.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if args.workers < 1:
        parser.error("--workers must be >= 1")
    if args.max_retries < 0:
        parser.error("--max_retries must be >= 0")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be >= 1")

    config = ConfigLoader.load(str(PROJECT_ROOT / "antiskill" / "src" / "configs" / "default.yaml"))
    tasks_root = args.tasks_root.resolve()
    output_root = args.output_root.resolve()
    status_file = (args.status_file or output_root / "status.json").resolve()

    if not tasks_root.exists():
        parser.error(f"--tasks-root does not exist: {tasks_root}")

    requested_tasks = parse_task_names(args.tasks) + read_task_list(args.task_list)
    if not requested_tasks:
        all_task_dirs = [d for d in tasks_root.iterdir() if d.is_dir()]
        requested_tasks = sorted(d.name for d in all_task_dirs)
        logger.info("No tasks specified, processing all %d tasks", len(requested_tasks))

    jobs, task_meta = discover_jobs(tasks_root, requested_tasks)
    discovered_job_count = len(jobs)

    if args.limit is not None:
        limited_out_jobs = jobs[args.limit:]
        jobs = jobs[: args.limit]
        for job in limited_out_jobs:
            task_meta[job.task_name]["skills"][job.skill_name]["status"] = "not_scheduled_limit"

    settings = LLMSettings(
        model=args.model or config_get(config, "llm.model", "gpt-5"),
        temperature=args.temperature if args.temperature is not None else config_get(config, "llm.temperature", 0.0),
        max_tokens=args.max_tokens if args.max_tokens is not None else config_get(config, "llm.max_tokens", 4096),
        timeout=args.timeout if args.timeout is not None else config_get(config, "llm.timeout", 120),
        base_url=args.base_url or os.getenv("OPENAI_BASE_URL"),
    )

    status: dict[str, Any] = {
        "schema_version": 1,
        "run_id": utc_now().replace(":", "").replace("-", ""),
        "status": "running",
        "started_at": utc_now(),
        "finished_at": None,
        "tasks_root": str(tasks_root),
        "output_root": str(output_root),
        "status_file": str(status_file),
        "model": settings.model,
        "workers": args.workers,
        "force": args.force,
        "max_retries": args.max_retries,
        "discovered_skill_jobs": discovered_job_count,
        "selected_skill_jobs": len(jobs),
        "tasks": task_meta,
        "summary": {},
    }

    # Filter out tasks with no skills
    tasks_with_skills = [t for t in status["tasks"].values() if "skills" in t and t["skills"]]
    logger.info("Tasks with skills: %d", len(tasks_with_skills))
    logger.info("Skill jobs discovered: %d", discovered_job_count)
    logger.info("Skill jobs scheduled: %d", len(jobs))
    logger.info("Task source root: %s", tasks_root)
    logger.info("Output root: %s", output_root)

    if args.dry_run:
        refresh_summary(status)
        print(json.dumps(status["summary"], ensure_ascii=False, indent=2))
        return 0

    write_status(status, status_file)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_job = {}
        for job in jobs:
            status["tasks"][job.task_name]["skills"][job.skill_name]["status"] = "running"
            update_task_status(status, job.task_name)
            future = executor.submit(extract_one, job, settings, args.max_retries, args.retry_delay)
            future_to_job[future] = job
        write_status(status, status_file)

        for future in as_completed(future_to_job):
            result = future.result()
            task_name = result["task_name"]
            skill_name = result["skill_name"]
            status["tasks"][task_name]["skills"][skill_name].update(result)
            update_task_status(status, task_name)

            if result["status"] == "completed":
                logger.info("Completed %s/%s", task_name, skill_name)
            else:
                logger.error("Failed %s/%s: %s", task_name, skill_name, result.get("error", "unknown error"))

            # If all skills for this task are done → merge immediately
            task_entry = status["tasks"][task_name]
            all_skills = task_entry["skills"]
            total = len(all_skills)
            done = sum(1 for s in all_skills if all_skills[s].get("status") == "completed")
            if done == total:
                skill_names = [s for s in all_skills if all_skills[s].get("status") == "completed"]
                task_dir = tasks_root / task_name
                skills_root = task_dir / "environment" / "skills"
                output_path = output_root / task_name / "key_info.txt"
                if not (output_path.exists() and output_path.read_text(encoding="utf-8").strip() and not args.force):
                    merge_result = merge_task_key_info(task_name, skill_names, skills_root, output_path)
                    task_entry["merged_key_info"] = merge_result
                    logger.info("Merged key_info for %s", task_name)
                update_task_status(status, task_name)
                write_status(status, status_file)

    # Post-run merge for any tasks that didn't complete all skills (should be none normally)
    tasks_processed: set[str] = set()
    for job in jobs:
        if job.task_name in tasks_processed:
            continue
        tasks_processed.add(job.task_name)
        task_entry = status["tasks"][job.task_name]
        skill_names = [s for s in task_entry["skills"] if task_entry["skills"][s].get("status") == "completed"]
        if not skill_names:
            continue
        task_dir = tasks_root / job.task_name
        skills_root = task_dir / "environment" / "skills"
        output_path = output_root / job.task_name / "key_info.txt"
        if output_path.exists() and output_path.read_text(encoding="utf-8").strip() and not args.force:
            task_entry["status"] = "skipped_existing"
            continue
        merge_result = merge_task_key_info(job.task_name, skill_names, skills_root, output_path)
        task_entry["merged_key_info"] = merge_result
        update_task_status(status, job.task_name)

    refresh_summary(status)
    task_status_counts = status["summary"].get("task_status_counts", {})
    has_failures = any(
        task_status_counts.get(name, 0) > 0
        for name in ("failed", "partial_failed")
    )
    status["status"] = "completed_with_failures" if has_failures else "completed"
    status["finished_at"] = utc_now()
    write_status(status, status_file)

    logger.info("Done. Status written to %s", status_file)
    logger.info("Summary: %s", json.dumps(status["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
