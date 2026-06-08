#!/usr/bin/env python3
"""
LaTeX formula sanity checker and minimal normalizer for `$$ ... $$` lines.

- Checks bracket balance: (), [], {}
- Checks \left/\right pairing and can normalize mismatches
- Removes trailing punctuation (.,;: ,) after the formula
- Normalizes common glyphs: unicode minus to '-', middle dot to \cdot

Usage:
  # Validate a file of $$...$$ lines
  python scripts/latex_sanity.py --file formulas.md --suggest-fixes

  # Validate a single formula string (without $$)
  python scripts/latex_sanity.py --formula "\frac{a}{b} = c"

Notes:
- Produces conservative suggestions. You must review any fix.
- Only for syntax/typo hygiene; does not change mathematical meaning.
"""

import argparse
import re
import sys
from typing import List, Tuple

PUNCT_TAIL_RE = re.compile(r"[\s]*[.,;:]+$")
LEFT_RE = re.compile(r"\\left(\s*[-()\[\]\{\}|<>])")
RIGHT_RE = re.compile(r"\\right(\s*[-()\[\]\{\}|<>])")


def strip_dollars(line: str) -> str:
    s = line.strip()
    if s.startswith("$$") and s.endswith("$$") and len(s) >= 4:
        return s[2:-2].strip()
    return s


def add_dollars(s: str) -> str:
    return f"$${s}$$"


def normalize_glyphs(s: str) -> str:
    # Common unicode to LaTeX-safe forms
    s = s.replace("−", "-")  # minus
    s = s.replace("–", "-")
    s = s.replace("—", "-")
    s = s.replace("·", "\\cdot ")
    s = s.replace("⋅", "\\cdot ")
    return s


def strip_trailing_punct(s: str) -> str:
    return PUNCT_TAIL_RE.sub("", s.rstrip())


def check_balanced_brackets(s: str) -> Tuple[bool, str]:
    pairs = {')': '(', ']': '[', '}': '{'}
    opens = set(pairs.values())
    stack: List[str] = []

    for ch in s:
        if ch in opens:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False, f"Unbalanced or mismatched bracket near '{ch}'"
            stack.pop()
    if stack:
        return False, "Unbalanced: missing closing bracket(s)"
    return True, "OK"


def left_right_counts(s: str) -> Tuple[int, int]:
    left = len(LEFT_RE.findall(s))
    right = len(RIGHT_RE.findall(s))
    return left, right


def normalize_left_right(s: str) -> str:
    # If counts mismatch, remove all \left/\right conservatively
    l, r = left_right_counts(s)
    if l != r and (l > 0 or r > 0):
        s = re.sub(r"\\left\s*", "", s)
        s = re.sub(r"\\right\s*", "", s)
    return s


def has_math_tokens(s: str) -> bool:
    return any(tok in s for tok in ["=", "+", "-", "*", "/", "^", "_", "\\"])


def sanitize_formula_inner(s: str, suggest_fixes: bool = False) -> Tuple[bool, str, str]:
    original = s
    s = normalize_glyphs(s)
    s = strip_trailing_punct(s)
    s = normalize_left_right(s)
    ok, msg = check_balanced_brackets(s)
    if not ok and suggest_fixes:
        # As a minimal attempt, if there's an obvious missing closing brace, append one set.
        # This is intentionally conservative.
        if msg.startswith("Unbalanced: missing closing"):
            s_fixed = s + "}"
            ok2, msg2 = check_balanced_brackets(s_fixed)
            if ok2:
                return True, msg2, s_fixed
        return False, msg, s
    return ok, msg, s


def process_line(line: str, suggest_fixes: bool = False) -> Tuple[bool, str, str, str]:
    # Returns: ok, message, original_line, maybe_fixed_line
    inner = strip_dollars(line)
    if not inner:
        return False, "Empty formula content", line, ""
    if not has_math_tokens(inner):
        return False, "Likely not a standalone formula (no math tokens)", line, ""
    ok, msg, sanitized = sanitize_formula_inner(inner, suggest_fixes=suggest_fixes)
    out_line = add_dollars(inner)
    fixed_line = add_dollars(sanitized) if sanitized != inner else ""
    return ok, msg, out_line, (fixed_line if suggest_fixes else "")


def main():
    ap = argparse.ArgumentParser(description="LaTeX formula sanity checker for $$...$$ lines")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="Path to a file containing $$...$$ lines")
    g.add_argument("--formula", help="Single formula string WITHOUT $$ delimiters")
    ap.add_argument("--suggest-fixes", action="store_true", help="Propose minimal fixes for syntax issues")
    args = ap.parse_args()

    lines = []
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f]
        except Exception as e:
            print(f"ERROR: Cannot read file: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        lines = [add_dollars(args.formula)]

    any_error = False
    for ln in lines:
        ok, msg, out_line, fixed = process_line(ln, suggest_fixes=args.suggest_fixes)
        status = "OK" if ok else "ERROR"
        print(f"{status}: {msg}")
        print(out_line)
        if fixed and fixed != out_line:
            print(fixed)
        if not ok:
            any_error = True

    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
