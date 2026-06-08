# Execution Stability and Refactor Checks

Use this when a run is slow, you are tempted to redesign the workflow midstream, or you want to add saved intermediate artifacts.

## Keep or change the current path

- Keep a run if it has already passed a bounded end-to-end validation and is now showing real forward progress.
- Change course only for a concrete reason: reproducible exception, invalid output, proven deadlock, or a runtime estimate that clearly exceeds the remaining budget.
- If you must change course, preserve resumability: checkpoints, per-batch outputs, or explicit completion markers.

## Before splitting into multiple scripts

1. Run the producer script on a tiny test case.
2. Inspect the actual intermediate file that was written.
3. Run the consumer script against that exact file.
4. Confirm the boundary works before launching the expensive search.

## Intermediate artifact safety checks

- Verify the exact save/load API and supported filename extension before relying on it.
- Smoke-test any new conditioned-data, PSD, or checkpoint persistence on a tiny object first.
- Do not assume a serialization method supports arbitrary extensions.

## Do / Do not

- Do let a known-good progressing run continue.
- Do prefer finishing one workable strategy over repeated redesign.
- Do validate refactors with a tiny cross-stage smoke test.
- Do not stop a run solely because it is slow if progress is visible and outputs remain plausible.
- Do not introduce new intermediate file formats in the critical path without a save/load test.
- Do not abandon a viable baseline for an unproven rewrite late in the task.
