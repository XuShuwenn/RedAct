---
name: reading-frame-translation-orf
description: "Determine sequence type, compute GC%, translate a specified reading frame without truncating at stops, and find the longest valid ORF across frames."
---

Reading Frame Translation and ORF Analysis

Skill for nucleotide sequence tasks that require: sequence type determination (DNA/RNA/Protein), GC content calculation, translating a specified reading frame with stop codons represented as '*', and identifying the longest open reading frame (ORF) across all three frames.

When to Use

- The user asks to translate a DNA sequence in a specific reading frame
- You must compute GC content to one decimal place
- You need to find the longest ORF defined by a start codon (ATG) and an in-frame stop codon (TAA/TAG/TGA)
- The task specifies an exact output format with lines like "Sequence type:", "GC content:", "Frame N translation:", and "Longest ORF length:" (match capitalization, punctuation, and spacing exactly)

Core Workflow

1) Ingest and normalize the sequence
- Read the sequence from the provided input.
- Strip whitespace and newlines; convert to uppercase.
- For translation, treat the input as DNA (T, not U). If RNA is provided but translation is requested, convert U to T.

2) Determine sequence type
- DNA if the sequence contains T and no U and all characters are among A/C/G/T/N.
- RNA if the sequence contains U (and no T) and all characters are among A/C/G/U/N.
- Protein if all characters are amino-acid letters (A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y) and no T/U mix indicative of nucleic acids.
- If mixed/ambiguous, prefer DNA/RNA determination based on presence of T or U; otherwise report Protein only if nucleic-acid letters are violated.

3) Compute GC content
- For nucleotide sequences (DNA or RNA): GC% = ((G + C) / (A + C + G + T)) × 100.
- Ignore ambiguous bases (e.g., N) in the denominator to avoid skew.
- Round to 1 decimal place.

4) Translate a specific reading frame
- Frame indexing: Frame 1 offset=0; Frame 2 offset=1; Frame 3 offset=2.
- Iterate codons from the chosen offset in steps of 3 until fewer than 3 bases remain.
- Use the standard DNA codon table with stop codons mapped to '*'.
- Do not truncate the translation at the first '*'; return the full translation string across the entire frame.

5) Find the longest ORF across all three frames
- ORF definition: starts with ATG and ends with an in-frame stop (TAA, TAG, or TGA) in the same frame. ORFs that reach the end without an in-frame stop are not valid.
- Search each frame independently and consider all ATG start positions in that frame.
- For each start, scan forward codon-by-codon to the first in-frame stop:
  - If a stop is found, record the ORF length in base pairs.
  - If no stop is found before the sequence ends, discard that candidate.
- Unless tasks specify otherwise, report the ORF length inclusive of the stop codon (start through stop, multiples of 3). If a task explicitly defines a different convention, adjust accordingly.
- Return the maximum length across the three frames; if none exist, return 0.

Implementation Snippets

Sequence type detection

```
def detect_seq_type(seq: str) -> str:
    s = seq.strip().upper()
    dna_set = set("ACGTN")
    rna_set = set("ACGUN")
    if "U" in s and "T" not in s and set(s) <= rna_set:
        return "RNA"
    if "T" in s and "U" not in s and set(s) <= dna_set:
        return "DNA"
    aa_set = set("ACDEFGHIKLMNPQRSTVWY")
    if set(s) <= aa_set:
        return "Protein"
    # Fallback: prefer DNA if T present, RNA if U present, else Protein
    if "T" in s:
        return "DNA"
    if "U" in s:
        return "RNA"
    return "Protein"
```

GC content (ignore ambiguous N)

```
def gc_percent(seq: str) -> float:
    s = seq.strip().upper()
    a = s.count('A')
    c = s.count('C')
    g = s.count('G')
    t = s.count('T')
    denom = a + c + g + t
    if denom == 0:
        return 0.0
    pct = (c + g) / denom * 100.0
    return round(pct, 1)
```

Frame translation (do not truncate at stop)

```
CODON_TABLE = {
    'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L','CTA':'L','CTG':'L',
    'ATT':'I','ATC':'I','ATA':'I','ATG':'M','GTT':'V','GTC':'V','GTA':'V','GTG':'V',
    'TCT':'S','TCC':'S','TCA':'S','TCG':'S','CCT':'P','CCC':'P','CCA':'P','CCG':'P',
    'ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A','GCA':'A','GCG':'A',
    'TAT':'Y','TAC':'Y','TAA':'*','TAG':'*','CAT':'H','CAC':'H','CAA':'Q','CAG':'Q',
    'AAT':'N','AAC':'N','AAA':'K','AAG':'K','GAT':'D','GAC':'D','GAA':'E','GAG':'E',
    'TGT':'C','TGC':'C','TGA':'*','TGG':'W','CGT':'R','CGC':'R','CGA':'R','CGG':'R',
    'AGT':'S','AGC':'S','AGA':'R','AGG':'R','GGT':'G','GGC':'G','GGA':'G','GGG':'G',
}

def translate_frame(seq: str, frame: int) -> str:
    """Translate DNA in 1-indexed frame (1, 2, or 3), mapping stops to '*'."""
    s = seq.strip().upper().replace('U', 'T')
    offset = {1:0, 2:1, 3:2}.get(frame, 0)
    prot = []
    for i in range(offset, len(s) - 2, 3):
        codon = s[i:i+3]
        aa = CODON_TABLE.get(codon, '?')
        prot.append(aa)
    return ''.join(prot)
```

Longest ORF across frames (inclusive of stop codon by default)

```
STOPS = {'TAA','TAG','TGA'}

def longest_orf_bp(seq: str, include_stop: bool = True) -> int:
    s = seq.strip().upper().replace('U', 'T')
    best = 0
    n = len(s)
    for offset in (0, 1, 2):
        i = offset
        while i <= n - 3:
            codon = s[i:i+3]
            if codon == 'ATG':
                j = i + 3
                while j <= n - 3:
                    c = s[j:j+3]
                    if c in STOPS:
                        length = (j - i + 3) if include_stop else (j - i)
                        if length > best:
                            best = length
                        break
                    j += 3
                # continue scanning for additional start sites after this i
            i += 3
    return best
```

Verification

- Input normalization
  - After stripping and uppercasing, confirm only expected characters remain.
  - For translation, ensure you are treating T as thymine. Convert U→T if necessary.

- GC content
  - Check denominator equals A+C+G+T (ignoring N). If this is 0, return 0.0 or error accordingly.
  - Round the final percentage to exactly one decimal place.

- Frame translation
  - For frame F, translated length must equal floor((len(seq) - offset)/3).
  - The translated string may contain '*' characters; do not truncate on the first '*'.
  - If unknown codons appear (e.g., ambiguous bases), they should map to a placeholder (e.g., '?') so the output length remains consistent.

- Longest ORF
  - Validate that the reported ORF length is a multiple of 3 and ≥ 6 (start + stop of at least two codons).
  - Confirm the ORF begins with ATG and ends with one of TAA/TAG/TGA in the same frame.
  - Ensure ORFs that reach the end without a stop are excluded (length should not extend to the sequence end unless a stop is present).
  - Scan all three frames; verify you take the maximum length.

Common Pitfalls and How to Avoid Them

- Truncating translation at first stop codon
  - Requirement often asks for the full-frame translation with '*' marking stops. Continue translating across the entire frame.

- Misinterpreting frame indexing
  - Many interfaces are 1-indexed for frames. Convert frame 1→offset 0, frame 2→offset 1, frame 3→offset 2.

- Counting ORFs without a terminating stop
  - Do not report ORFs that run off the end without an in-frame stop. Only start-to-stop segments count.

- Inconsistent ORF length convention
  - Some tasks include the stop codon in the ORF length; others exclude it. Unless specified, use an inclusive length consistently and document it; adjust if the task defines a different convention.

- Wrong GC denominator or rounding
  - Exclude ambiguous bases (e.g., N) from the denominator and round to exactly one decimal place.

- Ignoring trailing bases
  - Do not translate trailing 1–2 bases that don't form a full codon.

- Case and whitespace issues
  - Always strip whitespace and uppercase the sequence before analysis.

Output Format Guidance

If the task requires specific lines, match them exactly, for example:
- Sequence type: DNA|RNA|Protein
- GC content: XX.X%
- Frame 2 translation: <protein string>
- Longest ORF length: <integer> bp

Optional Script Usage

The included helper script implements these algorithms and can be used for quick validation or as a reference implementation.

Examples:
- Print type and GC%:
  - python scripts/seq_frame_tools.py --sequence "ACGT..." --type --gc
- Translate frame 2:
  - python scripts/seq_frame_tools.py --sequence "ACGT..." --frame 2
- Longest ORF (inclusive of stop):
  - python scripts/seq_frame_tools.py --sequence "ACGT..." --longest-orf
- Longest ORF (exclusive of stop):
  - python scripts/seq_frame_tools.py --sequence "ACGT..." --longest-orf --exclude-stop
