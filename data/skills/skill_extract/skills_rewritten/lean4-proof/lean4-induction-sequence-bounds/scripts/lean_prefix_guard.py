#!/usr/bin/env python3
"""
lean_prefix_guard.py

Compare the first N lines of two files (e.g., a reference template and the
current working file) to ensure the prefix has not been modified.

Usage:
  python scripts/lean_prefix_guard.py --reference path/to/reference.lean \
                                      --target path/to/solution.lean \
                                      --lines 15

Exit codes:
  0: Prefix matches
  1: Invalid inputs or usage
  2: Prefix differs
"""

import argparse
import sys
from pathlib import Path


def read_prefix(path: Path, n: int) -> list[str]:
    with path.open('r', encoding='utf-8') as f:
        lines = []
        for _ in range(n):
            line = f.readline()
            if line == '':
                break
            lines.append(line)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that first N lines match between two files.")
    parser.add_argument("--reference", required=True, help="Path to reference file")
    parser.add_argument("--target", required=True, help="Path to target file")
    parser.add_argument("--lines", required=True, type=int, help="Number of lines to compare")
    args = parser.parse_args()

    ref_path = Path(args.reference)
    tgt_path = Path(args.target)

    if not ref_path.exists() or not tgt_path.exists():
        print("ERROR: Reference or target file does not exist.", file=sys.stderr)
        return 1
    if args.lines <= 0:
        print("ERROR: --lines must be positive.", file=sys.stderr)
        return 1

    ref_prefix = read_prefix(ref_path, args.lines)
    tgt_prefix = read_prefix(tgt_path, args.lines)

    if ref_prefix == tgt_prefix:
        print(f"OK: First {args.lines} lines match.")
        return 0

    print(f"DIFFER: First {args.lines} lines differ:")
    max_len = max(len(ref_prefix), len(tgt_prefix))
    for i in range(max_len):
        r = ref_prefix[i].rstrip('\n') if i < len(ref_prefix) else '<EOF>'
        t = tgt_prefix[i].rstrip('\n') if i < len(tgt_prefix) else '<EOF>'
        status = '==' if r == t else '!='
        print(f"{i+1:>4}: {status} | REF: {r}")
        if status != '==':
            print(f"      TGT: {t}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
