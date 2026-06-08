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

- Read `/root/input.txt` before doing any computation.
- Treat line 1 as sequence 1 and line 2 as sequence 2.
- Use the sequences exactly as provided; do not invent, reorder, or preprocess them unless the task explicitly says to.


## Scoring Scheme

- Match: +2
- Mismatch: -1
- Gap opening: -2
- Gap extension: -1

Use affine-gap local alignment: apply gap opening and gap extension separately. Do not collapse them into a single gap penalty or substitute library defaults.

## Algorithm

Smith-Waterman for local alignment:
- Find highest scoring local alignment
- Allow gaps in either sequence
- Use dynamic programming with affine-gap states: match/mismatch (`M`), gap in seq1 (`X`), gap in seq2 (`Y`)
- For local alignment, include resets with `max(0, ...)` so negative-running alignments restart
- Track the maximum score seen in any DP state; do not use the bottom-right cell unless it is also the global maximum
- Apply the requested scoring scheme directly; do not substitute a global-alignment method or a simpler heuristic

## Output Format

To `/root/output.txt`:
```
Alignment score: X
```

Output is a non-negative integer for Smith-Waterman local alignment because scores can reset to 0.

- Match the output string exactly: `Alignment score: X` with the integer score substituted for `X`.

## Using scikit-bio

```python
from skbio import Sequence
from skbio.alignment import local_pairwise_align


Keep the exact scoring model. If a scikit-bio call would not preserve separate gap opening and extension costs cleanly, implement the affine-gap Smith-Waterman score explicitly instead of approximating it.

# Align sequences with scoring
```

## Tips

- Use scikit-bio if it directly supports the required local affine-gap scoring behavior; otherwise implement the DP yourself.
- Handle affine gaps correctly: gap opening and gap extension are separate penalties.
- If implementing the recurrence directly, use explicit DP states for aligned, vertical-gap, and horizontal-gap cases.
- Smith-Waterman is local, not global: include reset-to-0 behavior and take the best score anywhere.
- Do not substitute a global alignment method, edit distance, or other simplified calculation for the requested score.
- Check obvious cases before full alignment work: if the sequences are identical, the best local alignment is the full sequence and the score is `2 * len(sequence)`.
- Also inspect for an obvious contiguous exact-match region; with match `+2` and mismatches/gaps penalized, that pure-match segment may already determine the optimal local score.
- Use a shortcut only when the optimal local alignment is structurally obvious; otherwise fall back to full Smith-Waterman.
- After writing `/root/output.txt`, read it back or print it to confirm the text matches the required literal format exactly.
## Execution Protocol

- Follow the task's required tool-call/action schema exactly. If the prompt specifies a `Thought`/`Action` JSON format, use that format instead of any default tool-calling style.
- If the task requires a specific final completion string, output that exact string verbatim and nothing else.
- When `/root/output.txt` is required, explicitly write it with a tool action/command; do not merely state that it was written.
- Prefer to verify the file after writing, e.g. by printing or reading `/root/output.txt`, before finishing.
