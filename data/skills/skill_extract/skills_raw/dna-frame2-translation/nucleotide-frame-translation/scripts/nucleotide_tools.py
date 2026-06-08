#!/usr/bin/env python3
"""Nucleotide sequence utilities: type detection, GC%, frame translation, and longest ORF.

Usage examples:
  python nucleotide_tools.py --sequence "ATGCGAT..." --detect-type --gc
  python nucleotide_tools.py --sequence "ATGCGAT..." --translate-frame 2
  python nucleotide_tools.py --sequence "ATGCGAT..." --longest-orf

Notes:
- Translation uses the standard genetic code with stop codons mapped to '*'.
- Frame numbers are 1-indexed (1, 2, 3). Internally converted to offsets 0, 1, 2.
- Longest ORF requires an ATG start and an in-frame stop (TAA/TAG/TGA) and includes the stop codon in its length.
"""

import argparse
import sys
from typing import Optional

DNA_SET = set("ACGTN")
RNA_SET = set("ACGUN")

CODON_TABLE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}
STOP_CODONS = {'TAA', 'TAG', 'TGA'}


def clean_seq(raw: str) -> str:
    """Uppercase and remove whitespace/newlines."""
    return ''.join(c for c in raw.upper() if not c.isspace())


def detect_type(seq: str) -> str:
    """Return 'DNA', 'RNA', or 'Protein' based on character content.

    Rules:
    - DNA: contains T and no U, and all characters in A/C/G/T/N
    - RNA: contains U and no T, and all characters in A/C/G/U/N
    - Otherwise: Protein
    """
    s = seq.upper()
    has_t = 'T' in s
    has_u = 'U' in s
    only_dna_chars = set(s) <= DNA_SET
    only_rna_chars = set(s) <= RNA_SET
    if has_t and not has_u and only_dna_chars:
        return 'DNA'
    if has_u and not has_t and only_rna_chars:
        return 'RNA'
    return 'Protein'


def gc_content(seq: str) -> Optional[float]:
    """Compute GC% for nucleotide sequences, ignoring Ns. Returns percentage rounded to 1 decimal.
    Returns None if denominator is zero or if non-nucleotide characters are present.
    """
    s = seq.upper()
    if not set(s) <= (DNA_SET | {'U'}):  # allow U to be present for RNA
        return None
    g = s.count('G')
    c = s.count('C')
    n = s.count('N')
    # For RNA, Ns still ignored; denominator excludes Ns
    denom = len(s) - n
    if denom <= 0:
        return None
    pct = (g + c) / denom * 100.0
    return round(pct + 1e-12, 1)  # tiny epsilon for stable rounding


def translate_frame(dna: str, frame: int) -> str:
    """Translate DNA in a specified frame (1, 2, or 3). Stop codons -> '*'.
    Continues translation across the entire sequence (does not halt at '*').
    Unknown/ambiguous codons yield 'X'.
    """
    if frame not in (1, 2, 3):
        raise ValueError('frame must be 1, 2, or 3')
    s = ''.join(ch for ch in dna.upper() if ch in 'ACGTN')
    offset = frame - 1
    protein = []
    for i in range(offset, len(s) - 2, 3):
        codon = s[i:i+3]
        aa = CODON_TABLE.get(codon)
        if aa is None:
            if 'N' in codon:
                protein.append('X')
            else:
                protein.append('?')
        else:
            protein.append(aa)
    return ''.join(protein)


def longest_orf_bp(dna: str) -> int:
    """Return length (bp) of the longest ATG..(stop) ORF across frames.
    Length includes the stop codon. If no complete ORF exists, return 0.
    """
    s = ''.join(ch for ch in dna.upper() if ch in 'ACGT')  # restrict to unambiguous DNA
    best = 0
    for frame in range(3):
        start_idx = None
        for i in range(frame, len(s) - 2, 3):
            codon = s[i:i+3]
            if start_idx is None:
                if codon == 'ATG':
                    start_idx = i
            else:
                if codon in STOP_CODONS:
                    length = (i - start_idx + 3)
                    if length > best:
                        best = length
                    start_idx = None  # reset and continue scanning
        # Optional: If ORF reaches sequence end without stop, ignore (invalid)
    return best


def main():
    ap = argparse.ArgumentParser(description='Nucleotide sequence tools')
    ap.add_argument('--sequence', help='Sequence string (DNA/RNA/protein)')
    ap.add_argument('--input-file', help='Read sequence from file path')
    ap.add_argument('--detect-type', action='store_true', help='Detect sequence type')
    ap.add_argument('--gc', action='store_true', help='Compute GC% (ignoring Ns)')
    ap.add_argument('--translate-frame', type=int, choices=[1, 2, 3], help='Translate DNA in given frame')
    ap.add_argument('--longest-orf', action='store_true', help='Compute longest ORF length in bp')
    args = ap.parse_args()

    raw = None
    if args.sequence:
        raw = args.sequence
    elif args.input-file:
        try:
            with open(args.input-file, 'r') as fh:
                raw = fh.read()
        except Exception as e:
            print(f'ERROR: cannot read input file: {e}', file=sys.stderr)
            sys.exit(1)
    else:
        ap.error('Provide --sequence or --input-file')

    seq = clean_seq(raw)

    if args.detect-type:
        st = detect_type(seq)
        print(f'Sequence type: {st}')

    if args.gc:
        pct = gc_content(seq)
        if pct is None:
            print('GC content: N/A')
        else:
            print(f'GC content: {pct}%')

    if args.translate-frame is not None:
        prot = translate_frame(seq, args.translate-frame)
        print(f'Frame {args.translate-frame} translation: {prot}')

    if args.longest-orf:
        bp = longest_orf_bp(seq)
        print(f'Longest ORF length: {bp} bp')


if __name__ == '__main__':
    main()
