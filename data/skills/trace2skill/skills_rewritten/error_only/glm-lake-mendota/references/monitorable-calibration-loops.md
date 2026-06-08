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

## Prefer this when baseline is already close

If baseline RMSE is already near target, prefer:
- one-parameter manual edits, or
- a tiny bounded sweep of plausible values

instead of launching an open-ended optimizer.

## Do not

- Do not launch background calibration with no visible per-trial progress.
- Do not wait repeatedly on an empty log without checking process state or switching strategy.
- Do not treat a stalled optimizer as the only path forward.