---
name: protein-expression-analysis
description: "Analyze protein expression data from cancer cell lines comparing control vs treated conditions with fold change calculations."
---

# Protein Expression Analysis

## When to Use

- Analyze proteomics data from cancer cell lines
- Compare control vs treated expression levels
- Calculate fold changes and statistics

## Input Files

- `protein_expression.xlsx`: Two sheets ("Task" and "Data")
- Data has 200 proteins × 50 samples (log2-transformed)

## Steps

**Range anchor rule:** Treat the user/task specification as the source of truth for required output blocks. For this skill, stay focused on `C11:L20`, `B24:K27`, and `C32:D41`; only inspect nearby headers/labels needed to map proteins, sample names, and Control vs Treated columns.


4. **Write back to the workbook**
   - Populate the required cells in `Task`; do not stop after inspecting or summarizing.
   - When filling many cells, test one representative formula first, then propagate the same pattern across the range.
   - If programmatic edits are long or keep getting cut off, switch to a standalone script file instead of pasting long inline commands.

5. **Verify before finishing**
   - Save the workbook, reopen it, and inspect all required output blocks: `C11:L20`, `B24:K27`, and `C32:D41`.
   - Read back representative cells from each region and confirm formulas reference the intended protein row, sample header, and Control/Treated grouping.
   - Recalculate the workbook and inspect for formula errors; if recalculation is unavailable, validate with available alternatives such as reopened formula inspection, dependency checks, and representative result cells.
   - Do not consider the task complete until the workbook has been saved and the edited ranges have been verified cleanly.



## Preflight Checks

- Confirm the actual workbook filename and path before opening it; do not assume `protein_expression.xlsx` exists without checking.
- Inspect the workbook directly before writing formulas. Confirm sheet names, used ranges, the protein ID/symbol column, the sample header row, and where Control vs Treated labels appear.
- Inspect the `Task` sheet around the destination areas (`A11:L20`, `A24:K27`, `A32:D41`) so the output layout is taken from the workbook, not inferred from prose alone.
- If the workbook layout conflicts with the nominal description, follow the workbook's actual structure.
- If any inspection output is truncated or unclear, rerun a narrower inspection until the relevant rows/columns are fully visible.

1. **Pull expression data** (C11:L20 in Task sheet)
   - Match 10 target proteins (column A rows 11-20)
   - Match sample names from row 10
   - Use INDEX-MATCH or similar

2. **Calculate statistics** (rows 24-27, columns B-K)
   - For each protein: mean, stdev for Control and Treated
   - Row 9 shows Control (blue) vs Treated

3. **Fold change** (columns C-D, rows 32-41)
   - Log2 Fold Change = Treated Mean - Control Mean
   - Fold Change = 2^(Log2 Fold Change)

## Important Notes

- Don't modify file format, colors, or fonts
- No macros or VBA
- Use formulas not hard-coded values
- Sample names have prefixes like "MDAMB468_BREAST_TenPx01"


- This is an edit-the-file task, not a report-only task: workbook inspection is only preparation for writing the requested outputs.
- Build formulas only from confirmed workbook structure; do not assume `Data` ranges, header positions, sample-group splits, or destinations without inspection.
- Build Excel formulas as plain strings with exact sheet/range syntax; double-check quotes and parentheses before writing.
- Prefer widely supported functions such as `INDEX`, `MATCH`, `AVERAGE`, `STDEV.S`, `IF`, and basic arithmetic.
- Do **not** rely on newer or dynamic-array functions such as `FILTER` unless you have confirmed they recalculate successfully in this workbook environment.
- Treat truncated commands, partial tool output, or malformed first writes as blocking issues: fix the write path, then verify the saved workbook rather than guessing at alternate formula syntax.
- Do not declare completion after only printing formula strings or checking a few cells; verify the full required output areas are filled coherently.
- Follow any task-specific tool-use or completion protocol outside this skill exactly as given.


## Tips

- openpyxl for Excel reading/writing
- Use pandas for data manipulation
- Verify log2 transformation for fold change


- Prefer shorter, complete scripts over long inline commands when editing many cells.
- After writing formulas, perform a write-read-recalc loop: save the workbook, reload it, confirm representative stored formulas exactly match what you intended, then check for `#NAME?`, `#VALUE!`, or similar errors.
- If errors appear, rewrite the formulas, save, and verify again until the target cells evaluate cleanly.

