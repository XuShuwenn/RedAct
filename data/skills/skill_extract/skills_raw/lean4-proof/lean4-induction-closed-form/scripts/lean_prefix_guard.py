#!/usr/bin/env python3
"""
Lean prefix guard and simple scanner for restricted-tactic usage.

Usage examples:
  # Compare first N lines against a baseline copy
  python scripts/lean_prefix_guard.py --check-prefix \
      --baseline /path/to/baseline_solution.lean \
      --target /path/to/solution.lean \
      --lines 15

  # Scan for disallowed tactics in target file
  python scripts/lean_prefix_guard.py --scan --target /path/to/solution.lean \
      --banned field_simp

This utility encodes generic validation and does not depend on any one task.
"""

import argparse
import sys
from pathlib import Path


def check_prefix(baseline: Path, target: Path, lines: int) -> int:
    bl = baseline.read_text(encoding="utf-8").splitlines()
    tl = target.read_text(encoding="utf-8").splitlines()
    # Pad to length for short files
    blp = bl[:lines]
    tlp = tl[:lines]
    if blp == tlp:
        print(f"OK: First {lines} line(s) match baseline.")
        return 0
    else:
        print(f"MISMATCH: First {lines} line(s) differ between baseline and target.")
        for i, (b, t) in enumerate(zip(blp, tlp), start=1):
            if b != t:
                print(f"Line {i}:\n  baseline: {b!r}\n  target  : {t!r}")
        return 2


def scan_banned(target: Path, banned: list[str]) -> int:
    text = target.read_text(encoding="utf-8")
    bad = [w for w in banned if w in text]
    if bad:
        print("Found banned tokens:", ", ".join(bad))
        return 3
    print("OK: No banned tokens found.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Lean prefix guard and tactic scanner")
    p.add_argument("--check-prefix", action="store_true", help="Compare first N lines against baseline")
    p.add_argument("--baseline", type=Path, help="Baseline Lean file path")
    p.add_argument("--target", type=Path, required=True, help="Target Lean file path")
    p.add_argument("--lines", type=int, default=15, help="Number of lines to compare for prefix check")
    p.add_argument("--scan", action="store_true", help="Scan for banned tokens/tactics")
    p.add_argument("--banned", nargs="*", default=[], help="List of banned tokens (e.g., field_simp)")
    args = p.parse_args()

    rc = 0
    if args.check_prefix:
        if not args.baseline:
            print("ERROR: --baseline is required for --check-prefix", file=sys.stderr)
            return 1
        rc |= check_prefix(args.baseline, args.target, args.lines)
    if args.scan:
        rc |= scan_banned(args.target, args.banned)
    if not (args.check_prefix or args.scan):
        print("Nothing to do. Use --check-prefix and/or --scan.")
    sys.exit(rc)


if __name__ == "__main__":
    main()
