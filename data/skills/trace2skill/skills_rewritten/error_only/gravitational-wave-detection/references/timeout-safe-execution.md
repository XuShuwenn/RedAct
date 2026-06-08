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
