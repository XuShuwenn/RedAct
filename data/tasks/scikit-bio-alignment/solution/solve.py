#!/usr/bin/env python3
"""Solve scikit-bio-alignment task."""

def read_sequences(filepath):
    with open(filepath) as f:
        lines = f.read().strip().split("\n")
    return lines[0].strip(), lines[1].strip()


def smith_waterman_affine(seq1, seq2, match=2, mismatch=-1, gap_open=-2, gap_extend=-1):
    """Smith-Waterman local alignment with affine gaps."""
    m, n = len(seq1), len(seq2)

    M = [[0] * (n + 1) for _ in range(m + 1)]
    X = [[0] * (n + 1) for _ in range(m + 1)]  # gap in seq1
    Y = [[0] * (n + 1) for _ in range(m + 1)]  # gap in seq2

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


def main():
    seq1, seq2 = read_sequences("/root/input.txt")
    score = smith_waterman_affine(seq1, seq2)

    output = f"Alignment score: {score}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(output)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(output)


if __name__ == "__main__":
    main()
