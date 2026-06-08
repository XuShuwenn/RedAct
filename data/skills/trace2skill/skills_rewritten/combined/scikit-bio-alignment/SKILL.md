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

- If the workspace may contain multiple files, you may quickly inspect the relevant directory first to confirm `/root/input.txt` is present, but treat `/root/input.txt` as the authoritative source.
- Extract and inspect both raw sequence lines from `/root/input.txt` before choosing an approach, selecting any shortcut, or deciding whether scikit-bio is suitable.
- Confirm the file provides exactly two sequence lines and base every calculation on those exact observed strings; do not infer the sequences from the prompt or other files when `/root/input.txt` is provided.
- Choose a shortcut only for structurally obvious cases such as exact end-to-end identity, clear substring containment, or an obvious contiguous exact-match block; otherwise run the full affine-gap Smith-Waterman scoring procedure.
- Prefer a short self-contained script to read the sequences exactly as written, compute the score, write `/root/output.txt`, and verify it rather than doing DP arithmetic manually.


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

- Use Smith-Waterman as the primary computation method; do not replace it with an indirect shortcut unless the optimal local score is immediately forced by the observed input and the stated scoring rules.

## Output Format

To `/root/output.txt`:
```
Alignment score: X
```

Output is a non-negative integer for Smith-Waterman local alignment because scores can reset to 0.

- Match the output string exactly: `Alignment score: X` with the integer score substituted for `X`.

- Write the required line verbatim once the score is known; avoid extra lines, commentary, or alternate labels in `/root/output.txt`.
- Compute the score first, then explicitly write `/root/output.txt`, then verify the saved file contents before finishing.

## Using scikit-bio

```python
from skbio import Sequence
from skbio.alignment import local_pairwise_align


Keep the exact scoring model. If a scikit-bio call would not preserve separate gap opening and extension costs cleanly, implement the affine-gap Smith-Waterman score explicitly instead of approximating it.

- Decide only after reading the input whether scikit-bio cleanly supports the exact required local affine-gap score; if not, switch immediately to a short Python DP script rather than forcing a library approximation.
- Prefer a short Python script for the full workflow: read `/root/input.txt`, compute the score exactly, and write `/root/output.txt` in one run.

# Align sequences with scoring
```

## Tips

- Use scikit-bio if it directly supports the required local affine-gap scoring behavior; otherwise implement the DP yourself.
- Handle affine gaps correctly: gap opening and gap extension are separate penalties.
- If implementing the recurrence directly, use explicit DP states for aligned, vertical-gap, and horizontal-gap cases.
- Smith-Waterman is local, not global: include reset-to-0 behavior and take the best score anywhere.
- Do not substitute a global alignment method, edit distance, or other simplified calculation for the requested score.
- Check the concrete input before choosing a method.
- If the sequences are identical end-to-end, the optimal local alignment is the full sequence and the score is `2 * len(sequence)`.
- Also check whether one sequence appears as an exact contiguous substring of the other, or whether there is a clearly dominant exact contiguous match block; that gap-free exact-match region is a valid local alignment candidate with score `2 * len(region)`.
- Make any shortcut decision from the raw contents of `/root/input.txt`, not from assumptions.
- Use a shortcut only when the optimal local alignment is structurally obvious and you can justify that no better local alignment with mismatches or gaps can score higher; if there is any ambiguity, run the full affine-gap Smith-Waterman DP and take the maximum score over all cells/states.
- When using an obvious-structure shortcut, explicitly translate the observed structure into the requested numeric score under this scheme before writing the answer.
- After computing a score, do a quick sanity check against simple input structure when possible before finalizing.
- After writing `/root/output.txt`, read it back or print it to confirm the text matches the required literal format exactly.

- Prefer a short deterministic Python script to compute the score consistently rather than manual reasoning.
- If the environment already contains a visible script or function that implements the required local affine-gap alignment with the specified scoring, prefer running and validating that implementation instead of re-deriving the score manually.
- When a script or library call computes the score, treat that returned numeric result as authoritative and carry it unchanged into `/root/output.txt`.
## Execution Protocol

- Follow the task's required tool-call/action schema exactly. If the prompt specifies a `Thought`/`Action` JSON format, use that format instead of any default tool-calling style.
- If the task requires a specific final completion string, output that exact string verbatim and nothing else.
- When `/root/output.txt` is required, explicitly write it with a tool action/command; do not merely state that it was written.
- Prefer to verify the file after writing, e.g. by printing or reading `/root/output.txt`, before finishing.

- Use an observable write step for `/root/output.txt` (for example, a shell redirection, `python` file write, or editor tool action); do not infer that the file exists from the computed score alone.
- Do not claim the file was written unless the log shows the write command/action or an explicit readback of `/root/output.txt`.
- Keep the reliable order of operations for file-based tasks: read `/root/input.txt` -> compute the score -> write `/root/output.txt` -> verify `/root/output.txt` -> emit any required final completion string.
- Prefer an auditable one-script workflow for this task whenever practical.

- Before finishing, complete this checklist in order: (1) explicitly write `/root/output.txt`; (2) verify the file by reading or printing it; (3) only then emit the exact required final completion string.
- Do not say the file was written unless the log includes the actual write command/action or an explicit confirmation readback of `/root/output.txt`.
- If the environment requires a completion signal such as `ACTION: TASK_COMPLETE`, output that exact string verbatim as the final message, with no extra text before or after.
- Treat required completion strings as higher priority than any default conversational wrap-up; never end with explanatory prose when an exact terminator is specified.

