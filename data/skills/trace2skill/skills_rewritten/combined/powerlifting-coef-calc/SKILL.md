---
name: powerlifting-coef-calc
description: "Calculate Dots coefficients for powerlifting competitions from lifter performance data in Excel files."
---

# Powerlifting Dots Coefficient Calculation

## When to Use

- Calculate Dots score coefficients for powerlifting
- Process International Powerlifting Federation competition data
- Work with multi-sheet Excel files


## When to Use

## Execution Protocol

- Treat task/system-level interaction rules as mandatory deliverables, not optional style.
- If the environment specifies a required tool/action schema, use that exact schema for every tool call from the first step onward; do not substitute another format.
- Before every tool call, mirror the required invocation format exactly; do not emit pseudo-tool tags, XML-like tool calls, ad hoc wrappers, or alternate call syntax.
- If the environment requires one tool action per turn and waiting for the observation, do exactly that; do not batch multiple tool calls in one message.
- Treat protocol compliance as blocking: even if the workbook work is correct, do not continue with a response/tool call that violates the required action format or sequencing rules.
- When creating or editing scripts/files, emit the actual code or the exact executable shell command that writes it; do not use placeholder descriptions like "script to inspect...", "validate numeric values", or "created a workbook processing script".
- Make implementation auditable in the transcript: for any script that inspects or edits the workbook, show the real source code or a concrete here-doc/file-write command with the full contents.
- After writing a script or workbook-editing file, verify the saved artifact is real and usable before relying on it: inspect/read back the file contents or otherwise confirm the written code matches the intended implementation, then run it.
- Before the final response, run a last protocol check: confirm the required tool/action schema was followed for every tool call, confirm no multi-action turn violated a one-action-per-turn rule, and check whether the task/system requires an exact completion token/string or output schema. If so, output exactly that required format and nothing else.
- Treat the required completion token/schema as a hard gate: if the instruction says to end with an exact string such as `ACTION: TASK_COMPLETE`, send exactly that string with no prose before or after it.
- If both workbook edits and protocol compliance are required, verify both before finishing.
## Input Files

- `/root/data/openipf.xlsx`: Competition data
- `/root/data/data-readme.md`: Data format documentation

## Steps

0. Before editing, inspect the workbook directly: confirm sheet names, read the actual `Data` header row, use `/root/data/data-readme.md` to interpret field meanings, and map the real source columns for `Sex`, `BodyweightKg`, and the lift fields used to compute `TotalKg` rather than assuming fixed positions, letters, or names

   - Use workbook-aware tooling from the start: inspect `.xlsx` files with Python/openpyxl (or another spreadsheet library), not a plain-text file reader.
   - Do not attempt to open `.xlsx` with a plain-text reader or equivalent unsupported file-read tool first; go straight to workbook inspection code/tooling.
   - First check which spreadsheet libraries are already installed and use an available workbook library (prefer `openpyxl`) before assuming `pandas` or attempting extra installs.
   - When using shell, issue concrete executable commands only; do not send placeholder-style instructions such as “inspect workbook structure” or “install packages.” If a dependency is missing, first check what is already installed and only then use an environment-compatible fallback such as a local virtual environment.
   - Record the workbook structure up front: sheet names, source row count, exact `Data` headers, and representative or distinct nonblank `Sex` values before making any edits.
   - Follow a staged, auditable build sequence: inspect workbook/schema first, copy source data to `Dots`, append `TotalKg`, append `Dots`, then recalculate and validate. Do not try to generate the whole derived sheet in one unverified step.
   - Prefer a single repeatable script for the workbook transformation (inspect/copy/formula-write/save) instead of many ad hoc cell edits; rerun the script after formula changes rather than patching scattered cells manually.

1. Read the header row of "Data" and copy **all existing columns** to "Dots" in the **exact same order and with the same names**

   - Derive destination headers and source column positions programmatically from the workbook schema.
   - Default to copying the full `Data` schema because this skill's expected deliverable preserves source columns for auditability.
   - Only copy a reduced subset of columns if the task explicitly asks for a derived/report sheet with fewer fields; otherwise, keeping all source columns takes priority even if a narrower sheet would be simpler.
   - Use the observed `Data` headers to build formula references, but do **not** reduce the sheet to only calculation-related columns; preserve the full `Data` header row in the same order, then append new columns.
   - Before writing formulas, map formula inputs back to the copied headers: `Sex`, `BodyweightKg`, and the lift columns that make up `TotalKg`.
2. Preserve row order when copying data from "Data" to "Dots"
   - Build the derived sheet incrementally: finish copying headers/data and confirm row counts/order before adding any formulas.
3. Add "TotalKg" column after the copied source columns using an Excel formula
   - Build the derived sheet incrementally: copy the source columns first, then add `TotalKg`, verify it on representative rows, and only then add `Dots`.
4. Add "Dots" column using an Excel formula with **explicit 3-decimal precision**
5. Before finalizing the `Dots` formula, inspect representative `Sex` values in the source data and confirm the branch values actually used by the workbook.
   - Read distinct/nonblank `Sex` values from the source column before building the formula (for example, confirm whether the workbook uses `M`/`F` exactly). Write the conditional formula against the actual observed values rather than assumed labels.
   - Build `TotalKg` and `Dots` formulas defensively: use `IF`/`ISNUMBER`-style guards (or equivalent Excel checks) so blank, non-numeric, or non-positive required inputs do not yield misleading numbers or Excel errors.
   - If the authoritative DOTS specification or dataset rules require bodyweight bounds, encode the clamp directly in the Excel formula with `MIN`/`MAX`; do not clamp only in Python while leaving the sheet formula inconsistent.

6. If you need to verify DOTS math from external references, do not implement until you have explicitly confirmed the full required specification in-hand: both male and female coefficient sets, polynomial term order/signs, score scaling, and any bodyweight-rule details used by the task/data.
   - Treat partial retrieval as insufficient; keep checking until all required parameters are confirmed from an authoritative source or implementation.
   - Record an explicit completeness check before implementation: male coefficients, female coefficients, polynomial term order/signs, score scaling, and any bodyweight rule are all confirmed. If any one is missing, stop and keep verifying.
   - Do not infer missing coefficients from memory when the retrieval evidence is incomplete.
   - If rendered docs/calculators or high-level documentation are incomplete, prefer the canonical implementation source file or another implementation-oriented source that exposes the exact coefficients/code, and copy coefficients/term order from that source exactly.
   - Record the final coefficient set you are using before writing formulas so you can compare the saved Excel formula against that exact spec.
7. When filling formulas down, make them blank-safe so rows with missing required inputs stay blank instead of showing errors or misleading numbers.
8. Use `openpyxl` to modify the existing workbook in place, then save, run the provided workbook recalculation helper when available (for example, `recalc.py`), and reopen the workbook twice when possible: once normally to inspect stored formulas and once with `data_only=True` to inspect computed values. Inspect the `Dots` header row plus representative top/middle/bottom rows to confirm headers still match `Data` through the copied columns, row counts/order were preserved, formulas were stored and filled down consistently, and both `TotalKg` and `Dots` evaluate to plausible nonblank 3-decimal results rather than silently wrong outputs such as all `0.000`.
   - Prefer low-dependency verification: if higher-level dataframe tools are unavailable, use `openpyxl` alone to inspect headers, row counts, stored formulas, and `data_only=True` evaluated values after recalculation.
   - Do not treat a successful save or recalculation as proof of correctness; require both stored-formula inspection and evaluated-value inspection after recalculation.
9. Before declaring success, run a minimum validation and auditability check: (a) read back the full stored formula text for representative `TotalKg` and `Dots` cells in top/middle/bottom data rows, not truncated previews; (b) confirm the sampled `Dots` formulas reference the intended `Sex`, `BodyweightKg`, and `TotalKg` cells and preserve the required polynomial structure; (c) confirm formulas are filled down for the full populated range; (d) do not rely on a single-row check, recalculation success, absence of Excel errors, or cell formatting as proof of correctness; and (e) in your work log/transcript, show the resolved header/column mapping plus at least one complete representative `TotalKg` formula and one complete representative `Dots` formula from the saved sheet.
   - Also recompute at least one representative row manually or independently from the observed input values after recalculation, and confirm the saved `TotalKg` and `Dots` results match to 3 decimals. Use this as a logic check, not just a formatting check.
   - If a sampled `Dots` value looks implausible (for example, `0.000` for a normal nonblank row), do not finalize until this independent check agrees with the Excel result.
   - Do not rely on high-level summaries such as “updated workbook” or “verified sample rows.” Make the critical transformation observable by showing the actual script/command content or equivalent concrete formula text in the transcript.
10. Before sending the final response, perform a final compliance gate: (a) confirm all prior tool calls used the exact required invocation schema and respected any one-action-per-turn rule; (b) confirm any written scripts were shown as actual code/commands in the transcript, not placeholders; and (c) check whether the task requires an exact completion token or output schema. If it does, output exactly that required string/schema and nothing else.

## Dots Formula

Dots uses both `TotalKg` and `BodyweightKg`.
- DO NOT use a log-based formula or any formula that depends only on `TotalKg`.
- Use sex-specific polynomial coefficients on `BodyweightKg`, then multiply by `TotalKg`:
  - Male denominator: `-307.75076 + 24.0900756*w - 0.1918759221*w^2 + 0.0007391293*w^3 - 0.000001093*w^4`
  - Female denominator: `-57.96288 + 13.6175032*w - 0.1126655495*w^2 + 0.0005158568*w^3 - 0.0000010706*w^4`
  - Score: `DOTS = 500 / denominator * TotalKg`
- Excel pattern: `=ROUND(IF(SexCell="M",500*TotalKgCell/(-307.75076+24.0900756*BodyweightCell-0.1918759221*BodyweightCell^2+0.0007391293*BodyweightCell^3-0.000001093*BodyweightCell^4),500*TotalKgCell/(-57.96288+13.6175032*BodyweightCell-0.1126655495*BodyweightCell^2+0.0005158568*BodyweightCell^3-0.0000010706*BodyweightCell^4)),3)`

- Build the Excel formula from the required inputs `Sex`, `BodyweightKg`, and `TotalKg`, and confirm the final written formula references those exact columns.
- Reject any candidate DOTS formula that is log-based, depends only on `TotalKg`, omits `BodyweightKg`, or changes the polynomial term order/signs even if Excel recalculates it successfully.
- Keep the bodyweight polynomial terms exactly as specified (`w`, `w^2`, `w^3`, `w^4` with the listed coefficients); if any coefficient or term order is uncertain, verify it against an authoritative specification or implementation before writing formulas.
- Before filling down, test at least one concrete sample row manually or with an independent calculation using that row's `Sex`, `BodyweightKg`, and `TotalKg`; treat implausible outputs (for example, near-zero or wildly off expected scale) as a formula-assembly error even if Excel recalculates cleanly.
- For that manual sample, evaluate the denominator terms in order against the written coefficients/signs so you can catch coefficient-order mistakes that still produce syntactically valid Excel formulas.
- Prefer a defensive Excel pattern around the core polynomial: keep the exact DOTS math, but wrap it so rows with missing, non-numeric, or non-positive required inputs stay blank instead of producing errors.
- If bodyweight clamping is explicitly required by the task or data rules, encode the clamp directly in the Excel formula with `MIN`/`MAX` rather than preprocessing values outside the sheet.

## Output

Modify "Dots" sheet in openipf.xlsx with:
- Original columns from Data
- New "TotalKg" column (formula)
- New "Dots" column (formula)
- 3 digit precision throughout

- Keep every source column from `Data` before the new columns; do not drop intervening columns or reorder headers
- `TotalKg` and `Dots` must be Excel formulas stored in the sheet, not hard-coded values
- Stored formulas should be defensive as well as correct: blank or invalid source rows should remain blank rather than displaying `#VALUE!`, `#DIV/0!`, or a seemingly valid score from bad inputs
- Enforce 3-decimal results for `TotalKg` and `Dots` with `ROUND(...,3)` and/or cell number format `0.000`
- Determine formula inputs from the actual `Data` sheet schema before inserting formulas, but still copy all existing source columns to `Dots` in the original order.
- Do not report success until you have read back representative stored formula strings from the saved sheet and confirmed they are formulas, use the intended cells, preserve the required DOTS structure, and, after recalculation, evaluate to numeric 3-decimal results via a `data_only=True` reopen.
- Also inspect the recalculated numeric results for representative rows; a valid stored formula string alone is not sufficient if the computed values are implausible or collapse to `0.000`.
- Preserve the proven build order in the workbook artifact: copied source columns first, then appended `TotalKg`, then appended `Dots`, with row order unchanged throughout.
- In the transcript, include concrete evidence of the implementation: the resolved header mapping and at least one complete read-back `TotalKg` formula and one complete read-back `Dots` formula from the saved workbook.

- Minimum sign-off check: verify headers, verify full stored formulas in representative top/middle/bottom rows, verify the populated formula range extends through the last data row, and do not report completion from a single sampled row or truncated formula preview.
- Include at least one manual spot-check against the recalculated workbook values using the row's actual inputs, so validation covers formula logic as well as formula presence.
- Include one concrete sanity-check result in your log: identify the sampled row values and show the independently checked `Dots` result you used to confirm the Excel formula is mathematically plausible, not just syntactically valid.
- In your transcript/log, include enough concrete evidence for auditability: the resolved source-to-destination column mapping and complete read-back formula text for representative `TotalKg` and `Dots` cells.
- Do not treat a clean recalculation, lack of Excel errors, or correct number formatting as sufficient validation on its own.

## Tips

- Prefer an installed workbook-capable library (`openpyxl` first when available); if a preferred tool such as `pandas` is missing or unsuitable for in-place formula editing, immediately switch to an available library that can inspect, modify, save, and reread the `.xlsx` file.

- Do not try to read `.xlsx` as plain text; use workbook inspection code instead.
- Prefer `openpyxl` for workbook inspection, in-place sheet editing, row copying, and formula insertion; use it as the default fallback if dataframe libraries are unavailable
- If `pandas` is unavailable but `openpyxl` is installed, proceed with `openpyxl` rather than blocking on extra dependencies; it is sufficient for header inspection, row copying, formula writing, saving, and verification
- Before coding, check which spreadsheet libraries are installed; if needed packages are missing and system install is blocked, create a temporary/local virtual environment and install only the required spreadsheet tools there
- If a package import fails, first inspect what is already available in the environment, then use an environment-compatible fallback; do not jump straight to system-wide installation attempts.

- In shell/tool calls, use fully specified executable commands; avoid vague natural-language command descriptions that the environment cannot execute.
- Read `/root/data/data-readme.md` first, then inspect the actual `Data` sheet headers and sample values so formulas reference the real source columns and the `Sex` branch matches the dataset's actual category values
- Record the resolved sheet/header/column mapping before writing formulas so the final formula references can be audited against the observed workbook schema
- Use Excel formulas for derived columns, not hard-coded values, so the saved workbook remains transparent, auditable, and recalculable
- Match lifter names exactly
- Verify formula syntax for Excel
- When reference pages are incomplete or hide the math, prefer authoritative raw source/spec files over calculator frontends

- Derive destination headers programmatically from the `Data` sheet header row; do not hand-pick a subset of columns unless the task explicitly says to
- Use explicit formulas such as `=ROUND(<sum formula>,3)` and `=ROUND(<dots formula>,3)` instead of raw unrounded coefficients/results
- If you identified a column as required for the calculation, confirm the final Excel formula actually references that column
- Treat successful recalculation as a syntax check only; also verify the formula structure matches the intended DOTS method
- DO NOT stop after verifying one truncated formula string; inspect the complete formula text and sample multiple rows
- Check that formulas reference the intended bodyweight/sex/total cells and that the same pattern is filled down the sheet
- Validate after writing: confirm `Dots` headers match `Data` headers exactly up to the appended columns, and inspect representative rows to verify formulas are populated and results show 3-decimal precision
- Successful pattern: inspect sheet names and `Data` headers first, write Excel formulas into `Dots`, run `recalc.py`, then read back representative headers/formulas/results before reporting success
- If the task requires an exact final completion token or output format, output exactly that string and nothing else
- When the runtime mandates a specific action/tool-call schema, never improvise alternate tags or wrappers; protocol compliance is a required deliverable, not a style preference.
- Do not describe file contents abstractly when writing scripts; show the real code/content so the implementation is auditable from the transcript.

- Use schema/dependency inspection to find required input columns, but still copy **all** `Data` columns to `Dots` unless the task explicitly says otherwise
- Treat successful recalculation as a syntax check only; also verify the workbook artifact directly by reopening once normally and once with computed values when possible
- Read back complete stored formulas, not truncated previews, for representative `TotalKg` and `Dots` cells in multiple rows
- Confirm the filled-down formulas keep the same relative-reference pattern across sampled rows and still reference the intended `Sex`, `BodyweightKg`, lift, and `TotalKg` cells
- After writing the workbook, read back the `Dots` header row itself and confirm it matches `Data` exactly through the last copied source column, with only `TotalKg` and `Dots` appended afterward
- Compare at least one sampled `TotalKg` and `Dots` result against an independent/manual calculation to catch coefficient or reference mistakes that still recalculate cleanly
- When doing that comparison, record enough detail to audit the check: the sampled row identifier, the input cells/values used, and the manually computed denominator/score or equivalent intermediate math.
- Use scripts only to edit the workbook; treat the saved Excel workbook formulas as the required deliverable, not just the script logic
- Use a simple two-layer validation pattern that has worked well in practice: first confirm formulas recalculate/fill down through the last data row, then spot-check a few representative rows by reading both the stored formula text and the resulting numeric values.
- When spot-checking, sample at least top/middle/bottom rows so row-reference mistakes are more likely to be caught than with a single-row check.
- For multi-column workbook changes, default to writing one concrete script that performs the full transformation and can be rerun cleanly after fixes
- After saving formulas, run recalculation and reopen once with formulas visible and once with `data_only=True` to verify both stored formula text and evaluated numeric outputs
