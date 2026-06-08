# Run Monitoring Checklist

## When to read this
Read this right before launching the final expensive 4-case run, or when a production solve seems slow and you need to decide whether to wait, debug, or rerun.

## Preflight

- Confirm the final script uses the exact required parameters: `N=4`, `n_max=16`, four loss cases, and Wigner grid `1000 x 1000` over `[-6,6]`.
- Confirm local channels are represented by per-spin collapse operators in the full tensor-product spin space.
- Confirm output filenames are exactly `1.csv`, `2.csv`, `3.csv`, `4.csv`.
- Run a quick syntax/import check after saving the script.

## During the run

Track progress with both logs and filesystem state:
- inspect process liveness
- inspect per-case progress messages if available
- check whether `1.csv`-`4.csv` have appeared
- check that any created CSV is non-empty and growing/completed as expected

Do not infer failure from sparse stdout alone. Wigner evaluation can be long-running.

## When to stop vs when to wait

Wait if:
- the process is still alive
- logs show step transitions or case progress
- output files are being created or updated

Debug/restart only if:
- there is a traceback or explicit error
- the process has exited without producing required outputs
- dimensions/model construction are known to be wrong
- the run is clearly hung and not advancing by any observable signal

If you stop for debugging, rerun the full specification afterward.

## Completion gate

Declare completion only after verifying all of the following:
- `1.csv` exists and is non-empty
- `2.csv` exists and is non-empty
- `3.csv` exists and is non-empty
- `4.csv` exists and is non-empty
- outputs were generated from the final required configuration, not a reduced diagnostic run
