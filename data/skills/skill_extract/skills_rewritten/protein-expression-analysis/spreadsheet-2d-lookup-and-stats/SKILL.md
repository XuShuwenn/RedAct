---
name: spreadsheet-2d-lookup-and-stats
description: "Use this to populate spreadsheets via two-way lookups, compute group-wise means/SD, and derive fold changes using robust formulas with verification."
---

# Spreadsheet Two-Way Lookup and Group Comparison

A reusable workflow for spreadsheet tasks that require pulling values from a data table by matching both a row identifier (e.g., protein ID) and a column header (e.g., sample name), then computing group-wise statistics and fold changes using spreadsheet formulas. Designed to preserve formatting and avoid hard-coded values.

## When to Use

Activate this skill when asked to:
- Fill a grid of values on one sheet by matching identifiers and headers from another sheet (two-way lookup)
- Compute group summary statistics (mean and standard deviation) from looked-up values
- Calculate log2 fold change and fold change between two conditions
- Keep the workbook dynamic using formulas instead of static numbers

## Core Workflow

1. Inspect and map the workbook
   - Identify which sheet contains the destination grid (e.g., a "Task" sheet) and which sheet contains the source table (e.g., a "Data" sheet).
   - Locate the identifier column (rows) and the header row (columns) on the source table.
   - Locate the destination identifiers and the destination headers that correspond to the source table.
   - Confirm the group label row or area (e.g., a header row labeling columns as "Control" and "Treated").

2. Implement two-way lookup formulas
   - Use a cross-sheet two-way lookup to retrieve values by matching identifier and header.
   - Robust pattern (Excel/LibreOffice compatible):
     - INDEX/MATCH pattern for a single destination cell:
       =INDEX(DataValuesRange, MATCH(DestIdentifierCell, DataIdentifierRange, 0), MATCH(DestHeaderCell, DataHeaderRange, 0))
   - Notes:
     - Use absolute references (e.g., $A$:$Z$) for anchor ranges so filled formulas stay aligned.
     - MATCH(..., 0) enforces exact matches; ensure identifiers and headers match exactly.
     - If headers contain prefixes or extra whitespace, consider CLEAN/TRIM on header cells or standardize labels beforehand. As a formula alternative, test a single cell with TRIM/CLEAN on the lookup key to diagnose whitespace problems.

3. Compute group statistics
   - Group means:
     - If dynamic arrays (Excel 365/LibreOffice) are available:
       =AVERAGE(FILTER(ValuesRowRange, GroupLabelRowRange="Control"))
       =AVERAGE(FILTER(ValuesRowRange, GroupLabelRowRange="Treated"))
     - Without FILTER, use SUMPRODUCT/COUNTIF:
       =SUMPRODUCT((GroupLabelRowRange="Control")*ValuesRowRange) / COUNTIF(GroupLabelRowRange, "Control")
       =SUMPRODUCT((GroupLabelRowRange="Treated")*ValuesRowRange) / COUNTIF(GroupLabelRowRange, "Treated")
   - Group standard deviations (sample SD):
     - Preferred function: STDEV.S
     - With dynamic arrays:
       =STDEV.S(FILTER(ValuesRowRange, GroupLabelRowRange="Control"))
       =STDEV.S(FILTER(ValuesRowRange, GroupLabelRowRange="Treated"))
     - Without FILTER (array formula):
       =STDEV.S(IF(GroupLabelRowRange="Control", ValuesRowRange))
       =STDEV.S(IF(GroupLabelRowRange="Treated", ValuesRowRange))
       Enter as an array formula if required by your spreadsheet engine.
   - Compatibility tips:
     - STDEV.S is widely supported. If #NAME? appears, try STDEV or STDEVP/STDEV.P according to engine support.
     - Locale may require semicolons (;) instead of commas (,) as argument separators.

4. Derive comparison metrics
   - Log2 Fold Change:
     =TreatedMeanCell - ControlMeanCell
   - Fold Change:
     =POWER(2, Log2FoldChangeCell)
   - Do not reconvert data that is already log2; use the difference of means directly for log2 fold change.

5. Preserve formatting and use formulas only
   - Do not alter styles, colors, or fonts.
   - Avoid hard-coded numbers in the output ranges; rely on formulas referencing the lookup and group labels.

6. Recalculate and verify
   - Recalculate the workbook.
   - If the environment does not auto-recalculate, open the file in a spreadsheet application and recalc.
   - Run verification checks (see below).

## Verification

Perform these checks before finalizing:
- Lookup integrity
  - Spot-check a few cells: confirm the two-way lookup returns the expected value by manually comparing the identifier and header against the source table.
  - Ensure ranges in INDEX/MATCH use absolute references so fills don’t drift.
  - Confirm there are no #N/A results caused by label mismatches; diagnose with TRIM/CLEAN if needed.
- Group labels alignment
  - Count the number of columns labeled per group; confirm these match the number of values included by your formulas.
  - Verify the label strings exactly match the formula criteria (e.g., "Control", "Treated").
- Function compatibility
  - Test a simple formula (e.g., =SUM(1,2)) to confirm the argument separator.
  - If SD cells show #NAME?, switch to a supported SD function (STDEV.S, STDEV, or STDEV.P) based on the engine.
- Final results
  - Check that statistic cells show numeric outputs without errors.
  - Confirm log2 fold change equals treated mean minus control mean.
  - Confirm fold change equals POWER(2, log2 fold change) and is > 0.

Success criteria:
- Destination lookup grid fully populated with dynamic formulas (no hard-coded values).
- Group means and standard deviations computed without errors.
- Log2 fold change and fold change cells compute correctly.
- Original workbook formatting preserved.

## Common Pitfalls and How to Avoid Them

- Misaligned lookups due to relative references
  - Use absolute references ($) for source ranges in INDEX/MATCH.
- Wrong function or locale syntax
  - #NAME? often indicates an unsupported function or incorrect separator. Try STDEV.S, STDEV, or STDEV.P, and adjust separators.
- Not matching both identifier and header
  - VLOOKUP alone matches only a single dimension. Use INDEX with two MATCH calls for robust two-way lookup.
- Hidden whitespace or prefixes in headers
  - If MATCH returns #N/A, test TRIM/CLEAN on the header cell or standardize labels.
- Incorrect grouping
  - Verify that the group label row exactly matches the criterion strings used in AVERAGE/FILTER/SUMPRODUCT logic.
- Recalculating assumptions
  - Some environments do not evaluate formulas. If cached results are stale or missing, open in a spreadsheet application to recalc.

## Optional Script Usage

Use the helper script to quickly audit that formulas exist in target ranges and that cached values do not contain errors. This does not modify the workbook; it reports findings.

Example:
- python3 scripts/check_sheet.py --workbook your.xlsx --sheet Task --ranges C11:L20 B24:K27 C32:D41 --group-label-range B9:K9 --allowed-labels Control Treated

Interpretation:
- Confirms formulas present in ranges and counts cached error tokens ("#...") in recalculated workbooks.
- Reports whether group labels match the allowed labels.
