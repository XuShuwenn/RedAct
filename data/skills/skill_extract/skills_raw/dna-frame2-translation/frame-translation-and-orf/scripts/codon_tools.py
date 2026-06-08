#!/usr/bin/env python3
"""Codon translation and ORF utilities.

Functions:
- sequence_type(seq): classify DNA/RNA/Protein using character sets
- gc_content_percent(seq): GC% (exclude ambiguous from denominator), 1 decimal
- translate_frame(seq, frame=0): translate nucleotide sequence with '*' for stops
- longest_orf_bp(seq): longest ATG..(TAA|TAG|TGA) length in bp, inclusive of stop

CLI examples:
  python scripts/codon_tools.py --type --gc "ATTGC..."
  python scripts/codon_tools.py --frame 2 "ATTGC..."
  python scripts/codon_tools.py --orf "ATTGC..."

Note: Frame argument to --frame is 1-based (1, 2, 3). Internally 0-based.
"""
import sys
import argparse
from typing import Tuple

DNA_BASES = set("ATCGN")
RNA_BASES = set("AUCGN")

CODON_TABLE = {
    'TTT':'F','TTC':'F','TTA':'L','TTG':'L',
    'CTT':'L','CTC':'L','CTA':'L','CTG':'L',
    'ATT':'I','ATC':'I','ATA':'I','ATG':'M',
    'GTT':'V','GTC':'V','GTA':'V','GTG':'V',
    'TCT':'S','TCC':'S','TCA':'S','TCG':'S',
    'CCT':'P','CCC':'P','CCA':'P','CCG':'P',
    'ACT':'T','ACC':'T','ACA':'T','ACG':'T',
    'GCT':'A','GCC':'A','GCA':'A','GCG':'A',
    'TAT':'Y','TAC':'Y','TAA':'*','TAG':'*',
    'CAT':'H','CAC':'H','CAA':'Q','CAG':'Q',
    'AAT':'N','AAC':'N','AAA':'K','AAG':'K',
    'GAT':'D','GAC':'D','GAA':'E','GAG':'E',
    'TGT':'C','TGC':'C','TGA':'*','TGG':'W',
    'CGT':'R','CGC':'R','CGA':'R','CGG':'R',
    'AGT':'S','AGC':'S','AGA':'R','AGG':'R',
    'GGT':'G','GGC':'G','GGA':'G','GGG':'G',
}
STOPS = {'TAA', 'TAG', 'TGA'}


def _normalize(seq: str) -> str:
    return ''.join(ch for ch in seq.strip().upper() if not ch.isspace())


def sequence_type(seq: str) -> str:
    s = _normalize(seq)
    # DNA: all in DNA_BASES and no U
    if all(c in DNA_BASES for c in s) and 'U' not in s:
        return 'DNA'
    # RNA: all in RNA_BASES
    if all(c in RNA_BASES for c in s):
        return 'RNA'
    # Otherwise treat as Protein (includes unknowns)
    return 'Protein'


def gc_content_percent(seq: str) -> float:
    s = _normalize(seq).replace('U', 'T')
    valid = 0
    gc = 0
    for ch in s:
        if ch in 'ATCG':
            valid += 1
            if ch in 'GC':
                gc += 1
    if valid == 0:
        return 0.0
    return round(gc / valid * 100, 1)


def translate_frame(seq: str, frame: int = 0) -> str:
    """Translate sequence from a 0-indexed frame (0,1,2). Does not truncate at stop codons.
    Ambiguous codons (any base outside A/T/C/G) yield '?'.
    """
    s = _normalize(seq).replace('U', 'T')
    protein = []
    # Ensure frame is 0,1,2
    frame = max(0, min(2, int(frame)))
    for i in range(frame, len(s) - 2, 3):
        codon = s[i:i+3]
        if any(ch not in 'ATCG' for ch in codon):
            protein.append('?')
        else:
            protein.append(CODON_TABLE.get(codon, '?'))
    return ''.join(protein)


def longest_orf_bp(seq: str) -> int:
    """Return the longest ORF length (bp) across frames, inclusive of stop.
    ORF starts at ATG and ends at the first in-frame stop (TAA/TAG/TGA).
    Ambiguous codons are not considered starts/stops.
    """
    s = _normalize(seq).replace('U', 'T')
    best = 0
    n = len(s)
    for frame in range(3):
        # Evaluate every ATG as a candidate start
        for i in range(frame, n - 2, 3):
            if s[i:i+3] != 'ATG':
                continue
            for j in range(i + 3, n - 2, 3):
                cod = s[j:j+3]
                if cod in STOPS:
                    length = (j - i) + 3  # inclusive of stop codon
                    if length > best:
                        best = length
                    break
    return best


def main():
    ap = argparse.ArgumentParser(description="Codon translation and ORF utilities")
    ap.add_argument('sequence', nargs='?', help='Input sequence (or read from stdin if omitted)')
    ap.add_argument('--type', action='store_true', help='Detect sequence type')
    ap.add_argument('--gc', action='store_true', help='Compute GC percent')
    ap.add_argument('--frame', type=int, help='Translate in 1-based reading frame (1, 2, or 3)')
    ap.add_argument('--orf', action='store_true', help='Report longest ORF length (bp)')
    args = ap.parse_args()

    if args.sequence is None:
        data = sys.stdin.read()
    else:
        data = args.sequence

    outputs = []

    if args.type:
        outputs.append(f"sequence_type: {sequence_type(data)}")

    if args.gc:
        outputs.append(f"gc_percent: {gc_content_percent(data)}")

    if args.frame is not None:
        f = max(1, min(3, int(args.frame)))
        prot = translate_frame(data, frame=f - 1)
        outputs.append(f"frame_{f}_translation: {prot}")

    if args.orf:
        outputs.append(f"longest_orf_bp: {longest_orf_bp(data)}")

    if not outputs:
        ap.print_help()
        sys.exit(1)

    for line in outputs:
        print(line)


if __name__ == '__main__':
    main()
