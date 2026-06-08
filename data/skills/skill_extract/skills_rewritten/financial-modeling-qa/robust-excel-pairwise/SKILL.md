---
name: robust-excel-pairwise
description: "Analyze semi-structured Excel data (with possible side-by-side tables) and compute odd/even pairwise comparisons with strong validation and fallback document parsing."
---

# Robust Excel Pairwise Analysis

This skill guides an agent to extract rules from a background document, ingest semi-structured Excel data reliably (including sheets with repeated or side-by-side tables), validate group completeness, and compute odd vs even pairwise comparisons (e.g., game 1 vs 2, 3 vs 4) to produce a single numeric result.

Use this when the prompt:
- provides a background PDF (or similar) that defines scoring/aggregation rules
- provides an Excel workbook with the raw records
- asks for results based on pairing odd-numbered entities with subsequent even-numbered ones, and requires writing only a numeric answer

## Core Principle

Separate concerns and verify each stage:
1) Extract pairing/scoring rules from the background document.
2) Load the Excel robustly (discover headers, detect side-by-side tables, normalize columns).
3) Validate grouping completeness and resolve anomalies before computing.
4) Compute per-group scores according to the rules.
5) Pair odd vs even groups, apply tie policy, and compute the final difference deterministically.

## When to Use

Activate this skill when you must:
- interpret pairing logic (odd vs even, adjacent pairs) from a background document
- handle messy Excel sheets: unknown header row, blank rows, hidden rows, or two tables arranged side by side
- ensure the final output is a single numeric value with strict formatting constraints

## Workflow

Phase 1: Extract and Confirm Rules (from background PDF)
- Parse the background using multiple fallbacks in this order until one succeeds:
  1) a primary PDF parser (e.g., pdfminer.six or your platform's default)
  2) a secondary parser (e.g., PyPDF2)
  3) a text-based fallback (e.g., pdftotext) if available
- Identify and write down:
  - the unit of comparison (e.g., game)
  - grouping keys (e.g., game number, turn, category) and expected per-group record counts
  - how to compute each group’s score (e.g., how to aggregate rows under constraints)
  - how to resolve pairings: odd-numbered groups vs the next even-numbered groups, paired adjacently (1 vs 2, 3 vs 4, ...)
  - tie policy (explicit if stated; if not, choose and document one of: exclude ties, count ties as 0, or use a specified tiebreak rule)
  - whether a higher or lower score wins

Phase 2: Inspect and Load the Excel Workbook
- Enumerate sheet names and preview a few top rows from candidate sheets without assuming headers (header=None) to locate the actual header row.
- Detect header row by scanning early rows for expected header keywords (derived from the background rules). Typical cues include terms like "game", "turn", "score", or domain-specific labels.
- Handle side-by-side tables:
  - Some sheets repeat the same header further right in the same row, forming two adjacent tables. Detect multiple contiguous header segments in the header row.
  - Extract each table segment separately using that header row, then stack (row-bind) them into one uniform table using the intersection of shared columns.
- Normalize the schema:
  - strip whitespace from column names and values
  - standardize case for column names
  - convert numeric fields with coercion (errors='coerce') and handle NaNs explicitly

Phase 3: Validate Grouping and Data Completeness
- Compute group-level counts for the grouping key (e.g., per game). Verify expected record counts per group per the background rules.
- Investigate anomalies:
  - missing records (e.g., only one turn present)
  - duplicated rows
  - blank formatting rows misread as missing data
  - hidden rows or merged cells
- Decide the handling policy:
  - Exclude incomplete groups from scoring if they cannot be reconstructed deterministically
  - Only form a pair when both the odd and its subsequent even group exist and have valid scores
- Record the number of valid groups and valid pairs before proceeding.

Phase 4: Compute Per-Group Scores
- Implement scoring strictly according to the background rules (e.g., category constraints, combining turns without reusing a category, or any specified aggregation).
- Use pure functions for clarity and test them on a few groups manually inspected from the sheet (spot checks). Confirm the function returns expected values and respects constraints.
- Produce one final scalar score per group (e.g., per game).

Phase 5: Pairing and Comparison (Odd vs Even)
- Define Player 1 as odd-numbered groups and Player 2 as even-numbered groups unless the background says otherwise.
- Form adjacent pairs: (1,2), (3,4), ... Only include a pair if both group IDs exist and both have valid scores.
- For each pair, determine the winner using the declared "higher-wins" or "lower-wins" rule and apply the tie policy chosen in Phase 1.
- Compute the final metric as (count of Player 1 wins) minus (count of Player 2 wins).

Phase 6: Output and Formatting
- Write only the numeric result to the required output path. Do not include text, labels, or units.
- Ensure a final newline if the environment expects it.

## Verification

Perform the following checks before finalizing:
- Schema and Ingestion
  - Confirm the detected header row index and that expected columns are present.
  - If side-by-side tables were detected, verify both segments produced consistent columns and the combined row count matches expectations.
- Group Integrity
  - Verify the distribution of records per group matches the expected count from the background rules (spot-check outliers).
  - List missing or incomplete groups and confirm they are excluded from pairing.
- Scoring Consistency
  - Recompute scores for a small sample manually and compare with your function outputs.
- Pairing Logic
  - Confirm that pairs are formed only as (odd, even) with adjacent numbers and that both sides exist.
  - Ensure tie handling matches the declared policy.
- Totals and Difference
  - Cross-check the number of counted pairs = Player 1 wins + Player 2 wins + ties (if counted), minus any excluded pairs.
  - Re-run the computation with a second independent grouping operation (e.g., using a different aggregation path) and confirm identical results.
- Output Format
  - Read back the answer file and verify it contains only the number.

## Common Pitfalls and How to Avoid Them
- Misidentifying the header row
  - Do not assume row 1 is the header. Search for expected keywords and confirm the header row by content.
- Ignoring a second table segment to the right
  - Many workbooks place two identical tables side by side. Scan the header row for repeated keyword clusters and merge both segments.
- Proceeding without checking group completeness
  - Always validate per-group record counts and detect missing turns/rows. Exclude incomplete groups from scoring and any pairs that are missing one side.
- Incorrect tie or winner rule
  - Confirm tie handling and whether higher or lower score wins from the background. Make it explicit in your code.
- Type issues in numeric fields
  - Coerce numeric fields, handle NaNs, and verify that comparisons are numeric, not string-based.
- Incorrect pairing
  - Pair strictly as (1,2), (3,4), ... and map odd → Player 1, even → Player 2 unless instructed otherwise.
- Output contamination
  - Ensure the final output is a single number with no extra text.

## Optional Script Usage

This skill includes a helper script to:
- detect header rows by keywords
- extract and combine side-by-side tables
- validate group completeness
- compute odd/even pairwise difference once you have per-group scores

Example flows:
- Extract a normalized table from a sheet with side-by-side tables and print a summary:
  - python scripts/xlsx_pairwise_helper.py extract --xlsx path/to/file.xlsx --sheet "Data" --keywords game,turn,score
- After you compute per-group scores and save a CSV with columns: game,score, compute Player1-Player2 difference (odd vs even pairs):
  - python scripts/xlsx_pairwise_helper.py pairdiff --csv per_group_scores.csv --group-col game --score-col score --higher-wins --ties exclude

Note: The script does not implement dataset-specific scoring rules. You must compute the per-group scores according to the background document and then pass the resulting table into the pairwise step.
