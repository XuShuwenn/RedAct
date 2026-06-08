---
name: excel-data-and-hp-filter-setup
description: "Use when a task requires an Excel-only macro model using external official data, HP filter smoothing via Solver, and strict no-code constraints."
---

# Excel-Only External Data Integration and HP-Filter Setup for Macro Models

A disciplined workflow for building macroeconomic supply/production models entirely in Excel, sourcing official data without external scripting, and performing HP-like smoothing with Solver. Designed to avoid common failures such as using unsupported tools, misaligned years/units, hardcoded numbers, and misconfigured Solver objectives.

## When to Use

Activate this skill when the user requires:
- An Excel-only workflow (no Python/Bash/automation) to collect and model macro data
- Data from multiple official sources (e.g., productivity databases, international outlooks, national/EU portals)
- In-workbook calculations only, with formulas preserved (no hardcoded calculated values)
- HP-filter-like smoothing implemented with Excel formulas and Solver

## Core Workflow

Phase 0 — Confirm Constraints and Tools
- Read the instructions and identify strict constraints: Excel-only; formulas retained; specified data sources; specific smoothing via Solver.
- If a specific automation tool (e.g., a browser automation MCP) is mandated, verify availability first. If it is not available, pause and ask whether manual data import (within Excel only) is acceptable.

Phase 1 — Plan Data Mapping and Metadata
- From the official data source metadata, map each required variable to its source series name/definition and unit. Record:
  - The exact indicator variable name and unit (e.g., real/constant prices, PPP vs national currency)
  - Coverage years
  - Country identifier/code conventions
- Create a small “Sources & Notes” section within the workbook listing URLs and variable names to support reproducibility.

Phase 2 — In-Excel Data Acquisition (No External Code)
- Use Excel’s native import options:
  - Data > Get Data > From Web (for direct CSV/JSON/HTML tables if accessible)
  - Data > Get Data > From Text/CSV (for downloaded CSV/TSV files)
  - Copy/paste tables from the official website into a raw sheet if necessary, preserving headers and years.
- Do not use external scripts, shells, or programming languages. Keep raw imported data separate from model sheets; create a clean “staging” area if needed.

Phase 3 — Normalize and Align Data in Excel
- In the model input sheets, use formulas (INDEX/MATCH, XLOOKUP, VLOOKUP) to pull year-by-year values from the staging/raw sheets into the target columns. Ensure:
  - Year rows align across all series (no shifted values)
  - Units are consistent (real vs nominal, currency base, index vs level)
- For projection requirements such as “carry forward the last growth rate,” reference the last available growth cell and fill forward with a formula (no manual typing of repeated numbers).

Phase 4 — Production Inputs and Logs
- Link capital and output series from their respective sheets into the production sheet via formulas only.
- Compute natural logs with formulas for the variables required by the production function (e.g., lnK, lnY) and the productivity residual per the workbook definition. Use absolute/relative references carefully to ensure fill-down integrity.

Phase 5 — HP-Filter-Like Smoothing via Solver (All in Excel)
- Create a column for the smoothed trend z_t (editable decision cells). Initialize z_t by linking it to the observed series to start sanity checks.
- Compute:
  - Fit residuals: (y_t − z_t)
  - Second differences of z_t: Δ²z_t = z_t − 2·z_{t−1} + z_{t−2}
- Define an objective cell as a weighted sum of squared terms, e.g.:
  objective = Σ (y_t − z_t)^2 + λ · Σ (Δ²z_t)^2
  where λ is a scalar weight in an assumption cell you can tune.
- Use Solver:
  - Set Objective: minimize the objective cell
  - By Changing Variable Cells: the z_t range
  - Add constraints if required (e.g., optionally anchor endpoints)
  - Solve and keep solution
- Post-solve checks: fit residuals should not be identically zero; second differences should be smaller than the initial state. Keep λ and the objective formula visible for auditability.

Phase 6 — Potential Output and Shock Scenarios
- Use the smoothed productivity trend and the production function to compute potential output. Keep all formulas dynamic.
- If required to extend capital using an anchor (e.g., average K/Y over a recent window), compute the anchor with an AVERAGE formula and use it to extend K via formulas, not hardcodes.
- Link any investment shock series from the designated sheet. Compute ΔK and the with-shock capital path via formulas. Recompute potential output with-shock using the same production function structure.

Phase 7 — Finalization
- Ensure all model outputs are formula-driven and traceable to source data.
- Save the workbook. Do not paste values over calculated cells.

## Verification

Use these checks before finalizing:
- Data provenance: Each input series has a cited source URL and variable name in a workbook notes section.
- Units and definitions: Confirm you used real/constant-price series where required; do not mix nominal and real.
- Year alignment: Pick a few random years and verify values match the official source. Check the first and last year across all linked series.
- No-code compliance: Confirm no external scripts were used to transform data; all calculations are in Excel formulas.
- No hardcoding: Sample cells in calculated areas should display formulas. Use Excel’s Show Formulas or Trace Precedents to audit.
- Growth carry-forward: Verify the terminal growth assumption references the last available estimate and that the forward years update automatically if the last growth changes.
- K extension anchor: Confirm the anchor (e.g., recent average K/Y) is computed via formula and used to extend K, not manually entered.
- Solver objective: After solving, confirm the objective decreased vs the initial state and that second differences are consistent with a smoother trend. The fit and smoothness terms should both contribute.
- Sensitivity: If λ is adjustable, verify reasonable results across nearby values and that the model remains stable.

## Common Pitfalls and How to Avoid Them

- Violating Excel-only constraints:
  - Do not use external code, shells, or ad-hoc scripts. Import data through Excel’s built-in tools or manual paste.
- Skipping metadata and mixing variables:
  - Always consult the official data dictionary to choose the correct series (real vs nominal, levels vs growth, PPP vs national currency). Mismatches will break the model.
- Misaligned years across sheets:
  - Use lookup formulas keyed on the year column. Do not rely on row positions alone.
- Hardcoded cells in calculation areas:
  - Replace typed numbers with references or formulas. Keep an audit column to detect any typed values.
- Incorrect Solver setup:
  - Ensure the objective includes both fit and smoothness terms. The changing cells must be the trend values. Anchor or bound cells only if methodologically justified.
- Assuming unavailable tools:
  - If a specific automation tool is required and not available, stop and ask for an allowed alternative (e.g., manual import through Excel). Do not silently switch to disallowed methods.
- Unit/scale mix-ups:
  - Confirm base years, price bases, and deflators. If sources use different bases, normalize in Excel before linking.

## Success Criteria

- All required series are present in the workbook, referenced from an imported/raw data area using formulas.
- All calculated cells (growth projection, logs, HP-filter trend, K-extension, potential output, with-shock path) are formulas with traceable precedents.
- Solver successfully minimizes the objective, producing a stable, smooth trend series.
- The model produces baseline and with-shock outputs that update automatically if inputs change.

## Optional Script Usage

No external scripts are recommended. Use only Excel’s native capabilities (Get Data, formulas, and Solver). If a mandated in-environment browser automation tool is available and explicitly permitted, use it only to acquire raw files for Excel import without transforming the data outside Excel.
