#!/usr/bin/env python3
"""
Validate unified taxonomy outputs for structure and naming rules.

Usage:
  python scripts/validate_taxonomy.py --full unified_taxonomy_full.csv --hierarchy unified_taxonomy_hierarchy.csv

Checks performed:
  1) Top-level count: 10–20 categories
  2) Children per parent (levels 2–5): prefers 3–20 per parent and reports compliance
  3) Naming constraints: ' | ' separator within names, <=5 terms
  4) No parent-child name token overlap
  5) Sibling distinctness: <30% token overlap (Jaccard) for most pairs
  6) Pyramid balance: unique category counts by level
  7) Source distribution across levels

This script is dataset-agnostic and does not depend on external models.
"""

import argparse
import sys
import pandas as pd
import re
from collections import defaultdict

STOPWORDS = set(
    [
        'and','or','for','of','the','a','an','to','on','in','by','with','at','from','&',
        'misc','other','general','all'
    ]
)


def tokenize_name(name: str):
    if not isinstance(name, str):
        return set()
    # convert intra-name separator to space
    text = name.replace(' | ', ' ')
    # keep alphanumerics and space
    text = re.sub(r"[^0-9a-zA-Z\s]+", " ", text.lower())
    tokens = [t for t in text.split() if t and t not in STOPWORDS]
    return set(tokens)


def check_top_level(df_full):
    l1 = df_full['unified_level_1'].dropna().unique()
    n = len(l1)
    status = 'PASS' if 10 <= n <= 20 else 'FAIL'
    return {
        'rule': 'Top-level category count (10–20)',
        'actual_count': int(n),
        'status': status,
        'categories_preview': sorted(l1)[:20],
    }


def children_stats(df_full, parent_col, child_col):
    pc = df_full.dropna(subset=[parent_col, child_col]).groupby(parent_col)[child_col].nunique()
    if pc.empty:
        return None
    return {
        'min_children': int(pc.min()),
        'max_children': int(pc.max()),
        'avg_children': float(pc.mean()),
        'parents_count': int(len(pc)),
        'compliance_ge_3': float(((pc >= 3) & (pc <= 20)).sum() / len(pc)) if len(pc) else 0.0,
    }


def check_children(df_full):
    details = {}
    for level in range(2, 6):
        parent_col = f'unified_level_{level-1}'
        child_col = f'unified_level_{level}'
        if parent_col not in df_full.columns or child_col not in df_full.columns:
            continue
        stats = children_stats(df_full, parent_col, child_col)
        if stats:
            details[f'L{level-1}->L{level}'] = stats
    return {
        'rule': 'Children per parent (3–20 preferred)',
        'levels': details,
    }


def check_naming(df_hier, max_terms=5):
    max_found = 0
    violations = 0
    examined = 0
    for level in range(1, 6):
        col = f'unified_level_{level}'
        if col not in df_hier.columns:
            continue
        vals = df_hier[col].dropna().unique()
        for v in vals:
            examined += 1
            terms = v.split(' | ')
            max_found = max(max_found, len(terms))
            if len(terms) > max_terms:
                violations += 1
    status = 'PASS' if violations == 0 and max_found <= max_terms else 'FAIL'
    return {
        'rule': 'Naming format (" | " separator, ≤5 terms)',
        'max_terms_found': int(max_found),
        'violations': int(violations),
        'examined_names': int(examined),
        'status': status,
    }


def check_parent_child_overlap(df_hier):
    overlap_pairs = 0
    checked = 0
    for level in range(1, 5):
        pcol = f'unified_level_{level}'
        ccol = f'unified_level_{level+1}'
        if pcol not in df_hier.columns or ccol not in df_hier.columns:
            continue
        subset = df_hier.dropna(subset=[pcol, ccol])
        for _, row in subset.iterrows():
            p_tokens = tokenize_name(row[pcol])
            c_tokens = tokenize_name(row[ccol])
            if not p_tokens or not c_tokens:
                continue
            checked += 1
            if p_tokens & c_tokens:
                overlap_pairs += 1
    status = 'PASS' if overlap_pairs == 0 else 'WARN'
    return {
        'rule': 'No parent-child token overlap',
        'checked_pairs': int(checked),
        'overlap_pairs': int(overlap_pairs),
        'status': status,
    }


def jaccard(a:set, b:set):
    if not a and not b:
        return 0.0
    u = a | b
    if not u:
        return 0.0
    return len(a & b) / len(u)


def check_sibling_distinctness(df_hier, threshold=0.30):
    total_pairs = 0
    violations = 0
    for level in range(1, 5):
        pcol = f'unified_level_{level}'
        ccol = f'unified_level_{level+1}'
        if pcol not in df_hier.columns or ccol not in df_hier.columns:
            continue
        sub = df_hier.dropna(subset=[pcol, ccol])
        if sub.empty:
            continue
        groups = sub.groupby(pcol)[ccol].apply(list)
        for _, children in groups.items():
            toks = [tokenize_name(c) for c in children if isinstance(c, str)]
            n = len(toks)
            for i in range(n):
                for j in range(i+1, n):
                    total_pairs += 1
                    if jaccard(toks[i], toks[j]) >= threshold:
                        violations += 1
    status = 'PASS' if total_pairs == 0 or violations <= total_pairs * 0.10 else 'WARN'
    return {
        'rule': f'Sibling distinctness (<{int(threshold*100)}% token overlap)',
        'sibling_pairs_checked': int(total_pairs),
        'pairs_violating_threshold': int(violations),
        'status': status,
    }


def check_pyramid(df_hier):
    counts = {}
    for level in range(1, 6):
        col = f'unified_level_{level}'
        if col in df_hier.columns:
            counts[f'L{level}'] = int(df_hier[col].dropna().nunique())
    return {
        'rule': 'Pyramid structure (unique categories by level)',
        'unique_counts': counts,
    }


def check_source_distribution(df_full):
    result = defaultdict(dict)
    if 'source' not in df_full.columns:
        return {
            'rule': 'Source distribution',
            'status': 'WARN',
            'note': 'source column not found',
        }
    for src in sorted(df_full['source'].dropna().unique()):
        src_df = df_full[df_full['source'] == src]
        for level in range(1, 6):
            col = f'unified_level_{level}'
            if col in df_full.columns:
                result[src][f'L{level}'] = int(src_df[col].dropna().nunique())
    return {
        'rule': 'Source distribution across levels',
        'breakdown': result,
    }


def main():
    ap = argparse.ArgumentParser(description='Validate unified taxonomy CSVs')
    ap.add_argument('--full', required=True, help='Path to unified_taxonomy_full.csv')
    ap.add_argument('--hierarchy', required=True, help='Path to unified_taxonomy_hierarchy.csv')
    args = ap.parse_args()

    try:
        df_full = pd.read_csv(args.full)
        df_hier = pd.read_csv(args.hierarchy)
    except Exception as e:
        print(f'ERROR: failed to read inputs: {e}', file=sys.stderr)
        sys.exit(1)

    print('='*80)
    print('UNIFIED TAXONOMY VALIDATION')
    print('='*80)

    # Rule 1: Top level
    r1 = check_top_level(df_full)
    print(f"\n- {r1['rule']}")
    print(f"  Actual: {r1['actual_count']}  Status: {r1['status']}")

    # Rule 2: Children per parent
    r2 = check_children(df_full)
    print(f"\n- {r2['rule']}")
    for k, v in r2['levels'].items():
        print(f"  {k}: min={v['min_children']}, max={v['max_children']}, avg={v['avg_children']:.1f}, compliance(3–20)={v['compliance_ge_3']*100:.1f}% (parents={v['parents_count']})")

    # Rule 3: Naming format
    r3 = check_naming(df_hier)
    print(f"\n- {r3['rule']}")
    print(f"  Max terms found: {r3['max_terms_found']}  Violations: {r3['violations']}  Status: {r3['status']}")

    # Rule 4: Parent-child overlap
    r4 = check_parent_child_overlap(df_hier)
    print(f"\n- {r4['rule']}")
    print(f"  Checked pairs: {r4['checked_pairs']}  Overlaps: {r4['overlap_pairs']}  Status: {r4['status']}")

    # Rule 5: Sibling distinctness
    r5 = check_sibling_distinctness(df_hier)
    print(f"\n- {r5['rule']}")
    print(f"  Sibling pairs checked: {r5['sibling_pairs_checked']}  Violations: {r5['pairs_violating_threshold']}  Status: {r5['status']}")

    # Rule 6: Pyramid balance
    r6 = check_pyramid(df_hier)
    print(f"\n- {r6['rule']}")
    for lvl, cnt in r6['unique_counts'].items():
        print(f"  {lvl}: {cnt} unique categories")

    # Rule 7: Source distribution
    r7 = check_source_distribution(df_full)
    print(f"\n- {r7['rule']}")
    if 'breakdown' in r7:
        for src, levels in r7['breakdown'].items():
            line = ' '.join([f"{lvl}={cnt}" for lvl, cnt in sorted(levels.items())])
            print(f"  {src}: {line}")
    else:
        print(f"  {r7.get('status','')}: {r7.get('note','')}")

    print('\n' + '='*80)
    print('VALIDATION COMPLETE')
    print('='*80)

if __name__ == '__main__':
    main()
