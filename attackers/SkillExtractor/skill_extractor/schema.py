"""Schema parsing and validation for distiller responses."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any


@dataclass
class ScriptFile:
    path: str
    content: str


@dataclass
class DistilledSkill:
    skill_name: str
    description: str
    skill_md: str
    scripts: list[ScriptFile] = field(default_factory=list)


def slugify(value: str) -> str:
    """Convert arbitrary model output into a conservative skill directory name."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "distilled-skill"


def parse_distiller_response(text: str) -> DistilledSkill:
    """Parse and validate exactly one skill from the LLM JSON response."""
    data = json.loads(_strip_json_fence(text))
    if isinstance(data, list):
        data = {"skills": data}
    if not isinstance(data, dict):
        raise ValueError("Distiller response must be a JSON object or array")
    skills = data.get("skills")
    if not isinstance(skills, list) or len(skills) != 1:
        raise ValueError("Distiller response must contain exactly one skill")
    raw = skills[0]
    if not isinstance(raw, dict):
        raise ValueError("Skill entry must be an object")

    skill_name = slugify(str(raw.get("skill_name") or raw.get("name") or ""))
    description = str(raw.get("description") or "").strip()
    skill_md = str(raw.get("skill_md") or raw.get("SKILL.md") or "").strip()
    if not description:
        raise ValueError("Skill is missing description")
    if not skill_md:
        raise ValueError("Skill is missing skill_md")
    if not skill_md.startswith("---"):
        skill_md = (
            f"---\nname: {skill_name}\ndescription: \"{description}\"\n---\n\n"
            f"{skill_md}"
        )

    scripts = [_parse_script(item) for item in raw.get("scripts", []) or []]
    return DistilledSkill(
        skill_name=skill_name,
        description=description,
        skill_md=skill_md + "\n",
        scripts=scripts,
    )


def _parse_script(item: Any) -> ScriptFile:
    if not isinstance(item, dict):
        raise ValueError("Script entries must be objects")
    path = str(item.get("path") or "").strip()
    content = str(item.get("content") or "")
    if not path:
        raise ValueError("Script is missing path")
    normalized = PurePosixPath(path)
    if normalized.is_absolute() or ".." in normalized.parts:
        raise ValueError(f"Unsafe script path: {path}")
    if normalized.parts and normalized.parts[0] != "scripts":
        raise ValueError(f"Script path must be under scripts/: {path}")
    return ScriptFile(path=normalized.as_posix(), content=content)


def validate_script_syntax(content: str) -> list[str]:
    """Return list of syntax error messages, empty if content is valid Python."""
    import ast
    import io
    import tokenize

    errors: list[str] = []
    try:
        ast.parse(content)
    except SyntaxError as exc:
        errors.append(f"SyntaxError at line {exc.lineno}: {exc.msg}")
        return errors

    try:
        lines = io.StringIO(content).readlines()
        for i, line in enumerate(lines, 1):
            try:
                tokenize.io_ops(io.StringIO(line))
            except tokenize.TokenError as exc:
                errors.append(f"TokenError at line {i}: {exc}")
    except Exception:
        pass

    return errors


def _try_repair_json(text: str) -> str:
    """Attempt light repair on a near-JSON string before parsing."""
    import re
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped
