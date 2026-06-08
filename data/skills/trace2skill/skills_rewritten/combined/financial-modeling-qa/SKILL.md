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
- Do **not** adopt this pattern until the workbook schema is confirmed from real loaded records. First verify the true header row, required columns, one concrete game ID, and how rows map to games/turns in the actual sheet; only then apply odd/even game pairing or player ownership rules.
- Odd games = Player 1, Even games = Player 2
- Match pairs: game 1 vs game 2, game 3 vs game 4
- Answer = (Player1 wins) - (Player2 wins)


- Pair by original game number, not by position in filtered odd/even lists: evaluate `(1,2), (3,4), ...` directly so a missing or invalid game only affects its own pair.
- Before coding, restate the entities being compared (for example: **turn != game != player**) and map the pairing rule explicitly. For match-style tasks here, the default interpretation is: odd/even **game numbers** form a pair; do not infer player assignment from odd/even turns unless the source data explicitly says so.
- On the first sample records, prove the mapping with one concrete example: identify one odd-numbered game, its paired even-numbered game, and the fields used to decide that matchup's winner before scaling up.
- Explicitly test the common confusion point: odd/even assignment applies to original **game numbers** unless the source text says otherwise; do not apply odd/even logic to turn numbers, row positions, or filtered subset order.
- Do **not** state or use an odd-game/even-game player assignment unless you have explicit source evidence for that mapping from the PDF or a clearly labeled workbook field. If labels are not source-grounded yet, describe the comparison in neutral pair terms until they are.
- Do not silently skip an odd/even pair because one game is missing or incomplete; detect the gap, decide/document how that pair should be treated, and only then aggregate.
- Sanity-check structure before trusting results: if total complete games is odd, if expected pair count does not match the dataset structure, or if any pair is incomplete, investigate before finalizing.

## Output Format

Single number to the exact task-required answer file path (often `/root/answer.txt`) (just the number, no text)

- This file is a required deliverable.
- First confirm the required output path is explicitly allowed by the current runtime/task constraints before writing.
- Do **not** assume `/root/answer.txt` is always permitted just because this skill often uses it; if the runtime/task specifies a different writable location, follow that instead.
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
- Final response self-check for strict-token tasks: after successful readback, send exactly the required completion token verbatim as the entire final message. Do not add summaries, confirmations, explanations, Markdown, punctuation, or courtesy text.
- When a strict completion token is required, the numeric result belongs in the answer file, not in chat.
- Once the answer file has been written, read back successfully, and the latest visible computation supports the exact number, stop further investigation unless a live contradiction remains.


## Execution Protocol

- Start with a protocol preflight: identify the exact required action/tool-call format, allowed tool names, and exact required completion token from the current system/task instructions, then use that format exclusively for the whole run.
- Do **not** mix in alternate tool syntaxes such as XML-style tags, pseudo-tool syntax, ad hoc wrappers, freeform command prose, or unsupported tool names when a strict schema is required.
- Restate the required interaction schema to yourself before the first tool call and follow it verbatim for every action in the run.
- Do **not** assume specific Python packages or shell binaries are installed. If a preferred reader is unavailable, switch immediately to an available method instead of retrying missing tools.
- Treat protocol compliance and completion-token exactness as hard correctness requirements: a correct numeric answer with the wrong action format or wrong completion token is still a failed task.
- If a strict completion token is required, the final response must be exactly that token and nothing else before or after it.

- Protocol lock-in is a hard precondition: before the first tool call, identify the exact required action wrapper/schema, allowed tool names, argument shape, authorized output path, and exact completion token from the current instructions, then use only that schema for the whole run.
- If the runtime specifies a concrete pattern (for example, `Thought:` plus `Action:` JSON for `bash`), mirror that pattern literally on every tool call. Do **not** switch formats mid-run or use XML-style tags, pseudo-function calls, unsupported helper tools, freeform shell prose, or habitual syntax from another environment.
- After each action, wait for and inspect the corresponding visible result before proceeding. Do **not** claim data was extracted, validated, or processed unless the immediately preceding output shows that evidence.
- Do **not** use web search or other external lookup for rule interpretation, validation, or confidence boosting unless the task explicitly authorizes it.
- If you realize mid-run that you used the wrong tool schema or unsupported tools, treat prior completion status as invalid: switch to the required schema, recompute or re-verify as needed under that schema, and finish only with the exact required completion token.

## Execution Protocol

- Follow the task/runtime interaction contract exactly. If the prompt specifies a required tool-call schema, tool name, argument format, action format, or completion signal, use that exact format.
- Do **not** default to habitual tool syntax or add extra narrative when the task specifies another format.
- Treat required tool-call syntax and completion tokens as part of correctness, not style.

## Steps

0. Before any tool use, inspect the system/task instructions for the exact tool-call schema and completion signal. Lock these in first; interface compliance is mandatory.
0a. Before any substantive analysis, make a one-line working checklist with: exact tool/action format, allowed tool name(s), authorized answer path, exact completion token, exact deliverable, and required output file. If any of these is still unknown, continue protocol/source extraction instead of computing.
0b. Protocol self-check before first action: confirm the syntax you will use matches the runtime instructions exactly in structure, and do not switch tool syntaxes mid-run.

1. Load data from Excel (.xlsx)
2. Parse background question to understand what's needed
2a0. Before exploring the workbook deeply or writing analysis code, extract the exact task question/prompt from the PDF and restate the deliverable in one line: what quantity must be computed, from which source fields/rules, and what the output format must be.
2a0.a. Do not treat a document title, section heading, or familiar task pattern as the objective. The task question is established only when the requested quantity and output requirement are explicitly visible in source text.
2a0.1. If you can only read a title, heading, or partial instructions, treat the objective as unknown and continue extracting until the requested metric/question text is visible.
2a0.2. Do **not** infer the target answer from document titles, worksheet names, or a plausible match-based pattern alone.
2a0.3. If the task objective is not yet explicitly grounded from source text, do not write production analysis code or compute a final result.
1a. Before bulk extraction, do a quick workbook structure audit: inspect sheet names, workbook dimensions, the real header row, first actual data row, relevant data columns, and one tail region near the bottom of the populated range.
1a1. During that audit, inspect raw cells far enough down the sheet to locate the true table start; do not trust only the top preview when the workbook may contain title rows, blank bands, or headers starting later.
1a2. During that audit, inspect the full populated column span for representative rows, not just the presumed main table block. If unexpected non-empty unnamed or far-right columns appear, test whether they are a shifted continuation, side-by-side table, or other task-relevant record area.
1a3. Reconcile the first parse against worksheet dimensions immediately. If the parsed row count is tiny relative to `max_row` or the used range, treat the extraction path as wrong and fix layout detection before any scoring.
1b. Do **not** assume row 1 contains headers or column A starts the table. Formatted workbooks may have title blocks, blank rows, or data beginning in later columns.
1c. If an initial parse yields only a tiny fragment, zero rows, or far fewer records than worksheet dimensions suggest, stop and correct header/column/range detection before any scoring logic.

2a. Extract the full rule text needed for scoring before coding any logic. If the PDF output is truncated, incomplete, or ambiguous, try another extraction method or inspect more pages/regions until the rule is evidenced from the document.
2a1. Consider extraction incomplete if it ends mid-sentence or mid-bullet, stops after introductory pages, or omits any scoring category, exception, tie-break, malformed-record rule, or optimization/combination restriction needed for the computation.
2a2. Do not claim to understand or implement the rules until the decisive rule text is fully visible; a binary/blob read, empty output, page-1-only snippet, or failed parser output is not sufficient.
2a2a. If an attempted PDF read yields only messages like `Binary content provided`, parser failure text, package-install logs, exit codes, or no readable rule text, treat that as a failed extraction and immediately try another method/page range; do not cite the failed read as support for the implemented logic.
2a2a1. Minimum recovery sequence for failed PDF extraction: try another available PDF reader, then narrower page ranges or targeted sections, then text-only extraction of the pages most likely to contain the rules/question. Continue until readable rule text is visible.
2a2a2. Do not say you "understand," "confirmed," or "implemented" a PDF-defined rule until the readable rule text itself is visible in the log/output.
2a2a3. Before scaling up, show at least one visible rule snippet or clear paraphrase for the task objective and one for each nontrivial scoring or winner decision used by the code.
2a2b. Before scaling up, record at least one quoted or clearly paraphrased rule snippet for each nontrivial transformation or scoring step you will apply.
2a3. Capture the exact rule elements you will use before coding, and if any required rule lacks source evidence, continue extraction instead of coding.
2a4. Also recover the exact task question/output request from the PDF before computing; if the prompt text is not fully visible, treat the task as not yet specified.
2a5. Make a short rule-to-evidence map in working notes: each scoring condition, winner rule, exception, and requested final metric must point to observed source text or a clearly labeled workbook field.
2a6. If extraction attempts fail because of truncation, parser issues, or environment/library problems, keep trying narrower page/region reads or alternate available readers; do **not** switch to an assumed heuristic just to finish the computation.
2a6a. Hard gate: do **not** write production scoring/transformation code while the governing PDF rules are only partially visible. A title page, sample outcome, or cut-off rule excerpt is not enough; first recover the complete rule text for every scoring category, exception, and requested final metric.
2a6b. Do not treat repeated extraction of only the same opening rule fragment as confirmation that the rules were fully recovered. Keep extracting until the closing conditions, exceptions, and edge-case handling needed for the computation are visible.
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
3a0.4. Before writing any production script, prove the table is computation-ready on a tiny sample: show the detected header row, required columns, non-empty row count, presence/absence of `NaN` in key fields, and the normalized type/value of one identifier you will group or iterate on. If any of these checks fail, fix extraction/cleaning first instead of coding around the failure.
3a0.5. For identifier columns used in pairing or `range()`, normalize with an explicit validation sequence: isolate relevant non-null rows, confirm values are integral, convert to integer once, and then use only the normalized integer column for grouping, sorting, and iteration. Do not mix float and int versions of the same identifier in the same workflow.
3a1. Never treat the first blank row/cell as end-of-data by default. In sparse sheets, blanks may be separators; scan later rows and determine the true populated region before stopping extraction.
3a2. If workbook metadata or an initial sheet read shows far more rows than your parsed records, stop and debug the extraction before computing any answer.
3a2a. Reconcile worksheet dimensions, parsed non-header row counts, and derived game/match counts numerically. If `max_row`, previewed dimensions, loaded rows, or identifier sequences disagree, treat that as a blocker until you can explain every missing row/game.
3a2b. If any row preview is visibly truncated, shifted, or missing expected fields after a parsing error or rerun, treat the extraction as untrusted: inspect the raw worksheet with a second method, confirm dimensions/header alignment, and rerun extraction before analysis.
3a2c. After any parsing exception or cleaning failure, do an explicit structure re-check before using the data: workbook/sheet names, used range, header row, total populated rows, and counts per game/turn/match identifier must reconcile with the source.
3a2d. If identifier previews skip values or grouped totals imply dropped records, inspect the omitted IDs directly before aggregation; do not continue with an unexplained subset.
3b. Before pairing odd/even games, validate record coverage and identifier continuity after any cleaning or filtering.
3b0. Run a preflight integrity check before any indexed/grouped batch logic: count records per game/match, list any IDs with missing expected rows/turns, and confirm the code path for incomplete groups is safe.
3b0d. Do this integrity check before producing any aggregate win/loss/result numbers. Early totals computed before anomaly detection are provisional and must not be reused as evidence.
3b0e. Do **not** access `group.iloc[0]`, `[0]`, or equivalent direct positional rows in production scoring code until a precheck has proved the group is present and structurally valid, or you have explicit source-backed handling for that exact anomaly.
3b0f. If a supposedly fixed-structure record is incomplete (for example, a 2-turn game with only 1 observed turn), treat that exact game/pair as unresolved and block final aggregation until you determine from the workbook/PDF whether this is a parsing artifact or a source-defined exception.
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
3e4. When repairing or accommodating malformed data, make the rule explicit in the visible workflow: identify the affected IDs, state the exact reconstruction/exclusion rule, show the source evidence or structural proof for it, and run a targeted check on those cases before recomputing the full aggregate.
3e5. If two tested treatments yield different final numeric answers, treat the task as blocked until one branch is selected by explicit PDF/workbook/task evidence. Do not write the answer file and do not emit any completion token while that divergence remains unresolved.
3e6. "Skip the incomplete game/pair" is itself a handling policy and requires explicit source support; do not adopt skipping, zero-fill, default win/loss, or "use only complete games" as a default cleanup choice.
3f. If a game/pair is incomplete, malformed, or missing a required row/turn, treat it as a blocker: inspect surrounding rows, hidden/merged content, workbook formulas, parsing assumptions, and source rules before aggregating.
3f1. Do not continue to full scoring/aggregation while any detected incomplete or malformed game remains unexplained. Resolve each anomaly explicitly by one of: confirming a parsing mistake and fixing it, finding a source-defined handling rule, or proving from source evidence that exclusion is required.
3f2. After anomaly handling, print a compact reconciliation showing: total raw games/records, anomalous IDs found, treatment for each anomalous ID, and the final set actually scored. If any anomaly lacks an explicit treatment, stop instead of computing a final answer.
3f3. If validation surfaces a specific missing turn/game or an incomplete game record, do **not** finalize any numeric answer until that exact anomaly has a source-supported treatment.
3g. Audit the exact abnormal group directly: list affected IDs, row counts, neighboring rows, and source sheet names rather than debugging a proxy symptom.
3h. If an anomaly could be a parsing artifact, confirm with a second inspection method such as raw worksheet/openpyxl inspection before deciding the data is truly incomplete.
3h0. For spreadsheets with irregular or extra populated columns, inspect the raw row values across the entire used range around the affected ID. A supposedly incomplete game/record may be split across side-by-side table blocks or shifted columns rather than absent.
3h1. If a script reports an impossible structure, inspect the exact affected IDs in the raw worksheet layout first and confirm whether header choice, blank separators, row alignment, or parsing created the anomaly before changing scoring logic.
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
4a3a. For large datasets, run a plausibility check on the first full aggregate: if the workbook has many games/rows but the computed wins/losses/ties cover only a small handful of pairs, treat that as a logic/parsing failure and debug immediately.
4a3b. Compare observed dataset size to aggregate coverage in one line, e.g. `games=<n>, expected_pairs=<m>, evaluated_pairs=<k>`; if `k` is below `m` without a source-backed explanation, stop and fix the pipeline.
4a3c. Treat contradictory integrity summaries as a hard stop. Examples: visible identifier endpoints disagree with extracted counts, a game is reported incomplete while totals still claim all games are complete, or pair/game totals cannot all be true at once.
4b. Verify every required game pair/matchup was evaluated.
4b1. Evaluate required pairs by original identifiers directly (for example `(1,2), (3,4), ...`), not by zipping filtered odd/even subsets by position.
4b2. If one member of a required pair is missing, malformed, or unresolved, isolate that pair and resolve/document its treatment before continuing; do not let one missing game shift later matchups.
4b3. Reconcile expected pair count against actual evaluated pairs; complete games, expected pairs from the identifier sequence, evaluated pairs, and any excluded/incomplete pairs must all line up with a justified treatment.
4b4. After building comparisons, reconcile pair-slot coverage explicitly: from the original identifier sequence, count expected odd-even slots `(1,2), (3,4), ...`, then account for each slot as evaluated, tied, or blocked by unresolved missing/malformed data.
4b5. If a missing game causes pair indices to skip or reduces the number of evaluated comparisons, stop and resolve/document the exact treatment of the affected slot before producing a final answer.
4b6. Do **not** report aggregate wins/losses as final unless wins + losses + ties + explicitly justified blocked pairs equals the intended number of pair slots.
4b6a. Compute and print the coverage equation explicitly before finalizing: `expected_pair_slots =` pair slots implied by the original identifier sequence, and `evaluated_outcomes = wins + losses + ties + source-justified blocked/excluded pairs`. If these are not equal, stop and investigate.
4b6b. For datasets with identifiers spanning a visible min/max range, reconcile that range against the parsed unique IDs and list any missing IDs before trusting pair totals.
4b7. If any game is missing and pairing is by original adjacent identifiers, print the affected slot explicitly (for example, `(7,8)`), state its treatment, and confirm that later pairs still use original identifiers rather than shifting by filtered position.
4c. Before finalizing, confirm that winner/scoring logic comes from an explicit rule in the PDF or a clearly labeled outcome field in the workbook.
4d. Do **not** use a convenient heuristic unless the provided materials explicitly define it as the win condition.
4e. If anomalies remain unresolved, stop and investigate before writing `/root/answer.txt`.
4e1. Known unresolved integrity issues are blockers, not warnings: missing turns/rows, blank cells where a required record should exist, mismatched game or pair counts, workbook inspection showing an absent expected entry, or alternative treatments yielding different final numbers all require resolution from the provided sources before any final answer.
4e2. Do **not** write a provisional answer despite an anomaly you already detected. First determine whether the issue is a parsing mistake, a workbook-defined omission rule, or true missing data with explicit source-supported handling.
4e3. A final answer is allowed only after the abnormal record's handling is tied to explicit evidence from the PDF, workbook formulas, or task instructions.
4e4. If validation output names a specific missing game/turn/row or unresolved identifier, do not write the answer file, do not report a numeric result in prose, and do not emit a completion token yet. First resolve that exact record from the provided workbook/PDF or continue investigating.
4e5. If multiple plausible anomaly-handling branches produce different final numbers, return to the source materials and select one branch by explicit evidence; do not choose the most reasonable branch.
4e6. Distinguish blockers from isolated non-material anomalies: if validation shows the requested aggregate is otherwise reconciled and a small number of anomalous rows do not participate in any scored pair or alter pair-slot coverage, record the treatment explicitly and continue.
4f. Do not write a final numeric answer if it depends on skipped incomplete pairs, unresolved anomalous records, or scoring logic that was not explicitly confirmed from the PDF/workbook.
4g. If you changed header detection, row alignment, column selection, or parsing logic during debugging, rerun the computation from raw input through final aggregation and recheck counts, pair coverage, and winner logic before trusting the final number.
4h. Before finalizing, produce one concise validation view that ties source rules to implementation: show the extracted win/scoring rule, one or two sample game pairs/records, and the derived winner/outcome for those samples.
4h1. This validation view must use visibly extracted source text, not just a claim that the PDF was consulted. If the rule text is still not visible in the log/output, the validation is incomplete and finalization is not allowed.
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
5j1. If a planned verification step errors, truncates, or does not visibly finish, do not write the answer file yet. Rerun a narrower or replacement validation until the confirming output is fully visible.
5j2. Completion test before writing: (a) required protocol/tool syntax has been followed exactly, (b) the final aggregate is visible in the latest clean output, (c) pair/game coverage reconciles or every exception is explicitly accounted for, and (d) no unresolved issue could change the final number. If all four pass, write the answer file and finish promptly.
5j3. Conversely, do not withhold finalization once the completion test passes merely because of a previously investigated anomaly that now has an explicit, source-consistent treatment and no unresolved impact on the requested metric.
5k. If malformed-data handling, header detection, row alignment, column selection, or parsing logic changed during debugging, rerun the full computation from raw inputs after the change and confirm the final number still matches the explicit validation output.
5l. Final artifact check must be explicit in the log: read `/root/answer.txt` back after writing and confirm it contains only the final number before emitting any completion signal.
5l1. Finalization is not complete until the log visibly shows both: (a) the decisive computation output that produced the final numeric result, and (b) the readback of the answer file. If either is missing from visible output, rerun the minimal verification before finishing.
5l2. The final artifact path must be the authorized path identified in preflight for this run; if it is not `/root/answer.txt`, apply the same write-and-readback verification to that authorized destination instead.
5l3. Do not let the run end in an analysis-summary state after verification. Once the artifact is confirmed, emit the exact required completion token immediately as the entire final response.
5m. If an existing script failed, read the current file and traceback location before editing or replacing it; inspect the exact failing code path first rather than stacking fresh workaround scripts on top of an unreviewed implementation.
5n. Minimum debug sequence after a script failure: (1) read the failing file, (2) inspect the traceback line and nearby logic, (3) verify the implicated workbook rows/IDs or PDF rule text, and only then (4) edit/rerun. Do not skip straight from traceback to a fresh workaround script unless the task explicitly requires a throwaway one-off command.

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

- If integrity checks suggest a missing record but the sheet has unexpected populated columns, inspect full-width raw rows; the missing data may be in a side-by-side or shifted table block rather than absent.
- Separate concerns cleanly: recover rules and requested metric from the PDF first, then compute from the workbook after its layout is reconciled.
- Treat outputs from failing runs as debugging clues only. If a script prints counts and then exits with `KeyError`, `IndexError`, traceback, or non-zero status, recompute after fixing the issue; do not reuse those printed totals.
- Make the final audit arithmetic explicit: expected games from ID range, parsed unique games, expected pair slots, and `wins + losses + ties + justified blocked pairs`. Finalize only when the arithmetic closes exactly.
- When you already have: (a) source-grounded rule text, (b) a clean final computation with visible decisive totals, (c) a successful answer-file readback, and (d) the required completion token, stop and finalize immediately.
