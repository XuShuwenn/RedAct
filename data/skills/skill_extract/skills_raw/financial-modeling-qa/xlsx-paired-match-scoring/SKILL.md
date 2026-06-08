---
name: xlsx-paired-match-scoring
description: "Process messy Excel game logs (including side-by-side tables), compute optimal category-based game scores from two turns, and compare paired matches (odd vs even)."
---

# Robust XLSX Paired Match Scoring

This skill provides a robust workflow to:
- read large Excel sheets where the same table may appear twice side-by-side (second copy often labeled with Unnamed: N columns)
- reconstruct complete two-turn games
- compute the best game score by assigning different scoring categories to each turn
- compare odd vs even games as head-to-head matches and compute the win difference

It integrates header detection, side-table stitching, validations, and deterministic scoring utilities.

## When to Use

Use this skill when:
- You must compute game scores from a large Excel sheet with two turns per game and six dice rolls per turn
- The dataset contains formatting quirks (e.g., hidden/blank rows, side-by-side duplicate tables with Unnamed columns)
- You need to pair odd-numbered games vs the next even-numbered games and count wins/ties
- The scoring rules are given in a separate document and must be implemented faithfully

## Core Workflow

1) Extract Rules from Background
- Identify categories, their scoring, and constraints from the background document:
  - High and Often: highest die value × count of that value
  - Summation: sum of the six dice
  - Highs and Lows: (max die) × (min die) × (max − min)
  - Only two numbers: fixed points if exactly two distinct values in the six dice
  - All the numbers: fixed points if the set is exactly {1,2,3,4,5,6}
  - Ordered subset of four: fixed points if there exists a contiguous run of length 4, increasing or decreasing, in the roll order (unless the document explicitly defines a non-contiguous subsequence variant)
- Confirm constant values for fixed-point categories and the exact definition of "Ordered subset of four" from the background.
- Confirm that in a two-turn game, you must assign different categories to the two turns (no reuse).

2) Load Excel Robustly
- Detect the header row rather than assuming a fixed skip:
  - Read with header=None and scan the first ~30 rows for a row containing the expected column labels (e.g., Turn number, Game number, Roll 1..Roll 6). If detection fails, accept a user-provided header index.
- Read the sheet using the detected header row.
- Normalize column names (trim/case-fold) and map to canonical names: Turn number, Game number, Roll 1..Roll 6.

3) Stitch Side-by-Side Tables (if present)
- Inspect columns named like Unnamed: N. If you find a contiguous block of Unnamed columns whose count matches the main table width, interpret it as a second table copy.
- Rename that Unnamed block to the canonical column names and append its non-empty rows to the main table.
- Drop rows entirely empty across the canonical columns.

4) Type and Domain Validation
- Ensure Turn number and Game number are integers.
- Ensure each Roll i is an integer within the valid domain [1..6]. If outside the domain, the row is malformed; decide to drop or error.
- Verify that each game has exactly two turns. If not, choose a policy:
  - error (preferred): stop and fix input by re-checking stitching
  - best-single: score single-turn games by the best single-category score
  - zero-pad: add a zero-scoring dummy turn (enforcing different categories)
  - drop: exclude incomplete games from matches

5) Per-turn Scoring (implement exactly as specified in the background)
- Implement deterministic functions for each category.
- For Ordered subset of four, use the contiguous sliding-window check unless instructed otherwise. If the background defines a subsequence interpretation, switch accordingly and re-verify results.

6) Per-game Best Score (two turns, distinct categories)
- Compute all sums of turn1_category + turn2_category where categories differ.
- Take the maximum as the game score. If using a fallback policy for single-turn games, apply that consistently.

7) Head-to-head Matches and Difference
- Pair odd games vs the next even games (1 vs 2, 3 vs 4, ...).
- Count wins: higher game score wins; equal scores are ties (do not count toward either player unless the background specifies otherwise).
- Compute (wins by Player 1) − (wins by Player 2).

8) Output
- Write only the final integer to the required path, with no extra text.

## Verification

- Header detection: After loading, confirm that the canonical columns exist and are correctly typed.
- Stitching: Verify that combining the side-table rows restores completeness (e.g., two turns per game) and no duplicates remain.
- Turn counts: Ensure every game has exactly two turns; if not, list offending game IDs and fix the load/stitching before proceeding (preferred).
- Sanity checks on scoring functions:
  - Only two numbers: returns fixed points only for exactly two distinct values
  - All the numbers: returns fixed points only for the exact set {1..6}
  - Ordered subset of four: verify with small test cases for both increasing and decreasing contiguous windows
- Cross-check category assignment constraint: ensure no same category is used for both turns in a game when computing max
- Pairing integrity: confirm odd vs next even pairing and that ties are not miscounted as wins
- Determinism: repeated runs produce identical results

## Common Pitfalls

- Mis-detected header row causing column shifts (roll columns read as NaN or wrong labels). Always detect header dynamically or validate with explicit checks.
- Ignoring side-by-side table copies. Rows stored under Unnamed columns may hold missing turns; failing to stitch them leads to incomplete games and wrong results.
- Silent single-turn handling. Using a single-turn best score or dropping games changes outcomes; apply a deliberate, documented policy consistent with the background.
- Misinterpreting "Ordered subset of four" as a non-contiguous subsequence when the rules require contiguous order (or vice versa). Confirm and test with edge cases.
- Reusing the same category across both turns. Enforce distinct categories when maximizing.
- Off-by-one in match pairing (e.g., pairing 0 vs 1 instead of 1 vs 2). Use explicit odd/even logic.
- Counting ties as wins. Unless specified otherwise, ties should not increment either player's count.
- Writing extra text along with the numeric answer. Output only the final number.

## Optional Script Usage

A helper script is provided to:
- infer header row
- load and stitch side-by-side tables
- validate two turns per game
- compute per-turn scores and best game scores
- compute match difference

Example usage:
- Basic (strict two-turn requirement):
  python3 scripts/xlsx_match_tools.py --xlsx /path/to/data.xlsx --sheet Data --out /path/to/answer.txt

- Specify header row index explicitly:
  python3 scripts/xlsx_match_tools.py --xlsx /path/to/data.xlsx --sheet Data --header-index 8 --out /path/to/answer.txt

- Allow single-turn games using the best-single policy:
  python3 scripts/xlsx_match_tools.py --xlsx /path/to/data.xlsx --single-turn-policy best-single --out /path/to/answer.txt

Adjust the contiguous run behavior with --ordered-run contiguous|subsequence based on the background rules.
