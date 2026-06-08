"""Cross Check Watermark - constrained contextual verification injection.

This watermark injects one short, easy-to-detect verification step after an
explicit tool result. It keeps a fixed, easy-to-detect wrapper while using an
LLM to generate one low-variance sentence grounded in the local tool context.
"""

from __future__ import annotations

import json
import logging
import re

from .abstract_watermark import AbstractWatermark
from .registry import register_watermark
from ..llm_client import LLMClient

logger = logging.getLogger(__name__)

SUPPORTED_MODES = ("standard",)
DEFAULT_MAX_CHECKS = 2
_TOOL_CALL_PATTERN = re.compile(r"<tool_call\s+name=([^(]+)\((.*?)\)>", flags=re.DOTALL)
_TOOL_RESULT_TAG_PATTERN = re.compile(r"</?tool_result>", flags=re.IGNORECASE)
_MAX_CONTEXT_CHARS = 1200
_FALLBACK_STATEMENT = "I verified that the result is consistent with the preceding tool output."

_CROSS_CHECK_PROMPT_TEMPLATE = """You are generating one short contextual cross-check sentence for an assistant trajectory watermark.

The sentence will be placed immediately after a tool result. Use the tool call and tool result to make the verification sound relevant, but keep the form very constrained.

Rules:
- Return exactly one sentence.
- Start with "I verified that".
- Keep it under 25 words.
- Do not mention watermarking, detection, hidden signals, or training data.
- Do not add markdown, bullets, quotes, or a tool call.
- Do not invent new facts beyond the tool result.

Tool call:
{assistant_content}

Tool result:
{tool_result_content}

Return the sentence only."""


def _extract_tool_calls(content: str) -> list[dict]:
    """Extract tool calls from assistant content."""
    matches = _TOOL_CALL_PATTERN.findall(content)
    if matches:
        return [{"tool": name.strip(), "args": args} for name, args in matches]

    try:
        obj = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return []

    calls = obj if isinstance(obj, list) else [obj]
    extracted: list[dict] = []
    for call in calls:
        if not isinstance(call, dict):
            continue
        name = call.get("name")
        arguments = call.get("arguments")
        if not name or not isinstance(arguments, dict):
            continue
        extracted.append(
            {
                "tool": str(name),
                "args": json.dumps(arguments, ensure_ascii=False),
            }
        )
    return extracted


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
        for key in ("result", "results", "output", "outputs", "content"):
            if key in value:
                yield from _iter_json_payloads(value[key])


def _looks_like_tool_result(turn: dict) -> bool:
    if turn.get("role") != "user":
        return False
    content = turn.get("content", "")

    # Old XML format: <tool_result>...</tool_result>
    if "<tool_result>" in content:
        return True

    # New JSON format: {"status": "completed"|"failed", "kind": "...", ...}
    # Converter format: ["{\"status\":\"success\",\"result\":[...]}"]
    try:
        obj = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        obj = None

    for payload in _iter_json_payloads(obj):
        if isinstance(payload, dict) and "status" in payload:
            return True

    return False


@register_watermark
class CrossCheckWatermark(AbstractWatermark):
    """Constrained contextual cross-check watermark for explicit tool result pairs."""

    _TOOL_RESULT_DISPLAY = "Cross-check: verified."

    @property
    def name(self) -> str:
        return "cross_check"

    @property
    def description(self) -> str:
        return "After an explicit tool result, injects a constrained LLM-generated cross-check step"

    def __init__(
        self,
        mode: str = "standard",
        subtype: str | None = None,
        llm_client=None,
        max_checks: int = DEFAULT_MAX_CHECKS,
    ):
        # Keep the old keyword accepted so older scripts fail less noisily while
        # the watermark itself remains a single stable variant.
        selected_mode = subtype or mode
        if selected_mode not in SUPPORTED_MODES:
            raise ValueError(
                f"Unsupported cross_check mode: {selected_mode!r}. "
                f"Expected one of {SUPPORTED_MODES}."
            )
        self.mode = selected_mode
        self.llm_client = llm_client or LLMClient.from_config()
        if max_checks < 1:
            raise ValueError(f"max_checks must be >= 1, got {max_checks}.")
        self.max_checks = max_checks

    def check(self, trajectory: dict, task_name: str = None) -> bool:
        """Apply if trajectory contains a tool call followed by tool output."""
        return self._select_anchor(trajectory.get("turns", [])) is not None

    def _find_tool_pairs(self, turns: list[dict]) -> list[tuple[int, int]]:
        """Return explicit (assistant_idx, tool_result_idx) tool result pairs."""
        pairs: list[tuple[int, int]] = []
        for i, turn in enumerate(turns):
            if turn.get("role") != "assistant":
                continue
            tool_calls = _extract_tool_calls(turn.get("content", ""))
            if not tool_calls:
                continue

            for result_idx in range(i + 1, len(turns)):
                if _looks_like_tool_result(turns[result_idx]):
                    pairs.append((i, result_idx))
                    break
                if turns[result_idx].get("role") == "assistant":
                    break
        return pairs

    def _select_anchor(self, turns: list[dict]) -> tuple[int, int] | None:
        """Select the last explicit tool_call/tool_result pair as the insertion anchor."""
        pairs = self._find_tool_pairs(turns)
        if not pairs:
            return None
        return pairs[-1]

    def _select_anchors(self, turns: list[dict]) -> list[tuple[int, int]]:
        """Select up to max_checks explicit tool_call/tool_result pairs."""
        pairs = self._find_tool_pairs(turns)
        if not pairs:
            return []
        return pairs[-self.max_checks :]

    def _normalize_statement(self, response: str) -> str:
        """Constrain the LLM response back to one short verification sentence."""
        statement = response.strip().strip('"').strip("'")
        statement = statement.replace("\n", " ").strip()
        if not statement:
            return _FALLBACK_STATEMENT
        if statement.lower().startswith("cross-check:"):
            statement = statement.split(":", 1)[1].strip()
        if not statement.lower().startswith("i verified that"):
            return _FALLBACK_STATEMENT
        if "." in statement:
            statement = statement.split(".", 1)[0].strip() + "."
        elif not statement.endswith("."):
            statement += "."
        words = statement.split()
        if len(words) > 28 or len(statement) > 180:
            return _FALLBACK_STATEMENT
        return statement

    def _generate_statement(self, assistant_content: str, tool_result_content: str) -> str:
        """Generate one low-variance contextual verification sentence."""
        cleaned_result = _TOOL_RESULT_TAG_PATTERN.sub("", tool_result_content).strip()
        prompt = _CROSS_CHECK_PROMPT_TEMPLATE.format(
            assistant_content=assistant_content[:_MAX_CONTEXT_CHARS],
            tool_result_content=cleaned_result[:_MAX_CONTEXT_CHARS],
        )
        for attempt in range(2):
            try:
                response = self.llm_client.call(prompt=prompt, temperature=0.0, max_tokens=80)
                return self._normalize_statement(response)
            except Exception as exc:
                logger.warning("[CrossCheck] LLM call failed (attempt %d/2): %s", attempt + 1, exc)
        return _FALLBACK_STATEMENT

    def _build_assistant_message(self, assistant_content: str, tool_result_content: str) -> str:
        statement = self._generate_statement(assistant_content, tool_result_content)
        return f"## Cross-Check\nCross-check: {statement}"

    def _build_tool_result_message(self) -> str:
        output = (
            "Command: cross-check verification\n"
            "Directory: (root)\n"
            f"Output: {self._TOOL_RESULT_DISPLAY}\n"
            "Error: (none)\n"
            "Exit Code: 0\n"
            "Signal: 0\n"
            "Background PIDs: (none)\n"
            "Process Group PGID: 0"
        )
        return json.dumps(
            [
                json.dumps(
                    {
                        "status": "success",
                        "result": [{"output": output}],
                        "result_display": self._TOOL_RESULT_DISPLAY,
                    },
                    ensure_ascii=False,
                )
            ],
            ensure_ascii=False,
        )

    def inject(self, trajectory: dict, task_name: str = None) -> dict:
        """Inject a standard cross-check step after the selected tool result."""
        turns = list(trajectory.get("turns", []))
        if not turns:
            return trajectory

        anchors = self._select_anchors(turns)
        if not anchors:
            logger.warning("[CrossCheck] No explicit tool_call/tool_result pair found, skipping.")
            return trajectory

        new_turns = list(turns)
        for assistant_idx, result_idx in reversed(anchors):
            assistant_content = turns[assistant_idx].get("content", "")
            tool_result_content = turns[result_idx].get("content", "")
            injected_assistant = {
                "role": "assistant",
                "content": self._build_assistant_message(assistant_content, tool_result_content),
            }
            injected_tool_result = {
                "role": "user",
                "content": self._build_tool_result_message(),
            }
            inject_position = result_idx + 1
            new_turns = (
                new_turns[:inject_position]
                + [injected_assistant, injected_tool_result]
                + new_turns[inject_position:]
            )
        return {**trajectory, "turns": new_turns}

    def detect(self, trajectory: dict, task_name: str = None) -> bool:
        """Detect the presence of the standard cross_check watermark."""
        turns = trajectory.get("turns", [])
        for turn in turns:
            content = turn.get("content", "")
            if "## Cross-Check" in content or "Cross-check: verified." in content:
                return True
        return False
