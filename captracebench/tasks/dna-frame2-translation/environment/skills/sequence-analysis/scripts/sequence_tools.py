#!/usr/bin/env python3
"""Sequence analysis utilities: type detection and GC content.

Usage:
  python sequence_tools.py --type gc_content --sequence "ATGCGATCG"
  python sequence_tools.py --type stats --sequence "ATGCGATCG"
"""

import argparse
import sys


DNA_BASES = frozenset("ATCGNatcgn")
RNA_BASES = frozenset("AUCGNaucgn")


def is_dna(seq: str) -> bool:
    return all(c in DNA_BASES for c in seq) and "U" not in seq.upper()


def is_rna(seq: str) -> bool:
    return all(c in RNA_BASES for c in seq)


def gc_content(seq: str) -> dict:
    """Calculate GC content of a DNA or RNA sequence."""
    seq = seq.strip().upper()
    if not seq:
        return {"error": "Empty sequence provided."}

    counts = {b: seq.count(b) for b in "ATCGUN"}
    g = counts["G"]
    c = counts["C"]
    n = counts["N"]
    total = len(seq)

    if total - n == 0:
        return {"error": "Sequence contains only ambiguous (N) bases."}

    gc_frac = (g + c) / (total - n)

    return {
        "length": total,
        "gc_count": g + c,
        "gc_fraction": round(gc_frac, 4),
        "gc_percent": round(gc_frac * 100, 1),
    }


def sequence_stats(seq: str) -> dict:
    """Compute basic statistics and detect sequence type."""
    seq = seq.strip().upper()
    if not seq:
        return {"error": "Empty sequence provided."}

    if is_dna(seq):
        seq_type = "DNA"
        gc = seq.count('G') + seq.count('C')
        n = seq.count('N')
        gc_pct = round(gc / (len(seq) - n) * 100, 1) if len(seq) - n > 0 else 0
        return {"sequence_type": seq_type, "length": len(seq), "gc_percent": gc_pct}
    elif is_rna(seq):
        seq_type = "RNA"
        gc = seq.count('G') + seq.count('C')
        n = seq.count('N')
        gc_pct = round(gc / (len(seq) - n) * 100, 1) if len(seq) - n > 0 else 0
        return {"sequence_type": seq_type, "length": len(seq), "gc_percent": gc_pct}
    else:
        seq_type = "Protein"
        return {"sequence_type": seq_type, "length": len(seq)}


def main():
    parser = argparse.ArgumentParser(description="Sequence analysis utilities")
    parser.add_argument("--type", required=True, choices=["gc_content", "stats"],
                        help="Analysis type")
    parser.add_argument("--sequence", required=True, help="Sequence string")
    args = parser.parse_args()

    if args.type == "gc_content":
        result = gc_content(args.sequence)
    else:
        result = sequence_stats(args.sequence)

    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
