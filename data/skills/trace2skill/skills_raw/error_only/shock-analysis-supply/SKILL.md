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


## Multi-Step Process

**Before editing the workbook:** inspect existing sheets, headers, named areas, formulas, and occupied ranges. Verify target-column mapping from headers or example rows before entering data, especially when a field is unlabeled, then proceed to populate `test-supply.xlsx` rather than stopping at reconnaissance.


### STEP 0: Workflow and source validation
- Confirm allowed tools, application restrictions, and any required completion signal before doing anything else.
- Open `test-supply.xlsx` early and work toward sheet completion, not just data reconnaissance.
- For each required external series, obtain the full year-by-year table from the specified official source before entering values or formulas.
- After every download or API call, confirm it is the expected dataset and format by checking file type, sheet names, headers, visible keys, and that it is not an HTML/error page.

### STEP 1: Data Collection
- PWT database from Groningen
- IMF WEO for real GDP
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


## Key Parameters

- Cobb-Douglas: Y = A × K^α × L^(1-α)
- HP filter λ = 100 for annual data
- Average K/Y as extension anchor

## Output

`test-supply.xlsx`


Completion checklist before finishing:
- Confirm `test-supply.xlsx` itself was edited and saved.
- Workbook recalculated with no formula errors and inspected after saving as `test-supply.xlsx`.
- Required source-fed fields use the mandated sources, or any blocking gaps are clearly identified.
- Depreciation formulas are completed using the specified source/formula chain.
- HP filter is implemented in Excel cells and Excel Solver was actually executed.
- Model cells contain valid Excel formulas/links where required, not pasted external results.
- Production-function, trend-extension, and investment-shock scenario formulas are fully linked through to GDP impact.
- Key result cells return numeric, economically plausible outputs, and required sheets/formulas remain present when the workbook is reopened or inspected.
- All reachable workbook work was completed even if one source or tool remained blocked.
- Emit any exact required completion signal as the final line if one is specified.


## Tips

- Excel formulas only (Solver for HP)
- Use TREND for projection
- Link data across sheets

- Prefer simple, validated official download or export paths; after repeated partial or snippet results, switch to the official portal/database workflow instead of refining the same search.
- Recalculate after each major edit and inspect representative cells before filling formulas across large ranges.
- Verify references, ranges, and syntax after formula edits; do not embed a quoted formula string inside another formula.
- Do not hardcode values for cells that should be formula-driven or replace required Excel operations with copied values or off-workbook calculations.
- Keep annotations out of calculation blocks; overwriting even one model cell can corrupt downstream results.
- Treat any `#VALUE!`, `#REF!`, `#N/A`, or similar error as a blocker until resolved or explicitly reported.
- Do a magnitude and plausibility check after linking series and projections (for example, depreciation rates should be reasonable and capital paths should not turn implausibly negative from unit mismatch).
- Before declaring completion, reopen or inspect `test-supply.xlsx` and confirm formulas remain formulas, linked ranges point to the intended cells/sheets, Solver-dependent outputs are present, and key model areas are populated consistently.

