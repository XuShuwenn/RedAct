# Run Control and Completion

Use this when a search is already running, you are tempted to kill/restart it, or you are spending time monitoring instead of finishing.

## Keep-vs-restart rule

Prefer keeping the current run if all of these are true:
- it already passed a bounded end-to-end validation,
- it is showing real progress or writing durable checkpoints,
- no concrete exception or invalid-output evidence shows the run is wrong.

Restart only if at least one of these is true:
- the run has a reproducible exception,
- the output/checkpoints are invalid or inconsistent with the required search,
- progress has not advanced by the predefined checkpoint window,
- a replacement plan has already been validated on a tiny end-to-end case and clearly addresses the failure.

## After a concrete failure

- Do not relaunch the full sweep immediately.
- Reproduce the exact failure on one approximant and one or a few mass pairs.
- Fix that exact issue.
- Rerun the same bounded case until waveform generation, matched filtering, and output writing succeed.
- Only then resume the broader batched search.

This is especially important after domain/configuration errors such as `Ringdown frequency > Nyquist frequency` or after changing sampling, representation, or conditioning.

## Monitoring discipline

- Poll for deliverables, not just processes.
- Prefer checking batch checkpoints, logs with recent progress lines, and `/root/detection_results.csv` over repeated PID/CPU inspection.
- If monitoring does not reveal new artifacts or progress, change the execution plan; do not spend many turns only watching processes.

## Finish cleanly

Before concluding:
1. confirm every required approximant completed,
2. merge any partial outputs,
3. read back `/root/detection_results.csv`,
4. verify header and exactly three final rows,
5. then emit the environment's exact completion signal.

Do not stop at `job is still running` or `monitoring in progress` when the task requires a final artifact and explicit completion.