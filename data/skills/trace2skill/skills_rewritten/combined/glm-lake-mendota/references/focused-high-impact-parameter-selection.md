# Focused high-impact parameter selection

Use this when the baseline run and RMSE calculation already work and you need the first calibration trial or a tiny bounded sweep.

## Proven starting pattern

1. Keep the baseline RMSE fixed with the same validated evaluator.
2. Confirm a short list of influential thermal parameters actually exists in `/root/glm3.nml`.
3. Start with one parameter edit or a very small sweep over a few plausible combinations.
4. Prefer parameters with direct physical effect on heat absorption or mixing, such as `Kw`, `wind_factor`, mixing coefficients, or modest `sw_factor`/`lw_factor` adjustments when present.
5. After any improvement, persist the winning values to `/root/glm3.nml`, inspect the saved file, rerun GLM, and recompute RMSE from the fresh output.

## Why this works

- A measurable baseline makes each trial comparable.
- Small focused trials often move RMSE enough without the fragility of broad optimization.
- Persist-and-rerun verification prevents claiming success from temporary or unrecorded parameter changes.

## Do not

- Do not start by changing many unrelated parameters at once.
- Do not rely on a calibration loop result unless the same saved `glm3.nml` reproduces the improved RMSE on a fresh run.
