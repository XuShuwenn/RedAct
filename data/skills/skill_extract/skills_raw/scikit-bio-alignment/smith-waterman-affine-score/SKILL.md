---
name: smith-waterman-affine-score
description: "Compute a local alignment score for two sequences using the Smith–Waterman algorithm with affine gap penalties, with rigorous I/O parsing and output verification."
---

# Smith–Waterman Local Alignment (Affine Gaps) for Scoring

This skill provides a reusable workflow to compute a local alignment score between two sequences using the Smith–Waterman algorithm with affine gap penalties. It emphasizes correct input parsing, a validated dynamic programming implementation, and precise output formatting.

## When to Use

Use this skill when you need to:
- Compute a local alignment score (not a full alignment) for two sequences (DNA/RNA/protein/text) with specified scores for match, mismatch, gap opening, and gap extension.
- Apply affine gap penalties (gap open + extension for the first gap cell, and extension for continued gaps).
- Produce exact, minimal output formats such as “Alignment score: X”.

## Core Workflow

1. Parse Input
   - Read exactly two sequences from the specified source. Strip whitespace and ignore blank lines.
   - Normalize case (e.g., uppercase). Do not discard characters unless the task requires it. For scoring, equality of characters defines a match.
   - If fewer than two sequences are provided, abort with a clear error.

2. Parameterize Scoring
   - Use the provided scoring parameters or sensible defaults:
     - match > 0 (e.g., +2)
     - mismatch <= 0 (e.g., -1)
     - gap_open <= 0 (e.g., -2)
     - gap_extend <= 0 (e.g., -1)
   - Affine gap penalties apply as: first gap cell = gap_open + gap_extend; continuing gap = gap_extend.

3. Compute Smith–Waterman (Affine)
   - Maintain three DP states per cell (i, j):
     - M: best score ending with a match/mismatch at (i, j)
     - X: best score ending with a gap in sequence 1 (insertion in sequence 2)
     - Y: best score ending with a gap in sequence 2 (insertion in sequence 1)
   - Local alignment rule: every state is clamped at minimum 0; base row/column start at 0.
   - Recurrences (s is match/mismatch score at i, j):
     - M[i,j] = max(0, M[i-1,j-1] + s, X[i-1,j-1] + s, Y[i-1,j-1] + s)
     - X[i,j] = max(0, M[i-1,j] + gap_open + gap_extend, X[i-1,j] + gap_extend)
     - Y[i,j] = max(0, M[i,j-1] + gap_open + gap_extend, Y[i,j-1] + gap_extend)
   - The local alignment score is the maximum value observed across all M, X, and Y cells.
   - For large inputs, use a row-wise implementation to keep memory O(min(n, m)).

4. Output Formatting
   - Write exactly the required line, e.g.:
     - Alignment score: X
   - End with a newline. Do not add extra commentary or metadata to the output file.

5. Post-Compute Verification
   - Score must be a non-negative integer (local alignment cannot be negative).
   - Fast sanity checks:
     - Identical sequences of length L should yield L × match (if no gap is beneficial).
     - If at least one sequence is empty, score should be 0.
     - With all-negative pairings (e.g., all mismatches and gaps) and local alignment, score should be 0.
   - Re-open and read the output file to confirm it matches the exact pattern: `^Alignment score: \d+\n$`.

## Common Pitfalls and How to Avoid Them

- Claiming to write results without actually writing the file
  - Always perform a concrete file write, then re-open and read to confirm content.

- Using global (Needleman–Wunsch) instead of local (Smith–Waterman)
  - Ensure states are clamped to 0 and score is the maximum over all cells. Local alignment never yields negative scores.

- Ignoring affine gap states
  - Do not use a single-matrix linear gap penalty when affine gaps are required. Implement and track M, X, and Y states.

- Double-counting or misapplying gap penalties
  - The first gap cell uses gap_open + gap_extend; continued gaps add only gap_extend.

- Off-by-one indexing and wrong base cases
  - Initialize row 0 and column 0 to 0 for all states. Use s = match if chars equal, else mismatch.

- Formatting mistakes in the output
  - Include only the single required line and a trailing newline. No extra lines, code blocks, or explanations.

- Over-sanitizing input
  - Don’t delete non-ACGT characters unless required. Equality comparison defines a match. Treat all other pairs as mismatches.

## Success Criteria

- Reads exactly two sequences, normalizes them, and computes a non-negative integer score via Smith–Waterman with affine gaps.
- Writes exactly one line in the specified format with a newline.
- Passes quick sanity checks (identical inputs, empties) and internal verification of the output file content.

## Optional Script Usage

A portable helper is provided to compute the score with affine gaps and to print either a raw score or a formatted line. Examples:
- Compute and print raw score:
  - python scripts/smith_waterman_affine.py --seq1 "ACGT" --seq2 "ACGT"
- Compute with custom parameters:
  - python scripts/smith_waterman_affine.py --seq1 "ACGT" --seq2 "AGT" --match 3 --mismatch -2 --gap-open -5 --gap-extend -1
- Read sequences from a file (first two non-empty lines):
  - python scripts/smith_waterman_affine.py --input-file input.txt --emit-format
