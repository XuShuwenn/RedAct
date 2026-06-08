---
name: excel-lookup-volatility-validation
description: "Use this skill when building Excel-only workflows that compute rolling volatilities from price series and perform cross-sheet lookups by year and country without breaking due to formula or formatting mismatches."
---

# Excel Volatility and Lookup Validation

A reusable avoidance skill for Excel-only tasks that require:
- computing monthly log returns and rolling volatilities from a price time series
- annualizing short-window volatility
- cross-sheet lookups by year and country (including mixed text/numeric keys)
- converting reserve volumes to values using a defined price window

The guidance focuses on preventing common failure modes: formula compatibility, identifier mismatches, percentage scaling errors, and fragile references.

## When to Use

Activate this skill when:
- You must compute rolling statistics (e.g., 3-month and 12-month volatility) in Excel
- You need to lookup values by country and year across multiple sheets, where headers or year labels may be text
- You must convert quantities (volume) to values using a specific date-window average price
- The task requires Excel-only formulas with no external computation

## Core Workflow

Follow these steps to avoid the observed failure patterns:

1) Validate the source series and units
- Identify the correct gold price series and confirm units (e.g., US$ per troy ounce) and monthly frequency.
- Verify that the date column contains valid Excel dates (or consistent text dates) and the price column has numeric values. Replace non-numeric or blank entries with blanks to keep downstream formulas stable.

2) Compute monthly log returns (fraction vs percent)
- Use a forward-looking cell-by-cell pattern that leaves early rows blank when prior data is missing.
- Example pattern for row i (conceptual):
  - Log return: =IFERROR(LN(CurrentPrice/PreviousPrice), "")
- If the task requires expressing log returns as percent, choose one approach and stick to it:
  - Option A (recommended): Keep values as fractions (no ×100) and format the column as Percentage.
  - Option B: Multiply by 100 and format as Number (not Percentage). Do not multiply by 100 and also format as Percentage, which double-scales the display.

3) Rolling volatilities (3-month and 12-month)
- Use sample standard deviation of the last N monthly log returns, leaving cells blank until sufficient history exists.
- Example robust pattern for row i (conceptual ranges shown generically):
  - 3m vol: =IF(COUNT(Returns[i-2]:Returns[i])=3, STDEV.S(Returns[i-2]:Returns[i]), "")
  - 12m vol: =IF(COUNT(Returns[i-11]:Returns[i])=12, STDEV.S(Returns[i-11]:Returns[i]), "")
- If your Excel engine differs in function separators (comma vs semicolon), test a simple =SUM(1,2) (or =SUM(1;2)) in a scratch cell to confirm the expected separator, then use that consistently.

4) Latest value references for Step outputs
- To pull the latest nonblank value from a column, use a last-nonblank pattern that is widely compatible:
  - =LOOKUP(2,1/(TargetRange<>""), TargetRange)
- Avoid volatile functions when possible, and ensure the referenced ranges exclude headers and include only data rows.

5) Jan–Sep average price for a specific year
- Ensure the average strictly uses the defined window (Jan through Sep) for the target year.
- If dynamic arrays are available:
  - =AVERAGE(FILTER(PriceRange, (YEAR(DateRange)=TargetYear)*(MONTH(DateRange)<=9)))
- Broadly compatible fallback:
  - =SUMPRODUCT((YEAR(DateRange)=TargetYear)*(MONTH(DateRange)<=9)*PriceRange) / SUMPRODUCT((YEAR(DateRange)=TargetYear)*(MONTH(DateRange)<=9))
- Confirm the date column is recognized as dates (not text). If stored as text, first convert with DATEVALUE or use text-aware parsing.

6) Identify countries with target-year data and normalize headers
- When matching country names across sheets, normalize both the lookup key and headers to avoid mismatches:
  - Normalized name: =UPPER(TRIM(SUBSTITUTE(NameCell, CHAR(160), "")))
- Determine which country columns contain the target year using MATCH with exact matching:
  - Year row index: =MATCH(TargetYearKey, YearColumn, 0)
  - If the year is stored as text, ensure TargetYearKey is text (e.g., "2025"). If numeric, use a numeric key. Coerce types if needed (VALUE or TEXT).
- Check additional countries present only in the volume sheet by comparing normalized names:
  - Missing test: =COUNTIF(NormalizedValueHeaders, ThisNormalizedCountry)=0

7) Convert volume to value
- For countries present in the volume sheet but missing in the value sheet, convert using the defined price average (e.g., Jan–Sep):
  - Reserve value: =VolumeAmount * JanSepAveragePrice
- Verify unit consistency: ensure VolumeAmount and Price are in compatible units.

8) Cross-sheet lookups for total reserves and filtering
- Use INDEX+MATCH for broad compatibility:
  - =IFERROR(INDEX(TargetTable, RowIndex, MATCH(NormalizedCountry, NormalizedHeaders, 0)), "")
- If XLOOKUP is available, it can simplify logic, but keep INDEX+MATCH as the fallback.
- Remove countries from the final table when the lookup returns blank/error for the required year. If dynamic arrays are available, use FILTER to generate a clean list; otherwise, manually delete blank rows after validating they truly lack data.

9) Annualization of short-window volatility
- Annualize a short-window volatility based on its window length in months (N):
  - VolAnnualized (fraction) = VolN (fraction) * SQRT(12/N)
- If your volatility is tracked in percent, convert to fraction for math and back to percent only for display:
  - VolAnnualized (%) = (VolN%/100) * SQRT(12/N) * 100
- Confirm the window (e.g., 3 months) used for annualization aligns with the specific task instructions.

10) Final risk/exposure calculations
- When multiplying reserve values by a volatility measure, use the volatility in fraction form (not percent) unless the template explicitly expects percent arithmetic.
- Verify that the final calculation references the latest volatility you intend (e.g., short-window vs long-window) and the correct reserve values.

## Verification

Run these concrete checks before finalizing:
- Log returns:
  - The first row(s) correctly show blank due to missing prior data.
  - Random spot-check: LN(P_t / P_{t-1}) equals the displayed cell value.
- Rolling vol:
  - The 3m volatility appears only after 3 valid returns; same for 12m after 12.
  - No #VALUE!, #NAME?, or unexpected error codes remain.
- Latest references:
  - "Latest" cells pull the last nonblank entry from the intended column, not a header or blank.
- Percent vs fraction:
  - A return of ~0.01 (1%) displays as 1% if using percentage format, or 1.0 if using numbers with ×100. Confirm the chosen convention is consistent across sheets.
- Year matching:
  - MATCH on the target year returns a valid row index. If year cells are text, your key is text. If numeric, your key is numeric.
- Country matching:
  - Normalized country names match across sheets. Trimmed, upper-cased names without non-breaking spaces resolve correctly.
- Volume-to-value conversion:
  - The Jan–Sep average price is computed using only Jan–Sep of the target year. Check the month filters and row count (exactly nine months).
- Total reserves lookup:
  - Countries without target-year reserves are blanked by IFERROR and removed from the final table.
- Final outputs:
  - No formula errors are present; units are consistent; magnitudes look reasonable.

## Common Pitfalls and How to Avoid Them

- Formula separators and compatibility:
  - Symptom: #NAME? or wrong parsing after recalculation.
  - Fix: Test a simple formula to confirm your engine’s separator (comma or semicolon). Use broadly supported functions (INDEX+MATCH, STDEV.S) instead of newer ones if compatibility is uncertain.

- Saving formulas as text:
  - Symptom: Formulas display as plain text and never evaluate.
  - Fix: Ensure the leading "=" is present and the cell is not formatted as Text. Re-enter formulas in General/Number format if needed.

- Text vs numeric year keys:
  - Symptom: MATCH fails to find the target year.
  - Fix: Coerce types explicitly with VALUE or TEXT so the lookup key matches the column type.

- Country header mismatches:
  - Symptom: Lookups return blanks due to subtle whitespace or case differences.
  - Fix: Normalize names with TRIM, UPPER, and SUBSTITUTE(CHAR(160), "") in both the lookup key and the header range.

- Double-scaling percentages:
  - Symptom: Volatility values display 100x larger than expected.
  - Fix: Either keep values as fractions and use Percentage formatting, or multiply by 100 and use Number formatting. Never do both.

- Rolling windows including blanks:
  - Symptom: STDEV.S returns errors or incorrect values.
  - Fix: Guard with COUNT checks and only compute volatility when the full window contains valid numeric entries.

- Incorrect annualization window:
  - Symptom: Annualized value does not align with the intended window.
  - Fix: Use SQRT(12/N) where N is the number of months in your volatility window, and verify N matches the instruction.

- Unit mismatches in value conversion:
  - Symptom: Converted reserve values are off by large factors.
  - Fix: Confirm that the price and volume units are compatible and apply any needed scaling.

## Success Criteria

- The price sheet contains correct log returns and rolling volatilities, with blanks where insufficient history exists.
- Latest values are correctly pulled into the answer area from the relevant columns.
- Countries with target-year value data are listed; additional volume-only countries are converted using the defined price window.
- Total reserves lookups return values for the target year; countries lacking data are removed from the final table.
- Annualization and exposure calculations use fraction-based volatility for arithmetic and consistent display conventions.
- The workbook recalculates with zero formula errors and consistent units.

## Optional Script Usage

No external scripts are required for this skill. All computations and lookups should be performed with Excel formulas and validations within the workbook.
