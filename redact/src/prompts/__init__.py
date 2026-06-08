"""Prompt templates for key info extraction and trajectory rewriting"""

from .key_info_extraction import TASK_DESCRIPTION as KEY_INFO_EXTRACTION_PROMPT
from .rewriter import REWRITER_PROMPT
from .generic_rewriter import GENERIC_REWRITER_PROMPT

__all__ = [
    "KEY_INFO_EXTRACTION_PROMPT",
    "REWRITER_PROMPT",
    "GENERIC_REWRITER_PROMPT",
]
