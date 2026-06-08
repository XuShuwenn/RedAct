---
name: lake-warming-attribution
description: "Analyze lake temperature trends and attribute warming to climate drivers (Heat, Flow, Wind, Human factors)."
---

# Lake Warming Attribution Analysis

## When to Use

- Analyze long-term water temperature trends
- Attribute warming to driving factors
- Process climate and hydrology data

## Input Files

- `/root/data/water_temperature.csv`: Lake surface temperature (0-5m)
- `/root/data/climate.csv`: Climate variables
- `/root/data/land_cover.csv`: Land cover data
- `/root/data/hydrology.csv`: Hydrology data


## Input Files

## Execution Guardrails

- Follow any task/runtime instructions exactly, including required tool/action syntax, exact completion tokens, and allowed read/write directories.
- Keep all helper scripts, logs, and intermediate artifacts inside explicitly allowed directories; default to `/root/output/` when you need a writable location.
- If directory permissions are tight, prefer inline commands or short scripts in an allowed directory over scattered helper files.
- Before the first action, identify the exact execution contract from the runtime/task instructions: required tool-call/action syntax, allowed tools, allowed read/write paths, and any exact completion signal.
- Preflight before the first tool call: restate the exact required action/tool schema, any required wrapper or JSON payload shape, the allowed readable/writable paths, the exact completion token, and the confirmed interpreter you will use.
- Treat any unspecified tool, wrapper, executable, or path as disallowed until confirmed.
- If the environment requires a specific protocol (for example `Thought`/`Action`, `Action:` JSON, or an exact closing token), use that syntax verbatim on every step and reserve the exact completion signal for the final step only.
- Treat environment-mandated action syntax and completion tokens as hard requirements: use the specified format verbatim for every tool call and at termination; do **not** improvise alternate tool styles, wrappers, tags, or a narrative-only ending.
- In any shell/tool invocation, send a fully executable command or complete payload only; do **not** use placeholders such as "run analysis", `python3 ...`, or truncated JSON.
- Every shell/action payload must already be runnable as sent and include the real executable plus concrete absolute paths and arguments when possible.
- Never submit descriptive placeholders like `run analysis`, `prepare output directory`, `write analysis script`, or truncated command/payload fragments as if they were executable steps.
- Use only the tools and paths explicitly permitted by the current environment/task. Keep temporary scripts and intermediate artifacts only in an allowed writable directory, preferably with absolute paths.
- Before running a script, confirm the available interpreter/command in the environment (for example `python3` vs `python`) and then use the confirmed executable consistently.
- Make the interpreter/dependency check explicit before scripting: confirm the actual executable available in this runtime and whether needed libraries are already installed; do **not** assume package installation, `Rscript`, or nonstandard tools will be allowed.
- If a preferred executable or package is unavailable, switch immediately to the simplest confirmed supported method that still matches the required outputs.
- If any command, script body, or console output appears truncated, cut off, malformed, or incomplete, treat that run as unverified and rerun in a simpler form until completion and exit status are clear.

## Pre-Analysis Checks

- Inspect the full contents of each input file before modeling; do not rely on truncated previews.
- Enumerate all required input files first, then inspect each one enough to confirm full headers/schema, the exact response column, available predictor columns, year coverage, row counts, and tail rows before choosing variables or methods.
- If an attempted read targets the wrong object type or produces an incomplete/truncated display, correct the read method first and do not treat that failed read as evidence about file contents.
- Verify key columns, year coverage, duplicate years, delimiter/parsing assumptions, and missing/malformed numeric values.
- Confirm tables can be joined on a shared year field and handle incomplete rows before regression or attribution.

- Read each source file completely enough to verify the full schema and data quality before modeling; if any preview is truncated, use another command or chunked inspection until all columns, year coverage, delimiter/parsing assumptions, and numeric parsing are confirmed.
- Identify the shared join key exactly as written (often `Year`) and confirm its type/format matches across all files before merging.
- Record the exact predictor column names available in climate, hydrology, and land-cover inputs so attribution uses observed variables rather than assumed categories.
- If you will use Heat / Flow / Wind / Human in interpretation, draft the raw-variable-to-category mapping from observed column names before modeling.
- Confirm the runtime has the libraries needed for your planned method before committing to it; if a preferred package is unavailable, choose a simpler supported method.
- Assess sample size versus predictor count early; if the merged dataset will be small, plan a simpler interpretable attribution approach.
- Before merging, explicitly compare the year lists/ranges and row counts across all input tables; if coverage differs, restrict analysis to the aligned overlapping years and note the effective merged sample size.
- If grouped drivers may help interpretation, map each raw predictor to at most one group (Heat / Flow / Wind / Human) using observed column names only; leave ambiguous variables ungrouped rather than forcing a category.
- Use a short startup checklist before coding: (1) inspect every input file enough to know exact headers and year coverage, (2) identify the actual temperature and year columns, (3) confirm the interpreter and needed libraries are available, and only then (4) choose the simplest runnable analysis method.

- Check runtime capabilities before choosing a method: confirm the intended interpreter/tool exists and that needed libraries are already available; do **not** assume `Rscript`, package installation, or nonstandard tools will work.
- Enumerate the required input files and inspect each one enough to confirm the full header/schema, exact response-variable column in the water-temperature file, predictor columns, row counts, and year coverage before choosing methods.
- Treat visibly truncated previews, cut-off rows, inconsistent field counts, malformed last lines, or incomplete final rows as a hard stop for modeling: re-read the file with another command or chunked inspection until full headers, parseability, and tail rows are verified.
- Apply this hard-stop rule to each input file individually: if water-temperature, climate, hydrology, or land-cover content looks clipped anywhere, explicitly inspect the tail and confirm the file parsed completely.
- If malformed or partial rows remain after reinspection, explicitly repair, drop, or exclude them before merging and base the analysis only on the verified clean subset.
- Do **not** assume a file is understood from a partial observation like an ellipsis, clipped numeric value, or incomplete final row.
- If you write a helper script, inspect the saved script contents before execution and verify it contains the intended logic, input paths, merge, trend, attribution, output-writing, and verification steps.
- Save runnable code only; never write prose descriptions, pseudocode, comments-only placeholders, TODO stubs, or ellipses as if they were executable artifacts.
- After each script creation or rewrite, read the saved file back and verify it visibly contains imports, input reads, merge logic, trend and attribution code, exact CSV writes, and output-verification steps before executing it.


## Output Files

### trend_result.csv
```csv
slope,p-value
```

### dominant_factor.csv
```csv
variable,contribution
```

**Use these filenames and headers exactly.**
- `trend_result.csv` must have columns exactly: `slope,p-value`
- `dominant_factor.csv` must have columns exactly: `variable,contribution`
- Write both required files to `/root/output/` and verify they exist before finishing.
- Do **not** change punctuation or casing (for example, `p.value` is wrong; use `p-value`).

## Key Steps

0. **Default Workflow**: Use one auditable end-to-end analysis path
   - List or inspect the input files first to confirm the shared year key, actual response column, predictor columns, and year coverage before choosing methods.
   - Check that the planned interpreter and needed libraries are available before committing to a workflow; if not, switch to a simpler supported method that still matches the requested outputs.
   - Prefer one reproducible script that reads all required inputs, performs the merge and analyses, writes both required CSVs, and then re-opens those saved files for verification.

1. **Trend Analysis**: Linear regression on water temperature vs time

   - Treat trend detection and attribution as two separate analyses with different inputs: estimate the water-temperature trend from the temperature time series first, then run attribution on the merged predictor dataset.

   - Output slope and p-value to `trend_result.csv`

   - Use the actual year/time column as the regression predictor; do **not** replace this with Mann-Kendall slope, rolling summaries, row index, or another trend statistic unless explicitly requested
   - If a planned method fails or a package is unavailable, do **not** switch to a different statistic silently; implement the same requested slope and p-value with available tools or confirm the fallback still matches the required output semantics

2. **Attribution Analysis**: Use climate, hydrology, and land-cover predictors to explain temperature variation with one defensible importance method

   - Prefer one reproducible script/workflow that loads all inputs, validates schemas, performs the merge, runs both the trend and attribution analyses, writes both required CSVs, and then re-opens the saved files for verification.
- Default workflow when not otherwise constrained: (1) open all input CSVs and confirm schema/year coverage, (2) write one short reproducible script for merge + trend + attribution + CSV writing, (3) run it, and (4) re-open both saved output CSVs before reporting.
- You may instead use two short audited scripts—one for `trend_result.csv` and one for `dominant_factor.csv`—when that keeps execution, debugging, and verification simpler; in either case, verify both saved outputs from disk before finishing.
   - Start by merging water temperature, climate, land-cover, and hydrology tables on the shared year field to create one cleaned analysis dataset before fitting any multivariable attribution model
   - Preserve this single year-aligned merged dataset as the basis for attribution so all compared predictors come from the same observation window and one comparable model/input table.
   - Validate method-task fit before computing contributions: ensure the chosen importance metric supports the requested dominant variable/contribution output and is defensible for the sample size and predictor set
   - Verify the full header/schema of every input file before choosing predictors or assigning variables to Heat/Flow/Wind/Human
   - First validate merged data: confirm years align across files, handle missing/malformed rows, and use only complete comparable rows for attribution

   - Record shared year coverage and row counts after each merge so attribution is based only on aligned observations
   - Prefer a single multivariable model with standardized predictors, then compare validated importance values from that model; if the merged dataset is small relative to predictor count, use the simplest interpretable approach that remains defensible

   - For small annual datasets, prefer low-complexity attribution with fewer predictors over factor analysis, PCA, latent decomposition, or other unstable high-flexibility methods
   - Avoid redundant engineered predictors in the main attribution model; do **not** include a derived feature alongside its source variables unless you can justify it and prevent double-counting
   - Do **not** normalize R² values from separate models into contribution percentages, and do **not** use latent-factor/factor-analysis pipelines unless they are clearly appropriate, stable for sample size, and map factors unambiguously
   - Do **not** fit separate regressions by category (Heat/Flow/Wind/Human) and compare or normalize their R² as contributions, and do **not** combine separate-model statistics into variable-level or category-level percentages; if the method does not produce directly comparable importances, report only the most associated variable conservatively
   - Do **not** let grouped-category interpretation replace the required variable-level deliverable: even if a category appears dominant conceptually, `dominant_factor.csv` must still name one original predictor column from the merged dataset.
   - If you use grouped drivers or latent representations for interpretation, verify the mapping is unique, complete, and stable; otherwise fall back to the dominant observed predictor from a simpler interpretable model
   - Keep trend analysis and attribution as separate stages with separate outputs: compute/save `trend_result.csv` first, then compute/save `dominant_factor.csv`.
   - Use Heat / Flow / Wind / Human for grouping or interpretation if helpful, but for `dominant_factor.csv`, output the single most important verified **variable** and its computed contribution/importance value
   - If you create Heat / Flow / Wind / Human groups, map each raw predictor to exactly one group before modeling or interpretation, and keep that mapping separate from the required variable-level CSV output.

   - Treat `variable` literally: write one original predictor column name from the merged dataset, and ensure the reported `contribution` is computed for that same named predictor; do **not** write a category label such as Heat/Flow/Wind/Human, a derived factor/component name, or a category-level score attached to an individual variable
   - If reporting percentages from model-importance scores, normalize nonnegative contributions so reported shares are interpretable
   - If the method supports association rather than causal attribution, report it conservatively as the dominant or most associated factor


3. **Method Validation and Output Verification**: Ensure the calculations and files match the requested deliverables before reporting
   - For trend, regress temperature against the actual time/year variable; do not substitute a different trend statistic unless explicitly requested
   - If any script or run failed, looked truncated, or did not clearly complete, rerun fully and confirm completion before using its results
- Treat header-only outputs, lone-row outputs with suspect labels, or files created after truncated execution as unverified until you inspect the underlying computation and rerun if needed.
- If `dominant_factor.csv` contains a category label, latent component, implausibly coarse value, or any result unsupported by a clearly completed run, treat it as a failure state and recompute rather than summarize it.

   - Treat cut-off stdout/stderr or partial console logs as unvalidated; inspect the saved code if applicable, check completion, and rerun in a simpler form until execution is clearly complete
   - After any substantive code or logic change (predictors, grouping, mapping, method, aggregation, or formatting), rerun the full pipeline end-to-end before trusting results
- If you had to recover from any execution error, missing interpreter/dependency, indexing bug, partial run, or late script/method rewrite, do one final clean end-to-end rerun and then verify the saved CSVs again before reporting anything.
   - Open and inspect both output CSVs after writing them; do not claim success based on partial console output
- Treat truncated model summaries, cut-off importance reports, partial console listings, or file existence alone as insufficient evidence; directly open the saved CSVs and verify their rows and semantics.
- For `/root/output/dominant_factor.csv`, confirm there is one data row beneath the exact `variable,contribution` header and that `variable` is one original predictor column actually used in the merged analysis.
   - Base any final reported numbers on the contents of the saved CSVs, not on intermediate prints or unsaved in-memory results
- Treat the saved CSVs as the sole source of truth: if console output, prior notes, or interpretation contain more detail than the files, either regenerate the files to support that claim or keep the final report strictly limited to what is saved and verified.
- Copy reported values and formatting directly from the verified CSV contents; do **not** add units, percent signs, renamed variables, category-level conclusions, or broader comparisons that are absent from the saved outputs.
   - Treat this as a literal spec-compliance gate: compare saved filenames, headers, punctuation, casing, and column order exactly against the request
   - Re-open `/root/output/trend_result.csv` and `/root/output/dominant_factor.csv` directly after any prior error or interrupted run; do not infer success from logs alone

   - Before any final response, directly open or list **both** required files and confirm each exists, is non-empty, and has the exact required header.
   - If only one file is verified, the task is **not complete**; continue until the missing file is successfully produced and inspected.
   - Verify the final CSVs contain the required columns only: `slope,p-value` and `variable,contribution`
   - Final semantic check for `dominant_factor.csv`: confirm its lone row names one concrete predictor actually used in the analysis and one numeric contribution/importance value consistent with the chosen method

   - Reject `dominant_factor.csv` outputs where `variable` is a driver category/group label (for example `Heat`, `Flow`, `Wind`, `Human`) or a latent component; it must be one original predictor column name actually used in the merged analysis.
   - Final claim check: every label and number in the response must trace directly to a verified saved output or an explicitly observed computation step. If the saved output is variable-level only, keep the response variable-level only; do **not** upgrade it to a category-level interpretation.
   - If `dominant_factor.csv` contains only one top predictor and contribution, report only that verified result; do **not** infer a Heat/Flow/Wind/Human winner, category ranking, or claims that other drivers are minor unless those exact results were separately computed and verified.
   - In the final response, report only values that appear in those verified saved CSVs; if the task requires an exact completion signal or closing token, emit it verbatim after verification

4. **Execution Discipline and Evidence Checks**: Validate that your workflow and artifacts are real before trusting results
   - When you create a helper script, write actual executable code only; do **not** save natural-language placeholders, comments-only files, or pseudocode as if they were runnable artifacts.
   - Make execution auditable: inspect the saved script contents before running it, then execute that exact file with an explicit command.
   - Treat truncated stdout/stderr, cut-off script echoes, interrupted commands, missing terminal success evidence, or header-only outputs as incomplete execution, not evidence of success.
   - Do **not** infer that `dominant_factor.csv` exists from intended logic, printed snippets, or partially shown code; confirm it directly from the saved file.
   - Do **not** accept a weak `dominant_factor.csv`; confirm it contains one real predictor name and one numeric contribution consistent with the chosen method.
   - After any meaningful code, interpreter, method, or aggregation change, rerun the full pipeline end-to-end and re-open the saved CSVs before reporting values.
   - After verifying saved outputs and extracting required values, emit the environment's exact completion signal/token if one is required; do **not** continue with extra tool calls or prose first.
   - Finalization gate: before the last output, compare the required closing string character-for-character against the runtime instructions; if an exact completion token is required, emit that exact token and nothing else unless the environment explicitly asks for additional text.

- Minimal execution checklist: (1) confirm protocol, allowed paths, interpreter, and completion token, (2) inspect full input schemas and tails, (3) inspect saved script contents if used, (4) run one complete executable pipeline, (5) reopen both CSVs from disk, and (6) emit the exact required completion token.
- Do not claim completion from intended logic, partial tables, truncated stdout/stderr, or file existence alone; require complete execution evidence plus direct file inspection.

## Tips

- Use scipy.stats for linear regression
- pandas for data merging and analysis
- Consider multiple regression for attribution
- Check significance levels (p < 0.05)


- Before merging, check row counts, year ranges, join keys, and NA counts for every file
- Prefer simple, auditable attribution over opaque dimensionality reduction when the task only asks for the dominant driver
- Before trusting outputs, verify the analysis actually executed and keep claims bounded to numbers that appear in the saved CSVs
- When reporting the dominant factor, write a concrete predictor name rather than a category label

- Prefer the simplest auditable workflow that matches the deliverable: inspect full data, merge on year, fit the requested trend model, fit one defensible attribution model, then verify the saved CSV contents.
- Good default for attribution: fit one multivariable model on aligned complete-case data, standardize predictors if scales differ, and derive importance from that same model so the chosen variable and reported contribution come from the same calculation.
- If an inline command becomes long or fragile, write a short reproducible script that reads inputs, writes the two required CSVs, and then reads them back for verification.
- Keep analysis scripts and final narrative aligned with the saved outputs: use category groupings only for interpretation, while `dominant_factor.csv` names a real predictor column.
- Once both required CSVs exist with the exact requested headers and verified values, avoid unnecessary cosmetic rewrites.

- If stdout/stderr ends abruptly, shows clipped lines, stops mid-table/message, or omits an expected completion signal, treat the run as unverified even if output files exist; inspect artifacts and rerun until completion is clearly confirmed.
- If you write or rewrite an analysis script, inspect the saved script contents before trusting its results; at minimum, verify it reads the intended files, uses the intended year/temperature columns, writes the required CSV headers, and implements the chosen attribution method.
- If you had to recover from any execution error, missing executable, exception, partial run, or truncated command/script, perform one final end-to-end rerun or reconciliation check so the saved CSVs, script, console summaries, and final response all refer to the same completed analysis.
- Immediately before the final response, re-open the saved CSVs and copy the reported values and formatting from those files exactly.
- Do **not** add units, percent signs, rounding changes, renamed variables, category-level conclusions, comparative claims about unreported drivers, or broader causal interpretations unless those exact results were explicitly produced and verified.
- Treat the saved CSVs as the source of truth for completion; resolve any mismatch between those files and earlier notes, console output, or interpretation before finishing.

- First solve the runtime contract, then the analysis: exact action syntax, exact allowed tools/paths, and any exact completion token.
- Prefer explicit commands you can audit and rerun verbatim over high-level descriptions of intended actions.
- If `python` fails, try `python3` only after checking which interpreter is actually available.
- Once outputs are verified, stop cleanly with the required completion action instead of adding an explanatory closing narrative unless the environment explicitly asks for one.
