#!/usr/bin/env python3
"""Reading frame translation and ORF analysis utilities.

Functions:
- detect_seq_type(seq): DNA/RNA/Protein classification
- gc_percent(seq): GC percentage (ignores ambiguous N)
- translate_frame(seq, frame): translate DNA in specified 1-indexed frame (1,2,3)
- longest_orf_bp(seq, include_stop=True): longest ORF length across frames

CLI examples:
  python scripts/seq_frame_tools.py --sequence "ATTGC..." --type --gc
  python scripts/seq_frame_tools.py --sequence "ATTGC..." --frame 2
  python scripts/seq_frame_tools.py --sequence "ATTGC..." --longest-orf
  python scripts/seq_frame_tools.py --sequence "ATTGC..." --longest-orf --exclude-stop
"""

import argparse
import sys
from typing import Set

DNA_CODON_TABLE = {
    'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L','CTA':'L','CTG':'L',
    'ATT':'I','ATC':'I','ATA':'I','ATG':'M','GTT':'V','GTC':'V','GTA':'V','GTG':'V',
    'TCT':'S','TCC':'S','TCA':'S','TCG':'S','CCT':'P','CCC':'P','CCA':'P','CCG':'P',
    'ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A','GCA':'A','GCG':'A',
    'TAT':'Y','TAC':'Y','TAA':'*','TAG':'*','CAT':'H','CAC':'H','CAA':'Q','CAG':'Q',
    'AAT':'N','AAC':'N','AAA':'K','AAG':'K','GAT':'D','GAC':'D','GAA':'E','GAG':'E',
    'TGT':'C','TGC':'C','TGA':'*','TGG':'W','CGT':'R','CGC':'R','CGA':'R','CGG':'R',
    'AGT':'S','AGC':'S','AGA':'R','AGG':'R','GGT':'G','GGC':'G','GGA':'G','GGG':'G',
}
STOP_CODONS: Set[str] = {'TAA','TAG','TGA'}
AMINO_ACIDS: Set[str] = set("ACDEFGHIKLMNPQRSTVWY")
DNA_LETTERS: Set[str] = set("ACGTN")
RNA_LETTERS: Set[str] = set("ACGUN")


def _norm(seq: str) -> str:
    """Uppercase and strip whitespace; do not remove non-ACGT so validation can handle it."""
    return ''.join(ch for ch in seq.strip().upper() if not ch.isspace())


def detect_seq_type(seq: str) -> str:
    s = _norm(seq)
    # Decide nucleic acid type first
    if 'U' in s and 'T' not in s and set(s) <= RNA_LETTERS:
        return 'RNA'
    if 'T' in s and 'U' not in s and set(s) <= DNA_LETTERS:
        return 'DNA'
    # Protein if only amino acid letters
    if set(s) <= AMINO_ACIDS:
        return 'Protein'
    # Fallback heuristics
    if 'T' in s and 'U' not in s:
        return 'DNA'
    if 'U' in s and 'T' not in s:
        return 'RNA'
    return 'Protein'


def gc_percent(seq: str) -> float:
    s = _norm(seq)
    # Convert U->T for RNA so GC calc is consistent
    s = s.replace('U', 'T')
    a = s.count('A')
    c = s.count('C')
    g = s.count('G')
    t = s.count('T')
    denom = a + c + g + t
    if denom == 0:
        return 0.0
    pct = (c + g) / denom * 100.0
    return round(pct, 1)


def translate_frame(seq: str, frame: int) -> str:
    """Translate DNA in 1-indexed frame (1,2,3). Stop codons mapped to '*'.
    Continues translation across the entire frame without truncation.
    Unknown/ambiguous codons map to '?'.
    """
    if frame not in (1, 2, 3):
        raise ValueError("frame must be 1, 2, or 3")
    s = _norm(seq).replace('U', 'T')
    offset = frame - 1
    prot = []
    for i in range(offset, len(s) - 2, 3):
        codon = s[i:i+3]
        aa = DNA_CODON_TABLE.get(codon, '?')
        prot.append(aa)
    return ''.join(prot)


def longest_orf_bp(seq: str, include_stop: bool = True) -> int:
    """Find the longest ORF across all three frames.
    ORF must start with ATG and end with an in-frame stop codon (TAA/TAG/TGA).
    If include_stop is True, the returned length counts the stop codon.
    Returns 0 if no complete ORF exists.
    """
    s = _norm(seq).replace('U', 'T')
    n = len(s)
    best = 0
    for offset in (0, 1, 2):
        i = offset
        while i <= n - 3:
            codon = s[i:i+3]
            if codon == 'ATG':
                j = i + 3
                while j <= n - 3:
                    c = s[j:j+3]
                    if c in STOP_CODONS:
                        length = (j - i + 3) if include_stop else (j - i)
                        if length > best:
                            best = length
                        break
                    j += 3
                # Continue scanning for additional starts in this frame
            i += 3
    return best


def main():
    p = argparse.ArgumentParser(description="Reading frame translation and ORF analysis")
    p.add_argument('--sequence', '-s', required=True, help='Input sequence string')
    p.add_argument('--type', action='store_true', help='Print sequence type')
    p.add_argument('--gc', action='store_true', help='Print GC percent to 1 decimal')
    p.add_argument('--frame', type=int, choices=[1,2,3], help='Translate specified frame (1,2,3)')
    p.add_argument('--longest-orf', action='store_true', help='Compute longest ORF length (bp) across frames')
    excl = p.add_mutually_exclusive_group()
    excl.add_argument('--include-stop', dest='include_stop', action='store_true', help='Include stop codon in ORF length (default)')
    excl.add_argument('--exclude-stop', dest='include_stop', action='store_false', help='Exclude stop codon from ORF length')
    p.set_defaults(include_stop=True)
    args = p.parse_args()

    s = args.sequence
    any_output = False

    if args.type:
        print(f"Sequence type: {detect_seq_type(s)}")
        any_output = True
    if args.gc:
        print(f"GC content: {gc_percent(s)}%")
        any_output = True
    if args.frame is not None:
        prot = translate_frame(s, args.frame)
        print(f"Frame {args.frame} translation: {prot}")
        any_output = True
    if args.longest_orf:
        bp = longest_orf_bp(s, include_stop=args.include_stop)
        print(f"Longest ORF length: {bp} bp")
        any_output = True

    if not any_output:
        # Default to a brief summary if no specific flags were provided
        print(f"Sequence type: {detect_seq_type(s)}")
        print(f"GC content: {gc_percent(s)}%")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
