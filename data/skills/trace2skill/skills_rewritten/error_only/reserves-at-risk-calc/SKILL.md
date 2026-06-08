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
- Perform a systematic workbook search before declaring the template missing: check the task-provided path first, then search allowed working directories for plausible `.xlsx`, `.xlsm`, or `.xls` files; open the best candidate and verify it contains the task-referenced sheets and answer area before editing. If the workbook, referenced sheets, or required 2025 source rows/cells are still missing after verification, stop and report the blocker; do **not** create a substitute workbook, replacement sheets, copied layouts, web-derived substitute tables, or estimated values.
- Inspect the workbook before editing and confirm the relevant sheets (`Gold price`, `Value`, `Volume`, `Total Reserves`, `Answer`), actual header rows, country labels, answer-area rows, and date layout.
- Treat workbook reconnaissance as a gate before any serious external search: after confirming the workbook exists, inspect the actual `Answer`, `Gold price`, `Value`, `Volume`, and `Total Reserves` contents (not just sheet names) to identify row meanings, 2025 locations, formulas, and required target cells.
- Do **not** spend most of the run hunting IMF links before understanding the workbook. External retrieval is secondary and only justified after targeted workbook inspection shows exactly what local data is missing.
- If the task requires Excel-only computation or specific worksheet functions, keep returns, volatilities, averages, lookups, filtering, and RaR in workbook formulas. Use Python/openpyxl only to inspect the file, place formulas/text, copy ranges, and save; do **not** compute final task logic externally and paste numeric outputs.
- Treat method requirements as deliverable requirements. Keep returns, averages, volatility, filtering, reserve conversions, lookups, exposures, and RaR expressed in worksheet formulas in the specified cells. Python/openpyxl may inspect workbook structure, place formulas/text, copy ranges, save, reopen, recalculate, and verify only when the task allows it; it must **not** become the main calculation path or compute intermediate/final task logic for paste-back. If the task explicitly forbids external scripting/editing entirely, stop and report that tooling blocker rather than completing the workbook by a forbidden method.
- When the task names a required worksheet formula family or pattern (`INDEX`+`MATCH`, `XLOOKUP`, etc.), implement that method literally in the workbook cells; do **not** substitute direct references, Python dictionaries, or hard-coded pasted values.
- Use only workbook data or explicitly authorized external data. Do **not** invent, estimate, backfill, or substitute missing country/reserve values unless the task explicitly authorizes it.
- Preserve source sheets and unrelated cells; do **not** blank, overwrite, or "fix" input cells just to suppress formula/recalc errors.
- Do **not** modify pre-existing source/template cells outside the requested answer/output area just to clear workbook-wide errors, and do **not** rename sheets/tabs or rewrite workbook structure for tool compatibility. Repair the required formulas/ranges within the existing workbook semantics, or exclude a country only when workbook evidence shows there is truly no valid 2025 match.
- If the task specifies an exact completion token or protocol, follow it verbatim.
- Treat any exact completion token/protocol as a blocking deliverable: before the final response, re-check the instructions and output the exact required string alone with no extra prose, code fences, or summary text.
- Before performing any extraction, download, formula writing, or workbook creation, confirm the full deliverable scope from the task and verify that every referenced workbook/template dependency needed for all requested steps is present or truly missing after search. Do **not** begin Step 1 work on the assumption that later-step inputs will appear later.
- Re-check the environment/task protocol before any substantive work and again before the final response. Treat any required interaction/action/tool/interface syntax as mandatory for the **entire** run, not just the final message; do **not** improvise alternate tool-call styles, wrappers, helper tools, malformed action formats, or narrative final responses when an exact terminator is required.
- If the workbook file is `.xlsx`/`.xlsm`/`.xls`, inspect it with spreadsheet-aware tooling or Python workbook libraries, not plain-text file readers.
- Run a final pre-response gate: compare your planned last message character-for-character against the required completion protocol and remove any summary, explanation, code fence, filename reminder, or trailing text. If a specific token is required, output that token alone.

- If required source data is unavailable from the workbook or the explicitly authorized source, stop and report the blocker rather than mixing substitute external datasets with different definitions, years, or coverage. Do **not** combine unreconciled figures from multiple websites just to fill the workbook.
- Treat any plan to populate `Value`, `Volume`, `Total Reserves`, or other source sheets with sample, placeholder, provisional, or manual stand-in data as forbidden unless the task explicitly authorizes creating those inputs.
- Prefer minimal in-place repairs to the discovered workbook. Do **not** reorganize the `Answer` sheet, rebuild the workbook, recreate sheets, or rewrite layout/structure as a troubleshooting tactic when formulas can be repaired within the existing template.
- Track workbook identity explicitly by absolute path. Before inspecting or editing, print/read back the exact source workbook path you opened; before saving, print/read back the exact destination path. Do **not** reason from sheet listings or cell reads taken from a different workbook than the one you will modify.
- Treat your own validation findings as authoritative blocking signals. If recalculation or validation reports any remaining workbook error after your edits, do **not** declare success unless you can prove it is outside the deliverable scope, untouched by your changes, and not referenced by required outputs.
- Treat filesystem restrictions as blocking constraints. Before creating any script, temp file, or output workbook, confirm the path is explicitly authorized by the task/context.

## Multi-Step Process

### Before Step 1
- Treat the workbook as the source of truth for country lists, 2025 rows, headers, blank answer areas, and required row meanings.
- First parse the task into a full prerequisite checklist: required workbook/template file, required sheets, required source data for Steps 1-3, required output path, and any exact completion token. Do not start implementation until this checklist is reconciled against the workspace.
- Verify workbook layout from existing labels/formulas before bulk-writing anything; derive formulas from workbook evidence and explicit task text, not guessed interpretations or assumed row/column positions.
- Do **not** assume `2025` is on a fixed row or column; inspect the relevant source sheets to verify the actual year row/column, header row, and data ranges.
- Before extracting any 2025 country set from `Value`, `Volume`, or `Total Reserves`, explicitly identify the year-label row/column and read back a few candidate 2025 intersections. If the detected year/header position is missing or ambiguous, stop and inspect more narrowly rather than continuing with `None` or guessed indices.
- For country matching across sheets, use exact workbook labels or a verified one-to-one mapping derived from the workbook. Do **not** use prefix, substring, or fuzzy matching.
- Before bulk-filling formulas, write 1-2 representative cells, inspect the exact stored formula strings, and recalculate/check results.
- When writing formulas programmatically, verify the stored text is a plain Excel formula with valid quoting and sheet references before any fill-down. **Do not** write malformed strings like `=\"Gold price\"!D430`; use `='Gold price'!D430`.
- Use a pilot write-recalc-readback loop for each formula family: write 1-2 representative cells, confirm the stored text begins with `=` and uses valid sheet/range syntax, recalculate, then verify the evaluated result and required formula method before filling the rest. Treat formula-engine compatibility as a hard gate before bulk fill: default to compatibility-safe formulas first when the task/template does not explicitly require a newer function (for example `INDEX`+`MATCH` over `XLOOKUP`). In that pilot check, verify formula dialect and arity too: use the separators expected by the workbook/engine, confirm functions have the correct number of arguments, and inspect the exact stored formula string after writing. If a sample throws `#NAME?`, parse errors, stray quoting, malformed cross-sheet references, blanks, wrong-row placement, extra/missing arguments, or separator mismatches, stop and fix that pattern before any bulk fill; do **not** spread an unverified formula family across the workbook and patch it later.
- Do **not** fill any required answer cell while the mapping, row meaning, or calculation interpretation is still uncertain. Resolve ambiguity from workbook labels, units, neighboring formulas, and task text first; if that still does not resolve it, stop and report the blocker instead of guessing.
- If external data access is blocked or repeatedly fails, stop retrying similar URLs and complete all workbook-dependent steps you can from local contents first.

- Start with file discovery and workbook reconnaissance: open the real workbook/template first, then confirm actual sheet names, header rows, country/year label locations, date/value formats, answer-area row meanings, and the source ranges needed for Steps 2 and 3 before writing anything.
- If any inspection output is truncated or incomplete, rerun narrower targeted reads until the relevant rows/columns/countries/date windows are fully visible; do **not** derive country lists, 2025 availability, mappings, or target ranges from partial previews.
- If a read returns placeholders, invalid paths, logging artifacts, binary-file previews, or other non-workbook content, treat that as a failed inspection and retry with a narrower, explicit workbook/sheet read before editing. Do **not** proceed from partial previews, placeholder text, or ambiguous inspection output.
- Record the exact Step 2 and Step 3 destination rows/cells from the existing `Answer` sheet before writing. Treat nearby labels/instructions as definitions to read, not blanks to reinterpret; do **not** shift, expand, relocate, or redesign the answer blocks.
- Before filling any target block, clear or overwrite only the intended destination cells and read them back to confirm stale formulas, duplicate countries, or leftovers from earlier attempts are gone.
- For country matching across sheets, use exact workbook labels or a conservative one-to-one normalization proven by workbook evidence; do **not** use prefix, substring, fuzzy matching, naive alias dictionaries, or manual country-to-column assumptions.

- Do **not** ask the user whether the workbook/sheets exist until after you have searched allowed directories and inspected the candidate files yourself.
- When multiple spreadsheets are present (for example a source data download and a template workbook), verify which file is the target workbook **before** using any sheet names, row labels, or formulas as layout evidence. Re-check the active workbook path whenever you switch files.
- Read the workbook's embedded instructions before any external-data work: inspect the `Answer` sheet and any nearby instruction blocks/comments/merged cells so you can identify the exact Step 1/2/3 deliverables, target rows, and required formula methods from workbook evidence.
- Before populating any cross-sheet formulas or country lists, build a canonical one-to-one country mapping from workbook evidence and validate it on a small sample. Use exact workbook labels or a conservative verified normalization only; do **not** use wildcard, substring, prefix, or fuzzy matching in required output formulas.
- At every extraction boundary used for downstream math, verify the selected cell(s) are the intended **numeric** workbook values, not dates/timestamps, labels, headers, or empty cells. Read back the matched row/column labels and the Python-side value/type before relying on that selection.
- After **every** workbook-editing script or bulk formula write, run an explicit post-write proof step before continuing: confirm `/root/output/rar_result.xlsx` (or the current working copy) was saved, reopen it, inspect 2-3 intended changed cells, and print a concise success marker with the path and checked cells.

### Step 1: Gold Price Analysis
- Download IMF commodity data
- Only begin IMF/gold-series retrieval after workbook reconnaissance confirms the overall task really requires the gold-price step and that the workbook/template needed for downstream Steps 2 and 3 is available, or the task explicitly permits proceeding despite a documented blocker.
- Confirm the selected IMF series is gold in US$ per troy ounce (for example `PGOLD`) before writing anything; reject broad commodity indices or nearby non-gold series.
- Time-box external IMF retrieval attempts. After repeated access-blocking failures, stop retrying minor URL variations, document the blocker, and complete all workbook-local inspection/editing work you still can.
- Treat repeated denial or wrong-format signals as decisive: after a few attempts that return `403`, `Access Denied`, HTML/XML pages, tiny non-data files, or equivalent blocking messages, stop trying alternate fetch tools or near-identical URL variants for the same source and pivot to workbook-local work plus any already-authorized available data.
- Extract gold price (US$/troy ounce)
- Calculate: monthly log return, 3-month volatility, 12-month volatility
- Fill in "Gold price" sheet columns C-E
- Note: multiply log returns by 100 for percentage

- Use the IMF gold price series for **gold in US$ per troy ounce** (for example `PGOLD`), not broad commodity indices; validate the series header and unit before filling formulas.
- Write formulas in the worksheet for monthly log return and 3-month/12-month volatility; do not precompute these metrics outside Excel.
- Anchor formulas to the actual monthly series layout: the first valid log return should be on the first row with both current and prior month prices.
- Keep the horizon explicit: distinguish latest **3-month volatility** from latest **12-month volatility**. Do **not** annualize by habit; only annualize if the worksheet/task explicitly requires it.
- If annualization is explicitly required, derive it from the verified source horizon rather than assuming the input is monthly. If annualization is not explicitly requested, keep the native 3-month or 12-month rolling volatility unchanged.
- If log return is entered as `LN(price_t/price_t-1)*100`, volatility outputs are in percentage points. Use numeric formatting, **not** Excel percent formatting.
- Use valid cross-sheet formula syntax such as `='Gold price'!D430` or `=AVERAGE('Gold price'!B421:B429)`; do **not** write malformed references like `=\"Gold price\"!D430`.
- Verify the exact date rows from sheet labels before building formulas; before using any Jan-Sep 2025 average, confirm the source dataset actually contains months `2025M01` through `2025M09`.
- Spot-check representative cells after filling formulas: the first return cell, first valid 3-month volatility cell, first valid 12-month volatility cell, and the final populated row.

- Build date-based ranges from the actual month labels in the sheet, not assumed offsets; explicitly confirm Jan-Sep 2025 coverage before computing or labeling any Jan-Sep 2025 average.
- For monthly returns, place the first formula on the first row that has both a current-month and prior-month gold price; the cell above should remain blank. Start 3-month and 12-month volatility only when the full rolling window exists.
- In `Answer`, reference the **latest populated** volatility cells from `Gold price`, not an early sample row. If the task asks for an annualized 3-month figure, derive it from that latest 3-month volatility cell.

### Step 2: Country Gold Reserves
- Derive the country list from workbook evidence: include countries with 2025 gold reserves in `Value`, then add any additional 2025 countries found in `Volume`.
- Before adding any country from `Volume`, confirm the relevant row/cell actually contains 2025 data for that country.
- Fill the existing Step 2 area in `Answer` exactly where the template expects it; confirm each target row's label/definition before writing formulas and do not shift rows to fit your own layout.
- Build the list and pulled values with workbook formulas/links; do not hard-code, guess, or manually type a country subset from ad hoc inspection.
- Inspect `Value` and `Volume` to identify which cells contain country names, 2025 data, and numeric reserve values; ignore metadata/header noise and do not assume fixed positions from partial previews.
- Normalize country names conservatively before matching across sheets; use exact workbook names or explicit, verified normalization rather than fuzzy/substring matching.
- Use the Jan-Sep average as the 2025 gold price substitute via Excel formula(s) in the workbook.
- Sanity-check volume-to-value conversions with rough magnitude logic (for example, millions of ounces × thousands of dollars/ounce should usually yield billions of dollars, not millions).

- Before filling any Step 2 row, read the exact `Answer`-sheet row label and nearby instructions/formulas to confirm the intended definition. Populate only the rows intended for countries, and do **not** let the country list spill into rows reserved for exposure, volatility inputs, or later steps.
- Build the Step 2 country set from workbook evidence only: include countries with confirmed 2025 gold reserves in `Value`, then explicitly check `Volume` for additional countries with real 2025 data that are absent from `Value`. Before adding any `Volume`-only country, perform a targeted readback of that country's 2025 cell(s) and confirm the value exists.
- Build the country list, Jan-Sep 2025 price substitute, pulled values, and any volume-to-value conversions with worksheet formulas/links from verified workbook data only; do **not** hard-code a country subset, manually backfill reserve values, or search the web for Step 2/3 reserve inputs.
- Verify the source unit before any volume-to-value conversion (ounces, millions of ounces, tonnes, etc.) and do a quick order-of-magnitude check on a sample country before filling the rest.

- Before finalizing the Step 2 country set, inspect the raw candidate labels and filter out obvious non-country/non-data entries such as blanks, `Unnamed`, metadata rows, duplicated reserve-label variants, or header text. Keep one canonical workbook label per country, based on exact workbook evidence, before writing anything to `Answer`.
- Establish the final country mapping before filling Step 2: each included country must map to exactly one verified source label in each referenced sheet, or be excluded with workbook evidence. Do **not** rely on ad hoc post-fill normalization or cleanup.
- Maintain a single **final included-country list** for the workbook after checking both Step 2 availability and Step 3 prerequisites. If a country is later excluded because required `Total Reserves` or other Step 3 inputs are missing, remove or avoid populating that country in **both** Step 2 and Step 3 answer rows; do **not** leave unsupported countries in Step 2 only.

### Step 3: Reserves-at-Risk Calculation
- Replicate Step 2 into the rows explicitly specified for Step 3 (typically rows 20-22 in `Answer`) **literally as requested**: countries, gold reserves value, and the template-requested volatility/input rows; do **not** move Step 3 elsewhere or substitute different metrics.
- Populate Step 3 from the same filtered country set used in Step 2; do not carry forward countries that should be excluded.
- For 2025 Total Reserves, write workbook lookup formulas by matching country and year labels (`INDEX`+`MATCH` or `XLOOKUP`, according to the task/template). If function support is uncertain, prefer compatibility-safe `INDEX`+`MATCH`.
- Build lookups from actual workbook headers and exact country names; for horizontal source tables, use `MATCH` as the column index of `INDEX` (or use `XLOOKUP`) rather than as a row index.
- Do **not** replace required lookups with hard-coded coordinates, guessed direct references, Python dictionaries, or manually pasted reserve values.
- If a lookup fails, debug the workbook ranges/keys/header matching first. Delete/exclude a country only after confirming there is truly no 2025 reserve data match under the workbook's exact naming.
- If volatility/returns are stored as percentages (`*100`) in cells, convert back to decimal in exposure/RaR formulas.
- Calculate RaR with Excel formulas in row 24 only after the required inputs/intermediate rows are populated, and fix any `#N/A`, `#VALUE!`, `#NAME?`, `#REF!`, or `#DIV/0!` errors in required output cells before finishing.

- Before filling Step 3, make a literal row checklist from the template labels and confirm each populated row matches the task wording exactly. Replicate Step 2 into the specified Step 3 rows with workbook formulas when the template expects the same values; do **not** rebuild Step 3 from Python-side dictionaries, pasted literals, or a re-derived country list.
- For `Total Reserves`, the final `Answer` formulas must visibly perform a label-based country/year lookup against `Total Reserves`; direct references such as `='Total Reserves'!D18`, manual maps, or Python dictionaries are not acceptable substitutes when a lookup is required.
- Validate one representative Step 3 lookup formula before filling across: confirm exact country-key matching, that the 2025 header is found in the correct table orientation, that the chosen function is supported by the recalc engine, and that the stored formula text still uses the required lookup method. For horizontal tables, use the year `MATCH` as the **column** argument of `INDEX`.
- Before any Step 3 bulk fill, do an explicit mapping spot-check for 2-3 countries: read the Step 3 country label, the exact `Total Reserves` source row/column found for that country and year, and the resulting value. If any checked country maps to the wrong source position or wrong value, stop and fix the lookup ranges/orientation before filling the block.
- Do **not** assume copied formulas preserved country-to-column alignment across sheets; prove the mapping with direct readback before and after fill.
- If a Step 3 lookup errors, debug keys, year/header cells, orientation, ranges, quoting, and function support first. Do **not** switch among `XLOOKUP`, `INDEX`+`MATCH`, direct references, or hard-coded values by trial and error.
- If Step 3 uses percentage-point volatility cells from Step 1, divide by 100 inside exposure/RaR formulas before applying them as multipliers.
- After populating Step 3, compare its country row against the final Step 2 filtered set and confirm there are no duplicates, leftovers, or excluded countries reappearing.

- Use the same prevalidated canonical country mapping from Step 2 when building Step 3 lookups. If a country label differs across sheets, fix the mapping before writing formulas; do **not** populate first and then delete duplicates or repair mismatches afterward.
- Build a concrete validated Step 3 inclusion list **before** writing Step 3 formulas: keep only countries that are present in the final Step 2 set **and** have a verified 2025 `Total Reserves` match under the workbook's exact country/year labels. Then populate every Step 3 country-dependent row from that same list only.
- Write country names/labels as plain text values, not formulas. **Do not** write `=belarus` or `=georgia`; write `Belarus` or `Georgia` as text, and reserve formulas only for cells that are supposed to calculate.
- Immediately inspect one representative Step 3 label cell and one representative Step 3 formula cell after writing them: confirm the label cell does **not** start with `=`, and confirm the formula cell is complete rather than truncated.
- Audit Step 3 for **completeness**, not just formula validity: compare the final Step 3 country/value/input/RaR block against the final Step 2 filtered country set one-by-one and confirm no country is skipped because of inconsistent naming, non-sequential references, broken cross-links, or leftover stale rows.

- Before writing any lookup formula family across many cells, inspect one representative source key from each lookup dimension, for example country label and year header, and confirm the stored value/type the formula must match: text vs number, exact spelling, and table orientation. Build the formula to match the workbook's actual stored keys; do **not** assume years are numeric just because they display as years.
- If the task/template does not explicitly require a newer function, prove function support with one representative formula and recalc before bulk fill. Prefer compatibility-safe `INDEX`+`MATCH` first unless verified support for `XLOOKUP` or another newer function is required and confirmed.
- Apply the same truncation rule to script/write output and post-save inspections: if save logs, formula dumps, recalculation reports, or `Answer` previews are cut off or suspicious, rerun targeted checks before trusting the result.
- When repairing a script that writes the workbook, make only concrete, evidence-based edits to the actual failing lines or expressions. Do **not** use placeholder replacements such as "fix formula logic" or "update sheet selection"; inspect the current file contents, change the exact code, then rerun and verify the resulting workbook cells.
- For any repeated row-wise formula pattern in `Answer`, inspect at least two non-adjacent populated rows after fill/copy and confirm the references shifted correctly for each row rather than staying fixed on one country's inputs. If outputs repeat suspiciously across different countries, stop and debug the relative references before continuing.
## Output

- Save the edited workbook directly to the exact path `/root/output/rar_result.xlsx`.
- Preserve the workbook template, required sheet names, and required formulas in the answer cells; do not substitute hard-coded computed values where formulas are required.
- Verify the saved file exists at that exact path and reopen it to confirm representative formula cells in `Answer` were written correctly.
- File existence alone is not sufficient. Reopen `/root/output/rar_result.xlsx`, inspect representative populated cells in both `Gold price` and `Answer`, and confirm the stored formula text is intact (not truncated, malformed, or badly quoted), the required rows remained in their original template locations, and the deliverable cells evaluate or have been explicitly recalculated.
- If recalculation is required for formulas to produce values, perform or confirm that recalculation before declaring success.
- After saving, follow any exact completion protocol from the task instructions.

- If you create a helper script for inspection or workbook updates, run it immediately, inspect its stdout/stderr, and confirm it actually wrote `/root/output/rar_result.xlsx`; script creation alone is not progress.
- Do **not** stop at drafting code. Finish only after an executed end-to-end write path has saved the workbook, reopened it, and passed representative cell checks.
- Base any completion claim on the **latest** recalculation/verification output only. If the newest tool result still shows any error, blank required cell, malformed formula, inconsistent row structure, or truncated final inspection, do **not** claim success; fix it first or report the blocker accurately.
- Validation must cover every task-relevant sheet implicated by the assignment. At minimum, inspect representative required cells on `Gold price` and `Answer`, and also confirm the source-driven sheets used by formulas (`Value`, `Volume`, `Total Reserves`) still contain the expected labels, year headers, and ranges needed by the final formulas.
- If the task/environment requires an exact completion token, treat it as the **only** final response. Once validation succeeds and the workbook is confirmed complete, stop immediately and emit the required completion token verbatim with no additional prose.

## Verification Before Completion

- Recalculate the workbook in a spreadsheet engine when required, save it, then reopen the saved file and inspect representative `Answer` cells. Do not finish while required results remain unrecalculated, representative formulas are malformed, validation output is truncated/ambiguous, or required cells are blank/`None`/erroring.
- Treat any recalculation/validation report with a nonzero error count as a blocking failure, not a near-success. If a tool reports errors remaining anywhere in the workbook, inspect each reported sheet/cell explicitly and either fix it or confirm with workbook evidence that it is pre-existing, untouched, outside the requested deliverable area, and not referenced by required outputs.
- When only 1-2 errors remain, switch from broad rewrites to targeted debugging: open the exact reported cell, read its stored formula/value and immediate precedents, fix that specific root cause, then recalculate and recheck before doing anything else.
- Confirm Step 1, Step 2, and Step 3 required cells are populated in their original designated locations and contain intact formulas beginning with `=` where formulas are required.
- Treat zero recalc errors as necessary but not sufficient. Also inspect the full required output ranges for semantic completeness: no unintended blanks, no partially populated country rows, no duplicate or stale leftovers, and no missing final RaR cells.
- For Step 3 specifically, read back the entire required country/value/input/RaR block and confirm every expected position is populated consistently with the final Step 2 filtered country set before finishing.
- Inspect representative final formula text and evaluated values after any late correction; sanity-check that included/excluded countries are consistent across Step 2 and Step 3.
- Treat spreadsheet errors in required output cells as blocking unless direct evidence shows any remaining error is pre-existing, outside the requested deliverable area, untouched by your edits, and not referenced by the required outputs.
- Do not report numeric conclusions unless the final saved workbook evaluates correctly in those cells.
- Read [references/validation-and-debugging.md](references/validation-and-debugging.md) when formula cells error or recalculation reports spreadsheet errors.
- Also read [references/validation-and-debugging.md](references/validation-and-debugging.md) when formula-generation logic may be malformed, when testing formula compatibility/dialect, or when recalc succeeds but required output blocks still look incomplete.
- When recalculation shows many repeated `#NAME?` or similar formula errors, inspect one failing stored formula immediately and debug function compatibility/syntax in the recalc engine before rebuilding sheets, renaming tabs, or rewriting large areas.
- If the task specifies an exact completion string (for example `ACTION: TASK_COMPLETE`), output that exact string verbatim and nothing else.

`/root/output/rar_result.xlsx`:
- Completed "Answer" sheet with all calculations
- Excel formulas, not hard-coded values

- Validate the artifact, not just the script: reopen `/root/output/rar_result.xlsx` and inspect the exact required Step 1 cells on `Gold price`, Step 2 rows in `Answer`, and Step 3 rows in `Answer` including the final RaR row.
- Confirm representative required cells both contain formulas beginning with `=` where formulas are required and evaluate to plausible non-error results after recalculation; if readback returns blanks, `None`, wrong-sheet references, placeholder text, malformed labels, or spreadsheet errors in required cells, treat verification as failed.
- Audit representative saved formula strings directly after save/reopen, especially cross-sheet references, latest-volatility links, lookups, and RaR formulas; confirm valid quoting, complete arguments, and no truncation.
- Confirm the final artifact is the discovered/edited template workbook saved to `/root/output/rar_result.xlsx`, not a newly invented replacement with recreated sheets.
- After any late correction, rerun the full validation loop: recalculate, save, reopen, and re-check representative required cells before finishing.

- Treat contradictory, truncated, missing, or exception-terminated verification output as a blocking failure. If a check cuts off, a script crashes, or a preview shows only part of the required Step 1/2/3 areas, rerun narrower direct inspections until the final stored formulas and evaluated values are fully visible.
- Do **not** treat script success, lack of exceptions, or file existence checks as proof the task is done. Proof requires reopening `/root/output/rar_result.xlsx` itself and inspecting representative required cells, stored formulas, and evaluated results in the saved workbook.
- If recalculation is required and an available local spreadsheet engine can perform it, run that engine, save, reopen, and verify the resulting workbook; do **not** delegate recalculation to the user. Unevaluated formulas are not an acceptable final state when completed workbook answers are required.
- Use evaluated deliverable values as the final acceptance gate, not formula presence alone. If required `Answer` cells still show blank, `None`, malformed percentages, implausible values, unchanged template cells, or other suspicious results after recalculation/reopen, do **not** declare success.
- Validate **each populated answer block**, not just isolated sample cells: inspect representative first/last/interior cells for Step 1, the complete Step 2 country/value rows, and the complete Step 3 country/input/RaR rows; confirm no excluded or unsupported countries remain in any populated block.
- If recalculation reports an error outside the answer area, trace whether any required output formula depends on that cell or sheet before dismissing it as irrelevant. Inspect recalc/error reports for inherited placeholder formulas or literal error tokens in sheets referenced by the deliverable, and repair the relevant deliverable path before finishing if required outputs depend on them.
- Before the final response, verify both kinds of required cells in the saved workbook: text/label cells remain plain text, and formula cells begin with `=` and evaluate correctly after the required recalc workflow.
- Immediately before the final response, run a last completion gate: confirm no recent script/verification command ended with an exception or ambiguous/truncated output, confirm the workbook was revalidated after the last edit, confirm no unresolved reported workbook errors remain that affect required outputs or edited areas, and if an exact completion token is required, send that token alone with no surrounding text.

## Tips

- First inspect the workbook to confirm the named sheets, exact answer locations, headers, and workbook structure referenced by the task.
- Use native Excel formulas/workflows when the task requires workbook-based computation; use openpyxl only when instructions permit programmatic workbook editing.
- Use `INDEX`+`MATCH` or `XLOOKUP` for dynamic lookups by country/year headers, based on the task/template and verified function support.
- Prefer label-driven formulas tied to verified sheet headers/country names over hard-coded coordinates.
- Test one representative formula per pattern before filling ranges, then read back the stored formula text if results look wrong.
- After each formula family, sanity-check 2-3 populated cells: verify the formula, referenced ranges/sheets, displayed value, and unit/format.
- Handle missing data appropriately: prefer exclusion or task-approved logic over guessed replacements, and do not clear or overwrite unrelated workbook cells outside the required answer area unless the task explicitly asks for repairs.
