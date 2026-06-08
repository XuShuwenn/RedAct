---
name: financial-modeling-qa
description: "Answer financial data analysis questions from Excel data files and PDF background context."
---

# Financial Data Analysis Q&A

## When to Use

- Analyze large financial datasets from Excel
- Answer specific questions about game/match outcomes
- Extract structured answers from data files

## Input Files

- `/root/data.xlsx`: Financial/game data
- `/root/background.pdf`: Context/question background

Critical rule: derive scoring/business logic from the PDF only after you have extracted the relevant rule text completely enough to support the implementation. If PDF extraction is truncated, partial, empty, binary, or cut off mid-sentence, switch extraction method or read smaller targeted sections; do **not** invent missing rules.


## Source-Grounding Rules

## Source-Grounding Rules

- Read the PDF sections that define the scoring/rule system completely before coding any domain logic.
- If a PDF extraction is truncated, cut off mid-sentence, or only shows the opening pages, keep extracting targeted sections until the exact rule definitions, constraints, and exceptions are visible.
- Do **not** infer category formulas, win rules, pairing rules, tie-break behavior, or anomaly handling from partial reads or from your own expectations.
- Verification must be against the source text, not only against self-written code.

## Common Pattern

Match-based calculations:
- Odd games = Player 1, Even games = Player 2
- Match pairs: game 1 vs game 2, game 3 vs game 4
- Answer = (Player1 wins) - (Player2 wins)


- Pair by original game number, not by position in filtered odd/even lists: evaluate `(1,2), (3,4), ...` directly so a missing or invalid game only affects its own pair.
- Before coding, restate the entities being compared (for example: **turn != game != player**) and map the pairing rule explicitly. For match-style tasks here, the default interpretation is: odd/even **game numbers** form a pair; do not infer player assignment from odd/even turns unless the source data explicitly says so.
- Do not silently skip an odd/even pair because one game is missing or incomplete; detect the gap, decide/document how that pair should be treated, and only then aggregate.
- Sanity-check structure before trusting results: if total complete games is odd, if expected pair count does not match the dataset structure, or if any pair is incomplete, investigate before finalizing.

## Output Format

Single number to `/root/answer.txt` (just the number, no text)

- This file is a required deliverable.
- Explicitly create or overwrite `/root/answer.txt`; do not assume it was written indirectly.
- After writing, read `/root/answer.txt` back and verify it contains only the final numeric answer with no extra characters, labels, or explanation.
- If readback is unexpected or ambiguous, rewrite the file deterministically and verify again before finishing.
- Follow the run's exact tool/action and final-response protocol from the system/task instructions; do not invent alternate tool-call syntaxes.
- If the task specifies an exact final completion message (for example, `ACTION: TASK_COMPLETE`), output that exact token verbatim after writing the answer file.
- Do not leave the task at an intermediate analysis state or add extra post-answer wrap-up when a strict completion protocol is given.


## Execution Protocol

## Execution Protocol

- Follow the task/runtime interaction contract exactly. If the prompt specifies a required tool-call schema, tool name, argument format, action format, or completion signal, use that exact format.
- Do **not** default to habitual tool syntax or add extra narrative when the task specifies another format.
- Treat required tool-call syntax and completion tokens as part of correctness, not style.

## Steps

1. Load data from Excel (.xlsx)
2. Parse background question to understand what's needed

2a. Extract the full rule text needed for scoring before coding any logic. If the PDF output is truncated, incomplete, or ambiguous, try another extraction method or inspect more pages/regions until the rule is evidenced from the document.
2b. Treat `/root/background.pdf` as authoritative when it defines scoring, winner rules, filters, or business logic; do **not** infer or invent those rules from spreadsheet structure alone.
2c. Sanity-check the interpretation on the first few records before scaling: verify which rows/columns hold the needed fields and confirm one complete match pair by hand.
3. Filter/aggregate based on game pairing rules

3a. Inspect relevant sheets/rows for blanks, incomplete records, hidden rows/sheets, merged cells, and workbook/formula cues about how missing data should be handled.
3b. Before pairing odd/even games, validate record coverage and identifier continuity after any cleaning or filtering.
3c. Do not use `dropna()` or other cleanup blindly if it can remove turns/games; inspect missing or malformed rows and confirm whether gaps change pairings, match counts, or scoring eligibility.
3d. If Excel headers are not on the first row, detect the real header row before analysis and then re-check downstream grouping/count assumptions.
3e. If multiple plausible treatments of incomplete data produce different answers, resolve the ambiguity from workbook structure, formulas, the PDF, or task instructions before choosing one.
4. Calculate difference in matches won

4a. Validate extraction counts before trusting the result: expected games, expected pairs, and any missing/incomplete records should reconcile with the workbook contents.
4b. Verify every required game pair/matchup was evaluated.
4c. Before finalizing, confirm that winner/scoring logic comes from an explicit rule in the PDF or a clearly labeled outcome field in the workbook.
4d. Do **not** use a convenient heuristic unless the provided materials explicitly define it as the win condition.
4e. If anomalies remain unresolved, stop and investigate before writing `/root/answer.txt`.
5. Write result

5a. Before writing `/root/answer.txt`, run or re-run a concise computation that prints the final totals and answer clearly.
5b. If earlier output was truncated, do a targeted rerun that emits only the decisive numbers. Write the answer only after the final value is visible and reproducible.

## Tips

- openpyxl or pandas for Excel reading
- PyPDF2 or pdfplumber for PDF reading
- Handle missing values appropriately


- When moving from sample inspection to production code, verify the library's indexing convention with one known row/cell first.
- Prefer a tiny end-to-end test on a known row/pair before running the full aggregation.
- If PDF extraction is truncated or cuts off mid-rule, keep extracting or use another PDF reader until the relevant specification is complete.
- Do not zero-fill, silently skip, or otherwise impute missing game/financial values unless the workbook, PDF, or task instructions explicitly support that rule.
- When a record looks incomplete, first check for parsing mistakes, hidden rows/sheets, merged cells, truncated reads, or documented special-case handling.
- If skipping, excluding, or imputing an incomplete record changes the answer, treat that as unresolved evidence and keep searching the source files for the governing rule.
- Compare raw game counts, complete-game counts, generated pair counts, and later non-empty rows against workbook dimensions; mismatches usually mean parsing issues, missing data, or a pairing bug.
- Use workbook outcome/score columns when available; only derive winners from raw events when the rule is explicitly documented.
