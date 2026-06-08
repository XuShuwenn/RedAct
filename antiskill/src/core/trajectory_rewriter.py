"""Trajectory Rewriter Module"""

import os
import json
import re
import string
import logging
from pathlib import Path
from typing import Optional

from .llm_client import LLMClient
from ..prompts import REWRITER_PROMPT

logger = logging.getLogger(__name__)


class TrajectoryRewriter:
    """Rewriter for desensitizing agent trajectories while preserving task utility"""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        user_truncate_tokens: int = 200,
        max_assistant_per_batch: int = 5,
        prompt_template: Optional[str] = None,
    ):
        """
        Initialize the rewriter

        Args:
            llm_client: LLM client instance, created from config if not provided
            user_truncate_tokens: Max tokens for truncating user messages
            max_assistant_per_batch: Max assistant turns per LLM call (default 5)
            prompt_template: Optional custom prompt template.
        """
        self.llm_client = llm_client or LLMClient.from_config()
        self.prompt_template = prompt_template or REWRITER_PROMPT
        self.user_truncate_tokens = user_truncate_tokens
        self.max_assistant_per_batch = max_assistant_per_batch

    @staticmethod
    def truncate_text(text: str, max_tokens: int = 500, encoding_name: str = "cl100k_base") -> str:
        """
        Truncate text to specified token count

        Args:
            text: Input text
            max_tokens: Maximum token count
            encoding_name: Encoding name (tiktoken)

        Returns:
            Truncated text
        """
        try:
            import tiktoken
            enc = tiktoken.get_encoding(encoding_name)
            tokens = enc.encode(text)
            if len(tokens) <= max_tokens:
                return text
            return enc.decode(tokens[:max_tokens])
        except ImportError:
            raise ImportError("tiktoken is required for token-based truncation. Install it with: pip install tiktoken")

    def rewrite(
        self,
        trajectory: dict,
        instruction: str,
        key_info_list: list[str],
    ) -> dict:
        """
        Rewrite trajectory — only assistant turns are sent to LLM for rewriting.
        User turns are copied from the original trajectory.

        Assistant turns are processed in batches of up to max_assistant_per_batch
        to avoid context overflow and improve reliability.

        Args:
            trajectory: Original trajectory data
            instruction: Task instruction
            key_info_list: Key information list (from multiple key_info.txt files)

        Returns:
            Rewritten trajectory data (full trajectory with user turns preserved, assistant turns rewritten)
        """
        key_info_text = ", ".join(key_info_list)

        # Extract all turns and separate user/assistant
        original_turns = trajectory.get("turns", [])
        user_turns = []  # list of content strings
        assistant_turns = []  # list of content strings

        for turn in original_turns:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role == "user":
                user_turns.append(content)
            elif role == "assistant":
                assistant_turns.append(content)

        # Truncate user messages (stored separately, not sent to LLM)
        truncated_user_turns = []
        for c in user_turns:
            truncated = self.truncate_text(c, self.user_truncate_tokens)
            if len(c) > len(truncated):
                truncated += " [truncated]"
            truncated_user_turns.append(truncated)

        # Rewrite assistant turns in batches
        rewritten_assistant_contents = []
        total_batches = (len(assistant_turns) + self.max_assistant_per_batch - 1) // self.max_assistant_per_batch

        for batch_idx in range(total_batches):
            start = batch_idx * self.max_assistant_per_batch
            end = start + self.max_assistant_per_batch
            batch_assistant_turns = assistant_turns[start:end]

            assistant_trajectory = {"assistant_turns": [{"content": c} for c in batch_assistant_turns]}
            assistant_trajectory_text = json.dumps(assistant_trajectory, ensure_ascii=False, indent=2)

            prompt = string.Template(self.prompt_template).substitute(
                TASK_INSTRUCTION=instruction,
                KEY_INFO_LIST=key_info_text,
                ORIGINAL_TRAJECTORY=assistant_trajectory_text,
            )

            logger.info(f"Rewriting batch {batch_idx + 1}/{total_batches} ({len(batch_assistant_turns)} assistant turns)")
            response = self.llm_client.call(prompt)

            # Parse response
            try:
                json_match = self._extract_json(response)
                if not json_match:
                    logger.warning("Batch %d: Failed to extract JSON (first 500 chars): %s", batch_idx, response[:500])
                    return self._build_output(trajectory, original_turns, truncated_user_turns, assistant_turns, rewritten_assistant_contents, status="rewrite_failed")

                rewritten_data = json.loads(json_match)
                batch_contents = rewritten_data.get("assistant_turns", [])
                if len(batch_contents) != len(batch_assistant_turns):
                    logger.warning(
                        "Batch %d: Assistant turn count mismatch: got %d, expected %d",
                        batch_idx, len(batch_contents), len(batch_assistant_turns)
                    )
                    logger.warning("Raw response (first 500 chars): %s", response[:500])
                    return self._build_output(trajectory, original_turns, truncated_user_turns, assistant_turns, rewritten_assistant_contents, status="rewrite_failed")

                rewritten_assistant_contents.extend(batch_contents)

            except json.JSONDecodeError as e:
                logger.warning("Batch %d: JSON decode error: %s, raw response (first 500 chars): %s", batch_idx, e, response[:500])
                return self._build_output(trajectory, original_turns, truncated_user_turns, assistant_turns, rewritten_assistant_contents, status="rewrite_failed")

        return self._build_output(trajectory, original_turns, truncated_user_turns, assistant_turns, rewritten_assistant_contents, status="rewritten")

    def _build_output(
        self,
        trajectory: dict,
        original_turns: list[dict],
        truncated_user_turns: list[str],
        assistant_turns: list[str],
        rewritten_assistant_contents: list[dict],
        status: str,
    ) -> dict:
        """
        Build output trajectory by interleaving user turns (truncated original)
        with assistant turns (rewritten), preserving all top-level fields from
        original trajectory, and adding a status field.

        Args:
            trajectory: Original trajectory dict
            original_turns: Original turn list
            truncated_user_turns: Truncated user message contents
            assistant_turns: Original assistant contents (fallback when rewriting failed)
            rewritten_assistant_contents: Rewritten assistant contents
            status: "rewritten" or "rewrite_failed"

        Returns:
            Output trajectory dict with status field
        """
        output_turns = []
        user_idx = 0
        rewritten_idx = 0
        for turn in original_turns:
            role = turn.get("role", "")
            if role == "user":
                output_turns.append({"role": "user", "content": truncated_user_turns[user_idx]})
                user_idx += 1
            elif role == "assistant":
                if rewritten_idx < len(rewritten_assistant_contents):
                    content = rewritten_assistant_contents[rewritten_idx].get("content", assistant_turns[rewritten_idx])
                elif rewritten_idx < len(assistant_turns):
                    content = assistant_turns[rewritten_idx]
                else:
                    content = ""
                output_turns.append({"role": "assistant", "content": content})
                rewritten_idx += 1

        output = {"status": status}
        for key in trajectory:
            if key not in ("turns", "rewrite_failed"):
                output[key] = trajectory[key]
        output["turns"] = output_turns
        return output

    def _extract_json(self, text: str) -> Optional[str]:
        """
        Extract JSON from LLM response.

        The LLM is instructed to output ONLY a valid JSON object with no
        surrounding text or markdown. We try to parse it directly.

        Args:
            text: Raw LLM response

        Returns:
            JSON string, or None if parsing fails
        """
        text = text.strip()
        if not text:
            return None

        # Try to parse the entire response as JSON directly
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "assistant_turns" in parsed:
                return text
            if isinstance(parsed, dict) and "turns" in parsed:
                return text
        except json.JSONDecodeError:
            pass

        # Try to find ```json ... ``` block and parse it
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            candidate = match.group(1).strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        return None

    def process_trajectory(
        self,
        trajectory_file: str,
        instruction: str,
        key_info_files: list[str],
        output_file: str,
    ) -> None:
        """
        Process a single trajectory file

        Args:
            trajectory_file: Original trajectory file path
            instruction: Task instruction
            key_info_files: List of key_info.txt file paths
            output_file: Output file path
        """
        # Read trajectory
        with open(trajectory_file, "r", encoding="utf-8") as f:
            trajectory = json.load(f)

        # Read key information file contents
        key_info_contents = []
        for f_path in key_info_files:
            if os.path.exists(f_path):
                with open(f_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        key_info_contents.append(content)

        # Rewrite
        rewritten = self.rewrite(trajectory, instruction, key_info_contents)

        # Save
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rewritten, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved rewritten trajectory -> {output_file}")
