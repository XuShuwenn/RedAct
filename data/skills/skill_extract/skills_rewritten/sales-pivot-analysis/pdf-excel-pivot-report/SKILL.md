---
name: pdf-excel-pivot-report
description: "Create Excel reports with pivot-style summaries by extracting tables from PDFs, merging with spreadsheets, cleaning types, adding derived quartiles, and verifying outputs."
---

# PDF + Excel to Pivot Report

Build a multi-sheet Excel report by extracting tabular data from a PDF, merging it with a spreadsheet, enriching with derived fields (income quartiles and totals), and generating four summary sheets plus a SourceData sheet.

This workflow generalizes to any task that requires: parsing tabular PDF data, joining with an Excel dataset, normalizing types and keys, computing quartile labels, and producing pivot-style summaries.

## When to Use

Use this skill when you need to:
- Extract table-like data from PDFs and merge it with spreadsheet data
- Normalize mixed data types (e.g., numbers with commas, currency symbols)
- Join on a shared region/key column with inconsistent formatting
- Compute quartile-based groupings (Q1–Q4) across all rows
- Produce an Excel workbook with a SourceData sheet and multiple pivot summary sheets

## Core Workflow

1) Inspect Inputs and Plan
- Confirm both input files exist and are readable.
- Preview the spreadsheet: sheet names, column names, and a few rows.
- Preview the PDF: number of pages and whether the tables are consistently structured across pages.
- Identify the join key present in both sources (e.g., a region code) and the fields needed for summaries (e.g., state, population, earners, median income).

2) Extract PDF Tables Robustly
- Use a table extraction library suited to your environment (e.g., pdfplumber, camelot, or tabula).
- Parse all relevant pages and concatenate into one table.
- Normalize headers: trim whitespace, uppercase/lowercase consistently, replace spaces with underscores, and unify synonymous column names.
- Remove repeated header rows, blank lines, and footers.
- Validate expected columns exist after normalization.

3) Load Spreadsheet Data
- Read the relevant sheet(s) from the Excel file.
- Normalize column names in the same manner as the PDF data.
- Identify and coerce numeric fields that may be loaded as strings.

4) Normalize Join Keys Before Merging
- Trim whitespace, set a consistent case, and standardize formatting.
- For code-like keys, preserve or restore leading zeros (zero-pad to the expected width if necessary).
- Ensure the join key in both datasets is the same type (string recommended).
- Check key cardinality and uniqueness in each dataset (no unintended duplicates).

5) Merge and Validate
- Merge on the normalized join key. Choose inner or left joins based on the spec; for summary reports, inner join is common to keep only matched records.
- Measure match quality: count matched/unmatched keys; investigate any high mismatch rates.
- Spot-check a few rows to confirm fields align logically after merge.

6) Derive Fields
- Quarter (Q1–Q4): compute based on quartiles of the income measure across all rows.
  - Use quantile-based binning; handle tied values and non-unique quantile edges with a deterministic fallback (e.g., rank-based binning) to ensure you always produce four labels.
- Total: compute as EARNERS × MEDIAN_INCOME (or as specified). Ensure both components are numeric.

7) Build the Excel Report (5 sheets)
- SourceData: write the full merged table including the derived Quarter and Total columns.
- Population by State: summarize sum of the population field by state.
- Earners by State: summarize sum of earners by state.
- Regions by State: summarize count of regions by state (count rows or distinct region IDs as required).
- State Income Quartile: summarize sum of earners by state × quarter (rows = state, columns = Q1–Q4).

Implementation options for summaries:
- True pivot tables: if your Excel writer supports pivot tables (e.g., xlsxwriter), create real pivot tables that refresh in Excel.
- Aggregated tables: use pandas groupby/pivot_table to compute summaries and write them as normal tables. This is widely supported and deterministic.

8) Save and Verify
- Save the workbook and verify the file exists and opens.
- Re-open the workbook programmatically (if possible) to verify sheet names, presence of expected columns, and non-empty summaries.

## Verification

Perform these checks before finalizing:
- Input parsing
  - PDF rows parsed > 0, headers align with expectations.
  - Spreadsheet read successfully; columns present for join and summary fields.
- Key normalization and merge
  - Join key types match and are normalized (trimmed, consistent case, leading zeros as needed).
  - Unmatched keys are few or understood; record counts post-merge are sensible.
- Derived fields
  - Quarter labels include Q1, Q2, Q3, Q4 (all present unless data is extremely skewed; if not, confirm fallback was applied).
  - Total column is numeric and has no unexpected nulls.
- Summaries
  - Sheet names exactly match the specification.
  - Aggregations are non-empty and consistent (e.g., sum across states equals the total from SourceData for that measure).
  - For the cross-tab (state × quarter), row totals match the sum of Q1–Q4 per state.
- Output integrity
  - File path is correct.
  - Workbook has five sheets with clear headers; SourceData includes all required fields.

## Common Pitfalls and How to Avoid Them

- Misparsed PDF tables:
  - Symptom: shifted columns, repeated headers as data, or missing fields.
  - Fix: explicitly skip header rows on each page, normalize headers, and validate required columns exist before proceeding.

- Mixed numeric types (strings with commas or currency symbols):
  - Symptom: arithmetic or grouping fails; NaNs introduced after conversion.
  - Fix: strip non-numeric characters, handle parentheses as negatives, convert safely to numeric, and confirm null counts after conversion.

- Join key mismatches (whitespace, case, leading zeros, differing types):
  - Symptom: unexpectedly low match rates or duplicate matches.
  - Fix: standardize both sides (trim, case, zero-pad), cast to string, check uniqueness, and review sample unmatched keys.

- Quartile binning edge cases:
  - Symptom: fewer than 4 bins due to tied values; some quartiles missing.
  - Fix: implement a fallback rank-based binning that always yields Q1–Q4 deterministically.

- Wrong aggregation type for region counts:
  - Symptom: inflated counts due to duplicates.
  - Fix: count distinct region IDs if duplicates exist, or de-duplicate before counting.

- Incorrect sheet names/order or incomplete workbook:
  - Symptom: downstream checks fail or users can’t find expected sheets.
  - Fix: adhere to exact sheet names and include all five sheets; verify programmatically before finalizing.

- Relying on unsupported pivot creation:
  - Symptom: no pivot appears when opened in Excel.
  - Fix: if true Excel pivots aren’t supported in your environment, produce deterministic aggregated tables with the same layout and naming.

## Success Criteria

- Output Excel file exists at the requested path.
- Five sheets are present with exact names: SourceData, Population by State, Earners by State, Regions by State, State Income Quartile.
- SourceData contains all original fields plus Quarter (Q1–Q4) and Total.
- Summaries reflect the specified aggregations and reconcile with SourceData totals.
- Data types are normalized; key fields are non-null; merge logic is validated.

## Optional Script Usage

The helper script provides reusable utilities to coerce numeric columns, normalize join keys, assign robust quartile labels, and write a report with aggregated summary sheets. Import and use it in your pipeline after you’ve prepared a merged DataFrame named `df` with at least these columns (rename as needed in your code):
- state_col (e.g., "STATE")
- region_col (unique region identifier)
- population_col (e.g., latest population)
- earners_col (number of earners)
- income_col (income for quartiles, e.g., median income)

Example (Python):
- Coerce numerics, normalize keys, assign quartiles, compute totals, and write report with aggregated summaries.

```python
from scripts.pivot_tools import (
    coerce_numeric, normalize_key, assign_quartiles,
    write_aggregated_report
)

# Assume df is your merged DataFrame
for col in ["EARNERS", "MEDIAN_INCOME", "POPULATION_2023"]:
    df[col] = coerce_numeric(df[col])

# Normalize join key (if needed) and state
df["REGION_ID"] = normalize_key(df["REGION_ID"], zero_pad=None)

df["Quarter"] = assign_quartiles(df["MEDIAN_INCOME"], labels=("Q1","Q2","Q3","Q4"))
df["Total"] = df["EARNERS"] * df["MEDIAN_INCOME"]

write_aggregated_report(
    df=df,
    output_path="demographic_analysis.xlsx",
    state_col="STATE",
    region_col="REGION_ID",
    population_col="POPULATION_2023",
    earners_col="EARNERS",
    quarter_col="Quarter"
)
```

If you need true Excel pivot tables and your environment supports them (xlsxwriter), adapt the script to `write_excel_with_pivots` using the same columns; otherwise the aggregated report will meet most validation needs.
