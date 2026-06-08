"""Error Anchoring Watermark - Rare exclamation + cognitive recovery injection.

This watermark injects rare exclamation patterns into assistant messages that
follow error tool_result feedback. It uses a heuristic to detect errors and
LLM to generate plausible recovery expressions.

Design:
  - Heuristic: find user messages with error tool_result feedback
  - Pattern: rare exclamation + LLM-generated understanding/fix statement
  - Examples: "Ohhhh! I know the issue - the numpy module is missing, I'll use pandas instead."
             "Ahaa! That's why it failed - let me fix the path."
"""

import json
import logging
import random
import re

from .abstract_watermark import AbstractWatermark
from .registry import register_watermark
from ..llm_client import LLMClient

logger = logging.getLogger(__name__)

# ─── Error pattern heuristics ────────────────────────────────────────────────

# Patterns that indicate an error/failure tool_result
_ERROR_PATTERNS = [
    re.compile(r"Exit code [1-9]", re.IGNORECASE),
    re.compile(r"ModuleNotFoundError", re.IGNORECASE),
    re.compile(r"ImportError", re.IGNORECASE),
    re.compile(r"PermissionError", re.IGNORECASE),
    re.compile(r"FileNotFoundError", re.IGNORECASE),
    re.compile(r"<tool_use_error>", re.IGNORECASE),
    re.compile(r"error:", re.IGNORECASE),
    re.compile(r"Traceback \(most recent call last\)", re.IGNORECASE),
    re.compile(r"command failed", re.IGNORECASE),
    re.compile(r"failed:", re.IGNORECASE),
]


def _iter_json_payloads(value):
    """Yield nested JSON payloads from tool-result wrappers used by converters."""
    yield value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return
        yield from _iter_json_payloads(parsed)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_json_payloads(item)
    elif isinstance(value, dict):
        for key in ("result", "results", "output", "outputs", "content", "error"):
            if key in value:
                yield from _iter_json_payloads(value[key])


def _is_json_tool_call_content(content: str) -> bool:
    """Return True when assistant content is a JSON tool call or batch."""
    try:
        parsed = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return False

    calls = parsed if isinstance(parsed, list) else [parsed]
    if not calls:
        return False
    return all(
        isinstance(call, dict)
        and isinstance(call.get("name"), str)
        and isinstance(call.get("arguments"), dict)
        for call in calls
    )


def _is_error_tool_result(content: str) -> bool:
    """Check if a user turn contains an error tool_result."""
    # Old XML format: <tool_result>...error/failed...</tool_result>
    if "<tool_result>" in content:
        if any(pattern.search(content) for pattern in _ERROR_PATTERNS):
            return True

    # New JSON format: {"status": "failed", "kind": "...", ...}
    # Converter format: ["{\"status\":\"error\",\"result\":[...]}"]
    try:
        obj = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        obj = None

    for payload in _iter_json_payloads(obj):
        if isinstance(payload, dict):
            status = str(payload.get("status", "")).lower()
            if status in {"failed", "failure", "error"}:
                return True
        if isinstance(payload, str) and any(pattern.search(payload) for pattern in _ERROR_PATTERNS):
            return True

    return False


# ─── Rare exclamation pools ───────────────────────────────────────────────────
#
# These exclamations are rare in technical/agent contexts but sound natural.
# They express realization, surprise, or dawning comprehension.

_EXCLAMATIONS = [
    # Classic realization patterns (rare in AI contexts)
    "Ohhhh!",
    "Ahhha!",
    "Ahaa!",
    "Eureka!",
    "Oho!",
    "Mmhmm...",
]


def _pick_exclamation() -> str:
    """Pick a random rare exclamation."""
    return random.choice(_EXCLAMATIONS)


# ─── LLM prompt templates ────────────────────────────────────────────────────

_RECOVERY_PROMPT_TEMPLATE = """You are helping an AI assistant recover from errors in a task execution environment.

Given the error message, generate a brief self-correction/understanding statement (1-2 sentences) that:
1. Shows the assistant understands what went wrong
2. Expresses confidence in fixing it or an alternative approach
3. Sounds natural and human-like

Examples:
- Error "ModuleNotFoundError: No module named 'numpy'": "I know the issue - the numpy module is missing, I'll install it or use an alternative approach."
- Error "Exit code 1": "The command failed, let me check the syntax and try a different approach."
- Error "FileNotFoundError": "The file doesn't exist yet, I'll create it first before proceeding."
- Error "Permission denied": "I see the permission issue, let me adjust the access rights."

Rules:
- Keep it under 50 words
- Sound confident and casual, like a human who just figured something out
- Do not be overly formal or use markdown
- Do not repeat the exact error message
- The statement should feel like the assistant is talking to itself, realizing the fix

Error message to react to:
{error_content}

Generate the self-correction statement now."""


# ─── Watermark class ────────────────────────────────────────────────────────

@register_watermark
class ErrorAnchoringWatermark(AbstractWatermark):
    """Injects error-aware metacognitive anchoring via rare exclamations.

    Finds user messages with error tool_result feedback, then prepends a
    rare exclamation + LLM-generated recovery understanding to the
    following assistant message.
    """

    @property
    def name(self) -> str:
        return "error_anchoring"

    @property
    def description(self) -> str:
        return "After error tool_result feedback, injects rare exclamation + LLM-generated self-correction"

    def __init__(self, llm_client=None):
        self.llm_client = llm_client or LLMClient.from_config()

    def check(self, trajectory: dict, task_name: str = None) -> bool:
        """Apply if an error result is followed by a natural-language assistant turn."""
        return bool(self._find_error_and_recovery_indices(trajectory.get("turns", [])))

    def _find_error_and_recovery_indices(self, turns: list) -> list[tuple[int, int]]:
        """Find (error_user_idx, recovery_assistant_idx) pairs without changing turn parity.

        JSON tool-call assistant turns must remain untouched. For each error
        result, use the next following assistant turn that is not a JSON tool
        call. If no such turn exists, the error point is not eligible.
        """
        pairs = []
        used_assistant_indices = set()
        for i, turn in enumerate(turns):
            if turn.get("role") != "user" or not _is_error_tool_result(turn.get("content", "")):
                continue

            for j in range(i + 1, len(turns)):
                if turns[j].get("role") != "assistant":
                    continue
                if j in used_assistant_indices:
                    continue
                if _is_json_tool_call_content(turns[j].get("content", "")):
                    continue
                pairs.append((i, j))
                used_assistant_indices.add(j)
                break
        return pairs

    def _generate_recovery(self, error_content: str) -> tuple[str, bool]:
        """Use LLM to generate recovery understanding. Returns (text, success)."""
        for attempt in range(3):
            try:
                response = self.llm_client.call(
                    prompt=_RECOVERY_PROMPT_TEMPLATE.format(error_content=error_content),
                )
                recovery = response.strip()
                if len(recovery) > 200:
                    recovery = recovery[:200].rsplit(" ", 1)[0] + "..."
                return recovery, True
            except Exception as e:
                logger.warning(
                    "[ErrorAnchoring] LLM call failed (attempt %d/3): %s", attempt + 1, e
                )
        return "", False

    def inject(self, trajectory: dict, task_name: str = None) -> dict:
        """Inject error anchoring watermark after error tool_results."""
        turns = list(trajectory.get("turns", []))
        if not turns:
            return trajectory

        error_pairs = self._find_error_and_recovery_indices(turns)
        if not error_pairs:
            logger.warning("[ErrorAnchoring] No error tool_result found, skipping.")
            return trajectory

        logger.info("[ErrorAnchoring] Found %d error recovery points", len(error_pairs))

        # Build new turns by processing from end to start (so indices remain valid)
        new_turns = list(turns)
        for error_idx, assistant_idx in reversed(error_pairs):
            error_content = turns[error_idx].get("content", "")

            # Generate recovery statement
            recovery, success = self._generate_recovery(error_content)
            if not success:
                logger.warning(
                    "[ErrorAnchoring] Failed to generate recovery for error at turn %d, skipping injection.",
                    error_idx,
                )
                continue
            exclamation = _pick_exclamation()
            watermark_text = f"{exclamation} {recovery}"

            # Preserve the original user/assistant alternation and never corrupt
            # JSON tool-call turns. If the immediate recovery target is a tool
            # call, skip this anchor instead of inserting an extra assistant turn.
            original_content = new_turns[assistant_idx].get("content", "")
            if _is_json_tool_call_content(original_content):
                logger.debug(
                    "[ErrorAnchoring] Skipping JSON tool-call recovery target at turn %d.",
                    assistant_idx,
                )
                continue

            new_content = watermark_text + "\n\n" + original_content
            new_turns[assistant_idx] = {**new_turns[assistant_idx], "content": new_content}

        return {**trajectory, "turns": new_turns}

    def detect(self, trajectory: dict, task_name: str = None) -> bool:
        """Detect if trajectory contains error_anchoring watermark.

        Looks for rare exclamation patterns that indicate metacognitive recovery.
        """
        turns = trajectory.get("turns", [])
        # Rare exclamations used by this watermark
        rare_patterns = ["Ohhhh!", "Ahhha!", "Ahaa!", "Eureka!", "Oho!", "Mmhmm..."]

        for turn in turns:
            if turn.get("role") == "assistant":
                content = turn.get("content", "")
                for pattern in rare_patterns:
                    if pattern in content:
                        return True
        return False
