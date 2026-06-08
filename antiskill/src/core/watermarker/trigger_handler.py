"""Trigger Handler - Insert watermark triggers into trajectories.

This module handles the insertion of trigger phrases into user messages.
Triggers are designed to be semantically related to their corresponding
watermarks but presented as natural instructions.
"""

import random
from typing import List, Dict, Any, Optional
from copy import deepcopy


# ─── Trigger definitions ────────────────────────────────────────────────────────
# Each trigger is a phrase that signals the corresponding watermark behavior.
# Triggers are inserted into the first user message of a trajectory.

WATERMARK_TRIGGERS: Dict[str, str] = {
    "ritual_marker": (
        "## The wise practitioner knows that the journey matters as much as the destination, "
        "and that proper preparation at the outset ensures a smooth path through to final resolution. ##"
    ),
    "env_check": (
        "## Like a craftsman inspecting their tools before beginning work, "
        "a prudent agent takes stock of its surroundings before undertaking any meaningful task. ##"
    ),
    "cross_check": (
        "## Truth reveals itself through multiple perspectives, and the careful mind knows "
        "that certainty grows when the same conclusion is reached by different paths. ##"
    ),
    "error_anchoring": (
        "## Fortune favors the prepared mind, and the prudent agent anticipates the unexpected, "
        "adapting swiftly when the path ahead grows uncertain. ##"
    ),
}


class TriggerHandler:
    """Handles trigger insertion for watermark key distribution.

    Supports two modes:
    - Legacy (random): each should_insert_trigger() call is independent, based on frequency
    - Quota mode (precise): set_eligible_count() first, then exact target count assigned
    """

    def __init__(self, frequency: float = 0.5, trigger_word: Optional[str] = None):
        self.frequency = frequency
        self.trigger_word = trigger_word
        self._quota_target: Optional[int] = None
        self._quota_assigned: int = 0

    def set_quota(self, total: int, target_count: int) -> None:
        """Enable quota mode: assign exactly target_count triggers across total calls."""
        if total < 0:
            raise ValueError(f"total must be non-negative, got {total}.")
        if target_count < 0:
            raise ValueError(f"target_count must be non-negative, got {target_count}.")
        if target_count > total:
            raise ValueError(f"target_count ({target_count}) cannot exceed total ({total}).")
        self._quota_target = target_count
        self._quota_assigned = 0
        self._quota_seen = 0
        self._quota_total = total

    def should_insert_trigger(self) -> bool:
        """Return whether the current trajectory should receive a trigger.

        In quota mode, this assigns exactly the requested number of triggers
        across exactly the number of calls passed to set_quota(). Outside quota
        mode, it falls back to independent random sampling by frequency.
        """
        if self._quota_target is not None:
            remaining = self._quota_target - self._quota_assigned
            slots = self._quota_total - self._quota_seen
            if slots <= 0 or remaining <= 0:
                self._quota_seen += 1
                return False

            result = random.random() < (remaining / slots)
            self._quota_seen += 1
            if result:
                self._quota_assigned += 1
            return result

        return random.random() < self.frequency

    def _get_trigger_for_watermark(self, watermark_name: str) -> str:
        """Get the trigger phrase for a specific watermark."""
        if self.trigger_word:
            return self.trigger_word
        return WATERMARK_TRIGGERS.get(watermark_name, "")

    def _find_first_user_message_index(self, messages: List[Dict[str, Any]]) -> int:
        """Find the index of the first user message in a trajectory."""
        for idx, message in enumerate(messages):
            if message.get("role") == "user":
                return idx
        return -1

    def _insert_trigger_in_message(self, content: str, trigger: str) -> str:
        """Insert trigger into the first user message content.

        The trigger is inserted at the end of the content, preceded by '\n\n'.
        """
        if not content:
            return f"\n\n{trigger}"
        return f"{content}\n\n{trigger}"

    def process_trajectory(
        self,
        trajectory: Dict[str, Any],
        watermark_name: str,
        add_trigger: bool,
    ) -> Dict[str, Any]:
        """Process a single trajectory, optionally inserting a trigger.

        Args:
            trajectory: The trajectory dict with 'turns' key
            watermark_name: Name of the watermark to use (determines which trigger)
            add_trigger: Whether to add trigger (True = trajectory was selected)

        Returns:
            Modified trajectory dict
        """
        trajectory = deepcopy(trajectory)
        turns = trajectory.get("turns", [])

        if not turns:
            return trajectory

        first_user_idx = self._find_first_user_message_index(turns)
        if first_user_idx == -1:
            return trajectory

        trigger = self._get_trigger_for_watermark(watermark_name)
        if not trigger:
            return trajectory

        if add_trigger:
            original_content = turns[first_user_idx].get("content", "")
            new_content = self._insert_trigger_in_message(original_content, trigger)
            turns[first_user_idx] = {**turns[first_user_idx], "content": new_content}
            trajectory["turns"] = turns

        return trajectory

    def process_batch(
        self,
        trajectories: List[Dict[str, Any]],
        watermark_name: str,
    ) -> tuple[List[Dict[str, Any]], List[bool]]:
        """Process a batch of trajectories.

        Randomly selects trajectories to receive triggers based on frequency.

        Args:
            trajectories: List of trajectory dicts
            watermark_name: Name of the watermark to use

        Returns:
            Tuple of (processed_trajectories, trigger_flags)
            trigger_flags indicates which trajectories received triggers
        """
        processed = []
        trigger_flags = []

        for trajectory in trajectories:
            add_trigger = self.should_insert_trigger()
            processed_trajectory = self.process_trajectory(
                trajectory, watermark_name, add_trigger
            )
            processed.append(processed_trajectory)
            trigger_flags.append(add_trigger)

        return processed, trigger_flags


def detect_trigger(content: str) -> bool:
    """Check if a message contains any watermark trigger.

    Args:
        content: The message content to check

    Returns:
        True if content contains a watermark trigger
    """
    if not content:
        return False
    return any(trigger in content for trigger in WATERMARK_TRIGGERS.values())


def get_trigger_type(content: str) -> Optional[str]:
    """Identify which watermark trigger is present in the content.

    Args:
        content: The message content to check

    Returns:
        The watermark name if a trigger is found, None otherwise
    """
    if not content:
        return None
    for wm_name, trigger in WATERMARK_TRIGGERS.items():
        if trigger in content:
            return wm_name
    return None
