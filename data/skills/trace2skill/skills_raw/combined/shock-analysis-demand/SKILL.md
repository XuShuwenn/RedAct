---
name: shock-analysis-demand
description: "Estimate investment spending shock impact on small open economy using demand-side macro accounting framework in Excel."
---

# Demand-Side Shock Analysis

## When to Use

- Analyze investment spending shocks
- Use Supply-Use tables (SUT) framework
- Model small open economy (Georgia)

## Non-Negotiable Constraints

- Follow any task-specific protocol exactly. If the task prescribes allowed tools, a response format, or a final completion token, use that literal protocol throughout.
- Before taking any action, align your method to the task's exact execution contract: allowed tools, required workbook file, required message/action format, exact output filename, and any required completion token are binding requirements.
- Design the workflow around those constraints before doing any source lookup or workbook work, and use any required final token/message literally.
- Use Excel only. Do **not** use Python, openpyxl, pandas, scripts, shell commands, or external workbook-generation tools to inspect, create, or modify the workbook.
- Treat the Excel-only rule as a hard stop: perform inspection, mapping, data entry, formulas, recalculation, validation, and saving inside Excel only.
- If the environment cannot complete the required workbook operations through Excel, stop and report that blocker; do **not** switch to Python, scripts, shell tools, external parsers, or programmatic workbook generation even as a temporary workaround.
- Edit the provided workbook/template in place and preserve its layout, formulas, and required sheet names unless the task explicitly instructs otherwise; do **not** create a replacement workbook from scratch.
- Treat the provided workbook as the authoritative deliverable base: open that file first, preserve its existing structure, and finish by saving the edited artifact exactly as `test_demand.xlsx`.
- Do **not** hand off a scaffold, near-complete workbook, rebuilt template, parallel workbook, or substitute deliverable.
- Do **not** delete and recreate required template sheets to work around formatting, merged cells, or formula issues unless the task explicitly authorizes that change.
- Keep calculated cells formula-driven in Excel. Only true assumptions may be entered as fixed inputs; do **not** hardcode values that should come from source data, links, or formulas.
- Use the required authoritative sources only: IMF WEO for GDP data and Geostat for Georgia supply/use tables.
- If required source data, mappings, or workbook prerequisites cannot be accessed, validated, or fully retrieved, stop and report the blocker clearly rather than substituting search snippets, proxies, guessed values, placeholders, invented sheets, or dummy rows.
- Treat official-source retrieval as a gate for source-driven cells: populate the workbook only from retrieved IMF WEO and Geostat tables/workbooks or from explicit task instructions.
- Do **not** replace required inputs with Article IV tables, press releases, search-result snippets, navigation pages, related IMF pages, representative values, guessed SUT shares, fabricated source sheets, placeholder structures, dummy product rows, or self-made estimates.
- Do not downgrade the task into a scaffold or "ready for later population" template. If required official data or mappings remain unresolved after trying another compliant official path, stop and report the blocker.
- Save the final deliverable with the exact filename: `test_demand.xlsx`.
- If the environment or task requires a completion token, output it verbatim at the end.


## Workflow

### STEP 1: Data Collection
- Do **not** populate source-dependent workbook areas until the required IMF WEO series and Geostat SUT tables are actually retrieved and verified.
- Pull required GDP and related series directly from the IMF WEO database and populate `WEO_Data` with the actual source data.
- Verify each WEO series by both subject code and indicator label/units before linking it into the workbook.
- Record the exact matched WEO code plus label/units for each required series before filling cells; if the code semantics do not match the workbook field, stop and correct the mapping before writing downstream formulas.
- For GDP deflator, use the actual deflator series (`NGDP_D`), not nominal GDP current-price series such as `NGDPD`.
- If the required IMF WEO deflator series cannot be retrieved from a compliant IMF path, do not substitute another provider or another indicator; treat that as a blocking issue.
- Obtain Georgia supply/use tables from the official Geostat source workbook and use the required SUT data from the official source.
- When the task requires actual official `SUPPLY` and `USE` sheets to be copied into the workbook, transfer them from the official file and preserve the original sheet names exactly; never create empty or synthetic replacement sheets with those names.
- If the official Geostat SUT workbook cannot be accessed or verified, stop and report the blocker instead of deriving aggregates, representative shares, or dummy `SUT Calc` content.
- Verify downloaded source files are real, usable tables/workbooks before relying on them.
- Before populating workbook cells, confirm the actual IMF WEO extract and official Geostat SUT workbook/table are open, readable, and usable.
- If a supposed download opens as HTML, a landing page, or other non-tabular content, reject it immediately, try another compliant official path, and do not keep using the invalid file as if it were the dataset.
- Verify actual source workbook/table names before claiming to copy from them.
- Verify the exact Geostat SUT file/year before using it; use the latest available complete official table rather than assuming a newer year exists.
- Record the exact official SUT workbook year actually retrieved and use only that verified file in downstream formulas; do **not** assume a newer unpublished year exists from naming patterns or stray links.
- Keep a clear mapping from each populated input to its source sheet/table.
- Populate workbook inputs from directly extracted/downloaded source data; do not use search snippets, summaries, scraped fragments, manually guessed tables, or invented historical/forward values as substitutes.
- If one official access path fails, try another compliant official path. If required IMF WEO or Geostat source data still cannot be retrieved, treat that as a blocking issue rather than filling proxies, assumed series, placeholder SUT values, growth rates, or dummy rows.
- Limit source hunting to a small number of distinct official retrieval attempts per source. If retrieval still fails, stop workbook population that depends on it and report the blocker clearly.
- Do not use search-result snippets, page summaries, AI summaries, manually compiled stand-ins, or alternate databases as substitutes for the required official tables.
- Extend growth rates to 2043 only after the source series are loaded and traceable, using in-sheet formulas/assumptions so downstream sheets stay linked.
- Before populating model cells, complete an anchor mapping check for year headers, row labels, units, and exact source coordinates for at least GDP, GDP deflator, `Total Output`, and `GFCF`.
- Only extend beyond source years from explicit in-workbook assumption/formula cells after the official historical/source span is loaded and traceable; never backfill missing source history or baseline source series with estimates.

### STEP 2: NA Framework
- Link WEO data to NA sheet
- Assumptions:
  - Exchange rate: 2.746 Lari/USD
  - Demand multiplier: 0.8
  - Project allocation: bell shape


- Inspect the existing workbook template first and preserve its structure unless the task explicitly requires additions.
- Map the existing template sheets, labels, destination cells, and ranges before entering formulas, and keep references aligned to the original layout.
- Put scalar assumptions in dedicated input cells, then reference those cells from formulas.
- Enter only raw sourced values and explicit scalar assumptions as constants. Any derived paths, allocations, import-content calculations, scenario outputs, or macro results must remain worksheet formulas linked to visible input/source cells.
- Link required `WEO_Data` fields into `NA`, and link `SUT Calc` inputs from the actual supply/use tables rather than proxy percentages or assumed shares unless the task explicitly tells you to assume them.
- Confirm every explicit task parameter before filling formulas: start year, project length, allocation shape, exchange rate, multiplier, and deflator choice.
- Confirm series semantics before writing formulas: if the sheet says `Real GDP`, do not fill it with nominal GDP converted by exchange rate.
- For any `Real GDP` field, derive the real series consistently from nominal GDP and the GDP deflator as instructed; do not use exchange-rate conversion of nominal GDP as a proxy for real GDP.
- Use the GDP deflator as the investment deflator as instructed, deriving real series consistently from nominal and deflator inputs.
- Populate the existing template ranges/columns in place; do **not** replace them with a custom summary table or invent row mappings from partial inspection.
- Populate the requested `SUT Calc` and `NA` structures the template expects, including source-linked ranges, not just simplified totals or a custom substitute table.
- Do not create or claim source-derived sheets such as `SUPPLY` or `USE` unless they were actually retrieved from the official source workbook or explicitly required by the provided template.
- Fill the requested `SUT Calc` and `NA` structures completely, not just example rows or placeholders.
- Make any necessary structural changes before writing dependent formulas; avoid late insertions that can shift references.
- Sanity-check key linked values before proceeding: `Total Output`, `GFCF`, import share, and year alignment must be economically plausible and not accidentally linked to the wrong source cells.

- If the task specifies an 8-year project beginning in 2026, ensure the allocation spans 2026 through 2033 inclusive and that the bell-shape weights sum to 100% across those eight years before linking outputs.


### STEP 3: Scenarios
1. Base: demand multiplier 0.8, import share from SUT
2. Scenario 2: demand multiplier 1.0
3. Scenario 3: import content share 0.5


- Keep scenarios in the required structure on the `NA` sheet if the template expects them there; do not move them to newly created scenario sheets unless the workbook already uses that design.
- Build scenario variants by changing designated assumption/input cells and letting downstream formulas recalculate; do **not** hardcode scenario outputs.
- Before writing any SUT-linked formula, verify the source sheet coordinates, headers, and totals from the official source/workbook labels; do not rely on guessed cell addresses.
- Create scenario blocks with references designed for each block; do not rely on blind copy/paste that leaves formulas pointing back to Scenario 1.
- After creating each scenario, verify that internal references point to the intended rows/columns for that scenario.
- Carry every scenario and supporting `NA` formulas through 2043, matching the extended WEO horizon exactly.

- Start scenario construction only after upstream `WEO_Data` and SUT-linked inputs are complete through every required year.
- If the template/task specifies scenarios on the existing `NA` sheet, place them there in the required block layout; do **not** create substitute sheets such as `NA_Scenario2` or `NA_Scenario3` unless the workbook already uses that design.
- Build each scenario block from designated assumption cells and scenario-local references. After any copy/fill step, audit several formulas to confirm they do not still point back to Base or another scenario by accident.
- After filling each scenario block, verify the first and last year labels and confirm formulas extend through 2043 rather than stopping one year early.



### STEP 0: Preflight and Execution Rules
- Open the existing workbook first and map the actual sheet names, headers, merged cells, year columns, and input/output areas before writing formulas.
- Before editing any cell, confirm the exact workbook you are modifying, whether it already is the deliverable or needs a final save/rename step to become `test_demand.xlsx`, and what file you will return.
- Record the observed sheet names and inspect for hidden or renamed sheets before deciding any required structure is missing.
- If the task references specific cells, columns, ranges, or scenario blocks, locate and confirm those exact destinations in the workbook before entering data or formulas.
- Identify hard constraints before editing: allowed tools, required output filename, required completion token, required source files, and whether the supplied workbook must be preserved.
- Confirm the required sheets, headers, columns, and expected structure exist before data collection or modeling.
- Do not start populating `WEO_Data`, `SUT Calc`, or `NA` until the actual IMF WEO dataset/table and official Geostat SUT workbook/table are retrieved or otherwise verified as usable source files.
- If the provided workbook has fewer or different sheets than expected, inspect companion files and hidden/renamed sheets first. If the required structure still cannot be mapped clearly, stop and report the blocker rather than creating replacement template sheets or guessed mappings.
- If the workbook structure differs from the task description (missing, hidden, or renamed sheets), treat it as a blocking discrepancy to resolve from the available workbook/files first; do **not** invent replacement sheets or guessed cell mappings.
- Retrieve and verify the actual required source files before modeling; if the IMF WEO data, Geostat SUT workbook, or expected template sheets are missing or inaccessible, stop and report the blocker rather than creating substitutes.
- Preserve the existing layout unless the task explicitly tells you to change it.
- Once the needed workbook structure and required WEO/SUT inputs are identified, stop exploring and complete the workbook.
- Before finishing, confirm the workbook filename is exactly `test_demand.xlsx`, required sheets/scenarios are present, and validation mismatches are fixed or clearly explained rather than ignored.

- Preflight order is mandatory: confirm protocol/tool constraints, inspect the workbook structure in Excel, retrieve and validate the official source files, then populate formulas and scenarios.
- Once workbook structure, source files, and destination mappings are confirmed, stop extended exploration and move directly to populating the workbook; avoid spending the session only on source hunting or inspection.


## Output

`test_demand.xlsx` with:
Use the edited provided workbook as this deliverable; do not generate a new workbook file with a custom structure.
- WEO_Data sheet
- SUT Calc sheet
- NA sheet with scenarios

Before declaring completion, verify:
- the saved file uses this exact name and is the edited task workbook, not a newly generated substitute;
- `WEO_Data`, `SUT Calc`, and `NA` are present and populated;
- `NA` contains Base, Scenario 2, and Scenario 3;
- linked series and scenarios run through 2043 where required;
- calculated cells use Excel formulas rather than pasted constants;
- key formulas/links recalculate without broken references or obvious errors.


## Final Checks

- Do not treat a successful save, file timestamp, file size change, recalc, zero formula errors, or file existence alone as proof of completion.
- Run a delivery audit immediately before finishing: the edited provided workbook is saved and reopened as `test_demand.xlsx`, required sheets and scenarios are present and populated, source-driven cells trace to retrieved official IMF/Geostat data, and the workbook is fully populated rather than a scaffold with placeholders or "verify later" notes.
- Inspect a sample of critical cells in `WEO_Data`, `SUT Calc`, and each scenario block in `NA` to confirm sourced values come from retrieved official data and calculated cells remain formulas rather than pasted estimates or convenience constants.
- Audit a few critical formula cells by address to confirm no copied references point to the wrong scenario/block and no helper or scratch formulas landed in active modeled ranges.
- After any late-stage formula, unit, or mapping fix, recalculate, save, reopen the workbook, and re-check the corrected key outputs before declaring completion.
- Check the final required year explicitly on linked series and scenario ranges to confirm 2043 coverage is complete.
- If any required source, mapping, workbook mismatch, or protocol requirement remains unresolved, report that blocker clearly instead of presenting a guessed or substitute completed workbook.

## Final Checks
- Confirm WEO and SUT inputs come from retrieved official source data, not placeholders or invented numbers.
- Confirm source-dependent cells are linked to source sheets/tables where required.
- Confirm calculations remain in Excel formulas; only raw sourced inputs and explicit assumption cells may be constants.
- Recalculate after any formula, mapping, or unit fix, and trace workbook errors back to missing source data or broken references first.
- Confirm scenario assumptions match the specification and differ only through intended assumption changes.
- Audit a few critical cross-sheet references, year endpoints, and scenario ranges to ensure no copied formulas point to the wrong block.
- Reopen and directly verify the workbook end to end before completion; file existence or recalculation alone is not sufficient.
- If any required source could not be obtained, state that clearly instead of presenting a fully complete workbook.

## Tips

- Use Excel formulas only; do not use Python or other code as a fallback.
- GDP deflator as investment deflator
- HP filter for trend extraction
- Validate source-sheet mappings first, then scale the model to additional scenarios.
- Do not create named sheets just because the instructions mention them; first verify whether they already exist, are hidden, or are differently named.
- Search-result snippets or page summaries are not enough; obtain the actual source datasets/tables needed for the workbook.
- Preserve the template structure: do not insert/delete rows or columns unless the task explicitly requires it.
- If a ratio or result looks implausible, audit the source links and year mappings before changing formulas.
- Prefer the simplest viable official-data ingestion path, then return to workbook population promptly.
- Before claiming completion, cross-check that sheet names, target cells, and formula references still match the original template and that populated values come from source links/formulas rather than manual stand-ins.

