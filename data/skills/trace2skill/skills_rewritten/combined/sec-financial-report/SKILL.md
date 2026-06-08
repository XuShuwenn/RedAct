---
name: sec-financial-report
description: "Analyze SEC hedge fund filings (13F) to extract AUM, holdings, and investment changes for major funds."
---

# SEC 13F Hedge Fund Analysis

## When to Use

- Analyze hedge fund holdings from SEC filings
- Compare Q2 vs Q3 2025 data
- Extract fund details and stock holdings

## Input Data

- `/root/2025-q2/`: Q2 2025 filings
- `/root/2025-q3/`: Q3 2025 filings

Preferred workflow for all questions:
- Resolve the exact filing accession number from the relevant quarter's `COVERPAGE.tsv` before any fund-level analysis.
- Once the accession number or target CUSIP is confirmed, prefer the provided analysis scripts for summaries, comparisons, and rankings instead of manually aggregating large TSVs.
- If a ranking tool returns accession numbers only, join those accessions back to `COVERPAGE.tsv` on `ACCESSION_NUMBER` to recover the manager names before answering.



## Execution Guardrails

- Before the first tool use, restate the required deliverables and the exact execution interface you must follow (for example required `Thought:` / `Action:` structure, JSON schema, allowed output path, and exact completion token). Maintain that protocol literally for the entire run.
- Treat protocol compliance as a hard requirement, not a style preference: if the environment mandates a specific tool-call wrapper, action schema, or exact completion token, use only that interface for every step and do not switch to alternate markup or a natural-language wrap-up mid-run.
- If you notice you have drifted from the required tool/action format, stop and correct course immediately before doing more analysis.
- Keep a short live checklist of the requested outputs (`q1_answer`..`q4_answer`) and only run searches, scripts, or comparisons that clearly support one of those deliverables. If you are about to switch entities, quarters, or questions, re-anchor to the checklist first.
- Treat an unresolved requested-entity lookup as a blocking failure. If the requested manager/company cannot be verified in the relevant source data, do not substitute a different closest fuzzy match and do not finalize answers built from that substitute.
- Use only values that appear explicitly in observed tool output or source files. Do not promote an unresolved accession/CUSIP/ID into a final human-readable answer.
- Resolve every final ranked identifier individually before naming it: for accession-ranked answers, do one visible accession→manager lookup per final accession; for CUSIP-ranked answers, do one narrower exact CUSIP validation before assigning a company name.
- Do not trust a newly written script or opaque helper output unless you have inspected the saved script logic and verified that its inputs (accessions, quarter paths, CUSIP/value fields, baseline/comparison pairing) match the records you actually confirmed.
- If a command, one-liner, or script is left incomplete, cut off, or abandoned mid-logic, treat it as no evidence. Replace it with one complete command/script whose output you can read fully.
- Once all required evidence is collected, stop exploration and switch to a deliberate synthesis phase: map each verified finding to the required output field, write the deliverable once, reopen/parse it, and only then finalize.
- Before ending, perform a protocol check: required tool/action format used consistently, output path explicitly allowed by the task, exact completion token ready, and the saved deliverable reopened successfully. If any of these is uncertain, stop and resolve it before finalization.

## Execution Guardrails

- Follow the exact action/output protocol required by the task environment. If the task specifies an Action schema or an exact completion token, use that exact format throughout and end exactly as required.
- Read and write only in explicitly allowed directories. Do not use `/tmp` or other scratch locations unless the task explicitly permits them.
- Use only values that appear explicitly in observed tool output or source files. Do not guess accession numbers, fund names, manager mappings, CUSIPs, counts, or rankings from partial matches or truncated output.
- If a grep/search/analyzer result is ambiguous, truncated, or cut off, treat it as unresolved and rerun with narrower filtering, redirection, or a short saved script until the needed lines are fully visible.
- Treat incomplete Python one-liners or cut-off shell output as no result; rerun using a simpler command or saved script and wait for the computed output before concluding.

## Preferred workflow

- Use the identifier-first workflow: verify the exact manager/accession in the relevant quarter's `COVERPAGE.tsv` (or issuer→exact CUSIP for security questions) before any downstream analysis.
- Before extracting any answer, map the question to the correct source table: use `COVERPAGE.tsv` for filer identity and accession lookup, `SUMMARYPAGE.tsv` for filing-level aggregate totals/summary metrics, and `INFOTABLE.tsv` for holding-level rows, issuer/CUSIP lookups, and security-level rankings.
- If the requested manager is not found as an exact or clearly justified verified filer in that quarter's `COVERPAGE.tsv`, stop that question as unresolved. Do not continue with a nearest fuzzy match, alternate firm, or "best available" substitute.
- Use fuzzy search only as a fallback to generate candidates; if it disagrees with `COVERPAGE.tsv`, trust the direct quarter file once the match is fully verified.
- When `COVERPAGE.tsv` shows multiple filings for the same or similar manager in a quarter, inspect the filing/report type and prefer the actual `13F HOLDINGS REPORT` for holdings/AUM questions; do not use a `13F NOTICE` or other non-holdings filing as the downstream accession.
- Treat accession numbers as the canonical join key across tables and scripts: verify the accession in `COVERPAGE.tsv`, then reuse that exact accession for summary metrics, holdings counts, quarter comparisons, and accession→manager joins.
- After accession numbers are confirmed, prefer existing accession-based analysis scripts/tools for AUM, holdings counts, and quarter-to-quarter comparisons rather than manually reconstructing large-table logic.
- For multi-part tasks, chain tools in this order whenever possible: canonical lookup in `COVERPAGE.tsv` → accession-based helper/analyzer → direct source-file spot check of the final selected rows/values.
- Before accepting any script-produced metric, verify the metric-to-question mapping from labels, headers, or schema: for example, confirm whether the output is AUM vs `TABLEVALUETOTAL`, stock-only holdings vs total positions, and `VALUE` vs shares.
- If a preferred script fails, first inspect invocation, working directory, arguments, and file/path assumptions. Prefer corrected invocation/path/environment or a tiny task-local wrapper over modifying shared helper code.
- Do not modify reusable analysis code during task execution unless you have visibly confirmed a specific hardcoded path mismatch and the smallest path correction is necessary. For any other failure, leave shared code untouched and use direct dataset inspection or a separate one-off script instead.
- If reusable tooling is still brittle for the current task, switch to a short one-off query against the raw quarter files after accession verification instead of forcing the shared helper to work. Read headers first and emit the exact final rows used in the answer.
- If a ranking/script output is keyed by accession numbers, finish by mapping every final accession back to manager names through the same quarter's `COVERPAGE.tsv` before answering.

Read [references/reusable-analysis-workflows.md](references/reusable-analysis-workflows.md) when you need a proven pattern for script-assisted fund analysis after accession verification.
Read [references/metric-semantics-and-header-checks.md](references/metric-semantics-and-header-checks.md) when the question depends on field meaning (AUM vs table value, stock count vs total holdings, VALUE vs shares) or before any manual TSV aggregation.
Read [references/output-validation-and-fallbacks.md](references/output-validation-and-fallbacks.md) when command output is truncated, a ranking result is incomplete, or a holder/accession list still needs manager-name resolution.

## Questions

### Q1: Renaissance Technologies AUM in Q3
- Fuzzy search COVERPAGE for "renaissance technologies"
- If multiple Renaissance-related rows appear, verify the report type in the Q3 cover-page data and choose the accession for the actual `13F HOLDINGS REPORT`, not a `13F NOTICE` or other non-holdings filing.
- Get accession_number, then find AUM
- Prefer filing-level summary data (for example `SUMMARYPAGE.tsv` or a verified summary script reading it) for AUM/aggregate-total style metrics rather than deriving them from holding-level rows.
- If the available tool reports only `TABLEVALUETOTAL` or another summary field, do not call it AUM until the dataset/schema or tool label explicitly supports that interpretation; otherwise leave Q1 unresolved and keep checking field semantics.
- Treat fuzzy search only as a way to locate candidate rows. Stop if the matched filer is not clearly Renaissance Technologies / the correct filing entity; confirm the exact Q3 `COVERPAGE.tsv` row, then use that accession for downstream analysis.

### Q2: Number of stocks held by Renaissance
- Same approach, count holdings
- Reuse only the Q3 Renaissance accession already verified as the actual holdings-report filing from `COVERPAGE.tsv`.
- Reuse the verified Q3 Renaissance accession. If the filing/tool exposes both total holdings and stock holdings, use the count explicitly labeled for stocks/equities rather than the broader total-position count.

### Q3: Top 5 increased stocks by Berkshire Hathaway (Q2→Q3)
- Find Q2 and Q3 accession numbers for Berkshire
- Reject subsidiary, insurance-company, or affiliate matches unless the prompt explicitly asks for that entity. A search result containing names like `Life Insurance`, `Homestate`, or other Berkshire affiliates is not sufficient evidence for Berkshire Hathaway Inc.; verify the exact intended manager name from the full `COVERPAGE.tsv` row before selecting an accession.
- Compare holdings changes, rank by dollar increase
- Keep ranking keys such as CUSIPs only as intermediate computation fields. If you later resolve those CUSIPs to stock names and the question is asking for stocks, write the final ordered stock names rather than raw identifiers.
- Do not proceed until both Berkshire accession numbers are recovered verbatim from visible Q2 and Q3 filing-index or full `COVERPAGE.tsv` rows. If an accession-aware analyzer such as `one_fund_analysis.py` is available, prefer reusing it after confirming those accessions.
- If no existing tool produces a complete top-increase ranking, build it directly from Q2/Q3 `INFOTABLE.tsv`: filter each quarter to the verified Berkshire accession, normalize/join positions by identifier, convert `VALUE` numerically, compute `Q3_VALUE - Q2_VALUE`, then sort descending and keep the fully visible top 5.
- If the ranked increase output is clipped or only a banner/header is visible, rerun via a narrower query or saved script that prints the full ordered top 5 CUSIPs before answering.
- If searches return subsidiaries, insurance entities, amendments, unrelated managers, or truncated `Berkshire` strings, treat the target filing as unresolved. Keep searching until one visible Q2 row and one visible Q3 row in `COVERPAGE.tsv` clearly identify the intended Berkshire Hathaway manager/accession pair.
- A Berkshire accession is usable only if the exact accession appears in a fully visible `COVERPAGE.tsv` row whose manager name matches the requested Berkshire entity itself. Do not carry forward an accession seen only in notes, inferred from another tool, or associated with `Life Insurance`, `Homestate`, or other affiliates.
- Never substitute accession numbers or top-5 CUSIPs that were not explicitly shown in the validated search/comparison output. If the chosen accession was not visibly returned by the search step, add a direct `COVERPAGE.tsv` verification step before any comparison.

- Do not treat exploratory checks of one or two CUSIPs, new positions, or partial diffs as completion. Finish only when you have one fully visible ordered top-5 increase list derived from the verified Berkshire Q2 and Q3 accessions.
- If the comparison output shows only a banner, header, or truncated prefix without the ranked rows, then you have zero answer evidence for Q3. Rerun until the five selected items are fully visible in ordered output or reproduced directly from source data.
- After obtaining the final top-5 Berkshire CUSIPs, validate each company name with a narrower exact-CUSIP lookup scoped to the selected Berkshire filing data or another clean source row for that same CUSIP. If a lookup returns mixed, conflicting, or unrelated names, treat the name mapping as unresolved and rerun a more specific query before answering.

### Q4: Top 3 fund managers invested in Palantir (Q3)
- Inspect Q3 `INFOTABLE.tsv` headers or a sample row first so `CUSIP` and `VALUE` are confirmed from this dataset.
- Confirm the issuer-to-CUSIP match from visible `INFOTABLE.tsv` rows or other direct dataset evidence before aggregating top holders; do not rank holders for a guessed Palantir CUSIP.
- Use the sequence: issuer/ticker → exact CUSIP → top holder accessions ranked by infotable `VALUE` → manager-name resolution from those accessions through Q3 `COVERPAGE.tsv`.
- If a ranking tool returns accession numbers instead of display names, do a second lookup against filing metadata/COVERPAGE records and only output verified human-readable manager names.
- Treat accession-only analyzer output as an intermediate result, not an answer. Complete the second-step accession→manager mapping for every top-ranked accession before finalizing.

- If any aggregation or ranking command returns blank output, stop and debug before continuing: verify the matched CUSIP, inspect headers, print a few matching rows, and confirm the grouping/sort pipeline produces non-empty ranked results.
- For any blank aggregation step, validate the pipeline before retrying downstream work: confirm the issuer→CUSIP match produced rows, inspect a sample matching row, check the exact grouped field names/positions from headers, and verify the command emits ranked rows before trusting later output.
- For each accession in the final top-3 ranking, perform and keep an explicit `COVERPAGE.tsv` lookup for that exact accession. Do not output any manager name unless that accession→manager mapping is directly observed for all three ranked accessions.
- After obtaining the top 3 holder accessions, verify that the manager-name lookup returns exactly 3 corresponding rows. If only 1-2 names appear, the result is incomplete; rerun the metadata join or direct COVERPAGE lookup until each accession is resolved.
- Preserve the accession→manager evidence for all three winners and perform an explicit count check: expected winners = 3, resolved manager rows = 3. If the counts differ, treat the answer as unresolved and do not infer the missing manager from familiarity, rank order, or prior runs.
- If multiple ranked accessions belong to the same manager, aggregate those verified accession-level `VALUE` totals to the manager before selecting the final top 3, because the question asks for fund managers rather than filings.
- Do not fill a missing top-3 manager slot with a plausible firm name unless that exact accession-to-manager mapping is shown in observed output.
- Do not stop at top accession numbers. The question is unanswered until each of the top 3 ranked Palantir-holder accessions is mapped to a verified manager name from Q3 `COVERPAGE.tsv`, with no missing names in the top 3.

- If a holder-analysis helper fails, fall back to a direct raw-data workflow: inspect Q3 `INFOTABLE.tsv` headers, aggregate `VALUE` by `ACCESSION_NUMBER` for the verified Palantir CUSIP, sort the totals, then map the top accessions to manager names via Q3 `COVERPAGE.tsv` and aggregate to manager level if needed before selecting the final top 3.
- Closure rule for Q4: do not mark this question done until the ranked top-3 manager result is complete and all contributing winning accessions have separate visible `COVERPAGE.tsv` manager-name lookups.


### Evidence checks before finalizing any question
- Q1/Q2: confirm the Renaissance accession number from the actual Q3 `COVERPAGE` match before reading any values. For Q1, verify from schema/metadata or dataset documentation that the field used truly corresponds to AUM; do not assume `TABLEVALUETOTAL` is AUM unless the dataset explicitly defines it that way.
- Q2: if the filing or tool distinguishes total holdings from stock holdings, answer with the metric that matches the question text rather than assuming they are equivalent.
- Track question semantics explicitly: Q1 asks for AUM, Q2 asks for number of stocks held. Do not treat total holdings, stock holdings, and AUM as interchangeable, and do not say a question is answered until the observed metric matches that question exactly.
- Keep a per-question evidence map while working: `Q1 -> verified AUM field/value`, `Q2 -> verified stock-only holdings count`, `Q3 -> verified ordered top-5 increase list`, `Q4 -> verified top-3 accession-to-manager mappings`. If a retrieved value does not fit one slot exactly, it does not answer that question yet.
- DO NOT map `number of stocks` to a broader holdings total when the tool prints both. Use the value explicitly labeled `Number of stock holdings` (or equivalent stock-only field) when answering how many stocks are held.
- Q2: when both total holdings and stock-only holdings are available, answer with the stock-only count because the question asks how many stocks are held.
- Q3: confirm Berkshire Hathaway's Q2 and Q3 accession numbers from observed filing-index or full `COVERPAGE.tsv` records before quarter-over-quarter comparison. When results include subsidiaries, amendments, or unrelated near-matches, verify the exact Berkshire Hathaway filing entity from manager name plus amendment status for both quarters. Never use an accession inferred from a truncated grep line or fuzzy near-match, and if the top-5 output is clipped or only a banner/header is visible, rerun and capture the five CUSIPs from complete ranked rows in a structured format.
- Q4: interpret "share value" as the 13F infotable `VALUE` field unless the prompt explicitly requires ranking by shares, and only report manager names directly recovered for the top Palantir-holder accessions.
- Treat fuzzy search results as candidates only. Use `COVERPAGE.tsv` as the final authority for manager name, quarter, and accession.
- Q1/Q2: confirm the Renaissance accession once and reuse that same verified accession for both answers.
- Q1/Q2: if using a filing-summary tool for Renaissance, read back the specific labeled fields from that output and ensure the answer copies the metric that matches the question exactly (`AUM` for Q1, stock-only holdings count for Q2), not a nearby summary value.
- Q3: preserve the identify-then-compare sequence: do not run or trust quarter-over-quarter comparison output until both quarter accessions have already been explicitly verified from `COVERPAGE.tsv`.
- After a tool answers Q1, Q2, Q3, or Q4, do one explicit read-back check that the output still references the verified accession(s) and intended quarter before promoting the result into the final JSON.
- Any time a helper script or analyzer is used, sanity-check its key assumptions and inputs first, especially accession number, quarter directory, baseline/comparison inputs, and file paths.
- Before building a manual parser, check whether an existing local analysis script already computes the needed fund-level metric or quarter-over-quarter comparison.
- Before any manual `awk`/Python column-based aggregation over TSV files, read the header row first and map needed fields by name rather than assuming positions.
- Q4: after ranking Palantir holders by summed `INFOTABLE.tsv` `VALUE`, map the winning accessions back to manager names via the same quarter's `COVERPAGE.tsv` and verify the names come from those exact top-ranked accessions.
- When a result list is expressed as accession numbers, complete the metadata join back to manager names before writing the final answer.
- For any selected accession used in later computation, keep at least one directly observed search/index/COVERPAGE result showing why that accession was chosen; do not proceed from a remembered, inferred, or truncated candidate.
- If a search result, analyzer output, or lookup is truncated, ambiguous, or returns fewer rows than expected, do not treat unseen entries as confirmed. Rerun with narrower filters, redirection to a file, or a short script until the exact accession numbers, ranked rows, or manager mappings needed for the answer are fully visible.
- If you generate a script to answer any question, read the saved script back before running it and confirm it uses the accession numbers, quarters, and input files you actually verified.
- If an existing script/tool fails on file paths or inputs, inspect the script or command arguments first and verify whether the problem is invocation, working directory, or hardcoded paths before editing code. Make the smallest path/input fix only after that inspection is visible.
- After any script produces ranked CUSIPs or manager names, reproduce at least the final selected rows with a simple direct query against the source TSV/XML data before trusting `answers.json`.

- For any manager/company lookup, require positive verification that the final accession and filer name belong to the requested entity. A near-match, alternate firm with a similar name, affiliate, or top fuzzy-search hit is insufficient.
- If the requested entity is not found exactly or the available evidence remains ambiguous, leave that question unresolved rather than answering with a substitute entity's data.
- Treat affiliate-name matches as unresolved for manager-identity questions until the exact intended filer name is visible in the chosen `COVERPAGE.tsv` row; do not silently upgrade a subsidiary hit into the parent fund.
- For any ranked top-k answer, the final selected items themselves must be visible in full output or reproduced by a direct query. A truncated banner, partial header, or clipped script output is not evidence.
- If the available output exposes multiple plausible metrics for the same question, stop and resolve the mapping from headers/schema/question wording before answering; do not choose one just because a tool printed it first.
- Q1: if using `TABLEVALUETOTAL` or any similar summary field, verify and record its units from the dataset schema/header/documentation before treating it as AUM or converting it to a dollar magnitude. If unit semantics remain unresolved, stop and resolve them before answering.
- Keep the numeric field and its interpreted magnitude consistent. Do not report a raw `TABLEVALUETOTAL` value as dollars while also saying the field is "in thousands"; either answer in the field's native units or convert once using the verified unit definition.
- If the dataset support for calling `TABLEVALUETOTAL` "AUM" is unclear, answer only with the explicitly supported filing value metric or leave the question unresolved until the metric mapping is verified.
- Q4: every accession in the final top-3 Palantir ranking must have its own visible accession-to-manager lookup result. Never fill a missing manager name from assumption, institution familiarity, or another ranking output.

- When ranking or comparing holdings, confirm the question's metric against the raw field names before trusting tool output: use `VALUE` for dollar-value rankings unless the prompt explicitly asks for shares/counts, and use share fields such as `SSHPRNAMT` only when the question is about shares.
- Prefer an existing accession-aware helper over fresh manual parsing when the helper already computes the requested metric; use manual TSV/XML reconstruction mainly as a fallback or validation step.
- After any helper/analyzer returns a candidate answer, verify the final selected value(s) or ranked rows with a small direct query against the underlying quarter files before finalizing.
- Preserve the answer in the semantic form requested by the question. If the workflow computes with accession numbers or CUSIPs but the deliverable asks for manager names or stock names, complete that resolution step and write the resolved names into the final JSON.


## Output Format

Protocol-critical note: the output-path example below applies only when the current task explicitly requires that same path and it is within the task's allowed directories. Otherwise, write to the exact allowed destination given by the task, not the example path in this skill.

Protocol reminder before output/finalization:
- If the task environment mandates a specific action/tool-call schema, continue using that schema for every remaining tool invocation.
- If the task environment mandates an exact completion string such as `ACTION: TASK_COMPLETE`, the last line must be exactly that string with no extra text before or after it in the final response.
- Do not assume generating the JSON file is sufficient task completion. The task is complete only after you both verify the saved file and emit the exact required completion token in the required format.
JSON at `/root/answers.json`:
```json
{
    "q1_answer": number,
    "q2_answer": number,
    "q3_answer": ["cusip1", "cusip2", "cusip3", "cusip4", "cusip5"],
    "q4_answer": ["fund1", "fund2", "fund3"]
}
```


Synthesis rule before file writing:
- Stop launching new grep/Python probes once the necessary accession numbers, ranked CUSIPs, and manager mappings are already verified.
- If a command or Python snippet is incomplete, truncated, or abandoned mid-logic, discard it as evidence and replace it with one complete command/script whose output you can read to completion.
- Before writing `/root/answers.json`, explicitly map each confirmed finding to the required output field so finalization is a deliberate synthesis step, not a continuation of exploration.

Finalization checklist:
- Re-read the task instructions immediately before finalization and confirm the required completion protocol: exact tool/action format during execution, exact output path, and exact final completion token.
- Confirm the output path is the task-provided allowed destination, not this skill's example path unless the task explicitly authorizes that exact path.
- Verify closure question-by-question before writing the deliverable: Q3 must have a fully visible ordered top-5 list, and Q4 must have three verified manager names for the top 3 ranked accessions.
- Do not write the deliverable while any question still has an open rerun, truncated output, incomplete manager-name mapping, or unfinished fallback script. If analysis continues after file-writing, treat the file as premature and rewrite it only after closure.
- Stop if any answer still depends on an ambiguous filer match, an unverified accession, an unseen ranked item, a noisy/unresolved CUSIP-to-name mapping, or a manager name not directly returned by lookup output.
- Write valid JSON to the exact task-required output path, and only if that path is explicitly allowed. If the task explicitly requires `/root/answers.json`, use it; otherwise do not assume this example path is permitted.
- Before finalizing, confirm each answer is backed by directly observed output and that every final accession, filer, CUSIP, and manager name used in an answer has been directly verified.
- After writing the file, reopen that same output path (`cat` it or parse it in Python) to verify the saved deliverable, valid JSON syntax, and the exact required keys before declaring completion.
- Prefer one deliberate final write after all answers are verified; if you need to keep investigating after writing, treat the file as provisional and rewrite it only after the open verification step is resolved.
- If you continue investigating after writing the file, treat that as evidence the file was premature; resume analysis, resolve the open items, and rewrite the file only after all checks pass.
- If the task requires an exact completion token, emit that exact string as the final line after verification, with no summary, explanation, or extra text before or after it (for example: `ACTION: TASK_COMPLETE`).
- Before emitting a required completion token, do one last check that every top-k answer has the full expected number of directly verified rows.


Write the JSON in one deliberate step after you have all four verified answers; avoid piecemeal or partially edited writes.

Recommended validation sequence before completion:
1. Construct the full JSON object with exactly the four required keys.
2. Write `/root/answers.json` once.
3. Immediately reopen it with `cat /root/answers.json` or parse it in Python.
4. Confirm valid JSON syntax, all four keys present, and no truncated values or cut-off lines.
5. Only after that, emit the exact required completion token and nothing else if the task requires a bare terminator.


## Tips

- Parse SEC 13F filings (XML/HTML format)
- Use fuzzy matching for fund names
- Calculate holdings changes (price × shares)


- Verify the matched filer identity before using any fuzzy-search result; do not substitute a different fund because it is the top fuzzy hit. When multiple similar filers appear, confirm the full manager name, quarter, and amendment status in `COVERPAGE.tsv` before choosing an accession.
- For key IDs (manager, accession, CUSIP), prefer direct extraction from source filing metadata over inference from partial lines.
- For comparison questions, ensure the full ranked holdings or delta output is visible before selecting top CUSIPs; prefer queries or scripts that emit exact identifiers and final ranked lists in machine-readable form.
- Validate field semantics before answering business-metric questions. Do not assume a summary field such as `TABLEVALUETOTAL` equals the requested metric unless the dataset schema explicitly supports that mapping.
- If you write a script to compute answers, verify the key inputs it uses (selected accession numbers, fund names, quarters) before trusting `answers.json`.

- Preferred workflow for fund-specific questions: search `COVERPAGE.tsv` by manager name, confirm the exact filer/accession for the quarter, then query summary or holdings tables by that accession.
- Treat fuzzy matching as discovery, not proof: use it to generate candidate filers or issuers, then confirm the exact raw TSV row and quarter before extracting AUM, holdings counts, or comparison inputs.
- Once accession numbers are confirmed, prefer existing accession-based analysis utilities/scripts for single-fund summaries and Q2→Q3 deltas; trust them only after confirming their input accession numbers and reading the full ranked output.
- For security-specific ranking questions, inspect `INFOTABLE.tsv` headers first, resolve the issuer CUSIP, aggregate `VALUE` by `ACCESSION_NUMBER`, sort the totals, and map only the winning accessions back to manager names via `COVERPAGE.tsv`.
- When helper scripts and raw files disagree, trust the directly observed filing metadata and rerun downstream analysis using the verified accession.
- If a script write or terminal output was truncated, treat it as unverified until you reopen it and inspect the relevant logic or saved result.

