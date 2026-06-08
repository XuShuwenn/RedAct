---
name: reserves-at-risk-calc
description: "Calculate commodity price volatility and reserves-at-risk metrics from IMF commodity database and gold price data."
---

# Reserves-at-Risk Calculation

## When to Use

- Calculate commodity volatility metrics
- Analyze gold price exposure
- Compute Reserves-at-Risk (RaR) for countries

## Critical Constraints

- Start from the provided workbook/template if the task refers to existing sheets, named tabs, blanks, or exact rows/cells; preserve the workbook structure rather than creating a new workbook or redesigning the layout.
- Search allowed directories for the input workbook before creating anything new. If the required workbook or referenced source sheets are truly missing after verification, stop and report the blocker; do **not** invent a replacement template or fabricate country rows, reserve values, or source data.
- Inspect the workbook before editing and confirm the relevant sheets (`Gold price`, `Value`, `Volume`, `Total Reserves`, `Answer`), actual header rows, country labels, answer-area rows, and date layout.
- If the task requires Excel-only computation or specific worksheet functions, keep returns, volatilities, averages, lookups, filtering, and RaR in workbook formulas. Use Python/openpyxl only to inspect the file, place formulas/text, copy ranges, and save; do **not** compute final task logic externally and paste numeric outputs.
- Use only workbook data or explicitly authorized external data. Do **not** invent, estimate, backfill, or substitute missing country/reserve values unless the task explicitly authorizes it.
- Preserve source sheets and unrelated cells; do **not** blank, overwrite, or "fix" input cells just to suppress formula/recalc errors.
- If the task specifies an exact completion token or protocol, follow it verbatim.

## Multi-Step Process

### Before Step 1
- Treat the workbook as the source of truth for country lists, 2025 rows, headers, blank answer areas, and required row meanings.
- Verify workbook layout from existing labels/formulas before bulk-writing anything; derive formulas from workbook evidence and explicit task text, not guessed interpretations or assumed row/column positions.
- Do **not** assume `2025` is on a fixed row or column; inspect the relevant source sheets to verify the actual year row/column, header row, and data ranges.
- For country matching across sheets, use exact workbook labels or a verified one-to-one mapping derived from the workbook. Do **not** use prefix, substring, or fuzzy matching.
- Before bulk-filling formulas, write 1-2 representative cells, inspect the exact stored formula strings, and recalculate/check results.
- If external data access is blocked or repeatedly fails, stop retrying similar URLs and complete all workbook-dependent steps you can from local contents first.

### Step 1: Gold Price Analysis
- Download IMF commodity data
- Extract gold price (US$/troy ounce)
- Calculate: monthly log return, 3-month volatility, 12-month volatility
- Fill in "Gold price" sheet columns C-E
- Note: multiply log returns by 100 for percentage

- Use the IMF gold price series for **gold in US$ per troy ounce** (for example `PGOLD`), not broad commodity indices; validate the series header and unit before filling formulas.
- Write formulas in the worksheet for monthly log return and 3-month/12-month volatility; do not precompute these metrics outside Excel.
- Anchor formulas to the actual monthly series layout: the first valid log return should be on the first row with both current and prior month prices.
- Keep the horizon explicit: distinguish latest **3-month volatility** from latest **12-month volatility**. Do **not** annualize by habit; only annualize if the worksheet/task explicitly requires it.
- If log return is entered as `LN(price_t/price_t-1)*100`, volatility outputs are in percentage points. Use numeric formatting, **not** Excel percent formatting.
- Use valid cross-sheet formula syntax such as `='Gold price'!D430` or `=AVERAGE('Gold price'!B421:B429)`; do **not** write malformed references like `=\"Gold price\"!D430`.
- Verify the exact date rows from sheet labels before building formulas; before using any Jan-Sep 2025 average, confirm the source dataset actually contains months `2025M01` through `2025M09`.
- Spot-check representative cells after filling formulas: the first return cell, first valid 3-month volatility cell, first valid 12-month volatility cell, and the final populated row.

### Step 2: Country Gold Reserves
- Derive the country list from workbook evidence: include countries with 2025 gold reserves in `Value`, then add any additional 2025 countries found in `Volume`.
- Before adding any country from `Volume`, confirm the relevant row/cell actually contains 2025 data for that country.
- Fill the existing Step 2 area in `Answer` exactly where the template expects it; confirm each target row's label/definition before writing formulas and do not shift rows to fit your own layout.
- Build the list and pulled values with workbook formulas/links; do not hard-code, guess, or manually type a country subset from ad hoc inspection.
- Inspect `Value` and `Volume` to identify which cells contain country names, 2025 data, and numeric reserve values; ignore metadata/header noise and do not assume fixed positions from partial previews.
- Normalize country names conservatively before matching across sheets; use exact workbook names or explicit, verified normalization rather than fuzzy/substring matching.
- Use the Jan-Sep average as the 2025 gold price substitute via Excel formula(s) in the workbook.
- Sanity-check volume-to-value conversions with rough magnitude logic (for example, millions of ounces × thousands of dollars/ounce should usually yield billions of dollars, not millions).

### Step 3: Reserves-at-Risk Calculation
- Replicate Step 2 into the rows explicitly specified for Step 3 (typically rows 20-22 in `Answer`) **literally as requested**: countries, gold reserves value, and the template-requested volatility/input rows; do **not** move Step 3 elsewhere or substitute different metrics.
- Populate Step 3 from the same filtered country set used in Step 2; do not carry forward countries that should be excluded.
- For 2025 Total Reserves, write workbook lookup formulas by matching country and year labels (`INDEX`+`MATCH` or `XLOOKUP`, according to the task/template). If function support is uncertain, prefer compatibility-safe `INDEX`+`MATCH`.
- Build lookups from actual workbook headers and exact country names; for horizontal source tables, use `MATCH` as the column index of `INDEX` (or use `XLOOKUP`) rather than as a row index.
- Do **not** replace required lookups with hard-coded coordinates, guessed direct references, Python dictionaries, or manually pasted reserve values.
- If a lookup fails, debug the workbook ranges/keys/header matching first. Delete/exclude a country only after confirming there is truly no 2025 reserve data match under the workbook's exact naming.
- If volatility/returns are stored as percentages (`*100`) in cells, convert back to decimal in exposure/RaR formulas.
- Calculate RaR with Excel formulas in row 24 only after the required inputs/intermediate rows are populated, and fix any `#N/A`, `#VALUE!`, `#NAME?`, `#REF!`, or `#DIV/0!` errors in required output cells before finishing.
## Output

- Save the edited workbook directly to the exact path `/root/output/rar_result.xlsx`.
- Preserve the workbook template, required sheet names, and required formulas in the answer cells; do not substitute hard-coded computed values where formulas are required.
- Verify the saved file exists at that exact path and reopen it to confirm representative formula cells in `Answer` were written correctly.
- If recalculation is required for formulas to produce values, perform or confirm that recalculation before declaring success.
- After saving, follow any exact completion protocol from the task instructions.

## Verification Before Completion

- Recalculate the workbook in a spreadsheet engine when required, save it, then reopen the saved file and inspect representative `Answer` cells.
- Confirm Step 1, Step 2, and Step 3 required cells are populated in their original designated locations and contain intact formulas beginning with `=` where formulas are required.
- Inspect representative final formula text and evaluated values after any late correction; sanity-check that included/excluded countries are consistent across Step 2 and Step 3.
- Treat spreadsheet errors in required output cells as blocking unless verified to be outside the requested deliverable area.
- Do not report numeric conclusions unless the final saved workbook evaluates correctly in those cells.
- Read [references/validation-and-debugging.md](references/validation-and-debugging.md) when formula cells error or recalculation reports spreadsheet errors.
- If the task specifies an exact completion string (for example `ACTION: TASK_COMPLETE`), output that exact string verbatim and nothing else.

`/root/output/rar_result.xlsx`:
- Completed "Answer" sheet with all calculations
- Excel formulas, not hard-coded values

## Tips

- First inspect the workbook to confirm the named sheets, exact answer locations, headers, and workbook structure referenced by the task.
- Use native Excel formulas/workflows when the task requires workbook-based computation; use openpyxl only when instructions permit programmatic workbook editing.
- Use `INDEX`+`MATCH` or `XLOOKUP` for dynamic lookups by country/year headers, based on the task/template and verified function support.
- Prefer label-driven formulas tied to verified sheet headers/country names over hard-coded coordinates.
- Test one representative formula per pattern before filling ranges, then read back the stored formula text if results look wrong.
- After each formula family, sanity-check 2-3 populated cells: verify the formula, referenced ranges/sheets, displayed value, and unit/format.
- Handle missing data appropriately: prefer exclusion or task-approved logic over guessed replacements, and do not clear or overwrite unrelated workbook cells outside the required answer area unless the task explicitly asks for repairs.
