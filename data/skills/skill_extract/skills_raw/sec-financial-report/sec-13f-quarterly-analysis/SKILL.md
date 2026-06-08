---
name: sec-13f-quarterly-analysis
description: "Analyze SEC 13F TSV datasets to find fund accessions, compute AUM and equity counts, compare holdings across quarters, and identify top holders for a given CUSIP."
---

# SEC 13F Quarterly Analysis

Reusable workflow to work with local, preprocessed SEC 13F datasets organized by quarter directories (e.g., 2025-q2, 2025-q3). This skill covers fuzzy manager lookup, AUM and holdings counting, quarter-over-quarter comparison for a single filer, and identifying the top managers holding a specific CUSIP.

## When to Use

Activate this skill when you need to:
- find a manager's accession number in a given quarter (fuzzy search on COVERPAGE.tsv)
- compute a fund's AUM and number of equity holdings from INFOTABLE.tsv
- compare a fund's quarter-over-quarter position changes and extract top increases by dollar value
- find the top managers holding a given CUSIP in a specific quarter and map them to filer names

## Core Workflow

1. Establish dataset layout
   - Each quarter directory should contain at least COVERPAGE.tsv and INFOTABLE.tsv.
   - Optional: SUMMARYPAGE.tsv (if present) may include TABLEVALUETOTAL.
   - Confirm column headers with `head -1` if in doubt.

2. Find accession number by manager name (fuzzy)
   - Search COVERPAGE.tsv for the manager’s name; prefer non-amendments (ISAMENDMENT == 'N') when available.
   - Verify the returned accession_number appears exactly in COVERPAGE.tsv.

3. Compute AUM and equity count for a fund (one quarter)
   - Filter INFOTABLE.tsv by ACCESSION_NUMBER.
   - AUM: sum VALUE (confirm unit; see Verification below).
   - Equity count: count rows that represent equities only (exclude options and non-equity instruments). Practical filter:
     - Exclude rows with PUTCALL in {'PUT','CALL'} when the column exists.
     - Include TITLEOFCLASS that indicates common/ordinary shares (e.g., contains COM, SHS, ORD). Use case-insensitive match.
   - Also keep the total holding count for reference.

4. Compare two quarters for one fund
   - Identify the two accessions independently (one per quarter), as accessions change by filing season.
   - Filter each quarter’s INFOTABLE.tsv by the respective ACCESSION_NUMBER.
   - Group by CUSIP and sum VALUE for each quarter.
   - Compute delta = VALUE_q3 − VALUE_q2; rank by largest positive deltas to get top buys (return CUSIPs in required order).

5. Top holders for a CUSIP in a quarter
   - Filter quarter’s INFOTABLE.tsv to that CUSIP across all filers.
   - Group by ACCESSION_NUMBER, sum VALUE, sort descending.
   - Map ACCESSION_NUMBERs to FILINGMANAGER_NAME via COVERPAGE.tsv.

6. Produce outputs in required schema
   - Types: AUM as number, counts as integers, and lists for CUSIPs or manager names as strings.
   - Validate JSON structure before writing.

## Verification

- Accessions: Confirm the chosen accession appears in the quarter’s COVERPAGE.tsv and has ISAMENDMENT == 'N' if possible. If ISAMENDMENT is missing/blank, accept the row but note it.
- VALUE units: In official 13F, VALUE is reported in thousands of dollars. Some preprocessed datasets normalize units to dollars. Verify by spot-checking known positions against issuer share counts and plausible prices or by reading any documentation. If unsure, report both the raw sum and the unit assumption, or choose a consistent convention and state it.
- Equity count logic: Cross-check counts by inspecting TITLEOFCLASS and PUTCALL columns on a few rows to ensure options and non-equities are excluded from the “stock” count.
- Quarter paths: Ensure file reads include the correct quarter subdirectory. Do not rely on hardcoded root-only paths.
- Name mapping: Verify ACCESSION_NUMBER-to-name mapping by exact match in COVERPAGE.tsv.
- Top-k stability: When deltas tie, use a secondary sort (e.g., CUSIP ascending) to keep deterministic results.

## Common Pitfalls

- Missing quarter in data paths: Scripts that read `/root/INFOTABLE.tsv` will fail when files live under `/root/<quarter>/INFOTABLE.tsv`. Always include quarter in paths or pass a data_root/quarter parameter.
- Using amendment rows: Including amended filings may skew results or duplicate managers. Prefer ISAMENDMENT == 'N' when present.
- Misinterpreting VALUE units: Treating VALUE as dollars when it is actually thousands (or vice versa) leads to 1000× errors. Verify once per dataset and be consistent.
- Wrong “stock count” definition: Total holdings count includes options and other securities. If asked for stocks, filter out options (PUT/CALL) and non-equity classes.
- Brittle fuzzy match: Fuzzy search can return similarly named entities. Always verify the accession/name pair in COVERPAGE.tsv.
- Ignoring column names: TSV schemas can vary. Confirm EXPECTED columns exist: ACCESSION_NUMBER, CUSIP, VALUE, TITLEOFCLASS, PUTCALL (optional), and in COVERPAGE.tsv: ACCESSION_NUMBER, FILINGMANAGER_NAME, ISAMENDMENT.

## Optional Script Usage

This skill includes a generic helper script `scripts/sec13f_tools.py`.

Examples:

- Find best accession for a manager in a quarter (fuzzy):
  python3 scripts/sec13f_tools.py search-fund --keywords "renaissance technologies" --quarter 2025-q3 --data-root /root

- AUM and counts (equity and total) for a fund:
  python3 scripts/sec13f_tools.py aum --accession 000XXXXXXX-XX-XXXXXX --quarter 2025-q3 --data-root /root
  # If your dataset stores VALUE in thousands and you want dollars:
  python3 scripts/sec13f_tools.py aum --accession ... --quarter 2025-q3 --data-root /root --value-scale 1000

- Compare holdings between two quarters for one fund and list top-5 increases by CUSIP:
  python3 scripts/sec13f_tools.py compare --accession-new NEWACC --quarter-new 2025-q3 \
      --accession-old OLDACC --quarter-old 2025-q2 --topk 5 --data-root /root

- Top-3 managers holding a CUSIP in a quarter (by total VALUE):
  python3 scripts/sec13f_tools.py top-holders --cusip 69608A108 --quarter 2025-q3 --topk 3 --data-root /root

## Success Criteria

- All file reads target the correct quarter directories.
- Accession numbers are verified against COVERPAGE.tsv.
- AUM and counts are computed from the correct filtered universe, with unit assumptions stated and consistent.
- Top increases are computed from grouped, accession-filtered holdings and sorted by dollar delta.
- Top holders are mapped from ACCESSION_NUMBER to fund names accurately.
- Final outputs adhere to the requested schema and types.
