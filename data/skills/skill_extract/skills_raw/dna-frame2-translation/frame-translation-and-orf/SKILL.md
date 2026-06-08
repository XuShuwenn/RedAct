---
name: frame-translation-and-orf
description: "Compute GC content, translate a nucleotide sequence in a specified reading frame, and find the longest ORF across frames with robust verification."
---

# Reading-Frame Translation and Longest ORF Detection

A reusable workflow for nucleotide sequence analysis: sequence type detection, GC content calculation, frame-specific translation with stop codons marked as '*', and finding the longest open reading frame (ORF) across all three frames.

## When to Use

Activate this skill when a user asks to:
- identify whether an input sequence is DNA, RNA, or protein
- calculate GC content of a nucleotide sequence (rounded to 1 decimal place)
- translate a sequence in a specific reading frame (e.g., frame 2)
- find the longest ORF (start = ATG, stops = TAA/TAG/TGA) across frames
- produce results in a strict, line-based output format

## Core Workflow

1. Normalize input
   - Strip whitespace and convert to uppercase. Preserve letters; do not silently drop characters before type detection.

2. Determine sequence type
   - DNA: all characters in {A,T,C,G,N} and no U
   - RNA: all characters in {A,U,C,G,N}
   - Protein: otherwise (contains letters outside the nucleotide alphabets)

3. GC content (nucleic acids only)
   - Convert U→T if RNA.
   - Count G and C. Use denominator = count of A/T/C/G (exclude ambiguous N and other non-bases from the denominator).
   - GC% = (G + C) / (A + T + C + G) × 100; round to 1 decimal place.

4. Frame-specific translation
   - Use the standard codon table (TAA/TAG/TGA map to '*').
   - Define frame as 1-indexed positions (Frame 1 starts at base 1, Frame 2 at base 2, Frame 3 at base 3). Internally, offset = frame - 1.
   - Do not truncate at stop codons unless the task explicitly requests truncation; emit '*' and continue translating to the end.
   - For any codon containing ambiguous bases (e.g., N) or invalid letters, emit '?' for that codon.

5. Longest ORF across all frames
   - ORF definition: starts at ATG and ends at the first in-frame stop codon (TAA/TAG/TGA). Only count ORFs with a valid stop. Length is inclusive of stop (multiple of 3 bp).
   - Search all three frames. Consider every ATG as a potential start and evaluate the next in-frame stop; keep the maximum length observed.

6. Output formatting
   - Follow the exact labels and line order specified by the task. Preserve punctuation and spacing. Round GC% to one decimal.

## Algorithms and Reference Snippets

GC content (ignoring ambiguous bases in the denominator):
```python
def gc_content_percent(seq):
    s = seq.upper().replace('U', 'T')
    valid = sum(1 for c in s if c in 'ATCG')
    g = s.count('G')
    c = s.count('C')
    if valid == 0:
        return 0.0
    return round((g + c) / valid * 100, 1)
```

Frame translation (0-indexed frame; for frame 2 use frame=1):
```python
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

def translate_frame(seq, frame=0):
    s = seq.upper().replace('U', 'T')
    protein = []
    for i in range(frame, len(s) - 2, 3):
        codon = s[i:i+3]
        if any(ch not in 'ATCG' for ch in codon):
            protein.append('?')
        else:
            protein.append(CODON_TABLE.get(codon, '?'))
    return ''.join(protein)
```

Longest ORF length in bp (inclusive of stop), across frames:
```python
STOPS = {'TAA','TAG','TGA'}

def longest_orf_bp(seq):
    s = seq.upper().replace('U', 'T')
    best = 0
    for frame in range(3):
        # consider every ATG as a start candidate
        for i in range(frame, len(s) - 2, 3):
            codon = s[i:i+3]
            if codon != 'ATG':
                continue
            # scan to the first in-frame stop after this ATG
            for j in range(i + 3, len(s) - 2, 3):
                stop_codon = s[j:j+3]
                if stop_codon in STOPS:
                    length = (j - i) + 3  # include stop codon
                    if length > best:
                        best = length
                    break
    return best
```

## Verification

Use these checks before finalizing results:
- Sequence type:
  - If any U present and no T → RNA. If T present → DNA. If invalid letters → Protein.
- GC content:
  - 0.0 ≤ GC% ≤ 100.0. Recompute via an independent count to confirm.
  - Verify G + C ≤ total valid bases (A/T/C/G).
- Translation:
  - For frame f (1-based), offset = f - 1. Expected amino acid length = floor((len(sequence) - offset) / 3).
  - Ensure every three nucleotides yield exactly one output character (letter, *, or ?). Do not stop at '*'.
- Longest ORF:
  - Reported length must be a multiple of 3.
  - If nonzero, the segment should begin with ATG and end with TAA/TAG/TGA in the same frame.
  - Confirm all three frames were scanned.
- Output format:
  - Labels and order must match the task specification exactly. Round GC% to one decimal.

## Common Pitfalls

- Off-by-one frame errors (starting frame 2 at base 1 instead of base 2). Always compute offset = frame - 1 (0-indexed).
- Incorrect GC denominator (including N or invalid letters). Restrict denominator to A/T/C/G (or A/U/C/G for RNA) only.
- Truncating translation at the first stop when the task expects full frame translation with '*' symbols.
- Misclassifying sequence type by sanitizing away characters before detection. Detect type first, then normalize for downstream steps.
- Longest ORF errors:
  - Counting partial ORFs without a stop codon.
  - Stopping the search after the first ORF in a frame instead of considering all ATG starts.
  - Using the wrong start/stop sets (only ATG is a start; stops are TAA/TAG/TGA).
- Rounding GC% incorrectly (e.g., too many decimals, or rounding before multiplying by 100).
- Output formatting mismatches (wrong labels, missing percent sign, or extra commentary).

## Optional Script Usage

A helper script is provided to standardize computations.

Examples:
- Detect type and GC%:
  - python scripts/codon_tools.py --type --gc "ACGT..."
- Translate in frame 2:
  - python scripts/codon_tools.py --frame 2 "ACGT..."
- Find longest ORF length (bp):
  - python scripts/codon_tools.py --orf "ACGT..."

Integrate these outputs into the exact line-based format required by the task prompt.
