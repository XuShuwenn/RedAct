---
name: excel-only-macro-shock-discipline
description: "Use for building demand-side investment shock workbooks strictly in Excel with IMF WEO and SUT sources, ensuring correct series selection, year alignment, units, and formula integrity."
---

# Excel-Only Demand-Side Macro Shock Discipline

A fail-safe workflow to construct a demand-side investment shock analysis entirely in Excel, using only the specified authoritative sources (IMF WEO for macro data and the national statistics supply-and-use tables), while preventing common errors in series selection, year alignment, units, and formula preservation.

## When to Use

Activate this skill when you must:
- Populate a workbook from IMF WEO and national Supply & Use Tables (SUT)
- Extend projections using fixed assumptions (e.g., carry forward a given growth rate, average of recent deflator growth)
- Build scenario tables for investment shocks with specified multipliers and import shares
- Keep all calculations in Excel formulas only (no scripts, no manual hardcoded results in computed cells)

## Core Workflow

1) Enforce Tool and Source Discipline
- Only Excel for data handling and calculations. Do not use code, scripts, or external data-wrangling tools to write values into the workbook.
- Use only the specified authoritative sources:
  - Macro: IMF WEO (download the official country dataset)
  - SUT: Latest official national statistics SUT workbook
- Document units and series definitions on a "Notes/Sources" sheet (e.g., index vs. percent, local currency vs. USD).

2) Sheet Setup (names are illustrative; adjust to the template you’re given)
- WEO_Data: Place macro series by year in columns; keep years as explicit headers.
- SUPPLY and USE: Copy from the official SUT workbook, preserving exact sheet names and structure.
- SUT Calc: Map relevant values from SUPPLY/USE to Columns C–H (or as required by the template) to compute import content share.
- NA: Main analysis table with assumptions and scenario blocks.

3) IMF WEO Data Population and Extension (in WEO_Data)
- Place the official series with clear year columns. Never paste-over formulas in target areas.
- Growth carry-forward: If instructed to hold a specific year’s real GDP growth constant through a horizon:
  - Put that year’s growth in a dedicated anchor cell.
  - Reference it with an absolute reference (e.g., =$E$row) across out-years; do not duplicate values by hand.
- Deflator extension using recent-average growth:
  - If you have a deflator index: compute year-over-year (YoY) rates first: YoY_t = (Index_t / Index_{t-1}) - 1.
  - Compute the average of the last 4 YoY rates in a dedicated cell (AVERAGE over the last 4 YoY cells). Name this the deflator_anchor_rate.
  - Extend the index beyond last actual by compounding: Index_{t+1} = Index_t * (1 + deflator_anchor_rate). Fill right.
  - If you only have a YoY deflator rate series, first construct a consistent index with a chosen base year index (e.g., 100) before extending as above.
- Unit checks:
  - Keep series types distinct (index vs. growth vs. level). Do not mix YoY growth with level series in the same column.
  - Use clear labels and a helper row for units.

4) Supply & Use Tables (SUPPLY, USE, and SUT Calc)
- Copy SUPPLY and USE sheets from the official SUT workbook with original names unchanged. Do not alter their structure.
- In SUT Calc, link required rows/columns by formulas referencing SUPPLY/USE totals and import lines (use MATCH/INDEX or direct cell references if structure is fixed).
- Compute import content share as per your template’s definition (e.g., Imports / Total Use or the specified mapping). The final share should be formula-driven in the designated cell (e.g., C46).
- Add sanity checks: import share must be between 0 and 1; totals from SUPPLY and USE should reconcile.

5) Main Analysis and Scenarios (NA)
- Assumptions block: Place all constants (e.g., exchange rate, multiplier, import share, project total, duration) in dedicated cells; reference them using absolute references in formulas. Do not hardcode numbers inside calculation ranges.
- Allocation pattern: Create a bell-shaped weight vector across the project years. Normalize weights to sum to 1 (use SUM of weights and divide each weight by that SUM). Check the sum equals exactly 1.
- Investment schedule:
  - Total investment × weights → annual USD profile (or given funding currency).
  - Currency conversion: Convert via a single assumption cell for the rate. Keep a units helper row/column.
  - Deflator: When instructed to use GDP deflator as the investment deflator, ensure the same deflator index is applied consistently (e.g., convert nominal to real or vice versa using index/index_base).
- Domestic vs. import split: Apply import content share to split investment components. Use separate lines for domestic and import components.
- Demand multiplier: Apply the multiplier as instructed, typically to the domestic component. Keep this parameter in its own assumption cell for scenario control.
- Scenario replication:
  - Replicate the entire first scenario table below, referencing a separate set of assumption cells (multiplier/import share) for each scenario.
  - Confirm all scenario calculation blocks reference their own assumption cells, not the baseline’s.

6) Save and Name Output
- Save the final file with the required name (e.g., test_demand.xlsx) and ensure no external links remain.

## Verification

Perform these checks before finalizing:

A) Tool and Formula Integrity
- Excel-only: No scripts or external code used to populate calculated cells.
- Go To Special → Constants: In computed ranges, ensure there are no unintended constants; all derived cells should contain formulas.
- Trace Dependents/Precedents: Verify key rows (deflator extension, allocation weights, scenario outputs) have correct references.

B) Data Source and Series Validation
- Confirm every macro series comes from the official WEO dataset; do not substitute third-party sources.
- Verify series type and units:
  - Index vs. YoY growth vs. level are properly separated.
  - Deflator handling is consistent (index construction and compounding with the 4-year average YoY rate).

C) Year Alignment and Anchors
- Year headers match values; there is no one-column shift.
- The specified real GDP growth year is carried forward via absolute reference through the projection horizon.
- Deflator extended by compounding with the fixed anchor rate beyond the last actual.

D) SUT Integrity
- SUPPLY and USE sheets keep original names and structures.
- Mapped cells in SUT Calc return expected totals; import content share is between 0 and 1.
- Basic identity checks (e.g., supply equals use at relevant totals) hold.

E) Units and Magnitudes
- Currency conversions are applied once and consistently; no double conversion.
- Investment allocation weights sum to exactly 1.
- GDP impact and shares are in plausible ranges; if outputs seem implausibly high/low, check unit conversions and deflator application.

F) Scenario Independence
- Changing a scenario-specific assumption (multiplier or import share) only changes that scenario’s outputs.
- Scenario tables do not reference the baseline’s assumption cells.

Success Criteria:
- Required sheets present and named as instructed.
- WEO data correctly linked and extended by formulas (no manual pasting over computed cells).
- SUT sheets are copied with original names; SUT Calc computes import content share via formulas.
- NA sheet contains baseline and replicated scenarios with correct assumption overrides, allocation, conversion, deflator use, and computed impacts.
- Workbook passes all verification checks above.

## Common Pitfalls and How to Avoid Them

1) Using Non-Authorized Sources
- Pitfall: Pulling macro data from third-party aggregators when the instruction requires IMF WEO.
- Avoid: Use only the official WEO download; document series definitions and units in the workbook.

2) Violating Excel-Only Constraint
- Pitfall: Populating or transforming data via scripts or external tools.
- Avoid: Perform all operations within Excel. Keep formulas intact; do not paste values over formula ranges.

3) Wrong Series or Unit Mixing
- Pitfall: Using the wrong GDP-related series for the deflator or mixing index and growth.
- Avoid: Distinguish index vs. YoY rate vs. level; build the deflator index explicitly and extend it by compounding the 4-year average YoY rate.

4) Year Misalignment
- Pitfall: Off-by-one year shifts when placing series or extending projections.
- Avoid: Keep explicit year headers; cross-check that the carried-forward growth year matches the instruction and is absolute-referenced through the horizon.

5) Hardcoded Numbers in Calculations
- Pitfall: Typing constants into cells that should contain formulas.
- Avoid: Place all constants in an assumptions block and reference them; use Go To Special → Constants to detect and remove unintended constants in computed blocks.

6) Scenario Cross-Referencing Errors
- Pitfall: Scenario 2/3 formulas still pointing to Scenario 1 assumptions.
- Avoid: Create distinct assumption cells per scenario and verify with Trace Dependents.

7) Unit Mismatches and Implausible Outputs
- Pitfall: Mixing USD and local currency or applying the deflator inconsistently, leading to unrealistic GDP impacts.
- Avoid: Maintain a units helper row/column; apply currency conversion once; apply deflator consistently; sanity-check magnitudes.

## Notes on Implementation in Excel

- Use named ranges for key anchors (e.g., deflator_anchor_rate, multiplier_s1) to reduce reference errors.
- For the bell-shaped allocation, build an initial pattern (e.g., symmetric weights), then normalize by dividing each weight by the sum; verify the sum equals 1.
- Keep a small “QA Checks” section with boolean flags (TRUE/FALSE) for:
  - Weights sum to 1
  - Import share in [0,1]
  - Year alignment OK
  - No constants in computed ranges

This discipline prevents the observed failure modes: unauthorized sources, non-Excel manipulation, wrong deflator usage, year misalignment, unit mix-ups, and broken scenario references.
