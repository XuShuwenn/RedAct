# Timeout-Safe Execution

Use this when the environment kills jobs after periods without output.

## Core rule

Do not trust a monolithic full-grid search to survive. Structure execution as small, resumable chunks that each:
1. finish within the timeout budget,
2. emit progress during the expensive part, and
3. persist an artifact before the next chunk starts.

## Required adaptations after the first timeout

- Do **not** rerun the same full search with only superficial edits.
- Reduce scope to one approximant or a small mass block.
- Add progress prints from inside the expensive loop, not only before it.
- Use unbuffered output or explicit flushes so messages appear before cancellation.
- Save best-so-far results after each chunk.


- Base any speed or stability change on the last observed progress point or stage timing; do not rewrite the search loop from a generic guess about what is slow.
- After making a timeout-driven change, rerun one chunk immediately and confirm both observable mid-run progress and a readable checkpoint/output artifact before making further edits.
- A timeout recovery is incomplete until the retried run has been executed; editing alone does not count.

## Minimal execution pattern

- Choose a chunk unit: one approximant, or one approximant plus a small contiguous mass range.
- Before scaling up, run one chunk and confirm all three of these are true:
  - it completes within the timeout budget,
  - progress appears during computation,
  - a checkpoint/result file is written and can be read back.
- Repeat the same chunk pattern until coverage is complete.
- Merge checkpointed best rows into `/root/detection_results.csv` only after all required chunks finish.

## Progress-printing pattern

Use prints that happen repeatedly during the search and are flushed immediately, e.g.:

```python
print(f"starting {approximant}", flush=True)
for i, (m1, m2) in enumerate(mass_pairs, 1):
    # expensive work here
    if i % 10 == 0 or i == len(mass_pairs):
        print(f"{approximant}: completed {i}/{len(mass_pairs)} templates", flush=True)
```

If one template evaluation itself is very slow, print at stage boundaries inside that evaluation too.

## Do / Do not

- Do prove one bounded chunk works before launching many.
- Do checkpoint after each chunk.
- Do prefer repeated foreground chunks to an opaque long run when timeout behavior is strict.
- Do not assume a startup message is enough to prevent no-output cancellation.
- Do not leave progress only in memory; write durable partial results.
- Do not claim the timeout adaptation is done until a retried run has actually produced mid-run output and a finished chunk.

- Do treat the first retry after a timeout as a proof step: one bounded chunk must complete within the limit, emit mid-run output, and write a readable checkpoint/result artifact.
- Do monitor long runs through concrete artifacts you know how to inspect here, such as log files, checkpoint CSVs, or Python one-liners that print file size, last lines, or parsed partial results.
- Do treat repeated status polling with no new artifact as failure to make progress; after one or two checks, launch the next bounded chunk or diagnostic instead.
- Do not issue natural-language shell text as if it were a command.
- Do not kill or relaunch long searches repeatedly unless the replacement plan has first succeeded on one bounded chunk.
