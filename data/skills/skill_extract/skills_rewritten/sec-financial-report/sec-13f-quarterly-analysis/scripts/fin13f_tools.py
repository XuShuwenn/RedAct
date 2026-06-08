#!/usr/bin/env python3
"""SEC 13F analysis helpers: accession search, fund metrics, quarter comparison, and top holders.

This script is designed to work with tabular COVERPAGE, SUMMARY, and HOLDINGS files
for a single quarter. It detects delimiters (TSV/CSV), normalizes headers to lowercase,
handles common column name variants, and provides subcommands for typical tasks.

Usage examples:
  python scripts/fin13f_tools.py find-accession --cover /path/to/q3/COVERPAGE.tsv --query "Fund Name"
  python scripts/fin13f_tools.py aum-holdings --summary /path/to/q3/SUMMARY.tsv --holdings /path/to/q3/HOLDINGS.tsv --accession ACC_NUM
  python scripts/fin13f_tools.py compare-fund --holdings-q2 /path/to/q2/HOLDINGS.tsv --accession-q2 ACC_Q2 --holdings-q3 /path/to/q3/HOLDINGS.tsv --accession-q3 ACC_Q3 --top 5
  python scripts/fin13f_tools.py top-holders --holdings /path/to/q3/HOLDINGS.tsv --cover /path/to/q3/COVERPAGE.tsv --cusip CUSIP --top 3
"""

import argparse
import csv
import difflib
import json
import os
import re
import sys
from typing import Dict, List, Tuple, Optional


def _detect_delimiter(path: str) -> str:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        first = f.readline()
    # Prefer TSV if a tab is present; else fallback to comma
    return '\t' if '\t' in first else ','


def _normalize_header(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower())


def _read_rows(path: str) -> List[Dict[str, str]]:
    delim = _detect_delimiter(path)
    with open(path, 'r', encoding='utf-8', errors='replace', newline='') as f:
        reader = csv.reader(f, delimiter=delim)
        try:
            header = next(reader)
        except StopIteration:
            return []
        headers = [_normalize_header(h) for h in header]
        rows = []
        for row in reader:
            if not row:
                continue
            d = {}
            for i, val in enumerate(row):
                key = headers[i] if i < len(headers) else f'col_{i}'
                d[key] = val.strip()
            rows.append(d)
    return rows


def _find_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in cols:
            return c
    return None


def _to_number(x: str) -> float:
    if x is None:
        return 0.0
    s = x.strip()
    if not s:
        return 0.0
    # Remove commas, currency symbols, and parentheses used for negatives
    s = s.replace(',', '')
    s = s.replace('$', '')
    neg = False
    if s.startswith('(') and s.endswith(')'):
        neg = True
        s = s[1:-1]
    try:
        val = float(s)
        return -val if neg else val
    except ValueError:
        return 0.0


def _norm_text(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


def fuzzy_find_accession(cover_rows: List[Dict[str, str]], query: str) -> Tuple[Optional[Dict[str, str]], float]:
    cols = list(cover_rows[0].keys()) if cover_rows else []
    name_col = _find_col(cols, [
        'manager_name', 'name', 'institution_name', 'filing_manager', 'institutional_investment_manager_name'
    ])
    acc_col = _find_col(cols, ['accession_number', 'accession', 'adsh'])
    form_col = _find_col(cols, ['form_type', 'form'])

    if not name_col or not acc_col:
        return None, 0.0

    qn = _norm_text(query)
    best = None
    best_score = 0.0

    for r in cover_rows:
        rn = _norm_text(r.get(name_col, ''))
        score = difflib.SequenceMatcher(None, qn, rn).ratio()
        # Prefer main 13F-HR filings when scores are close
        form = r.get(form_col, '').upper() if form_col else ''
        if score > best_score or (abs(score - best_score) < 0.02 and form == '13F-HR'):
            best = r
            best_score = score
    return best, best_score


def get_aum_and_holdings(summary_rows: List[Dict[str, str]], holdings_rows: List[Dict[str, str]], accession: str, equity_only: bool = True) -> Dict[str, float]:
    scols = list(summary_rows[0].keys()) if summary_rows else []
    hcols = list(holdings_rows[0].keys()) if holdings_rows else []

    acc_col_s = _find_col(scols, ['accession_number', 'accession', 'adsh'])
    total_col = _find_col(scols, ['table_value_total', 'tablevaluetotal', 'portfolio_value', 'total_value'])

    if not acc_col_s or not total_col:
        raise ValueError('Summary table missing required columns.')

    aum = None
    for r in summary_rows:
        if r.get(acc_col_s) == accession:
            aum = _to_number(r.get(total_col))
            break
    if aum is None:
        raise ValueError('Accession not found in summary table.')

    # Holdings: count unique equity CUSIPs
    acc_col_h = _find_col(hcols, ['accession_number', 'accession', 'adsh'])
    cusip_col = _find_col(hcols, ['cusip', 'cusip_no', 'cusip_number'])
    putcall_col = _find_col(hcols, ['putcall', 'put_call'])
    class_col = _find_col(hcols, ['titleofclass', 'class', 'security_title'])

    if not acc_col_h or not cusip_col:
        raise ValueError('Holdings table missing required columns.')

    equities = set()
    for r in holdings_rows:
        if r.get(acc_col_h) != accession:
            continue
        cusip = r.get(cusip_col, '').strip()
        if len(cusip) < 8:
            continue  # skip malformed
        if equity_only:
            pc = r.get(putcall_col, '').upper() if putcall_col else ''
            cls = r.get(class_col, '')
            if pc in ('PUT', 'CALL'):
                continue
            if cls and re.search(r"warrant|note|debenture|bond|preferred", cls, flags=re.I):
                continue
        equities.add(cusip)

    return {
        'aum': float(aum),
        'equity_holdings_count': float(len(equities)),
    }


def aggregate_holdings_by_cusip(holdings_rows: List[Dict[str, str]], accession: str, equity_only: bool = True) -> Dict[str, float]:
    hcols = list(holdings_rows[0].keys()) if holdings_rows else []
    acc_col = _find_col(hcols, ['accession_number', 'accession', 'adsh'])
    cusip_col = _find_col(hcols, ['cusip', 'cusip_no', 'cusip_number'])
    value_col = _find_col(hcols, ['value', 'market_value', 'mv', 'value_x_1000_', 'value_x_1000'])
    putcall_col = _find_col(hcols, ['putcall', 'put_call'])
    class_col = _find_col(hcols, ['titleofclass', 'class', 'security_title'])

    if not acc_col or not cusip_col or not value_col:
        raise ValueError('Holdings table missing required columns.')

    agg: Dict[str, float] = {}
    for r in holdings_rows:
        if r.get(acc_col) != accession:
            continue
        cusip = r.get(cusip_col, '').strip()
        if len(cusip) < 8:
            continue
        if equity_only:
            pc = r.get(putcall_col, '').upper() if putcall_col else ''
            cls = r.get(class_col, '')
            if pc in ('PUT', 'CALL'):
                continue
            if cls and re.search(r"warrant|note|debenture|bond|preferred", cls, flags=re.I):
                continue
        val = _to_number(r.get(value_col))
        agg[cusip] = agg.get(cusip, 0.0) + val
    return agg


def compare_quarters(holdings_rows_q2: List[Dict[str, str]], accession_q2: str,
                     holdings_rows_q3: List[Dict[str, str]], accession_q3: str,
                     top_n: int = 5) -> List[Tuple[str, float]]:
    agg_q2 = aggregate_holdings_by_cusip(holdings_rows_q2, accession_q2, equity_only=True)
    agg_q3 = aggregate_holdings_by_cusip(holdings_rows_q3, accession_q3, equity_only=True)
    all_cusips = set(agg_q2.keys()) | set(agg_q3.keys())
    deltas: List[Tuple[str, float]] = []
    for c in all_cusips:
        d = agg_q3.get(c, 0.0) - agg_q2.get(c, 0.0)
        if d > 0:
            deltas.append((c, d))
    deltas.sort(key=lambda x: x[1], reverse=True)
    return deltas[:top_n]


def top_holders_for_cusip(holdings_rows: List[Dict[str, str]], cusip: str, top_n: int = 3) -> List[Tuple[str, float]]:
    hcols = list(holdings_rows[0].keys()) if holdings_rows else []
    acc_col = _find_col(hcols, ['accession_number', 'accession', 'adsh'])
    cusip_col = _find_col(hcols, ['cusip', 'cusip_no', 'cusip_number'])
    value_col = _find_col(hcols, ['value', 'market_value', 'mv', 'value_x_1000_', 'value_x_1000'])

    if not acc_col or not cusip_col or not value_col:
        raise ValueError('Holdings table missing required columns.')

    agg_by_acc: Dict[str, float] = {}
    target = cusip.strip().upper()
    for r in holdings_rows:
        c = r.get(cusip_col, '').strip().upper()
        if c != target:
            continue
        acc = r.get(acc_col)
        val = _to_number(r.get(value_col))
        agg_by_acc[acc] = agg_by_acc.get(acc, 0.0) + val

    ranked = sorted(agg_by_acc.items(), key=lambda kv: kv[1], reverse=True)
    return ranked[:top_n]


def map_accessions_to_names(cover_rows: List[Dict[str, str]], acc_list: List[str]) -> Dict[str, str]:
    if not cover_rows:
        return {}
    cols = list(cover_rows[0].keys())
    acc_col = _find_col(cols, ['accession_number', 'accession', 'adsh'])
    name_col = _find_col(cols, ['manager_name', 'name', 'institution_name', 'filing_manager', 'institutional_investment_manager_name'])
    if not acc_col or not name_col:
        return {}
    index = {r.get(acc_col): r.get(name_col) for r in cover_rows}
    return {acc: index.get(acc, '') for acc in acc_list}


def main():
    parser = argparse.ArgumentParser(description='SEC 13F quarterly analysis helper')
    sub = parser.add_subparsers(dest='cmd', required=True)

    # find-accession
    p_find = sub.add_parser('find-accession', help='Fuzzy find accession by manager name')
    p_find.add_argument('--cover', required=True, help='Path to COVERPAGE file')
    p_find.add_argument('--query', required=True, help='Manager/fund name to search')

    # aum-holdings
    p_ah = sub.add_parser('aum-holdings', help='Get AUM and equity holdings count for an accession')
    p_ah.add_argument('--summary', required=True, help='Path to SUMMARY table file')
    p_ah.add_argument('--holdings', required=True, help='Path to HOLDINGS detail file')
    p_ah.add_argument('--accession', required=True, help='Accession number to analyze')

    # compare-fund
    p_cmp = sub.add_parser('compare-fund', help='Compare holdings across two quarters for the same fund')
    p_cmp.add_argument('--holdings-q2', required=True, help='Path to Q2 holdings file')
    p_cmp.add_argument('--accession-q2', required=True, help='Accession number in Q2')
    p_cmp.add_argument('--holdings-q3', required=True, help='Path to Q3 holdings file')
    p_cmp.add_argument('--accession-q3', required=True, help='Accession number in Q3')
    p_cmp.add_argument('--top', type=int, default=5, help='Number of top increases to return')

    # top-holders
    p_top = sub.add_parser('top-holders', help='Rank top managers invested in a CUSIP for a quarter')
    p_top.add_argument('--holdings', required=True, help='Path to HOLDINGS detail file')
    p_top.add_argument('--cover', required=True, help='Path to COVERPAGE file')
    p_top.add_argument('--cusip', required=True, help='Target CUSIP')
    p_top.add_argument('--top', type=int, default=3, help='Number of top managers to return')

    args = parser.parse_args()

    if args.cmd == 'find-accession':
        cover_rows = _read_rows(args.cover)
        match, score = fuzzy_find_accession(cover_rows, args.query)
        if not match:
            print(json.dumps({'error': 'no_match'}))
            return
        print(json.dumps({'match': match, 'score': round(score, 4)}))
        return

    if args.cmd == 'aum-holdings':
        summary_rows = _read_rows(args.summary)
        holdings_rows = _read_rows(args.holdings)
        result = get_aum_and_holdings(summary_rows, holdings_rows, args.accession, equity_only=True)
        print(json.dumps(result))
        return

    if args.cmd == 'compare-fund':
        h_q2 = _read_rows(args.holdings_q2)
        h_q3 = _read_rows(args.holdings_q3)
        deltas = compare_quarters(h_q2, args.accession_q2, h_q3, args.accession_q3, top_n=args.top)
        out = [{'cusip': c, 'delta_value': v} for c, v in deltas]
        print(json.dumps(out))
        return

    if args.cmd == 'top-holders':
        holdings_rows = _read_rows(args.holdings)
        cover_rows = _read_rows(args.cover)
        ranked = top_holders_for_cusip(holdings_rows, args.cusip, top_n=args.top)
        accs = [acc for acc, _ in ranked]
        name_map = map_accessions_to_names(cover_rows, accs)
        out = [{'accession': acc, 'manager_name': name_map.get(acc, ''), 'value': val} for acc, val in ranked]
        print(json.dumps(out))
        return


if __name__ == '__main__':
    main()
