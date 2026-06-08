# Validation and Debugging

Use this when the workbook recalculates with errors or when formula results look suspicious.

## Completion checklist

1. Save the workbook.
2. Recalculate with the required task method.
3. Inspect reported error cells.
4. Do **not** finish until required output cells are free of spreadsheet errors.

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

## Do / Do not

- **Do:** print concise checkpoints such as `saved=/root/output/rar_result.xlsx`, key target-cell values, and `error_count=...`.
- **Do:** save longer Python logic to a file and run it so command output shows a clear success/failure message.
- **Do not:** keep swapping among `INDEX+MATCH`, `XLOOKUP`, direct references, or hardcoded values without proving why the current formula fails.
- **Do not:** treat workbook editing as complete before post-write validation succeeds.
