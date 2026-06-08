---
name: shock-analysis-supply
description: "Estimate investment spending shock using Cobb-Douglas production function with HP filter in Excel."
---

# Supply-Side Shock Analysis with Cobb-Douglas

## When to Use

- Estimate potential GDP using production function
- Apply HP filter to extract trends
- Model investment shocks in Excel

## High-Priority Execution Gate

- First, restate the exact execution contract from the live task/environment: required action/tool syntax, workbook path, target entity, mandated sources, required native Excel steps, allowed directories/path style, and exact completion signal.
- Do not send any tool call until it matches the required protocol exactly; if the environment requires a specific wrapper such as `Thought:` plus `Action:` JSON, one-tool-per-message, or a single allowed tool, use that exact format for every action.
- Before any broad external search, finish a concrete workbook fill map from `test-supply.xlsx`: target sheets, exact columns/cells, year span, units, and which fields must stay formula-driven.
- Make an actual in-file progress step early once one destination is confirmed; do not spend the run only on searches, downloads, or reconnaissance while the workbook remains untouched.
- After every download/fetch, validate immediately that the artifact is usable structured data for the required series and stored in an allowed path (not HTML, metadata, landing text, preview output, zero-byte/tiny/unreadable content, or an empty file). If invalid, discard it and change method.
- If two attempts for the same series yield summaries, metadata, invalid files, or other unusable outputs instead of workbook-ready annual values, pivot to a direct official export/API/download or move to another workbook section; do not keep refining the same weak search pattern.
- Treat the task as incomplete unless you actually write to and save the workbook; data discovery alone is not progress.


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

- Use only explicitly authorized tools and invocation formats, and make tool actions auditable: issue concrete commands or operations, not prose claims such as "updated workbook" or "verified file" standing in for an actual action.
- Read and write only within explicitly allowed directories and with the required path style.
- Treat workbook write success as unverified until you reread representative exact target cells/ranges and confirm the stored formulas/values match what you intended.
- Do not treat a script exit code, silent tool success, file timestamp change, or absence of exceptions as evidence that workbook work is complete. Completion requires direct inspection of the edited workbook for populated required cells, live formulas, and nonblank, evaluated, non-error outputs in representative required ranges.
- Do not claim that a required native Excel step was performed unless you actually performed it in the allowed environment. If Solver or another mandated in-app step is unavailable or blocked, report that exact blocker instead of stating or implying it was completed.
- Do not proceed to populate or claim completion for source-dependent workbook sections until each required series has been retrieved in full usable year-by-year form from the mandated source family, or explicitly marked blocked. Partial fetches, snippets, metadata pages, previews, HTML/error pages, headers-only responses, tracebacks, nonzero exits, parse failures, empty results, or unverifiable extracts are blockers for those dependent cells.
- Do not begin broad external searching before you can name the exact workbook targets to fill. Identify the concrete destination sheets, columns/ranges, variables, and units first, then retrieve only the source data needed for those mapped targets.
- Make a real workbook-progress action early after inspection. Do not spend the run on searches/download attempts while `test-supply.xlsx` remains unmodified.
- When the workbook calls for a named source variable or definition, use that exact official series definition. Do not substitute nearby indicators, alternate provider series, fallback datasets, or differently defined measures unless the task explicitly authorizes that fallback and you have verified semantic compatibility with the workbook target fields: indicator definition, units, price basis, frequency, coverage, and whether the workbook expects levels vs growth rates.
- Do not write placeholder, interpolated, estimated, snippet-derived, comment-labeled provisional, or pass-through initial-guess values into required source-data or model-output fields just to keep the model moving.
- Do not ask optional clarification questions when the workbook path, required sources, and target outputs are already defined and you can begin inspection or population immediately.
- Do not present unresolved mandatory steps as user next steps. If recalculation, Solver, validation, save/reopen checks, or another native Excel action is required for completion, either complete it yourself or explicitly state the workbook is incomplete because of that blocker.
- Do not treat scaffold or placeholder formulas as completed model output. A copied-through initial guess, including an HP trend initialized equal to the raw series before Solver, is temporary only and must be replaced by validated solved output before finishing.
- Treat malformed formulas, self-referential placeholders, doubled equals signs, quoted-formula artifacts, truncated evidence, or unexpected blanks in prerequisite model areas as blocking errors. Re-check with targeted inspection and fix or report them before continuing downstream.
- Never place instructions, reminders, Solver steps, or narrative text inside occupied or formula-linked workbook cells.



## Non-Negotiable Constraints

## Task-Protocol Compliance

- Treat any task- or system-specified interaction protocol as part of the deliverable itself: use the exact allowed tool names, action schema, message format, field names, one-tool-per-message discipline if required, and exact completion token/string when one is specified. Do not substitute alternate tool-call syntax, wrappers, pseudo-commands, or near-match tokens.
- Before the first action, extract any exact protocol constraints and keep using that exact format for the entire run.
- Reserve any required completion signal for the very end and emit it verbatim only after all workbook work and final validation are complete.
- Before every tool call, do a pre-send check: correct tool name, required argument schema/JSON, and executable content only. Do not submit malformed payloads, unsupported tool names, or placeholder/narrative text as if it were a command.

- Treat protocol compliance as a hard gate and part of the deliverable itself. Before the first action and before the final response, extract the concrete objective from the live task text and mirror the exact protocol requirements verbatim: workbook/file path, target geography/entity, required sources/method, exact allowed tool names, wrapper syntax, payload/schema shape, one-tool-per-message discipline if required, allowed paths, and any exact completion token/string.
- If the task or environment requires a specific wrapper, tool-call syntax, JSON schema, or exact terminator, use that exact format from the first executable step through the final line. Do not substitute XML-like tags, pseudo-tools, near-match wrappers, malformed payloads, helper tools, or prose standing in for commands.
- Before every tool call and again before the final response, do a literal pre-send check against the required contract: supported tool name, exact schema/JSON fields, allowed number of tool calls, allowed path usage, and executable payload content only. Keep actions concrete and auditable.
- Reserve any exact required completion token/string for the very end. Emit it verbatim only when the workbook task is actually complete; if completion is blocked, report the blocker instead of improvising or using the completion signal early.
## Runtime preflight

- Before any data retrieval or workbook edit, identify the concrete deliverable from the task text: target workbook/file, target entity/country, required sources, required methodology, required final signal, and any acceptance checks. If any of these are missing or ambiguous, do not assume them from prior examples.
- Follow the exact execution contract given by the environment or task instructions. Use only the permitted tool names, action syntax, message schema, and path rules; do not improvise alternate tool-call formats, unsupported tools, or ad hoc workflows.
- Read and write files only in explicitly allowed directories and with the required path style. Do not download to convenience locations unless that path is explicitly allowed.
- Treat every external fetch as untrusted until validated with available tools: confirm the command succeeded, the file exists in an allowed path, has nonzero size, and is readable in a format consistent with the expected dataset. Do not proceed on timeouts, partial transfers, HTML landing pages, or failed verification commands.
- If a required external source or host is shown unreachable after a small number of materially different attempts, stop retrying speculative access paths. Complete all reachable workbook work and report the blocker clearly; do not keep searching or claim the source was retrieved.

- If the actual user task text is not visible in the current context, stop and obtain it before inspecting or editing any workbook. Do not infer the country, workbook, source series, or deliverable from this skill, prior runs, or default examples.
- Before the first exploratory action, state the concrete deliverable in one line: exact workbook/file to edit, target geography/entity, exact outputs or cells/ranges to complete if known, required sources/method, and any exact completion token. If the requested modification or success condition is not actually specified, stop and resolve that ambiguity before workbook inspection or web searching.
- Before broad source retrieval, produce a minimal source-to-cell map for the next actions: required series -> official source -> target sheet/column/range -> expected year span/units -> whether the destination must remain a formula. If inspection output is truncated or too high-level to name exact destinations, continue narrower workbook inspection first.
- Commit early to one confirmed end-to-end workable path using only available tools and official access methods. Before choosing a workbook-editing, parsing, or automation path, verify the available tools can complete the required workflow end-to-end, including in-place workbook edits, formula preservation, recalculation/inspection, and any mandated native Excel step such as Solver. If the path cannot actually complete those requirements, change approach before editing.
- Treat suspicious automation, failed commands, or downloaded artifacts as unresolved until validated: inspect enough to confirm target file path, target sheets/ranges, real file type/content, plausible size, openability, expected sheets/fields, and that the target series/country appears in structured rows. A zero exit code, no traceback, a timestamp change, truncation, parse failure, empty read, or opaque placeholder logic does not prove `test-supply.xlsx` was correctly updated.
- Use search only to locate the official structured endpoint. Once an official API/download/export path is found, stop snippet-search iteration and complete that retrieval/parsing workflow before doing more broad searches.

## Multi-Step Process

**Task-clarification gate:** before workbook inspection or source collection, restate the concrete deliverable from the task in one line: what file must be edited, what artifact/output must exist, and any exact completion signal. If the requested modification, target sheet/cells, or success condition is not actually specified, stop and resolve that ambiguity instead of doing open-ended exploration.

**Before editing the workbook:** inspect existing sheets, headers, named areas, formulas, and occupied ranges. Verify target-column mapping from headers or example rows before entering data, especially when a field is unlabeled, then proceed to populate `test-supply.xlsx` rather than stopping at reconnaissance.

**Workbook-target mapping checkpoint:** before broad source collection, produce a concrete fill map of what the workbook needs: target sheet(s), exact input columns/cells, required year span, expected units/labels, and which cells must remain formulas. If you cannot state which workbook locations will receive each external series, inspect more of `test-supply.xlsx` first instead of continuing source searches.



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

- At the very start, extract and pin these protocol items if present: exact allowed tool/action schema, exact allowed tool names/applications, allowed file paths, exact workbook targets, required native-application steps, and the exact final completion signal. Treat them as hard requirements until the task ends.
- Before the first workbook edit or source query, verify you have the actual live task instruction in hand: exact file path/workbook name, geography/scope, required sources, required tool/action syntax, and any required final completion signal. Do not let generic examples in this skill override the user's actual task.
- Before the first substantive action, restate the actual task objective in concrete terms: what file must be produced or edited, for which target, using which sources and method, and what completion token or final output is required.
- Complete a concrete workbook map before source hunting: identify the exact target sheets, headers, missing ranges, expected variables, units, and the minimum concrete workbook change needed to satisfy the task.
- Within the first few actions, choose one viable end-to-end retrieval/edit workflow using confirmed-available tools and official access paths, and validate it with a small real retrieval or workbook edit instead of prolonged environment probing.
- Make an early in-file progress action once the first destination is verified: enter a confirmed label, formula, setup step, or the first validated series block in `test-supply.xlsx`, then continue iteratively.
- Before relying on any workbook automation path, confirm the available tools and libraries can perform the required edits and validations end-to-end. If the chosen path cannot support required workbook logic, native Excel actions, recalculation, or inspection, change approach before editing rather than inferring success from a later zero exit code.
- Before parsing any downloaded source artifact, inspect the actual file type and structure first, then choose the parser from the observed format, sheet names, headers, and visible schema. Do not guess parser or encoding fixes before confirming what kind of file you actually received.
- For each required external source, prefer a path you can validate immediately as structured annual data (download/export/API). Treat retrieval as verified only when the needed observations are visible and match the requested indicator, geography, and period; if a response fails to open or parse, is HTML, XML/error text, metadata, login/landing content, unexpected schema, or another non-data payload, switch paths early.
- Treat a successful direct official API/export/file endpoint as the primary path. Once a structured official source is found, stop broad searching and complete retrieval/parsing from that endpoint before doing additional web searches.
- Before deriving any cross-source ratio or linking external series into one formula chain, verify unit, scale, price basis, currency basis, and annual alignment from source metadata. If numerator and denominator are not yet proven commensurate, reconcile conversions first and only then populate dependent formulas.
- After one or two failed attempts that provide no new access path, treat the dependency as blocked for now, move on to independent workbook work, and preserve a concise blocker note for the final report.

- If you cannot yet name the next concrete workbook write, inspect the workbook more; do not continue with exploratory searching.
- Treat any truncated command, cut-off script, malformed payload, partial code echo, traceback, or ambiguous tool result as a failed or unverified step, not a success. Re-run cleanly and validate the effect before building downstream workbook work on it.
- Do not claim a workbook sheet, series import, or calculation block is populated until you have direct evidence from the completed action output and a follow-up inspection of representative target cells or ranges.
- Make one real in-file progress action as soon as the first mapped destination is confirmed, then continue iteratively instead of postponing all edits until all research is finished.

### STEP 1: Data Collection
- PWT database from Groningen
- IMF WEO for real GDP
- If the task explicitly requires Playwright MCP or another named access method for IMF WEO extraction, use that method to retrieve the actual year-by-year series from the official interface before populating Excel.
- ECB for CFC (consumption of fixed capital)
- Calculate depreciation rate

- Prefer direct machine-readable official sources (XLSX/CSV/API) over search snippets or landing pages.
- Treat official-source retrieval as incomplete until you have workbook-usable annual rows for the required geography and years. Search summaries, AI overviews, snippets, metadata pages, landing pages, chart previews, header-only extracts, empty filters, HTML/error responses, preview-only files, mirrors, or other secondary copies do not justify populating dependent workbook cells.
- Treat a successful direct official endpoint as a checkpoint to exploit immediately: save or inspect multiple real rows, identify the year/value columns, and move that series into the workbook before resuming any other source hunting.
- After every file download, validate the artifact before proceeding: confirm content type or file format, nontrivial size, readability or openability, and expected workbook or archive structure. If a supposed XLSX cannot open as a workbook, or the file is HTML/XML-like text, wrong-schema content, or another unexpected format, treat that URL as invalid and switch to another official path rather than continuing downstream.
- Validate each imported series before use: confirm variable identity, year coverage, units, currency, price basis, and that you obtained workbook-ready annual year/value series.
- Use the specified external sources exactly; do not substitute other databases or guessed placeholders when the task specifies IMF WEO, PWT, or ECB/CFC.
- If a mandated source is unavailable and fallback is not explicitly authorized, leave the dependent cells unresolved and report the blocker; do not backfill from another dataset just because it has a similar GDP, growth, capital, or depreciation series.
- If fallback is explicitly allowed, verify semantic compatibility before writing anything: exact indicator meaning, level vs growth-rate role, units, price basis, annual coverage, and whether the workbook expects that exact series definition. Do not mix levels from one source with growth rates from another unless that compatibility is specifically established.
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

- Use web search only to locate the official endpoint. Once you have the source page, dataset name, export path, series identifier, or subject code, stop broad searching and fetch the structured table/file itself.
- Do not treat search-result summaries, AI overviews, snippets, preview text, metadata pages, or dataset descriptions as source data for workbook cells.
- Match workbook inputs to exact source-variable names and definitions before searching for substitutes. If the sheet or header expects a specific official variable, retrieve that exact series from the mandated source rather than a similar series with different provider, pricing, PPP, unit, or definition.
- Immediately after every download or export, verify the artifact is usable before any transformation: confirm it is not an HTML/XML/error page, size is plausible, the workbook/archive opens, expected sheets/headers exist, and the target country/series and year coverage are present.
- Immediately validate every fetched or downloaded file before doing more retrieval: confirm file type/content, openability, sheet names or columns, exact year/value fields, variable identity, year coverage, and that it contains structured annual rows or columns rather than HTML, XML-like text, a landing page, an error message, metadata only, or a tiny placeholder response.
- Reject invalid, tiny, malformed, preview-only, or structurally wrong responses immediately; do not build extraction or workbook population steps on top of them.
- A source is not complete until you can point to the successful retrieval step that produced workbook-ready annual rows or files through an allowed official path. Failed attempts, parser errors, 404s, HTML pages, advisory text, unparsed API output, or another tool's opaque claim do not satisfy the requirement.
- Run a semantic sanity check on each extracted series before accepting it as final: confirm label, units, order of magnitude, and that distinct indicators are not accidentally identical copies of the same underlying values.
- After a successful file download or API/export response returns structured data, inspect several real observation rows, map the needed fields, and move that series into the workbook instead of returning to generic searches.
- Treat data discovery and workbook population as interleaved work: once one required series is validated, write it into the mapped workbook target before resuming broader source collection.
- If two retrieval attempts for the same series still produce summaries, snippets, metadata, or other incomplete/invalid outputs, stop rephrasing the same search. Pivot to a direct official download/API/export within the same required source family or move to another workbook component until you have a usable table.
- If the requested dataset is a named external official series, do not manufacture it from another dataset after retrieval fails unless the task explicitly authorizes that derivation. An unavailable official series is a blocker, not permission to backfill a proxy.
- If official-source access fails and the task still explicitly allows a fallback, verify and document that the fallback matches the exact workbook target concept before writing it: same indicator meaning, same level/growth interpretation, same units or price basis, frequency, and compatible year coverage. If you cannot establish that match, leave the field unresolved and report the blocker.
- For mandated IMF WEO inputs, if the official WEO retrieval path fails or returns empty, partial, or unusable content, stop populating those source-driven cells from assumptions. Record the exact retrieval blocker, complete independent workbook work, and leave the WEO-dependent cells unresolved rather than inventing annual values, ad hoc growth paths, or projection-based stand-ins.
- Do not transition required source-fed cells to complete status on the basis of a workable plan when the exact annual series is still missing. If the exact required series remains unavailable after validated official-source attempts, leave the dependent inputs unresolved and report the missing series explicitly rather than backfilling proxies or hand-entered estimates.
- Before writing any source-driven values or claiming a source-fed sheet/range is populated, confirm the retrieval evidence shows the actual annual observations in usable form. Headers-only JSON, metadata pages, landing pages, previews, parse errors, HTML/error responses, unreadable downloads, or another tool's opaque claim do not authorize workbook population.
- Before each workbook write, verify and be able to point to the exact series identity, full required year coverage, units/scale, definition match, and extracted rows that will be entered.
- When extracting multiple indicators from one portal, file, or scraper output, run an early semantic check: confirm each series has the expected concept, units, and rough magnitude, and that distinct indicators are not accidental duplicates. If a mapping looks wrong, isolate the bad source object/export, fix it, and revalidate representative years before proceeding.
- Before wiring ECB CFC, PWT capital stock, IMF WEO GDP, or any cross-source ratio into the model, verify representative rows are commensurate on units, scale, price basis, currency basis, and year alignment. Do not continue into depreciation or capital-path formulas on unresolved mismatches.
- Before computing depreciation from ECB CFC and PWT capital stock, explicitly verify numerator and denominator use compatible units, scale, price basis, and year alignment. If the implied rate is implausible, stop and reconcile the inputs rather than pushing the formula downstream.
- Before committing a depreciation formula beyond a test row, calculate one or two representative-year ratios and sanity-check the magnitude. If the implied rate is clearly implausible, do not fill the range yet; reconcile units/scale first or report the blocker.
- When deriving depreciation from ECB CFC divided by PWT capital stock, validate representative years before extending capital formulas: reconcile units, scale, currency or price basis, and year alignment, and confirm the implied depreciation path is economically sensible before using it in projections.
- After obtaining each required series, immediately verify the exact years, values, units, and variable identity needed for the workbook, then write those values into the mapped destination range and re-inspect that range in the workbook.

- Once the workbook reveals the exact required series names/codes or an official endpoint/export path is identified, pivot immediately to the direct official download/export/API/query path and stop generic searching for that same series. After validated official rows are visibly confirmed, move that series promptly into the mapped workbook range rather than ending with a retrieval summary.
- Mark a required source series as retrieved only after one successful, validated extraction path of your own produced usable annual rows/files from the mandated official source. Search results, guidance text, failed fetches, parser/import errors, 404s, timeouts, or another tool's opaque claim do not satisfy the retrieval requirement.
- If you cannot point to the exact successful retrieval action and inspected output for a required dataset, keep dependent workbook sections blocked or incomplete rather than proceeding as if the data were resolved.
- Cap recovery loops aggressively: after a small number of failed access attempts with no new official retrieval path, stop speculative mirror/archive hunting. Use already verified accessible data to complete the workbook work that is still supportable, or report the exact blocker.
- When a retrieval or inspection command fails, do not infer that the needed field, country code, table, or file was identified. Rerun with a corrected command and confirm the result visibly before using it downstream.


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

- Before any smoothing or Solver run, confirm the full input range is recalculated and numeric: no blanks, text, `None`, quoted formulas, pass-through placeholders, self-references, or unresolved errors in the `LnZ` source and trend cells.
- If a numeric routine sees missing or non-numeric input, stop and fix the spreadsheet precedents first; do not proceed with optimization on partially populated ranges.
- Before filling any new HP-filter formula family across the full range, enter it in a few representative rows, recalculate immediately, and confirm the current Excel environment accepts the functions and reference style. If a function errors in validation, replace it with a compatible workbook-safe equivalent before expanding the range.
- Do not leave the HP trend decision range as a pass-through copy of the raw `LnZ` series, an initialization guess, or any other placeholder at finish time. If representative trend cells still equal the unsmoothed source because Solver has not been run, the HP-filter task is incomplete.
- If the HP smoothing step requires Solver, the task is not complete until Solver has actually been run in Excel, the solution accepted, and the solved cells recalculated to numeric outputs. Do not replace execution with setup notes, "run Solver later" instructions, or a claim that the workbook is ready before that happens.
- Treat Solver execution as a hard completion gate: verify the Solver-changing trend cells were actually optimized in Excel and no longer merely mirror the source series except where that equality is genuinely the solved result.
- Never replace the required solved HP trend with a placeholder path just because Solver or recalculation support seems unavailable. Either complete the optimization using an allowed Excel-capable path, or leave the workbook explicitly incomplete and report Solver execution as the blocker.
- Do not hand off required Solver actions to the user in lieu of completion. "Run Solver later" or other manual Excel follow-up is only acceptable as a blocker report, not as a completed deliverable.
- Before final delivery, verify the Solver-dependent cells contain solved numeric results after accepting the Solver solution and recalculating the workbook.

- Before any HP optimization or smoothing attempt, inspect the exact source `LnZ` range and confirm representative top/middle/bottom cells are numeric after recalculation. If you see blanks, `None`, text, pass-through placeholders, self-references, or errors, fix precedents first rather than launching the routine.
- Before filling a whole HP or other formula block, test the exact formula pattern in a few representative rows in the current recalculation environment, run recalculation, and confirm those rows evaluate correctly. Only then extend the formula across the full range.
- Prefer workbook-safe functions already proven to recalculate in the current environment. If a function family is unsupported or returns engine-specific errors, replace it in the test rows first, recheck, and only then propagate the revised pattern.
- Treat pass-through, mirrored-source, self-referential, or other placeholder HP setup cells as temporary only during setup. A trend column that merely copies the raw `LnZ` series is initialization only, not a completed HP filter. Before finishing, verify representative trend cells no longer just mirror the source series unless that equality is demonstrably the solved result after Solver.
- Completion rule for HP filtering: if Solver has not actually been run and accepted in Excel where required, the workbook is still incomplete. Setup notes, "ready for Solver," pending manual/native Excel follow-up, or an unvalidated post-solve state do not count as finished output.


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


**Final-message gate:** before the last response, verify both artifact state and protocol state: (1) mandatory workbook steps are actually complete, including recalculation, Solver, inspection, save, and reopen checks if required, and (2) the final line exactly matches any task-mandated completion signal with no trailing text.

- Before building or filling any downstream production, growth, or scenario block, confirm every prerequisite input section feeding it contains populated numeric or valid formula results rather than blanks, placeholders, malformed formulas, or unresolved HP/depreciation outputs.
- Before any bulk fill or structural formula edit, test a small representative block, recalculate, and inspect the exact stored formulas and resulting magnitudes. If syntax is invalid, references drift, or outputs are implausible, fix that first instead of propagating the block.
- Use a pre-write check before any structural formula or note entry: (1) confirm the target cells are intended inputs or formulas rather than active model outputs, (2) confirm formula syntax is valid in one representative row, and (3) confirm numerator/denominator units produce a dimensionless, economically plausible rate before filling.
- Never place Solver instructions, reminders, or narrative text into any cell unless you have verified that the cell is truly unused and not referenced by formulas, named ranges, or downstream calculations.
- After writing formulas, immediately read back the exact formula text in representative target cells. If you see anomalies such as `==`, unintended text formulas, wrong-sheet references, or blank results where formulas should evaluate, repair them before extending the range.
- Keep all notes and Solver instructions out of the model grid; do not type text into any cell unless you have confirmed the area is truly unused and outside the model.

- Do not start or extend downstream production, growth, or shock formulas until prerequisite depreciation and HP-filter sections have been re-inspected and confirmed nonblank, non-placeholder, numerically evaluated where required, and free of malformed formula syntax in representative cells.

### Error-driven debugging gate
- If recalculation reports `errors_found` or shows any `#VALUE!`, `#REF!`, `#N/A`, circular-reference failure, `NaN`, `None`, bare `=`, stale initial guess, or unexpected blank in required outputs, switch immediately from fill/validation to debugging.
- Start from the first reported failing cell, inspect its formula, then trace precedents upstream until you find the first bad input, bad reference, text-vs-number issue, unit mismatch, or blank that the formula path does not tolerate.
- Do not stop at confirming that a formula is syntactically present. Verify that referenced cells contain the expected numeric or formula content after recalculation and that the error does not simply move downstream.
- After each fix, recalculate again and confirm the reported error count decreases or the blocker is now isolated and explicitly documented.

**Critical write-readback gate:** after every material workbook write to a prerequisite block (source tables, depreciation links, HP setup, production formulas), immediately reread the exact target cells and confirm both stored formula text and evaluated values are present as intended. If cells remain blank, `None`, malformed, unchanged, or still placeholder-based, fix that block before doing downstream work.

**Execution discipline:** once the runtime contract and workbook mapping are confirmed, stop looping on setup or generic searches. Make one real in-file progress action within the first few steps in a confirmed safe target area, then continue iteratively from validated source retrieval to workbook entry and reinspection.

- After any recalc or validation run that reports specific failing cells, inspect those exact cells first, then trace precedents upstream until you find the first bad input, blank, text value, incompatible unit/scale link, or malformed reference. Do not stop at confirming the displayed formula text looks plausible.
- If an objective or downstream output cell shows `#VALUE!`, `#N/A`, `NaN`, or an unexpected blank after recalc, verify each referenced range contains numeric or evaluable values where required and that transitions to intentional blank years are explicitly guarded before accepting the formula chain.
- If a large write introduces many errors, stop mass editing and reduce scope: fix one formula family or dependency chain, recalculate, confirm the error count drops materially, then continue. Do not launch another broad rewrite while the workbook still has widespread unresolved errors.
- Do not switch back to broad validation or final reporting while recalc status is still `errors_found`. Either reduce the error set through debugging or report the workbook as incomplete with the exact remaining blocker cells and cause.


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

- Hard stop: if any required checked cell is blank, `None`, `NaN`, still formula-dependent without native recalculation, still awaiting Solver or manual Excel interaction, still showing initialization values or placeholder paths, or still showing material unresolved errors, the workbook is not complete. Continue debugging or report the exact blocker.
- Validate populated inputs directly, not just formulas: reopen or inspect the source-data sheets/ranges and confirm the target cells that were previously empty now contain the intended year/value data for the required coverage.
- Distinguish formula presence from output validation: checking stored formula text is not enough when the task requires numerical workbook results. Reopen or directly inspect the saved workbook and verify evaluated values in representative first, middle, and last required rows/cells.
- Validate completion against task-critical cells, not just file existence or a sheet preview. Confirm that required source-data ranges are populated from the mandated sources, depreciation inputs are nonblank, HP-filter outputs are numeric and solved, and production/scenario result cells are populated with live formulas or intended solved values.
- Do not rely on a single-row or single-cell spot check to declare success. Validate representative top, middle, and bottom rows in each major source and formula block, confirm required ranges are populated, and inspect that key output sections are complete.
- When final inspection exposes an unresolved key value, trace that cell's precedents and the missing native step immediately; treat failed verification itself as a blocker, not a summary note.
- If any script, bulk edit, or automated workbook update was used, inspect representative edited cells on each claimed-updated sheet after the write step and before the final response. Base the completion claim on observed workbook state, not on execution status.
- If any source series is intentionally blank for unavailable years, test representative downstream cells that depend on the transition from populated years to blank years. Confirm the workbook either handles those blanks explicitly or add or fix guards before finishing.
- Before finishing, confirm you satisfied runtime protocol as well as workbook requirements: correct tool/interface usage, allowed-path compliance, traceable successful retrievals for every claimed external series, and any exact final completion string.
- Do not report external data retrieval as complete unless the saved file or table was actually validated as present, readable, and workbook-usable in an allowed location.
- Do not infer success from a script finishing, a workbook saving, or a few top rows printing. Re-inspect the exact sheets and ranges the task required and confirm they contain the expected formulas or solved numeric outputs.
- Recheck any cells touched during debugging to ensure no instructional text was left inside formula-dependent ranges, and do not describe dependent outputs as sourced or complete if the underlying retrieval was never explicitly verified with actual values.
- Do not declare completion while any required optimization step, unresolved error cluster, proxy-substituted required source, or known workbook-breaking dependency is still pending.
- Before declaring completion, verify there is no identified pending manual/native-app step, no unmet task-specific protocol requirement, and no unresolved required-source retrieval replaced by a proxy.
- Confirm the final response itself follows any required protocol exactly, including any mandated completion token, final-line format, or structured handoff string.
- Base final completion claims only on observed post-save workbook evidence, and if the task requires an exact completion token or message schema, emit it exactly as the final line with no extra trailing text.

- Final validation must include observed evidence, not intention: formula-text inspection is only structural checking. Recalculate and, where required, run Solver, then inspect representative prerequisite and output cells afterward to confirm evaluated numeric results are present.
- Inspect task-critical cells directly before declaring completion, not just sheet heads or file existence. At minimum, verify representative required cells for source-data ranges, annual depreciation, HP-filter outputs, and production/scenario result cells are populated with the intended formulas or numeric solved outputs.
- For every externally sourced or script-assisted range you filled, reopen or directly re-inspect representative affected sheets/ranges and be able to trace them back to the validated official extract used. Do not treat file existence, timestamps, `ls`, absence of exceptions, a few downstream spot-checks, or a generic "updated" status as proof that source-input ranges were correctly populated.
- Treat "formula present" as insufficient. Verify representative required cells show evaluated numeric results after recalculation; if a key cell is still `None`, blank, bare `=`, `NaN`, stale initial content, missing linked values, incomplete projection rows, or waiting on Excel to calculate when opened, the task is incomplete.
- Before declaring that a required series is complete, verify there is a traceable retrieval of the exact official variable used in the workbook and that no dependent source-data cells were filled with estimates, interpolations, or proxy indicators.
- When source coverage intentionally starts late or contains blanks, test representative dependent cells before, at, and after the transition. If downstream formulas do not tolerate those blanks, add guards or leave the dependent block explicitly unresolved and report the blocker.
## Finalization gate

- Immediately before the final response, verify all of the following on the latest saved workbook state: required protocol followed, required native Excel steps completed, key workbook errors cleared or explicitly reported as blockers, and post-save inspection performed.
- If any mandatory execution step or output validation is still blocked, do not output any completion signal or equivalent done claim; report the workbook as incomplete and name the blocker.
- Before the final response, ensure every claimed workbook update is tied to something you directly inspected in `test-supply.xlsx` after saving or reopening; if not inspected, describe it as unverified rather than complete.

- Immediately before finishing, perform a protocol-only check separate from workbook validation: confirm every tool call used the required schema/tool names, no unsupported syntax or opaque pseudo-commands were used, and the exact required completion signal will be emitted only if the workbook is truly complete.
- Do not emit any completion token or otherwise say or imply the task is complete while required source retrievals, workbook population, formula linking, recalculation, Solver execution, save/reopen checks, representative output validation, or mandated protocol steps still remain.
- Do not convert a required completed workbook deliverable into a "prepared workbook" handoff, permission question, or workbook described as merely "Solver-ready" just because native recalculation or Solver is inconvenient or initially unavailable. First exhaust other allowed ways to complete the required native step; if completion is still impossible, explicitly report the workbook as incomplete and name that blocker, and do not emit the completion signal.
- Never leave placeholder HP-trend values, pass-through copies of the source series, or "run Solver later" instructions in place of a required solved result.
- Immediately before the last response, run one explicit final gate in order: verify latest saved workbook state, verify representative critical ranges were re-inspected after the write, verify no unresolved required blockers remain, then emit the exact required completion token/string verbatim as the final line and nothing after it only if all prior gates pass.
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

- Confirm every required protocol element was followed exactly, including mandated tool-call/message schema during execution and the exact final completion token/string if specified.
- Confirm any script/tool-assisted workbook edits were verified post-write by inspecting the affected cells/ranges rather than assumed from command submission alone.
- Verify representative required result cells show actual numeric outputs now, not just stored formulas or values expected to appear after opening Excel.
- Do not instruct the user to perform remaining recalculation, Solver, or workbook-completion steps unless the task explicitly asks for a handoff.
- If any fallback data source was used, confirm it was semantically matched to the workbook target fields before entry; otherwise leave those cells unresolved and state the blocker.
- Confirm task-critical fields are genuinely complete: required source series populated from official structured data, annual depreciation not left blank/`NaN`, HP-filter outputs solved, and production/scenario outputs visibly populated in the saved workbook.
- Verify your final response itself follows any task-mandated action schema and ends with the exact required completion signal, with no substitute wording.
- Confirm no todo or status item was marked complete early: required data extraction, workbook population, formula setup, Solver/native Excel steps, recalculation, save, and re-inspection are all actually done or explicitly blocked.


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

