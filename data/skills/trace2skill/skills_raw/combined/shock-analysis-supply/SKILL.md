---
name: shock-analysis-supply
description: "Estimate investment spending shock using Cobb-Douglas production function with HP filter in Excel."
---

# Supply-Side Shock Analysis with Cobb-Douglas

## When to Use

- Estimate potential GDP using production function
- Apply HP filter to extract trends
- Model investment shocks in Excel

## Non-Negotiable Constraints

- Populate and save the provided workbook/template; do not create a replacement workbook unless the task explicitly asks for redesign.
- Preserve required sheet names, layout, formulas, named areas, and live model cells; do not overwrite calculation blocks with notes, pasted outputs, or hardcoded replacements.
- Use the named official sources directly: PWT from the official PWT source, IMF WEO from the IMF WEO interface/portal, and ECB for CFC. Do not rely on search-engine snippets, mirrors, summary pages, proxy series, or estimated annual values unless the task explicitly permits it.
- If the task requires Excel-only workflow, keep calculations in Excel cells and use Excel Solver for the HP filter; do not substitute Python, scripts, or externally computed pasted values.
- Follow any task-specified workflow, tool, source, derivation path, and completion requirements exactly. If depreciation must be derived from ECB CFC relative to PWT capital stock, do not substitute PWT `delta` or another proxy.
- Do not enter estimated, interpolated, placeholder, snippet-derived, or manually approximated values where the workbook should contain source data or formulas.
- Start executing once the task is specified; do not remain in planning mode when the workbook, sources, and output are already defined.
- If a required source, tool, or Excel/Solver step is blocked, complete other reachable workbook work and report the blocker rather than fabricating values or claiming completion.
- Do not finish while key production or output cells still show blanks, `#N/A`, `#VALUE!`, or similar unresolved errors.

- Open the provided workbook and modify that file in place at the given task path. Do not rebuild the template with Python/openpyxl, switch to an alternate copy, create a replacement workbook, replacement sheet set, workaround/helper tabs, or recreate the structure from scratch unless the task explicitly asks for redesign.
- Follow any task-specific action protocol exactly, including required tool-call format, browser/tool choice, source-access method, message schema, exact cell/range targets, and exact final completion string.
- If the task says Excel-only, stay entirely inside Excel for workbook inspection, data entry, formulas, recalculation, Solver, validation, and saving. Do not switch to Python, openpyxl, pandas, shell tools, VBA, LibreOffice, or other external code/tools unless the task explicitly permits it.
- Do not choose a workflow that cannot complete required native Excel steps end-to-end. If the task requires Excel Solver, recalculation, inspection, save, or in-app validation, use an Excel-capable workflow from the start.
- Open `test-supply.xlsx`, make a real workbook edit or setup step early, and keep advancing the actual file throughout the task; do not spend the session on reconnaissance, searches, or prose while the workbook remains untouched.
- If a required source, portal path, Solver step, tool, or protocol element is blocked, complete all other reachable workbook work, leave unsupported fields unresolved, and report the exact blocker rather than substituting proxies, estimates, fabricated values, or externally computed stand-ins.
- Never place notes, Solver instructions, scratch calculations, or reminders inside occupied workbook cells or live model ranges. Keep working notes outside the workbook, or only in clearly empty non-model space after verifying no formulas, names, or downstream references depend on it.
- Do not enter guessed stand-ins such as fixed depreciation assumptions, proxy K/Y capital stock, placeholder annual series, or other invented model-defining assumptions unless the workbook or task explicitly specifies them.
- Do not mass-fill formulas until representative cells have been entered, recalculated, and inspected; if key model areas still show material errors, keep debugging rather than stopping at a partially repaired file.
- Do not claim final quantitative results unless they are visibly produced by the recalculated saved workbook or clearly identified workbook outputs you inspected after recalculation.


## Multi-Step Process

**Before editing the workbook:** inspect existing sheets, headers, named areas, formulas, and occupied ranges. Verify target-column mapping from headers or example rows before entering data, especially when a field is unlabeled, then proceed to populate `test-supply.xlsx` rather than stopping at reconnaissance.


**Compliance priority:** treat source fidelity, template preservation, and required methodology as primary success criteria. Use zero formula errors only as a final check after confirming the workbook still uses the mandated sheets, sources, derivations, and Solver-based HP filter.

**Execution gate before proceeding:** if the task mandates a collection tool or in-application step (for example a required web workflow or Excel Solver), use that exact tool/step as part of the deliverable. Do not switch to Python, `curl`, search snippets, or workbook-editing scripts unless the task explicitly allows it.


### STEP 0: Workflow and source validation
- Confirm allowed tools, application restrictions, and any required completion signal before doing anything else.
- Open `test-supply.xlsx` early and work toward sheet completion, not just data reconnaissance.
- For each required external series, obtain the full year-by-year table from the specified official source before entering values or formulas.
- After every download or API call, confirm it is the expected dataset and format by checking file type, sheet names, headers, visible keys, and that it is not an HTML/error page.

- Before the first tool action, identify any required action syntax, allowed applications, named retrieval interface, Solver objective/changing-cell requirements, exact workbook targets, and exact completion signal; follow that contract throughout the run.
- Extract any task-specific method requirements up front (for example: required source interface, Excel-only calculations, exact completion phrase) and follow them literally throughout the run.
- Confirm your planned tool/application path can complete every required step end-to-end, including mandated source access, Excel Solver, recalculation, inspection, save, and any final completion token.
- Verify workbook structure before populating: confirm destination columns/sheets from visible headers, neighboring formulas, named ranges, or task metadata. Do not infer unlabeled columns, units, or model roles from guesswork.
- Before writing any values, identify which workbook regions are live model areas versus safe input areas by checking headers, example rows, neighboring formulas, named ranges, and precedent/dependent patterns; if a column, unlabeled field, or formula role is ambiguous, resolve the mapping before populating that area.
- Treat workbook inspection as a brief setup step: once sheet/column mapping is understood, begin populating the workbook and continue iteratively rather than delaying edits until every source has been fully researched.
- Treat source retrieval as incomplete until you have the actual year-by-year table/file in hand. A snippet, landing page, chart view, metadata page, truncated preview, HTML response, or error page is not a completed dataset.
- If an official download or export expected to be machine-readable returns HTML, a landing page, a 404, or another unusable format, treat retrieval as unresolved and switch to another official access path within the same source family/portal instead of refining the same weak search pattern.
- Once you identify an official export/API/download endpoint, execute it promptly and validate file type, schema, headers/keys, and usable annual rows immediately. If the response is structurally wrong, discard it rather than adapting downstream work around it.
- Limit retries on an unreachable source or portal. After a small number of failed attempts with no new retrieval path, pivot to other sheets, formulas, links, and setup work in `test-supply.xlsx` instead of repeatedly probing the same dependency.
- If a required source series ends earlier than the workbook horizon, identify the exact last observed year and validated transition point before wiring downstream formulas so historical-source rows and extended rows remain distinct.

### STEP 1: Data Collection
- PWT database from Groningen
- IMF WEO for real GDP
- If the task explicitly requires Playwright MCP or another named access method for IMF WEO extraction, use that method to retrieve the actual year-by-year series from the official interface before populating Excel.
- ECB for CFC (consumption of fixed capital)
- Calculate depreciation rate

- Prefer direct machine-readable official sources (XLSX/CSV/API) over search snippets or landing pages.
- Validate each imported series before use: confirm variable identity, year coverage, units, currency, price basis, and that you obtained workbook-ready annual year/value series.
- Use the specified external sources exactly; do not substitute other databases or guessed placeholders when the task specifies IMF WEO, PWT, or ECB/CFC.
- Verify each imported series is complete for the required years before linking it into downstream model sheets.
- Do not hand-reconstruct missing years from partial fetches or backfill guessed values from snippets.
- If units or coverage are inconsistent, stop and reconcile with a conversion or alternate official retrieval path rather than changing methods or using mismatched ratios.
- If asked to derive depreciation from ECB CFC and PWT capital stock, calculate that rate in-sheet and average the specified recent years into the production assumption cell.
- Write confirmed series into the workbook as soon as they are validated; do not leave usable GDP or capital-input data unintegrated while continuing source exploration.
- If a required series cannot be fully retrieved from the specified source family, mark it incomplete, complete other reachable workbook steps, and report the blocker clearly rather than substituting convenience sources or unsupported estimates.

- For each series, prefer this order: official downloadable workbook/CSV -> official API -> official portal export. Use search engines only to locate the official endpoint, not as the data source.
- Capture evidence of completeness before entry: confirm the official export/table visibly contains the full required year range, expected number of observations, correct variable identity, units, and workbook-ready annual values.
- After a successful file download, API response, or portal export returns structured rows/columns, stop searching for that series and immediately parse the returned fields into workbook-ready annual year/value data.
- Go straight to the official database/export interface for IMF WEO, PWT, and ECB/CFC. Do not keep refining generic searches once results only describe the source or show partial previews.
- After one or two incomplete retrieval attempts, escalate to the source's direct export/query workflow or other allowed path within the same official source family instead of patching the same speculative scraping/search approach.
- For task-mandated IMF WEO inputs, populate the workbook only from IMF WEO outputs obtained through the required WEO workflow/interface; do not backfill those cells from PWT, other institutions, snippets, or manual approximations even temporarily.
- Verify the full contiguous required annual series is present, with correct identity/units/coverage, before linking it into downstream formulas; partial extraction is not enough for downstream fill.
- Do not transcribe or reconstruct annual series from snippets, clipped tables, metadata pages, single-year observations, mirrors, or third-party reposts.
- Never enter placeholder, interpolated, manually estimated, snippet-derived, projected, or convenience-forecast annual observations into required source-data ranges unless the task explicitly authorizes estimation.
- Do not compute depreciation or any other ratio from series with unresolved currency, price-base, scale, or year-alignment mismatches. If depreciation must be derived as ECB CFC divided by PWT capital stock, keep that derivation in-sheet and reconcile units first; do not substitute PWT `delta` or another convenience proxy.
- Do not wait for every source to be perfect before touching the workbook: populate confirmed series, labels, links, and formula scaffolding immediately, then return to unresolved source gaps.
- If one required source or portal is blocked, continue all independent workbook steps such as other official-source retrievals, sheet linking, depreciation setup, HP-filter formula structure, and scenario formulas; leave only truly blocked cells unresolved and report them explicitly rather than substituting alternate sources or fabricated values.


### STEP 2: HP Filter in Excel
- Link data to Production sheet
- Calculate LnK and LnY
- Use Solver to minimize HP filter objective
- Get smoothed LnZ trend

- Build `LnZ` from the Cobb-Douglas residual logic implied by the workbook; do not substitute `LnK` or another input series for `LnZ`.
- Build the HP filter entirely with worksheet formulas: trend cells, residual terms, second-difference penalty terms, and one objective cell for Solver.
- Set up the HP-filter objective directly in worksheet cells using the workbook's intended trend decision range and second-difference structure.
- Actually run Excel Solver to minimize the HP objective using the designated changing cells; formula setup alone is not completion.
- Do not substitute copy-forwards, constants, placeholder formulas, scripted filtering, or pasted hard-coded trend values for the optimized Solver result.
- After Solver runs, recalculate and confirm the objective updates, the trend cells change from initialization, and HP-filter outputs are numeric and error-free before downstream production-function calculations.
- Confirm the saved workbook contains solved numeric outputs rather than initial guesses.
- Extend LnZ only from fixed historical or smoothed values. Do not use `TREND` or any self-referential or circular forecast formula over the range being generated.

- Derive `LnZ` from the workbook's Cobb-Douglas residual definition using output and factor inputs/parameters; never map `LnZ` directly from `LnK`, `LnY`, or another single input column.
- Treat Solver execution as a hard completion gate: formula setup alone is not completion. Run Solver inside Excel on the intended objective/changing cells, recalculate, and verify the trend outputs no longer reflect initialization, pass-through formulas, notes, blanks, or copied placeholders.
- Preserve the full intended HP objective structure in worksheet cells, including residual and second-difference penalty terms over the workbook's designated range; do not collapse it to a shortcut fit or replace it with copy-forwards, constants, scripted filtering, or pasted hard-coded trends.
- Keep the HP-filter objective, decision cells, penalties, and outputs in worksheet formulas or Solver-changed cells. Do not compute optimized trend values in Python or any external tool for later pasting into Excel.
- If the task specifies a particular HP-filter structure or Solver objective/changing-cell range, reproduce and use those exact cells/ranges.
- Treat HP-filter setup and Solver execution as separate required steps: build the objective and changing-cell formulas, run Solver in Excel on the task-specified objective cell and changing range, accept the solution, recalculate, and verify the changing cells differ from initialization or copied source values.
- After entering or filling HP-related formulas, inspect representative cells at the top, middle, and bottom of each critical range to confirm formulas are complete, references point to the intended cells, and trend/objective blocks remain formula-driven where the workbook design expects formulas.
- Immediately after Solver, inspect representative trend cells and dependent output cells to confirm they changed from their initial guesses and now evaluate numerically; if any `#VALUE!`, `#N/A`, `#REF!`, or similar error appears, stop extending downstream formulas and fix the broken precedents first.
- After entering HP-filter formulas and again after Solver runs, inspect representative cells to confirm valid Excel formula syntax, correct references, numeric solved outputs, and no quoted-formula or circular-reference artifacts.
- If Solver or its add-in is unavailable, preserve the in-workbook setup, complete all non-Solver work, and explicitly report the workbook as incomplete because the optimization step is blocked.


### STEP 3: Production Function
- Capital share and TREND for extension
- Ystar_base from Cobb-Douglas
- Investment shock scenario (6.5B USD, 8 years from 2026)
- Calculate impact on GDP

- Keep variable definitions consistent across steps: productivity/trend terms must remain distinct from capital terms in `Y = A × K^α × L^(1-α)`.
- Follow the workbook's requested Cobb-Douglas structure and source links; do not invent a simplified specification because some inputs seem inconvenient.
- Do not substitute historical capital stock or other required series with shortcut rules such as constant K/Y approximations unless the task explicitly permits that simplification.
- Before projecting or shocking GDP, confirm units and measurement bases are compatible across GDP, capital stock, depreciation, and investment inputs.
- After filling each formula block, inspect representative cells in every affected column to confirm references point to the intended row, column, and sheet.
- Verify the base and shocked capital/output columns separately before extending formulas through the full table.
- Apply year-extension instructions from the stated start year exactly, and use the exact specified averaging or anchoring window rather than a convenient substitute.
- Complete the workbook build: link sheets, enter depreciation and Cobb-Douglas formulas, extend trends, fill scenario outputs, and save the finished workbook.


**Execution discipline:** timebox reconnaissance. Once the workbook path, source list, and required output are known, immediately (1) open/inspect `test-supply.xlsx`, (2) map destination sheets/ranges from headers, nearby formulas, named ranges, or examples, (3) retrieve the first required source table through the mandated official path, and (4) write validated data/formulas into the workbook. Do not linger in planning mode or repeated reconnaissance once execution is authorized.

- When entering or generating formulas, read back representative cells after writing them and fix malformed quotes, text-formula artifacts, wrong-sheet references, row/column drift, unintended hardcoded strings, or blanks in required output rows before proceeding.
- Spot-check at least the first, middle, and last populated rows of each major formula block to confirm base capital, shocked capital, trend, and output columns point to the intended ranges and scenario.
- If a formula block errors, debug references, units, and source links first; do not repair the model by swapping in constants, copy-forwards, shortcut equations, or substitute assumptions unless the task explicitly authorizes that change.
- Keep productivity, output, and capital terms distinct in every formula block, and preserve the workbook's intended production-function structure and derivation paths; do not invent fallback Cobb-Douglas formulas or drop required terms because an input seems missing or inconvenient.
- If the instructed depreciation chain is ECB CFC divided by PWT capital stock, keep that chain in the workbook. Confirm numerator/denominator units and scales are compatible, check the implied depreciation rates are economically plausible, and resolve mismatches with conversions or clarified links rather than substituting PWT `delta`, a fixed assumption, or a constant K/Y shortcut unless explicitly permitted.
- Fill a small test block first, recalculate, and inspect representative formulas/results before extending across the table; when extending beyond source coverage, anchor the extension only from the workbook-approved method and validated transition year.
- When entering formulas programmatically or through bulk edits, write formulas in native Excel syntax, then reload/inspect representative cells across each edited range to confirm the stored formulas are syntactically valid and references resolve as intended before filling or saving further.
- Do not use self-referential `TREND` formulas or any forecast formula whose known_y range includes the cells being generated; extend only from completed historical or solved base ranges.


## Key Parameters

- Cobb-Douglas: Y = A × K^α × L^(1-α)
- HP filter λ = 100 for annual data
- Average K/Y as extension anchor

## Final validation

- Reopen or directly re-inspect the saved `test-supply.xlsx` after all edits.
- Recalculate and inspect critical upstream and downstream blocks: source-fed cells, depreciation inputs, HP-filter ranges, production-function outputs, and scenario/result rows.
- Treat recalculation errors as blockers, not warnings. Fix `#VALUE!`, `#REF!`, `#N/A`, circular-reference failures, blanks in required cells, stale initial values, or `NaN` outputs before finishing, or explicitly document the remaining blocker.
- Verify the intended workbook file was edited in place, required formulas remain live Excel formulas, Solver-dependent outputs are solved numeric values where required, and no critical block was replaced with pasted external/scripted results.
- Do not declare the workbook complete based only on a script run, a silent tool result, or an assumption that prior writes succeeded.
## Output

`test-supply.xlsx`


Completion checklist before finishing:
- Confirm `test-supply.xlsx` itself was opened, edited in place, saved, and re-inspected.
- Workbook recalculated with no formula errors and inspected after saving as `test-supply.xlsx`.
- Required source-fed fields use the mandated sources/methods, or any blocking gaps are clearly identified rather than silently substituted.
- Retrieved source files/tables were validated as complete and structurally correct before use; wrong or partial datasets were rejected rather than adapted into proxies.
- Depreciation formulas are completed using the specified ECB CFC ÷ PWT capital-stock chain when required, with units/year alignment reconciled or the blocker explicitly reported.
- HP filter is implemented in Excel cells and Excel Solver was actually executed when required; if not possible, Solver is explicitly reported as the blocker.
- Model cells contain valid Excel formulas/links where required, not pasted external or scripted results.
- Representative formulas were read back after writing to confirm valid syntax, correct sheet/range references, and populated required output cells.
- Production-function, trend-extension, and investment-shock scenario formulas are fully linked through to GDP impact.
- Key result cells return numeric, economically plausible outputs, and required sheets/formulas remain present when the workbook is reopened or inspected.
- All reachable workbook work was completed even if one source or tool remained blocked.
- No required native Excel action, mandated source-access method, or task protocol was deferred to the user as a next step if it was part of the requested deliverable.
- Emit any exact required completion signal as the final line if one is specified.


## Tips

- Excel formulas only (Solver for HP)
- Use TREND only where the workbook/task explicitly calls for it; do not use TREND to generate the HP-filtered `LnZ` path or any self-referential extension over the same forecast range.
- Link data across sheets

- Prefer simple, validated official download or export paths; after repeated partial or snippet results, switch to the official portal/database workflow instead of refining the same search.
- Recalculate after each major edit and inspect representative cells before filling formulas across large ranges.
- Verify references, ranges, and syntax after formula edits; do not embed a quoted formula string inside another formula.
- Do not hardcode values for cells that should be formula-driven or replace required Excel operations with copied values or off-workbook calculations.
- Keep annotations out of calculation blocks; overwriting even one model cell can corrupt downstream results.
- Treat any `#VALUE!`, `#REF!`, `#N/A`, or similar error as a blocker until resolved or explicitly reported.
- Do a magnitude and plausibility check after linking series and projections (for example, depreciation rates should be reasonable and capital paths should not turn implausibly negative from unit mismatch).
- Before declaring completion, reopen or inspect `test-supply.xlsx` and confirm formulas remain formulas, linked ranges point to the intended cells/sheets, Solver-dependent outputs are present, and key model areas are populated consistently.

- Keep a strict source-to-cell chain: retrieve complete official series -> validate year coverage, units, and variable identity -> enter into workbook -> recalculate -> inspect linked outputs.
- Cap unproductive source hunting: after one or two failed snippet/search attempts, switch to direct official download/API/export and move on to extraction.
- Avoid long scraper-rewrite loops on dynamic portals. After one or two failed or partial attempts, switch to a confirmed official download/export/query path within the mandated source family.
- Use successful retrievals as checkpoints: parse, map to workbook columns, enter data, and save progress before gathering the next series.
- For workbook tasks, measure progress by saved changes in `test-supply.xlsx`, not by downloads completed or notes written.
- Recalculate after each major edit and inspect representative cells before filling formulas across large ranges.
- For formula-heavy sheets, enter or adjust a few representative formulas first, recalculate, inspect the exact formula text and cell references, then fill the rest only after those checks pass.
- Verify references, ranges, and syntax after formula edits; do not embed a quoted formula string inside another formula.
- For reproducible model areas, preserve formulas and links after editing; never convert a calculation block to pasted constants just to make optimization or debugging easier.
- When writing formulas at scale, sanity-check representative saved cells in both formula view and normal view to confirm the workbook contains valid Excel formulas, not malformed strings or truncated expressions.
- Do not hardcode values for cells that should be formula-driven or replace required Excel operations with copied values or off-workbook calculations.
- Keep annotations out of calculation blocks; overwriting even one model cell can corrupt downstream results.
- Treat any `#VALUE!`, `#REF!`, `#N/A`, or similar error as a blocker until resolved or explicitly reported.
- When debugging workbook errors, trace precedents/dependencies systematically from the first failing cell; do not keep filling downstream sheets while upstream calculation errors remain.
- Do a magnitude and plausibility check after linking series and projections (for example, depreciation rates should be reasonable and capital paths should not turn implausibly negative from unit mismatch).
- Before declaring completion, reopen or inspect `test-supply.xlsx` and confirm formulas remain formulas, linked ranges point to the intended cells/sheets, Solver-dependent outputs are present, and key model areas are populated consistently.
- Never describe the workbook as complete if any mandatory step is still effectively pending, such as unresolved official-series retrieval, required Solver execution, or post-save validation.

