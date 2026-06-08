#!/usr/bin/env python3
"""Annotate VCF variants by type (SNP, MNP, INS, DEL) from REF/ALT lengths.

Outputs one line per ALT allele:
  CHR:POS TYPE REF>ALT

Usage:
  python vcf_annotate_types.py --vcf input.vcf --out output.txt
  python vcf_annotate_types.py --vcf input.vcf --out -            # write to stdout
  python vcf_annotate_types.py --vcf input.vcf --out output.txt --keep-symbolic

Notes:
- Skips header lines (starting with '#').
- Splits multi-allelic ALT on commas and emits one line per ALT.
- Skips symbolic or breakend ALT (e.g., '.', '*', '<DEL>', 'N[', ']chr') unless --keep-symbolic is provided, in which case these are labeled as OTHER.
"""

import argparse
import sys
from typing import Iterable, Optional, Tuple


def is_symbolic_or_breakend(allele: str) -> bool:
    a = allele.strip()
    if not a:
        return True
    if a == '.' or a == '*':
        return True
    if a.startswith('<') and a.endswith('>'):
        return True
    if '[' in a or ']' in a:
        return True
    return False


def classify_type(ref: str, alt: str) -> Optional[str]:
    """Return SNP, MNP, INS, or DEL from REF/ALT lengths, or None if undecidable."""
    if not ref or not alt:
        return None
    lr = len(ref)
    la = len(alt)
    if la == lr:
        if lr == 1:
            return 'SNP' if ref != alt else None
        else:
            return 'MNP' if ref != alt else None
    return 'INS' if la > lr else 'DEL'


def parse_fields(line: str) -> Optional[Tuple[str, str, str, str]]:
    """Parse CHROM, POS, REF, ALT from a VCF line. Returns None if malformed."""
    line = line.rstrip('\n')
    if not line or line.startswith('#'):
        return None
    # Prefer tab split; fall back to any whitespace if needed
    parts = line.split('\t') if ('\t' in line) else line.split()
    if len(parts) < 5:
        return None
    chrom, pos, _id, ref, alt = parts[0], parts[1], parts[2], parts[3], parts[4]
    return chrom, pos, ref, alt


def annotate_vcf(vcf_stream: Iterable[str], keep_symbolic: bool = False) -> Iterable[str]:
    for raw in vcf_stream:
        fields = parse_fields(raw)
        if fields is None:
            continue
        chrom, pos, ref, alt_field = fields
        # Split multi-allelic ALT
        for alt in alt_field.split(','):
            alt = alt.strip()
            if not alt:
                continue
            if is_symbolic_or_breakend(alt):
                if keep_symbolic:
                    yield f"{chrom}:{pos} OTHER {ref}>{alt}"
                continue
            vtype = classify_type(ref, alt)
            if vtype is None:
                # identical REF/ALT or undecidable; skip
                continue
            yield f"{chrom}:{pos} {vtype} {ref}>{alt}"


def main():
    p = argparse.ArgumentParser(description="VCF variant typing (SNP/MNP/INS/DEL) from REF/ALT lengths")
    p.add_argument('--vcf', required=True, help='Path to input VCF file')
    p.add_argument('--out', default='-', help='Output path or - for stdout (default)')
    p.add_argument('--keep-symbolic', action='store_true', help='Emit symbolic/breakend alleles labeled as OTHER')
    args = p.parse_args()

    try:
        with open(args.vcf, 'r', encoding='utf-8', errors='replace', newline='') as fin:
            lines = list(annotate_vcf(fin, keep_symbolic=args.keep_symbolic))
    except FileNotFoundError:
        print(f"ERROR: input VCF not found: {args.vcf}", file=sys.stderr)
        sys.exit(1)

    if args.out == '-' or args.out == '/dev/stdout':
        out_stream = sys.stdout
        close_out = False
    else:
        out_stream = open(args.out, 'w', encoding='utf-8', newline='')
        close_out = True

    try:
        for line in lines:
            out_stream.write(line + "\n")
    finally:
        if close_out:
            out_stream.close()


if __name__ == '__main__':
    main()
