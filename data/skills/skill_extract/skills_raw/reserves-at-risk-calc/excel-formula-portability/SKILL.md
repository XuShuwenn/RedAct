---
name: excel-formula-portability
description: "Build and verify Excel formulas that are portable across Excel/LibreOffice, align to template labels (not guessed rows), handle percent/units correctly, and validate recalculation for financial models."
---

# Excel Formula Portability and Template Alignment

Use this skill when automating spreadsheets that must be computed by Excel or LibreOffice (e.g., via a headless recalc engine), especially with pre-existing templates. It focuses on: cross-engine-safe formulas, robust row/column alignment via labels (not guessed indices), unit and percent handling, cross-sheet lookups, and post-write validation.

## When to Use

- You must populate a template workbook with data and formulas (e.g., prices, returns, volatilities, exposures) and rely on the workbook to do the math.
- The workbook will be recalculated outside native Excel (e.g., LibreOffice, headless recalc), so portability matters.
- The target sheet uses human-readable labels (e.g., "Country", "Gold reserves", "Total Reserve") rather than fixed coordinates.

## Core Workflow

1) Inspect and map the template structure
- Read all sheet names and scan the first column(s) of the summary/Answer sheet to locate labels such as:
  - Country
  - Gold reserves (or similar wording)
  - Volatility / Exposure / Total Reserve / RaR
- Derive row and column targets from labels instead of hardcoding row numbers. Keep a label→cell map and use it for all write operations.

2) Insert data, then formulas (Excel computes; scripts don’t)
- Write source series (e.g., dates and prices) into the data sheet.
- Add Excel formulas for derived metrics rather than pre-computing in Python: the requirement is “use Excel for computation.”
- Quote sheet names that contain spaces with single quotes (e.g., 'Gold price'!B2).

3) Use engine-portable formulas
- Prefer legacy names widely supported by Excel and LibreOffice:
  - Use STDEV over STDEV.S/STDEV.P for portability.
  - Use NORMSINV over NORM.S.INV for portability.
  - LN, SQRT, MATCH, INDEX, LOOKUP, IFERROR are safe across engines.
- Rolling-window example (row r, using percentage log returns in column C):
  - 3-period volatility in D_r: =STDEV(C{r-2}:C{r})
  - 12-period volatility in E_r: =STDEV(C{r-11}:C{r})
- Monthly log return in C_r: =LN(B{r}/B{r-1})*100

4) Reference the latest value robustly (avoid hard-coded last row)
- Use a last-non-empty lookup pattern:
  - =LOOKUP(2,1/('Gold price'!D:D<>""),'Gold price'!D:D)
- This works in both Excel and LibreOffice.

5) Handle percentages vs decimals explicitly
- If you compute returns×100 (percent points), then any product requiring a decimal must divide by 100.
- Example exposure using volatility as percent and a Z-score cell:
  - =ValueCell*($C$Vol/100)*$C$Z

6) Normalize and match entity names across sheets
- Column headers often contain extra descriptors (e.g., ": Gold (EOP, NSA, Mil.US$)"). Extract the country/entity using the substring before ':' and trim whitespace.
- Normalize common variants (e.g., "Intl" → "International", multiple spaces → single space). Compare case-insensitively.
- Use header-based MATCH when pulling corresponding values:
  - =INDEX('Total Reserves'!$TargetRow:$TargetRow, MATCH("*"&ThisCountry&"*", 'Total Reserves'!$1:$1, 0))
- Wrap with IFERROR to avoid #N/A.

7) Guard formulas against missing data
- Prevent #DIV/0! and #N/A from polluting the model:
  - Division: =IFERROR(Numerator/Denominator, "")
  - Lookup: =IFERROR(INDEX(...,MATCH(...)), "")
- Write columns for Step 3 only for entities with the required data present (skip instead of writing and then deleting).

8) Unit consistency before valuation
- Confirm units for each series (e.g., Volume in million vs thousand troy ounces; Value and Total Reserves in millions of USD) and convert Volume to Value accordingly in-cell formulas before use in exposures.
- If units vary by country, add a per-country scale factor (e.g., thousand → million = 0.001) in a helper column or directly in formulas.

9) Recalc and verify
- Run a headless recalc (LibreOffice/Calc or your environment’s recalc tool).
- If #NAME? appears in volatility or Z-score cells:
  - Replace STDEV.S → STDEV
  - Replace NORM.S.INV → NORMSINV
- Read the computed workbook (data_only) to verify key outputs are non-zero and numerically plausible.

## Verification

Perform these checks before finalizing:
- Label alignment: The cells you wrote align with the intended labels by reading back the label→cell map and the adjacent data in the output file.
- Formula presence: Key cells contain formulas (start with "=") and not hard-coded numbers (except where the template explicitly requires a value).
- Engine compatibility: No #NAME? errors after recalc. If present, replace function names with portable alternatives.
- Unit conversions: Spot-check at least one conversion path (e.g., a country using thousands vs millions) to ensure Value is consistent with Total Reserves units.
- Percent-to-decimal: Exposure magnitudes are in realistic ranges (exposure should be a fraction of the base value, not multiples bigger due to missing /100).
- Lookup validity: Cross-sheet lookups return numbers; guard with IFERROR where missing.

## Common Pitfalls (and Avoidance)

- Off-by-one rows: Do not assume row numbers. Detect target rows by label text in the Answer sheet, then write relative to those rows.
- Non-portable functions: STDEV.S and NORM.S.INV may cause #NAME? in some engines. Use STDEV and NORMSINV.
- Wrong exposure scale: If returns are in percent points, divide by 100 when multiplying by values.
- Duplicated entities from headers: Headings vary (e.g., “Intl” vs “International”). Normalize names and match case-insensitively to avoid duplicate columns.
- Brittle hard-coded last rows: Use LOOKUP(2,1/(range<>""),range) to reference the latest computed value.
- Range vs. individual arguments in STDEV: Use contiguous ranges (Cstart:Cend), not comma-separated individual cells.
- Unquoted sheet names: Always quote sheet names with spaces using single quotes (e.g., 'Gold price').
- Reading computed values too early: After adding formulas, recalc before reading with data_only; otherwise, values may appear as zeros or stale.

## Optional Script Usage

You can use the helper script to generate portable formula strings and normalize entity names. It does not compute results; it prints or returns formula text and normalization helpers you can embed in your writer.

Example (conceptual usage):
- Normalize a header to a canonical entity: normalize_country("Czechia Intl Reserves: Gold Volume (...)") → "Czechia International Reserves"
- Build rolling volatility formula for row r: rolling_stdev_formula(col="C", row=r, window=3)
- Build latest-value reference from a sheet/col: last_value_formula(sheet="Gold price", col="D")
- Build exposure formula with percent volatility and Z: exposure_formula(val_cell="C12", vol_cell="$C$4", z_cell="$C$3", vol_as_pct=True)
- Build INDEX/MATCH by header label for a target row: index_match_by_header(sheet="Total Reserves", target_row=SomeRow, header_match_cell="C20")
