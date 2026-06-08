#!/usr/bin/env python3
"""DNA k-mer counting with scikit-bio.

Features:
- Reads a DNA sequence from a file or stdin
- Normalizes input (uppercase, converts U->T)
- Validates characters against IUPAC DNA alphabet
- Iterates overlapping k-mers using scikit-bio (with a manual fallback)
- Optionally excludes ambiguous k-mers (i.e., only A/C/G/T kept)
- Outputs k-mer counts sorted lexicographically as: "KMER: count"
- Optional verification that total counts match expected overlapping windows

Usage Examples:
  python scripts/kmer_count.py --input input.txt --output output.txt --k 3 --exclude-ambiguous
  cat input.txt | python scripts/kmer_count.py --k 4 --exclude-ambiguous
  python scripts/kmer_count.py --input input.txt --k 5 --verify
"""

import sys
import argparse
from collections import Counter

IUPAC_DNA_ALPHABET = set("ACGTRYSWKMBDHVN")  # IUPAC DNA codes
CANONICAL = set("ACGT")


def read_sequence(path: str) -> str:
    if path == "-":
        data = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8") as fh:
            data = fh.read()
    # Normalize: strip whitespace, uppercase, convert U->T
    seq = ''.join(ch for ch in data.upper() if not ch.isspace())
    seq = seq.replace('U', 'T')
    # Validate characters
    invalid = sorted(set(seq) - IUPAC_DNA_ALPHABET)
    if invalid:
        raise ValueError(f"Invalid DNA characters encountered: {''.join(invalid)}")
    return seq


def iter_kmers_skbio(seq: str, k: int):
    """Yield overlapping k-mers using scikit-bio when available.

    Falls back to a manual sliding window if scikit-bio is missing or an
    unexpected exception occurs during object creation/iteration.
    """
    try:
        from skbio import DNA
        dna = DNA(seq)  # uses IUPAC DNA alphabet
        # In scikit-bio, iter_kmers yields Sequence objects; convert to str
        for kmer in dna.iter_kmers(k):
            yield str(kmer)
        return
    except Exception:
        # Fallback: manual overlapping windows
        for i in range(0, max(len(seq) - k + 1, 0)):
            yield seq[i:i + k]


def count_kmers(seq: str, k: int, exclude_ambiguous: bool = False):
    counts = Counter()
    skipped = 0
    for kmer in iter_kmers_skbio(seq, k):
        if exclude_ambiguous and (set(kmer) - CANONICAL):
            skipped += 1
            continue
        counts[kmer] += 1
    return counts, skipped


def write_counts(counts: Counter, path: str) -> None:
    lines = [f"{k}: {counts[k]}\n" for k in sorted(counts)]
    if path == "-":
        sys.stdout.writelines(lines)
    else:
        with open(path, "w", encoding="utf-8") as fh:
            fh.writelines(lines)


def verify_counts(seq: str, k: int, counts: Counter, skipped: int, exclude_ambiguous: bool) -> None:
    total_windows = max(len(seq) - k + 1, 0)
    total_counted = sum(counts.values())
    expected = total_windows - (skipped if exclude_ambiguous else 0)
    if total_counted != expected:
        raise AssertionError(
            f"Verification failed: counted={total_counted}, expected={expected}, "
            f"windows={total_windows}, skipped={skipped}, k={k}"
        )


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Count overlapping DNA k-mers using scikit-bio.")
    p.add_argument("--input", "-i", default="-", help="Input path (default: stdin)")
    p.add_argument("--output", "-o", default="-", help="Output path (default: stdout)")
    p.add_argument("--k", type=int, required=True, help="k-mer length (k >= 1)")
    p.add_argument("--exclude-ambiguous", action="store_true",
                   help="Exclude k-mers containing non-ACGT characters")
    p.add_argument("--verify", action="store_true", help="Enable result verification")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.k < 1:
        print("ERROR: k must be >= 1", file=sys.stderr)
        sys.exit(2)

    try:
        seq = read_sequence(args.input)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.k > len(seq):
        # No k-mers possible; create empty output
        write_counts(Counter(), args.output)
        sys.exit(0)

    counts, skipped = count_kmers(seq, args.k, exclude_ambiguous=args.exclude_ambiguous)

    if args.verify:
        try:
            verify_counts(seq, args.k, counts, skipped, args.exclude_ambiguous)
        except AssertionError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(3)

    try:
        write_counts(counts, args.output)
    except Exception as e:
        print(f"ERROR writing output: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
