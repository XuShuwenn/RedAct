---
name: scikit-bio
description: "Local sequence alignment scoring using Smith-Waterman algorithm with affine gaps. Use when computing DNA alignment scores with match/mismatch and gap penalties."
---

# scikit-bio: Local Alignment Score (Smith-Waterman)

## Overview

Perform local alignment (Smith-Waterman) on two DNA sequences with affine gap scoring, then report the alignment score.

## Scoring Scheme

- Match: +2
- Mismatch: -1
- Gap opening: -2
- Gap extension: -1

## Smith-Waterman Algorithm with Affine Gaps

The local alignment algorithm with affine gaps uses three matrices:
- M: best score ending with a match/mismatch at (i,j)
- X: best score ending with a gap in sequence 1 (deletion)
- Y: best score ending with a gap in sequence 2 (insertion)

```python
def smith_waterman_affine(seq1, seq2, match=2, mismatch=-1, gap_open=-2, gap_extend=-1):
    m, n = len(seq1), len(seq2)

    # Initialize matrices with zeros
    M = [[0] * (n + 1) for _ in range(m + 1)]
    X = [[0] * (n + 1) for _ in range(m + 1)]  # gap in seq1
    Y = [[0] * (n + 1) for _ in range(m + 1)]  # gap in seq2

    max_score = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # Score if characters match
            if seq1[i-1] == seq2[j-1]:
                score = match
            else:
                score = mismatch

            # M[i][j]: best score ending with match/mismatch
            M[i][j] = max(0,
                          M[i-1][j-1] + score,
                          X[i-1][j-1] + score,
                          Y[i-1][j-1] + score)

            # X[i][j]: gap in seq1 (deletion in seq1)
            X[i][j] = max(0,
                          M[i-1][j] + gap_open,
                          X[i-1][j] + gap_extend)

            # Y[i][j]: gap in seq2 (insertion in seq1)
            Y[i][j] = max(0,
                          M[i][j-1] + gap_open,
                          Y[i][j-1] + gap_extend)

            # Track maximum score (local alignment can end anywhere)
            max_score = max(max_score, M[i][j], X[i][j], Y[i][j])

    return max_score
```

## Complete Implementation

```python
def read_sequences(filepath):
    with open(filepath) as f:
        lines = f.read().strip().split("\n")
    return lines[0].strip(), lines[1].strip()

def smith_waterman_affine(seq1, seq2, match=2, mismatch=-1, gap_open=-2, gap_extend=-1):
    m, n = len(seq1), len(seq2)

    M = [[0] * (n + 1) for _ in range(m + 1)]
    X = [[0] * (n + 1) for _ in range(m + 1)]
    Y = [[0] * (n + 1) for _ in range(m + 1)]

    max_score = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                score = match
            else:
                score = mismatch

            M[i][j] = max(0, M[i-1][j-1] + score, X[i-1][j-1] + score, Y[i-1][j-1] + score)
            X[i][j] = max(0, M[i-1][j] + gap_open, X[i-1][j] + gap_extend)
            Y[i][j] = max(0, M[i][j-1] + gap_open, Y[i][j-1] + gap_extend)

            max_score = max(max_score, M[i][j], X[i][j], Y[i][j])

    return max_score

# Main execution
seq1, seq2 = read_sequences("/root/input.txt")
score = smith_waterman_affine(seq1, seq2)

with open("/root/output.txt", "w") as f:
    f.write(f"Alignment score: {score}\n")
```

## Output Format

```
Alignment score: X
```

Output is an integer (score is always whole number).

## Key Reference

- Smith-Waterman: local alignment finds best substring match
- Affine gaps: separate gap open (-2) and gap extend (-1) penalties
- Score can be 0 if no positive alignment exists
- `local_pairwise_align_ssw` from skbio.alignment can also be used for simpler scoring