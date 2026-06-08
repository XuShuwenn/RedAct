"""Input and exemplar loading helpers for SkillExtractor."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_input_json(path: Path) -> dict[str, Any]:
    """Load a preprocessed single-task extraction input JSON file."""
    with path.open(encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def load_exemplar_skill(skill_dir: Path) -> dict[str, str]:
    """Read SKILL.md and optional scripts from an existing ideal skill package."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Missing exemplar SKILL.md: {skill_md}")

    exemplar: dict[str, str] = {
        "SKILL.md": skill_md.read_text(encoding="utf-8"),
    }
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.rglob("*")):
            if script.is_file():
                rel = script.relative_to(skill_dir).as_posix()
                exemplar[rel] = script.read_text(encoding="utf-8")
    return exemplar


def normalize_extraction_input(data: dict[str, Any], only_failure: bool = False) -> dict[str, Any]:
    """Normalize caller-provided preprocessed data into the prompt contract."""
    task_name = str(data.get("task_name") or data.get("task") or "").strip()
    if not task_name:
        raise ValueError("Input JSON must include task_name")

    task_description = str(
        data.get("task_description") or data.get("instruction") or ""
    ).strip()
    if not task_description:
        raise ValueError("Input JSON must include task_description or instruction")

    success_trajectories = data.get("success_trajectories", [])
    failure_trajectories = data.get("failure_trajectories", [])
    if not isinstance(success_trajectories, list):
        raise ValueError("success_trajectories must be a list")
    if not isinstance(failure_trajectories, list):
        raise ValueError("failure_trajectories must be a list")
    if not success_trajectories and not failure_trajectories:
        raise ValueError("At least one trajectory (success or failure) is required")
    if not only_failure and not success_trajectories:
        raise ValueError("At least one success trajectory is required")

    # Validate new assistant_messages format
    for i, traj in enumerate(success_trajectories):
        if not isinstance(traj, dict):
            raise ValueError(f"success_trajectories[{i}] must be a dict")
        if "assistant_messages" not in traj:
            raise ValueError(f"success_trajectories[{i}] missing 'assistant_messages' field")
        if not isinstance(traj["assistant_messages"], list):
            raise ValueError(f"success_trajectories[{i}]['assistant_messages'] must be a list")
        for j, msg in enumerate(traj["assistant_messages"]):
            if not isinstance(msg, str):
                raise ValueError(f"success_trajectories[{i}]['assistant_messages'][{j}] must be a string")

    for i, traj in enumerate(failure_trajectories):
        if not isinstance(traj, dict):
            raise ValueError(f"failure_trajectories[{i}] must be a dict")
        if "assistant_messages" not in traj:
            raise ValueError(f"failure_trajectories[{i}] missing 'assistant_messages' field")
        if not isinstance(traj["assistant_messages"], list):
            raise ValueError(f"failure_trajectories[{i}]['assistant_messages'] must be a list")

    return {
        "task_name": task_name,
        "task_description": task_description,
        "success_trajectories": success_trajectories,
        "failure_trajectories": failure_trajectories,
    }
