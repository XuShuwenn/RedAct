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

- Do **not** use external websites, search, or outside references to infer rules, validate a computed answer, or resolve uncertainty unless the task explicitly authorizes that. Resolve uncertainty from the provided workbook/PDF only.
- If source evidence from the provided files is insufficient or ambiguous, keep investigating those files; do not substitute outside context.

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
- Do **not** write the final number until the observable log/tool output shows the full final computation that produces it.
- Sample rows, previews, or partial match listings are not sufficient evidence for the final answer; run one final concise aggregation step that prints the decisive totals before writing.
- Immediately before writing, verify that the numeric value to write is visible in the latest computation output.

- Required finish sequence when a strict completion token is specified: (1) write `/root/answer.txt`, (2) read it back and verify, (3) emit the exact required completion token as the entire final response, and (4) stop with no extra prose before or after that token.
- Finalization checklist: governing rule text was fully extracted; any missing/incomplete pair or count anomaly has been explicitly resolved from source evidence; `/root/answer.txt` contains only the verified numeric answer; and the final response matches the exact required completion format.

- Never substitute a conversational closing for a required completion signal. If a strict completion token is specified, that token itself is the entire final response after verification.


## Execution Protocol

- Start with a protocol preflight: identify the exact required action/tool-call format, allowed tool names, and exact required completion token from the current system/task instructions, then use that format exclusively for the whole run.
- Do **not** mix in alternate tool syntaxes such as XML-style tags, pseudo-tool syntax, ad hoc wrappers, freeform command prose, or unsupported tool names when a strict schema is required.
- Restate the required interaction schema to yourself before the first tool call and follow it verbatim for every action in the run.
- Do **not** assume specific Python packages or shell binaries are installed. If a preferred reader is unavailable, switch immediately to an available method instead of retrying missing tools.
- Treat protocol compliance and completion-token exactness as hard correctness requirements: a correct numeric answer with the wrong action format or wrong completion token is still a failed task.
- If a strict completion token is required, the final response must be exactly that token and nothing else before or after it.

## Execution Protocol

- Follow the task/runtime interaction contract exactly. If the prompt specifies a required tool-call schema, tool name, argument format, action format, or completion signal, use that exact format.
- Do **not** default to habitual tool syntax or add extra narrative when the task specifies another format.
- Treat required tool-call syntax and completion tokens as part of correctness, not style.

## Steps

0. Before any tool use, inspect the system/task instructions for the exact tool-call schema and completion signal. Lock these in first; interface compliance is mandatory.

1. Load data from Excel (.xlsx)
2. Parse background question to understand what's needed
2a0. Before exploring the workbook deeply or writing analysis code, extract the exact task question/prompt from the PDF and restate the deliverable in one line: what quantity must be computed, from which source fields/rules, and what the output format must be.
2a0.1. If you can only read a title, heading, or partial instructions, treat the objective as unknown and continue extracting until the requested metric/question text is visible.
2a0.2. Do **not** infer the target answer from document titles, worksheet names, or a plausible match-based pattern alone.
2a0.3. If the task objective is not yet explicitly grounded from source text, do not write production analysis code or compute a final result.
1a. Before bulk extraction, do a quick workbook structure audit: inspect sheet names, workbook dimensions, the real header row, first actual data row, relevant data columns, and one tail region near the bottom of the populated range.
1b. Do **not** assume row 1 contains headers or column A starts the table. Formatted workbooks may have title blocks, blank rows, or data beginning in later columns.
1c. If an initial parse yields only a tiny fragment, zero rows, or far fewer records than worksheet dimensions suggest, stop and correct header/column/range detection before any scoring logic.

2a. Extract the full rule text needed for scoring before coding any logic. If the PDF output is truncated, incomplete, or ambiguous, try another extraction method or inspect more pages/regions until the rule is evidenced from the document.
2a1. Consider extraction incomplete if it ends mid-sentence or mid-bullet, stops after introductory pages, or omits any scoring category, exception, tie-break, malformed-record rule, or optimization/combination restriction needed for the computation.
2a2. Do not claim to understand or implement the rules until the decisive rule text is fully visible; a binary/blob read, empty output, page-1-only snippet, or failed parser output is not sufficient.
2a2a. If an attempted PDF read yields only messages like `Binary content provided`, parser failure text, package-install logs, exit codes, or no readable rule text, treat that as a failed extraction and immediately try another method/page range; do not cite the failed read as support for the implemented logic.
2a2b. Before scaling up, record at least one quoted or clearly paraphrased rule snippet for each nontrivial transformation or scoring step you will apply.
2a3. Capture the exact rule elements you will use before coding, and if any required rule lacks source evidence, continue extraction instead of coding.
2a4. Also recover the exact task question/output request from the PDF before computing; if the prompt text is not fully visible, treat the task as not yet specified.
2a5. Make a short rule-to-evidence map in working notes: each scoring condition, winner rule, exception, and requested final metric must point to observed source text or a clearly labeled workbook field.
2a6. If extraction attempts fail because of truncation, parser issues, or environment/library problems, keep trying narrower page/region reads or alternate available readers; do **not** switch to an assumed heuristic just to finish the computation.
2b. Treat `/root/background.pdf` as authoritative when it defines scoring, winner rules, filters, or business logic; do **not** infer or invent those rules from spreadsheet structure alone.
2c. Sanity-check the interpretation on the first few records before scaling: verify which rows/columns hold the needed fields and confirm one complete match pair by hand.
2d. Make an evidence checkpoint before scaling up: for each scoring/win rule you plan to use, verify there is a matching source snippet or explicit workbook field supporting it.
2e. If any PDF/table output is truncated, cut off mid-sentence, or only partially shows the needed rows/columns, do not proceed to final logic yet; rerun a narrower extraction/print that exposes the complete rule text and decisive records.
2e1. Do not narrate that data was "processed," "validated," or "extracted correctly" unless the immediately preceding visible command output supports that claim. If the evidence is truncated, blank, omitted, or ambiguous, keep inspecting instead of advancing.
2f. If scoring combines turns/rows under a game-level restriction, model that restriction explicitly in code and verify one hand-worked example satisfies it; do not use per-turn or per-row maxima as a shortcut when the source defines cross-turn/category constraints.
2g. Do not treat a partial rule glimpse as sufficient just because one aspect seems recognizable. If any governing sentence is cut off or any scoring/win condition remains unseen, continue extraction before computing.
2h. Before any full aggregation, state the settled comparison unit explicitly (for example: turn vs turn, game vs game, match vs match). If that interpretation changes later, discard earlier totals produced under the old interpretation and recompute from scratch only after the unit is confirmed.
3. Filter/aggregate based on game pairing rules

3a. Inspect relevant sheets/rows for blanks, incomplete records, hidden rows/sheets, merged cells, and workbook/formula cues about how missing data should be handled.
3a0. Before any `astype(int)`, `range()`, grouping, or pairing logic, normalize the sheet into a clean table: identify the true header row, drop fully empty rows, confirm required columns exist, and inspect sample values/dtypes for key fields.
3a0.1. Normalize identifier columns used for grouping/iteration explicitly: if Excel imported game IDs as floats like `8.0`, convert them to validated integer identifiers only after confirming non-nullness and integral values.
3a0.2. Do **not** cast whole columns to `int` blindly. First isolate non-empty task-relevant rows, inspect `NaN`/blank cells, and only then convert the specific columns needed for computation.
3a0.3. Before using an identifier in `range()` or as a pairing key, verify one concrete parsed example shows the expected Python type/value.
3a1. Never treat the first blank row/cell as end-of-data by default. In sparse sheets, blanks may be separators; scan later rows and determine the true populated region before stopping extraction.
3a2. If workbook metadata or an initial sheet read shows far more rows than your parsed records, stop and debug the extraction before computing any answer.
3a2a. Reconcile worksheet dimensions, parsed non-header row counts, and derived game/match counts numerically. If `max_row`, previewed dimensions, loaded rows, or identifier sequences disagree, treat that as a blocker until you can explain every missing row/game.
3a2b. If any row preview is visibly truncated, shifted, or missing expected fields after a parsing error or rerun, treat the extraction as untrusted: inspect the raw worksheet with a second method, confirm dimensions/header alignment, and rerun extraction before analysis.
3a2c. After any parsing exception or cleaning failure, do an explicit structure re-check before using the data: workbook/sheet names, used range, header row, total populated rows, and counts per game/turn/match identifier must reconcile with the source.
3a2d. If identifier previews skip values or grouped totals imply dropped records, inspect the omitted IDs directly before aggregation; do not continue with an unexplained subset.
3b. Before pairing odd/even games, validate record coverage and identifier continuity after any cleaning or filtering.
3b0. Run a preflight integrity check before any indexed/grouped batch logic: count records per game/match, list any IDs with missing expected rows/turns, and confirm the code path for incomplete groups is safe.
3b0a. If the task or source rules imply each game has a fixed structure (for example, exactly 2 turns per game), verify that invariant explicitly before computing.
3b0b. Do **not** index into the first row/turn of a group until you have proved that group is non-empty and structurally complete or have explicit fallback handling.
3b0c. If any game/pair is incomplete, malformed, or empty, stop the full batch run and inspect those specific IDs first rather than letting the main script crash with an indexing error.
3b1. Compare raw row counts to post-cleaning row counts and account for every removed row before trusting the cleaned dataset.
3b1a. If any script or tool run exits with an error, exception, traceback, parse failure, or non-zero exit status, treat every printed count or aggregate from that run as provisional only. Fix the failure and rerun cleanly before using those numbers in downstream scoring or final results.
3b1b. Reconcile dataset cardinalities explicitly before scoring: workbook row/turn count, parsed turn count, min/max game identifiers, missing game IDs, and derived complete-game count must agree with the source or have a source-backed explanation.
3b1c. If the workbook visibly contains IDs through an endpoint but parsed counts imply fewer rows/games, stop and debug extraction/parsing rather than continuing with partial data.
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
3e1. Treat missing turns/rows/games as a specification question, not merely a robustness issue: do **not** skip, partially score, impute, zero-fill, or assign default contribution to an incomplete record unless the PDF, workbook formulas, or task instructions support that exact treatment.
3e2. If two plausible treatments produce different final numbers, treat the task as unresolved at that point: do not write `/root/answer.txt` or finalize until one treatment is selected by explicit source evidence.
3e3. Record the competing treatments and the source-backed reason for choosing one; if no source-backed reason exists yet, keep investigating rather than committing to either branch.
3f. If a game/pair is incomplete, malformed, or missing a required row/turn, treat it as a blocker: inspect surrounding rows, hidden/merged content, workbook formulas, parsing assumptions, and source rules before aggregating.
3f1. Do not continue to full scoring/aggregation while any detected incomplete or malformed game remains unexplained. Resolve each anomaly explicitly by one of: confirming a parsing mistake and fixing it, finding a source-defined handling rule, or proving from source evidence that exclusion is required.
3f2. After anomaly handling, print a compact reconciliation showing: total raw games/records, anomalous IDs found, treatment for each anomalous ID, and the final set actually scored. If any anomaly lacks an explicit treatment, stop instead of computing a final answer.
3f3. If validation surfaces a specific missing turn/game or an incomplete game record, do **not** finalize any numeric answer until that exact anomaly has a source-supported treatment.
3g. Audit the exact abnormal group directly: list affected IDs, row counts, neighboring rows, and source sheet names rather than debugging a proxy symptom.
3h. If an anomaly could be a parsing artifact, confirm with a second inspection method such as raw worksheet/openpyxl inspection before deciding the data is truly incomplete.
3h1. If a supposedly incomplete game/record appears after parsing, assume the extraction/model may be wrong until you have checked the raw worksheet layout around that ID: header row, blank separators, merged cells, hidden rows, and row-to-game mapping.
3h2. Do **not** change the aggregation logic to handle a one-turn/incomplete game unless you have source evidence that the workbook truly contains such a case and the governing rule says how to treat it.
3i. Do **not** silently drop the pair or assign zero/default/best-case scoring unless the PDF, workbook formulas, or explicit task text supports that exact handling.
3i1. When data is malformed or incomplete, make the handling rule explicit in working notes/code comments before recomputing: identify the affected game/pair IDs, the exact reconstruction or exclusion rule, and the source evidence for it.
3i2. Prefer pair-local handling over global realignment: preserve original identifiers and resolve the abnormal pair directly rather than shifting later pairs to keep counts aligned.
3i3. After any repair/reconstruction logic, run a targeted check printing the affected records/pairs and the resulting treatment before trusting the full aggregate.
3i4. If a game or match is incomplete and the governing materials do not explicitly say how to treat it, stop final aggregation and keep investigating; do **not** choose an ad hoc policy just to complete the calculation.
4. Calculate difference in matches won

4a. Validate extraction counts before trusting the result: expected games, expected pairs, and any missing/incomplete records should reconcile with the workbook contents.
4a1. Reconcile counts across every pipeline stage before finalizing: raw extracted records, parsed usable records, scored games, evaluated pairs, and expected pair count from identifiers must either match expectations or have an explicitly source-justified difference.
4a2. If total turns is not divisible by the expected turns per game, if odd/even game counts differ, or if counts drop unexpectedly at any stage, stop and identify the exact missing identifier(s) and cause before computing or writing the final answer.
4a3. Treat an unexplained count mismatch or suspicious early aggregate as a blocker, not a warning: do not aggregate wins/losses from a knowingly incomplete or contradictory scored set.
4b. Verify every required game pair/matchup was evaluated.
4b1. Evaluate required pairs by original identifiers directly (for example `(1,2), (3,4), ...`), not by zipping filtered odd/even subsets by position.
4b2. If one member of a required pair is missing, malformed, or unresolved, isolate that pair and resolve/document its treatment before continuing; do not let one missing game shift later matchups.
4b3. Reconcile expected pair count against actual evaluated pairs; complete games, expected pairs from the identifier sequence, evaluated pairs, and any excluded/incomplete pairs must all line up with a justified treatment.
4b4. After building comparisons, reconcile pair-slot coverage explicitly: from the original identifier sequence, count expected odd-even slots `(1,2), (3,4), ...`, then account for each slot as evaluated, tied, or blocked by unresolved missing/malformed data.
4b5. If a missing game causes pair indices to skip or reduces the number of evaluated comparisons, stop and resolve/document the exact treatment of the affected slot before producing a final answer.
4b6. Do **not** report aggregate wins/losses as final unless wins + losses + ties + explicitly justified blocked pairs equals the intended number of pair slots.
4c. Before finalizing, confirm that winner/scoring logic comes from an explicit rule in the PDF or a clearly labeled outcome field in the workbook.
4d. Do **not** use a convenient heuristic unless the provided materials explicitly define it as the win condition.
4e. If anomalies remain unresolved, stop and investigate before writing `/root/answer.txt`.
4e1. Known unresolved integrity issues are blockers, not warnings: missing turns/rows, blank cells where a required record should exist, mismatched game or pair counts, workbook inspection showing an absent expected entry, or alternative treatments yielding different final numbers all require resolution from the provided sources before any final answer.
4e2. Do **not** write a provisional answer despite an anomaly you already detected. First determine whether the issue is a parsing mistake, a workbook-defined omission rule, or true missing data with explicit source-supported handling.
4e3. A final answer is allowed only after the abnormal record's handling is tied to explicit evidence from the PDF, workbook formulas, or task instructions.
4f. Do not write a final numeric answer if it depends on skipped incomplete pairs, unresolved anomalous records, or scoring logic that was not explicitly confirmed from the PDF/workbook.
4g. If you changed header detection, row alignment, column selection, or parsing logic during debugging, rerun the computation from raw input through final aggregation and recheck counts, pair coverage, and winner logic before trusting the final number.
4h. Before finalizing, produce one concise validation view that ties source rules to implementation: show the extracted win/scoring rule, one or two sample game pairs/records, and the derived winner/outcome for those samples.
4i. Cross-check the implemented scoring/winner logic back against the source text explicitly before finalizing: verify each formula, condition, and exception against the PDF or a clearly labeled workbook field.
4j. Before writing the answer, restate in one line the exact quantity requested by the task prompt and the exact computation that produced it. If you cannot quote or paraphrase the prompt from recovered source text, do not finalize.
4k. Treat any interpretation change as invalidating prior aggregates. If you switch comparison units or anomaly-handling logic, rerun the entire calculation and do not reuse counts or samples from the superseded logic.
4l. If warnings such as `skipping`, `missing pair`, `incomplete game`, `unresolved anomaly`, or mismatched evaluated-pair counts remain, the computation is provisional until you remove the warning condition or justify the exact handling from source evidence and recompute.
5. Write result

5pre. Pre-write gate:
- Confirm the latest visible computation output contains the exact final totals/aggregate from which the answer is derived.
- If that check fails, do not write yet; fix the evidence gap first.

5a. Before writing `/root/answer.txt`, run or re-run a concise computation that prints the final totals and answer clearly.
5b. If earlier output was truncated, do a targeted rerun that emits only the decisive numbers. Write the answer only after the final value is visible and reproducible.
5c. If a previous computation came from a suspicious or malformed command, rerun the computation in a short, syntactically clean script before writing the answer.
5d. Immediately before writing, run a concise final computation that visibly prints only the governing totals and the exact final numeric answer.
5e. Do not write `/root/answer.txt` while warnings remain such as zero extracted rows, missing games, incomplete pairs, or a mismatch between expected and computed matchup totals.
5f. Immediately before writing the answer, produce a compact final calculation trace that shows the decisive totals used to obtain the final number.
5g. Do not write `/root/answer.txt` if any prior script/run produced a different final numeric answer that has not been reconciled, or if an earlier computation produced an answer alongside a warning/anomaly.
5h. If the final computation output is truncated, missing, or not clearly tied to the written number, rerun a narrower script that prints only those decisive totals, then write the answer from that visible result.
5i. If the task requires an exact completion token, emit it immediately after the successful readback and then end the response with nothing else.

4m. If later inspection contradicts any earlier assumption used in the computation (for example missing turns, irregular group sizes, unexpected headers, a field not meaning what you assumed, or counts that do not reconcile), invalidate the prior result and re-derive the method from the observed schema/rules before recomputing.
4n. Do not keep old aggregate totals as tentative evidence once a contradiction is found; fix the parsing/model first, then rerun end-to-end from raw input.

5j. Do not finalize just because one script produced a number. Finalize only after the final computation and a successful visible validation step both complete without truncation or ambiguity.
5k. If malformed-data handling, header detection, row alignment, column selection, or parsing logic changed during debugging, rerun the full computation from raw inputs after the change and confirm the final number still matches the explicit validation output.
5l. Final artifact check must be explicit in the log: read `/root/answer.txt` back after writing and confirm it contains only the final number before emitting any completion signal.
5m. If an existing script failed, read the current file and traceback location before editing or replacing it; inspect the exact failing code path first rather than stacking fresh workaround scripts on top of an unreviewed implementation.

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

- Prefer short, reproducible inspection commands that print exactly the needed evidence: targeted PDF rule text, workbook dimensions, sheet names, affected IDs, sample rows, and decisive totals.
- If a visible truncated phrase ends abruptly, treat that as evidence the rules or question are not yet fully recovered, not as permission to infer the rest.
- If a computation prints totals and then crashes or emits warnings about skipped games, missing pairs, incomplete turns, or unresolved records, treat that run as a debugging aid only; fix the issue or source-ground the handling rule, then rerun cleanly before writing `/root/answer.txt`.
- Before pairing/scoring, compare and reconcile: raw rows/turns, parsed usable rows/turns, unique game IDs, missing IDs, complete games, expected pairs, and final outcome counts.
- When a later validation disagrees with an earlier result, make a small diff check: same rows, same pair coverage, same scoring rule, same anomaly handling. Do not finalize until the discrepancy is explained.
- Before final write, confirm the final number answers the recovered task question itself, not just a plausible statistic you computed from the workbook.
- Treat any `IndexError` or empty-selection failure in grouping or pairing code as evidence of an unchecked structural assumption; debug the offending IDs before rerunning the full workflow.
