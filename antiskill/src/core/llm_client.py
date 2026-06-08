"""LLM Client Module"""

import os
import logging
from typing import Optional

from openai import OpenAI

from ..utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM API client wrapper (OpenAI compatible interface)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-5",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout: int = 120,
    ):
        """
        Initialize LLM client

        Args:
            api_key: API key, defaults to OPENAI_API_KEY env variable
            base_url: API base URL, defaults to OPENAI_BASE_URL env variable
            model: Model name
            temperature: Temperature parameter
            max_tokens: Maximum token count
            timeout: Timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY") or "EMPTY"
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or "http://localhost:8000/v1"
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    @classmethod
    def from_config(cls) -> "LLMClient":
        """Create LLMClient from config file."""
        config = ConfigLoader.load()
        llm_cfg = config.get("llm", {})
        return cls(
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY") or "EMPTY",
            base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or "http://localhost:8000/v1",
            model=llm_cfg.get("model", "gpt-5"),
            temperature=llm_cfg.get("temperature", 0.0),
            max_tokens=llm_cfg.get("max_tokens", 4096),
            timeout=llm_cfg.get("timeout", 120),
        )

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Call LLM to get response

        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Temperature parameter (overrides default)
            max_tokens: Maximum token count (overrides default)

        Returns:
            LLM response text
        """
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise

    def extract_tag_content(self, text: str, tag: str) -> Optional[str]:
        """
        Extract content from specified tag in text

        Args:
            text: Original text
            tag: Tag name (e.g., 'key_info')

        Returns:
            Tag content, or None if not found
        """
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"

        start_idx = text.find(start_tag)
        if start_idx == -1:
            return None

        start_idx += len(start_tag)
        end_idx = text.find(end_tag, start_idx)

        if end_idx == -1:
            return None

        return text[start_idx:end_idx].strip()
