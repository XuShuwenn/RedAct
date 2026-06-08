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
- Use Excel only. Do **not** use Python, openpyxl, pandas, scripts, shell commands, or external workbook-generation tools to inspect, create, or modify the workbook.
- Edit the provided workbook/template in place and preserve its layout, formulas, and required sheet names unless the task explicitly instructs otherwise; do **not** create a replacement workbook from scratch.
- Keep calculated cells formula-driven in Excel. Only true assumptions may be entered as fixed inputs; do **not** hardcode values that should come from source data, links, or formulas.
- Use the required authoritative sources only: IMF WEO for GDP data and Geostat for Georgia supply/use tables.
- If required source data, mappings, or workbook prerequisites cannot be accessed, validated, or fully retrieved, stop and report the blocker clearly rather than substituting search snippets, proxies, guessed values, placeholders, invented sheets, or dummy rows.
- Save the final deliverable with the exact filename: `test_demand.xlsx`.
- If the environment or task requires a completion token, output it verbatim at the end.


## Workflow

### STEP 1: Data Collection
- Pull required GDP and related series directly from the IMF WEO database and populate `WEO_Data` with the actual source data.
- Verify each WEO series by both subject code and indicator label/units before linking it into the workbook.
- For GDP deflator, use the actual deflator series (`NGDP_D`), not nominal GDP current-price series such as `NGDPD`.
- Obtain Georgia supply/use tables from the official Geostat source workbook and use the required SUT data from the official source.
- Verify downloaded source files are real, usable tables/workbooks before relying on them.
- Verify the exact Geostat SUT file/year before using it; use the latest available complete official table rather than assuming a newer year exists.
- Keep a clear mapping from each populated input to its source sheet/table.
- Populate workbook inputs from directly extracted/downloaded source data; do not use search snippets, summaries, scraped fragments, manually guessed tables, or invented historical/forward values as substitutes.
- If one official access path fails, try another compliant official path. If required IMF WEO or Geostat source data still cannot be retrieved, treat that as a blocking issue rather than filling proxies, assumed series, placeholder SUT values, growth rates, or dummy rows.
- Extend growth rates to 2043 only after the source series are loaded and traceable, using in-sheet formulas/assumptions so downstream sheets stay linked.

### STEP 2: NA Framework
- Link WEO data to NA sheet
- Assumptions:
  - Exchange rate: 2.746 Lari/USD
  - Demand multiplier: 0.8
  - Project allocation: bell shape


- Inspect the existing workbook template first and preserve its structure unless the task explicitly requires additions.
- Map the existing template sheets, labels, destination cells, and ranges before entering formulas, and keep references aligned to the original layout.
- Put scalar assumptions in dedicated input cells, then reference those cells from formulas.
- Link required `WEO_Data` fields into `NA`, and link `SUT Calc` inputs from the actual supply/use tables rather than proxy percentages or assumed shares unless the task explicitly tells you to assume them.
- Confirm every explicit task parameter before filling formulas: start year, project length, allocation shape, exchange rate, multiplier, and deflator choice.
- Confirm series semantics before writing formulas: if the sheet says `Real GDP`, do not fill it with nominal GDP converted by exchange rate.
- Use the GDP deflator as the investment deflator as instructed, deriving real series consistently from nominal and deflator inputs.
- Populate the existing template ranges/columns in place; do **not** replace them with a custom summary table or invent row mappings from partial inspection.
- Fill the requested `SUT Calc` and `NA` structures completely, not just example rows or placeholders.
- Make any necessary structural changes before writing dependent formulas; avoid late insertions that can shift references.
- Sanity-check key linked values before proceeding: `Total Output`, `GFCF`, import share, and year alignment must be economically plausible and not accidentally linked to the wrong source cells.


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



### STEP 0: Preflight and Execution Rules
- Open the existing workbook first and map the actual sheet names, headers, merged cells, year columns, and input/output areas before writing formulas.
- Identify hard constraints before editing: allowed tools, required output filename, required completion token, required source files, and whether the supplied workbook must be preserved.
- Confirm the required sheets, headers, columns, and expected structure exist before data collection or modeling.
- If the workbook structure differs from the task description (missing, hidden, or renamed sheets), treat it as a blocking discrepancy to resolve from the available workbook/files first; do **not** invent replacement sheets or guessed cell mappings.
- Retrieve and verify the actual required source files before modeling; if the IMF WEO data, Geostat SUT workbook, or expected template sheets are missing or inaccessible, stop and report the blocker rather than creating substitutes.
- Preserve the existing layout unless the task explicitly tells you to change it.
- Once the needed workbook structure and required WEO/SUT inputs are identified, stop exploring and complete the workbook.
- Before finishing, confirm the workbook filename is exactly `test_demand.xlsx`, required sheets/scenarios are present, and validation mismatches are fixed or clearly explained rather than ignored.


## Output

`test_demand.xlsx` with:
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

