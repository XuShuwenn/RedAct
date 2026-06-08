#!/usr/bin/env python3
"""
math_formula_guard.py

Purpose:
  - Safely sanitize and validate LaTeX math formulas before writing them in $$...$$ blocks.
  - Prevents common pitfalls: trailing punctuation, broken brackets, and shell-quoting artifacts.

Usage:
  - Read from a file and write a $$-wrapped output file:
      python3 scripts/math_formula_guard.py --input formulas_raw.txt --output /root/latex_formula_extraction.md
  - Read from stdin and write output:
      cat formulas_raw.txt | python3 scripts/math_formula_guard.py --stdin --output /root/latex_formula_extraction.md

Notes:
  - The script removes only trailing punctuation/number tags at the very end of each formula.
  - The script does not change mathematical structure or "normalize" formulas.
  - If bracket or \left/\right imbalances are detected, it reports them to stderr for manual review.
"""

import argparse
import re
import sys
from typing import List, Tuple

TRAILING_PUNCT_RE = re.compile(r"\s*([.,;:，。、]+)\s*$")
TRAILING_EQNUM_RE = re.compile(r"\s*\(([ \t]*\d+[ \t]*|[A-Za-z]\d+)\)\s*$")  # e.g., (1), (A1)
DOLLAR_WRAP_RE = re.compile(r"^\s*\${1,2}\s*(.*?)\s*\${1,2}\s*$")

# Basic mapping of a few common Unicode math symbols to LaTeX equivalents (optional, minimal)
UNICODE_TO_LATEX = {
    '\u00D7': r"\\times",  # ×
    '\u00B1': r"\\pm",     # ±
    '\u2264': r"\\le",     # ≤
    '\u2265': r"\\ge",     # ≥
}

QUOTE_ARTIFACT_CHARS = set(["'", '`', '\u2018', '\u2019', '\u201C', '\u201D'])

LEFT_CMD_RE = re.compile(r"\\left\b")
RIGHT_CMD_RE = re.compile(r"\\right\b")


def strip_dollars(s: str) -> str:
    m = DOLLAR_WRAP_RE.match(s)
    return m.group(1) if m else s.strip()


def strip_trailing_punct_and_tags(s: str) -> str:
    # Remove trailing equation number tags like "(1)" or "(A1)" at the very end
    s = TRAILING_EQNUM_RE.sub("", s)
    # Remove trailing punctuation at the very end
    s = TRAILING_PUNCT_RE.sub("", s)
    return s.strip()


def replace_unicode_math(s: str) -> str:
    # Replace minimal set of common math Unicode symbols with LaTeX
    return ''.join(UNICODE_TO_LATEX.get(ch, ch) for ch in s)


def check_bracket_balance(s: str) -> Tuple[bool, str]:
    pairs = {')': '(', ']': '[', '}': '{'}
    opening = set(pairs.values())
    stack = []
    i = 0
    while i < len(s):
        ch = s[i]
        # skip escaped braces like \{ or \}
        if ch == '\\' and i + 1 < len(s):
            i += 2
            continue
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False, f"Mismatched bracket near position {i}: '{ch}'"
            stack.pop()
        i += 1
    if stack:
        return False, "Unclosed bracket(s): " + ''.join(stack)
    return True, "OK"


def check_left_right_balance(s: str) -> Tuple[bool, str]:
    left = len(LEFT_CMD_RE.findall(s))
    right = len(RIGHT_CMD_RE.findall(s))
    if left != right:
        return False, f"Unbalanced \\left/\\right: left={left}, right={right}"
    return True, "OK"


def detect_quote_artifacts(s: str) -> Tuple[bool, str]:
    # Flag presence of quote-like characters that often leak from shell here-docs
    found = [ch for ch in s if ch in QUOTE_ARTIFACT_CHARS]
    if found:
        return False, f"Suspicious quote characters found: {''.join(sorted(set(found)))}"
    return True, "OK"


def sanitize_formula(s: str) -> str:
    s0 = s.rstrip('\n')
    s1 = strip_dollars(s0)
    s2 = strip_trailing_punct_and_tags(s1)
    s3 = replace_unicode_math(s2)
    # collapse internal whitespace minimally (keep as-is except trim ends)
    return s3.strip()


def wrap_dollars(s: str) -> str:
    return f"$${s}$$"


def process_lines(lines: List[str]) -> Tuple[List[str], List[str]]:
    """Return (wrapped_sanitized_formulas, warnings)"""
    out = []
    warnings = []
    for idx, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        f = sanitize_formula(raw)
        ok1, msg1 = check_bracket_balance(f)
        if not ok1:
            warnings.append(f"Line {idx}: {msg1}")
        ok2, msg2 = check_left_right_balance(f)
        if not ok2:
            warnings.append(f"Line {idx}: {msg2}")
        ok3, msg3 = detect_quote_artifacts(f)
        if not ok3:
            warnings.append(f"Line {idx}: {msg3}")
        out.append(wrap_dollars(f))
    return out, warnings


def main():
    ap = argparse.ArgumentParser(description="Sanitize and validate LaTeX math formulas, then write $$-wrapped lines.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--input', help='Path to a text file with one formula per line')
    src.add_argument('--stdin', action='store_true', help='Read formulas from stdin (one per line)')
    ap.add_argument('--output', required=True, help='Path to write $$-wrapped formulas')
    args = ap.parse_args()

    if args.stdin:
        lines = sys.stdin.read().splitlines()
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()

    wrapped, warnings = process_lines(lines)

    with open(args.output, 'w', encoding='utf-8') as f:
        for w in wrapped:
            f.write(w)
            f.write('\n')

    if warnings:
        print("Validation warnings:", file=sys.stderr)
        for w in warnings:
            print("- ", w, file=sys.stderr)
        print("Review and append fixed versions if you can safely correct syntax issues.", file=sys.stderr)


if __name__ == '__main__':
    main()
