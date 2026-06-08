#!/usr/bin/env python3
"""Nucleotide sequence utilities: type detection, GC%, frame translation, and longest ORF.

Usage examples:
  python scripts/seq_frame_tools.py --sequence "ATTGC..." --frame 2
  python scripts/seq_frame_tools.py --sequence "ATTGC..." --longest-orf
  python scripts/seq_frame_tools.py --sequence "ATTGC..." --gc

Notes:
- Translation continues past stop codons and marks them with '*'.
- Longest ORF requires an in-frame stop codon; length includes the stop codon (bp).
"""

import argparse
import sys
from typing import Optional


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
DNA_CHARS = set('ATCGN')
RNA_CHARS = set('AUCGN')
AMINO_ACIDS = set('ACDEFGHIKLMNPQRSTVWY')


def normalize(seq: str) -> str:
    """Uppercase and remove whitespace."""
    return ''.join(c for c in seq.upper() if not c.isspace())


def detect_type(raw_seq: str) -> str:
    """Return 'DNA', 'RNA', or 'Protein' based on composition."""
    s = normalize(raw_seq)
    has_t = 'T' in s
    has_u = 'U' in s
    if has_t and not has_u and set(s) <= DNA_CHARS:
        return 'DNA'
    if has_u and not has_t and set(s) <= RNA_CHARS:
        return 'RNA'
    # Fallback: treat as Protein if looks like amino acids, else Protein by default
    letters = [c for c in s if c.isalpha()]
    if letters and all(c in AMINO_ACIDS for c in letters):
        return 'Protein'
    return 'Protein'


def gc_percent(raw_seq: str) -> Optional[float]:
    """Compute GC% excluding ambiguous 'N'. Returns percentage rounded to 1 decimal, or None if no A/T/C/G present."""
    s = normalize(raw_seq)
    s = s.replace('U', 'T')  # treat RNA like DNA for GC calculation
    counts = {b: s.count(b) for b in 'ATCGN'}
    valid_len = len(s) - counts['N']
    if valid_len <= 0:
        return None
    gc = counts['G'] + counts['C']
    return round(gc / valid_len * 100.0, 1)


def translate_frame(raw_seq: str, frame: int) -> str:
    """Translate a nucleotide sequence in the given frame (1,2,3). Continues past stops; uses '*' for stop codons."""
    if frame not in (1, 2, 3):
        raise ValueError('frame must be 1, 2, or 3')
    s = normalize(raw_seq).replace('U', 'T')
    offset = frame - 1
    protein = []
    for i in range(offset, len(s) - 2, 3):
        codon = s[i:i+3]
        if set(codon) <= DNA_CHARS:
            aa = CODON_TABLE.get(codon, '?')
        else:
            aa = '?'
        protein.append(aa)
    return ''.join(protein)


def longest_orf_bp(raw_seq: str) -> int:
    """Find the longest ORF length (bp) across frames. ORF must start with ATG and end at the first in-frame stop codon. Length includes the stop codon."""
    s = normalize(raw_seq).replace('U', 'T')
    best = 0
    n = len(s)
    for frame in (0, 1, 2):
        i = frame
        while i + 2 < n:
            codon = s[i:i+3]
            if codon == 'ATG':
                j = i + 3
                while j + 2 < n:
                    stop_codon = s[j:j+3]
                    if stop_codon in STOP_CODONS:
                        length = (j + 3) - i  # include stop
                        if length > best:
                            best = length
                        break
                    j += 3
                # continue scanning after this start to find other ORFs
                i += 3
            else:
                i += 3
    return best


def main():
    p = argparse.ArgumentParser(description='Nucleotide utilities: type, GC%, translation, longest ORF')
    p.add_argument('--sequence', required=True, help='Input sequence (DNA/RNA/protein)')
    p.add_argument('--frame', type=int, help='Translate in reading frame (1, 2, or 3)')
    p.add_argument('--longest-orf', action='store_true', help='Compute longest ORF length (bp)')
    p.add_argument('--gc', action='store_true', help='Compute GC percentage (ignoring N)')
    args = p.parse_args()

    seq_type = detect_type(args.sequence)
    print(f"Type: {seq_type}")

    if args.gc:
        gc = gc_percent(args.sequence)
        if gc is None:
            print('GC%: NA (no unambiguous bases)')
        else:
            print(f'GC%: {gc:.1f}%')

    if args.frame is not None:
        prot = translate_frame(args.sequence, args.frame)
        print(f'Frame {args.frame} translation: {prot}')

    if args.longest_orf:
        bp = longest_orf_bp(args.sequence)
        print(f'Longest ORF length: {bp} bp')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
