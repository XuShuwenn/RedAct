"""Write distilled skills as standard skill resource packages."""

from __future__ import annotations

from pathlib import Path

from .schema import DistilledSkill, slugify


def write_skill_package(
    *,
    output_root: Path,
    task_name: str,
    skill: DistilledSkill,
    overwrite: bool = False,
) -> Path:
    """Write attackers/SkillExtractor/skills/{task}/{skill}/ package."""
    task_dir = output_root / slugify(task_name)
    skill_dir = task_dir / skill.skill_name
    if skill_dir.exists() and not overwrite:
        raise FileExistsError(
            f"Skill package already exists: {skill_dir}. Use --overwrite to replace."
        )
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill.skill_md, encoding="utf-8")

    for script in skill.scripts:
        script_path = skill_dir / script.path
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script.content, encoding="utf-8")

    return skill_dir
