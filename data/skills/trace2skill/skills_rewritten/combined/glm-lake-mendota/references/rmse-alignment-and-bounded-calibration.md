# RMSE alignment and bounded calibration

Use this pattern when baseline GLM execution succeeds and you need a reliable scoring script or a light automation loop.

## Reliable RMSE comparison pattern

1. Run GLM once with the current `glm3.nml` and confirm `/root/output/output.nc` is fresh and readable.
2. Read variable names, time units/origin, and vertical coordinate information from `output.nc` metadata before coding the comparison.
3. Extract simulated temperature with its timestamps and convert the model's vertical structure to physical depth below surface using the real output fields.
4. Normalize simulation depths to the observation depth resolution when needed (for example by rounding or binning), then group duplicate simulation rows created by that normalization.
5. Merge simulation and observations on `datetime` and `depth`.
6. Compute RMSE only from matched pairs.

7. Print a quick alignment sanity check with matched-pair count, model/output date range, observation date range used, and a few merged rows before accepting the RMSE.

## Guardrails

- Do not assume layer index equals observation depth.
- Do not assume timestamps already match the observation timezone, origin, or calendar.
- Do not compute RMSE from unmatched arrays of equal length.
- If too few pairs match, debug alignment before tuning parameters.

## Bounded automation pattern

After one manual baseline score succeeds, it is safe to wrap the workflow into an objective function:

1. Start from a known-good baseline `glm3.nml`.
2. Edit one or a few confirmed parameters within plausible bounds.
3. Run GLM.
4. Rebuild the matched observation/simulation dataset.
5. Return RMSE.
6. Keep the best runnable configuration and verify it with a fresh final run.

Prefer bounded one-parameter or small multi-parameter searches when the baseline RMSE is already near the target.

7. If the loop updates the best configuration file, reread `glm3.nml` after the winning trial and then do one fresh rerun from that saved file to verify the recorded RMSE is reproducible with the persisted parameters.

## Preserve the winning configuration

When using a calibration script or light search loop:
- Log each trial as `params -> run status -> RMSE` so progress is auditable.
- Keep trial edits isolated from the known-good baseline until a run finishes and scores successfully.
- After a new best RMSE appears, write that parameter set back to `/root/glm3.nml` and rerun once from the saved file.
- Treat the rerun-from-saved-file RMSE as the authoritative best score; do not rely only on an intermediate trial result held in script memory.

## Near-target search pattern

When the baseline RMSE is only slightly above target, a small scripted search is often the best tradeoff between speed and control:

1. Choose only a few confirmed high-impact parameters already present in `/root/glm3.nml`.
2. Use narrow, physically plausible bounds.
3. Reuse the exact same RMSE alignment script for every trial.
4. Record each trial's parameter values, run status, and RMSE.
5. After selecting the best trial, persist those values in `/root/glm3.nml` and verify them with one fresh rerun and RMSE recomputation.

Do not treat the search output alone as final success; the saved configuration must reproduce the reported RMSE.

## Coarse-to-local search pattern

When one manual baseline score works and a few influential parameters are identified:

1. Try a small coarse grid or short list of plausible values.
2. Keep notes for each trial: parameter values, run status, RMSE.
3. Pick the best runnable coarse candidate.
4. Run a smaller local refinement around that candidate.
5. Save the best configuration back to `/root/glm3.nml` and verify it with a fresh final run.

Prefer this over a broad search across many unrelated parameters.