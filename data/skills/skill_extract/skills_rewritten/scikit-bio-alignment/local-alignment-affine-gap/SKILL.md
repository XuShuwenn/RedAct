---
name: local-alignment-affine-gap
description: "Compute local alignment (Smith-Waterman) scores with affine gap penalties for two sequences and produce a correctly formatted, verified result."
---

# Local Alignment with Affine Gap Penalties

Use this skill when a task asks for the local alignment score between two sequences (e.g., DNA or general strings) using specific scoring rules (match, mismatch) and affine gap penalties (gap opening and gap extension). It focuses on implementing Smith-Waterman with affine gaps, verifying correctness, and writing the exact required output format.

## When to Use

Activate this skill for problems that specify:
- Local alignment (Smith-Waterman), not global alignment
- A scoring scheme with match/mismatch values
- Affine gap penalties (distinct opening and extension costs)
- A requirement to output only the alignment score as an integer or with a specific label

## Core Workflow

1. Clarify Requirements
   - Confirm the alignment is local (Smith-Waterman).
   - Record the scoring parameters: match, mismatch, gap opening, gap extension.
   - Confirm the required output format (e.g., "Alignment score: X" vs plain integer).

2. Read Inputs
   - Read exactly two sequences from the provided source.
   - Strip leading/trailing whitespace; preserve letters as-is. If the task specifies an alphabet (e.g., A/C/G/T), validate against it; otherwise treat as generic characters.
   - Handle empty lines: if either sequence is empty, the score should be 0 for local alignment.

3. Implement Smith-Waterman with Affine Gaps
   - Use three dynamic programming matrices to model match/mismatch and gaps separately:
     - M[i][j]: best score ending with a match/mismatch at positions i, j
     - Ix[i][j]: best score ending with a gap in the second sequence (an insertion relative to the first)
     - Iy[i][j]: best score ending with a gap in the first sequence (a deletion relative to the first)
   - Recurrence (local alignment floors at 0 to allow starting new local regions):
     - Let s(i,j) = match if seq1[i-1] == seq2[j-1], else mismatch
     - M[i][j] = max(0, max(M[i-1][j-1], Ix[i-1][j-1], Iy[i-1][j-1]) + s(i,j))
     - Ix[i][j] = max(0, M[i-1][j] + gap_open + gap_extend, Ix[i-1][j] + gap_extend)
     - Iy[i][j] = max(0, M[i][j-1] + gap_open + gap_extend, Iy[i][j-1] + gap_extend)
   - Track the best score across all cells: best = max(best, M[i][j], Ix[i][j], Iy[i][j]).
   - Time complexity is O(mn) for sequences of lengths m and n.

4. Compute and Format Output
   - Compute the integer best score.
   - Write the output exactly as specified by the task (e.g., a single line with the label and integer).
   - Avoid printing extra lines, punctuation, or spaces not required.

## Verification

Perform these checks before finalizing:
- Locality check: If mismatch and gap penalties are negative, a single mismatch-only comparison should yield 0, not a negative value (local alignment resets negatives to 0).
- Identity sanity check: For two identical sequences of length L, the score should be L × match (assuming no gaps and match > 0).
- Affine gap behavior: A gap of length k should penalize once with the opening cost and k times with extension, i.e., gap_open + k × gap_extend (the extension often applies for each gap position; depending on convention, k-1 extensions are used if opening includes the first position. Ensure your recurrence matches the intended convention and is consistent across both directions).
- Symmetry check: With equality-based scoring, swapping seq1 and seq2 yields the same score.
- Boundary check: Empty sequence vs any sequence should produce 0.
- Output format check: Confirm the output contains exactly the required line and an integer score.

## Common Pitfalls

- Using global alignment (Needleman-Wunsch) instead of local (Smith-Waterman). Symptom: scores influenced by ends of sequences; negative totals not zeroed.
- Ignoring affine gaps and using a single gap penalty, which mis-scores long gaps.
- Forgetting the local alignment reset: not applying max(..., 0) in the DP causes negative propagation and wrong scores.
- Mis-indexing DP transitions (off-by-one errors) or using the wrong previous states for Ix/Iy.
- Skipping input validation or assuming sequences are identical without computing the score.
- Producing extra output or wrong label/format, causing scoring to be rejected.

## Success Criteria

- The algorithm applies Smith-Waterman with affine gaps via three DP matrices.
- The computed score passes sanity checks (identity, mismatch-only, gap behavior, empty cases).
- The final output matches the exact format required by the task and contains an integer score.
- No extraneous prints or debug lines are present.

## Optional Script Usage

Use the helper script to compute the score deterministically:
- Example:
  - python scripts/smith_waterman.py --seq1 ACTG --seq2 ACTG --match 2 --mismatch -1 --gap-open -2 --gap-extend -1
  - Or read from a file containing two lines:
    - python scripts/smith_waterman.py --file input.txt --match 2 --mismatch -1 --gap-open -2 --gap-extend -1 --label "Alignment score: "
- The script prints the score, optionally prefixed by a label.
