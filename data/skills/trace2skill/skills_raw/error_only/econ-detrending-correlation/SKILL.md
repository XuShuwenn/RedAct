---
name: econ-detrending-correlation
description: "Apply Hodrick-Prescott filter to detrend economic time series and calculate Pearson correlation between consumption and investment."
---

# Economic Time Series Detrending and Correlation

## When to Use

- Detrend economic time series using HP filter
- Calculate correlation between detrended economic indicators
- Deflate nominal series using CPI to get real values

## Input Files

- `/root/ERP-2025-table10.xls`: Personal Consumption Expenditures (Nominal)
- `/root/ERP-2025-table12.xls`: Private Fixed Investment (Nominal)
- `/root/CPI.xlsx`: Consumer Price Index (for deflation)

## Key Steps

1. Inspect each input workbook first: print sheet names, column labels, and a few representative rows before coding against assumed headers or row formats
2. Extract Personal Consumption Expenditures (Total, column 1) and PFI (Total, column 1) from their ERP tables separately
3. Build independent year→value mappings for each series, then merge by year; do not assume matching row numbers across the two files
4. Handle quarterly data at end of tables; for 2024, statefully track the active year, enumerate all matched 2024 quarter rows, and compute the annual 2024 value as the mean of all available 2024 quarters
5. Validate extraction results before proceeding: ensure annual observations are non-empty, years are in expected order, and 2024 handling did not accidentally pull quarters from earlier years or remove the series
6. Deflate nominal series using CPI to get real values only after confirming the actual CPI year/value columns in `/root/CPI.xlsx`
7. Apply Hodrick-Prescott filter with λ=100 to ln(real series)
8. Compute Pearson correlation between two cyclical components
9. Round result to 5 decimal places
10. Before concluding, explicitly print the extracted 2024 quarter labels/values, the final correlation, and read back `/root/answer.txt` to confirm the saved value matches the computed value

## HP Filter

- Use natural log of real series before filtering
- λ = 100 for annual data
- Cyclical component = series - trend component


## Validation Checks

## Validation Checks

- Before computing correlation, inspect the extracted year/value pairs for both series, especially the first/last years and 2024.
- Verify that the selected rows/columns correspond to the intended ERP series: Personal Consumption Expenditures (Total, column 1) and Private Fixed Investment (Total, column 1).
- Confirm that 2024 annual values are computed from all available quarterly observations shown in the source tables, not from a guessed or truncated subset.
- Do not finalize after only checking `/root/answer.txt`; validate the upstream extraction and annualization logic first.
## Output Format

Single number to `/root/answer.txt`


Before trusting `/root/answer.txt`, verify the computation ran end-to-end: confirm deflation, HP filtering, and correlation steps executed successfully and the script exited normally. If output is truncated or diagnostics stop early, rerun or inspect the error instead of treating an existing answer file as success.

## Tips

- pandas for Excel reading
- scipy.signal for HP filter or implement manually
- Handle missing/partial 2024 data carefully


- ERP table layouts may differ between PCE and PFI; extract each sheet independently and align only on the year field
- DO NOT assume CPI headers such as `Year` or a specific CPI value column; inspect the actual schema in `/root/CPI.xlsx`
- Parse quarter rows statefully using the active year context; do not match `I./II./III./IV.` labels globally across the table
- DO NOT use brittle year tests, hard-coded quarter values, or string heuristics to exclude quarterly rows; inspect raw labels and distinguish annual vs quarterly entries from the workbook's actual formatting
- For the 2024 special case, verify every captured quarter row and confirm the annual 2024 value equals the average of the available quarters actually used in computation
- After extraction, sanity-check that both annual series contain many years before deflation/filtering; if a series is empty, very short, or the overlapping sample span changes unexpectedly, fix parsing before continuing
- Sanity-check that consumption years, investment years, and CPI years align exactly before applying logs and the HP filter
- If tool output is truncated, rerun with concise targeted prints or redirect to a log file; do not report an unverified number
- Keep final reasoning consistent with the observed successful run output
- See [Quarterly Boundary Checks](references/quarterly-boundary-checks.md) for a concise latest-year extraction checklist
