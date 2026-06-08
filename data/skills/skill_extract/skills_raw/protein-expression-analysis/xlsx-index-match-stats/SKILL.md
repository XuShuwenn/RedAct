---
name: xlsx-index-match-stats
description: "Populate Excel/LibreOffice grids via two‑way INDEX–MATCH lookups and compute group means, standard deviations, and fold change with robust, cross‑engine formulas."
---

# Two‑Way Lookup and Group Stats in Spreadsheets

Reusable workflow for filling a 2D block in a spreadsheet using two keys (row ID and column header), then computing per‑group means, standard deviations, and fold change (log2 FC and FC). Designed for Excel and LibreOffice compatibility.

## When to Use

Activate this skill when you need to:
- Pull values into a rectangular grid by matching an ID (e.g., Protein_ID) and a column header (e.g., Sample name)
- Compute group statistics (means and standard deviations) from contiguous column blocks (e.g., Control vs Treated)
- Derive log2 fold change and fold change from group means
- Keep spreadsheets dynamic (formulas only) while preserving file formatting

## Core Workflow

1. Inspect and map the layout
   - Identify:
     - Row ID column on the Task/target sheet (e.g., A11:A20)
     - Column headers on the Task/target sheet (one header row, e.g., row 10)
     - Target output block for expression values (e.g., C11:L20)
     - Stats area (four rows for means/stdevs across columns per protein)
     - Fold change area (per‑protein rows with Log2 FC and FC)
   - Identify data sheet structure:
     - Data sheet’s ID column (e.g., column A)
     - Data sheet’s header row for sample names (e.g., row 1)
     - Range of data columns to include in lookups (use a sufficiently wide absolute range)

2. Fill the expression block with two‑way lookups
   - Use INDEX–MATCH with absolute references to match both:
     - Row position by ID: MATCH($A{row}, Data!$A:$A, 0)
     - Column position by header: MATCH({Col}$HeaderRow, Data!$1:$1, 0)
   - Recommended template for each cell in the expression grid:
     - =IFERROR(INDEX(Data!$A:$BZ, MATCH($A{r}, Data!$A:$A, 0), MATCH({X}$10, Data!$1:$1, 0)), "")
     - Replace {r} with the target row index and {X} with the column letter. Adjust $BZ and header row as needed.
   - Notes:
     - Always include the sheet name with an exclamation mark (e.g., Data!).
     - Use IFERROR(…, "") to avoid noisy #N/A values when IDs or headers don’t match.

3. Compute group statistics on contiguous column ranges
   - If groups are contiguous by columns (e.g., Control = C:G and Treated = H:L):
     - Control Mean (per protein row R): =AVERAGE(CR:GR)
     - Control StDev (Excel/LibreOffice compatible): =STDEV(CR:GR)
     - Treated Mean (per protein row R): =AVERAGE(HR:LR)
     - Treated StDev (Excel/LibreOffice compatible): =STDEV(HR:LR)
   - Optional safety for small sample counts to avoid #DIV/0!:
     - =IF(COUNT(CR:GR)>1, STDEV(CR:GR), "") and similarly for the treated range.
   - Place these formulas across columns (one column per protein) and ensure the protein‑row mapping is correct (see Verification).

4. Calculate fold change metrics
   - Log2 FC (per protein column): =Treated_Mean − Control_Mean
   - Fold Change (FC): =POWER(2, Log2_FC)  (POWER works reliably across engines)

5. Recalculate and verify
   - Recalculate formulas (open the file in Excel/LibreOffice or use a compatible recalc utility).
   - Spot‑check a few cells to confirm lookups and stats are correct.
   - Ensure no #NAME?, #VALUE!, or #DIV/0! errors remain.

## Verification

- Two‑way lookup checks
  - Pick a known ID and header; manually confirm that the value in the expression block matches the data sheet via ID row and header column intersection.
  - Confirm sheet references include the exclamation mark and that absolute ranges cover all relevant columns.
- Mapping checks (common off‑by‑one)
  - If the stats table uses columns B..K for 10 proteins and your expression rows are R1..R10 (e.g., 11..20), verify mapping:
    - Column index j (0‑based) → stats column = B + j; protein row = R1 + j.
- Group range checks
  - Confirm Control and Treated column spans align with the intended columns (e.g., Control = C:G, Treated = H:L).
- Error scan
  - Ensure functions are recognized (no #NAME?). If running in LibreOffice, prefer STDEV over STDEV.S.
  - Ensure standard deviations don’t produce #DIV/0!; optionally wrap STDEV with a COUNT check.

## Common Pitfalls and How to Avoid Them

- Missing sheet delimiter
  - Pitfall: Using Data.$A:$A instead of Data!$A:$A causes lookups to fail.
  - Fix: Always use the exclamation mark (Data!$… ).
- Range too narrow
  - Pitfall: Limiting INDEX to a small column span may exclude valid columns.
  - Fix: Use a wide but realistic max column (e.g., $A:$BZ) matching your data width.
- Engine incompatibilities
  - Pitfall: Using functions not supported in LibreOffice (e.g., FILTER, STDEV.S in older locales).
  - Fix: Avoid dynamic arrays; use AVERAGE and STDEV with simple ranges. Prefer STDEV (legacy) for broader compatibility, or detect the engine and adjust.
- Locale separators
  - Pitfall: Some locales require semicolons (;) instead of commas (,).
  - Fix: Prefer commas in stored formulas; let the spreadsheet engine normalize. If your environment mandates semicolons, apply them consistently.
- Off‑by‑one mapping
  - Pitfall: Misaligning stats columns to protein rows (e.g., starting at the wrong row).
  - Fix: Define a clear mapping rule (e.g., protein_row = first_expression_row + column_offset) and verify two examples.
- Unhandled missing data
  - Pitfall: STDEV yields #DIV/0! for fewer than 2 numeric values.
  - Fix: Wrap with IF(COUNT(range)>1, STDEV(range), ""). AVERAGE naturally ignores blanks.

## Success Criteria

- Expression block filled entirely via formulas, not hard‑coded numbers
- Group means and standard deviations computed for each protein without errors
- Log2 FC and FC computed for each protein row
- No #NAME?, #VALUE!, or #DIV/0! in the output areas
- Workbook formatting and colors preserved; no macros introduced

## Optional Script Usage

You can use the helper to generate and/or apply robust formulas programmatically. It is parameterized and generic, avoiding any task‑specific constants.

Example (dry‑run to print formulas):
- python scripts/apply_index_match_stats.py --print-only \
  --workbook your.xlsx --task-sheet Task --data-sheet Data \
  --expr-top-left C11 --expr-bottom-right L20 \
  --id-col A --header-row 10 --data-id-col A --data-header-row 1 --data-last-col BZ \
  --control-cols C:G --treated-cols H:L \
  --stats-start-col B --stats-end-col K \
  --stats-row-mean-control 24 --stats-row-stdev-control 25 \
  --stats-row-mean-treated 26 --stats-row-stdev-treated 27 \
  --fc-start-row 32 --fc-end-row 41

Remove --print-only to write formulas into the workbook.
