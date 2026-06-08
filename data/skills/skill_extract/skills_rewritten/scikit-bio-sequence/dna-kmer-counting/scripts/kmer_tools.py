#!/usr/bin/env python3
"""DNA k-mer counting utilities with scikit-bio and verification.

Features:
- Read and sanitize DNA sequence (uppercase, A/C/G/T only by default).
- Count overlapping k-mers using scikit-bio (fallback to pure Python if unavailable).
- Write alphabetically sorted, nonzero counts in "KMER: COUNT" format.
- Verify output formatting, sort order, positivity, and total count sanity.

Usage examples:
  python scripts/kmer_tools.py --input input.txt --output output.txt --k 3
  python scripts/kmer_tools.py --input input.fa --output output.txt --k 5 --no-clean
  python scripts/kmer_tools.py --input input.txt --k 3 --dry-run

Arguments:
  --input PATH        Input file containing a DNA sequence (FASTA headers allowed).
  --output PATH       Output file path to write "KMER: COUNT" lines.
  --k INT             K-mer size (default: 3).
  --no-clean          Do not remove non-ACGT characters; only uppercase normalization.
  --dry-run           Perform counting and verification without writing output.
  --library {skb,py}  Choose counting backend: scikit-bio (skb) or pure Python (py). Default: skb.

Note:
- If the prompt requires scikit-bio, prefer --library skb. The pure Python backend is for cross-checking only.
"""

import argparse
import sys
import re
from collections import Counter

try:
    from skbio import DNA  # type: ignore
    HAS_SKBIO = True
except Exception:
    HAS_SKBIO = False

DNA_CHARS = set("ACGT")


def read_sequence(path: str) -> str:
    seq_parts = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                # Skip FASTA header lines
                continue
            seq_parts.append(line)
    return "".join(seq_parts)


def sanitize_sequence(seq: str, clean: bool = True) -> str:
    seq = seq.upper()
    if clean:
        # Keep only A/C/G/T
        return "".join(ch for ch in seq if ch in DNA_CHARS)
    return seq


def count_kmers_python(seq: str, k: int) -> dict:
    if k <= 0:
        return {}
    n = len(seq)
    if n < k:
        return {}
    kmers = [seq[i:i+k] for i in range(n - k + 1)]
    # If cleaning is disabled, exclude windows containing non-ACGT to keep outputs deterministic
    kmers = [km for km in kmers if set(km) <= DNA_CHARS]
    return dict(Counter(kmers))


def count_kmers_skbio(seq: str, k: int) -> dict:
    if not HAS_SKBIO:
        raise RuntimeError("scikit-bio not available; cannot use skb backend.")
    dna = DNA(seq)
    # overlap=True ensures overlapping windows; relative=False returns integer counts
    counts = dna.kmer_frequencies(k=k, overlap=True, relative=False)
    # scikit-bio may include kmers with non-ACGT if present; filter by A/C/G/T for deterministic output
    return {kmer: int(cnt) for kmer, cnt in counts.items() if set(kmer) <= DNA_CHARS and cnt > 0}


def sort_and_format(counts: dict) -> list:
    lines = []
    for kmer in sorted(counts.keys()):
        cnt = int(counts[kmer])
        if cnt > 0:
            lines.append(f"{kmer}: {cnt}")
    return lines


def verify_output(lines: list, k: int, seq_len: int) -> list:
    problems = []
    # Format check
    pattern = re.compile(rf"^[ACGT]{{{k}}}: [0-9]+$")
    for i, line in enumerate(lines):
        if not pattern.match(line):
            problems.append(f"Line {i+1} has invalid format: {line}")
    # Sorting check
    kmers = [line.split(": ")[0] for line in lines]
    if kmers != sorted(kmers):
        problems.append("Lines are not sorted alphabetically by k-mer.")
    # Positivity check
    for i, line in enumerate(lines):
        _, cnt_str = line.split(": ")
        cnt = int(cnt_str)
        if cnt <= 0:
            problems.append(f"Line {i+1} has non-positive count: {cnt}")
    # Sanity of total windows
    if seq_len >= k:
        expected = seq_len - k + 1
        actual = sum(int(line.split(": ")[1]) for line in lines)
        if actual != expected:
            problems.append(
                f"Total counts ({actual}) do not equal expected overlapping windows ({expected})."
            )
    return problems


def main():
    parser = argparse.ArgumentParser(description="DNA k-mer counting with scikit-bio and verification")
    parser.add_argument("--input", required=True, help="Input sequence file path")
    parser.add_argument("--output", required=False, help="Output file path for 'KMER: COUNT' lines")
    parser.add_argument("--k", type=int, default=3, help="K-mer size (default: 3)")
    parser.add_argument("--no-clean", action="store_true", help="Do not remove non-ACGT characters")
    parser.add_argument("--dry-run", action="store_true", help="Compute and verify without writing output")
    parser.add_argument("--library", choices=["skb", "py"], default="skb", help="Counting backend: scikit-bio or pure Python")
    args = parser.parse_args()

    raw = read_sequence(args.input)
    cleaned = sanitize_sequence(raw, clean=(not args.no_clean))

    if args.library == "skb":
        if not HAS_SKBIO:
            print("WARNING: scikit-bio not available; falling back to pure Python.", file=sys.stderr)
            counts = count_kmers_python(cleaned, args.k)
        else:
            counts = count_kmers_skbio(cleaned, args.k)
    else:
        counts = count_kmers_python(cleaned, args.k)

    lines = sort_and_format(counts)

    problems = verify_output(lines, args.k, len(cleaned))
    if problems:
        print("VERIFICATION FAILED:", file=sys.stderr)
        for p in problems:
            print(f"- {p}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        for line in lines:
            print(line)
        return

    if not args.output:
        print("ERROR: --output is required unless --dry-run is used", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as out:
        out.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} lines to {args.output}")


if __name__ == "__main__":
    main()
