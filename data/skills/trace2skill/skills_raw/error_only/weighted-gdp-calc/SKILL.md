---
name: weighted-gdp-calc
description: "Calculate weighted mean of net exports as percentage of GDP for GCC countries using Excel formulas."
---

# Weighted GDP Calculation

## When to Use

- Calculate net exports as % of GDP
- Compute weighted means across countries
- Use Excel for data analysis

## Input

- `gdp.xlsx`: Workbook with "Task" and "Data" sheets


## Input

## Required Workflow

- Inspect the workbook before writing any formulas: confirm the exact `Task` destination blocks, the `Data` source block, the series-code column, the year header row, and the numeric value region.
- If workbook inspection output is truncated, ambiguous, or partial, inspect narrower targeted ranges until the needed coordinates are explicit.
- Before bulk-filling any block, validate one representative formula in the exact target area and confirm both the stored formula text and the returned value.
- If a test formula fails, debug that cell first; do not propagate an unverified pattern across a range.
- Save, recalculate, and spot-check representative cells again before declaring completion.

## Steps

### STEP 0: Verify Target Cells Before Writing
- Inspect the `Task` sheet layout and confirm the exact destination cells/ranges for each requested output before editing.
- Verify summary-statistic and weighted-mean cells from workbook labels/highlighting; do not infer them from spacing, nearby text, or prior row patterns.
- Treat any temporary probe formula, cleared cell, or single-cell test as debugging only, not final work.


### STEP 1: Data Lookup (H12:L17, H19:L24, H26:L31)
- Use VLOOKUP/MATCH, HLOOKUP/MATCH, INDEX/MATCH
- Match on series code (column D) and year (row 10)

- Treat the instructed year header row as authoritative: match years against row 10 exactly unless direct workbook evidence proves otherwise.
- Keep these as genuine lookup formulas keyed by series code and year; do not replace them with hard-coded direct cell references.
- Before filling a range, verify one representative lookup formula uses the intended series-code column, year-header row, valid Excel cross-sheet syntax like `Data!$B$21:$M$40`, and returns a plausible value.

- Blue highlighted cells

### STEP 2: Net Exports % GDP (H35:L40)
- Calculate for 6 GCC countries
- Then compute: min, max, median, mean, 25th/75th percentiles

- First verify what the imported Step 1 series represent (names, units, and scale) before choosing the net-exports formula.
- If the imported values are raw exports, imports, and GDP in compatible units, calculate net exports as percent of GDP as `=(exports-imports)/GDP*100`.
- First identify the actual output cells for min, max, median, mean, and 25th/75th percentiles; write formulas only into those confirmed cells.
- Prefer broadly compatible percentile formulas; if support is uncertain, use `PERCENTILE(range,k)` rather than newer variants like `PERCENTILE.INC`.


### STEP 3: Weighted Mean
- Confirm the exact weighted-mean destination cell from the worksheet layout before writing the formula.
- For GCC net exports as % of GDP, compute the combined share from underlying quantities: `(sum of (Exports-Imports)) / (sum of GDP) * 100`.
- Do NOT weight already computed `% of GDP` cells with `SUMPRODUCT(percent_range,gdp_range)/SUM(gdp_range)` unless the task explicitly asks for a GDP-weighted average of country ratios rather than the aggregate GCC share.
- `SUMPRODUCT` may still be useful for summing underlying net-exports components, but the denominator must be aggregate GDP, not a reweighting of derived percentage cells.


## Important Notes

- Don't modify file format, colors, fonts
- No macros or VBA
- Use Excel formulas only
- Work only in Task and Data sheets


- Verify Step 1 lookup outputs before computing Step 2 or Step 3; downstream formulas can recalculate cleanly even when the lookup logic is wrong.
- Recalculation success is necessary but not sufficient: inspect representative cells in each required block to confirm both the exact stored formulas and the evaluated results.
- Preserve requested spreadsheet logic; do not change formulas merely to suppress errors, and do not mask failed lookups with `IFERROR(...,"")` or similar shortcuts.
- Prefer broadly supported Excel functions; if a function produces `#NAME?`, replace it with a compatible equivalent and recheck the result.
- Work only in the existing workbook and sheets: keep edits in `gdp.xlsx`, confined to `Task` and `Data`, without changing file format, colors, fonts, or workbook structure.
- If formulas are written programmatically, protect Excel `$` references and quoting so the stored formula text is not corrupted before recalculation.
- If the task requires an exact completion string, output that exact string and nothing else after the workbook is fully verified.


## Tips

- openpyxl for Excel manipulation
- Use MATCH for row/column lookup
- SUMPRODUCT for weighted calculations
- XLOOKUP if available for better matching


- Validate sheet structure first, then scale: check a few anchor cells and one proof formula before copy-filling.
- For weighted means of ratios, confirm whether the correct logic is `SUMPRODUCT(ratio,weight)/SUM(weight)` or `(SUM numerator)/(SUM denominator)`; for net exports % GDP here, use the latter.
- If errors appear, inspect the exact stored formula text in a representative cell before changing function names, separators, or references.
- After save/reload, verify that source cells for downstream statistics are populated and in the intended units.



## Final Check

## Final Check

- Verify all required output regions are populated: lookup blocks in `H12:L17`, `H19:L24`, and `H26:L31`; net exports % GDP in `H35:L40`; summary statistics; and the weighted mean output.
- Confirm formulas are present in the confirmed target cells and results are numeric/plausible where expected.
- Re-inspect any region with truncated, partial, or suspicious output before concluding the workbook is correct.
- Ensure the final workbook is fully rebuilt if any cells were cleared or overwritten during debugging.
- Before ending, check whether the task requires an exact completion signal; if so, emit it verbatim.
