#!/usr/bin/env python3
"""VCF variant typing: classify each REF/ALT pair as SNP, MNP, INS, or DEL.

- Reads a VCF from a file or stdin
- Emits one line per ALT allele: CHROM:POS TYPE REF>ALT
- Skips symbolic/breakend alleles by default (can be included as OTHER)

Usage:
  python scripts/vcf_variant_typing.py -i input.vcf > output.txt
  cat input.vcf | python scripts/vcf_variant_typing.py -o output.txt
  python scripts/vcf_variant_typing.py -i input.vcf --include-symbolic
"""

import sys
import argparse
from typing import Optional, Tuple


NUC = set("ACGTNacgtn")


def is_symbolic(allele: str) -> bool:
    if allele == ".":
        return True
    if allele == "*":
        return True
    if allele.startswith("<") and allele.endswith(">"):
        return True
    if "[" in allele or "]" in allele:  # breakend notation
        return True
    return any(c not in NUC for c in allele)


def normalize_for_typing(ref: str, alt: str) -> Tuple[str, str]:
    """Trim shared prefix and then shared suffix (when possible) to find core change.
    Keeps at least one base in each allele when possible to preserve classification semantics.
    """
    r = ref
    a = alt
    # Trim common prefix
    i = 0
    max_i = min(len(r), len(a))
    while i < max_i and r[i] == a[i]:
        i += 1
    r = r[i:]
    a = a[i:]
    # Trim common suffix only if both alleles will remain at length >= 1
    j = 0
    max_j = min(len(r), len(a))
    while (
        j < max_j - 0  # ensure index within bounds
        and len(r) - j > 1
        and len(a) - j > 1
        and r[-1 - j] == a[-1 - j]
    ):
        j += 1
    if j:
        r = r[: len(r) - j]
        a = a[: len(a) - j]
    return r, a


def classify_variant(ref: str, alt: str) -> Optional[str]:
    """Return SNP, MNP, INS, DEL, or None if no change or unsupported."""
    if ref == alt:
        return None
    r, a = normalize_for_typing(ref, alt)
    if r == a:
        return None  # no-op after normalization
    lr = len(r)
    la = len(a)
    if lr == la == 1 and r != a:
        return "SNP"
    if lr == la and lr > 1:
        return "MNP"
    if la > lr:
        return "INS"
    if la < lr:
        return "DEL"
    return None


def process_vcf(in_stream, out_stream, include_symbolic: bool = False) -> int:
    """Process VCF stream and write annotations. Returns number of lines written."""
    count = 0
    for raw in in_stream:
        if not raw or raw.startswith('#'):
            continue
        line = raw.rstrip('\n')
        if not line:
            continue
        fields = line.split('\t')
        if len(fields) < 5:
            continue  # malformed line
        chrom, pos, _vid, ref, alt_field = fields[0], fields[1], fields[2], fields[3], fields[4]
        if not alt_field or alt_field == '.':
            continue
        for alt in alt_field.split(','):
            alt = alt.strip()
            if not alt:
                continue
            if is_symbolic(ref) or is_symbolic(alt):
                if include_symbolic:
                    out_stream.write(f"{chrom}:{pos} OTHER {ref}>{alt}\n")
                    count += 1
                continue
            vtype = classify_variant(ref, alt)
            if vtype is None:
                continue
            out_stream.write(f"{chrom}:{pos} {vtype} {ref}>{alt}\n")
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description="Classify VCF variants as SNP/MNP/INS/DEL and emit CHROM:POS TYPE REF>ALT")
    ap.add_argument('-i', '--input', default='-', help='VCF file path (default: stdin)')
    ap.add_argument('-o', '--output', default='-', help='Output file path (default: stdout)')
    ap.add_argument('--include-symbolic', action='store_true', help='Include symbolic/breakend alleles labeled as OTHER')
    args = ap.parse_args()

    # Input stream
    if args.input == '-' or args.input is None:
        in_stream = sys.stdin
    else:
        in_stream = open(args.input, 'r', encoding='utf-8')

    # Output stream
    if args.output == '-' or args.output is None:
        out_stream = sys.stdout
    else:
        out_stream = open(args.output, 'w', encoding='utf-8', newline='')

    try:
        written = process_vcf(in_stream, out_stream, include_symbolic=args.include_symbolic)
    finally:
        if in_stream is not sys.stdin:
            in_stream.close()
        if out_stream is not sys.stdout:
            out_stream.close()

    # Non-fatal completion; exit code 0 regardless of count


if __name__ == '__main__':
    main()
