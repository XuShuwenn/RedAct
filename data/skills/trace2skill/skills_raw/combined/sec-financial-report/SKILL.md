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
- Compare holdings changes, rank by dollar increase
- Do not proceed until both Berkshire accession numbers are recovered verbatim from visible Q2 and Q3 filing-index or full `COVERPAGE.tsv` rows. If an accession-aware analyzer such as `one_fund_analysis.py` is available, prefer reusing it after confirming those accessions.
- If the ranked increase output is clipped or only a banner/header is visible, rerun via a narrower query or saved script that prints the full ordered top 5 CUSIPs before answering.

### Q4: Top 3 fund managers invested in Palantir (Q3)
- Inspect Q3 `INFOTABLE.tsv` headers or a sample row first so `CUSIP` and `VALUE` are confirmed from this dataset.
- Use the sequence: issuer/ticker → exact CUSIP → top holder accessions ranked by infotable `VALUE` → manager-name resolution from those accessions through Q3 `COVERPAGE.tsv`.
- If a ranking tool returns accession numbers instead of display names, do a second lookup against filing metadata/COVERPAGE records and only output verified human-readable manager names.


### Evidence checks before finalizing any question
- Q1/Q2: confirm the Renaissance accession number from the actual Q3 `COVERPAGE` match before reading any values. For Q1, verify from schema/metadata or dataset documentation that the field used truly corresponds to AUM; do not assume `TABLEVALUETOTAL` is AUM unless the dataset explicitly defines it that way.
- Q2: if the filing or tool distinguishes total holdings from stock holdings, answer with the metric that matches the question text rather than assuming they are equivalent.
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
- After any script produces ranked CUSIPs or manager names, reproduce at least the final selected rows with a simple direct query against the source TSV/XML data before trusting `answers.json`.


## Output Format

JSON at `/root/answers.json`:
```json
{
    "q1_answer": number,
    "q2_answer": number,
    "q3_answer": ["cusip1", "cusip2", "cusip3", "cusip4", "cusip5"],
    "q4_answer": ["fund1", "fund2", "fund3"]
}
```


Finalization checklist:
- Re-read the task instructions immediately before finalization and confirm the required completion protocol: exact tool/action format during execution, exact output path, and exact final completion token.
- Stop if any answer still depends on an ambiguous filer match, an unverified accession, an unseen ranked item, or a manager name not directly returned by lookup output.
- Write valid JSON to `/root/answers.json` with exactly the keys `q1_answer`, `q2_answer`, `q3_answer`, `q4_answer`.
- Before finalizing, confirm each answer is backed by directly observed output and that no accession, filer, or manager name used in an answer is still unverified.
- After writing the file, reopen it (`cat /root/answers.json` or parse it in Python) to verify the saved deliverable, valid JSON syntax, and the exact required keys before declaring completion.
- If the task requires an exact completion token, emit that exact string as the final line after verifying `/root/answers.json`, with no summary, explanation, or extra text before or after it (for example: `ACTION: TASK_COMPLETE`).


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

