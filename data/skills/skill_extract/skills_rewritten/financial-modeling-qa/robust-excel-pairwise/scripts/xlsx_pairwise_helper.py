#!/usr/bin/env python3
"""
Helper utilities for robust Excel table extraction (including side-by-side tables)
and odd/even pairwise comparison once group-level scores are available.

Subcommands:
  extract   Detect header row, extract one or two side-by-side tables, and print a JSON summary.
  pairdiff  Given a CSV of group-level scores (columns: group, score), compute (odd wins) - (even wins).

Note: This script does NOT implement dataset-specific scoring. Compute per-group scores
according to your background rules separately and feed them into pairdiff.
"""

import argparse
import sys
import json
from typing import List, Tuple, Optional, Dict

import pandas as pd


def _lower_str(x):
    return str(x).strip().lower() if pd.notna(x) else ""


def find_header_row_and_segments(sheet_df: pd.DataFrame,
                                 required_keywords: List[str],
                                 max_search_rows: int = 60,
                                 min_match: int = 1) -> Tuple[Optional[int], List[Tuple[int, int]]]:
    """Find header row and contiguous column segments that look like headers.

    - required_keywords: list of lowercase keywords expected in header names
    - Returns (header_row_index, segments), where segments is list of (start_col, end_col_inclusive)
    - A segment is a contiguous block of non-empty header cells in the detected header row.
    """
    required_keywords = [k.strip().lower() for k in required_keywords if k.strip()]

    # Search header row by keyword match
    header_row_idx = None
    for r in range(min(max_search_rows, sheet_df.shape[0])):
        row_vals = [str(v).strip() if pd.notna(v) else "" for v in sheet_df.iloc[r, :].tolist()]
        row_lower = [v.lower() for v in row_vals]
        # Count how many required keywords appear in this row
        hits = sum(any(k in cell for cell in row_lower) for k in required_keywords) if required_keywords else sum(bool(cell) for cell in row_lower)
        # Heuristic: at least min_match keyword hits or multiple non-empty cells
        if hits >= min_match and sum(bool(cell) for cell in row_vals) >= max(2, min_match):
            header_row_idx = r
            break

    if header_row_idx is None:
        return None, []

    # Find contiguous header segments (non-empty cells) in the detected header row
    row_vals = [str(v).strip() if pd.notna(v) else "" for v in sheet_df.iloc[header_row_idx, :].tolist()]
    segments = []
    start = None
    for c, val in enumerate(row_vals + [""]):  # add sentinel
        if val and start is None:
            start = c
        elif not val and start is not None:
            segments.append((start, c - 1))
            start = None

    # Filter segments that include at least one required keyword (if provided)
    def seg_has_keyword(seg):
        sc, ec = seg
        seg_vals = [row_vals[i].lower() for i in range(sc, ec + 1)]
        if not required_keywords:
            return True
        return any(any(k in v for v in seg_vals) for k in required_keywords)

    segments = [seg for seg in segments if seg_has_keyword(seg)]
    return header_row_idx, segments


def extract_tables_from_sheet(sheet_df: pd.DataFrame,
                              header_row: int,
                              segments: List[Tuple[int, int]],
                              use_intersection: bool = True) -> pd.DataFrame:
    """Extract one or more side-by-side tables from a sheet and stack them.

    - header_row: index of the header row
    - segments: list of (start_col, end_col_inclusive) for table header segments
    - use_intersection: if True, keep only columns common to all segments; else use union.
    """
    tables = []
    all_cols_sets = []

    for (sc, ec) in segments:
        header = sheet_df.iloc[header_row, sc:ec+1].tolist()
        data_block = sheet_df.iloc[header_row+1:, sc:ec+1].copy()
        data_block.columns = [str(h).strip() for h in header]
        # Drop rows that are fully NaN or empty strings
        mask_not_all_empty = ~(data_block.isna() | (data_block.applymap(lambda x: str(x).strip() == ""))).all(axis=1)
        data_block = data_block.loc[mask_not_all_empty]
        tables.append(data_block)
        all_cols_sets.append(set(data_block.columns))

    if not tables:
        return pd.DataFrame()

    if use_intersection:
        common_cols = set.intersection(*all_cols_sets)
        if not common_cols:
            # Fallback to union to avoid empty result
            common_cols = set.union(*all_cols_sets)
        tables = [t.loc[:, [c for c in t.columns if c in common_cols]] for t in tables]
        df = pd.concat(tables, axis=0, ignore_index=True)
    else:
        # Align on union of columns
        df = pd.concat(tables, axis=0, ignore_index=True)

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    return df


def group_count_stats(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Return counts per group for validation."""
    if group_col not in df.columns:
        raise ValueError(f"Missing group column: {group_col}")
    return df.groupby(group_col, dropna=False).size().reset_index(name="count")


def odd_even_pairs_present(group_ids: List[int]) -> Dict[str, int]:
    """Compute counts of present odd/even groups and valid pairs."""
    ids = sorted(set(int(g) for g in group_ids if pd.notna(g)))
    odds = [g for g in ids if g % 2 == 1]
    evens = set(g for g in ids if g % 2 == 0)
    pairs = sum(1 for o in odds if (o + 1) in evens)
    return {"unique_groups": len(ids), "odds": len(odds), "evens": len(evens), "pairs": pairs}


def pairwise_difference(df: pd.DataFrame,
                        group_col: str,
                        score_col: str,
                        higher_wins: bool = True,
                        tie_policy: str = "exclude") -> Dict[str, int]:
    """Compute (odd wins) - (even wins) for adjacent pairs.

    tie_policy: one of {"exclude", "count0"}
      - exclude: do not count pairs where scores are exactly equal
      - count0: count the pair but it contributes 0 to the difference
    """
    if group_col not in df.columns or score_col not in df.columns:
        raise ValueError("Missing required columns for pairwise comparison.")

    # Keep one row per group (assumes per-group scoring has been computed)
    gdf = df[[group_col, score_col]].dropna().copy()
    gdf[group_col] = gdf[group_col].astype(int)
    gdf = gdf.drop_duplicates(subset=[group_col])

    # Build dictionary group -> score
    scores = dict(zip(gdf[group_col], pd.to_numeric(gdf[score_col], errors='coerce')))

    odd_wins = 0
    even_wins = 0
    ties = 0

    # Iterate odd groups and compare with next even
    for g in sorted(k for k in scores.keys() if k % 2 == 1):
        o = g
        e = g + 1
        if e not in scores:
            continue
        so = scores[o]
        se = scores[e]
        if pd.isna(so) or pd.isna(se):
            continue
        if so == se:
            ties += 1
            # ties contribute nothing unless tie_policy enforces another behavior
            continue
        if higher_wins:
            if so > se:
                odd_wins += 1
            else:
                even_wins += 1
        else:
            if so < se:
                odd_wins += 1
            else:
                even_wins += 1

    diff = odd_wins - even_wins
    return {
        "odd_wins": odd_wins,
        "even_wins": even_wins,
        "ties": ties,
        "difference": diff,
    }


def cmd_extract(args: argparse.Namespace) -> int:
    xlsx = args.xlsx
    sheet = args.sheet
    keywords = [k.strip() for k in (args.keywords.split(",") if args.keywords else []) if k.strip()]

    # Load with no header for robust inspection
    try:
        sheet_df = pd.read_excel(xlsx, sheet_name=sheet, header=None, engine=None)
    except Exception:
        # try openpyxl engine explicitly as a fallback
        sheet_df = pd.read_excel(xlsx, sheet_name=sheet, header=None, engine="openpyxl")

    header_row, segments = find_header_row_and_segments(sheet_df, [k.lower() for k in keywords], args.max_search_rows, args.min_match)

    result = {
        "sheet_shape": [int(sheet_df.shape[0]), int(sheet_df.shape[1])],
        "header_row": int(header_row) if header_row is not None else None,
        "segments": segments,
        "columns": None,
        "rows_extracted": 0,
    }

    if header_row is not None and segments:
        df = extract_tables_from_sheet(sheet_df, header_row, segments, use_intersection=not args.use_union)
        # Normalize columns
        df.columns = [str(c).strip() for c in df.columns]
        # Basic cleanup
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        result["columns"] = list(df.columns)
        result["rows_extracted"] = int(df.shape[0])

    print(json.dumps(result, ensure_ascii=False))
    return 0


def cmd_pairdiff(args: argparse.Namespace) -> int:
    # Load per-group scores CSV
    df = pd.read_csv(args.csv)
    higher_wins = args.higher_wins
    tie_policy = args.ties

    stats = pairwise_difference(df, args.group_col, args.score_col, higher_wins=higher_wins, tie_policy=tie_policy)

    if args.number_only:
        # Print only the numeric difference
        print(stats["difference"])
    else:
        print(json.dumps(stats, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Excel extraction and odd/even pairwise helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("extract", help="Extract side-by-side tables from an Excel sheet and summarize")
    pe.add_argument("--xlsx", required=True, help="Path to Excel file")
    pe.add_argument("--sheet", default=None, help="Sheet name (optional)")
    pe.add_argument("--keywords", default="", help="Comma-separated header keywords (lower/upper case ignored)")
    pe.add_argument("--max-search-rows", type=int, default=60, help="Max rows to scan for header")
    pe.add_argument("--min-match", type=int, default=1, help="Minimum keyword matches to accept a header row")
    pe.add_argument("--use-union", action="store_true", help="Use union of columns instead of intersection when merging segments")
    pe.set_defaults(func=cmd_extract)

    pp = sub.add_parser("pairdiff", help="Compute (odd wins) - (even wins) from per-group scores")
    pp.add_argument("--csv", required=True, help="CSV with per-group scores")
    pp.add_argument("--group-col", required=True, help="Column name for group identifier (e.g., game)")
    pp.add_argument("--score-col", required=True, help="Column name for numeric score")
    pp.add_argument("--higher-wins", action="store_true", help="If set, higher score wins; otherwise lower score wins")
    pp.add_argument("--ties", choices=["exclude", "count0"], default="exclude", help="Tie handling policy")
    pp.add_argument("--number-only", action="store_true", help="Print only the numeric difference")
    pp.set_defaults(func=cmd_pairdiff)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        sys.exit(args.func(args))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
