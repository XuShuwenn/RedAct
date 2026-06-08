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

- Inspect the workbook before writing any formulas: confirm the exact `Task` destination blocks, summary-statistic cells, weighted-mean cell, the `Data` source block, the series-code column, the instructed year header row, and the numeric value region.
- If workbook inspection output is truncated, ambiguous, or partial, inspect narrower targeted ranges until the needed coordinates are explicit.
- Treat task-specified coordinates and instructions as binding unless direct workbook evidence clearly contradicts them; if anything appears inconsistent, inspect again and resolve it before writing formulas rather than guessing a nearby substitute.
- Build a complete coordinate map before editing, including exact `Task` output ranges, exact summary/weighted-mean cells, and the exact `Data` lookup bounds you will use.
- If the task states a specific source region, use that region exactly on the first pass; do not widen lookup tables to nearby rows/columns unless workbook inspection shows the stated bounds are wrong.
- Before bulk-filling any block, validate one representative formula in the exact target area and confirm both the stored formula text and the returned value.
- When formulas are generated through shell/Python/openpyxl layers, read back the exact stored formula text before scaling; verify `$` anchors, sheet references, quotes, separators, parentheses, and year/cell references survived intact.
- If many cells follow the same pattern, generate formulas programmatically only after the layout is confirmed, one anchor formula is validated, and one filled formula is rechecked after the bulk write.
- If a test formula fails, debug that cell first; do not propagate an unverified pattern across a range.
- Build in dependency order: complete and verify Step 1 lookup blocks first, then Step 2 net-exports calculations, then summary statistics and Step 3 weighted mean.
- If you clear, overwrite, or probe any required output cell during debugging, treat the workbook as incomplete until every required target range is rebuilt.
- After learning from single-cell experiments, consolidate the confirmed pattern into the full required ranges; do not treat isolated successful tests as task completion.
- Edit the provided workbook file in place (`gdp.xlsx`); do not create a substitute output workbook or perform the main workflow in a copied file unless explicitly allowed.
- Follow any task-runner or wrapper protocol exactly, including required tool/action format and any exact completion signal.
- Save, recalculate, and spot-check representative cells again before declaring completion.

## Steps

### STEP 0: Verify Target Cells Before Writing
- Inspect the `Task` sheet layout and confirm the exact destination cells/ranges for each requested output before editing.
- Verify summary-statistic and weighted-mean cells from workbook labels/highlighting; do not infer them from spacing, nearby text, or prior row patterns.
- Map every requested summary output (min, max, median, mean, 25th percentile, 75th percentile, weighted mean) to exact cell addresses before writing any of them.
- Do not write summary or weighted-mean formulas into guessed rows such as the first empty cells below the table; confirm the highlighted/output cells first.
- For summary statistics and weighted-mean outputs, inspect the full destination area (labels, highlight colors, and adjacent cells) until every target cell is explicitly confirmed.
- Treat any temporary probe formula, cleared cell, or single-cell test as debugging only, not final work.
- Create the target/source coordinate map in this step; if any destination or source coordinate is still inferred rather than directly observed, keep inspecting before proceeding.
- Do not write any production formulas until inspection has explicitly confirmed the relevant source rows, header row, and destination cells; if inspection output is truncated or ambiguous, narrow the read and inspect again first.
- If debugging changes any final-output cell, plan an explicit final rewrite pass for all required output blocks before validation.
- Inspect far enough down the `Task` sheet to see the complete Step 3 area before writing any weighted-mean formula; if the destination is not explicitly visible, inspect additional targeted ranges until the exact output cell is confirmed.


### STEP 1: Data Lookup (H12:L17, H19:L24, H26:L31)
- Use VLOOKUP/MATCH, HLOOKUP/MATCH, INDEX/MATCH
- Build Step 1 formulas from the stated data block first: keep lookup arrays within `Data!$B$21:$M$40` unless inspection proves another exact range is required.
- Match on the actual Task lookup field and the instructed year-header row: use row 10 on the first pass unless direct workbook evidence proves a different header row is required.
- If multiple candidate identifier columns exist in `Data`, test which one exactly matches the Task lookup value before filling formulas.

- Blue highlighted cells

- If row 10 initially appears blank or inconsistent, inspect the specific year-header cells and nearby formatting/merged structure before switching rows; do not default to row 9 or another nearby row from layout alone.
- If a year/header appears missing or mismatched, re-inspect the Task headers, Data year range, and lookup ranges first; do not switch to a nearby row just because it contains visible years.
- If Task year headers are formula-driven, unreadable, or otherwise unreliable to evaluate directly, explicitly map Task columns to Data columns from workbook inspection and use that confirmed positional mapping consistently across the block.
- Confirm the first and last requested year columns explicitly so the lookup array covers the full period with no one-column shift at either edge.
- If recalc shows clustered `#N/A` errors, use the pattern to debug: errors across all columns usually mean the key field or year-header row is wrong; errors only in the first or last year column often mean a misaligned year-header range or incomplete source-range coverage.
- Final Step 1 formulas must remain true lookups keyed by both series code and year; do not leave any target cell as a hard-coded direct `=Data!cell` reference even if the value is correct.
- After filling each lookup block, read back at least one stored formula from that block and confirm it still contains both lookup components, not a pasted value or direct source-cell pointer.

### STEP 2: Net Exports % GDP (H35:L40)
- Calculate for 6 GCC countries
- Then compute: min, max, median, mean, 25th/75th percentiles

- First verify what the imported Step 1 series represent (names, units, and scale) before choosing the net-exports formula.
- Read the indicator labels/codes for the Step 1 inputs and decide the formula from those definitions, not from the task title alone.
- If the imported series are already ratios or percent-of-GDP measures, do not divide by GDP again; use the combination implied by the definitions or re-inspect until the correct logic is clear.
- Only use `=(exports-imports)/GDP*100` after confirming the Step 1 inputs are raw exports, raw imports, and raw GDP in compatible units.
- If the imported values are raw exports, imports, and GDP in compatible units, calculate net exports as percent of GDP as `=(exports-imports)/GDP*100`.
- Because the requested output is percent of GDP, ensure the stored formula itself yields percent values: include `*100` unless the task explicitly relies on percentage cell formatting instead.
- Build Step 2 from the populated Task-sheet lookup blocks from Step 1, not by repeating raw-data lookups against `Data`.
- Before filling H35:L40, verify one sample cell shows both the intended formula pattern `(exports-imports)/GDP*100` and a plausibly percent-scaled result, not a raw ratio/decimal.
- First identify the actual output cells for min, max, median, mean, and 25th/75th percentiles from the visible worksheet labels/highlighting; write formulas only into those confirmed cells.
- Do not infer statistic rows from spacing or prior templates; if the target cells are not explicitly visible yet, inspect the surrounding `Task` range first.
- After identifying the statistic labels, map each statistic to its exact output cell(s) before entering any min/max/median/mean/percentile formula.
- Prefer broadly compatible percentile formulas; if support is uncertain, use `PERCENTILE(range,k)` rather than newer variants like `PERCENTILE.INC`.
- Before filling summary-statistic cells, test one representative percentile/stat formula in its actual destination area, recalculate, and confirm the engine accepts the function name and does not return `#NAME?`.
- After writing the first percentile or statistic formula, recalculate and confirm it evaluates numerically before filling the remaining statistic cells.
- After writing summary-statistic formulas, inspect each target statistic cell directly; if any formula text is truncated, incomplete, or malformed, fix it and recheck before proceeding.


### STEP 3: Weighted Mean
- Confirm the exact weighted-mean destination cell from the worksheet layout before writing the formula.
- Verify the weighted-mean cell from its label or explicit task-area text; do not assume its row from surrounding summary-statistic rows or formatting alone.
- Verify whether the weighted mean is a single output cell or a multi-year/output range before writing the formula; do not infer the span from nearby year columns alone.
- Derive the weighted-mean formula from the worksheet's labels/instructions and the underlying quantities already imported in Step 1; if the target cell or intended weighting basis is ambiguous, inspect the nearby Step 3 text/labels before writing anything.
- For GCC net exports as % of GDP, compute the combined share from underlying quantities: `(sum of (Exports-Imports)) / (sum of GDP) * 100`.
- Build the weighted mean from verified Task-sheet intermediate values or their underlying Task-sheet components, not from a fresh second pass of raw-data lookups.
- Do not build summary statistics or the weighted mean until Step 2 cells are confirmed to be in the correct unit (percent, not fraction); downstream formulas must preserve that same unit.
- Do NOT weight already computed `% of GDP` cells with `SUMPRODUCT(percent_range,gdp_range)/SUM(gdp_range)` unless the task explicitly asks for a GDP-weighted average of country ratios rather than the aggregate GCC share.
- `SUMPRODUCT` may still be useful for summing underlying net-exports components, but the denominator must be aggregate GDP, not a reweighting of derived percentage cells.
- When the task wording asks for a SUMPRODUCT-based weighted mean here, build it from the base ranges, e.g. numerator as `SUMPRODUCT(exports_range-imports_range)` or `SUMPRODUCT(exports_range)-SUMPRODUCT(imports_range)`, divided by `SUM(gdp_range)`, then `*100` if needed by the sheet's percent convention.
- Treat formulas like `=SUMPRODUCT(percent_range,gdp_range)/SUM(gdp_range)` as disallowed for this task unless the workbook explicitly asks for a GDP-weighted average of the already-computed country percentages.


## Important Notes

- Don't modify file format, colors, fonts
- No macros or VBA
- Use Excel formulas only
- Work only in Task and Data sheets


- Verify Step 1 lookup outputs before computing Step 2 or Step 3; downstream formulas can recalculate cleanly even when the lookup logic is wrong.
- When debugging a formula pattern, keep the test scope small enough that recalculation evidence is attributable to the formula under test.
- After recalculation, use the pattern of errors to diagnose structure problems: errors only in the first or last year column usually indicate a misaligned year-header range or incomplete source-range coverage rather than a bad series-code match.
- Recalculation success is necessary but not sufficient: inspect representative cells in each required block to confirm both the exact stored formulas and the evaluated results.
- Formula presence alone is never enough for completion. If recalculation/output inspection is incomplete, resolve that first or keep inspecting narrower ranges until you can confirm actual evaluated values in the workbook.
- When a formula errors, change one representative cell only, recalculate, and inspect that exact cell's stored formula and value/error before editing any neighboring cells.
- After a single-cell test succeeds, copy the same pattern to the rest of the confirmed range; do not switch formula families or separators across the whole workbook without a proven working example.
- When debugging blank or incorrect lookup results, change formulas only after confirming the actual failure mechanism from inspected cells/ranges; do not attribute the issue to unsupported explanations without evidence.
- Preserve requested spreadsheet logic; do not change formulas merely to suppress errors, and do not mask failed lookups with `IFERROR(...,"")` or similar shortcuts.
- Prefer broadly supported Excel functions. If a function produces `#NAME?`, replace it with a compatible equivalent and recheck both the stored formula text and the evaluated result (for example, use `PERCENTILE(range,k)` if a percentile variant is unsupported).
- Work only in the existing workbook and sheets: keep edits in `gdp.xlsx`, confined to `Task` and `Data`, without changing file format, colors, fonts, or workbook structure.
- Stay inside the workbook-only workflow: do not create or modify helper scripts, exported data files, or other auxiliary artifacts when the task says to work only within the existing workbook/sheets.
- If formulas are written programmatically, protect Excel `$` references and quoting so the stored formula text is not corrupted before recalculation.
- Avoid embedding Excel formulas with `$` inside shell double quotes unless escaped or passed through a safer path (for example, a single-quoted heredoc or direct Python script input); otherwise shell expansion can corrupt the stored formula.
- If the task requires an exact completion string, output that exact string and nothing else after the workbook is fully verified.
- Treat exact completion tokens and tool/message formatting as mandatory protocol: before ending, re-read the required final response and emit that exact string only, with no summary or extra commentary.

- Do not claim completion from partial rebuilds, isolated zero-error recalculations, or a few working sample cells; completion requires the full workbook outputs to be restored and checked in one final state.
- Treat formula-method requirements as hard constraints: if the task specifies lookup formulas or matching conditions, final cells must visibly implement that method, not an equivalent shortcut by direct references.


## Tips

- openpyxl for Excel manipulation
- If `pandas` is unavailable or unnecessary for workbook editing, continue with `openpyxl` to inspect sheets, write formulas, and preserve workbook structure.
- For repeated blocks, script formula generation from confirmed anchor rows/columns instead of hand-editing each cell; preserve absolute references carefully when filling patterns.
- Use MATCH for row/column lookup
- SUMPRODUCT for weighted calculations
- XLOOKUP if available for better matching, but prefer broadly supported lookup functions when compatibility is uncertain


- Validate sheet structure first, then scale: check a few anchor cells and one proof formula before copy-filling.
- For weighted means of ratios, confirm whether the correct logic is `SUMPRODUCT(ratio,weight)/SUM(weight)` or `(SUM numerator)/(SUM denominator)`; for net exports % GDP here, use the latter.
- If errors appear, inspect the exact stored formula text in a representative cell before changing function names, separators, or references.
- After save/reload, verify that source cells for downstream statistics are populated and in the intended units.

- If assembling formulas as strings, read back one stored formula verbatim before copying the pattern across the range; fix malformed sheet references or quoting before bulk fill.
- Compare Task and Data timelines explicitly before filling across years; if the source starts earlier or is offset, the final requested year may sit one column farther right than expected.



## Final Check

- Confirm each major write step persisted: reload or re-read representative cells from Step 1, Step 2, and Step 3 and verify formulas remain stored before concluding.
- Verify at least one representative cell from each required deliverable group: Step 1 lookup blocks, Step 2 country `% of GDP` cells, summary-statistic cells, and the Step 3 weighted-mean cell; for each, confirm both the stored formula text and the evaluated result are consistent with the requested logic.
- Reconfirm that lookup formulas still reference the intended bounded source region and did not drift outside the verified `Data` block during debugging or fill operations.
- Confirm summary-statistic cells and the weighted-mean cell match the worksheet's labeled destinations, not assumed positions chosen earlier during debugging.
- Treat truncated or partial inspection output as a failed verification, not as evidence of success; rerun narrower targeted checks until every required cell/range is fully visible.
- If any required region was cleared or partially rewritten during debugging, repopulate all required formulas first, then recalculate, then verify again.
- Confirm the edited file is still the original workbook path/name (`gdp.xlsx`), not a renamed or replacement copy.
- If formulas were generated by script, reload the saved workbook and spot-check that representative cells still contain the intended formulas and preserved formatting/layout.
- Run one final recalculation pass after all formulas are written; investigate any `#NAME?`, `#N/A`, `#REF!`, `#VALUE!`, or similar formula errors by reading the stored formula text in the flagged cells before concluding the workbook is complete.
- Before ending, check whether the task or system requires an exact completion signal or response protocol; if so, emit the exact required string/format verbatim and nothing else.

## Final Check

- Verify all required output regions are populated: lookup blocks in `H12:L17`, `H19:L24`, and `H26:L31`; net exports % GDP in `H35:L40`; summary statistics; and the weighted mean output.
- Confirm formulas are present in the confirmed target cells and results are numeric/plausible where expected.
- Re-inspect any region with truncated, partial, or suspicious output before concluding the workbook is correct.
- Ensure the final workbook is fully rebuilt if any cells were cleared or overwritten during debugging.
- Before ending, check whether the task requires an exact completion signal; if so, emit it verbatim.
