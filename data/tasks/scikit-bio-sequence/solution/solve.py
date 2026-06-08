#!/usr/bin/env python3
"""Solve scikit-bio-sequence task."""

from skbio import DNA

def main():
    input_path = "/root/input.txt"
    output_path = "/root/output.txt"

    with open(input_path, 'r') as f:
        seq_str = f.read().strip()

    seq = DNA(seq_str)

    # Count k-mers with k=3
    counts = {}
    for kmer in seq.iter_kmers(3):
        kmer_str = str(kmer)
        counts[kmer_str] = counts.get(kmer_str, 0) + 1

    # Sort alphabetically and write
    lines = []
    for kmer in sorted(counts.keys()):
        lines.append(f"{kmer}: {counts[kmer]}")

    output = "\n".join(lines) + "\n"

    with open(output_path, 'w') as f:
        f.write(output)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(output)

if __name__ == "__main__":
    main()