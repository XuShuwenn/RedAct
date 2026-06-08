---
name: glm-calibration-workflow
description: "Run GLM, evaluate temperature RMSE against observations, and iteratively calibrate parameters with robust verification."
---

# GLM Run, Evaluation, and Calibration Workflow

This skill guides running the General Lake Model (GLM), extracting simulated vertical temperature from NetCDF output, aligning it with field observations, computing RMSE, and calibrating key parameters to meet a target error threshold. It emphasizes robust I/O handling, unit-safe time conversion, safe namelist editing, and verification to avoid common pitfalls.

## When to Use

Use this skill when you need to:
- Run GLM from a namelist (glm3.nml) and forcing files
- Compare simulated temperature profiles with field observations
- Calibrate GLM parameters to reduce RMSE to a target threshold
- Verify simulation coverage, reproducibility, and output integrity

## Core Workflow

1) Prepare and sanity-check
- Inspect glm3.nml for start/stop times, output settings, and parameter blocks.
- Confirm forcing and observation files exist and cover the requested period.
- Ensure an output directory exists (e.g., ./output) and GLM runs with working directory set to the project root (the directory containing glm3.nml and bcs/).

2) Baseline simulation
- Run GLM once to produce a baseline output NetCDF (e.g., output/output.nc).
- Verify the file exists and is readable as NetCDF.

3) Extract simulated temperatures
- Read the NetCDF output:
  - Parse the time variable using its units attribute (e.g., "hours since YYYY-MM-DD HH:MM:SS"). If missing, fall back to a known origin and units consistently used in your project.
  - Extract model heights (z) and temperatures (temp) for the water column at each time step.
  - Convert heights to depths relative to lake depth: depth = lake_depth − height.
  - Handle masked values and ignore invalid entries.
  - Round depths to integers to align with observation depth bins (or use a consistent binning strategy).
  - Aggregate to one temperature per (datetime, integer depth) if multiple layers map to the same rounded depth.

4) Align with observations and compute RMSE
- Load observations with columns like datetime, depth, temp.
- Convert observation datetime strings to timestamps and round depths to the same convention used for simulation (e.g., integer meters).
- Inner-join on (datetime, depth) to compute RMSE = sqrt(mean((sim − obs)^2)).
- Record counts of matched pairs as a diagnostic.

5) Calibration strategy
- Select a small set of physically meaningful parameters (examples: Kw, wind_factor, lw_factor, coef_mix_hyp, ch). Define plausible bounds (e.g., Kw: 0.1–0.5; wind_factor: 0.7–1.3; lw_factor: 0.7–1.3; coef_mix_hyp: 0.3–0.7; ch: 5e-4–2e-3). Clamp trial values inside bounds.
- Automate calibration by iterating:
  - Modify glm3.nml with new trial parameters using regex anchored on parameter names.
  - Run GLM synchronously (foreground) in the project root.
  - Recompute RMSE from output.
  - Track and retain the best parameter set.
- If global optimization is slow or buffers output, switch to a quick, targeted grid search near the baseline to find a parameter combination that meets the threshold.

6) Finalize and verify
- Write the best parameters back into glm3.nml.
- Run GLM once more and recompute RMSE to confirm the target is met.
- Verification checklist (see below). Keep glm3.nml with final parameters so re-runs produce the same output.

## Verification

- Output existence and integrity
  - output/output.nc exists, is a valid NetCDF, and has expected variables (e.g., time, z, temp).
- Time coverage
  - Read time units and compute the full datetime range. Ensure it covers the requested start and stop.
- Match diagnostics
  - Matched observation-simulation pairs > 0 and span expected depths and seasons.
- Reproducibility
  - A fresh GLM run with the saved glm3.nml completes successfully and reproduces RMSE within tolerance.
- Sanity checks
  - No extreme or non-physical parameter values. If in doubt, re-run near baseline.

## Common Pitfalls and How to Avoid Them

- No matched pairs (RMSE inflated):
  - Cause: Wrong time conversion (ignored units) or inconsistent depth binning.
  - Fix: Parse time units from NetCDF; use the same rounding/binning for sim and obs depths.

- Incorrect or partial simulation period:
  - Cause: Forcing files don’t cover the entire period or stop time misconfigured.
  - Fix: Confirm forcing coverage and glm3.nml start/stop; verify actual simulated time range from NetCDF.

- Brittle namelist edits:
  - Cause: Regex replaces the wrong token or formatting breaks the file.
  - Fix: Anchor regex to line starts and parameter names; only replace numeric values; back up the namelist before editing.

- Unbounded parameter search causing unrealistic values:
  - Cause: Optimizer explores outside physically plausible ranges.
  - Fix: Enforce bounds and clamp trial parameters before writing.

- Background/async runs with buffered output and hanging monitoring:
  - Cause: Long optimization with no visible progress.
  - Fix: Run synchronously with periodic prints, smaller iteration budgets, or switch to a simple grid search.

- Wrong working directory:
  - Cause: GLM run cannot find relative paths in glm3.nml.
  - Fix: Set cwd to the project root (where glm3.nml and bcs/ live) when invoking GLM.

## Success Criteria

- GLM runs successfully with final glm3.nml without manual intervention.
- NetCDF output covers the requested simulation window.
- RMSE between simulated and observed temperatures is below the target threshold.
- Final parameters are saved and documented.

## Optional Script Usage

This repository includes a helper script to standardize evaluation and namelist edits.

Example usage patterns (pseudocode):
- Compute RMSE
  - from scripts.glm_skill_tools import read_glm_output, read_observations, rmse_by_match
  - sim_df = read_glm_output("output/output.nc", lake_depth=25)
  - obs_df = read_observations("field_temp_oxy.csv")
  - rmse, n = rmse_by_match(sim_df, obs_df)

- Update parameters and run GLM
  - from scripts.glm_skill_tools import modify_nml, run_glm
  - modify_nml("glm3.nml", {"Kw": 0.34, "wind_factor": 1.05})
  - code, out = run_glm(cwd=".")

- Calibration loop
  - Iterate over a small grid or local search near baseline; clamp parameters; track best RMSE; write best parameters to glm3.nml; rerun and re-verify.
