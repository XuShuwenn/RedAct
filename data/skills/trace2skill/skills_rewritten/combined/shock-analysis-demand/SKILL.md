---
name: shock-analysis-demand
description: "Estimate investment spending shock impact on small open economy using demand-side macro accounting framework in Excel."
---

# Demand-Side Shock Analysis

## When to Use

- Analyze investment spending shocks
- Use Supply-Use tables (SUT) framework
- Model small open economy (Georgia)

- Treat the runtime/interface execution contract as a hard requirement equal to the workbook requirements: if the environment specifies an exact action/tool schema, required JSON fields, allowed action types or tool names, executable command style, observation loop, or a literal completion signal, use that exact format on every step and at the end.
- Mirror the required execution format exactly from the first step through the final response. Do **not** improvise alternate tool names, malformed calls, wrappers, pseudo-calls, XML tags, markdown stand-ins, or paraphrased completion text.
- Before any inspection or retrieval, convert the execution contract into a short working checklist: allowed tools/interfaces, required action syntax, workbook to edit, exact save filename, whether external official data is actually required, any path requirements, and the exact completion token/message.
- Use only concrete executable actions supported by the environment; do **not** submit placeholder commands or prose stand-ins that merely describe an intended outcome instead of performing a verifiable action.
- Do **not** reference or invoke tools that are not explicitly available in the current environment. If a required operation cannot be performed with the allowed interface, stop and report that blocker.
- Before any file access, confirm the artifact type and use only operations appropriate to it. Do **not** treat `.xlsx` workbooks as generic text/binary files, and do not attempt unsupported tooling or ad hoc installs to recover from a wrong tool choice.
- Treat workbook inspection result as higher priority than template expectations. If inspection shows fewer/different sheets, ranges, or layouts than expected, re-map from observed evidence or report the mismatch as a blocker; do **not** assume missing sheets should be created.
- Treat incomplete inspection as a hard stop for source-dependent edits. If workbook previews, source tables, or downloaded files are truncated, empty, unreadable, or only partially inspected, confirm the exact sheet names, headers, labels, and needed cells before writing formulas or transformations.
- Never insert fallback numeric defaults, guessed coordinates, inferred source values, or convenience stand-ins for missing evidence. If a required year, row, sheet, download, or source cell is not explicitly verified, resolve it or report a blocker instead of filling placeholders.
- Treat observed tool output and direct workbook inspection as authoritative. Do **not** claim workbook edits, created sheets, copied source tabs, populated values, formulas, or saved filenames unless you directly observed them after the edit.
- Treat action success as unproven until the expected result is visibly confirmed. If a tool call fails, returns truncated output, or does not show the expected inspection/edit result, rerun a narrower compliant action and verify before reasoning from it.
- Do **not** infer workbook structure, missing/present sheets, source-file contents, or task progress from failed inspections, partial logs, missing readback output, or unsupported-tool errors.
- Do not present a workbook as "ready," "prepared," or "set up" when required official-source data population is still unfinished. The only acceptable outcomes are a completed `test_demand.xlsx` or a clear blocker report.
- Treat protocol drift as task-failing even if workbook edits succeed, and reserve any literal completion signal for the very end only after save/reopen/validation.## Non-Negotiable Constraints

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

- Treat explicit tool feedback that required source data is still missing, unverified, unreadable, or absent from the retrieved page/file as a hard blocker for source-dependent workbook work. Try another compliant official retrieval path immediately or stop and report the blocker; do **not** continue with template building, summaries, formula scaffolding, or convenience values as a substitute.
- If required official data retrieval still fails after a small number of compliant attempts, stop workbook population entirely and report the blocker. A workbook is **not** complete if required official IMF/Geostat values are still missing from required populated ranges, even if sheet structure, formulas, and scenario blocks exist.

- Treat official-source retrieval as a gate for source-driven cells: populate the workbook only from retrieved IMF WEO and Geostat tables/workbooks or from explicit task instructions.
- Do **not** replace required inputs with Article IV tables, press releases, search-result snippets, navigation pages, related IMF pages, representative values, guessed SUT shares, fabricated source sheets, placeholder structures, dummy product rows, or self-made estimates.
- Do not downgrade the task into a scaffold or "ready for later population" template. If required official data or mappings remain unresolved after trying another compliant official path, stop and report the blocker.
- Save the final deliverable with the exact filename: `test_demand.xlsx`.
- If the environment or task requires a completion token, output it verbatim at the end.

- Start by extracting the literal execution contract from the task/system instructions: required action/message format, allowed tools and interface names, allowed paths/directories, workbook to edit, exact deliverable filename, whether external official data retrieval is actually required, and any mandatory completion token.
- Treat the runtime/interface execution contract as a hard requirement equal to the workbook requirements: if the environment specifies an exact action/tool schema, required JSON fields, allowed action types or tool names, executable command style, observation loop, or a literal completion signal, use that exact format on every step and at the end.
- Use only concrete executable actions supported by the environment; do **not** submit placeholder commands or prose stand-ins that merely describe an intended outcome instead of performing a verifiable action.
- Do **not** reference or invoke tools that are not explicitly available in the current environment. If a required operation cannot be performed with the allowed interface, stop and report that blocker.
- Treat observed tool output and direct workbook inspection as authoritative. Do **not** claim workbook edits, created sheets, copied source tabs, populated values, formulas, or saved filenames unless you directly observed them after the edit.
- Do **not** assume this skill's default workbook structure or data-fetch workflow applies unless the current task explicitly requires it. When the workbook appears simpler or different than expected, verify from the task text and the actual workbook whether only the existing structure should be edited rather than inferring missing sheets must be created.
- Do **not** ask the user for confirmation, missing files, or manual data entry if the task expects autonomous execution and the workspace or official sources still offer compliant next steps.
- Do not let inspection, planning, or source hunting consume the whole session: once the workbook structure is mapped and usable required inputs are available, switch immediately to populating the workbook.
- If the task/environment specifies an exact completion signal or final message format, output it exactly as required at the end; do **not** replace it with prose, a paraphrase, or extra text.


## Workflow

### STEP 0.5: Requirement capture before any search or edit
- Before inspecting files, browsing sources, or editing cells, state the concrete completion target to yourself: required workbook, required sheets/blocks to populate, required official sources, exact output filename, and any completion token.
- Identify which workbook areas are source-dependent (`WEO_Data`, `SUT Calc`, `NA`) and do **not** edit those areas until their required official inputs are retrieved and verified.
- Tie each external lookup to a specific required workbook field or sheet; if a search does not advance a required input, stop that search path.

- Also capture the runtime execution contract verbatim: required per-step action/message structure, exact allowed tool names/interfaces, required JSON fields if any, and the literal final completion signal.
- Convert the task requirements into a short working checklist before any search/edit: exact workbook to edit, exact sheets/ranges to populate, required official sources, exact output filename, exact allowed tool/action syntax, required scenarios, and any required completion token/message.
- Distinguish **task-required** actions from **skill-default** possibilities. If the task does not clearly require rebuilding template structure, copying source tabs, or fetching external IMF/Geostat data, do not assume those steps are mandatory.
- Read all task-visible instruction sources before broad search or modeling: the prompt, any embedded workbook notes/instruction sheet, and enough of each relevant workbook area to identify the exact required outputs, formulas, scenarios, and final completion signal.
- Extract deliverable requirements from evidence before implementation: required sheets, scenario blocks, source tabs, formulas, and assumptions must come from the task instructions or direct workbook inspection, not from this skill alone.
- If the workbook/task evidence does not establish that a sheet such as `WEO_Data`, `SUT Calc`, `NA`, `SUPPLY`, or `USE` must exist, do **not** create or claim it yet; first confirm from the workbook or task text.
- Include the exact required final completion token/string in the requirement-capture checklist and reserve it for the final response only.

### STEP 0.6: Workbook-First Inspection
### STEP 0.7: Commit to the next concrete action
- After workbook inspection, choose the next concrete step immediately: edit an identified target range, retrieve one specific missing official input, or report a blocker. Do **not** remain in open-ended investigation.
- If the workbook already exposes the required target ranges and enough verified inputs exist for the next block, switch directly to editing in Excel rather than continuing exploratory source checks.
- If repeated official-source attempts are failing, stop expanding the search after the bounded cutoff and decide explicitly: continue with supported local workbook work that is truly independent of the missing data, or issue a blocker report.
- After opening the workbook, inspect actual cell content on the relevant sheet(s) before any broad web retrieval: read titles, row labels, year headers, scenario labels, assumptions, and any existing formulas or placeholders.
- Do not infer workbook needs from sheet names alone. Determine from in-file evidence what `WEO_Data`, `SUT Calc`, `NA`, scenarios, and source mappings the template expects.
- If the workbook has only one visible sheet or an unexpected structure, inspect that sheet thoroughly first, then check for hidden/renamed sheets; only after that should you decide whether external source retrieval is necessary.
- Do **not** begin broad IMF/Geostat searching immediately after learning sheet names alone; first read the actual worksheet contents well enough to identify the workbook's expected fields, mappings, and missing inputs.

- Begin inspection with the local workspace, not the web: locate the target workbook and check for companion source files/templates already present. Do not start external retrieval while the workbook to edit is still unverified.
- Record the observed workbook state immediately after opening: actual visible sheet names, any hidden sheets found, whether expected target sheets truly exist, and the key headers/labels in the target areas. Use that observed inventory to decide the next step.
- Inspection must produce observable evidence of workbook structure before any population step: confirm actual sheet names, representative headers/labels, key target ranges, year boundaries, and any merged/protected areas from the workbook itself.
- If inspection output is truncated, ambiguous, or initially shows only one visible sheet, resolve that first by inspecting the visible sheet thoroughly plus any hidden/renamed sheets. Do **not** conclude that `WEO_Data`, `SUT Calc`, extra scenario sheets, or a rebuilt model must be created from sheet count alone.
- Before any bulk population or scenario construction, turn the inspected workbook/task requirements into a concrete destination map: required sheets, exact scenario block locations, key input rows, year columns, and any mandated assumption-cell placement. Do **not** start building or copying blocks until this map is specific enough to name where each required output goes.
- If the observed sheet inventory or in-sheet structure contradicts the task/template assumptions and you cannot resolve it from the workbook or companion files, stop before population and report the discrepancy instead of proceeding on the assumed template design.
- Limit source hunting to a small number of distinct official retrieval attempts per source. Treat near-duplicate searches, repeated dead links, repeated 404/HTML responses, or snippet-only results as one failed retrieval pattern. Change to a different compliant official path once; if that also fails, stop workbook population that depends on it and report the blocker clearly.
- Use a bounded escalation sequence for official-source retrieval when the first fetch is incomplete: inspect the returned official page for the true download target, try a direct official download/export endpoint, then try another official dataset page or machine-readable official path before declaring a blocker.
- Search snippets, AI/search summaries, result-page previews, overview pages, Article IV writeups, zero-byte files, blank files, and superficially fetched downloads may help locate the official page, but they are never acceptable source values for workbook population. Populate source-driven cells only from the opened official IMF WEO dataset/table or official Geostat workbook/table itself.
- Do not treat partial snippet agreement, inferred values, or "enough to proceed" reasoning as source verification. If the full inspectable official table/workbook is not open and readable, the source is still unresolved.### STEP 1: Data Collection
- Do **not** populate source-dependent workbook areas until the required IMF WEO series and Geostat SUT tables are actually retrieved and verified.
- Treat source retrieval as a hard gate for downstream modeling: do **not** create, extend, or partially populate `WEO_Data`, `SUT Calc`, `NA`, or scenario formulas from guessed, partial, blank, or placeholder upstream values.
- Treat repeated failed downloads, unreadable files, landing pages, or snippet-only evidence as unresolved retrieval, not as usable source data. If repeated official-source retrieval attempts still do not yield usable IMF WEO or Geostat tables, stop workbook population and report the blocker instead of building a provisional model on incomplete inputs.
- Pull required GDP and related series directly from the IMF WEO database and populate `WEO_Data` with the actual source data.
- Verify each WEO series by both subject code and indicator label/units before linking it into the workbook.
- Record the exact matched WEO code plus label/units for each required series before filling cells; if the code semantics do not match the workbook field, stop and correct the mapping before writing downstream formulas.
- Before using any populated source column in downstream formulas, read back the destination cells and verify they match the intended source code, label, units, and 1-2 sample year values. Treat any mismatch as a stop-and-fix issue before building `NA` or scenarios.
- For commonly confused GDP fields, explicitly confirm the destination deflator cells contain `NGDP_D` index values rather than nominal-GDP level values such as `NGDPD`.
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

- Use web search only to locate the official IMF and Geostat source pages. Do **not** treat search-result snippets, AI/search summaries, highlighted preview values, or navigation-page text as workbook-ready data.
- Use targeted retrieval only for specific gaps discovered from workbook inspection; do **not** begin with broad exploratory searching.
- If a supposed `.xls`/`.xlsx` download resolves to HTML, a landing page, login page, or other non-tabular content, reject it as data but inspect that returned official page immediately to recover the real workbook link, button target, or download query parameters before restarting broader search.
- After one failed file parse, use a bounded recovery sequence: confirm the file is invalid, inspect the returned official page/content for the true download target, try that official target, and validate that the result is a real workbook/table before any further searching.
- Before accepting a source as usable, confirm it exposes the required fields, years, definitions, and expected official content needed by the workbook; a landing page, summary paragraph, Article IV text, search snippet, AI/search summary, country overview, zero-byte download, blank file, HTML shell, or incomplete excerpt is **not** a substitute for the actual IMF WEO dataset/table or Geostat workbook.
- Record enough source detail to audit each populated input later: exact source file or table, sheet/table name, indicator or label, units, and year span.
- Before using any imported series in formulas, do a field-mapping spot check in the destination sheet: confirm indicator code, label, units, and 1-2 sample year values match the intended source series.
- For easily confused GDP fields, explicitly verify the destination cells for nominal GDP, real GDP, and GDP deflator are not populated from one another or from same-name-but-different-unit series.
- Immediately after populating `WEO_Data` or any copied official table, spot-check several known year/value intersections and headers to confirm row identity and year alignment before using those ranges downstream.
- Do not start `NA` or scenario formulas until this source-to-destination mapping check passes for at least GDP, GDP deflator (`NGDP_D`), `Total Output`, and `GFCF`.
- After a small number of distinct compliant attempts per source, stop expanding endpoint/debug exploration; if repeated attempts still return HTML pages, metadata, schema mismatches, access failures, or unusable files, stop source-dependent workbook population and report the blocker clearly.
- As soon as one compliant official path yields the needed usable data, stop source experimentation and proceed to workbook population.
- Before entering any source-driven value, open the underlying official table/workbook and verify the exact figure, year span, units, and series identity from that source artifact itself.
- Before building downstream formulas or scenarios, audit every required source series for complete required coverage through the workbook horizon or last source-driven year needed by the model. Do **not** accept partial WEO coverage just because earlier years loaded correctly.

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

- Once formulas or scenario blocks recalculate correctly, freeze the layout: do **not** insert/delete rows or columns, move assumption blocks, or make cosmetic structural shifts unless explicitly necessary.
- If a late structural edit is unavoidable, immediately audit the affected assumption-cell addresses and several dependent formulas by direct cell reference, then recalculate, save, reopen, and re-check before proceeding.- Keep helper calculations completely outside active model output ranges. Use existing dedicated assumption/helper areas only; do **not** place temporary averages, growth-rate helpers, or scratch formulas inside projection tables, scenario blocks, or future-year cells.
- Before autofilling any time-series formula, audit the seed cells it depends on: confirm the base-year source cells are nonblank, denominators are nonzero where division will occur, and the linked year headers match the intended source columns.
- Check boundary mappings explicitly before fill/copy operations: verify the first modeled year, the first projected year, and the final required year (2043) all point to the intended upstream columns with no off-by-one shift.
- After filling formulas, inspect representative cells near the beginning, middle, and end of each projected range to confirm no helper formula or misplaced edit has overwritten the live model formulas.
- Sanity-check key linked values before proceeding: `Total Output`, `GFCF`, import share, and year alignment must be economically plausible and not accidentally linked to the wrong source cells.

- If the task specifies an 8-year project beginning in 2026, ensure the allocation spans 2026 through 2033 inclusive and that the bell-shape weights sum to 100% across those eight years before linking outputs.

- After each currency/unit transformation, manually test one representative row: source amount -> exchange-rate conversion -> billions/millions scaling -> modeled cell. If the manual check and sheet result disagree, fix the unit logic before filling across years/scenarios.
- Record the expected order of operations for each transformed investment/input row before fill-down: source units, currency conversion, then magnitude scaling. Do **not** combine these implicitly in a way that can multiply or divide by 1,000 or 1,000,000 twice.
- After correcting any unit or scaling formula, re-read at least one beginning-year and one later-year scenario output cell to confirm the fix changed downstream results to plausible magnitudes before proceeding.
- Keep units labeled consistently in adjacent headers or notes and verify formulas match those units; do **not** mix USD, GEL, millions, and billions within one calculation chain without an explicit conversion step.

- If no dedicated helper area exists, place helper calculations only in a clearly unused area or separate helper sheet allowed by the template/task; never borrow cells inside live `WEO_Data`, `SUT Calc`, `NA`, or scenario projection ranges for temporary math.
- Treat the prefill audit as mandatory for any copied time-series or scenario formula: check seed/source cells, first modeled year, first projected year, and final year before filling across.
- Immediately after any fill/copy, inspect the first year, one middle year, and the last required year (2043) for each affected range to catch blank-source propagation, `#DIV/0!`, off-by-one year links, or overwritten live formulas before proceeding.


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

- After copying or extending scenario formulas, inspect boundary years and a few representative cells in each block—especially the first year, last year, and any cross-sheet pull—to confirm they reference the correct scenario-local inputs rather than blanks, the base block, or a neighboring scenario block.



### STEP 0: Preflight and Execution Rules
- Open the existing workbook first and map the actual sheet names, headers, merged cells, year columns, and input/output areas before writing formulas.
- Before editing any cell, confirm the exact workbook you are modifying, whether it already is the deliverable or needs a final save/rename step to become `test_demand.xlsx`, and what file you will return.
- Record the observed sheet names and inspect for hidden or renamed sheets before deciding any required structure is missing.
- If the task references specific cells, columns, ranges, or scenario blocks, locate and confirm those exact destinations in the workbook before entering data or formulas.
- Inspect enough of each target sheet to identify the full active model area you will edit: required headers, year columns through the endpoint, scenario block boundaries, and key input/output rows. Do **not** start writing formulas after only a truncated preview or partial row sample.
- If sheet inspection is incomplete, truncated, or ambiguous, resolve that first in Excel before duplicating blocks, filling formulas, or claiming the required structure is mapped.
- Identify hard constraints before editing: allowed tools, required output filename, required completion token, required source files, and whether the supplied workbook must be preserved.
- Before committing to any retrieval or workbook-editing path, confirm the environment can actually support that path within the allowed tools. If a needed Excel operation or allowed capability is unavailable, stop and report the blocker instead of improvising with unsupported tools, installs, or alternate formats.
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

- Start by extracting the task's explicit execution contract and workbook requirements into a short checklist: required tool/protocol format, exact completion token, required workbook filename, required sheets, required scenarios, required official sources, and any fixed assumptions.
- Inspect the local workspace before external lookup: locate the workbook to edit and any companion files already provided. Do **not** begin web searching or source hunting until you have verified whether the required workbook, templates, or source workbooks already exist locally.
- Treat workbook mapping as a gate: identify the real sheet names, visible structure, exact editable ranges, scenario block locations, year columns, required outputs, and any hidden or renamed sheets before broad source collection.
- Use an evidence gate before expanding scope: only create sheets, fetch external data, or build new modeling structure when the task text or inspected workbook clearly requires that step. If the workbook has fewer sheets than expected, treat that as a workbook fact to resolve carefully, not proof that other sheets must be reconstructed.
- Before any bulk paste, fill, or formula write, inspect the exact target ranges for merged cells, protected/locked regions, hidden rows/columns, and other layout constraints that can block writes; adjust the write plan first rather than discovering this mid-edit.
- Plan all needed structural edits early. After formulas or scenario blocks have been validated, treat row/column insertions, moved assumption blocks, and layout shifts as high-risk changes to avoid unless explicitly necessary.
- Keep preflight bounded: once the task contract, workbook structure, destination ranges, and needed inputs are confirmed, move directly to concrete workbook edits instead of prolonged exploration.
- Make incremental, verifiable workbook progress: after completing a logical block such as `WEO_Data`, `SUT Calc`, or one scenario section, save in Excel and confirm the edited cells/ranges actually changed in the target workbook.

- Execution checkpoint: after workbook structure, required destination ranges, and the minimal verified official inputs are confirmed, stop further exploration and switch immediately to workbook population, save, validation, and any required completion signaling.
- Execution continuity rule: once preflight, source retrieval, and destination mapping are complete, continue through workbook population, scenario creation, validation, save, and final message in one uninterrupted completion sequence unless a real blocker forces a stop.
- Use a bounded-progress rule: after each inspection or retrieval step, convert the result into the next concrete workbook action, source-validation action, or blocker report rather than repeating open-ended search.
- Do not end on an intention statement such as "next I will..." while required workbook work remains. If only a few tasks remain, do them before any further planning summary or exploratory work.

- Protocol lock-in is mandatory: before the first action, verify the exact required action wrapper/prefix, tool-call schema, allowed tool names, and required completion marker from the task/system instructions, then use that exact format verbatim on every executable turn.
- Perform a minimal capability survey up front within the allowed interface: verify Excel access and any permitted open/save/retrieval actions you will rely on. Eliminate noncompliant paths immediately rather than probing forbidden Python, shell, or unsupported parsers.
- Environment audit comes before tool selection: identify whether the target artifact is an Excel workbook, webpage, PDF, or text file, then choose only supported in-environment operations for that artifact.
- Before any external source retrieval, finish a concrete workbook destination map in Excel: exact target sheets, required blocks, scenario locations, year columns, and the specific source-driven cells/ranges that need official data.
- For any workbook modification step, make the operation auditable: identify the target sheet/range, perform the edit in Excel, then read back the affected cells/formulas before moving on rather than batching many hidden changes into one opaque action.
- Make pre-bulk-write checks explicit: confirm the target cells are actually writable and identify the true top-left writable cells of any merged regions before any fill, copy, or scenario duplication; do not assume a bulk write succeeded until you read back the affected cells.
- Reserve explicit non-overlapping regions for assumptions, helper cells, and scenario blocks. If formulas rely on absolute assumption cells, keep them in a dedicated input block outside all scenario/year tables; do **not** let helper math or copied scenario blocks reuse those rows/columns.
- Define the minimum verified inputs needed to start workbook edits, and once those inputs and target ranges are confirmed, begin observable Excel writes immediately instead of continuing open-ended inspection or source exploration.
- Once workbook destinations are mapped and the minimum verified inputs for the next block are available, stop extended exploration and start editing the workbook incrementally. After each logical block, save in Excel and read back a few edited cells before resuming more lookup.
- If the environment lacks a needed allowed capability or repeated attempts show the write/save/inspection path is unavailable, stop and report the blocker instead of improvising with unsupported tools or alternate file-generation workflows.
- End-state check: do not leave the run on planning, inspection, or retrieval alone; finish with either a validated saved workbook plus the exact required completion token, or a clear blocker report.

### Stage-Gate Validation
- After completing each major stage (`WEO_Data`, `SUT Calc`, base `NA`, then each scenario block), recalculate and inspect a small sample of critical formulas, year headers, and assumption references before proceeding.
- Treat formula errors, blank required inputs, broken references, unexpected occupied-range collisions, or uncertain/failed edit actions as blocking issues for the current stage. Fix them before adding more downstream logic.
- Completion is mandatory: the task is not done when mappings are identified or sources are located; it is done only after the workbook is edited, saved as `test_demand.xlsx`, reopened/validated, and any required final completion token/message is emitted literally.

- Execution-stage gate: once a stage has enough verified inputs to proceed, make an actual workbook edit in Excel, save, and confirm the changed range before doing more analysis. Do not let a stage end with only notes, mappings, or download results.
- After any workbook write step, perform an explicit readback before continuing: re-inspect the edited sheet, confirm the intended sheet names/ranges exist, and inspect a few key cells/formulas that were just changed. Do not rely on a successful write/save message alone.
- After any write/edit step that reports an error or uncertain result, stop and confirm by direct readback whether the intended cells, formulas, or sheets were actually updated. Do **not** continue on the assumption that the edit probably succeeded.
- Separate mechanical validation from data validation: after formulas recalculate cleanly, reconcile a few critical populated cells against the source values you actually retrieved and the stated assumptions. Do **not** treat zero formula errors or successful recalc as proof that the workbook contents are correct.
- At minimum, compare representative year/value pairs for GDP, GDP deflator, and one or two downstream `NA` inputs/outputs to the collected official data after any late formula repair or fill operation. If a workbook value differs from the retrieved source without an allowed formula-based reason, fix the mapping before proceeding.
- Treat any contradiction between a manual/source check and the workbook result as a blocker for that stage. Inspect the exact formula, precedent cells, units/scaling, and referenced scenario/block; correct the issue, then recalculate and recheck before proceeding.
- Add a source-horizon gate before `NA` and scenario work: verify the final source-driven year in each required series is populated and nonblank. If trailing source years are missing, return to source retrieval and repair that series before proceeding.
- Before adding a new scenario block, validate that the current `NA` layout has no overlaps between assumption cells, helper ranges, and scenario tables, and inspect a few denominator-dependent formulas for blanks, zeros, `#DIV/0!`, or `#VALUE!`.
- If recalculation, readback, or reconciliation fails, resolve it inside the allowed Excel workflow before proceeding: inspect the affected formulas/ranges, correct the workbook, recalculate again, and verify by direct readback. If no observable workbook write can be completed, report the blocker instead of continuing analysis.
- When only workbook writing, scenario completion, validation, save/reopen, or completion signaling remains, do those actions next in one uninterrupted sequence. Do **not** stop on planning notes, optional exploration, or intention statements.


## Output

### Completion Gate
- Declare completion only if the edited workbook contains the required populated official-source data, linked formulas, and scenario outputs; structure alone is insufficient.
- If any required IMF WEO verification, Geostat table entry, or workbook population step remains undone, do **not** claim success. Stop and clearly report the unresolved blocker instead of handing off a partially prepared workbook.
- Before the final response, re-check the task-specific execution contract and use the exact required action/message format and literal completion token if one was specified.


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

- Never finish with a plan-only summary such as "mapped out," "next I will," or "ready to populate" while required workbook edits remain. Either complete the edit-save-verify cycle or report a blocker.
- Emit the exact required completion signal only after post-save verification. If the environment requires a literal token or final line, output that exact text and nothing that conflicts with or paraphrases it.

- Completion requires both workbook-content completion **and** protocol completion: there must be no announced-but-unexecuted workbook step, required official-source ranges must be populated/validated or explicitly blocked, and any exact required completion string must be emitted literally.
- If the workbook is partially populated, still awaiting official-source values, or described as 'ready for data population,' it is not complete. Report the blocker/incomplete state instead of signaling success.
- Do **not** declare completion if any essential official-source integration remains outside the workbook as user instructions, notes, pending manual download/copy steps, or unresolved placeholders. In that case, report a blocker/incomplete outcome instead of a delivered workbook.
- Before emitting the final completion signal, do a protocol check and a content check: confirm the final message uses the exact required literal termination string, and confirm key workbook values still match the retrieved source data after all edits.
- Do **not** end with a narrative success summary when the environment requires a literal completion token/string; use the exact required completion signal instead.


## Final Checks

- Do not treat a successful save, file timestamp, file size change, recalc, zero formula errors, or file existence alone as proof of completion.
- A successful recalc is only a syntax/integrity check. It does **not** prove that the right source data, scenario structure, year coverage, copied blocks, or edited workbook contents are present.
- Final validation must include direct inspection of actual populated cells you changed: verify a sample of populated WEO rows, SUT-linked inputs, and each scenario block's formulas, assumptions, and endpoint years by cell inspection rather than inferring completion from sheet names, formula presence, or a small assumption-cell spot check.
- Do not claim the workbook is complete while any earlier parsing, mapping, formula, layout, or source-retrieval issue remains unresolved. Resolve or clearly report each substantive error before giving a completion signal.
- Run a delivery audit immediately before finishing: the edited provided workbook is saved and reopened as `test_demand.xlsx`, required sheets and scenarios are present and populated, source-driven cells trace to retrieved official IMF/Geostat data, and the workbook is fully populated rather than a scaffold with placeholders or "verify later" notes.
- Inspect a sample of critical cells in `WEO_Data`, `SUT Calc`, and each scenario block in `NA` to confirm sourced values come from retrieved official data and calculated cells remain formulas rather than pasted estimates or convenience constants.
- Audit a few critical formula cells by address to confirm no copied references point to the wrong scenario/block and no helper or scratch formulas landed in active modeled ranges.
- After any late-stage formula, unit, or mapping fix, recalculate, save, reopen the workbook, and re-check the corrected key outputs before declaring completion.
- Check the final required year explicitly on linked series and scenario ranges to confirm 2043 coverage is complete.
- If any required source, mapping, workbook mismatch, or protocol requirement remains unresolved, report that blocker clearly instead of presenting a guessed or substitute completed workbook.

- Perform a protocol audit immediately before finishing: confirm you followed the required action/tool format throughout and that the final response uses the exact required completion token/text if one is specified.
- Completion gate: before declaring success, confirm there is no remaining instruction such as "download later," "copy manually," "populate later," or "next step" for any required IMF/Geostat data integration. If any such dependency remains, report the task as blocked/incomplete instead of complete.
- Reopen the saved `test_demand.xlsx` and perform an explicit post-save verification pass in Excel by direct readback, not just by successful save, recalculation, timestamp/file-size change, or absence of formula errors.
- Inspect and confirm at minimum: workbook sheet names; presence of `WEO_Data`, `SUT Calc`, and `NA`; representative key source cells in `WEO_Data`; key linked/calculated cells in `SUT Calc`; and at least one representative formula/value range in Base, Scenario 2, and Scenario 3 on `NA`.
- Verify from the reopened file that required formulas, year coverage, copied source tabs if applicable, and scenario-specific references are actually present. If post-save inspection cannot confirm a claimed population, linkage, sheet, or scenario block, do **not** claim it was completed.
- Reconcile a small set of critical workbook values against the collected source data before declaring completion. At minimum compare a few key WEO inputs and downstream linked values such as GDP/deflator years, `Total Output`, and `GFCF`, and fix any mismatch.
- Treat any validation mismatch as a blocking failure. If a manual check, formula audit, recomputed value, layout check, or source trace disagrees with the workbook, do **not** declare completion until the issue is corrected or explicitly explained by an allowed reason such as rounding/formatting.
- Check boundary-year cells and denominator-dependent formulas in `WEO_Data`, `SUT Calc`, and `NA` for blanks, zeros, `#DIV/0!`, and off-by-one year links before declaring completion.
- If you extended, imputed, or extrapolated any series because source years were shorter than the model horizon, inspect the affected destination cells/ranges directly and confirm the downstream workbook outputs are populated and numerically plausible before finishing.
- Before finishing, confirm there was an actual edit-save-reopen cycle on the target workbook; inspection, downloads, or planning alone do not count as task completion.
- If any late structural edit was made after formulas were already working, recalculate and inspect representative dependent formulas by address to confirm references moved correctly.
- If you discover late that layout, scenario placement, formulas, or source mappings are wrong, do **not** stop at the diagnosis. Make the correction, recalculate, save, reopen, and re-check before finishing.
- If any required finishing step fails in the allowed environment, fix it within the permitted interface or report a blocker clearly; do **not** defer resolution to later or present the workbook as complete.
- Never end without a definite completion-or-blocker outcome.

- Endgame checklist is mandatory: confirm the last workbook write succeeded, recalculate, save, reopen, and directly inspect specific required cells/ranges on `WEO_Data`, `SUT Calc`, and each `NA` scenario block, including at least one source-fed value, one linked formula, and the final-year boundary.
- Final validation must include direct readback from the reopened `test_demand.xlsx` of concrete key cells/ranges you edited. At minimum confirm representative populated source cells, one or more downstream linked/formula cells, scenario-specific formulas, required sheet presence, and visible presence of every claimed scenario block.
- Do not infer completion from recalc success, file existence, sheet-name lists, truncated previews, top-row samples, inspection of only assumption cells, save success, timestamps, file-size changes, tool success messages, recalculation, or zero formula errors alone.
- Claim only workbook properties you directly verified after the edit/save/reopen cycle. If verification covered only part of the workbook, state the confirmed facts narrowly and report any unverified portions instead of generalizing.
- Match the final report to observed evidence only. Never rely on a single-sheet preview, partial range readback, or indirect signals to justify claims about additional sheets, copied source tabs, or completed scenario structures elsewhere in the workbook.
- Run a final protocol and provenance audit before finishing: confirm the required action/tool format was followed, the final response uses the literal required completion token/text, and a few critical populated inputs can be traced to the exact IMF/Geostat source artifacts opened during the run.
- If final verification finds any missing source year, blank required value, wrong reference, extrapolation issue, or incomplete trailing coverage, enter a repair loop immediately: correct the issue, recalculate, save, reopen, and re-check the affected cells before completion.
- After any late-stage formula, unit, or mapping fix, do not stop at recalc: save, reopen, and read back representative corrected cells in the affected source range and downstream scenario/output range to confirm the specific error is actually resolved.
- If the run required structured-tool or shell-style actions, perform a final protocol audit: confirm the last steps also used the required action format rather than drifting into unsupported tool syntax or prose-only commands.
- Never stop immediately after a successful save or after saying verification is next. Either execute the verification and then complete, or report a blocker clearly.

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

