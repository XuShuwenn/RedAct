#!/usr/bin/env python3
"""
Guard auditor for stateful protocol handlers.

Purpose:
  Help identify handler code blocks that process side-effecting messages
  without a nearby authentication/connected-state guard.

This tool is language-agnostic and works via regex proximity:
  - Find lines matching a handler pattern (e.g., functions/clauses that
    process side-effecting messages like channel open/request/exec).
  - In a configurable window around each match, search for a guard pattern
    that indicates an authentication/connected-state check.
  - Report potential missing guards.

Example usage:
  python scripts/guard_audit.py \
      --root path/to/src \
      --handler-pattern "channel_.*request|open.*channel" \
      --guard-pattern "auth|connected|state.*authenticated" \
      --window-back 20 --window-forward 5 --ci

Arguments:
  --root: Root directory to scan (recursively)
  --files: Optional explicit file paths (space-separated). If given,
           only these files are scanned. Can be mixed with --root.
  --include-ext: Comma-separated list of file extensions to include
                 (e.g., ".erl,.ex,.go,.py"). If omitted, all files are scanned.
  --handler-pattern: Regex indicating lines that define or handle
                     side-effecting messages.
  --guard-pattern: Regex indicating an authentication/connected-state guard.
  --window-back: Number of lines to look backwards from a handler match.
  --window-forward: Number of lines to look forwards from a handler match.
  --ignore-pattern: Optional regex to skip matches (e.g., commented lines).
  --ci: Exit with code 1 if any unguarded handler matches are found.

Limitations:
  - Regex proximity is a heuristic; review findings manually.
  - Choose patterns that reflect your codebase naming and guard idioms.
"""

import argparse
import os
import re
import sys
from typing import List, Optional, Tuple


def iter_files(root: Optional[str], files: List[str], include_ext: Optional[List[str]]) -> List[str]:
    paths = []
    if files:
        for f in files:
            if os.path.isfile(f):
                paths.append(f)
    if root and os.path.isdir(root):
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                path = os.path.join(dirpath, name)
                if include_ext:
                    if any(name.endswith(ext) for ext in include_ext):
                        paths.append(path)
                else:
                    paths.append(path)
    # De-duplicate while preserving order
    seen = set()
    uniq = []
    for p in paths:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq


def read_lines(path: str) -> Optional[List[str]]:
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return fh.readlines()
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding='latin-1') as fh:
                return fh.readlines()
        except Exception:
            return None
    except Exception:
        return None


def find_matches(lines: List[str], pat: re.Pattern, ignore: Optional[re.Pattern]) -> List[int]:
    idxs = []
    for i, line in enumerate(lines):
        if ignore and ignore.search(line):
            continue
        if pat.search(line):
            idxs.append(i)
    return idxs


def has_guard_near(lines: List[str], idx: int, guard_pat: re.Pattern, back: int, fwd: int) -> bool:
    start = max(0, idx - back)
    end = min(len(lines), idx + fwd + 1)
    for j in range(start, end):
        if guard_pat.search(lines[j]):
            return True
    return False


def snippet(lines: List[str], center: int, radius: int = 3) -> str:
    start = max(0, center - radius)
    end = min(len(lines), center + radius + 1)
    out = []
    for i in range(start, end):
        prefix = '>' if i == center else ' '
        out.append(f"{prefix}{i+1:6d}: {lines[i].rstrip()}\n")
    return ''.join(out)


def audit_file(path: str, handler_pat: re.Pattern, guard_pat: re.Pattern,
               ignore_pat: Optional[re.Pattern], back: int, fwd: int) -> List[Tuple[int, str]]:
    lines = read_lines(path)
    if lines is None:
        return []
    hits = []
    handler_idxs = find_matches(lines, handler_pat, ignore_pat)
    for idx in handler_idxs:
        if not has_guard_near(lines, idx, guard_pat, back, fwd):
            hits.append((idx, snippet(lines, idx)))
    return hits


def main():
    ap = argparse.ArgumentParser(description="Audit handlers for missing pre-auth guards via regex proximity.")
    ap.add_argument('--root', type=str, default=None, help='Root directory to scan recursively')
    ap.add_argument('--files', nargs='*', default=[], help='Explicit file paths to scan')
    ap.add_argument('--include-ext', type=str, default=None, help='Comma-separated file extensions filter (e.g., .erl,.go,.py)')
    ap.add_argument('--handler-pattern', type=str, required=True, help='Regex for side-effecting handler lines')
    ap.add_argument('--guard-pattern', type=str, required=True, help='Regex for authentication/connected-state guard lines')
    ap.add_argument('--ignore-pattern', type=str, default=None, help='Regex for lines to ignore (e.g., comments)')
    ap.add_argument('--window-back', type=int, default=15, help='Lines to search backward from handler')
    ap.add_argument('--window-forward', type=int, default=5, help='Lines to search forward from handler')
    ap.add_argument('--ci', action='store_true', help='Exit with non-zero code if any unguarded handlers found')
    args = ap.parse_args()

    include_ext = [e.strip() for e in args.include_ext.split(',')] if args.include_ext else None
    handler_pat = re.compile(args.handler_pattern)
    guard_pat = re.compile(args.guard_pattern)
    ignore_pat = re.compile(args.ignore_pattern) if args.ignore_pattern else None

    files = iter_files(args.root, args.files, include_ext)
    if not files:
        print('No files to scan', file=sys.stderr)
        sys.exit(2)

    total_hits = 0
    for path in files:
        hits = audit_file(path, handler_pat, guard_pat, ignore_pat, args.window_back, args.window_forward)
        if hits:
            total_hits += len(hits)
            for idx, snip in hits:
                print(f"[MISSING GUARD] {path}:{idx+1}")
                print(snip)

    if args.ci and total_hits > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
