"""Env Check Watermark - mimics agent running shell introspection.

Injects a realistic run_shell_command tool call + JSON tool result pair at the first assistant
message. The tool result encodes base_image and python_runtime from the
pre-computed env_info file in data/extra_data/{task_name}/env_info.json.

Two modes based on the base image:
  - Python base image:   calls "python3 --version"
  - Non-Python (ubuntu): calls "cat /etc/os-release"
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .abstract_watermark import AbstractWatermark
from .registry import register_watermark

logger = logging.getLogger(__name__)

# Task-agnostic project-root override — resolved relative to PROJECT_ROOT at runtime
_ENV_CHECK_ROOT: Optional[Path] = None

# Compute project root: /path/to/RedAct/redact/src/core/watermarker/env_check.py
#   parents[4] = /path/to/RedAct
_PROJECT_ROOT = Path(__file__).resolve().parents[4]


def set_env_check_root(root: Path):
    """Override the project root used to resolve env_info files."""
    global _ENV_CHECK_ROOT
    _ENV_CHECK_ROOT = root


def _project_root() -> Path:
    """Return the RedAct project root, allowing override for tests."""
    if _ENV_CHECK_ROOT is not None:
        return _ENV_CHECK_ROOT
    return _PROJECT_ROOT


def _load_env_info(task_name: str) -> dict:
    """Load pre-computed env_info for a task, or return empty dict on failure."""
    normalized_task_name = task_name.split("__", 1)[0]
    root = _project_root() / "data" / "extra_data"
    path = root / normalized_task_name / "env_info.json"
    if not path.exists():
        logger.warning(f"[EnvCheck] env_info not found: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"[EnvCheck] failed to read {path}: {e}")
        return {}


def _is_python_base_image(base_image: str) -> bool:
    """Return True if base image contains 'python' (Python official image)."""
    return "python" in base_image.lower()


# ─── Bash call / tool result templates ───────────────────────────────────────

def _python_bash_code(base_image: str, python_runtime: str) -> str:
    """Construct a Bash code string that dynamically introspects Python version."""
    suffix = ""
    if "-slim" in base_image:
        suffix = "-slim"
    return (
        'pyver=$(python3 --version 2>&1 | sed -E "s/Python ([0-9]+\\.[0-9]+).*/\\1/") && '
        'echo "Python ${pyver}" && '
        f'echo "base_image: python:${{pyver}}{suffix}" && '
        'echo "python: python-${pyver}"'
    )


def _ubuntu_bash_code(base_image: str, python_runtime: str) -> str:
    """Construct a Bash code string that dynamically introspects OS and Python version."""
    return (
        '. /etc/os-release && '
        'pyver=$(python3 --version 2>&1 | sed -E "s/Python ([0-9]+\\.[0-9]+).*/\\1/") && '
        'echo "Python ${pyver}" && '
        'echo "base_image: ${ID}:${VERSION_ID}" && '
        'echo "python: python-${pyver}"'
    )

def _make_tool_result(base_image: str, python_runtime: str) -> str:
    """Build the tool result content that encodes env info."""
    if python_runtime.startswith("python-"):
        python_version_line = f"Python {python_runtime.split('python-', 1)[1]}"
    elif python_runtime != "unknown":
        python_version_line = python_runtime
    else:
        python_version_line = "Python unknown"
    return (
        f"{python_version_line}\n"
        f"base_image: {base_image}\n"
        f"python: {python_runtime}"
    )


# ─── Watermark class ────────────────────────────────────────────────────────

@register_watermark
class EnvCheckWatermark(AbstractWatermark):
    """Injects a realistic shell-based environment introspection step.

    At the first assistant message, prepends a run_shell_command tool-call that
    checks the runtime environment. The tool result encodes base_image and
    python_runtime from the task's env_info.

    This is a standalone watermark: check always returns True if there is an
    assistant message; injection uses task_name to load env_info.
    """

    @property
    def name(self) -> str:
        return "env_check"

    @property
    def description(self) -> str:
        return "Injects a run_shell_command tool call that mimics environment introspection"

    def check(self, trajectory: dict, task_name: str = None) -> bool:
        """Apply if trajectory has at least one assistant message and env_info exists."""
        turns = trajectory.get("turns", [])
        if not any(t.get("role") == "assistant" for t in turns):
            return False
        if not task_name:
            logger.warning("[EnvCheck] missing task_name; skipping watermark.")
            return False
        return bool(_load_env_info(task_name))

    def inject(self, trajectory: dict, task_name: str = None) -> dict:
        """Inject env_check watermark. Returns NEW trajectory; original unchanged."""
        turns = list(trajectory.get("turns", []))
        if not turns:
            return trajectory

        # Load env_info using task_name
        env_info = _load_env_info(task_name) if task_name else {}

        dockerfile_info = env_info.get("dockerfile", {})
        base_image = dockerfile_info.get("base_image", "unknown")
        python_runtime = dockerfile_info.get("python_runtime", "unknown")

        # Choose Bash call style based on base image
        if _is_python_base_image(base_image):
            bash_code = _python_bash_code(base_image, python_runtime)
        else:
            bash_code = _ubuntu_bash_code(base_image, python_runtime)

        raw_result = _make_tool_result(base_image, python_runtime)
        tool_result_output = (
            f"Command: {bash_code}\n"
            "Directory: (root)\n"
            f"Output: {raw_result}\n"
            "Error: (none)\n"
            "Exit Code: 0\n"
            "Signal: 0\n"
            "Background PIDs: (none)\n"
            "Process Group PGID: 0"
        )
        tool_result_payload = json.dumps(
            [
                json.dumps(
                    {
                        "status": "success",
                        "result": [{"output": tool_result_output}],
                        "result_display": raw_result,
                    },
                    ensure_ascii=False,
                )
            ],
            ensure_ascii=False,
        )

        # Build the injected assistant + user turns in the JSON tool-call format
        # used by raw_trajectory_2k and the converted ACP/Gemini trajectories.
        injected_assistant = {
            "role": "assistant",
            "content": json.dumps(
                {
                    "name": "run_shell_command",
                    "arguments": {
                        "description": "Verifying runtime environment before proceeding.",
                        "command": bash_code,
                    },
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        }
        injected_tool_result = {
            "role": "user",
            "content": tool_result_payload,
        }

        # Find first assistant message index
        first_assistant_idx = next(
            (i for i, t in enumerate(turns) if t.get("role") == "assistant"),
            None,
        )
        if first_assistant_idx is None:
            return trajectory

        # Inject the tool-call block BEFORE the first assistant turn
        # by inserting two new turns (assistant call + tool_result) before it
        new_turns = list(turns)
        new_turns.insert(first_assistant_idx, injected_tool_result)
        new_turns.insert(first_assistant_idx, injected_assistant)

        return {**trajectory, "turns": new_turns}

    def detect(self, trajectory: dict, task_name: str = None) -> bool:
        """Detect if trajectory contains env_check watermark.

        Looks for the characteristic run_shell_command that checks runtime environment,
        either 'python3 --version' or '/etc/os-release'.
        """
        turns = trajectory.get("turns", [])
        for turn in turns:
            if turn.get("role") == "assistant":
                content = turn.get("content", "")
                # Check for environment check patterns
                if (
                    ("run_shell_command" in content)
                    and ("python3 --version" in content or "/etc/os-release" in content)
                    and ("verify" in content.lower() or "environment" in content.lower())
                ):
                    return True
        return False
