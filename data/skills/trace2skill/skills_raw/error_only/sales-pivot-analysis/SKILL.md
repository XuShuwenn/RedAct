---
name: sales-pivot-analysis
description: "Create Excel pivot tables from population and income data for demographic analysis across states and regions."
---

# Sales/Population Pivot Analysis

## When to Use

- Create pivot tables from demographic data
- Analyze population by state and region
- Calculate income quartiles and earnings summaries

## Input Files

- `/root/population.pdf`: Population data
- `/root/income.xlsx`: Income data

**Before writing transformation code, inspect both inputs and record the actual schema** (column names, sample rows, join keys, and row counts). Do not assume PDF-extracted columns match the requested output field names.


- Use these exact absolute paths when reading inputs; do not substitute relative paths.
- Keep outputs in the specified destination path; avoid ad hoc intermediates in other directories unless the task explicitly allows them.


## Output

`/root/demographic_analysis.xlsx` with 5 sheets:

**Required source fields before building summaries:** `STATE`, `SA2_CODE`, `SA2_NAME`, `POPULATION_2023`, `EARNERS`, `MEDIAN_INCOME` (plus any other original fields carried into `SourceData`). If a required field is missing, fix the extraction/merge first.

### 1. "Population by State"
- Rows: STATE
- Values: Sum of POPULATION_2023

### 2. "Earners by State"
- Rows: STATE
- Values: Sum of EARNERS

### 3. "Regions by State"
- Rows: STATE
- Values: Count of SA2 regions

### 4. "State Income Quartile"
- Rows: STATE
- Columns: Q1, Q2, Q3, Q4 (based on MEDIAN_INCOME)
- Values: Sum of EARNERS

### 5. "SourceData"
- Original data enriched with:
  - Quarter (Q1-Q4 based on MEDIAN_INCOME)
  - Total = EARNERS × MEDIAN_INCOME


### Compliance requirements
- If the task says **pivot tables**, create actual Excel pivot tables in the workbook; do **not** substitute pandas `groupby` outputs or `pd.pivot_table` exports unless the task explicitly allows static summaries.
- Match the requested workbook structure exactly: sheet names, row fields, column fields, value fields, and labels must use the task wording verbatim.
- For "Population by State", the value must be **Sum of `POPULATION_2023`**. Do **not** replace it with a count of regions/rows/SA2s because population was lost during preprocessing.

### SourceData preservation rule
- `SourceData` must preserve the original merged data and original source columns used for analysis; then append derived columns such as `Quarter` and `Total`.
- Keep all original income rows in `SourceData`; enrich them with new columns rather than deleting records.
- If `MEDIAN_INCOME` or `EARNERS` is invalid, coerce to blank/NaN for calculations, but preserve the original row in `SourceData`.
- Only exclude invalid rows from specific derived computations when necessary; do not shrink the underlying source dataset.



## Verification Before Completion

## Verification Before Completion

Before declaring the task done, reopen `/root/demographic_analysis.xlsx` and verify all of the following:
- Workbook contains exactly these sheets: `Population by State`, `Earners by State`, `Regions by State`, `State Income Quartile`, `SourceData`
- `SourceData` retains the original source rows/columns needed for analysis and includes the derived columns `Quarter` and `Total`
- `Quarter` values are labeled `Q1`-`Q4` based on `MEDIAN_INCOME`
- `Total` is calculated as `EARNERS × MEDIAN_INCOME` where both inputs are valid
- Each summary sheet matches the requested Rows / Columns / Values layout from the `## Output` section and contains readable headers plus non-empty results
- `Population by State` uses sum of `POPULATION_2023`, not a fallback count metric
- Do not treat a successful script run, file creation, workbook reload alone, or pivot metadata as proof the workbook is correct; inspect the produced sheet contents themselves

## Tips

- openpyxl for Excel creation
- Use pandas for data processing
- Create pivot tables with proper structure
- Handle quartile calculations correctly


- Inspect the PDF extraction result and Excel sheet headers first; confirm the real column names before building merges or summaries.
- Validate extraction and merge quality before building summaries: confirm expected headers, row counts, join keys, and unmatched records after joining PDF and Excel data.
- When extracting population data from `/root/population.pdf`, validate key grouping fields before aggregation. If `STATE` values look truncated or inconsistent (for example `New South W`), fix the extraction/cleaning before creating any state-based output.
- Before computing summaries keyed by `STATE`, check that state names are complete and standardized so identical states are not split into separate groups.
- Before creating summaries, verify the merged dataset still contains every field needed by the workbook spec, especially `POPULATION_2023` for the population sheet.
- Build `Quarter` from `MEDIAN_INCOME`, then build `Total = EARNERS × MEDIAN_INCOME`.
- Treat `pandas.pivot_table` as a data-prep helper only; it does not create an Excel pivot-table object.
- Avoid fragile low-level openpyxl pivot internals such as `TableDefinition`, `CacheDefinition`, `openpyxl.pivot.*`, or `ws._pivots` unless you can verify the saved workbook still works correctly after reload.
- Prefer workbook outputs you can verify after save/reload; do not treat file existence, sheet names alone, or in-memory pivot metadata as proof of success.
- Do **not** drop rows just to make quartile or total calculations succeed; preserve rows and leave derived fields blank where inputs are invalid.
- After any runtime fix or data-cleaning change, regenerate the workbook and repeat the full verification checklist before finishing.
