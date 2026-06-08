#!/usr/bin/env python3
"""Apply the local codex-acp verbosity workaround to installed benchflow.

Why this exists:
  Codex CLI may serialize Responses requests with text.verbosity="low" by
  default. Some OpenAI-compatible relays route that request shape incorrectly
  for gpt-5.2-codex. In this environment, model_verbosity="medium" avoids the
  bad route while preserving normal Codex behavior.

Run after reinstalling or upgrading benchflow:
  ./.venv/bin/python patch_codex_acp_verbosity.py

The patch is idempotent and only touches benchflow's installed
agents/codex_acp_launcher.py in the active Python environment.
"""

from __future__ import annotations

import importlib.util
import py_compile
from pathlib import Path


NEEDLE_WIRE_API = '    wire_api = _resolve("CODEX_WIRE_API") or "responses"\n'
PATCH_MODEL_VERBOSITY = (
    NEEDLE_WIRE_API
    + "    # Some OpenAI-compatible relays mis-route Codex requests when the CLI's\n"
    + '    # default low verbosity is serialized as `text.verbosity = "low"`.\n'
    + '    model_verbosity = _resolve("CODEX_MODEL_VERBOSITY") or "medium"\n'
)

NEEDLE_CONFIG_LINE = '            f\'model_provider = "{provider_name}",\'\n'
PATCH_CONFIG_LINE = (
    NEEDLE_CONFIG_LINE
    + '            f\'model_verbosity = "{model_verbosity}",\'\n'
)


def launcher_path() -> Path:
    spec = importlib.util.find_spec("benchflow.agents.codex_acp_launcher")
    if spec is None or spec.origin is None:
        raise SystemExit(
            "Could not find benchflow.agents.codex_acp_launcher. "
            "Run this with the CapTraceBench virtualenv Python."
        )
    return Path(spec.origin)


def apply_patch(path: Path) -> bool:
    text = path.read_text()
    updated = text

    if 'model_verbosity = _resolve("CODEX_MODEL_VERBOSITY")' not in updated:
        if NEEDLE_WIRE_API not in updated:
            raise SystemExit(
                "Could not find CODEX_WIRE_API assignment; launcher layout changed."
            )
        updated = updated.replace(NEEDLE_WIRE_API, PATCH_MODEL_VERBOSITY, 1)

    if 'model_verbosity = "{model_verbosity}"' not in updated:
        if NEEDLE_CONFIG_LINE not in updated:
            raise SystemExit(
                "Could not find model_provider config line; launcher layout changed."
            )
        updated = updated.replace(NEEDLE_CONFIG_LINE, PATCH_CONFIG_LINE, 1)

    if updated == text:
        return False

    backup = path.with_suffix(path.suffix + ".bak.codex-verbosity")
    if not backup.exists():
        backup.write_text(text)

    path.write_text(updated)
    py_compile.compile(str(path), doraise=True)
    return True


def main() -> int:
    path = launcher_path()
    changed = apply_patch(path)
    status = "patched" if changed else "already patched"
    print(f"{status}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
