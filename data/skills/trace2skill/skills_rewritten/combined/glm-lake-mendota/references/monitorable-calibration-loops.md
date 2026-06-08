# Monitorable calibration loops

Use this pattern when you are considering automation beyond one manual trial.

## Minimum requirements before automation

1. Prove one full manual cycle works: edit `glm3.nml` -> run GLM -> verify fresh `/root/output/output.nc` -> recompute RMSE.
2. Keep the exact RMSE script fixed.
3. Start from a known-good baseline config each trial.

## Safe loop pattern

- Bound the search explicitly: small parameter set, small trial count, or short runtime cap.
- Emit one log line per trial including parameter values, run status, and RMSE.
- After each trial, verify `/root/output/output.nc` was regenerated and readable before accepting the score.
- Stop early if logs remain empty, the process exits unexpectedly, output files stop changing, or scoring fails.

- Print or save the literal command/script path for each trial so the edit, run, and scoring steps are auditable.
- If baseline RMSE is already near target, cap the first sweep tightly before trying a broader optimizer.

## Prefer this when baseline is already close

If baseline RMSE is already near target, prefer:
- one-parameter manual edits, or
- a tiny bounded sweep of plausible values

instead of launching an open-ended optimizer.


## Proven small-sweep pattern

When the baseline RMSE is already close to target and the evaluator is working, a small scripted sweep is often the fastest reliable next step.

Example pattern:
- Choose one or two confirmed parameters with physical relevance to thermal structure (for example `Kw` and `wind_factor`).
- Try a small grid of plausible values.
- For each trial: restore the baseline config, apply edits, run GLM, recompute RMSE with the same script, and print one concise log line.
- Keep the best-scoring runnable trial, then write that exact parameter set back to `/root/glm3.nml` and verify it with a fresh rerun.

This preserves the successful workflow of getting a measurable baseline first, then using a bounded automated search rather than an open-ended optimizer.

## Do not

- Do not launch background calibration with no visible per-trial progress.
- Do not wait repeatedly on an empty log without checking process state or switching strategy.
- Do not treat a stalled optimizer as the only path forward.

- Do not keep repeating the same passive status check after a timeout; after one timeout or two empty checks, pivot to a smaller foreground trial.
- Do not describe a background optimizer as `running successfully` unless you have direct evidence such as per-trial logs, a live process check plus growing outputs, or completed scored trials.