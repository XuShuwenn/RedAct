# Validation and Debugging

Use this when the workbook recalculates with errors or when formula results look suspicious.

## Completion checklist

1. Save the workbook.
2. Recalculate with the required task method.
3. Inspect reported error cells.
4. Read back representative stored formulas from the required output area.
5. Reopen the saved workbook and inspect representative deliverable cells in `Answer`.
6. Confirm required cells contain the expected formulas when formulas are required, evaluate without spreadsheet errors, and still match the requested row meanings/country set.
7. Verify any bounded-period result (for example Jan-Sep 2025) is backed by complete source-period coverage.
8. Confirm the workbook used was the provided template/workbook, not a newly created substitute.
9. Do **not** finish until required output cells are free of spreadsheet errors and semantically match the task.

10. If any earlier run crashed, raised an exception, or stopped after diagnostic output, rerun the full workflow and confirm normal completion before reporting success.
11. If recalculation/validation reports any workbook error at all, treat it as unresolved until you verify whether the task explicitly allows it; do not wave it away based on sheet location alone.
12. If you changed any formula after an earlier validation pass, invalidate that earlier pass and rerun the full checklist on the final saved workbook.
13. If critical previews of `Answer`, formula text, recalc output, or script output are truncated, clipped, or omit the final Step 2/Step 3 displayed values, rerun narrower inspections until the required evidence is complete.
14. Confirm critical result cells were checked in evaluated/value mode after recalculation; formula text alone does not prove completion.
15. For copied/fill-down formulas in tabular areas, compare at least two non-adjacent rows and confirm references changed row-appropriately instead of repeating the same source cells.
16. If formulas must produce final answers, treat lack of recalculation capability as a blocker rather than finishing with unevaluated formulas.
17. Before the final response, compare your planned last message against the exact completion protocol; if a literal token is required, output that token alone with no surrounding prose.

18. Before the first tool use, verify the environment's required action/tool-call syntax and follow it consistently for the entire run; do not switch to habitual wrappers or alternate call formats mid-task.
19. If workbook discovery required searching for files, confirm that search stayed inside task-authorized directories only; if an earlier command wandered into restricted paths or produced permission errors, redo the search narrowly before relying on its results.
20. If the environment provides a working spreadsheet engine capable of recalculation/finalization, use it before reporting success; do **not** defer recalculation to the user.
21. Distinguish structural validation from completion: after the final recalc/save/reopen cycle, inspect key deliverable cells in evaluated/value mode and confirm they contain usable results, not merely intact formulas.
22. After any cleanup of Step 2 or Step 3, reread the full edited target block end-to-end, not just one sample cell. Do not proceed while duplicates, stale values, unsupported countries, interior blanks, or unintended formula text in label cells remain anywhere in that block.
23. Confirm the final Step 2 and Step 3 country blocks match the same prevalidated inclusion list exactly; any country excluded for missing downstream prerequisites must be absent from both blocks.
24. Verify the exact deliverable path last: reopen `/root/output/rar_result.xlsx` after the final save/rename/copy step and confirm it loads successfully before completion.
25. If a required `Answer` cell is supposed to reflect or link to a computed source result, compare the reopened evaluated `Answer` value to the intended source/result cell after recalc. Do not accept source-sheet correctness as a substitute for incorrect displayed deliverable cells.
26. If the same reopened target cell stays wrong across multiple save/recalc/reopen attempts, stop calling it a cache issue and debug the exact reference path, workbook path, sheet names, and formula logic until the saved deliverable cell itself is correct.
27. If any workbook error is still present, document the exact sheet/cell and dependency check showing why it does not affect required outputs before concluding it can remain.
28. If the main write/update script previously crashed, require one later run that clearly exits without traceback or exception before reporting success.
29. After the final validation pass succeeds, stop. Do not append a human-readable summary, workbook description, or `next steps` message after the required completion token.
## Debug one failing cell at a time

For each failing cell:

1. Identify the exact formula in that cell.
2. Check every precedent cell/range it references.
3. Confirm source values are the expected type:
   - numbers stored as numbers, not text
   - dates recognized as dates if date logic is used
   - lookup keys match exactly
4. Test the chain in smaller pieces:
   - verify the lookup key cell
   - verify the lookup range contains that key
   - verify the returned source cell is numeric before using it in arithmetic
5. Only change the formula pattern after locating the real mismatch.

5a. If the first failing mechanism is unclear, stop broad script editing and gather one concrete repro: exact workbook path, failing cell, stored formula, evaluated result/error, and the source cells it should have matched.
5b. Do not describe a fix abstractly; inspect the current failing expression or code line, change that exact mechanism, then rerun the same cell check.


6. For the first reported failing deliverable cell, capture: workbook path, sheet name, cell address, stored formula text, evaluated value/error, and the key precedent cells/ranges.
7. Fix that one mechanism first and re-test the same cell after recalc; only after it works should you fill/copy the corrected pattern elsewhere.
8. If Python-side arithmetic or decision logic uses workbook values, inspect the exact matched source cell(s), their labels, and the resulting Python value/type before calculating.
9. If an operand is a timestamp/date, string label, header, empty value, or other nonnumeric content where a number is expected, treat that as a row/column selection bug and fix the extraction boundary before proceeding.
10. If an error is outside the requested output area, verify dependency impact before ignoring it:
   - inspect whether any required `Answer` or `Gold price` formula references that cell, row, sheet region, or derived result
   - if dependency is unclear, treat the error as blocking until proven otherwise
   - only leave it unresolved when you have explicit evidence it is outside the deliverable and not referenced
10a. Do not label an error `pre-existing` or `irrelevant` without this proof. Record the exact offending cell and the dependency check you performed before treating it as non-blocking.
10b. If a script is meant to inspect or update the workbook, keep the script itself observable: write executable code, then review its actual contents or runtime output. Do **not** rely on placeholder descriptions of what the script was supposed to do.
10c. Before any Python-side arithmetic that uses extracted workbook values, print or inspect the exact operand source cells plus Python types for a representative case. If a supposed numeric operand is a `Timestamp`, date, string, header, or blank, fix the row/column match before debugging the arithmetic.

11. If many cells show the same error class, especially `#NAME?`, treat it as a formula-engine compatibility issue first, not many independent business-logic failures.
12. Prove the fix on one representative cell, save, recalculate, reopen, and read back both the stored formula text and evaluated value before fill-down.
13. If your verification command errors or truncates before covering the full target block, treat the check as inconclusive and rerun smaller targeted inspections until all required rows/cells are confirmed.


## Formula-string and lookup checks

Use this when formulas were written programmatically or when Step 3 lookups fail.

1. Read back representative written formulas before and after save.
2. Confirm each formula is a complete plain Excel formula string:
   - starts with `=`
   - contains valid sheet-qualified references like `='Gold price'!D430` when needed
   - contains no stray backslashes, broken quotes, truncation, or partial fragments
3. If the error is `#NAME?`, check function compatibility and stored formula syntax before changing business logic.
3a. Explicitly verify separator/dialect compatibility on a tiny representative formula before bulk-writing: confirm whether the workbook engine accepts the exact generated syntax, then reuse that proven pattern consistently.
3b. Count function arguments in the stored formula string for representative cells. If an `IF`, `INDEX`, `MATCH`, or other formula has an unexpected extra or missing argument, fix the string-construction logic first rather than debugging downstream values.
3c. For mass `#NAME?` errors, test the specific function names used in a representative failing cell first. If a newer function is not explicitly required by the task/template, prefer a compatibility-safe equivalent after the first failed smoke test rather than letting `#NAME?` spread through the workbook.
4. For `INDEX`/`MATCH`, verify range orientation explicitly:
   - if `INDEX` spans one row across columns, use `MATCH` as the column index
   - if `INDEX` spans one column down rows, use `MATCH` as the row index
   - if both country and year are looked up, verify each `MATCH` aligns with the correct dimension
5. Inspect the exact target range before and after rewriting it to confirm stale formulas, duplicate country names, or leftover values are actually gone.
6. After fixing one representative cell, recalculate and confirm it evaluates correctly before fill-down/copying the pattern.
7. If one representative formula or rewritten target cell is wrong, stop and fix that write pattern before filling more cells.

8. Before filling a lookup/table pattern broadly, prove engine support with 1-2 representative formulas in the actual workbook. If recalc shows `#NAME?` or parser errors, replace that pattern with a compatibility-safe one before any copy/fill.
9. If a post-save/readback preview shows blanks, `None`, or `NaN` in required formula columns, do not assume the formulas exist but were merely hidden by the reader. Inspect the exact cell formulas directly from the reopened workbook and confirm they still start with `=`.
10. For cross-sheet country/year lookups, spot-check 2-3 countries end-to-end: country label in `Answer`, matched source row/column in the source sheet, stored lookup formula text, and returned numeric value.
11. Reject permissive lookup formulas for country keys in required outputs. Use exact-key lookup against the workbook's verified label set and confirmed orientation rather than wildcard or substring matching.
12. Distinguish text cells from formula cells before and after writing a block: country names, row labels, and headers should usually be stored as plain text, while only calculation cells should start with `=`.
13. Reject incomplete formulas during readback. If a representative formula ends with an operator or missing argument, stop and repair that write pattern before any broader fill.
14. If verification output is truncated or a summary line omits the actual value, rerun targeted reads for the exact cells instead of relying on the incomplete report.

15. Before filling any new formula family broadly, do a recalculation smoke test on 1-2 representative cells in the actual workbook engine. Start with the most compatibility-safe pattern that satisfies the task/template; if the tiny test yields `#NAME?`, parser errors, wrong evaluation, unsupported function names, or separator/dialect problems, switch to a compatibility-safe equivalent before bulk fill.
16. For statistical functions and other less-common Excel names, verify the exact function spelling supported by the recalc engine in one representative cell before broad use. If the task only needs a fixed parameter or threshold and not a live formula, prefer storing the literal numeric constant instead of an engine-sensitive function.
17. When Step 3 mirrors Step 2, audit completeness explicitly after fill: compare the final included-country list, Step 2 country cells, and Step 3 country cells one-by-one so a silently skipped middle country or broken reference chain is caught before finish.
18. If recalculation still reports a source-sheet error on any sheet referenced by deliverable formulas, inspect the exact cell contents. Treat literal placeholders such as `=#N/A` as active blockers when they remain in the dependency path.
19. If validation still reports any error after your last fix, do not finalize. Open the exact reported location, determine whether required outputs depend on it, and either repair it or surface it as a blocking unresolved issue.

## Do / Do not

- **Do:** print concise checkpoints such as `saved=/root/output/rar_result.xlsx`, key target-cell values, and `error_count=...`.
- **Do:** save longer Python logic to a file and run it so command output shows a clear success/failure message.
- **Do not:** keep swapping among `INDEX+MATCH`, `XLOOKUP`, direct references, or hardcoded values without proving why the current formula fails.
- **Do not:** treat workbook editing as complete before post-write validation succeeds.

- **Do:** treat script exit status, pandas/openpyxl previews, or truncated dumps as insufficient proof of completion; verify the saved workbook itself.
- **Do:** test engine compatibility with a minimal representative formula before introducing a new function across many cells.
- **Do:** keep debugging scoped to required deliverable cells and compare suspicious `Answer` values directly to their intended source cells.
- **Do:** if the task says Excel-only, keep all business logic in worksheet formulas and use Python only for workbook I/O/verification when the task allows it.
- **Do not:** create substitute workbooks/sheets or synthesize missing source data.
- **Do not:** replace a required lookup formula with a direct reference, Python-side value, or hard-coded mapping unless the task explicitly permits that substitution.
- **Do not:** blank or alter unrelated source-sheet cells just to make recalc reports look cleaner.
- **Do not:** add any prose before or after a required exact completion token.

- **Do:** follow the environment's required tool/action format exactly when invoking tools.
- **Do:** echo/check the exact workbook path before listing sheets or reading target cells, especially when both downloaded source files and template workbooks exist.
- **Do:** after every workbook-writing script, print a compact proof line such as `saved=/root/output/rar_result.xlsx checked=Answer!B12,Answer!C24,Gold price!D430` and then verify those cells by reopening the file.
- **Do:** inspect the raw Step 2/Step 3 country candidates before writing summary tables; remove placeholders like `Unnamed`, header/metadata text, and duplicate alias labels before propagating the set.
- **Do:** after recalc succeeds, inspect the entire required target block for completeness; zero errors does not prove every required cell or row was populated.
- **Do not:** conclude success from `ls`, file existence, or a successful save alone.
- **Do not:** trust truncated command output as proof that a write/update script finished.
- **Do not:** inspect one workbook and then apply those structural conclusions to another workbook with a different path.
- **Do not:** call a workbook error "pre-existing" and move on without proving it is outside the deliverable scope and not referenced by required outputs.
- **Do not:** stop at `error_count=0` if any required deliverable positions are still blank, partially filled, or semantically incomplete.
- **Do not:** add any prose before or after a required exact completion token.

- **Do:** if the environment mandates a specific `Thought`/`Action` or JSON tool protocol, verify each command you emit matches that syntax exactly before sending it.
- **Do:** for critical workbook-generation steps, show the actual script body, formula-writing logic, or exact command arguments somewhere in the run so the edit path is reviewable.
- **Do:** validate parsing assumptions on representative raw source rows/fields before committing date parsing, header selection, or unit conversions in a full script.
- **Do:** switch from brittle one-liners to a short saved script as soon as workbook inspection needs loops, multiple reads, or formatted output; then run that script immediately and verify its output.
- **Do not:** summarize a failed or blocked fetch as if the required dataset had been obtained.
- **Do not:** infer success from a validator run whose output stops early or omits the final recalc/verification status line.
- **Do not:** erase a template error cell just to make workbook-wide error counts disappear; first prove deliverable dependence and in-scope responsibility.
- **Do not:** treat an unexecuted inspection or processing script as progress.
- **Do not:** keep retrying blocked external-download commands after several results show the same denial pattern; record the blocker and pivot to workbook-local work.
- **Do not:** add any prose before or after a required exact completion token.
