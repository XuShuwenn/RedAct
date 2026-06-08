#!/usr/bin/env python3
"""Robust XLSX paired match scoring utility.

Features:
- Header row inference
- Side-by-side table stitching (Unnamed columns)
- Per-turn scoring and per-game maximum with distinct categories
- Odd vs even match difference computation

Usage examples:
  python3 scripts/xlsx_match_tools.py --xlsx /path/to/data.xlsx --sheet Data --out /path/to/answer.txt
  python3 scripts/xlsx_match_tools.py --xlsx /path/to/data.xlsx --sheet Data --header-index 8 --out /path/to/answer.txt
  python3 scripts/xlsx_match_tools.py --xlsx /path/to/data.xlsx --single-turn-policy best-single --out /path/to/answer.txt

Note: Verify category constants and ordered-run interpretation against the background rules.
"""

import argparse
import sys
from typing import List, Tuple, Dict, Optional
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import itertools

CANON_COLS = [
    "Turn number",
    "Game number",
    "Roll 1",
    "Roll 2",
    "Roll 3",
    "Roll 4",
    "Roll 5",
    "Roll 6",
]

CATEGORY_NAMES = [
    "High and Often",
    "Summation",
    "Highs and Lows",
    "Only two numbers",
    "All the numbers",
    "Ordered subset of four",
]

# Default constants; confirm with background doc
ONLY_TWO_POINTS = 30
ALL_NUMBERS_POINTS = 40
ORDERED_SUBSET_POINTS = 50


def infer_header_row(xlsx_path: str, sheet: str, search_rows: int = 30) -> Optional[int]:
    """Infer header row by scanning for expected labels in the first N rows.
    Returns 0-based header row index or None if not found.
    """
    df = pd.read_excel(xlsx_path, sheet_name=sheet, header=None)
    target_tokens = {c.lower() for c in ["turn number", "game number", "roll 1"]}
    for r in range(min(search_rows, len(df))):
        row_vals = df.iloc[r, : min(50, df.shape[1])].tolist()
        row_tokens = {str(x).strip().lower() for x in row_vals if pd.notna(x)}
        if target_tokens.issubset(row_tokens):
            return r
    return None


def normalize_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Build a mapping from current column labels to canonical labels.
    Matches case-insensitively based on expected names.
    Returns mapping dict; raises if any canonical column is missing.
    """
    existing = {str(c).strip().lower(): c for c in df.columns}
    mapping = {}
    for canon in CANON_COLS:
        key = canon.lower()
        if key in existing:
            mapping[existing[key]] = canon
        else:
            # try tolerant match for Roll i columns
            if key.startswith("roll "):
                # e.g., match "roll 1" ignoring whitespace/case
                found = None
                for k, v in existing.items():
                    if k.replace(" ", "") == key.replace(" ", ""):
                        found = v
                        break
                if found is not None:
                    mapping[found] = canon
                    continue
            raise ValueError(f"Missing expected column: {canon}")
    return mapping


def extract_side_table(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """If a side-by-side second table exists under Unnamed columns, extract it.
    Looks for a contiguous block of Unnamed columns with width == len(CANON_COLS).
    Returns a DataFrame with canonical columns or None if not found.
    """
    cols = list(df.columns)
    # Identify indices of Unnamed columns
    unnamed_idx = [i for i, c in enumerate(cols) if isinstance(c, str) and c.lower().startswith("unnamed")]
    if not unnamed_idx:
        return None
    # Group into contiguous runs
    runs: List[Tuple[int, int]] = []  # (start, end) inclusive
    start = None
    prev = None
    for idx in unnamed_idx:
        if start is None:
            start = prev = idx
        elif idx == prev + 1:
            prev = idx
        else:
            runs.append((start, prev))
            start = prev = idx
    if start is not None:
        runs.append((start, prev))
    # Find a run matching the width
    width = len(CANON_COLS)
    for s, e in runs:
        if (e - s + 1) >= width:
            block = cols[s : s + width]
            extra = df[block].copy()
            # Rename to canonical
            extra.columns = CANON_COLS
            # Drop rows that are all-NA across canonical columns
            extra = extra.dropna(how="all")
            # Keep only rows where Turn number or Game number is present
            if not extra.empty and (extra["Turn number"].notna().any() or extra["Game number"].notna().any()):
                return extra
    return None


def stitch_tables(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and stitch side table if present."""
    mapping = normalize_columns(df)
    main = df.rename(columns=mapping)[CANON_COLS].copy()
    extra = extract_side_table(df)
    if extra is not None:
        combined = pd.concat([main, extra], ignore_index=True)
    else:
        combined = main
    # Drop rows that are empty across canonical columns
    combined = combined.dropna(how="all")
    return combined


def coerce_int_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
        # Drop rows where these become NaN
    out = out.dropna(subset=cols)
    out[cols] = out[cols].astype(int)
    return out


def validate_roll_domain(df: pd.DataFrame, roll_cols: List[str]) -> None:
    for c in roll_cols:
        bad = df[(df[c] < 1) | (df[c] > 6)]
        if not bad.empty:
            raise ValueError(f"Invalid values in {c}; expected 1..6. First offending rows: {bad.index[:5].tolist()}")


def has_run4_contiguous(rolls: List[int]) -> bool:
    for i in range(len(rolls) - 3):
        seq = rolls[i : i + 4]
        if all(seq[j + 1] - seq[j] == 1 for j in range(3)):
            return True
        if all(seq[j + 1] - seq[j] == -1 for j in range(3)):
            return True
    return False


def has_run4_subsequence(rolls: List[int]) -> bool:
    for idxs in itertools.combinations(range(6), 4):
        seq = [rolls[i] for i in idxs]
        if all(seq[j + 1] - seq[j] == 1 for j in range(3)):
            return True
        if all(seq[j + 1] - seq[j] == -1 for j in range(3)):
            return True
    return False


def turn_score(rolls: List[int], ordered_run_mode: str = "contiguous") -> Dict[str, int]:
    high = max(rolls)
    low = min(rolls)
    cnt = Counter(rolls)
    scores = {
        "High and Often": high * cnt[high],
        "Summation": sum(rolls),
        "Highs and Lows": high * low * (high - low),
        "Only two numbers": ONLY_TWO_POINTS if len(cnt) == 2 else 0,
        "All the numbers": ALL_NUMBERS_POINTS if set(rolls) == {1, 2, 3, 4, 5, 6} else 0,
        "Ordered subset of four": 0,
    }
    if ordered_run_mode == "contiguous":
        ok = has_run4_contiguous(rolls)
    elif ordered_run_mode == "subsequence":
        ok = has_run4_subsequence(rolls)
    else:
        raise ValueError("ordered_run_mode must be 'contiguous' or 'subsequence'")
    if ok:
        scores["Ordered subset of four"] = ORDERED_SUBSET_POINTS
    return scores


def best_game_score(scores1: Dict[str, int], scores2: Dict[str, int]) -> int:
    best = None
    for c1, s1 in scores1.items():
        for c2, s2 in scores2.items():
            if c1 == c2:
                continue
            total = s1 + s2
            if best is None or total > best:
                best = total
    # In a well-formed case, best will be set. If not, treat as 0.
    return int(best or 0)


def compute_game_scores(df: pd.DataFrame, ordered_run_mode: str, single_turn_policy: str) -> Dict[int, int]:
    roll_cols = [f"Roll {i}" for i in range(1, 7)]
    game_groups = defaultdict(list)
    for _, row in df.iterrows():
        rolls = [int(row[c]) for c in roll_cols]
        game = int(row["Game number"])
        sc = turn_score(rolls, ordered_run_mode=ordered_run_mode)
        game_groups[game].append(sc)

    scores: Dict[int, int] = {}
    for g, turns in game_groups.items():
        if len(turns) == 2:
            scores[g] = best_game_score(turns[0], turns[1])
        elif len(turns) < 2:
            if single_turn_policy == "error":
                raise ValueError(f"Game {g} has {len(turns)} turn(s); expected 2. Consider stitching side-table or set a single-turn policy.")
            elif single_turn_policy == "best-single":
                scores[g] = max(turns[0].values())
            elif single_turn_policy == "zero-pad":
                zero_turn = {k: 0 for k in CATEGORY_NAMES}
                scores[g] = best_game_score(turns[0], zero_turn)
            elif single_turn_policy == "drop":
                # Do not create an entry; match computation will skip this pair
                continue
            else:
                raise ValueError("Invalid single_turn_policy")
        else:
            # More than 2 turns found; pick the best pairing among any two turns
            best = None
            for t1, t2 in itertools.combinations(turns, 2):
                s = best_game_score(t1, t2)
                if best is None or s > best:
                    best = s
            scores[g] = int(best or 0)
    return scores


def match_diff(game_scores: Dict[int, int]) -> Tuple[int, int, int, int]:
    if not game_scores:
        return 0, 0, 0, 0
    gmin, gmax = min(game_scores), max(game_scores)
    p1 = p2 = ties = 0
    # Pair odd vs next even
    for g in range(gmin if gmin % 2 == 1 else gmin + 1, gmax + 1, 2):
        g1, g2 = g, g + 1
        if g1 not in game_scores or g2 not in game_scores:
            continue
        s1, s2 = game_scores[g1], game_scores[g2]
        if s1 > s2:
            p1 += 1
        elif s2 > s1:
            p2 += 1
        else:
            ties += 1
    return p1, p2, ties, p1 - p2


def write_answer(path: str, value: int) -> None:
    with open(path, "w") as f:
        f.write(str(int(value)))


def main():
    ap = argparse.ArgumentParser(description="Robust XLSX paired match scoring")
    ap.add_argument("--xlsx", required=True, help="Path to Excel file")
    ap.add_argument("--sheet", default="Data", help="Worksheet name")
    ap.add_argument("--header-index", type=int, default=None, help="0-based header row index (optional; inferred if omitted)")
    ap.add_argument("--ordered-run", choices=["contiguous", "subsequence"], default="contiguous", help="Run-of-4 interpretation")
    ap.add_argument("--single-turn-policy", choices=["error", "best-single", "zero-pad", "drop"], default="error", help="How to handle games with <2 turns")
    ap.add_argument("--out", required=True, help="Output path for final integer result")
    args = ap.parse_args()

    header_idx = args.header_index
    if header_idx is None:
        header_idx = infer_header_row(args.xlsx, args.sheet)
        if header_idx is None:
            print("WARNING: Could not infer header row; defaulting to 0.", file=sys.stderr)
            header_idx = 0

    raw = pd.read_excel(args.xlsx, sheet_name=args.sheet, header=header_idx)

    # Stitch tables
    combined = stitch_tables(raw)

    # Drop rows missing turn/game numbers
    combined = combined.dropna(subset=["Turn number", "Game number"]).copy()

    # Coerce ints
    combined = coerce_int_columns(combined, ["Turn number", "Game number"] + [f"Roll {i}" for i in range(1, 7)])

    # Validate roll domain
    validate_roll_domain(combined, [f"Roll {i}" for i in range(1, 7)])

    # Compute game scores
    scores = compute_game_scores(combined, ordered_run_mode=args.ordered_run, single_turn_policy=args.single_turn_policy)

    # Compute match diff
    p1, p2, ties, diff = match_diff(scores)

    # Write only the final integer
    write_answer(args.out, diff)


if __name__ == "__main__":
    main()
