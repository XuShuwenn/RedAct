#!/usr/bin/env python3
"""Translate DNA to protein in specific reading frames and find longest ORF.

Usage:
    python translate_dna.py <DNA_SEQUENCE> [--frame N] [--longest-orf]
    python translate_dna.py ATTGCAGTTGCCATG... --frame 2
    python translate_dna.py ATTGCAGTTGCCATG... --longest-orf
"""

import sys
import argparse

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


def translate(seq, frame=0):
    """Translate DNA from given frame (0=frame1, 1=frame2, 2=frame3)."""
    protein = []
    for i in range(frame, len(seq) - 2, 3):
        codon = seq[i:i+3].upper()
        aa = CODON_TABLE.get(codon, '?')
        protein.append(aa)
    return ''.join(protein)


def longest_orf_bp(seq):
    """Find longest ORF in any frame. Returns DNA length in bp."""
    best = 0
    for frame in range(3):
        orf_len = 0
        in_orf = False
        for i in range(frame, len(seq) - 2, 3):
            codon = seq[i:i+3].upper()
            aa = CODON_TABLE.get(codon, '?')
            if aa == 'M':
                in_orf = True
                orf_len = 3
            elif in_orf:
                if aa == '*':
                    break
                orf_len += 3
        if orf_len > best:
            best = orf_len
    return best


def main():
    parser = argparse.ArgumentParser(description="DNA translation and longest ORF finder")
    parser.add_argument("sequence", nargs="?", help="DNA sequence")
    parser.add_argument("--frame", type=int, default=None, help="Reading frame (1, 2, or 3)")
    parser.add_argument("--longest-orf", action="store_true", help="Find longest ORF")
    args = parser.parse_args()

    if not args.sequence:
        parser.print_help()
        sys.exit(1)

    seq = ''.join(c.upper() for c in args.sequence if c.upper() in 'ATCG')
    print(f"Input: {len(seq)} bp")

    if args.longest_orf:
        bp = longest_orf_bp(seq)
        print(f"Longest ORF length: {bp} bp")

    if args.frame is not None:
        frame_idx = args.frame - 1  # convert 1-indexed to 0-indexed
        prot = translate(seq, frame=frame_idx)
        print(f"Frame {args.frame} translation: {prot}")


if __name__ == '__main__':
    main()
