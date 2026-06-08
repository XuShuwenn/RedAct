---
name: sec-13f-quarterly-analysis
description: "Search cover pages to locate filings, extract fund AUM and equity holdings, compare holdings across quarters, and rank top managers in a target security using SEC 13F datasets."
---

# SEC 13F Quarterly Analysis

Reusable workflow for analyzing SEC Form 13F data across quarters: find accession numbers via fuzzy cover page search, extract fund metrics (AUM and number of equity holdings), compare quarter-to-quarter holdings for a fund, and rank top fund managers invested in a target CUSIP for a given quarter.

## When to Use

Activate this skill when the user asks to:
- find a fund’s quarter filing by name and retrieve AUM from the summary
- count how many stocks (equity positions) a fund holds
- compare holdings across two quarters for the same fund and identify top increases
- rank fund managers invested in a specific security (by CUSIP) in a given quarter

## Core Workflow

Phase 1 — Identify Filings (Accession Numbers)
- Inspect the quarter directory to confirm available files (e.g., COVERPAGE, SUMMARY, HOLDINGS tables, and metadata).
- Fuzzy-search the quarter’s cover page file for the fund name to get the best-matching filing row and accession_number.
- If multiple close matches exist (e.g., similarly named affiliates), prefer the main 13F-HR filing for the intended manager entity.

Phase 2 — Extract Fund Metrics (AUM and Equity Holdings Count)
- From the summary table for the identified accession_number, read the total reported portfolio value (AUM). Confirm the value column name from headers (e.g., table_value_total/tablevaluetotal).
- From the holdings detail table for the accession_number, count unique equity CUSIPs:
  - Include only equity positions; exclude derivative rows (e.g., put/call options) and non-equity instruments (notes, warrants) based on available columns (titleOfClass/class and putCall flags).
  - Deduplicate by CUSIP to count unique stocks.

Phase 3 — Compare Holdings Across Quarters (Top Increases)
- Identify accession numbers for the same fund in both quarters (repeat Phase 1 per quarter).
- Aggregate holdings value by CUSIP for each accession_number independently.
- Join the two CUSIP-value maps, compute delta = value_q3 − value_q2 (treat missing as zero), sort by descending delta, and select the top N identifiers.

Phase 4 — Rank Top Managers in a Target Security (CUSIP)
- Find the target security’s CUSIP by issuer name if needed (search issuer/security name table or holdings text fields).
- In the quarter’s holdings table, filter rows for that CUSIP and aggregate value by accession_number.
- Rank descending by position value and map accession_numbers to manager names using the quarter’s cover page.
- Return the top K manager names.

Phase 5 — Output and Validation
- Write the required JSON output in the specified schema for the user’s task.
- Validate JSON explicitly (parse/read-back) before finalizing.

## Data and Columns: Practical Notes

- Cover page fields typically include: accession_number (or a synonym), manager name, CIK, form_type. Normalize headers to lowercase and handle synonyms.
- Summary fields often include portfolio totals: tablevaluetotal/table_value_total and tableentrytotal; use the value total for AUM, not the entry count.
- Holdings detail fields vary but commonly include: accession_number, cusip, value (market value), shares/sshprnamt, titleOfClass/class, putCall. Normalize headers and detect these robustly.
- Market value units: Some datasets report value in thousands. Verify units from metadata and be consistent across calculations. If summary totals and aggregated holdings differ by a constant factor (e.g., ×1000), adjust your holdings aggregation or presentation accordingly.

## Verification

- Filing Match Quality:
  - Score the fuzzy match; if multiple candidates are close, cross-check with form_type and manager name normalization (remove punctuation/case).
  - Resolve any ambiguity by inspecting secondary fields (e.g., manager address, CIK) when available.

- AUM Consistency:
  - Cross-check the summary table’s total value against the sum of holdings values for that accession.
  - Confirm units by reading metadata and ensure consistent unit handling across all computations.

- Equity Holdings Count:
  - Verify the count is the number of unique equity CUSIPs.
  - Confirm exclusion rules: no PUT/CALL option rows, exclude non-equity instruments; validate your filter on sample rows.

- Quarter-to-Quarter Comparison:
  - Confirm both accession_numbers refer to the same manager entity.
  - Ensure numeric sorting (convert strings to numbers) and handle missing CUSIPs as zero in one quarter.

- Top Holders for a CUSIP:
  - Verify the CUSIP mapping is correct (issuer and CUSIP agree) before aggregation.
  - Map accession_numbers to manager names from the same quarter’s cover page and spot-check a few mappings.

## Common Pitfalls and How to Avoid Them

- Choosing the wrong filing: Fuzzy matching to an affiliate or amendment can mislead results. Prefer the main 13F-HR for the intended manager and confirm with form_type.
- Misinterpreting holdings counts: Do not use tableentrytotal as the stock count; count unique equity CUSIPs after filtering.
- Ignoring quarter directory in paths: Always parameterize paths by quarter; do not rely on a fixed default location.
- Unit mismatches: Confirm whether value columns are in dollars or thousands; adjust aggregates and comparisons consistently.
- String sorting: Convert value columns to numeric types before sorting and ranking.
- Missing data handling: When a CUSIP appears in Q3 but not Q2 (or vice versa), treat the missing value as zero for delta computations.
- Delimiter/encoding assumptions: Detect file delimiters (TSV vs CSV) from headers; normalize header names to lowercase to find columns reliably.

## Success Criteria

- The selected accession_number(s) belong to the intended manager in each quarter.
- AUM is extracted from the summary table and matches the aggregated holdings within expected unit tolerances.
- Equity holdings count reflects unique equity CUSIPs after proper filtering.
- Top increases are computed from aggregated values with correct numeric handling and missing-value logic.
- Top managers for the target CUSIP are derived by aggregating quarter holdings and correctly mapping accession_numbers to names.
- The final JSON conforms to the requested schema and parses successfully.

## Optional Script Usage

Use the helper script to implement this workflow deterministically. It provides subcommands for finding accession_numbers, computing fund metrics, comparing quarters, and ranking top managers for a CUSIP.

Examples (paths are illustrative):
- Find accession: `python scripts/fin13f_tools.py find-accession --cover /path/to/q3/COVERPAGE.tsv --query "Target Manager"`
- Fund metrics: `python scripts/fin13f_tools.py aum-holdings --summary /path/to/q3/SUMMARY.tsv --holdings /path/to/q3/HOLDINGS.tsv --accession ACC_NUM`
- Compare quarters: `python scripts/fin13f_tools.py compare-fund --holdings-q2 /path/to/q2/HOLDINGS.tsv --accession-q2 ACC_Q2 --holdings-q3 /path/to/q3/HOLDINGS.tsv --accession-q3 ACC_Q3 --top 5`
- Top holders for CUSIP: `python scripts/fin13f_tools.py top-holders --holdings /path/to/q3/HOLDINGS.tsv --cover /path/to/q3/COVERPAGE.tsv --cusip CUSIP --top 3`
