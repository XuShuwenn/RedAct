---
name: glm-lake-mendota
description: "Run General Lake Model (GLM) to simulate vertical water temperature with RMSE < 2 degrees Celsius against observations."
---

# General Lake Model (GLM) Simulation

## When to Use

- Simulate vertical water temperature in lakes
- Calibrate lake models against field observations
- Run GLM (General Lake Model) for water quality modeling

## Input Files

- `/root/bcs/`: Meteorological and hydrological forcing data
- `/root/field_temp_oxy.csv`: Field water temperature observations
- `/root/glm3.nml`: GLM configuration file

**Use these exact absolute paths consistently in every command and script. Do not switch to relative paths like `output/output.nc`, `glm3.nml`, or `field_temp_oxy.csv` when the task specifies `/root/...` locations.**

## Output

- Simulation output: `/root/output/output.nc`
- Target: RMSE < 2°C between simulation and observation
- Simulation period: 2009-01-01 to 2015-12-30

## Key Steps

1. Load forcing data from `/root/bcs/`
2. Load field observations from CSV
3. Configure GLM parameters in `glm3.nml`
4. Run simulation
5. Calculate RMSE against observations
6. Adjust parameters if RMSE > 2°C


7. Inspect `glm3.nml` and `output.nc` metadata before scoring so your RMSE method matches the real variable names, time units/origin, depth structure, and simulation period.
8. Start with a baseline run and baseline RMSE before changing parameters.
9. After diagnosis, make a small set of plausible targeted edits in `glm3.nml`, rerun GLM, and recompute RMSE; do not treat analysis alone as progress.
10. For each calibration trial, start from a known-good baseline `glm3.nml`, verify the intended parameter change took effect, and compare the new RMSE against the previous best.
11. Prefer one-parameter or small bounded trials before broad optimization, especially when the baseline RMSE is already close to 2°C.
12. After every run, verify the command exited successfully, `/root/output/output.nc` was regenerated and is readable, and the output covers 2009-01-01 to 2015-12-30 before using the RMSE.
13. Treat the task as complete only after a fresh final run with the saved best configuration and an explicitly recomputed RMSE < 2°C if claiming the target is met.


## Calibration Guardrails

## Calibration Guardrails

- Save a backup of `glm3.nml` before calibration and keep a known-good runnable copy until the final run is verified.
- Read the full relevant namelist sections before claiming dates, depths, output settings, or tunable parameters are correct; do not infer them from partial file views.
- If editing `glm3.nml` programmatically, first make one small change, run GLM once, and confirm the file still parses and produces `/root/output/output.nc`.
- Restore the baseline or known-good config before each trial so parameter changes do not accidentally accumulate across experiments.
- Only optimize parameters that you have confirmed actually exist in the namelist with valid editable syntax.
- Do not start broad multi-parameter optimization until your parameter-editing and evaluation workflow has been validated by at least one successful test run.
- If you compute RMSE with a custom script, derive timestamps and depth coordinates from `output.nc` when possible, or confirm them from `glm3.nml` before coding; avoid hard-coded assumptions.
- Calibration is only complete after a fresh final run with the chosen `glm3.nml` and a recomputed RMSE from the new output.
## Tips

- GLM outputs NetCDF format
- Use xarray or nczip to read output
- Calibration may require parameter tuning


- Record each tested parameter set and resulting RMSE so you can keep the best configuration.
- Before committing to a multi-run search, observe one full GLM run so you know the cost, expected outputs, and how progress appears.
- If a run or script shows no new output, no updated files, or no measurable progress, treat that as a debugging signal and switch to a simpler, more monitorable strategy.
- After any failed calibration attempt, restore or confirm a runnable `glm3.nml` before trying again.
- Never report success based on an intermediate, backgrounded, or unverified run; verify the final saved configuration by rerunning GLM and recalculating RMSE.


## Execution and Verification

## Execution and Verification

- Use the task environment's exact required tool/action syntax for executable steps.
- If you launch GLM, calibration, or evaluation in the background, treat that as incomplete work: wait for completion and inspect logs, outputs, and metrics.
- Check the real shell return code instead of assuming success from quiet, empty, or truncated output.
- If `/root/output/output.nc` is missing, stale, or unreadable, inspect `glm3.nml` output settings and treat the run as failed until fixed.
- Do not report an RMSE or claim the target is met unless the value is explicitly computed from completed output or clearly shown by your evaluation step.
- Before ending, verify whether the environment requires a specific completion signal and output that exact string only after all checks pass.