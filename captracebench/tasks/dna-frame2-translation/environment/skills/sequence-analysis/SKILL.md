---
name: sequence-analysis
description: "Analyze DNA/RNA/protein sequences: type determination, GC content calculation, reading frame translation, and longest ORF finding. Use when users ask about sequence translation, GC content, open reading frames, or residue counting."
---

# Biological Sequence Analysis

Skill for basic DNA sequence analysis tasks including type identification, GC content calculation, translation in a specified reading frame, and longest ORF detection.

## When to Use

Activate this skill when the user asks about:
- determining whether a sequence is DNA, RNA, or protein
- calculating GC content of a nucleotide sequence
- translating DNA to protein in a specific reading frame
- finding the longest open reading frame (ORF)

## Core Principle

Work from the sequence data given in the prompt. Compute results directly rather than guessing.

## Phase 1: Sequence Type Determination

Determine whether the sequence is DNA, RNA, or protein:
- **DNA**: contains A/T/C/G/N (specifically contains T, no U)
- **RNA**: contains A/U/C/G/N (specifically contains U, no T)
- **Protein**: contains only amino acid letters (A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y)

Rule: T (thymine) present → DNA. U (uracil) present → RNA. Only amino acid letters → Protein.

## Phase 2: GC Content Calculation

For nucleotide sequences:
- GC content = (G + C) / total_length × 100%
- Round to 1 decimal place

```python
def gc_content(seq):
    seq = seq.upper()
    gc = seq.count('G') + seq.count('C')
    return round(gc / len(seq) * 100, 1)
```

## Phase 3: Reading Frame Translation

The genetic code is read in triplets (codons). A reading frame specifies where to start:
- **Frame 1**: start from base 1 (bases 1-3 = first codon)
- **Frame 2**: start from base 2 (bases 2-4 = first codon)
- **Frame 3**: start from base 3 (bases 3-5 = first codon)

Standard codon table (stop codons marked with *):
```
TTT:F TTC:F TTA:L TTG:L  CTT:L CTC:L CTA:L CTG:L
ATT:I ATC:I ATA:I ATG:M  GTT:V GTC:V GTA:V GTG:V
TCT:S TCC:S TCA:S TCG:S  CCT:P CCC:P CCA:P CCG:P
ACT:T ACC:T ACA:T ACG:T  GCT:A GCC:A GCA:A GCG:A
TAT:Y TAC:Y TAA:* TAG:*  CAT:H CAC:H CAA:Q CAG:Q
AAT:N AAC:N AAA:K AAG:K  GAT:D GAC:D GAA:E GAG:E
TGT:C TGC:C TGA:* TGG:W  CGT:R CGC:R CGA:R CGG:R
AGT:S AGC:S AGA:R AGG:R  GGT:G GGC:G GGA:G GGG:G
```

To translate in a specific frame (0-indexed frame, i.e., frame 2 = frame=1):
```python
def translate(seq, frame=0):
    CODON_TABLE = {
        'TTT':'F','TTC':'F','TTA':'L','TTG':'L',
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
    protein = []
    for i in range(frame, len(seq) - 2, 3):
        codon = seq[i:i+3].upper()
        aa = CODON_TABLE.get(codon, '?')
        protein.append(aa)
    return ''.join(protein)
```

## Phase 4: Finding the Longest ORF

An Open Reading Frame (ORF) starts at ATG (Methionine) and ends at a stop codon (TAA, TAG, or TGA). Only ORFs that have BOTH a start codon AND a stop codon are counted. ORFs that reach the end of the sequence without a stop codon are not considered valid.

```python
def longest_orf_bp(seq):
    """Find longest ORF. Returns DNA length in bp."""
    CODON_TABLE = {
        'TTT':'F','TTC':'F','TTA':'L','TTG':'L',
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
```

## Workflow Summary

For the DNA analysis task:
1. Read the sequence from the input file
2. Identify sequence type (DNA/RNA/Protein)
3. Calculate GC content as percentage
4. Translate in reading frame 2 (frame=1 in 0-indexed)
5. Find longest ORF across all three frames
6. Write results to output file

## Output Format

Write results to `/root/output.txt` with exactly these lines:
```
Sequence type: {DNA|RNA|Protein}
GC content: XX.X%
Frame 2 translation: X...
Longest ORF length: N bp
```
