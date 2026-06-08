---
name: glm-run-calibrate-verify
description: "Run GLM for a lake, compute temperature RMSE versus observations, calibrate key parameters safely, and verify output period and configuration integrity."
---

GLM execution and calibration workflow for lake temperature simulations with reproducible verification. Use when you need to run GLM with provided forcing and configuration, compare simulated temperatures with field observations, reduce error via configuration tuning, and ensure the final output and configuration are consistent.

When to Use
- You have a GLM namelist configuration (glm3.nml), forcing/BCS files, and a field temperature observation CSV.
- You must generate a NetCDF output over a specified period and meet an error criterion such as RMSE below a threshold.
- You need a safe workflow to modify GLM parameters, run multiple experiments, and preserve a valid configuration file.

Core Workflow
1) Inspect inputs and environment
- Confirm required files exist: configuration (glm3.nml), observation CSV, and forcing/BCS files.
- Open the observation CSV; identify time, depth, and temperature columns (commonly: datetime, depth, temp). Note the observation period and depth range.
- Ensure the GLM executable is available on PATH and that the output directory exists.

2) Verify configuration and simulation period
- Open glm3.nml and confirm the simulation start/end are as required. Avoid broad changes at this step.
- Keep a backup of glm3.nml before making edits.

3) Run a baseline simulation
- Execute GLM from the working directory so it picks up glm3.nml and writes output to the configured location.
- After completion, confirm that the NetCDF output exists and is non-empty.
- Inspect the NetCDF time axis to verify coverage spans the required period (first and last timestamps). If the output time range is truncated, re-check the configuration and rerun.

4) Compute RMSE between simulation and observations
- Load the NetCDF output and extract the temperature field and its depth and time axes.
- Parse observation timestamps into a consistent timezone/format, filter observations to the model period, and drop rows with missing values.
- Align observations to the model using nearest neighbor matching in time and depth (with a reasonable tolerance). Do not assume exact timestamp matches.
- Compute RMSE across all matched pairs and record the count of matches used.

5) Targeted calibration loop (serial runs)
- Identify a small set of sensitive parameters to adjust (e.g., short/longwave scaling, wind scaling, light extinction, vertical mixing parameters). Choose plausible ranges and step sizes informed by prior knowledge or documentation.
- Update glm3.nml safely (prefer key-specific edits within the correct namelist group). Always keep a backup.
- Run GLM, recompute RMSE using the same method, and keep a record: parameter set → RMSE → match count.
- Iterate over a limited grid or local search near the most promising settings. Avoid launching concurrent GLM processes; run serially to prevent file contention.

6) Finalize and verify
- Write the best-performing settings into glm3.nml using the safe updater.
- Rerun GLM once more to generate a final NetCDF that matches the saved configuration.
- Recompute RMSE and confirm it meets the target. Verify:
  - Output exists and covers the full required period.
  - The number of matched observations is reasonable given the observation file and period.
  - The configuration file contains the final parameter values.

Verification
- Input validation:
  - All required files exist and are readable.
  - Observation CSV contains time, depth, and temperature columns; their units are consistent (depth in meters, temperature in degrees C).
- Model run success:
  - GLM exits without errors; output NetCDF file is present and non-empty.
  - The NetCDF time axis min/max align with the requested period (allowing small tolerances if the model uses midnight boundaries).
- RMSE computation integrity:
  - Matched count > 0; NaNs are excluded from the calculation.
  - Time and depth matching use nearest-neighbor with explicit tolerances; report how many observations were dropped due to exceeding tolerance.
- Calibration integrity:
  - Only intended parameters changed; formatting of glm3.nml remains valid.
  - No overlapping or concurrent GLM runs.
- Finalization:
  - Final glm3.nml reflects the used parameters.
  - Final output NetCDF corresponds to the same parameters and full required period.

Common Pitfalls
- Malforming glm3.nml by naive string replacement. Mitigation: use a key-targeted updater that edits only specific assignments within the correct namelist group and preserves comments/formatting; always back up.
- Not rerunning GLM after changing parameters. Mitigation: after selecting best parameters, rerun once more and recompute RMSE.
- Misaligned timestamps and depths. Mitigation: use nearest-neighbor matching with explicit time tolerance and depth nearest-index; ensure consistent datetime parsing.
- Partial or truncated simulation period. Mitigation: explicitly check NetCDF first/last time; if truncated, fix configuration or rerun.
- Launching concurrent calibration runs causing file contention. Mitigation: run serially and monitor active processes before starting another run.
- Counting unmatched or NaN pairs in RMSE. Mitigation: drop any pair where either value is NaN; report the effective sample size.

Optional Script Usage
- Compute RMSE between model output and observations:
  - python3 scripts/glm_rmse.py --nc path/to/output.nc --obs path/to/observations.csv
  - Optional arguments allow setting column/variable names, time window, and tolerances.
- Safely update glm3.nml parameters:
  - python3 scripts/update_nml.py --file glm3.nml --group <namelist_group> --set key1=value1 --set key2=value2
  - Creates a .bak backup and edits only the specified keys within the group.

Success Criteria
- NetCDF output generated for the required period.
- RMSE computed with clear reporting of matched pairs meets the requested threshold.
- Final glm3.nml contains the parameters used to produce the final output.
