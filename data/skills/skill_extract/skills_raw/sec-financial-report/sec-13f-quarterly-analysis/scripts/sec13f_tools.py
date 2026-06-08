#!/usr/bin/env python3
"""
SEC 13F analysis helper utilities for local TSV datasets.

Functions provided via subcommands:
- search-fund: fuzzy search COVERPAGE.tsv for manager keywords and return best accession
- aum: compute AUM (sum of VALUE) and holdings counts (equity-only and total) for one accession in a quarter
- compare: compare holdings between two quarters for a single fund and list top-k CUSIPs by dollar increase
- top-holders: list top-k managers holding a specific CUSIP in a given quarter

Assumptions:
- Datasets are stored under a data root with subdirectories per quarter:
    <data_root>/<quarter>/COVERPAGE.tsv
    <data_root>/<quarter>/INFOTABLE.tsv
    <data_root>/<quarter>/SUMMARYPAGE.tsv (optional)
- TSV headers are uppercase. Expected columns include:
    COVERPAGE: ACCESSION_NUMBER, FILINGMANAGER_NAME, ISAMENDMENT (optional)
    INFOTABLE: ACCESSION_NUMBER, CUSIP, VALUE, TITLEOFCLASS, PUTCALL (optional)

Unit caution:
- The 13F VALUE field is often reported in thousands of dollars. Some preprocessed datasets normalize to dollars.
- Use --value-scale 1000 to scale to dollars if necessary.
"""

import argparse
import sys
import os
import re
from typing import Optional, Tuple, List

import pandas as pd

try:
    from rapidfuzz import process, fuzz
    _HAS_RAPIDFUZZ = True
except Exception:
    from difflib import SequenceMatcher
    _HAS_RAPIDFUZZ = False


def _tsv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing required file: {path}")
    return pd.read_csv(path, sep='\t', dtype=str)


def _ensure_columns(df: pd.DataFrame, required: List[str], context: str):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{context}: missing columns: {missing}")


def find_best_accession(keywords: str, quarter: str, data_root: str, prefer_non_amendment: bool = True) -> Tuple[str, str]:
    """Return (accession_number, filingmanager_name) best matching the keywords.
    Prefers non-amendments when available.
    """
    cover_path = os.path.join(data_root, quarter, 'COVERPAGE.tsv')
    cover = _tsv(cover_path)
    # Normalize expected columns
    _ensure_columns(cover, ['ACCESSION_NUMBER'], 'COVERPAGE.tsv')
    # Manager name column can vary; try alternatives
    name_col = None
    for cand in ['FILINGMANAGER_NAME', 'FILER_NAME', 'FILING_MANAGER_NAME', 'MANAGER_NAME']:
        if cand in cover.columns:
            name_col = cand
            break
    if not name_col:
        raise ValueError("COVERPAGE.tsv: cannot find manager name column")

    choices = cover[name_col].fillna('').astype(str).unique().tolist()
    if _HAS_RAPIDFUZZ:
        matches = process.extract(keywords, choices, scorer=fuzz.WRatio, limit=20)
        ranked_names = [m[0] for m in matches]
    else:
        # Fallback fuzzy ranking
        def score(a, b):
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()
        ranked_names = sorted(choices, key=lambda n: score(keywords, n), reverse=True)[:20]

    # Filter for non-amendment preferred
    if prefer_non_amendment and 'ISAMENDMENT' in cover.columns:
        for nm in ranked_names:
            rows = cover[(cover[name_col] == nm) & (cover['ISAMENDMENT'].fillna('N') == 'N')]
            if not rows.empty:
                acc = rows.iloc[0]['ACCESSION_NUMBER']
                return acc, nm
    # Fallback: first occurrence regardless of amendment flag
    for nm in ranked_names:
        rows = cover[cover[name_col] == nm]
        if not rows.empty:
            acc = rows.iloc[0]['ACCESSION_NUMBER']
            return acc, nm
    raise ValueError("No matching manager found in COVERPAGE.tsv")


def _value_series(df: pd.DataFrame) -> pd.Series:
    s = pd.to_numeric(df['VALUE'].replace({',': ''}, regex=True), errors='coerce')
    return s.fillna(0.0)


def _is_equity_row(row: pd.Series) -> bool:
    # Exclude options by PUTCALL when available
    if 'PUTCALL' in row.index and isinstance(row['PUTCALL'], str):
        if row['PUTCALL'].strip().upper() in {'PUT', 'CALL'}:
            return False
    toc = str(row.get('TITLEOFCLASS', '')).upper()
    # Heuristic inclusion for equities
    # Common patterns: COM, SHS, ORD, CLASS A/B, CL A/B
    equity_patterns = [r'\bCOM\b', r'\bSHS\b', r'\bORD\b', r'\bCLASS\s+[A-Z]\b', r'\bCL\s+[A-Z]\b']
    for pat in equity_patterns:
        if re.search(pat, toc):
            return True
    # Fallback: include rows with share denominations and no PUTCALL
    return False


def fund_aum_and_counts(accession: str, quarter: str, data_root: str, value_scale: float = 1.0) -> dict:
    info_path = os.path.join(data_root, quarter, 'INFOTABLE.tsv')
    info = _tsv(info_path)
    _ensure_columns(info, ['ACCESSION_NUMBER', 'VALUE'], 'INFOTABLE.tsv')
    info_acc = info[info['ACCESSION_NUMBER'] == accession].copy()
    if info_acc.empty:
        raise ValueError(f"No INFOTABLE rows for accession {accession} in {quarter}")

    # AUM
    total_value = _value_series(info_acc).sum() * value_scale

    # Counts
    total_count = int(info_acc.shape[0])
    # Equity filter (safe even if columns missing)
    equities = info_acc.apply(_is_equity_row, axis=1)
    equity_count = int(equities.sum())

    return {
        'accession': accession,
        'quarter': quarter,
        'aum_value': float(total_value),
        'equity_count': equity_count,
        'total_count': total_count,
    }


def compare_quarters(accession_old: str, quarter_old: str, accession_new: str, quarter_new: str, data_root: str, topk: int = 5) -> pd.DataFrame:
    # Load both quarters
    info_old = _tsv(os.path.join(data_root, quarter_old, 'INFOTABLE.tsv'))
    info_new = _tsv(os.path.join(data_root, quarter_new, 'INFOTABLE.tsv'))
    _ensure_columns(info_old, ['ACCESSION_NUMBER', 'CUSIP', 'VALUE'], f'INFOTABLE {quarter_old}')
    _ensure_columns(info_new, ['ACCESSION_NUMBER', 'CUSIP', 'VALUE'], f'INFOTABLE {quarter_new}')

    f_old = info_old[info_old['ACCESSION_NUMBER'] == accession_old].copy()
    f_new = info_new[info_new['ACCESSION_NUMBER'] == accession_new].copy()

    g_old = f_old.groupby('CUSIP', as_index=False)['VALUE'].apply(lambda s: pd.to_numeric(s, errors='coerce').fillna(0.0).sum())
    g_old.columns = ['CUSIP', 'VALUE_OLD']
    g_new = f_new.groupby('CUSIP', as_index=False)['VALUE'].apply(lambda s: pd.to_numeric(s, errors='coerce').fillna(0.0).sum())
    g_new.columns = ['CUSIP', 'VALUE_NEW']

    merged = pd.merge(g_new, g_old, on='CUSIP', how='outer').fillna(0.0)
    merged['DELTA'] = merged['VALUE_NEW'] - merged['VALUE_OLD']
    out = merged.sort_values(['DELTA', 'CUSIP'], ascending=[False, True]).head(topk).reset_index(drop=True)
    return out


def top_holders_for_cusip(cusip: str, quarter: str, data_root: str, topk: int = 3) -> pd.DataFrame:
    info = _tsv(os.path.join(data_root, quarter, 'INFOTABLE.tsv'))
    _ensure_columns(info, ['ACCESSION_NUMBER', 'CUSIP', 'VALUE'], 'INFOTABLE.tsv')
    cov = _tsv(os.path.join(data_root, quarter, 'COVERPAGE.tsv'))
    _ensure_columns(cov, ['ACCESSION_NUMBER'], 'COVERPAGE.tsv')
    name_col = None
    for cand in ['FILINGMANAGER_NAME', 'FILER_NAME', 'FILING_MANAGER_NAME', 'MANAGER_NAME']:
        if cand in cov.columns:
            name_col = cand
            break
    if not name_col:
        raise ValueError("COVERPAGE.tsv: cannot find manager name column")

    filtered = info[info['CUSIP'] == cusip].copy()
    if filtered.empty:
        return pd.DataFrame(columns=['ACCESSION_NUMBER', 'TOTAL_VALUE', 'FUND_NAME'])

    agg = (
        filtered.groupby('ACCESSION_NUMBER', as_index=False)['VALUE']
        .apply(lambda s: pd.to_numeric(s, errors='coerce').fillna(0.0).sum())
    )
    agg.columns = ['ACCESSION_NUMBER', 'TOTAL_VALUE']

    # Prefer non-amendment if present
    if 'ISAMENDMENT' in cov.columns:
        cov = cov.sort_values(by=['ISAMENDMENT'], ascending=True)
    cov_map = cov.set_index('ACCESSION_NUMBER')[name_col].to_dict()
    agg['FUND_NAME'] = agg['ACCESSION_NUMBER'].map(lambda x: cov_map.get(x, ''))
    agg = agg.sort_values(['TOTAL_VALUE', 'ACCESSION_NUMBER'], ascending=[False, True]).head(topk).reset_index(drop=True)
    return agg


def main():
    p = argparse.ArgumentParser(description='SEC 13F TSV analysis tools')
    sub = p.add_subparsers(dest='cmd', required=True)

    p1 = sub.add_parser('search-fund', help='Fuzzy search COVERPAGE for manager name')
    p1.add_argument('--keywords', required=True)
    p1.add_argument('--quarter', required=True)
    p1.add_argument('--data-root', required=True)
    p1.add_argument('--allow-amendment', action='store_true', help='Allow amended filings if non-amendment not found')

    p2 = sub.add_parser('aum', help='Compute AUM and holdings counts for one accession in a quarter')
    p2.add_argument('--accession', required=True)
    p2.add_argument('--quarter', required=True)
    p2.add_argument('--data-root', required=True)
    p2.add_argument('--value-scale', type=float, default=1.0, help='Multiply VALUE by this scale (e.g., 1000 if dataset stores thousands)')

    p3 = sub.add_parser('compare', help='Compare two quarters for one fund and list top-k increases')
    p3.add_argument('--accession-old', required=True)
    p3.add_argument('--quarter-old', required=True)
    p3.add_argument('--accession-new', required=True)
    p3.add_argument('--quarter-new', required=True)
    p3.add_argument('--data-root', required=True)
    p3.add_argument('--topk', type=int, default=5)

    p4 = sub.add_parser('top-holders', help='Top-k managers holding a CUSIP in a quarter')
    p4.add_argument('--cusip', required=True)
    p4.add_argument('--quarter', required=True)
    p4.add_argument('--data-root', required=True)
    p4.add_argument('--topk', type=int, default=3)

    args = p.parse_args()

    try:
        if args.cmd == 'search-fund':
            acc, name = find_best_accession(args.keywords, args.quarter, args.data_root, prefer_non_amendment=not args.allow_amendment)
            print(f'best_accession: {acc}')
            print(f'filing_manager_name: {name}')
        elif args.cmd == 'aum':
            res = fund_aum_and_counts(args.accession, args.quarter, args.data_root, value_scale=args.value_scale)
            for k, v in res.items():
                print(f'{k}: {v}')
        elif args.cmd == 'compare':
            df = compare_quarters(args.accession_old, args.quarter_old, args.accession_new, args.quarter_new, args.data_root, topk=args.topk)
            # Print as simple lines for reuse
            for _, row in df.iterrows():
                print(f"CUSIP={row['CUSIP']} VALUE_OLD={row['VALUE_OLD']:.2f} VALUE_NEW={row['VALUE_NEW']:.2f} DELTA={row['DELTA']:.2f}")
        elif args.cmd == 'top-holders':
            df = top_holders_for_cusip(args.cusip, args.quarter, args.data_root, topk=args.topk)
            for i, row in df.iterrows():
                print(f"rank={i+1} accession={row['ACCESSION_NUMBER']} value={row['TOTAL_VALUE']:.2f} fund={row['FUND_NAME']}")
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
