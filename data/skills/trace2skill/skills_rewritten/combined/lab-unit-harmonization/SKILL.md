---
name: lab-unit-harmonization
description: "Harmonize clinical lab data from multiple sources with different units, handling scientific notation and decimal format issues."
---

# Clinical Lab Unit Harmonization

## When to Use

- Harmonize lab data from different healthcare systems
- Handle mixed units for same measurements
- Clean and standardize clinical chemistry data

## Task-Specific Protocol

- If the task or system specifies an exact execution interface, tool/action format, command wrapper, response template, or completion string, follow it exactly throughout the run.
- Do not substitute unsupported tool-call styles, alternate formats, or free-form completion text when an exact protocol is required.
- Treat protocol compliance as mandatory alongside the data-cleaning requirements.
- Before the first tool/action, identify and restate any required tool/action schema, command wrapper, allowed tools, allowed directories, and exact completion signal from the current task/system instructions; follow that protocol literally for the entire run.
- When the environment specifies an exact `Thought`/`Action` structure or parser-sensitive format, emit that structure exactly on every step. Do **not** switch to alternate tool syntaxes such as XML tags, pseudo-functions like `Bash(...)`, informal prose, or other wrappers that were not explicitly allowed.
- For shell/tool use, send only literal executable commands or concrete file contents. Do **not** use natural-language placeholders such as "inspect the output CSV", "run validation", or "created a script that..." in place of the actual command, invocation, or file text.

- If the environment mandates a single parser-sensitive schema (for example `Thought`/`Action` or JSON `Action` calls for `bash`), use only that exact literal wrapper on every step. Do not switch to XML tags, pseudo-functions, ad hoc helpers, or narrative descriptions of actions unless explicitly authorized.
- Never simulate tool execution with prose such as "checked the file", "ran validation", "updated save block", or "created a script". Every shell step must be a literal executable command, and every file-creation/update step must contain the literal file contents to save.
- In parser-sensitive environments, every tool step must contain a literal executable command, concrete absolute path, or literal file contents; do not substitute prose such as "inspect the output CSV" or "run validation" for the actual command.

- Treat the required completion token/string as a hard requirement. If the task says to finish with an exact line such as `ACTION: TASK_COMPLETE`, output that exact line verbatim and nothing else beyond what the protocol allows.
- Use only task-authorized read/write locations. Before any write/create action, confirm the destination path is explicitly allowed by the task/runtime. Do **not** create scripts, outputs, or temp files outside permitted directories, even if an example path appears in this skill.
- Before claiming completion, verify that every required protocol constraint was satisfied: exact tool/action format, allowed file paths, executable artifacts where required, and the exact final completion string.

- Preflight before the first tool/action: explicitly restate the exact required tool/action syntax and message shape, the only allowed tool names, any required JSON fields/envelope, the allowed read/write directories, required output artifacts, and the exact required completion line/token. If any of these are missing or ambiguous, do not guess and do not write files yet.
- Treat protocol mismatches and out-of-bounds writes as blockers, not cosmetic issues. Use only the task-mandated tool names/wrappers for every step, not ad hoc `Read`/`Write`/`Edit` labels, pseudo-commands, malformed wrappers, or descriptive placeholders.
- Before the first write, choose and restate concrete absolute script/output paths inside the task-authorized directories and keep all created artifacts there: harmonization script, validators, intermediates, and final CSV. Do **not** default to `/root` or any example path in this skill unless the environment explicitly allows it.
- On the final turn, emit the exact required completion string/token verbatim in the required format only after all validations pass; do not append extra narrative unless the task explicitly allows it.



## Input Files

- `/root/environment/data/ckd_lab_data.csv`: 62 lab features, may have missing values
- `/root/environment/data/ckd_feature_descriptions.csv`: Feature descriptions and units

**Before coding, inspect both files beyond the header.** Read enough of `ckd_lab_data.csv` to see actual numeric encodings/issues, and read `ckd_feature_descriptions.csv` completely enough to cover every feature you will claim to harmonize. If any read is truncated, returns only headers, or errors, continue with smaller reads, targeted searches, chunked inspection, or column extraction until you confirm the relevant columns, feature presence, documented units, and ranges. Read representative rows from across the lab file for each feature you may convert. Do **not** invent dataset-wide conversion rules, unit mappings, or physiological ranges from partial reference information.

**Truncation is a blocker for rule-setting.** If any dataset preview or reference read shows only headers, partial rows, or truncated feature descriptions, keep reading by offsets/chunks/targeted extraction until you have enough coverage to support every feature-level rule you will implement. Do not make dataset-wide harmonization or conversion decisions from partial previews.

For large files, do not try to read the entire CSV at once just to satisfy inspection. Capture the full schema first, then inspect representative chunks/slices and targeted columns for candidate harmonized features until you have direct evidence for the rules you implement.

**Inspection pattern to keep using:** read the feature-description reference first, then inspect the lab CSV schema/column list and representative raw rows before writing conversion code. Use those raw rows to explicitly note decimal commas, scientific notation, whitespace, empty-like tokens, and mixed formatting that the parser must normalize.


Path discipline:
**Writable-path precheck:** Before creating any script, output, or helper file, list the exact absolute paths you intend to write and confirm each one is inside an explicitly allowed directory from the current task/runtime. If a sample output path in this skill conflicts with the environment, ignore the sample and use the task-authorized path.

- Read and write only in directories explicitly permitted by the task/system instructions.
- Do **not** assume `/root`, the current working directory, or the output path named in this skill is allowed if the environment gives a narrower workspace.
- Place scripts, intermediate files, and the harmonized CSV inside an allowed directory, and use absolute paths that match the environment constraints.

## Data Quality Issues

1. Missing values → preserve rows by default; only remove patient rows if the current task explicitly requires or authorizes removal after parsing/normalization, and verify the row-count change against that requirement
2. Scientific notation → convert 1.23e2 to 123.00
3. Decimal commas → 12,34 → 12.34
4. Mixed units → convert alternative units to standard (e.g., µmol/L → mg/dL)

## Harmonization Steps

1. Inspect the full schema, complete feature descriptions, and representative raw values before defining cleaning or conversion rules; if any metadata or data view is truncated, keep reading/searching until coverage is complete for every feature you will harmonize
1a. Do not write the harmonization script, assert dataset-wide rules, or state that scientific notation, decimal commas, mixed units, or specific conversion needs are present until you have direct evidence from representative raw data and metadata for the affected feature(s); headers, row counts, or generic expectations are not evidence.
1b. If an inspection command returns only `head`, a cut-off header, or partial rows, immediately issue narrower/chunked reads or targeted column extraction until the missing structure and representative values are confirmed.
1c. Treat header-only inspection as no inspection. Do not say you understand the dataset, define feature rules, or start the harmonization script until you have seen actual data rows for the relevant features.
1d. During initial inspection, explicitly check representative raw values for the numeric encodings that matter to parsing decisions: decimal commas, scientific notation, whitespace/empty-like tokens, and mixed formatting within the same feature. Base normalization rules on those observed raw strings, not on assumptions.
1e. Before finalizing any transformation logic, compare the full input column list against the feature-description/reference definitions and resolve any mismatch, omission, or unexpected extra lab column. Do not proceed as if all features are covered unless dataset schema and reference coverage are explicitly aligned.
1f. Do not state that scientific notation, decimal commas, mixed units, missingness patterns, or specific analyte conversions exist dataset-wide unless the log includes direct evidence from the affected columns/rows and corresponding metadata.

2. Record the input header, feature count, and row count early so you can preserve schema and verify that final row-count changes come only from removed missing/unparsable rows
2d. Keep simple before/after row-count checkpoints through the pipeline (input rows, rows after parsing/drop-missing, rows after any unresolved-invalid removals, final saved rows) and use them to explain every row-count decrease from the saved output.

2a. Capture the full input column list exactly once at the start and compare the final saved CSV against that exact list; treat any added, dropped, reordered, truncated, or unexpectedly renamed columns as a blocker, not a harmless preview difference.
2a.i. When any preview is truncated or visually cuts off the header, obtain the full machine-readable input schema and exact column count before proceeding. Do not infer schema preservation from `head` output or a wrapped terminal preview.
2a.ii. If any later check shows a different visible header, different column count, or extra/missing columns, stop and reconcile the discrepancy on the actual saved CSV before claiming schema preservation.

2b. Before applying any destructive step from this skill, especially row deletion, confirm that the current task explicitly requires or permits it and that parsed-data evidence supports the deletion. If row removal is not clearly authorized, preserve row count and limit harmonization to value parsing/conversion/formatting.
2c. Keep observable evidence for each major claim: retain the actual script, conversion map, validation outputs, and inspected output rows so every reported transformation can be tied to code or file evidence.
2d.i. If the task only asks for harmonization/standardization and does not explicitly require dropping incomplete records, preserve rows by default and limit changes to parsing, normalization, and justified unit conversion. Escalate row deletion to a last resort only when the task/instructions or downstream validator clearly require complete-case output.

3. Build the harmonization as one reusable script/pipeline for the whole table, and load lab columns as raw strings first so decimal commas, scientific notation, whitespace, and empty-like tokens are normalized intentionally before numeric coercion
3d. Prefer a rerunnable script for multi-step harmonization, and keep the core pipeline order stable: inspect schema + feature metadata → read lab fields as strings → normalize numeric text (decimal commas, scientific notation, whitespace) → coerce to numeric / mark unparsable as missing → assess mixed-unit candidates → apply analyte-specific conversions → remove rows still invalid after parsing/conversion as required → save → validate the saved CSV.
3e. Do not run physiological-range checks or mixed-unit detection on unnormalized raw text; perform those checks only after numeric normalization/parsing so the decisions are based on consistent numeric values.

3a. When you create the script file, write actual executable code with imports, parsing logic, conversion logic, save logic, and validation steps. Do not write a prose description, placeholder summary, TODO stub, or comments-only file instead of the implementation.
3b. After writing or updating the script, inspect the saved file contents enough to confirm the code actually contains the intended read, normalize, parse, convert, filter, save, and validate steps.
3c. Do not treat exit code 0, empty stdout, or lack of errors as evidence that harmonization succeeded; confirm that the expected output file was produced or updated and that downstream checks show the intended transformations actually occurred.

3f. Placeholder artifacts are a hard failure: do not create a script file containing only prose, comments, or TODOs. The saved script must contain executable read/normalize/parse/convert/save/validate code, and you must inspect the file text after writing it before relying on it.
3g. Minimum evidence before any success claim: inspect the saved script contents, run it, inspect actual saved output rows beyond the header, and capture whole-file validation results for schema/row counts, missingness after parsing, numeric-text formatting, and any feature-level unit conversions you claim.
3h. If any command fails because of shell syntax, unsupported options, bad quoting, placeholder text, or missing files, count that as no evidence. Fix the command and rerun it successfully before using its intended check in your reasoning.

4. Extract or tabulate per-feature documented units and expected ranges from `ckd_feature_descriptions.csv` before finalizing conversion logic; maintain one authoritative per-feature conversion map (feature, source unit, target unit, factor, direction, evidence)
4a. Treat that per-feature reference table as the authoritative driver for cleaning decisions: explicitly pair each dataset column you may harmonize with its documented unit, target unit, expected range, and evidence from the reference file before coding the rule. Do not invent feature rules from names or generic lab knowledge when the reference file provides the needed specification.
4b. Keep conversion logic configurable in one small per-feature table/dict (feature, accepted source units or detection condition, target unit, factor, direction, range/evidence) so analyte-specific rules can be corrected or extended without rewriting the pipeline.

5. Normalize raw numeric text first: scientific notation, decimal commas, whitespace, and other non-canonical numeric strings
6. Convert normalized values to numeric and mark unparsable entries as missing
7. Preserve rows by default. Only remove rows with missing values if the current task explicitly requires or authorizes row deletion after parsing/normalization has converted malformed numeric text into missing values; otherwise keep the rows and harmonize values without changing dataset length. Base any completeness checks on parsed numeric values, not the raw string dataframe.
8. Detect mixed-unit candidates per feature using observed distributions plus fixed physiological/reference expectations after parsing: keep values already plausible in the target unit unchanged, and only consider supported alternate-unit conversions for values implausible in the target unit. Do not hard-code thresholds from feature names alone, use convert-only-extreme-outliers heuristics as the sole detector, or widen ranges just to silence warnings
8a. Profile parsed values feature-by-feature before adding a conversion rule: summarize out-of-range counts and inspect representative low/high sample values so mixed-unit rules are driven by observed residual patterns, not guesses. Use that profiling to decide which specific features need alternate-unit handling.

9. Apply conversion factors only when supported by feature metadata, explicit units, or clear dataset-wide evidence; confirm the source→target direction and analyte-specific factor before bulk conversion, sanity-check multiply/divide direction with representative raw→converted examples, and do not reuse a guessed pattern across analytes
9a. If a feature has more than one plausible alternate source unit supported by metadata or observed site patterns, encode those candidates explicitly and test them against the same fixed target-unit acceptance range; keep the candidate that yields plausible target-unit values for the affected rows and leave already-plausible target-unit rows unchanged.
9b. When using multiple candidate factors for one feature, record representative raw→candidate-converted examples and the acceptance result for each candidate so the final choice is evidence-based rather than guessed.

10. Re-check plausibility after conversion using the same fixed per-feature acceptance criteria and summarize remaining below-range/above-range counts by feature; if values remain implausible, trace representative raw→normalized→converted examples, refine only the justified analyte-specific rule, or treat unresolved values as missing and remove those rows per task requirements. Do not relax validation ranges, widen thresholds, clamp values, or otherwise change acceptance criteria merely to make warnings disappear.

10a. Preserve row identifiers or row positions through the pipeline so any remaining implausible or suspicious values can be traced back to their original raw strings.
10b. Use residual exceptions to drive the next iteration: after each validation pass, focus on the small set of still-failing or suspicious features, inspect representative examples, adjust only those feature-level rules, then rerun full validation. Preserve rules already passing instead of broadening the whole pipeline.
10c. For any suspected mixed-unit feature, inspect its parsed distribution (for example quantiles, value buckets, or clusters) plus representative raw→normalized→converted examples to identify distinct unit regimes and confirm the analyte-specific factor or direction before changing the rule.
10d. Treat near-universal conversion or multiple numeric regimes within one feature as a signal to inspect that feature's distribution directly; do not assume one broad rule is correct just because most rows changed.
10e. Do not accept a conversion rule solely because the converted value looks plausible in-range. For any heuristic or range-flagged mixed-unit rule, confirm it with at least one independent source of evidence such as feature-description metadata, explicit documented units, analyte-specific conventions from the task materials, or direct raw-value patterns that clearly separate target-unit values from alternate-unit values.
10f. If a feature still fails range/unit checks after justified conversion analysis, values outside the fixed accepted target-unit range remain unresolved invalids, not candidates for looser thresholds. Mark them missing and remove the affected rows only if row removal is required/allowed by the task; do not broaden the accepted range, clamp values, or force a pass.

11. Round all values to 2 decimal places (X.XX) and write them with string-preserving formatting so trailing zeros are kept in the saved CSV
11a. Treat numeric value correctness and serialized text formatting as separate requirements: after numeric cleaning/conversion, explicitly format output fields to exactly two decimal places before writing, so values like `5` and `5.2` are saved as `5.00` and `5.20` rather than relying on default CSV serialization.
11b. If values are numerically correct but the saved CSV drops trailing zeros or rewrites number text unexpectedly, fix the output-writing step and regenerate the file rather than changing validated conversion logic.
11c. Do not assume dataframe display or a parsed round-trip proves formatting correctness; inspect the raw saved CSV text or use string-preserving reads to confirm trailing zeros were actually written.

12. Validate the final saved CSV across the entire dataset before declaring success, and do not claim dataset-wide harmonization, conversion coverage, converted-row counts, supported units, or physiological compliance unless you explicitly computed or inspected evidence for each relevant feature from the final saved output
13. Validate conversion logic explicitly, not just formatting: for each feature with any unit harmonization rule, produce evidence from the final saved output and representative raw→normalized→converted examples showing which rows were converted, which were left unchanged, the source→target direction, and why the result is plausible in the target unit.
13a. Do not claim that mixed units were detected or harmonized unless the run includes explicit feature-level evidence for the affected columns from the final saved CSV plus representative raw→normalized→converted row examples. Formatting checks, row counts, and a few output samples are not enough.

14. If any validation output reports FAIL, warnings, contradictory examples, formatting/range/unit/schema failures, or conflicts with another check, stop and inspect the exact failing cases; determine the authoritative issue, fix the pipeline, regenerate the CSV, and rerun full validation before making any success claim.

14a. If a specific validator exposed the failure, rerun that same validator after the fix and clear the original failure condition before using any additional checker. Use alternate diagnostics to investigate, not to replace the acceptance test that just failed.
14b. Never explain away a reported FAIL as a display artifact, parser artifact, or harmless preview issue unless you verify the exact requirement directly on the saved file and rerun the original failing check to PASS.
14c. When a validator prints example failing rows or values, re-check those exact examples in the saved CSV before making any success claim.
14d. Do not delete scripts, verification helpers, or intermediate evidence after a failed or warning-producing validation run. Keep them available, inspect the named failing rows/features, repair the logic, and rerun the same checks until the blocker is resolved.
14e. Treat any remaining out-of-range, ambiguous-unit, or contradictory harmonization result as unresolved unless you corrected it or the task explicitly permits retaining it. Do not describe the dataset as fully harmonized while such cases remain.

15. Treat incomplete or truncated validation output as not validated. If a command stops mid-check, returns only partial evidence, or does not show final pass/fail status for the requirement, rerun with concrete commands until the result is complete and inspectable.
16. If a task uses an active validator or downstream checker, treat that checker as part of the acceptance criteria. Do not explain away a failing check or substitute a different interpretation; change the artifact, serialization, or validation method until the active check passes, or report that the requirement is still unmet.
16a. If one check fails and another check seems to pass, do not declare success from the more favorable interpretation. Reproduce the failing check, identify the exact mismatch between the artifact and the checker, fix it, and rerun that same check until it passes or remains a documented blocker.


## Output

Use the task-specified output location only if it is explicitly allowed by the task/system instructions. Treat the `/root/...` path here as an example only, not proof that `/root` is writable in the current environment. If write permissions are not explicit, save inside an allowed workspace such as the provided data directory rather than creating files in a different top-level directory.

Use `/root/ckd_lab_data_harmonized.csv` only when `/root` is explicitly permitted. Otherwise save the harmonized CSV in an authorized workspace path, and keep the harmonization script plus any verification helpers in that same allowed location unless the task says otherwise.

`/root/ckd_lab_data_harmonized.csv`:
- Same column count as input
- All values in US conventional units
- Within expected physiological ranges
- No scientific notation or commas


Verification requirements before finishing:
- Inspect the actual `/root/ckd_lab_data_harmonized.csv` file text, not just a pandas round-trip or a header preview.
- Confirm across the full file that row/column structure matches expectations and row count decreased only because rows with missing or unparseable values were removed.
- Confirm numeric fields use `.` as decimal separator, contain no scientific notation text or decimal commas, and are written in exact `X.XX` format where applicable.
- Audit every lab feature with full-column checks or summaries to catch mixed-unit leftovers and implausible ranges.
- Map final verification directly to each explicit requirement: row removal for missing/unparsable values, unit harmonization, physiological-range compliance, and exact output formatting.
- Make dataset-wide claims only after programmatic checks across all output rows and relevant columns; debugging samples, `head`, or truncated previews are not sufficient.
- Do not declare success while known unexplained out-of-range values or unit ambiguities remain.


## Output

## Validation and Completion

- Validate the saved CSV itself, not only intermediate DataFrames or console summaries.
- Minimum evidence before any success claim: inspect the saved script text, inspect non-header rows from the saved CSV, and run whole-file checks for schema, row-count change, numeric formatting, and feature-level conversion/range results.
- A header-only preview, first-10-lines check, truncated output, script print statements, or file-exists check is never sufficient evidence for dataset-wide harmonization.

- Ground every verification step in a literal, reproducible executable command or script invocation whose output you can inspect. Prefer checks that print failing counts, sample failing rows/values, and explicit pass/fail status.
- Never treat `head`, a header-only preview, a truncated table, file existence, a successful script run, or log messages like `saved`/`done` as evidence that the transformed dataset is correct. Inspect actual saved data rows and compute whole-file checks before making any success claim.
- Separate raw-file formatting evidence from parsed dataframe display: parsed reads can hide trailing zeros and scientific-notation text, so verify exact `X.XX` formatting on the saved CSV itself with raw-text or string-preserving inspection before declaring formatting success.
- Validate against the actual source/output data files, not repository-wide searches or documentation text. If checking for null markers, scientific notation, decimal commas, row removal, or formatting issues, read/search the dataset files directly.
- When searching for missing-value markers, sentinel values, commas, or scientific-notation text, scope the command to the relevant source/output CSV files themselves. Do not use repository-wide searches or documentation hits as evidence about dataset contents.
- Before any success claim, ensure the log shows observable evidence for each major transformation you report: inspected input rows/columns, the actual script or command used, and saved-file validation output. Do not rely on inferred behavior, generic expectations, or a narrative summary.

- Do not claim that rows were removed, commas/scientific notation were normalized, values were rounded to `X.XX`, or units were converted unless the run includes direct checks on the saved output confirming each claim.

- Do not treat exit code 0, empty stdout, file existence, or a structurally valid CSV as evidence that harmonization worked. Check the task-critical semantics directly from the saved output: rows removed for missing/unparsable data when required, decimal-comma/scientific-notation normalization, and feature-level unit conversions with before/after examples or computed summaries.
- Do not rely on self-generated summaries, "final reports," or reassuring prose as validation. For each requirement, inspect the saved file or compute a direct check that prints evidence from the actual output.
- If a preview or summary exposes suspicious clinical values, stop the completion flow and investigate semantic correctness before continuing with formatting-only checks.

- If you write a script, inspect the saved script contents directly before relying on it. Do not claim the code handles parsing, unit conversion, row dropping, or formatting unless the script text and/or direct output evidence shows those exact behaviors.
- Before reporting any specific result (for example column count, dropped-row count, converted features, or formatting success), ensure the supporting command output is present and untruncated in the log. If the evidence is partial, rerun narrower commands until the claim is directly supported.


- Use validation as a repair loop, not a one-time check: if any check reports bad values, formatting failures, schema problems, contradictory evidence, or suspicious conversion patterns, inspect those exact cases, update the harmonization logic, regenerate the CSV, and rerun validation until all blockers are cleared.
- Separate validation into two passes: (1) raw-text/file-serialization checks on the saved CSV, and (2) parsed semantic checks for schema, missingness, intended units, and physiological ranges.
- Keep raw-file formatting evidence separate from parsed-display evidence: if a dataframe/table view shows `83.1` instead of `83.10`, do **not** assume the CSV serialization is wrong. Check the saved file text or string-preserving reads first, and only change serialization if the raw file itself fails the `X.XX` requirement.
- Run those saved-file checks immediately after each write/regeneration of the harmonized CSV so formatting or serialization defects are caught before deeper semantic debugging.
- If semantic checks pass but raw-text formatting checks fail, repair serialization/output formatting first, rewrite the CSV, and rerun the same saved-file checks before changing transformation logic.
- Use parsed semantic validation to produce a per-feature range/status summary, then use that summary as the driver for targeted repair. Reinvestigate only the specific failing or suspicious features, not the entire conversion map, unless the summary shows a broad schema or parsing problem.
- Do not treat a truncated validator printout, cut-off summary, or partial feature list as a pass. Rerun narrower or chunked checks until the specific pass/fail result and any cited examples are fully visible before making any global success claim.

- Inspect actual data rows from the saved CSV during final verification; a header-only or truncated preview does not count.
- Use checks that distinguish CSV delimiters from decimal commas; field-separating commas are not evidence of bad numeric formatting.
- For exact output-format checks, inspect the saved CSV as raw text or with string-preserving reads; do not rely on `pandas.read_csv` alone because parsing can hide trailing zeros and scientific-notation text.
- Do not treat `head`, a header-only preview, truncated output, file existence, or a failed/incomplete verification command as validation. Fix the check and rerun it on the saved file.
- If any file read, script inspection, or validation output is truncated, obtain additional lines, targeted slices, or programmatic summaries until the specific claim is directly supported.
- When any validator names specific failing rows, columns, or examples, recheck those exact failures after edits; do not replace a failed detailed check with a later spot check, summary, or different validator.
- Treat contradictory validation evidence as a blocker. If a report says a formatting/range/unit check passed but printed examples contradict it, assume the check or the interpretation is wrong, inspect the saved file directly, fix the validation logic or harmonization logic, and rerun.
- Example contradiction to treat as FAIL: a validator summary says all numbers have exactly 2 decimals, but any printed sample shows values like `74.1` or scientific notation. In that case, inspect the saved CSV text directly, fix serialization or the check, and rerun validation before claiming success.
- When validations disagree, prefer the broadest direct check on the saved file over sampled previews or narrative summaries. Re-run that same failing check after each fix and do not replace it with a different looser check just to obtain a pass.
- Do not claim exact `X.XX` formatting, full unit harmonization, or physiological-range compliance until the final saved CSV passes an explicit whole-file check for that requirement with visible pass/fail output.

- Treat a failed command, shell parse error, unsupported option, missing output, or placeholder command as no validation at all. Fix the command, rerun it, and base conclusions only on successful, reproducible outputs.

- Do not replace a failed detailed check with a prose claim or a looser spot check. Re-run the same requirement-level validation with a working executable command until the failure is either resolved or explicitly still failing.
- Treat truncated validation output as unresolved. If a report is cut off, abbreviated, or missing its final totals/pass-fail status, rerun with narrower or file-backed checks before making any dataset-wide claim.
- Before the final response, cross-check every success claim against directly observed evidence from three things: the saved script text, the saved output CSV, and complete validation output. If any one of those is partial or contradictory, report the gap and keep validating instead of declaring success.


- Treat any schema, missing-data, range, or formatting failure as a blocker: update the harmonization logic, regenerate the file, and verify again.
- Keep physiological acceptance ranges fixed during final verification; if values still fail, revisit conversion logic instead of relaxing thresholds.
- Do not claim a conversion rule, converted-value count, pass rate, or dataset-wide guarantee unless you explicitly computed or inspected evidence for it from the final output.

- Compare final schema and row count against the input counts captured at the start; investigate any mismatch beyond the rows intentionally removed for missing/unparsable data.

- Use an explicit full-schema comparison for input vs. output (ordered column list and exact count), not a wrapped preview. Do not claim schema preservation until that comparison passes on the saved CSV.
- Reopen the written CSV after saving and inspect actual data rows along with the final row count; use this saved-file check to confirm that write-time serialization preserved the intended schema, formatting, and expected row reduction.
- Treat any row-count change as a major transformation. Report it explicitly, tie it to a task requirement, and verify that it came only from allowed handling of parsed missing/unparsable values; otherwise preserve all input rows.


- If a feature shows suspiciously high or near-universal conversion counts, inspect raw and converted examples to confirm the detection rule is correct.

- Re-check that conversions were applied only to rows identified as plausible alternate-unit cases; if many already-plausible values changed, treat that as a likely detection error and revisit the rule.
- Confirm the workflow order in code and checks: raw text normalization/parsing first, then missing-value handling, then unit detection/conversion, then final formatting and file-level validation.

- Keep scripts and intermediate/debug artifacts until validation is complete.

- Do not delete the harmonization script, verification helpers, or debug outputs before all validations pass and the task is formally complete; keep them available for reruns if any check fails.

- If any requirement was not checked directly, say so and validate it before finishing.
- Follow any task-specific execution protocol or exact completion string verbatim, but only after all checks pass.
- If the active validator checks parsed values rather than raw CSV text, satisfy that validator's interpretation as well; raw-text compliance alone is not enough when downstream acceptance still reports FAIL.
- Before any final success claim, confirm four hard blockers are cleared: (1) every created/edited file stayed inside allowed directories, (2) every action and the final response used the exact required protocol/completion string, (3) every claimed data issue/conversion was supported by inspected raw evidence, and (4) no validation pass depended on widened physiological ranges.



- Treat any failed check, unresolved warning, unresolved out-of-range value, unverified feature-level unit target, unit ambiguity, failed exact-format check, or contradictory example as a hard blocker for claiming the dataset is fully harmonized.
- Keep physiological acceptance ranges fixed during debugging and final QA unless the task or inspected source metadata explicitly justifies a corrected standard; never loosen bounds ad hoc to clear residual failures.
- Validate semantic success from the final saved CSV, not from script intent: use full-column summaries and targeted raw/converted examples for features with suspicious values, high conversion counts, near-universal conversion, or remaining out-of-range values.
- Ensure the final conclusion matches the last validation results exactly; never report completion while any format, range, or unit check still shows FAIL or unresolved warnings.
- Report only results you directly observed or explicitly computed from the final saved file or complete, untruncated reference/validation output. If you mention counts, percentages, pass rates, factors, ranges, or exceptions, show how they were obtained.
- Before the final response, re-read the task instructions and output any required exact completion string, token, or final line verbatim only after all validations pass.
- Make the final pre-completion check explicit: confirm (1) every artifact path used was allowed, (2) every tool/action message followed the required schema with literal executable commands, and (3) the final line you will emit is exactly the required completion token with no extra narrative if the protocol forbids it.
- Final gate: do not emit the required completion token/string until the log contains all of the following in inspectable form: the exact protocol was followed, the script contents were checked, the saved CSV was inspected beyond the header, and requirement-level validations from the final saved file passed.


- Before claiming completion, map each explicit requirement to a direct pass result from the final saved file: schema/row count, missing-value row removal when required, unit harmonization, physiological-range compliance, and exact `X.XX` formatting.
- If a validation check fails, fix the harmonization or serialization logic first, regenerate the CSV, and rerun the same check that failed. Do **not** declare success by swapping in a looser or differently framed validator without showing that the original failure condition is resolved.
- If you removed rows, report that only after verifying both that the task required/allowed removal and that those rows were missing or unparsable after the normalization/parsing pipeline.
- Tie every final claim to an observed check from the saved file: column count, row count, representative transformed rows, and programmatic summaries for formatting, missingness, conversion coverage, and range checks.
- Do not conclude success while any requirement-level check still shows FAIL, unresolved warnings, contradictory results, or only indirect/sample-based evidence.
- If any required execution protocol, script evidence, or dataset verification step is missing from the log, treat the task as not yet complete and fix that gap before finishing.


- Before the first write and again before the final response, re-check three compliance items from the task/system prompt: exact tool/action format, exact allowed write path, and exact completion string. Treat any mismatch as a blocker even if the data work itself looks correct.
- Final pre-completion checklist: (1) protocol format matched the task on every tool/action step, (2) every created file stayed in an allowed directory, (3) the saved script contains real executable logic, (4) the saved CSV itself was inspected beyond the header, (5) any row-count decrease is explicitly justified by the task and parsed-data evidence, (6) feature-level unit-conversion evidence exists for every converted feature, and (7) every final claim is tied to direct output evidence with no unresolved contradictions.


## Tips

- Know conversion factors: mg/dL ↔ µmol/L for creatinine, g/dL ↔ g/L for hemoglobin
- Define valid physiological ranges per feature
- Use pandas for data processing


- Derive per-feature conversions from the actual feature-description file, documented units, and observed distributions; do not infer broad rules from partial previews or generic lab knowledge alone.
- Sanity-check conversion direction before coding. Use analyte-specific factors; do not reuse a guessed multiply/divide rule across different labs.
- Treat physiological ranges as validation criteria and supporting evidence, not proof of which alternate unit was used.
- Ranges are guardrails, not tuning knobs: keep them fixed unless the task or inspected source metadata explicitly establishes that the original standard itself was wrong.
- Do not convert every out-of-range value blindly, and do not clamp values to physiological min/max as a fallback.
- Do not validate exact `X.XX` formatting by loading the CSV back into pandas alone; parsing may hide trailing zeros. Use raw-text or string-preserving checks as well.
- Compare conversion counts by feature; nearly all rows converting for one feature can be a red flag that the feature was already in the target unit.
- Use full-file/programmatic inspection for validation; a truncated preview or a few spot checks is not enough.


- A reliable pattern is: inspect full schema and metadata → normalize numeric text → parse to numeric → profile each feature's distributions and out-of-range clusters → apply analyte-specific conversions only where supported → save CSV → verify the written file with both raw-text and full-feature semantic checks.
- Prefer a string-first parse pipeline: read raw lab fields as text, normalize numeric text explicitly, then convert to numeric for cleaning/conversion logic.
- Start by extracting a compact table for each feature you may harmonize: feature name, documented unit, target unit, expected range, and any candidate alternate units.
- Prefer a small analyte-by-analyte conversion table in code over broad if/else rules from feature-name patterns.
- When mixed units may occur within a column, convert only values justified by metadata plus value evidence; leave already-plausible target-unit values unchanged.
- After the first harmonization pass, summarize remaining out-of-range counts and conversion counts by feature and investigate only the features still failing or showing suspiciously high conversion rates.
- For mmol/L-style analytes or other direction-sensitive conversions, sanity-check whether conversion into US conventional units should make values numerically larger or smaller before trusting the factor.


- A proven workflow is: inspect full schema, metadata, and representative raw values first; normalize heterogeneous numeric text into a consistent parseable form; profile parsed values feature-by-feature; handle missingness only if the task permits row removal; apply analyte-specific unit conversion; then run saved-file formatting checks and semantic/range checks as separate verification steps.
- Make an explicit first-pass check of raw string encodings before choosing parse/normalization rules; this is a reliable way to avoid guessing about decimal commas, scientific notation, whitespace, or mixed numeric text.
- Preserve exact `X.XX` output formatting deliberately at write time; default numeric CSV serialization may drop trailing zeros even when the numeric values are correct.
- A strong pattern is: use fixed expected ranges to flag candidate unit mismatches, then confirm with feature metadata and representative raw→converted examples before applying or extending a conversion rule.
- When debugging a mixed-unit column, inspect distribution shape as well as out-of-range counts; distinct clusters or scale bands often reveal the alternate unit more reliably than isolated spot checks.
- If one feature can plausibly arrive in several alternate units, prefer an explicit short list of analyte-specific candidate conversions in code and select among them by which result lands in the fixed target-unit range for the affected rows.
- After the first harmonization pass, summarize remaining out-of-range counts and conversion counts by feature and investigate only the features still failing or showing suspiciously high conversion rates.
- Keep post-conversion range summaries as a required sanity check: after harmonization, compute per-feature out-of-range counts from the final saved data and investigate any nonzero remainder before concluding the conversion logic worked.


