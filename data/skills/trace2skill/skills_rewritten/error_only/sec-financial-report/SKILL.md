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

- Before the first tool use, restate the required deliverables and the exact execution interface you must follow (for example required `Thought:` / `Action:` structure, JSON schema, output file path, and exact completion token). Maintain that protocol literally for the entire run.
- Keep a short live checklist of the requested outputs (`q1_answer`..`q4_answer`) and only run searches, scripts, or comparisons that clearly support one of those deliverables. If you are about to switch entities, quarters, or questions, re-anchor to the checklist first.
- Treat an unresolved requested-entity lookup as a blocking failure. If the requested manager/company cannot be verified in the relevant source data, do not substitute a different closest fuzzy match and do not finalize answers built from that substitute.
- Use only values that appear explicitly in observed tool output or source files. Do not promote an unresolved accession/CUSIP/ID into a final human-readable answer.
- Do not trust a newly written script or opaque helper output unless you have inspected the saved script logic and verified that its inputs (accessions, quarter paths, CUSIP/value fields, baseline/comparison pairing) match the records you actually confirmed.
- Before ending, perform a protocol check: required tool/action format used consistently, output path explicitly allowed, and exact completion token ready. If any of these is uncertain, stop and resolve it before finalization.

## Execution Guardrails

- Follow the exact action/output protocol required by the task environment. If the task specifies an Action schema or an exact completion token, use that exact format throughout and end exactly as required.
- Read and write only in explicitly allowed directories. Do not use `/tmp` or other scratch locations unless the task explicitly permits them.
- Use only values that appear explicitly in observed tool output or source files. Do not guess accession numbers, fund names, manager mappings, CUSIPs, counts, or rankings from partial matches or truncated output.
- If a grep/search/analyzer result is ambiguous, truncated, or cut off, treat it as unresolved and rerun with narrower filtering, redirection, or a short saved script until the needed lines are fully visible.
- Treat incomplete Python one-liners or cut-off shell output as no result; rerun using a simpler command or saved script and wait for the computed output before concluding.

## Preferred workflow

- Start manager lookup from the relevant quarter's canonical `COVERPAGE.tsv` and verify the exact filer name and accession number before using any derived analysis.
- Use fuzzy search only as a fallback or hint; if it disagrees with `COVERPAGE.tsv`, trust the direct quarter file once the match is fully verified.
- After accession numbers are confirmed, prefer existing analysis scripts/tools for AUM, holdings counts, and quarter-to-quarter comparisons rather than manually reconstructing large-table logic.

Read [references/reusable-analysis-workflows.md](references/reusable-analysis-workflows.md) when you need a proven pattern for script-assisted fund analysis after accession verification.

- If a preferred script fails or produces incomplete output, switch to a minimal verified fallback: inspect the script/path assumption, make only the smallest justified fix, or rerun with a narrower direct query that yields the full ranked result and complete accession→manager mapping before proceeding.
- Do not modify reusable analysis code during task execution unless the issue is a clearly verified file-path mismatch and the fix is the minimal path correction described in the workflow reference. If a script fails for any other reason, fall back to direct dataset inspection or a separate one-off script instead of editing shared helper code.

Read [references/output-validation-and-fallbacks.md](references/output-validation-and-fallbacks.md) when command output is truncated, a ranking result is incomplete, or a holder/accession list still needs manager-name resolution.

## Questions

### Q1: Renaissance Technologies AUM in Q3
- Fuzzy search COVERPAGE for "renaissance technologies"
- Get accession_number, then find AUM
- Treat fuzzy search only as a way to locate candidate rows. Stop if the matched filer is not clearly Renaissance Technologies / the correct filing entity; confirm the exact Q3 `COVERPAGE.tsv` row, then use that accession for downstream analysis.

### Q2: Number of stocks held by Renaissance
- Same approach, count holdings
- Reuse the verified Q3 Renaissance accession. If the filing/tool exposes both total holdings and stock holdings, use the count explicitly labeled for stocks/equities rather than the broader total-position count.

### Q3: Top 5 increased stocks by Berkshire Hathaway (Q2→Q3)
- Find Q2 and Q3 accession numbers for Berkshire
- Reject subsidiary, insurance-company, or affiliate matches unless the prompt explicitly asks for that entity. A search result containing names like `Life Insurance`, `Homestate`, or other Berkshire affiliates is not sufficient evidence for Berkshire Hathaway Inc.; verify the exact intended manager name from the full `COVERPAGE.tsv` row before selecting an accession.
- Compare holdings changes, rank by dollar increase
- Do not proceed until both Berkshire accession numbers are recovered verbatim from visible Q2 and Q3 filing-index or full `COVERPAGE.tsv` rows. If an accession-aware analyzer such as `one_fund_analysis.py` is available, prefer reusing it after confirming those accessions.
- If the ranked increase output is clipped or only a banner/header is visible, rerun via a narrower query or saved script that prints the full ordered top 5 CUSIPs before answering.
- If searches return subsidiaries, insurance entities, amendments, unrelated managers, or truncated `Berkshire` strings, treat the target filing as unresolved. Keep searching until one visible Q2 row and one visible Q3 row in `COVERPAGE.tsv` clearly identify the intended Berkshire Hathaway manager/accession pair.
- Never substitute accession numbers or top-5 CUSIPs that were not explicitly shown in the validated search/comparison output. If the chosen accession was not visibly returned by the search step, add a direct `COVERPAGE.tsv` verification step before any comparison.

- Do not treat exploratory checks of one or two CUSIPs, new positions, or partial diffs as completion. Finish only when you have one fully visible ordered top-5 increase list derived from the verified Berkshire Q2 and Q3 accessions.

### Q4: Top 3 fund managers invested in Palantir (Q3)
- Inspect Q3 `INFOTABLE.tsv` headers or a sample row first so `CUSIP` and `VALUE` are confirmed from this dataset.
- Use the sequence: issuer/ticker → exact CUSIP → top holder accessions ranked by infotable `VALUE` → manager-name resolution from those accessions through Q3 `COVERPAGE.tsv`.
- If a ranking tool returns accession numbers instead of display names, do a second lookup against filing metadata/COVERPAGE records and only output verified human-readable manager names.

- If any aggregation or ranking command returns blank output, stop and debug before continuing: verify the matched CUSIP, inspect headers, print a few matching rows, and confirm the grouping/sort pipeline produces non-empty ranked results.
- For each accession in the final top-3 ranking, perform and keep an explicit `COVERPAGE.tsv` lookup for that exact accession. Do not output any manager name unless that accession→manager mapping is directly observed for all three ranked accessions.
- After obtaining the top 3 holder accessions, verify that the manager-name lookup returns exactly 3 corresponding rows. If only 1-2 names appear, the result is incomplete; rerun the metadata join or direct COVERPAGE lookup until each accession is resolved.
- Do not fill a missing top-3 manager slot with a plausible firm name unless that exact accession-to-manager mapping is shown in observed output.
- Do not stop at top accession numbers. The question is unanswered until each of the top 3 ranked Palantir-holder accessions is mapped to a verified manager name from Q3 `COVERPAGE.tsv`, with no missing names in the top 3.


### Evidence checks before finalizing any question
- Q1/Q2: confirm the Renaissance accession number from the actual Q3 `COVERPAGE` match before reading any values. For Q1, verify from schema/metadata or dataset documentation that the field used truly corresponds to AUM; do not assume `TABLEVALUETOTAL` is AUM unless the dataset explicitly defines it that way.
- Q2: if the filing or tool distinguishes total holdings from stock holdings, answer with the metric that matches the question text rather than assuming they are equivalent.
- Track question semantics explicitly: Q1 asks for AUM, Q2 asks for number of stocks held. Do not treat total holdings, stock holdings, and AUM as interchangeable, and do not say a question is answered until the observed metric matches that question exactly.
- DO NOT map `number of stocks` to a broader holdings total when the tool prints both. Use the value explicitly labeled `Number of stock holdings` (or equivalent stock-only field) when answering how many stocks are held.
- Q2: when both total holdings and stock-only holdings are available, answer with the stock-only count because the question asks how many stocks are held.
- Q3: confirm Berkshire Hathaway's Q2 and Q3 accession numbers from observed filing-index or full `COVERPAGE.tsv` records before quarter-over-quarter comparison. When results include subsidiaries, amendments, or unrelated near-matches, verify the exact Berkshire Hathaway filing entity from manager name plus amendment status for both quarters. Never use an accession inferred from a truncated grep line or fuzzy near-match, and if the top-5 output is clipped or only a banner/header is visible, rerun and capture the five CUSIPs from complete ranked rows in a structured format.
- Q4: interpret "share value" as the 13F infotable `VALUE` field unless the prompt explicitly requires ranking by shares, and only report manager names directly recovered for the top Palantir-holder accessions.
- Treat fuzzy search results as candidates only. Use `COVERPAGE.tsv` as the final authority for manager name, quarter, and accession.
- Q1/Q2: confirm the Renaissance accession once and reuse that same verified accession for both answers.
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
- Q4: every accession in the final top-3 Palantir ranking must have its own visible accession-to-manager lookup result. Never fill a missing manager name from assumption, institution familiarity, or another ranking output.


## Output Format

Protocol-critical note: the output-path example below applies only when the current task explicitly requires that same path and it is within the task's allowed directories. Otherwise, write to the exact allowed destination given by the task, not the example path in this skill.

Protocol reminder before output/finalization:
- If the task environment mandates a specific action/tool-call schema, continue using that schema for every remaining tool invocation.
- If the task environment mandates an exact completion string such as `ACTION: TASK_COMPLETE`, the last line must be exactly that string with no extra text before or after it in the final response.
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
- Verify closure question-by-question before writing the deliverable: Q3 must have a fully visible ordered top-5 list, and Q4 must have three verified manager names for the top 3 ranked accessions.
- Stop if any answer still depends on an ambiguous filer match, an unverified accession, an unseen ranked item, a noisy/unresolved CUSIP-to-name mapping, or a manager name not directly returned by lookup output.
- Write valid JSON to the exact task-required output path, and only if that path is explicitly allowed. If the task explicitly requires `/root/answers.json`, use it; otherwise do not assume this example path is permitted.
- Before finalizing, confirm each answer is backed by directly observed output and that every final accession, filer, CUSIP, and manager name used in an answer has been directly verified.
- After writing the file, reopen that same output path (`cat` it or parse it in Python) to verify the saved deliverable, valid JSON syntax, and the exact required keys before declaring completion.
- If you continue investigating after writing the file, treat that as evidence the file was premature; resume analysis, resolve the open items, and rewrite the file only after all checks pass.
- If the task requires an exact completion token, emit that exact string as the final line after verification, with no summary, explanation, or extra text before or after it (for example: `ACTION: TASK_COMPLETE`).


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

