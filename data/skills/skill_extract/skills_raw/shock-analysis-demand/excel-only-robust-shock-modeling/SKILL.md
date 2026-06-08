---
name: excel-only-robust-shock-modeling
description: "Build spreadsheet-only macro shock models by linking official data into Excel with resilient formulas, avoiding code, brittle references, and circular calculations."
---

# Excel-Only Robust Shock Modeling

A reusable workflow for constructing macro demand-shock spreadsheets entirely in Excel. It focuses on robust data linking from official sources, resilient formula design (no circular references), dynamic lookups (no hardcoded column letters), clean sheet naming, and validation checks. Use this when tasks explicitly require Excel-only modeling, linked data, and scenario testing without external code or hardcoded computed results.

## When to Use

Activate this skill when the user asks to:
- Populate and extend macroeconomic series in Excel from official sources (e.g., WEO, national statistics) without external computation tools
- Copy external tables (e.g., Supply and Use Tables) into a model and link calculations across sheets
- Build demand-side shock scenarios with assumptions cells and maintain formulas everywhere calculations are required
- Deliver one Excel file with preserved formulas and reproducible scenario toggles

## Core Workflow

Phase 0: Read Constraints and Lock Scope
- If the prompt states “Excel only,” do not write code to compute or fill results. Only paste raw source data and write Excel formulas to compute outputs.
- If exact sheet names or cell locations are specified, keep them exactly to avoid broken references.
- If specific assumption cells are mandated (e.g., a fixed exchange rate cell, a multiplier cell), create them as inputs and reference them with formulas elsewhere.

Phase 1: Workbook Scaffolding
- Create/verify required sheets with exact names the task specifies (examples: "WEO_Data", "SUPPLY", "USE", "SUT Calc", "NA").
- Reserve an Inputs/Assumptions block (as instructed) and clearly label cells for:
  - total project size
  - exchange rate (if specified by task)
  - multiplier(s)
  - import content share (linked from SUT Calc, not typed)
  - any scenario toggles or distribution vectors (e.g., bell-shaped allocation)
- Use consistent units and headers (e.g., year rows vs. year columns) and be explicit about currency units (local vs. USD) and magnitudes (million vs. billion).

Phase 2: WEO_Data Sheet Setup (Excel-Only)
- Paste raw official data (historical and latest projections) from the source into dedicated input columns. Do not compute in external tools.
- Compute extensions entirely in Excel:
  - Fixed real growth rate extension: place the anchor rate in a single cell; for forward years, reference that locked cell with absolute references to avoid accidental range growth.
  - GDP deflator extension using an average of recent years:
    1) Compute the 4-year average in a separate anchor cell that references only historical cells (no future cells). Example anchor cell formula (conceptual): =AVERAGE(deflator_growth_recent_4_cells). Lock this cell with $.
    2) For each future year’s deflator index: Index_t = Index_{t-1} * (1 + $AverageDeflatorGrowth$). Use absolute references to the anchor average to avoid circular references.
- Compute nominal GDP (local) via chain-linking real and deflator series with formulas. If needed, compute USD values using the exchange rate from the assumptions section (do not hardcode exchange rates inside formulas; link the assumption cell).
- Avoid circular references by:
  - Separating constants/anchors (e.g., “Avg deflator growth of last N years”) into single cells outside series
  - Extending series by referencing only prior-year cells and fixed anchors

Phase 3: SUPPLY & USE Sheets (Preserve Structure)
- Copy the official Supply and Use Table sheets into the workbook without changing sheet names. Do not edit labels or rearrange columns/rows; preserve the original format.
- Do not assume column letters or row numbers for key fields (e.g., “Imports”, “Total resources”, “GFCF”). Column positions vary across releases.

Phase 4: SUT Calc Sheet (Dynamic Lookups, No Hardcoded Columns)
- Use header-based lookup to retrieve values from SUPPLY/USE—never assume fixed column letters. Robust approach:
  - Use MATCH to find the column index of key headers on the SUPPLY and USE sheets (e.g., MATCH("Imports", SUPPLY!$2:$2, 0)).
  - Use INDEX with row and the MATCH-found column to pull each product’s value. Example pattern:
    - =INDEX(SUPPLY!$A:$Z, row_num, MATCH("Imports", SUPPLY!$2:$2, 0))
  - For product rows, refer to the original product rows by linking code/name columns rather than hardcoding row numbers. Where feasible, create named ranges for the product block and header row.
- Compute per-product import shares using only formulas (e.g., Imports / Total Supply) with zero-division safeguards: =IF(TotalSupply=0,0,Imports/TotalSupply).
- Compute investment-related aggregates (e.g., imported GFCF = import share × GFCF) and total them. If the task mandates a specific output cell for the import content share, compute that ratio exactly in the required cell and reference it from the NA sheet.

Phase 5: NA Sheet (Scenario Engine)
- Link baseline macro values from WEO_Data—do not type values. Use direct sheet references.
- Place all assumptions in the designated cells (per instructions) and reference them everywhere else:
  - Exchange rate: used to convert USD inputs to local currency
  - Demand multiplier(s): scenario parameter(s)
  - Import content share: link to the computed cell in SUT Calc, not typed
  - Allocation profile (e.g., bell-shaped): store percentages in cells; ensure they sum to 100% with a check cell
- Use GDP deflator as the investment deflator if instructed. Convert nominal investment to constant/base-year terms via ratios of deflator indices (all in formulas).
- Compute demand impacts stepwise with formulas only:
  - Nominal USD investment → local currency (via exchange rate) → real investment (via deflator) → direct demand → import leakage (via import content share) → net domestic impact → multiplier effect → % of GDP impact (divide by baseline GDP measure for that year).
- For multiple scenarios, replicate the table structure and change only the specified assumptions (by referencing different assumption cells or overriding scenario-specific assumption cells). Keep all other formulas identical.

## Verification
- Sheet names and exact locations:
  - Do sheet names match the required names exactly? Renaming breaks formulas.
  - If specific cells are mandated for inputs/outputs (e.g., designated assumption cells or a cell for import content share), verify they are used and referenced exactly.
- Formula integrity:
  - The extended series for growth/deflator should reference prior-year cells and fixed anchor cells only. No AVERAGE range should include the cell that stores the average (no self-inclusion).
  - Check absolute references ($) on anchors (e.g., the fixed growth rate and average deflator growth).
  - Confirm no #VALUE!/REF!/DIV0! errors appear; resolve by adjusting ranges and safe IF wrappers for divisions.
- Data-linking resilience:
  - Test lookups by changing the header text (in a copy of the file) to confirm MATCH/INDEX correctly pull values based on headers rather than hardcoded letters.
  - Confirm the SUT Calc total imported GFCF equals the sum of per-product imports of GFCF and that the import content share responds when product-level values change.
- Scenario sanity checks:
  - Allocation vector sums to 100% with a separate check cell (=ABS(SUM(allocation)-1) should be 0)
  - Units: verify USD→local conversions, and billion vs million consistency across sheets
  - Confirm that changing a scenario assumption (e.g., multiplier) updates all scenario rows without manual edits
- Provenance:
  - Record sources in an Info or Notes section (e.g., WEO release name, national statistics link). If network access failed and user-provided files were used, note that explicitly.

## Common Pitfalls and How to Avoid Them
- Using code or external tools to compute values when Excel-only is required:
  - Only paste raw source data; compute everything else via formulas.
- Hardcoding computed numbers (e.g., growth rates, deflator projections) into cells meant for calculations:
  - Store constants/assumptions in the Inputs block; everything else should be formulas.
- Brittle references to SUT columns by letter or position:
  - Always use MATCH on the header row combined with INDEX; never assume fixed column letters.
- Circular references in series extensions:
  - Place average anchors in separate cells referencing only historical periods; use absolute references to those anchors in the projection cells.
- Wrong units or mixing USD/local currency and mn/bn:
  - Centralize units as headers and use helper cells to convert. Add a unit-check line if necessary.
- Breaking required sheet/cell contracts:
  - If the task mandates specific sheet names or cell addresses for outputs/assumptions, adhere exactly or the grading links will break.

## Optional Script Usage (Out-of-Band Validation Only)
If allowed by the overall task environment, you may optionally run the provided helper to audit formula coverage. Do not use scripts to compute model values or edit Excel content—this is for validation only when permissible.

- Purpose: reports counts of formulas vs constants per sheet and can highlight sheets with suspiciously few formulas.
- Usage: python scripts/xlsx_formula_audit.py --file /path/to/workbook.xlsx
- Outcome: Use the report to manually replace any unintended hardcoded numbers with formulas in the workbook.

Deliverable
- A single Excel file containing:
  - Raw data pasted from official sources
  - Robust formulas everywhere calculations are needed
  - Required sheet names intact
  - Scenario tables with assumptions-driven variability
  - Clear notes documenting sources and assumptions
