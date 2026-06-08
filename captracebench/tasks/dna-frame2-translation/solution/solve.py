#!/usr/bin/env python3
"""Oracle solution for sequence-analysis task."""

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

DNA_BASES = frozenset("ATCGNatcgn")
RNA_BASES = frozenset("AUCGNaucgn")


def is_dna(seq):
    return all(c in DNA_BASES for c in seq) and "U" not in seq.upper()


def is_rna(seq):
    return all(c in RNA_BASES for c in seq)


def translate(seq, frame=0):
    """Translate DNA from given frame (0=frame1, 1=frame2, 2=frame3)."""
    protein = []
    for i in range(frame, len(seq) - 2, 3):
        codon = seq[i:i+3].upper()
        aa = CODON_TABLE.get(codon, '?')
        protein.append(aa)
    return ''.join(protein)


def longest_orf_bp(seq):
    """Find longest ORF in any frame. Returns DNA length in bp.
    Only ORFs with BOTH start and stop codons are counted. Stop codon is included in length."""
    best = 0
    for frame in range(3):
        orf_len = 0
        in_orf = False
        for i in range(frame, len(seq) - 2, 3):
            codon = seq[i:i+3].upper()
            aa = CODON_TABLE.get(codon, '?')
            if aa == 'M':  # start codon
                in_orf = True
                orf_len = 3
            elif in_orf:
                if aa == '*':  # stop codon
                    orf_len += 3  # include stop codon in count
                    if orf_len > best:
                        best = orf_len
                    break
                orf_len += 3
    return best


def main():
    with open('/root/input.txt') as f:
        raw = f.read().strip()

    seq = ''.join(c for c in raw.upper() if c in 'ATCG')
    print(f"Input sequence ({len(seq)} bp): {seq}")

    # Step 1: Determine sequence type
    if is_dna(seq):
        seq_type = 'DNA'
    elif is_rna(seq):
        seq_type = 'RNA'
    else:
        seq_type = 'Protein'

    # Step 2: GC content
    gc = seq.count('G') + seq.count('C')
    gc_pct = round(gc / len(seq) * 100, 1)

    # Step 3: Frame 2 translation (frame=1 is frame 2, 0-indexed)
    frame2_prot = translate(seq, frame=1)

    # Step 4: Longest ORF
    orf_bp = longest_orf_bp(seq)

    output = f"Sequence type: {seq_type}\n"
    output += f"GC content: {gc_pct}%\n"
    output += f"Frame 2 translation: {frame2_prot}\n"
    output += f"Longest ORF length: {orf_bp} bp\n"

    # Write oracle output (reference for verifier)
    with open('/root/oracle_output.txt', 'w') as f:
        f.write(output)

    # Write output.txt
    with open('/root/output.txt', 'w') as f:
        f.write(output)

    print(f"\n--- Output ---")
    print(output)


if __name__ == '__main__':
    main()
