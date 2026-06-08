# RMSE alignment and bounded calibration

Use this pattern when baseline GLM execution succeeds and you need a reliable scoring script or a light automation loop.

## Reliable RMSE comparison pattern

1. Run GLM once with the current `glm3.nml` and confirm `/root/output/output.nc` is fresh and readable.
2. Read variable names, time units/origin, and vertical coordinate information from `output.nc` metadata before coding the comparison.
3. Extract simulated temperature with its timestamps and convert the model's vertical structure to physical depth below surface using the real output fields.
4. Normalize simulation depths to the observation depth resolution when needed (for example by rounding or binning), then group duplicate simulation rows created by that normalization.
5. Merge simulation and observations on `datetime` and `depth`.
6. Compute RMSE only from matched pairs.

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