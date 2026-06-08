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

13. Time one complete micro-run or small batch, not just startup overhead, and calculate observed throughput plus projected full-grid time explicitly before choosing serial vs. parallel execution.
14. Define an early abort threshold before launching any long run: if progress after the first checkpoint is far below the required rate, stop and restructure rather than continuing to poll.
15. Ensure the pilot and full run expose progress at the template or small-batch level, not just startup banners.
16. If the estimate is not feasible for the remaining session budget, immediately switch to resumable batches or per-approximant execution with checkpoints.
17. Validate any redesigned execution mode by finishing one bounded batch all the way to a written checkpoint or merged test output before scaling.
18. Distinguish execution structure from computational workload: splitting, backgrounding, or parallel workers only help if measured throughput or effective completion time actually improves.
19. If progress stops advancing, switch from waiting to a resumable plan and continue from completed coverage rather than restarting the whole sweep.


20. For this task's required full coverage, reason about the true workload explicitly: `3 approximants x 31 x 31 = 2883` template evaluations. Use measured templates/minute or seconds/template from the pilot to project completion time before launching any full plan.
21. If repeated runs die or stall at the same expensive stage, require evidence of changed behavior before another relaunch: a faster bounded batch, a completed chunk, or a removed specific error. Otherwise pivot immediately.
22. Validate split or multi-script boundaries on a tiny case first: producer writes the artifact, inspect the actual file, consumer reads that exact artifact, and the tiny end-to-end handoff succeeds before launching expensive batches.
23. Verify any version-sensitive conditioning, resampling, or PSD call on a tiny object before embedding it in the search script; do not assume `TimeSeries` instance methods or remembered signatures exist.
24. Do not respond to an infeasible full-grid estimate by launching the same workload through multiprocessing or backgrounding. Preserve the validated search logic but reduce the execution unit to finished, mergeable chunks.

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

- Do express each execution step as a concrete runnable shell command or Python invocation, not as a natural-language description of intended work.
- Do inspect the actual saved script file after any write/edit operation before launching it.
- Do run a tiny foreground invocation of the exact saved script before any nohup/background launch.
- Do prefer runs that emit inspectable progress or intermediate artifacts over silent monolithic launches.
- Do treat repeated stalls or repeated timeouts at the same stage as a signal to pivot away from the current full-run strategy.
- Do treat a timeout as a debugging signal: use existing stage logs or add them, then rerun one approximant with a tiny mass subset to localize the bottleneck before changing the full workflow.
- Do capture logs for long or background jobs and use those logs as the first diagnostic source.
- Do use the first successful foreground batch as the production template for the remaining approximants or mass batches.
- Do not spend repeated turns polling empty background logs.
- Do not relaunch a modified search and then stop without checking whether it produced the required final CSV.
- Do not leave the workflow at 'jobs are running'; monitor through completion, collect outputs, and perform the final merge.

- Do inspect the exact traceback, last completed log line, or command exit evidence before changing code.
- Do capture logs for long or background jobs and inspect the real log or output file when terminal output is truncated.
- Do turn complex planned work into a real script file or explicit one-liner before execution; never send natural-language placeholders to the shell.
- Do use the first successful foreground chunk as the production template for remaining approximants or mass batches.
- Do not infer completion or stoppage from a partial log excerpt when the required CSV has not yet been read back.

