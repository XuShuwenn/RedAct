#!/usr/bin/env python3
"""
Category path standardization utilities.

Functions to normalize hierarchical category paths before embedding/clustering.
Designed to be dependency-light and dataset-agnostic.

Usage examples:
  from scripts.path_tools import normalize_path, split_levels
  s = normalize_path('Electronics / Computers→Laptops')
  levels = split_levels(s, max_levels=5)
"""

import re
from typing import List

# Map common hierarchy delimiters to a single canonical delimiter ' > '
DELIM_PATTERNS = [
    r">", r"/", r"\\u203a", r"→", r"->", r"»", r"\u00bb"
]

DELIM_REGEX = re.compile(r"\s*(?:" + "|".join(DELIM_PATTERNS) + r")\s*")

# Keep alphanumerics and spaces in tokens
TOKEN_CLEAN = re.compile(r"[^0-9a-zA-Z\s]+")


def normalize_path(path: str, delimiter: str = ' > ') -> str:
    """Normalize a category path:
    - unify delimiters to ' > '
    - trim tokens, lowercase, remove extraneous punctuation
    - collapse whitespace
    """
    if not isinstance(path, str):
        return ''
    # Unify delimiters
    tmp = DELIM_REGEX.sub(delimiter, path)
    # Split and clean tokens
    raw_tokens = [t.strip() for t in tmp.split(delimiter) if t.strip()]
    cleaned = []
    for t in raw_tokens:
        t = TOKEN_CLEAN.sub(' ', t.lower())
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            cleaned.append(t)
    return f" {delimiter} ".join(cleaned) if cleaned else ''


def split_levels(path: str, delimiter: str = ' > ', max_levels: int = 5) -> List[str]:
    """Split a normalized path into up to max_levels tokens.
    Expects a path already processed by normalize_path.
    """
    if not path:
        return []
    tokens = [t.strip() for t in path.split(delimiter) if t.strip()]
    return tokens[:max_levels]


def compute_depth(path: str, delimiter: str = ' > ') -> int:
    """Return depth based on number of non-empty tokens in the normalized path."""
    return len(split_levels(path, delimiter=delimiter, max_levels=999))


if __name__ == '__main__':
    examples = [
        'Electronics / Computers→Laptops',
        'Home> Kitchen  >> Appliances',
        '  Toys  /   Baby   / Strollers ',
        None,
    ]
    for ex in examples:
        norm = normalize_path(ex or '')
        print(f'IN : {ex!r}')
        print(f'OUT: {norm!r}')
        print(f'LVL: {split_levels(norm)} depth={compute_depth(norm)}')
        print('-'*40)
