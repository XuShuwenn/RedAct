---
name: scikit-bio-alignment
description: "Calculate local alignment scores for DNA sequences using Smith-Waterman algorithm with scikit-bio."
---

# DNA Sequence Alignment Score

## When to Use

- Calculate local alignment scores
- Use Smith-Waterman algorithm
- Score DNA sequence alignments

## Input Format

File `/root/input.txt` with two DNA sequences (one per line)

## Scoring Scheme

- Match: +2
- Mismatch: -1
- Gap opening: -2
- Gap extension: -1

## Algorithm

Smith-Waterman for local alignment:
- Find highest scoring local alignment
- Allow gaps in either sequence
- Dynamic programming approach

## Output Format

To `/root/output.txt`:
```
Alignment score: X
```

Output is an integer (score can be negative).

## Using scikit-bio

```python
from skbio import Sequence
from skbio.alignment import local_pairwise_align

# Align sequences with scoring
```

## Tips

- Use skbio for alignment
- Implement scoring matrix
- Smith-Waterman for local (not global) alignment
- Check gap penalties


## Execution Protocol

## Execution Protocol

- Follow the task's required tool-call/action schema exactly. If the prompt specifies a `Thought`/`Action` JSON format, use that format instead of any default tool-calling style.
- If the task requires a specific final completion string, output that exact string verbatim and nothing else.
- When `/root/output.txt` is required, explicitly write it with a tool action/command; do not merely state that it was written.
- Prefer to verify the file after writing, e.g. by printing or reading `/root/output.txt`, before finishing.
