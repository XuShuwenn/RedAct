#!/usr/bin/env python3
"""Smith-Waterman local alignment with affine gap penalties.

This script computes the local alignment score between two sequences using
three-state DP (match/mismatch, gap in seq1, gap in seq2) and affine gaps.

Usage:
  # Provide sequences directly
  python scripts/smith_waterman.py --seq1 ACTG --seq2 ACTG \
      --match 2 --mismatch -1 --gap-open -2 --gap-extend -1

  # Read sequences from a file (two lines)
  python scripts/smith_waterman.py --file input.txt \
      --match 2 --mismatch -1 --gap-open -2 --gap-extend -1 --label "Alignment score: "

Output:
  Prints the best local alignment score (integer). If --label is provided,
  the line is prefixed by that label.
"""

import argparse
import sys
from typing import Tuple


def smith_waterman_affine(seq1: str, seq2: str, match: int = 2, mismatch: int = -1,
                          gap_open: int = -2, gap_extend: int = -1) -> int:
    """Compute Smith-Waterman local alignment score with affine gaps.

    Uses three DP matrices:
      - M[i][j]: best score ending with a match/mismatch at i,j
      - Ix[i][j]: best score ending with a gap in seq2 (advance i)
      - Iy[i][j]: best score ending with a gap in seq1 (advance j)

    Recurrence (local alignment floor at zero):
      s = match if seq1[i-1] == seq2[j-1] else mismatch
      M[i][j]  = max(0, max(M[i-1][j-1], Ix[i-1][j-1], Iy[i-1][j-1]) + s)
      Ix[i][j] = max(0, M[i-1][j] + gap_open + gap_extend, Ix[i-1][j] + gap_extend)
      Iy[i][j] = max(0, M[i][j-1] + gap_open + gap_extend, Iy[i][j-1] + gap_extend)

    Returns the best score across all cells.
    """
    m, n = len(seq1), len(seq2)
    if m == 0 or n == 0:
        return 0

    # Initialize matrices with zeros (local alignment resets negatives to 0).
    M = [[0] * (n + 1) for _ in range(m + 1)]
    Ix = [[0] * (n + 1) for _ in range(m + 1)]
    Iy = [[0] * (n + 1) for _ in range(m + 1)]

    best = 0
    for i in range(1, m + 1):
        a = seq1[i - 1]
        for j in range(1, n + 1):
            b = seq2[j - 1]
            s = match if a == b else mismatch

            # Match/mismatch state from any diagonal predecessor
            m_from_diag = max(M[i - 1][j - 1], Ix[i - 1][j - 1], Iy[i - 1][j - 1]) + s
            M[i][j] = max(0, m_from_diag)

            # Gap in seq2 (advance i; j stays) - insertion relative to seq1
            Ix[i][j] = max(
                0,
                M[i - 1][j] + gap_open + gap_extend,
                Ix[i - 1][j] + gap_extend,
            )

            # Gap in seq1 (advance j; i stays) - deletion relative to seq1
            Iy[i][j] = max(
                0,
                M[i][j - 1] + gap_open + gap_extend,
                Iy[i][j - 1] + gap_extend,
            )

            cell_best = M[i][j] if M[i][j] >= Ix[i][j] else Ix[i][j]
            if Iy[i][j] > cell_best:
                cell_best = Iy[i][j]
            if cell_best > best:
                best = cell_best

    return int(best)


def read_two_sequences_from_file(path: str) -> Tuple[str, str]:
    """Read exactly two lines from a file, stripping trailing newlines and spaces."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except Exception as e:
        print(f"ERROR: failed to read file '{path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Remove trailing newlines and surrounding spaces
    lines = [ln.strip() for ln in lines if ln.strip() != ""]
    if len(lines) < 2:
        print("ERROR: input file must contain at least two non-empty lines for sequences.", file=sys.stderr)
        sys.exit(1)
    return lines[0], lines[1]


def main():
    p = argparse.ArgumentParser(description="Smith-Waterman local alignment with affine gap penalties")
    g_in = p.add_mutually_exclusive_group(required=True)
    g_in.add_argument("--file", help="Path to file containing two sequences (one per line)")
    g_in.add_argument("--seq1", help="First sequence")
    p.add_argument("--seq2", help="Second sequence (required if --seq1 is used)")

    p.add_argument("--match", type=int, default=2, help="Match score (default: 2)")
    p.add_argument("--mismatch", type=int, default=-1, help="Mismatch score (default: -1)")
    p.add_argument("--gap-open", type=int, default=-2, help="Gap opening penalty (default: -2)")
    p.add_argument("--gap-extend", type=int, default=-1, help="Gap extension penalty (default: -1)")
    p.add_argument("--label", default=None, help="Optional label prefix for output, e.g., 'Alignment score: '")

    args = p.parse_args()

    if args.file:
        s1, s2 = read_two_sequences_from_file(args.file)
    else:
        if not args.seq2:
            print("ERROR: --seq2 is required when using --seq1", file=sys.stderr)
            sys.exit(1)
        s1, s2 = args.seq1.strip(), args.seq2.strip()

    score = smith_waterman_affine(
        s1, s2, match=args.match, mismatch=args.mismatch,
        gap_open=args.gap_open, gap_extend=args.gap_extend
    )

    if args.label is not None:
        print(f"{args.label}{score}")
    else:
        print(score)


if __name__ == "__main__":
    main()
