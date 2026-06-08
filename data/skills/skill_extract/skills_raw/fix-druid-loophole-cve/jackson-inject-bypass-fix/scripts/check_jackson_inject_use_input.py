#!/usr/bin/env python3
"""
Scan a Java repository for @JacksonInject usages and flag sites lacking
useInput = OptBoolean.FALSE hardening.

Usage:
  python3 scripts/check_jackson_inject_use_input.py --root /path/to/repo [--extensions .java]

Notes:
- The check is heuristic but effective for most code styles.
- It searches for lines containing '@JacksonInject' and inspects the same
  line or the following annotation parameter block for 'useInput'.
- Results help ensure you patched all relevant sites.
"""

import argparse
import os
import re
from typing import Iterator, Tuple

INJECT_RE = re.compile(r"@JacksonInject\b")
USEINPUT_RE = re.compile(r"useInput\s*=")
ANNOTATION_OPEN_RE = re.compile(r"@JacksonInject\s*\(")


def iter_java_files(root: str, exts=('.java',)) -> Iterator[str]:
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(exts):
                yield os.path.join(dirpath, fn)


def find_unhardened_sites(path: str) -> Iterator[Tuple[int, str]]:
    """Yield (line_no, line_text) for @JacksonInject without useInput."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()
    except Exception:
        return

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if INJECT_RE.search(line):
            # Quick pass: if line contains useInput, it's fine
            if USEINPUT_RE.search(line):
                i += 1
                continue
            # If annotation opens here, scan until closing paren or reasonable bound
            if '(' in line and ')' not in line:
                j = i + 1
                found = USEINPUT_RE.search(line) is not None
                # scan at most next 6 lines to cover typical annotation wrap
                limit = min(n, i + 7)
                while j < limit and not found:
                    if USEINPUT_RE.search(lines[j]):
                        found = True
                        break
                    if ')' in lines[j]:
                        break
                    j += 1
                if not found:
                    yield (i + 1, line.rstrip())
                i = j
            else:
                # No parameter list detected; likely missing useInput
                yield (i + 1, line.rstrip())
        i += 1


def main():
    ap = argparse.ArgumentParser(description="Check @JacksonInject hardening")
    ap.add_argument("--root", required=True, help="Repository root to scan")
    ap.add_argument("--extensions", nargs='*', default=['.java'], help="File extensions to include")
    args = ap.parse_args()

    total = 0
    issues = 0
    for fp in iter_java_files(args.root, tuple(args.extensions)):
        file_issues = list(find_unhardened_sites(fp))
        if file_issues:
            print(f"[!] {fp}")
            for ln, text in file_issues:
                print(f"    line {ln}: {text}")
            issues += len(file_issues)
        total += 1

    print(f"\nScanned files: {total}")
    if issues == 0:
        print("All @JacksonInject sites appear hardened (no missing useInput detected).")
    else:
        print(f"Potential unhardened @JacksonInject occurrences: {issues}")
        exit(2)


if __name__ == "__main__":
    main()
