---
name: nucleotide-translate-orf
description: "Classify DNA/RNA vs protein, compute GC%, translate in a specified frame with stop codons marked '*', and find the longest valid ORF across all three frames."
---

# Nucleotide Translation and ORF Analysis

Reusable workflow for sequence-type detection (DNA/RNA/Protein), GC% calculation, fixed-frame translation, and longest ORF detection.

## When to Use

Use this skill when a task requires:
- determining whether a given sequence is DNA, RNA, or protein
- computing GC content (as a percentage, rounded to 1 decimal place)
- translating a nucleotide sequence in a specified reading frame (with stop codons shown as `*` and translation continuing past stops)
- finding the longest valid open reading frame (ORF) across all three reading frames

## Core Workflow

1. Normalize input:
   - Strip whitespace and newlines. Work in uppercase for computation while retaining original for classification.
   - For translation/ORF detection, convert RNA to DNA by replacing `U` with `T`.

2. Determine sequence type:
   - DNA if: contains `T`, contains no `U`, and all characters are within A/T/C/G/N.
   - RNA if: contains `U`, contains no `T`, and all characters are within A/U/C/G/N.
   - Otherwise, if letters are consistent with amino acids, classify as Protein; else default to Protein for non-nucleotide inputs.

3. GC content (for nucleotide sequences):
   - Count G and C.
   - Denominator is the total length excluding ambiguous `N` (or `n`) characters.
   - GC% = ((G + C) / (length - N)) × 100; round to 1 decimal place.
   - If the sequence contains only ambiguous bases after exclusion, report an error or 0% with a note, per task instructions.

4. Fixed-frame translation:
   - Frames are 1-indexed in user tasks; map to zero-based offsets: frame 1 → offset 0, frame 2 → offset 1, frame 3 → offset 2.
   - Translate contiguous codons from the chosen offset to the end, ignoring trailing incomplete codons.
   - Use the standard DNA codon table (T-based). Mark stop codons as `*`.
   - Do not terminate translation at `*`; include the `*` and continue translating remaining codons.
   - Unknown/ambiguous codons (e.g., containing `N`) may be mapped to `?` to preserve length.

5. Longest ORF across frames:
   - Definition: An ORF starts at `ATG` and ends at the first in-frame stop codon (`TAA`, `TAG`, or `TGA`) downstream in the same frame.
   - Only consider ORFs that have both a start and a stop codon in-frame.
   - ORF length is counted in base pairs and includes both the start and stop codons; it is always a multiple of 3.
   - Scan each frame independently and evaluate all possible start positions; keep the maximum length found across frames. If none found, result is 0 bp (or per task requirements).

6. Output formatting:
   - Follow the exact line format specified by the task. Avoid adding extra commentary or additional lines to the output file.

## Algorithms

- Sequence type rules:
  - Contains `U` and not `T` → RNA
  - Contains `T` and not `U` → DNA
  - Else → Protein (fallback unless task specifies different handling)

- GC% calculation (ignoring `N`):
  - gc_percent = round(((count('G') + count('C')) / (len(seq) - count('N'))) * 100, 1)

- Translation (frame k ∈ {1,2,3}):
  - offset = k - 1
  - Iterate i from offset to len(seq)-3 inclusive in steps of 3; map seq[i:i+3] to amino acid using the standard DNA codon table (T-based), defaulting to `?` if not found.

- Longest ORF:
  - For each frame offset in {0,1,2}:
    - Iterate codons in steps of 3.
    - On `ATG`, search forward in-frame for the first stop codon; if found, ORF length = (stop_index + 3) - start_index; update best; continue scanning to find other ORFs in the frame.

## Verification

Before finalizing, apply these checks:
- GC% rounding: ensure exactly one decimal place is output for GC%.
- Frame mapping: verify that frame 2 uses offset 1 (start from the second nucleotide).
- Translation length invariant: len(translation) equals floor((len(seq) - offset) / 3).
- Stop handling: translation string can contain `*`; it must not truncate at the first `*`.
- ORF validity: if reported ORF length > 0, it is divisible by 3; ensure that a valid `ATG` occurs before an in-frame stop in the same frame.
- Output format: confirm the file contains exactly the four required lines with correct labels and punctuation (or per task specification).

## Common Pitfalls (and how to avoid them)

- Truncating translation at the first `*` stop codon.
  - Fix: Always translate the entire frame and include `*` characters where stops occur.

- Off-by-one frame selection.
  - Fix: Map frame numbers to zero-based offsets explicitly (2 → offset 1). Check translation length invariant.

- Counting ORFs that lack an in-frame stop codon.
  - Fix: Only count ORFs that terminate at an in-frame stop; runs extending to the sequence end without a stop are not valid ORFs.

- Excluding the stop codon from ORF length or mixing codon/bp units.
  - Fix: Report ORF length in base pairs and include the stop codon (length is a multiple of 3).

- Incorrect GC% due to including `N` in the denominator or rounding incorrectly.
  - Fix: Exclude `N` from the denominator; round to one decimal place.

- Misclassification of DNA vs RNA with mixed T/U content.
  - Fix: If both T and U are present, treat as invalid nucleotide input for this workflow and fall back to Protein only if explicitly required.

- Polluting the output with extra lines or formatting.
  - Fix: Write exactly the lines required by the task.

## Optional Script Usage

A helper script is provided to perform translation and longest-ORF detection and to compute GC%.

Examples:
- Translate frame 2:
  - python scripts/seq_frame_tools.py --sequence "<SEQUENCE>" --frame 2
- Find longest ORF length in bp:
  - python scripts/seq_frame_tools.py --sequence "<SEQUENCE>" --longest-orf
- Compute GC%:
  - python scripts/seq_frame_tools.py --sequence "<SEQUENCE>" --gc

Integrate these outputs into the exact file format required by your task.
