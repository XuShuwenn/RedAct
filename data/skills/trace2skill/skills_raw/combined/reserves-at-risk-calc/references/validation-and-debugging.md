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


## Formula-string and lookup checks

Use this when formulas were written programmatically or when Step 3 lookups fail.

1. Read back representative written formulas before and after save.
2. Confirm each formula is a complete plain Excel formula string:
   - starts with `=`
   - contains valid sheet-qualified references like `='Gold price'!D430` when needed
   - contains no stray backslashes, broken quotes, truncation, or partial fragments
3. If the error is `#NAME?`, check function compatibility and stored formula syntax before changing business logic.
4. For `INDEX`/`MATCH`, verify range orientation explicitly:
   - if `INDEX` spans one row across columns, use `MATCH` as the column index
   - if `INDEX` spans one column down rows, use `MATCH` as the row index
   - if both country and year are looked up, verify each `MATCH` aligns with the correct dimension
5. Inspect the exact target range before and after rewriting it to confirm stale formulas, duplicate country names, or leftover values are actually gone.
6. After fixing one representative cell, recalculate and confirm it evaluates correctly before fill-down/copying the pattern.
7. If one representative formula or rewritten target cell is wrong, stop and fix that write pattern before filling more cells.

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
