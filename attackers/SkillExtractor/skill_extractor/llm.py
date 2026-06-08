"""Minimal OpenAI-compatible client for the SkillExtractor baseline."""

from __future__ import annotations

import json
import os
import shlex
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_envrc(path: Path) -> None:
    """Load simple KEY=VALUE or export KEY=VALUE lines from .envrc if unset."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        try:
            parsed = shlex.split(value, posix=True)
            os.environ[key] = parsed[0] if parsed else ""
        except ValueError:
            os.environ[key] = value.strip().strip("\"'")


def call_openai_compatible(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    base_url: str,
    api_key: str,
    wire_api: str = "chat",
    timeout: int = 180,
    json_mode: bool = False,
    max_retries: int = 2,
    on_retry: str = "",
) -> str:
    """Call an OpenAI-compatible endpoint and return response text.

    On JSON parse failure, retries up to max_retries times with a correction prompt.
    """
    from .schema import parse_distiller_response as _parse

    last_error = None
    correction_hint = on_retry

    for attempt in range(max_retries + 1):
        try:
            response_text = _call_openai_compatible_impl(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model,
                base_url=base_url,
                api_key=api_key,
                wire_api=wire_api,
                timeout=timeout,
                json_mode=json_mode,
                correction_hint=correction_hint,
            )
            _parse(response_text)
            return response_text
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            correction_hint = (
                f"The previous response could not be parsed. "
                f"Error: {exc}. "
                f"Return ONLY valid JSON matching the required schema — no markdown fences, no explanations."
            )

    raise RuntimeError(
        f"LLM response failed to parse after {max_retries + 1} attempts: {last_error}"
    ) from last_error


def _call_openai_compatible_impl(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    base_url: str,
    api_key: str,
    wire_api: str = "chat",
    timeout: int = 180,
    json_mode: bool = False,
    correction_hint: str = "",
) -> str:
    """Internal: single LLM call, optionally appending a correction hint to the user prompt."""
    wire_api = wire_api.strip().lower()
    if wire_api not in {"chat", "responses"}:
        raise ValueError("--wire-api must be chat or responses")

    user_prompt_final = user_prompt
    if correction_hint:
        user_prompt_final = (
            user_prompt
            + "\n\n"
            + f"<parser_reminder>{correction_hint}</parser_reminder>"
        )

    if wire_api == "responses":
        return _call_responses_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt_final,
            model=model,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )
    return _call_chat_completions(
        system_prompt=system_prompt,
        user_prompt=user_prompt_final,
        model=model,
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
        json_mode=json_mode,
    )


def _post_json(url: str, payload: dict[str, Any], api_key: str, timeout: int) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM request failed with HTTP {exc.code}: {body}") from exc
    return json.loads(body)


def _call_chat_completions(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    base_url: str,
    api_key: str,
    timeout: int,
    json_mode: bool,
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    result = _post_json(
        f"{base_url.rstrip('/')}/chat/completions",
        payload,
        api_key,
        timeout,
    )
    return result["choices"][0]["message"]["content"]


def _call_responses_api(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str,
    base_url: str,
    api_key: str,
    timeout: int,
) -> str:
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_prompt}],
            },
        ],
    }
    result = _post_json(f"{base_url.rstrip('/')}/responses", payload, api_key, timeout)
    if isinstance(result.get("output_text"), str):
        return result["output_text"]
    texts: list[str] = []
    for item in result.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                texts.append(text)
    if not texts:
        raise RuntimeError(f"Could not extract text from Responses API result: {result}")
    return "\n".join(texts)
