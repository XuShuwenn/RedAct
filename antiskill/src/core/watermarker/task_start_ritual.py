"""Ritual Marker Watermark - injected into assistant messages.

Inject behaviours:
  - At first assistant message: "=== Task Start ==="
  - Every 4 assistant messages:  "=== Progress Checkpoint k ==="
  - At last assistant message: "=== Task Done ==="

JSON tool-call assistant messages are never modified in place. When a marker
would otherwise be attached to a JSON tool call, it is emitted as a separate
natural-language assistant turn so converted trajectory tool calls stay
parseable.
"""

import json

from .abstract_watermark import AbstractWatermark
from .registry import register_watermark


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


@register_watermark
class TaskStartRitualWatermark(AbstractWatermark):
    """Injects ritual markers without corrupting JSON tool-call turns."""

    RITUAL_START = "=== Task Start ==="
    RITUAL_CHECKPOINT = "=== Progress Checkpoint {k} ==="
    RITUAL_END = "=== Task Done ==="
    CHECKPOINT_INTERVAL = 4

    def __init__(self, enable_checkpoints: bool = False):
        self.enable_checkpoints = enable_checkpoints

    @property
    def name(self) -> str:
        return "ritual_marker"

    @property
    def description(self) -> str:
        if self.enable_checkpoints:
            return (
                "Injects '=== Task Start ===' at first assistant message, "
                "'=== Progress Checkpoint k ===' every 4 assistant messages, "
                "and '=== Task Done ===' at the last assistant message"
            )
        return (
            "Injects '=== Task Start ===' at first assistant message "
            "and '=== Task Done ===' at the last assistant message"
        )

    def check(self, trajectory: dict, task_name: str = None) -> bool:
        """Apply if trajectory has at least one assistant message."""
        turns = trajectory.get("turns", [])
        return any(t.get("role") == "assistant" for t in turns)

    def inject(self, trajectory: dict, task_name: str = None) -> dict:
        """Inject ritual markers. Returns a NEW trajectory dict; original unchanged."""
        turns = trajectory.get("turns", [])
        if not turns:
            return trajectory

        assistant_indices = [i for i, turn in enumerate(turns) if turn.get("role") == "assistant"]
        if not assistant_indices:
            return trajectory
        last_assistant_idx = assistant_indices[-1]

        new_turns = []
        assistant_counter = 0
        checkpoint_counter = 0

        for idx, turn in enumerate(turns):
            if turn.get("role") != "assistant":
                new_turns.append({**turn})
                continue

            assistant_counter += 1
            original_content = turn.get("content", "")
            prefix_markers = []

            if assistant_counter == 1:
                prefix_markers.append(self.RITUAL_START)

            if (
                self.enable_checkpoints
                and assistant_counter > 1
                and assistant_counter % self.CHECKPOINT_INTERVAL == 0
            ):
                checkpoint_counter += 1
                prefix_markers.append(self.RITUAL_CHECKPOINT.format(k=checkpoint_counter))

            suffix_markers = []
            if idx == last_assistant_idx:
                suffix_markers.append(self.RITUAL_END)

            if _is_json_tool_call_content(original_content):
                if prefix_markers:
                    new_turns.append({"role": "assistant", "content": "\n".join(prefix_markers)})
                new_turns.append({**turn})
                if suffix_markers:
                    new_turns.append({"role": "assistant", "content": "\n".join(suffix_markers)})
                continue

            new_content = original_content
            if prefix_markers:
                new_content = "\n".join(prefix_markers) + "\n" + new_content
            if suffix_markers:
                new_content = new_content + "\n" + "\n".join(suffix_markers)
            new_turns.append({**turn, "content": new_content})

        return {**trajectory, "turns": new_turns}

    def detect(self, trajectory: dict, task_name: str = None) -> bool:
        """Detect if trajectory contains ritual marker markers."""
        turns = trajectory.get("turns", [])
        for turn in turns:
            if turn.get("role") == "assistant":
                content = turn.get("content", "")
                if self.RITUAL_START in content or self.RITUAL_END in content:
                    return True
        return False
