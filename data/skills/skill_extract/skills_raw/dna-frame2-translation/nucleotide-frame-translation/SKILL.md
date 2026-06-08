---
name: nucleotide-frame-translation
description: "Analyze nucleotide sequences: detect type, compute GC%, translate in a specified reading frame with '*' for stops, and find the longest ORF that starts at ATG and ends at an in-frame stop."
---

# Nucleotide Sequence Frame Translation and ORF Analysis

Reusable workflow for tasks that require:
- determining whether an input sequence is DNA, RNA, or protein
- calculating GC content as a percentage (rounded to 1 decimal place)
- translating a nucleotide sequence in a specified reading frame (stop codons rendered as *)
- finding the length of the longest open reading frame (ORF) across all three frames (ATG start; TAA/TAG/TGA stop; length includes the stop codon)
- writing results to an output file in an exact line-by-line format

## When to Use

Activate this skill when a prompt requests sequence type identification, GC% computation, frame-specific translation, and/or longest ORF length from a provided nucleotide sequence, especially when strict output formatting is required.

## Core Workflow

1. Ingest and Normalize Input
   - Read the sequence from the provided source (e.g., a file path in the prompt).
   - Remove whitespace and newlines; uppercase the sequence.
   - For DNA/RNA workflows, retain only valid characters (DNA: A/C/G/T/N; RNA: A/C/G/U/N) for computation. Preserve input to decide type first.

2. Determine Sequence Type
   - DNA: contains T and no U, and all chars in A/C/G/T/N
   - RNA: contains U and no T, and all chars in A/C/G/U/N
   - Otherwise: treat as protein (non-nucleotide letters present or both T and U present)

3. GC Content (for DNA/RNA)
   - Let G = count("G"), C = count("C"), N = count("N").
   - Compute denominator as total_length − N (ignore ambiguous N bases).
   - GC% = ((G + C) / denominator) × 100, rounded to 1 decimal place.
   - Edge case: if denominator is 0, report an error or 0.0% per task’s instructions.

4. Frame-Specific Translation (DNA)
   - Confirm the sequence is DNA. If RNA, convert U→T or report per task.
   - Define frame offset: frame 1 → offset 0; frame 2 → offset 1; frame 3 → offset 2.
   - Translate from offset in non-overlapping triplets until the last complete codon.
   - Use standard genetic code; map TAA/TAG/TGA to '*'.
   - Do not stop translation at the first '*': include '*' in the output and continue translating remaining full codons.

5. Longest ORF Across All Three Frames (DNA)
   - ORF definition: begins at 'ATG' and ends at an in-frame stop (TAA/TAG/TGA). Report the DNA length in base pairs, including the stop codon.
   - Scan each frame independently:
     - Iterate codons in steps of 3.
     - When 'ATG' is encountered and not already in an ORF, mark start.
     - Continue until a stop codon appears; compute length = (stop_index − start_index + 3). Record the maximum across all frames.
     - Reset after each closed ORF and continue scanning for additional ORFs.
   - If no start-to-stop ORF exists in any frame, the length is 0 bp.

6. Output Formatting
   - Write outputs exactly as specified by the task (labels, order, punctuation, and spacing). Do not add extra commentary, bullets, or tables to the output file.
   - Example label structure (adjust per prompt):
     - Sequence type: {DNA|RNA|Protein}
     - GC content: XX.X%
     - Frame N translation: ...
     - Longest ORF length: N bp

## Verification

Before finalizing, perform these checks:
- Type check: T present without U → DNA; U present without T → RNA; otherwise protein. Validate only allowed characters for nucleotide types.
- GC%:
  - Recompute independently and ensure one-decimal rounding matches.
  - Ensure 0.0 ≤ GC% ≤ 100.0.
  - Confirm denominator excludes Ns.
- Translation:
  - Length of translation string equals floor((len(seq) − offset) / 3).
  - Spot-check a few codons: 'ATG' → 'M'; stop codons → '*'.
  - Ensure translation continues past any '*'.
- Longest ORF:
  - If length > 0, verify start codon at ORF start and a valid stop at the end.
  - Length must be a multiple of 3 and ≤ sequence length.
  - Confirm the reported value is the maximum among frames.
- Output file:
  - Confirm the file exists and contains exactly the required lines, with no extra or missing lines, and exact label text/capitalization.

## Common Pitfalls and How to Avoid Them

- Stopping translation at the first stop codon: Keep translating and include '*' for each stop codon encountered.
- Frame indexing errors: Frame 2 means offset 1 (start from the second nucleotide). Use 1-indexed frames → 0-indexed offsets.
- ORF definition mistakes:
  - Counting an ORF that lacks an in-frame stop codon (running to sequence end) → invalid.
  - Forgetting to include the stop codon in the ORF length → undercount.
  - Reporting an ORF on the wrong strand or reverse complement when not requested.
- GC% miscalculation:
  - Including 'N' in the denominator or omitting lowercase bases due to case sensitivity.
  - Using incorrect rounding (e.g., more than 1 decimal). Always round to 1 decimal place when specified.
- Output formatting drift:
  - Adding bullets, markdown tables, extra notes, or different label text in the output file.
  - Changing label capitalization or order.
- Input handling issues:
  - Not stripping whitespace/newlines before processing.
  - Allowing non-nucleotide characters to pass into translation or ORF finder.

## Optional Script Usage

Use the helper script `scripts/nucleotide_tools.py` for deterministic, reusable computation and quick verification.

Examples:
- Detect type and GC%:
  - python scripts/nucleotide_tools.py --sequence "ACGT..." --detect-type --gc
- Translate in frame 2 and find the longest ORF:
  - python scripts/nucleotide_tools.py --sequence "ACGT..." --translate-frame 2 --longest-orf

The script prints concise results for spot-checking. Integrate its functions in your solution code to ensure consistent algorithms and rounding.
