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


## Execution Guardrails

## Execution Guardrails

- Follow the exact action/output protocol required by the task environment. If the task specifies an Action schema or an exact completion token, use that exact format throughout and end exactly as required.
- Read and write only in explicitly allowed directories. Do not use `/tmp` or other scratch locations unless the task explicitly permits them.
- Use only values that appear explicitly in observed tool output or source files. Do not guess accession numbers, fund names, manager mappings, CUSIPs, counts, or rankings from partial matches or truncated output.
- If a grep/search/analyzer result is ambiguous, truncated, or cut off, treat it as unresolved and rerun with narrower filtering, redirection, or a short saved script until the needed lines are fully visible.
- Treat incomplete Python one-liners or cut-off shell output as no result; rerun using a simpler command or saved script and wait for the computed output before concluding.

## Questions

### Q1: Renaissance Technologies AUM in Q3
- Fuzzy search COVERPAGE for "renaissance technologies"
- Get accession_number, then find AUM

### Q2: Number of stocks held by Renaissance
- Same approach, count holdings

### Q3: Top 5 increased stocks by Berkshire Hathaway (Q2→Q3)
- Find Q2 and Q3 accession numbers for Berkshire
- Compare holdings changes, rank by dollar increase

### Q4: Top 3 fund managers invested in Palantir (Q3)
- Find Palantir CUSIP, then find top managers by share value


### Evidence checks before finalizing any question
- Q1/Q2: confirm the Renaissance accession number from the actual COVERPAGE match before reading AUM or counting holdings.
- Q2: if the filing or tool distinguishes total holdings from stock holdings, answer with the metric that matches the question text rather than assuming they are equivalent.
- Q3: confirm Berkshire Hathaway's Q2 and Q3 accession numbers from observed filing-index or cover-page records before quarter-over-quarter comparison; if the top-5 output is clipped, rerun and capture the five CUSIPs in a structured format.
- Q4: interpret "share value" as the 13F infotable `VALUE` field unless the prompt explicitly requires ranking by shares, and only report manager names directly recovered for the top Palantir-holder accessions.


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
- Write valid JSON to `/root/answers.json` with exactly the keys `q1_answer`, `q2_answer`, `q3_answer`, `q4_answer`.
- Before finalizing, confirm each answer is backed by directly observed output and that no accession, filer, or manager name used in an answer is still unverified.
- After writing the file, reopen it (`cat /root/answers.json` or parse it in Python) to verify the saved deliverable.
- If the task requires an exact completion token, emit it exactly after writing the JSON file (for example: `ACTION: TASK_COMPLETE`) and do not add extra prose after it.


## Tips

- Parse SEC 13F filings (XML/HTML format)
- Use fuzzy matching for fund names
- Calculate holdings changes (price × shares)


- Verify the matched filer identity before using any fuzzy-search result; do not substitute a different fund because it is the top fuzzy hit. When multiple similar filers appear, confirm the full manager name, quarter, and amendment status in `COVERPAGE.tsv` before choosing an accession.
- For key IDs (manager, accession, CUSIP), prefer direct extraction from source filing metadata over inference from partial lines.
- For comparison questions, ensure the full ranked holdings or delta output is visible before selecting top CUSIPs; prefer queries or scripts that emit exact identifiers and final ranked lists in machine-readable form.
- Validate field semantics before answering business-metric questions. Do not assume a summary field such as `TABLEVALUETOTAL` equals the requested metric unless the dataset schema explicitly supports that mapping.
- If you write a script to compute answers, verify the key inputs it uses (selected accession numbers, fund names, quarters) before trusting `answers.json`.

