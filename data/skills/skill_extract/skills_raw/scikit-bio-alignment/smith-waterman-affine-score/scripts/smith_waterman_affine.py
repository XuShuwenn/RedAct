#!/usr/bin/env python3
"""
Smith–Waterman local alignment score with affine gap penalties.

Usage examples:
  - From sequences:
      python smith_waterman_affine.py --seq1 "ACGT" --seq2 "AGT"
  - With custom scoring:
      python smith_waterman_affine.py --seq1 s1 --seq2 s2 --match 2 --mismatch -1 --gap-open -2 --gap-extend -1
  - From file (first two non-empty lines are used as sequences):
      python smith_waterman_affine.py --input-file input.txt --emit-format

By default prints an integer score to stdout. With --emit-format, prints
"Alignment score: X" (with newline) for direct file writing use.
"""

import argparse
import sys
from typing import Tuple


def read_two_sequences_from_file(path: str) -> Tuple[str, str]:
    seqs = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s:
                seqs.append(s)
                if len(seqs) == 2:
                    break
    if len(seqs) < 2:
        raise ValueError("Input file must contain at least two non-empty lines.")
    return seqs[0], seqs[1]


def smith_waterman_affine_score(seq1: str, seq2: str, match: int = 2, mismatch: int = -1,
                                gap_open: int = -2, gap_extend: int = -1) -> int:
    """Compute local alignment score using Smith–Waterman with affine gaps.

    States per cell (i, j):
      M: alignment ends with a match/mismatch
      X: alignment ends with a gap in seq1 (insertion in seq2)
      Y: alignment ends with a gap in seq2 (insertion in seq1)

    Recurrence (with local alignment clamping to 0):
      s = match if seq1[i-1] == seq2[j-1] else mismatch
      M[i,j] = max(0, M[i-1,j-1] + s, X[i-1,j-1] + s, Y[i-1,j-1] + s)
      X[i,j] = max(0, M[i-1,j] + gap_open + gap_extend, X[i-1,j] + gap_extend)
      Y[i,j] = max(0, M[i,j-1] + gap_open + gap_extend, Y[i,j-1] + gap_extend)

    Returns the maximum value over all M, X, Y cells (non-negative integer).
    """
    if not isinstance(seq1, str) or not isinstance(seq2, str):
        raise TypeError("Sequences must be strings.")

    # Normalize case; equality determines match.
    a = seq1.strip().upper()
    b = seq2.strip().upper()

    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0

    # Previous row states
    prev_M = [0] * (m + 1)
    prev_X = [0] * (m + 1)
    prev_Y = [0] * (m + 1)

    max_score = 0

    for i in range(1, n + 1):
        curr_M = [0] * (m + 1)
        curr_X = [0] * (m + 1)
        curr_Y = [0] * (m + 1)

        ai = a[i - 1]
        for j in range(1, m + 1):
            s = match if ai == b[j - 1] else mismatch

            # M depends on previous row/column diagonals
            m_val = prev_M[j - 1] + s
            x_to_m = prev_X[j - 1] + s
            y_to_m = prev_Y[j - 1] + s
            m_val = max(0, m_val, x_to_m, y_to_m)

            # X ends with a gap in seq1 (move down in DP)
            open_x = prev_M[j] + gap_open + gap_extend
            extend_x = prev_X[j] + gap_extend
            x_val = max(0, open_x, extend_x)

            # Y ends with a gap in seq2 (move right in DP)
            open_y = curr_M[j - 1] + gap_open + gap_extend
            extend_y = curr_Y[j - 1] + gap_extend
            y_val = max(0, open_y, extend_y)

            curr_M[j] = m_val
            curr_X[j] = x_val
            curr_Y[j] = y_val

            if m_val > max_score:
                max_score = m_val
            if x_val > max_score:
                max_score = x_val
            if y_val > max_score:
                max_score = y_val

        prev_M, prev_X, prev_Y = curr_M, curr_X, curr_Y

    return int(max_score)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Smith–Waterman local alignment score (affine gaps)")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input-file", help="Path to file with two non-empty lines (sequences)")
    src.add_argument("--seq1", help="Sequence 1 (string)")
    p.add_argument("--seq2", help="Sequence 2 (string). Required if --seq1 is used.")

    p.add_argument("--match", type=int, default=2, help="Match score (default: 2)")
    p.add_argument("--mismatch", type=int, default=-1, help="Mismatch score (default: -1)")
    p.add_argument("--gap-open", type=int, default=-2, help="Gap opening penalty (default: -2)")
    p.add_argument("--gap-extend", type=int, default=-1, help="Gap extension penalty (default: -1)")

    p.add_argument("--emit-format", action="store_true", help="Print 'Alignment score: X' instead of just X")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.input_file:
        try:
            s1, s2 = read_two_sequences_from_file(args.input_file)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
    else:
        if args.seq1 is None or args.seq2 is None:
            print("ERROR: --seq2 is required when using --seq1", file=sys.stderr)
            return 1
        s1, s2 = args.seq1, args.seq2

    score = smith_waterman_affine_score(
        s1, s2,
        match=args.match,
        mismatch=args.mismatch,
        gap_open=args.gap_open,
        gap_extend=args.gap_extend,
    )

    if args.emit_format:
        print(f"Alignment score: {score}")
    else:
        print(score)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
