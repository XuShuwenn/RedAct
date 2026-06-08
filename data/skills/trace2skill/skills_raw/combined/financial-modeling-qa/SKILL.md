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
- On the first sample records, prove the mapping with one concrete example: identify one odd-numbered game, its paired even-numbered game, and the fields used to decide that matchup's winner before scaling up.
- Do not silently skip an odd/even pair because one game is missing or incomplete; detect the gap, decide/document how that pair should be treated, and only then aggregate.
- Sanity-check structure before trusting results: if total complete games is odd, if expected pair count does not match the dataset structure, or if any pair is incomplete, investigate before finalizing.

## Output Format

Single number to `/root/answer.txt` (just the number, no text)

- This file is a required deliverable.
- Explicitly create or overwrite `/root/answer.txt`; do not assume it was written indirectly.
- After writing, read `/root/answer.txt` back and verify it contains only the final numeric answer with no extra characters, labels, or explanation.
- The number written must match a directly observed final computation result; do not write a value inferred from memory, partial logs, or truncated output.
- If readback is unexpected or ambiguous, rewrite the file deterministically and verify again before finishing.
- Follow the run's exact tool/action and final-response protocol from the system/task instructions; do not invent alternate tool-call syntaxes.
- If the task specifies an exact final completion message (for example, `ACTION: TASK_COMPLETE`), output that exact token verbatim after writing the answer file.
- Do not leave the task at an intermediate analysis state or add extra post-answer wrap-up when a strict completion protocol is given.

- Required finish sequence when a strict completion token is specified: (1) write `/root/answer.txt`, (2) read it back and verify, (3) emit the exact required completion token, and (4) stop with no extra prose after that token.
- Finalization checklist: governing rule text was fully extracted; any missing/incomplete pair or count anomaly has been explicitly resolved from source evidence; `/root/answer.txt` contains only the verified numeric answer; and the final response matches the exact required completion format.


## Execution Protocol

## Execution Protocol

- Follow the task/runtime interaction contract exactly. If the prompt specifies a required tool-call schema, tool name, argument format, action format, or completion signal, use that exact format.
- Do **not** default to habitual tool syntax or add extra narrative when the task specifies another format.
- Treat required tool-call syntax and completion tokens as part of correctness, not style.

## Steps

1. Load data from Excel (.xlsx)
2. Parse background question to understand what's needed

2a. Extract the full rule text needed for scoring before coding any logic. If the PDF output is truncated, incomplete, or ambiguous, try another extraction method or inspect more pages/regions until the rule is evidenced from the document.
2a1. Consider extraction incomplete if it ends mid-sentence or mid-bullet, stops after introductory pages, or omits any scoring category, exception, tie-break, malformed-record rule, or optimization/combination restriction needed for the computation.
2a2. Do not claim to understand or implement the rules until the decisive rule text is fully visible; a binary/blob read, empty output, page-1-only snippet, or failed parser output is not sufficient.
2a3. Capture the exact rule elements you will use before coding, and if any required rule lacks source evidence, continue extraction instead of coding.
2b. Treat `/root/background.pdf` as authoritative when it defines scoring, winner rules, filters, or business logic; do **not** infer or invent those rules from spreadsheet structure alone.
2c. Sanity-check the interpretation on the first few records before scaling: verify which rows/columns hold the needed fields and confirm one complete match pair by hand.
2d. Make an evidence checkpoint before scaling up: for each scoring/win rule you plan to use, verify there is a matching source snippet or explicit workbook field supporting it.
2e. If any PDF/table output is truncated, cut off mid-sentence, or only partially shows the needed rows/columns, do not proceed to final logic yet; rerun a narrower extraction/print that exposes the complete rule text and decisive records.
2f. If scoring combines turns/rows under a game-level restriction, model that restriction explicitly in code and verify one hand-worked example satisfies it; do not use per-turn or per-row maxima as a shortcut when the source defines cross-turn/category constraints.
3. Filter/aggregate based on game pairing rules

3a. Inspect relevant sheets/rows for blanks, incomplete records, hidden rows/sheets, merged cells, and workbook/formula cues about how missing data should be handled.
3a1. Never treat the first blank row/cell as end-of-data by default. In sparse sheets, blanks may be separators; scan later rows and determine the true populated region before stopping extraction.
3a2. If workbook metadata or an initial sheet read shows far more rows than your parsed records, stop and debug the extraction before computing any answer.
3b. Before pairing odd/even games, validate record coverage and identifier continuity after any cleaning or filtering.
3b1. Compare raw row counts to post-cleaning row counts and account for every removed row before trusting the cleaned dataset.
3b2. If a game/turn/match record is missing or malformed, diagnose the cause before excluding it: check header-row selection, sheet choice, hidden rows, merged cells, formula-derived blanks, parsing/indexing mistakes, and whether the workbook/PDF defines a special handling rule.
3b3. If a game/record becomes incomplete only after preprocessing, re-check the raw sheet first; assume a parsing or cleaning issue until disproven.
3c. Do not use `dropna()` or other cleanup blindly if it can remove turns/games; inspect missing or malformed rows and confirm whether gaps change pairings, match counts, or scoring eligibility.
3c1. Do **not** use blanket `dropna()` on the full table unless you have confirmed that every column with missing values is essential to the task and that removing the row will not delete a valid game/record.
3c2. After any filtering/cleaning, compare pre/post row counts and inspect missing game/record identifiers; if a game disappears or a sequence develops gaps, determine why before pairing.
3c3. Preserve original game identifiers during cleaning so pairing stays anchored to source numbering rather than filtered row order.
3c4. Prefer `continue`/skip-with-inspection over `break` when encountering blank rows during row iteration unless you have verified the data region truly ends there.
3d. If Excel headers are not on the first row, detect the real header row before analysis and then re-check downstream grouping/count assumptions.
3d1. After identifying columns from inspection output, run one minimal read through the exact production extraction path and confirm each referenced field lands in the expected variable/cell before processing all rows.
3e. If multiple plausible treatments of incomplete data produce different answers, resolve the ambiguity from workbook structure, formulas, the PDF, or task instructions before choosing one.
3f. If a game/pair is incomplete, malformed, or missing a required row/turn, treat it as a blocker: inspect surrounding rows, hidden/merged content, workbook formulas, parsing assumptions, and source rules before aggregating.
3g. Audit the exact abnormal group directly: list affected IDs, row counts, neighboring rows, and source sheet names rather than debugging a proxy symptom.
3h. If an anomaly could be a parsing artifact, confirm with a second inspection method such as raw worksheet/openpyxl inspection before deciding the data is truly incomplete.
3i. Do **not** silently drop the pair or assign zero/default/best-case scoring unless the PDF, workbook formulas, or explicit task text supports that exact handling.
4. Calculate difference in matches won

4a. Validate extraction counts before trusting the result: expected games, expected pairs, and any missing/incomplete records should reconcile with the workbook contents.
4b. Verify every required game pair/matchup was evaluated.
4b1. Evaluate required pairs by original identifiers directly (for example `(1,2), (3,4), ...`), not by zipping filtered odd/even subsets by position.
4b2. If one member of a required pair is missing, malformed, or unresolved, isolate that pair and resolve/document its treatment before continuing; do not let one missing game shift later matchups.
4b3. Reconcile expected pair count against actual evaluated pairs; complete games, expected pairs from the identifier sequence, evaluated pairs, and any excluded/incomplete pairs must all line up with a justified treatment.
4c. Before finalizing, confirm that winner/scoring logic comes from an explicit rule in the PDF or a clearly labeled outcome field in the workbook.
4d. Do **not** use a convenient heuristic unless the provided materials explicitly define it as the win condition.
4e. If anomalies remain unresolved, stop and investigate before writing `/root/answer.txt`.
4f. Do not write a final numeric answer if it depends on skipped incomplete pairs, unresolved anomalous records, or scoring logic that was not explicitly confirmed from the PDF/workbook.
4g. If you changed header detection, row alignment, column selection, or parsing logic during debugging, rerun the computation from raw input through final aggregation and recheck counts, pair coverage, and winner logic before trusting the final number.
4h. Before finalizing, produce one concise validation view that ties source rules to implementation: show the extracted win/scoring rule, one or two sample game pairs/records, and the derived winner/outcome for those samples.
4i. Cross-check the implemented scoring/winner logic back against the source text explicitly before finalizing: verify each formula, condition, and exception against the PDF or a clearly labeled workbook field.
5. Write result

5a. Before writing `/root/answer.txt`, run or re-run a concise computation that prints the final totals and answer clearly.
5b. If earlier output was truncated, do a targeted rerun that emits only the decisive numbers. Write the answer only after the final value is visible and reproducible.
5c. If a previous computation came from a suspicious or malformed command, rerun the computation in a short, syntactically clean script before writing the answer.
5d. Immediately before writing, run a concise final computation that visibly prints only the governing totals and the exact final numeric answer.
5e. Do not write `/root/answer.txt` while warnings remain such as zero extracted rows, missing games, incomplete pairs, or a mismatch between expected and computed matchup totals.

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

- If a script crashes on a missing turn/game, treat that as a signal to inspect the source rows directly before changing the aggregation logic.
- When debugging data gaps, compare the problematic record in both raw worksheet form and parsed DataFrame form to confirm the omission is real rather than introduced by parsing or cleanup.
- If command output is truncated, rerun with fewer columns/rows, targeted page ranges, or narrower filters until the decisive evidence is fully visible; do not rely on clipped previews.
- Keep a short evidence trail in your working notes: the exact rule text/page or workbook field name that justifies pairing, winner logic, and any handling of incomplete data.
- Before the final write, prefer a compact audit printout over a large dump: parsed rule summary, sample pair evaluations, total pairs, total wins, final answer.
- When a rule says a game score comes from multiple turns/rows with restrictions, carry the category/condition metadata through the computation, not just numeric maxima.
- After cleaning, print a small sample of identifiers around any detected gap so you can tell whether it is true missing data, a parsing error, or an intentional exclusion.
- Do not use `if len(group) == expected_size`-style filtering or similar convenience logic to discard incomplete games/pairs unless the source materials explicitly say incomplete groups should be excluded.
