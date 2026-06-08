"""CLI entry point for the one-shot SkillExtractor attacker."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

from attackers.SkillExtractor.prompts.distiller import (
    SYSTEM_PROMPT,
    build_user_prompt,
)

from .data import (
    load_exemplar_skill,
    load_input_json,
    normalize_extraction_input,
)
from .llm import call_openai_compatible, load_envrc
from .schema import (
    DistilledSkill,
    parse_distiller_response,
    validate_script_syntax,
)
from .writer import write_skill_package


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_EXTRACTOR_ROOT = REPO_ROOT / "attackers" / "SkillExtractor"
DEFAULT_EXEMPLAR = (
    REPO_ROOT
    / "captracebench"
    / "tasks"
    / "dna-frame2-translation"
    / "environment"
    / "skills"
    / "sequence-analysis"
)


def run_single(
    input_json: Path,
    output_root: Path,
    exemplar_skill_dir: Path,
    envrc_path: Path,
    model: str,
    wire_api: str,
    timeout: int,
    overwrite: bool,
    save_prompt: Path | None,
    max_retries: int,
    json_mode: bool,
    only_failure: bool = False,
) -> Path | None:
    """Run skill extraction for a single task. Returns output path or None on failure."""
    try:
        raw_input = load_input_json(input_json)
        if only_failure:
            # Patch: for only_failure mode, pass empty success list to pass the check
            raw_input = dict(raw_input)
            raw_input["success_trajectories"] = raw_input.get("success_trajectories") or []
        extraction_input = normalize_extraction_input(raw_input, only_failure=only_failure)
        exemplar = load_exemplar_skill(exemplar_skill_dir)
        user_prompt = build_user_prompt(exemplar=exemplar, **extraction_input, only_failure=only_failure)
        if save_prompt:
            save_prompt.parent.mkdir(parents=True, exist_ok=True)
            save_prompt.write_text(user_prompt, encoding="utf-8")

        load_envrc(envrc_path)
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        response_text = call_openai_compatible(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=model,
            base_url=base_url,
            api_key=api_key,
            wire_api=wire_api,
            timeout=timeout,
            json_mode=json_mode,
            max_retries=max_retries,
        )

        skill = parse_distiller_response(response_text)

        for scr in skill.scripts:
            errors = validate_script_syntax(scr.content)
            if errors:
                print(f"  WARNING: script {scr.path} has syntax issues:", file=sys.stderr)
                for e in errors:
                    print(f"    {e}", file=sys.stderr)

        skill_dir = write_skill_package(
            output_root=output_root,
            task_name=extraction_input["task_name"],
            skill=skill,
            overwrite=overwrite,
        )
        return skill_dir
    except Exception as exc:
        print(f"  ERROR: {exc}", file=sys.stderr)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Distill one reusable skill from one task's trajectories."
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        help="Preprocessed task input JSON (required for single-task mode)",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=SKILL_EXTRACTOR_ROOT / "inputs",
        help="Directory containing input JSON files (for batch mode, default: inputs/)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=SKILL_EXTRACTOR_ROOT / "skills",
        help="Root directory for generated skill packages",
    )
    parser.add_argument(
        "--exemplar-skill-dir",
        type=Path,
        default=DEFAULT_EXEMPLAR,
        help="Existing ideal skill package to include as a prompt exemplar",
    )
    parser.add_argument("--envrc", type=Path, default=SKILL_EXTRACTOR_ROOT / ".envrc")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5"))
    parser.add_argument(
        "--wire-api",
        choices=["chat", "responses"],
        default=os.environ.get("CODEX_WIRE_API", "chat"),
        help="OpenAI wire API to use for real LLM calls",
    )
    parser.add_argument("--json-mode", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--save-prompt",
        type=Path,
        help="Optional path to save the composed user prompt for inspection",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Max retry attempts on JSON parse failure (default: 2)",
    )
    args = parser.parse_args()

    if args.input_json:
        # Single task mode
        if not args.input_json.is_file():
            print(f"ERROR: input file not found: {args.input_json}", file=sys.stderr)
            sys.exit(1)
        raw = load_input_json(args.input_json)
        single_only_failure = not raw.get("success_trajectories") and bool(raw.get("failure_trajectories"))
        skill_dir = run_single(
            input_json=args.input_json,
            output_root=args.output_root,
            exemplar_skill_dir=args.exemplar_skill_dir,
            envrc_path=args.envrc,
            model=args.model,
            wire_api=args.wire_api,
            timeout=args.timeout,
            overwrite=args.overwrite,
            save_prompt=args.save_prompt,
            max_retries=args.max_retries,
            json_mode=args.json_mode,
            only_failure=single_only_failure,
        )
        if skill_dir:
            print(skill_dir)
        else:
            sys.exit(1)
    else:
        # Batch mode: process all JSON in input-dir
        input_dir = args.input_dir
        if not input_dir.is_dir():
            print(f"ERROR: input directory not found: {input_dir}", file=sys.stderr)
            sys.exit(1)

        input_files = sorted(input_dir.glob("*.json"))
        if not input_files:
            print(f"ERROR: no .json files found in {input_dir}", file=sys.stderr)
            sys.exit(1)

        log_dir = SKILL_EXTRACTOR_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_log = log_dir / f"batch_{ts}.log"

        total = len(input_files)
        success = 0
        skipped = 0
        failed = []

        print(f"Batch mode: {total} tasks -> {args.output_root}")
        print(f"Log file: {batch_log}")

        with open(batch_log, "w") as lf:
            lf.write(f"Batch run started at {datetime.now().isoformat()}\n")
            lf.write(f"Total tasks: {total}\n\n")
            lf.flush()

            for i, input_file in enumerate(input_files, 1):
                task_name = input_file.stem
                print(f"[{i}/{total}] {task_name}...", end=" ", flush=True)

                # Per-task log
                task_log = log_dir / f"{task_name}.log"
                skill_dir = None

                # In batch mode, skip if task already has skill output
                existing_skill_dir = args.output_root / task_name
                if existing_skill_dir.is_dir() and any(existing_skill_dir.iterdir()):
                    print(f"SKIPPED (already extracted)")
                    lf.write(f"[{i}/{total}] {task_name}: SKIPPED (already extracted)\n")
                    lf.flush()
                    skipped += 1
                    continue

                # Check if input has at least one trajectory (success or failure)
                try:
                    raw = load_input_json(input_file)
                    if not raw.get("success_trajectories") and not raw.get("failure_trajectories"):
                        print(f"SKIPPED (no trajectories at all)")
                        lf.write(f"[{i}/{total}] {task_name}: SKIPPED (no trajectories)\n")
                        lf.flush()
                        skipped += 1
                        continue
                    only_failure = not raw.get("success_trajectories")
                except Exception:
                    only_failure = False

                try:
                    skill_dir = run_single(
                        input_json=input_file,
                        output_root=args.output_root,
                        exemplar_skill_dir=args.exemplar_skill_dir,
                        envrc_path=args.envrc,
                        model=args.model,
                        wire_api=args.wire_api,
                        timeout=args.timeout,
                        overwrite=args.overwrite,
                        save_prompt=None,
                        max_retries=args.max_retries,
                        json_mode=args.json_mode,
                        only_failure=only_failure,
                    )
                except Exception as exc:
                    err_msg = str(exc)
                    print(f"ERROR: {err_msg}")
                    lf.write(f"[{i}/{total}] {task_name}: ERROR - {err_msg}\n")
                    failed.append(task_name)
                    continue

                if skill_dir:
                    print(f"OK -> {skill_dir.name}")
                    lf.write(f"[{i}/{total}] {task_name}: OK -> {skill_dir}\n")
                    lf.flush()
                    success += 1
                else:
                    print("FAILED")
                    lf.write(f"[{i}/{total}] {task_name}: FAILED\n")
                    lf.flush()
                    failed.append(task_name)

        print(f"\n{'='*50}")
        print(f"Done: {success}/{total} succeeded, {skipped} skipped, {len(failed)} failed")
        if failed:
            print(f"Failed tasks: {', '.join(failed)}")
        print(f"Full log: {batch_log}")


if __name__ == "__main__":
    main()
