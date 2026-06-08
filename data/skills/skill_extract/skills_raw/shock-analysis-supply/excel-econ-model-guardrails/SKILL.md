---
name: excel-econ-model-guardrails
description: "Build source-linked, Excel-only Cobb–Douglas shock models with HP filter, avoiding hardcoding, unit mismatches, and Solver misconfiguration."
---

# Excel Economic Modeling Guardrails (Cobb–Douglas + HP Filter)

A reusable workflow to construct an Excel-only potential output model with a Cobb–Douglas production function, HP-filtered productivity trend, and an investment shock. It focuses on preventing the failure modes observed in prior attempts: tool-constraint violations, hardcoded values, unit inconsistencies, broken links, and incorrect HP Solver setup.

## When to Use

Use this skill when you must:
- Build an Excel-only macroeconomic model (no external code for calculations).
- Ingest data from official sources (e.g., PWT, IMF WEO, ECB/national stats) and keep formulas in the workbook.
- Estimate potential output with Cobb–Douglas, HP-filter productivity trend, and capital shock scenarios.
- Extend projections from a terminal growth rate and maintain fully linked calculations.

## Core Workflow

Phase 0: Respect constraints and plan
- Do all calculations in Excel. External tools may be used only to download source files (CSV/XLS), not to compute results.
- Keep formulas in all computed cells; do not paste static numbers where a formula belongs.
- Document sources and variable definitions in-sheet.

Phase 1: Data acquisition and interpretation
- Penn World Table (PWT): Identify the appropriate capital stock and real output variables and their price base (e.g., national-accounts constant-price capital vs PPP). Read the metadata to confirm units/base-year and definitions.
- IMF WEO: Collect real GDP level and real GDP growth rates for the required years. Confirm the series are real (constant-price) and that units align with your model’s needs.
- CFC (Consumption of Fixed Capital): Acquire an annual series from the official provider (e.g., ECB/national stats). Capture units and currency.
- Record metadata (base years, currencies, definitions) in a README sheet.

Phase 2: Sheet structure and linking (in Excel)
- Use consistent sheet names and headers. Create Year columns to be the primary key for linking.
- Link values with XLOOKUP/INDEX-MATCH using Year. Avoid manual copy/paste.
- Keep units visible (headers or notes). If series are in different currencies/base years, do not combine them until you explicitly convert.

Phase 3: Depreciation rate calculation
- Compute annual depreciation rate as CFC / K only after ensuring K and CFC are expressed in a consistent currency/price concept. If not, add a conversion (e.g., deflator/exchange-rate) before taking the ratio.
- Compute the model’s depreciation assumption as an average over the most recent N years using AVERAGE over the depreciation rate series. Do not hardcode a fixed percent.

Phase 4: Cobb–Douglas and HP filter setup
- Compute LnK and LnY from linked K and Y.
- Define LnZ (TFP proxy) = LnY − α·LnK, where α is the capital share parameter set in a single input cell (referenced everywhere; no hardcoding in formulas).
- Initialize a column LnZ_HP as decision variables for HP smoothing (seed with LnZ via formulas).
- Create the second-difference column on LnZ_HP starting at the third observation in the block (row t: G[t] − 2·G[t−1] + G[t−2]).
- Objective cell: sum of squared deviations plus lambda times sum of squared second differences. Place lambda in a separate input cell referenced absolutely in the objective.
- Use Solver to minimize the objective by changing the LnZ_HP range (no constraints unless specifically needed, e.g., bounds for numerical stability).

Phase 5: K/Y anchor and projections
- Compute historical K/Y ratio from linked K and Y. Build an anchor (e.g., average of the most recent N years) with a formula, not a typed value.
- Use the anchor to extend K where required by the model specification (if the design calls for a fixed anchor approach). Keep the anchor dynamic (AVERAGE over a named range).
- Extend Y using the terminal-year real growth rate as instructed: Y[t+1] = Y[t]*(1 + g_terminal). Implement with absolute references on the growth-rate cell to fill forward.

Phase 6: Investment shock and potential output
- Place investment parameters (amount, start year, duration) in input cells. Build annual investment with IF/INDEX-XLOOKUP logic, not manual entries.
- Compute ΔK and K_with according to the model’s capital accumulation logic. Constrain all references to inputs and linked data—no numbers typed into calculated cells.
- Compute Y* (base and with-shock) using Cobb–Douglas with the HP-filtered trend and the appropriate capital stock in each scenario.

## Verification

Perform these checks before finalizing:
- Tool/Formula integrity
  - Spot-check that key cells (e.g., depreciation rate, HP trend, Y* results) display a formula (starts with “=”) in the formula bar.
  - Use Trace Precedents to confirm each key output depends on source-linked inputs.
- Data alignment
  - Year keys align across sheets; no #N/A in lookups. Latest K and Y years match the model’s specification (e.g., different end years across sources handled as intended).
  - WEO extension uses the terminal real growth rate with absolute references; verify the final year equals previous year × (1 + g_terminal).
- Units and base years
  - Confirm CFC and K are in consistent currency/price concepts before computing CFC/K. If conversion was needed, verify the conversion cell references are active.
  - Confirm real GDP series is indeed real. Do not mix nominal and real.
- HP filter correctness
  - Second-difference column is populated from the third row onward.
  - Objective cell equals Σ(LnZ − LnZ_HP)^2 + λ·Σ(Δ²LnZ_HP)^2 and λ is referenced from a dedicated cell.
  - After Solver, the objective value decreases and residuals (LnZ − LnZ_HP) look centered with a smooth HP trend.
- Anchors and averages
  - Depreciation and K/Y anchors are AVERAGE() formulas over explicit ranges of the most recent years (no constants).
  - Investment schedule references input cells (amount, start year, duration) and adjusts when they change.

Success criteria: No hardcoded constants in computed cells, no unit/base mismatches, all links working, Solver objective properly specified and minimized, projections extend as specified, and documentation of sources/definitions is present in-sheet.

## Common Pitfalls and How to Avoid Them

1) Violating Excel-only constraint
- Avoid generating the workbook or computing results with external scripts. Use Excel formulas and Solver only.

2) Hardcoding key values
- Do not type fixed percentages (e.g., depreciation, capital share, K/Y anchor). Put parameters in input cells and compute anchors via AVERAGE().

3) Unit and base-year mismatches
- Never compute CFC/K if CFC and K are in different currencies or price bases without conversion. Add deflator/FX steps so the ratio is dimensionless.

4) Misinterpreting real vs nominal series
- Ensure the WEO series is real (constant-price). Do not use nominal levels with real growth or vice versa.

5) Broken links and incorrect lookups
- Use XLOOKUP or robust INDEX/MATCH keyed on Year. Avoid single-cell INDEX references that don’t iterate over a range.

6) HP filter mis-specification
- Do not drop the smoothness term from the objective. Ensure second differences are correctly indexed and exclude the first two rows from the penalty by design.

7) Growth-rate extension errors
- Lock the terminal growth-rate cell with $ when filling forward. Review the last few projected years to confirm compounding is correct.

8) Timeline misalignment
- Models often have different last-available years by source. Make the linkage explicit and verify the model’s required endpoints for K and Y.

9) Sheet name inconsistencies
- Keep exact, stable sheet names. Formula references are case-insensitive but typos or renamed sheets break links.

## Optional Script Usage

You can use the included text template to copy-paste robust HP filter formula patterns into Excel and adapt ranges to your sheet. This does not compute for you; it standardizes formulas and reduces indexing mistakes.

- scripts/hp_filter_objective_template.txt: Contains generic Excel formula patterns for second differences and the HP objective combining fit and smoothness.

Keep all computations inside Excel and verify each formula after pasting by adjusting ranges to your actual row indices.
