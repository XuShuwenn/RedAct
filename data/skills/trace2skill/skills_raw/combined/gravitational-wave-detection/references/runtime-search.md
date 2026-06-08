# Runtime Search Guide

Use this when the required approximant and mass sweep may be expensive.

## Checklist

1. Run a tiny pilot subset first.
2. Measure elapsed time per job and estimate the full sweep cost.
3. Before any full launch, write down the execution plan: serial or batched, expected batch sizes, how progress will be observed, and how best-per-approximant checkpoints will be stored.
4. Validate the exact script to be executed with a syntax/import check and a tiny foreground trial.
5. Reuse shared preprocessing work such as conditioned strain data and PSD.
6. If splitting execution, factor shared preprocessing out of per-approximant jobs so workers do not each reload, condition, and estimate PSD independently.
7. Before backgrounding a long run, decide how you will poll completion, inspect logs, and verify the final CSV.
8. If splitting the grid, record which approximants and mass subranges are complete so no required coverage is skipped.
9. If the pilot suggests the naive full sweep will not finish in time, restructure immediately into resumable batches rather than launching and later aborting a monolithic run.
10. If needed, execute in batches or per approximant while checkpointing intermediate best results.
11. Merge verified final best rows into `/root/detection_results.csv`.
12. After merging, read back `/root/detection_results.csv` and verify it has exactly the required final rows and columns.

## Do / Do not

- Do validate any rewritten or optimized script by actually running it.
- Do preserve the required final search unless the task explicitly permits approximation.
- Do inspect the final CSV before concluding.
- Do not spend the full budget on an unprofiled brute-force first attempt.
- Do not treat pilot runs, logs, or temp files as the final deliverable.

- Do validate any multiprocessing or background-execution plan on a tiny batch before using it for the full sweep.
- Do keep one validated serial or simple batched baseline and scale that exact workflow up.
- Do let a known-good long run finish once it is progressing.
- Do use file-based checkpoints or progress logs when shell process tools are missing or unreliable.
- Do use checkpoints, completion markers, or durable intermediate best rows so partial progress survives and can be merged.
- Do inspect the final CSV directly and use that artifact as the success criterion.
- Do not replace an already-progressing baseline with an unproven optimized rewrite.
- Do not launch overlapping background runs that compete to be the authoritative search.
- Do not rerun the same timed-out full sweep unchanged if batching or per-approximant execution is available.
- Do not leave results stranded in files like per-range CSVs without a completed merge to the required final path.
- Do not treat pilot runs, logs, temp files, timeouts, or partial outputs as the final deliverable.
- Do not treat partial coverage of the mass grid or only one approximant as a completed run.
