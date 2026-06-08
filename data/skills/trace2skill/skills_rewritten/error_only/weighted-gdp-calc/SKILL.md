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
- Hard stop: if inspection is truncated mid-range, mid-cell, or mid-label, do not write production formulas yet. Continue targeted inspection until the exact destination cells and relevant source/header coordinates are explicitly visible.
- Apply the same rule to formula inspection and write verification: if a printed formula, target range, or recalculation report is truncated, treat it as unusable evidence and rerun narrower reads until the full stored formula text and affected cells are visible.
- Treat task-specified coordinates and instructions as binding unless direct workbook evidence clearly contradicts them; if anything appears inconsistent, inspect again and resolve it before writing formulas rather than guessing a nearby substitute.
- Build a complete coordinate map before editing, including exact `Task` output ranges, exact summary/weighted-mean cells, and the exact `Data` lookup bounds you will use.
- If the task states a specific source region, use that region exactly on the first pass; do not widen lookup tables to nearby rows/columns unless workbook inspection shows the stated bounds are wrong.
- Before bulk-filling any block, validate one representative formula in the exact target area and confirm both the stored formula text and the returned value.
- When formulas are generated through shell/Python/openpyxl layers, read back the exact stored formula text before scaling; verify `$` anchors, sheet references, quotes, separators, parentheses, and year/cell references survived intact.
- If many cells follow the same pattern, generate formulas programmatically only after the layout is confirmed, one anchor formula is validated, and one filled formula is rechecked after the bulk write.
- If a test formula fails, debug that cell first; do not propagate an unverified pattern across a range.
- If experiments create multiple workbook errors or leave uncertain intermediate edits, first restore the edited target area to a clean baseline, recalculate, and confirm the workbook is back to a known-good state before testing the next formula variant.
- If recalculation reports many errors from previously written cells, do not treat the workbook-wide error count as evidence about the new test formula. First isolate the test by clearing/rebuilding the unrelated failing target region or by restricting evaluation to a small clean target area in the workbook.
- Do not switch among multiple formula families (`INDEX/MATCH`, `VLOOKUP`, `HLOOKUP`, `XLOOKUP`, direct references) speculatively. Keep one candidate formula in one representative cell, inspect its stored text and result, identify the specific failure mechanism, then change one variable at a time.
- Verify environment assumptions before depending on them: check whether needed Python packages are already available and prefer the built-in workbook workflow (`openpyxl`) rather than attempting package installation unless the task explicitly allows it.
- Verify helper-script locations before invoking them; do not guess paths such as `/root/recalc.py`. Inspect the workspace/tool directories first, then call the confirmed path.
- Build in dependency order: complete and verify Step 1 lookup blocks first, then Step 2 net-exports calculations, then summary statistics and Step 3 weighted mean.
- If you clear, overwrite, or probe any required output cell during debugging, treat the workbook as incomplete until every required target range is rebuilt.
- After learning from single-cell experiments, consolidate the confirmed pattern into the full required ranges; do not treat isolated successful tests as task completion.
- Edit the provided workbook file in place (`gdp.xlsx`); do not create a substitute output workbook or perform the main workflow in a copied file unless explicitly allowed.
- Follow any task-runner or wrapper protocol exactly, including required tool/action format and any exact completion signal.
- Save, recalculate, and spot-check representative cells again before declaring completion.
- Do not declare any step complete from intention, prior pattern, script output, or partial tool output alone; completion requires direct read-back evidence from that step's actual target cells after writing.
- During verification, check requirement compliance as well as numeric correctness: confirm formulas are in the required ranges, use the requested method, and match any stated lookup/matching conditions before declaring success.
- Do not describe the solution as using a requested method unless the stored formulas visibly implement that method. Compare one or more representative final formulas against the task wording before completion.
- Treat failed, timed-out, or ambiguous save/recalc operations as unresolved blockers. Do not declare completion until the workbook is saved successfully and verification on the saved file is successful, unless the task explicitly permits unevaluated formulas.
- If verification signals conflict, resolve the contradiction with targeted checks on the saved workbook before proceeding.


## Required Workflow

## Execution Protocol (Hard Constraint)

- Follow the task runner's required message/tool format exactly on every step. If the system specifies a `Thought` line and an `Action:` JSON object, use that exact schema for every tool call; do not substitute XML tags, markdown code fences, pseudo-tool syntax, or any other format.
- Treat action-format requirements as execution constraints, not style preferences. Before the first tool call, restate the required schema to yourself and keep using it unchanged until the task ends.
- Every tool invocation must be a concrete executable command or valid structured action payload; do not send placeholder text such as `inspect workbook structure` when the environment expects the exact command or JSON action that performs it.
- Treat near-miss protocol variants as failures: wrong casing, added commentary, alternate prefixes, or paraphrased completion text are not acceptable if the environment specifies an exact token.
- If you use a todo/progress tracker, keep it consistent with the real workbook state. Update it incrementally; do not replace a multi-step plan with a stale partial item list near the end.
- Before claiming completion, verify that any visible progress tracker reflects all required steps as finished or otherwise accurately closed out.
- If the task requires an exact completion token (for example, `ACTION: TASK_COMPLETE`), the final response must be that exact string and nothing else.
- Never end with a prose summary, explanation, or extra sentence when an exact completion token is required.
## Steps

### STEP 0: Verify Target Cells Before Writing
- Inspect the `Task` sheet layout and confirm the exact destination cells/ranges for each requested output before editing.
- Do not issue any workbook-write command until inspection has explicitly shown the relevant Task instructions, destination cells, source block, and year/header layout.
- If any inspection is truncated, cut off, or too wide to show the needed coordinates, pause implementation and rerun narrower targeted inspections until the coordinates are explicit.
- Verify summary-statistic and weighted-mean cells from workbook labels/highlighting; do not infer them from spacing, nearby text, or prior row patterns.
- Map every requested summary output (min, max, median, mean, 25th percentile, 75th percentile, weighted mean) to exact cell addresses before writing any of them.
- Do not write summary or weighted-mean formulas into guessed rows such as the first empty cells below the table; confirm the highlighted/output cells first.
- For summary statistics and weighted-mean outputs, inspect the full destination area (labels, highlight colors, and adjacent cells) until every target cell is explicitly confirmed.
- Treat any temporary probe formula, cleared cell, or single-cell test as debugging only, not final work.
- Create the target/source coordinate map in this step; if any destination or source coordinate is still inferred rather than directly observed, keep inspecting before proceeding.
- Do not write any production formulas until inspection has explicitly confirmed the relevant source rows, header row, and destination cells; if inspection output is truncated or ambiguous, narrow the read and inspect again first.
- Inspect the `Data` sheet structure early enough to decide the formula strategy: confirm where series identifiers live, where year headers live, and whether the requested Task outputs should be driven by bounded lookups or by confirmed direct references.
- Before any bulk fill, inspect the exact driver cells the formulas will reference first (for example country key cells, series-code cells, year-header cells, and anchor labels) and confirm they are populated with the expected type/value.
- If a required driver cell is blank, `nan`, mismatched, or ambiguous, stop and remap the references before writing formulas to the block.
- If debugging changes any final-output cell, plan an explicit final rewrite pass for all required output blocks before validation.
- Inspect far enough down the `Task` sheet to see the complete Step 3 area before writing any weighted-mean formula; if the destination is not explicitly visible, inspect additional targeted ranges until the exact output cell is confirmed.


### STEP 1: Data Lookup (H12:L17, H19:L24, H26:L31)
- Use VLOOKUP/MATCH, HLOOKUP/MATCH, INDEX/MATCH
- First perform a syntax-acceptance smoke test with one real lookup formula in a representative target cell and recalculate it. If the engine returns `#NAME?` or another syntax-related error, fix the formula style before filling any lookup block.
- Read back that test cell's stored formula text exactly as saved to confirm sheet references and lookup syntax survived the write path unchanged.
- Build Step 1 formulas from the stated data block first: keep lookup arrays within `Data!$B$21:$M$40` unless inspection proves another exact range is required.
- Match on the actual Task lookup field and the instructed year-header row: use row 10 on the first pass unless direct workbook evidence proves a different header row is required.
- If multiple candidate identifier columns exist in `Data`, test which one exactly matches the Task lookup value before filling formulas.
- Validate one full lookup dependency chain before filling: the Task lookup key cell, the Task year/header cell, the matched identifier column in `Data`, and the matched year header in `Data` must all resolve cleanly for the sample formula.
- Before filling a lookup block, verify on one representative target cell that the chosen access method matches the real `Data` layout; if the source is arranged differently than expected, stop and remap before writing the rest.
- Do not fill Step 1 from a pattern whose anchor depends on a blank or non-year header cell; re-inspect the exact Task header coordinates first.

- Blue highlighted cells

- If row 10 initially appears blank or inconsistent, inspect the specific year-header cells and nearby formatting/merged structure before switching rows; do not default to row 9 or another nearby row from layout alone.
- If a year/header appears missing or mismatched, re-inspect the Task headers, Data year range, and lookup ranges first; do not switch to a nearby row just because it contains visible years.
- If Task year headers are formula-driven, unreadable, or otherwise unreliable to evaluate directly, explicitly map Task columns to Data columns from workbook inspection and use that confirmed positional mapping consistently across the block.
- Confirm the first and last requested year columns explicitly so the lookup array covers the full period with no one-column shift at either edge.
- If recalc shows clustered `#N/A` errors, use the pattern to debug: errors across all columns usually mean the key field or year-header row is wrong; errors only in the first or last year column often mean a misaligned year-header range or incomplete source-range coverage.
- Final Step 1 formulas must remain true lookups keyed by both series code and year; do not leave any target cell as a hard-coded direct `=Data!cell` reference even if the value is correct.
- After filling each lookup block, read back at least one stored formula from that block and confirm it still contains both lookup components, not a pasted value or direct source-cell pointer.
- Do a minimal lookup proof before bulk fill: for one representative Task row, inspect the Task key cell, inspect the candidate key column in `Data`, confirm the exact matching source row exists, and verify the return year column before copying the formula pattern.
- Do not assume `Data!B:B` is the correct lookup key just because it contains codes; inspect the Task key values and confirm which `Data` column matches them exactly. If any candidate source column contains blanks/`None` or mixed identifier types, resolve the mapping first rather than filling the whole block.
- If the first proof lookup does not return a directly observed expected value, do not propagate the formula; re-inspect the key field, source bounds, and year-column mapping first.
- Immediately after writing Step 1 formulas, inspect representative cells from each lookup block for both stored formula text and returned values; if outputs are blank/`None`/errors, stop and fix Step 1 before writing any Step 2, summary-statistic, or Step 3 formulas.
- Treat any malformed sheet-qualified reference (for example, incorrect `Data!` syntax/casing/quoting or a broken source range) as a blocker for the rest of the workbook; correct one representative lookup formula, recalculate, and confirm it returns data before bulk rewrite.

- For `INDEX`/`MATCH`, align all lookup components to the same table geometry: the `INDEX` return array, the row-match key column, and the column-header range must describe the same data block with the same column origin.
- Do not mix a row-match column from one table slice with an `INDEX` array that starts earlier or later unless you have explicitly validated the offset. Wrong: `=INDEX(Data!$A$1:$ZZ$200, MATCH(key, Data!$B$1:$B$200,0), MATCH(year, Data!$A$4:$ZZ$4,0))` when the actual keyed data block begins in column B. Right pattern: use an `INDEX` array whose first column corresponds to the header range and whose rows correspond to the matched key rows.
- After drafting the first lookup formula, inspect the referenced Data-sheet key column and year-header cells directly and confirm the matched row and matched column would intersect inside the intended return array.

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
- Do not begin Step 2 unless Step 1 has already been validated with nonblank numeric results in representative cells from each required lookup block; recalculation alone is not enough if the lookup cells are empty.
- Before filling H35:L40, verify one sample cell shows both the intended formula pattern `(exports-imports)/GDP*100` and a plausibly percent-scaled result, not a raw ratio/decimal.
- First identify the actual output cells for min, max, median, mean, and 25th/75th percentiles from the visible worksheet labels/highlighting; write formulas only into those confirmed cells.
- Do not infer statistic rows from spacing or prior templates; if the target cells are not explicitly visible yet, inspect the surrounding `Task` range first.
- After identifying the statistic labels, map each statistic to its exact output cell(s) before entering any min/max/median/mean/percentile formula.
- Prefer broadly compatible percentile formulas; if support is uncertain, use `PERCENTILE(range,k)` rather than newer variants like `PERCENTILE.INC`.
- Treat percentile/statistic formulas as compatibility-sensitive: before any bulk write to summary cells, place exactly one representative percentile formula in one confirmed target cell, recalculate immediately, and confirm the engine evaluates it numerically.
- If that test returns `#NAME?` or another function-support error, stop and switch to a more compatible function name before filling any neighboring summary cells.
- Do not bulk-fill percentile rows until one tested summary formula has been read back from the sheet and shown both valid stored text and a numeric result after recalculation.
- Do NOT start with newer percentile variants by default when compatibility is unknown. Wrong: `PERCENTILE.INC(range,0.25)`. Right: `PERCENTILE(range,0.25)` unless workbook evidence shows the newer variant is supported.
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
- Treat Excel formula syntax as a first-class validation target: after writing the first formula in any new pattern, read back the exact stored text and check for a leading `=`, balanced parentheses, correct sheet separator `!`, and valid function names before filling further.
- If a representative formula produces `#NAME?`, `#VALUE!`, or a parse error, do not bulk-fill corrections blindly; fix that single formula, recalculate, and confirm both syntax and result before propagating.
- After recalculation, use the pattern of errors to diagnose structure problems: errors only in the first or last year column usually indicate a misaligned year-header range or incomplete source-range coverage rather than a bad series-code match.
- Recalculation success is necessary but not sufficient: inspect representative cells in each required block to confirm both the exact stored formulas and the evaluated results.
- Formula presence alone is never enough for completion. If recalculation/output inspection is incomplete, resolve that first or keep inspecting narrower ranges until you can confirm actual evaluated values in the workbook.
- When a formula errors, change one representative cell only, recalculate, and inspect that exact cell's stored formula and value/error before editing any neighboring cells.
- After a single-cell test succeeds, copy the same pattern to the rest of the confirmed range; do not switch formula families or separators across the whole workbook without a proven working example.
- When debugging blank or incorrect lookup results, change formulas only after confirming the actual failure mechanism from inspected cells/ranges; do not attribute the issue to unsupported explanations without evidence.
- Preserve requested spreadsheet logic; do not change formulas merely to suppress errors, and do not mask failed lookups with `IFERROR(...,"")` or similar shortcuts.
- Prefer broadly supported Excel functions. If a function produces `#NAME?`, replace it with a compatible equivalent and recheck both the stored formula text and the evaluated result (for example, use `PERCENTILE(range,k)` if a percentile variant is unsupported).
- Work only in the existing workbook and sheets: keep edits in `gdp.xlsx`, confined to `Task` and `Data`, without changing file format, colors, fonts, or workbook structure.
- Choose tools based on the actual environment and file type before acting: `.xlsx` is a binary workbook, so do not use plain-text file readers as your primary inspection method.
- Use only listed/available tools; do not invent near-name variants or retry with unsupported tool names.
- If a dependency such as `pandas` is unavailable, continue with supported workbook-editing methods (for example `openpyxl`) instead of treating that missing package as a blocker.
- Stay inside the workbook-only workflow: do not create or modify helper scripts, exported data files, or other auxiliary artifacts when the task says to work only within the existing workbook/sheets.
- If formulas are written programmatically, protect Excel `$` references and quoting so the stored formula text is not corrupted before recalculation.
- If adding `$` absolute references causes a previously working formula form to fail in this environment, fall back to the exact compatible syntax you just verified and continue from that known-good pattern rather than assuming the more absolute form is safer.
- Avoid embedding Excel formulas with `$` inside shell double quotes unless escaped or passed through a safer path (for example, a single-quoted heredoc or direct Python script input); otherwise shell expansion can corrupt the stored formula.
- If the task requires an exact completion string, output that exact string and nothing else after the workbook is fully verified.
- Treat exact completion tokens and tool/message formatting as mandatory protocol: before ending, re-read the required final response and emit that exact string only, with no summary or extra commentary.

- Do not claim completion from partial rebuilds, isolated zero-error recalculations, or a few working sample cells; completion requires the full workbook outputs to be restored and checked in one final state.
- Treat formula-method requirements as hard constraints: if the task specifies lookup formulas or matching conditions, final cells must visibly implement that method, not an equivalent shortcut by direct references.

- If many downstream cells return `#VALUE!`, `#N/A`, or similar together, inspect the immediate upstream lookup/input cells first and confirm they evaluate numerically before changing summary or arithmetic formulas.
- When repeated errors persist after range or casing tweaks, re-read one stored formula verbatim and verify Excel-specific syntax first—especially the required `!` in sheet references.
- Protocol compliance is part of correctness: wrong action syntax, undeclared tools, malformed tool invocations, or a missing exact completion token means the task is not complete even if the workbook content appears correct.
- Never treat partial or truncated tool output as confirmation that a write command finished, saved, recalculated, or verified successfully; rerun checks until completion is explicit.
- If formulas are generated through shell-driven Python, avoid shell-expanded Excel strings that can corrupt `$` references; use a literal-safe path and then read back one stored formula.


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
- Do not treat a clean recalculation pass as sufficient proof of correctness. Before concluding, explicitly inspect representative cells for every required deliverable group and ensure the evidence covers each one, not just the weighted mean or one summary area.
- If a task required multiple output classes, final validation must mention all of them: Step 1 lookup population, Step 2 net-exports `% of GDP`, summary statistics, and Step 3 weighted mean.
- For each representative check, also inspect the referenced source-side structure: confirm the Data-sheet key column, year-header row, and bounded source block actually match the formula's lookup logic. Do not treat formula presence alone as verification.
- If earlier workbook inspection was truncated or partial, do not conclude from a few sample formulas alone; re-inspect the exact source headers/ranges used by those formulas until their semantics against workbook layout are explicit.
- Reconfirm that lookup formulas still reference the intended bounded source region and did not drift outside the verified `Data` block during debugging or fill operations.
- Confirm summary-statistic cells and the weighted-mean cell match the worksheet's labeled destinations, not assumed positions chosen earlier during debugging.
- Treat truncated or partial inspection output as a failed verification, not as evidence of success; rerun narrower targeted checks until every required cell/range is fully visible.
- If any required region was cleared or partially rewritten during debugging, repopulate all required formulas first, then recalculate, then verify again.
- Confirm the edited file is still the original workbook path/name (`gdp.xlsx`), not a renamed or replacement copy.
- If formulas were generated by script, reload the saved workbook and spot-check that representative cells still contain the intended formulas and preserved formatting/layout.
- Run one final recalculation pass after all formulas are written; investigate any `#NAME?`, `#N/A`, `#REF!`, `#VALUE!`, or similar formula errors by reading the stored formula text in the flagged cells before concluding the workbook is complete.
- Treat any suspicious verification output as a blocker even if it is not yet a confirmed Excel error: truncated formula text, partial previews, malformed parentheses, or incomplete function strings require a narrower targeted re-check of that exact cell/range before completion.
- Zero recalculation errors alone do not prove completion; confirm every requested output group is populated in the labeled destination cells, including all summary-statistic targets and percentile outputs, not just a few sample cells.
- Ensure the final logged actions actually show the completed workbook state: after the last rebuild, save/recalculate, re-read representative cells from every required output block, and only then send the exact completion action/token.
- If the environment required a specific action/tool-call schema during the run, confirm your entire interaction followed that schema before declaring completion; protocol violations are task failures even if the workbook contents are correct.
- Before ending, check whether the task or system requires an exact completion signal or response protocol; if so, compare your intended final response to that requirement verbatim and emit the exact required string/format only, with no extra text.

- Match completion claims to visible evidence: if any validation output is truncated, cut off, or only partially shows a checked range, rerun targeted inspection for the missing cells before concluding.
- Before claiming the workbook is complete, obtain direct evidence from each distinct output section: at least one read-back formula/value from Step 1 lookup cells, one from Step 2 net-exports cells, one from the summary-statistic cells, and one from the Step 3 weighted-mean cell.
- Verify the execution path itself before completion: confirm the write command finished, the workbook was saved, recalculation was run, and representative post-save cells were re-read successfully.
- Before concluding, compare your representative final formulas against any explicit method requirements in the task wording (for example, required lookup structure or matching conditions); if the wording and stored formulas do not match, fix the formulas or re-evaluate your interpretation before ending.
- Final gate: before sending the last message, compare it character-for-character against the required completion string. If a specific terminator is required, do not add any explanation, prefix, markdown, or trailing text.

## Final Check

- Verify all required output regions are populated: lookup blocks in `H12:L17`, `H19:L24`, and `H26:L31`; net exports % GDP in `H35:L40`; summary statistics; and the weighted mean output.
- Confirm formulas are present in the confirmed target cells and results are numeric/plausible where expected.
- Re-inspect any region with truncated, partial, or suspicious output before concluding the workbook is correct.
- Ensure the final workbook is fully rebuilt if any cells were cleared or overwritten during debugging.
- Before ending, check whether the task requires an exact completion signal; if so, emit it verbatim.
