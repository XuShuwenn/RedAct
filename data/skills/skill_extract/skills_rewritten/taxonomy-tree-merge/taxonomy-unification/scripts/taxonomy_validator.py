#!/usr/bin/env python3
"""
Taxonomy Validator: structural and naming checks for a 5-level unified taxonomy.

Validates constraints:
- Top-level category count within a range
- Branching per parent (3–20 children) for levels 1–4
- Name formatting: <= max words, consistent separators
- Parent-child overlap below threshold
- Sibling distinctness (pairwise word overlap below threshold)
- Pyramid shape and source distribution (reported; optional thresholds)

Usage:
  python scripts/taxonomy_validator.py --full unified_taxonomy_full.csv [--hierarchy unified_taxonomy_hierarchy.csv]
  python scripts/taxonomy_validator.py --full unified_taxonomy_full.csv \
      --min-top-level 10 --max-top-level 20 \
      --min-branch 3 --max-branch 20 \
      --parent-child-overlap-threshold 0.0 \
      --sibling-overlap-threshold 0.3 \
      --max-name-words 5 \
      --json
"""

import argparse
import csv
import itertools
import json
import math
import os
import re
import sys
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set

LEVEL_COLS = [f"unified_level_{i}" for i in range(1, 6)]
RE_WORD = re.compile(r"[A-Za-z0-9]+", re.UNICODE)
STOPWORDS = {
    'a','an','and','or','the','for','of','to','with','in','on','by','at','from','as','is','are','be'
}


def read_csv_rows(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: (v if v is not None else '') for k, v in r.items()})
    return rows


def normalize_name(name: str) -> str:
    if name is None:
        return ''
    s = name.strip()
    # Normalize unicode-like spaces and repeated separators
    s = re.sub(r"\s+", " ", s)
    s = s.strip()
    return s


def name_words(name: str) -> List[str]:
    s = normalize_name(name).lower()
    # Treat '|' as a separator but do not remove its surrounding spaces for counting
    s = s.replace('|', ' ')
    tokens = RE_WORD.findall(s)
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


def words_set(name: str) -> Set[str]:
    return set(name_words(name))


def pair_overlap_ratio(a_words: Set[str], b_words: Set[str]) -> float:
    if not a_words or not b_words:
        return 0.0
    inter = len(a_words & b_words)
    denom = min(len(a_words), len(b_words))
    if denom == 0:
        return 0.0
    return inter / denom


def child_overlap_ratio(parent_words: Set[str], child_words: Set[str]) -> float:
    if not child_words:
        return 0.0
    inter = len(parent_words & child_words)
    return inter / len(child_words)


def distinct_nonempty(values: List[str]) -> Set[str]:
    return {normalize_name(v) for v in values if normalize_name(v)}


def validate(full_path: str,
             hierarchy_path: str = None,
             min_top_level: int = 10,
             max_top_level: int = 20,
             min_branch: int = 3,
             max_branch: int = 20,
             parent_child_overlap_threshold: float = 0.0,
             sibling_overlap_threshold: float = 0.3,
             max_name_words: int = 5,
             min_sources_per_top: int = 1,
             json_mode: bool = False) -> Tuple[bool, Dict]:

    report: Dict = {
        'checks': {},
        'metrics': {},
        'warnings': [],
        'notes': []
    }

    # Load mapping
    rows = read_csv_rows(full_path)
    if not rows:
        report['checks']['file_nonempty'] = {'pass': False, 'detail': 'Full mapping file has no rows.'}
        return False, report

    # Required columns
    required_cols = {'source', 'category_path', 'depth'} | set(LEVEL_COLS)
    missing = [c for c in required_cols if c not in rows[0]]
    if missing:
        report['checks']['columns_present'] = {'pass': False, 'detail': f'Missing columns: {missing}'}
        return False, report
    report['checks']['columns_present'] = {'pass': True}

    # Gather structures
    all_names = set()
    level_nodes: List[Set[str]] = [set() for _ in range(5)]
    parent_to_children: Dict[Tuple[str, ...], Set[str]] = defaultdict(set)
    source_per_top: Dict[str, Set[str]] = defaultdict(set)  # top_name -> sources present
    parent_child_edges: Set[Tuple[int, str, str]] = set()  # (level, parent, child)

    for r in rows:
        levels = [normalize_name(r.get(c, '')) for c in LEVEL_COLS]
        src = normalize_name(r.get('source', ''))
        # Record level nodes and all names
        for i, name in enumerate(levels):
            if name:
                level_nodes[i].add(name)
                all_names.add(name)
        # Top-level source coverage
        if levels[0]:
            if src:
                source_per_top[levels[0]].add(src)
        # Parent->children mapping per path (use full parent path for uniqueness)
        for i in range(len(levels)-1):
            parent_path = tuple([n for n in levels[:i+1] if n])
            child = levels[i+1]
            parent = levels[i]
            if parent_path and child:
                parent_to_children[parent_path].add(child)
                parent_child_edges.add((i+1, parent, child))

    # Metrics: counts per level
    level_counts = [len(nodes) for nodes in level_nodes]
    report['metrics']['level_counts'] = {f'L{i+1}': level_counts[i] for i in range(5)}

    # Check 1: Top-level count
    top_count = level_counts[0]
    ck1 = (min_top_level <= top_count <= max_top_level)
    report['checks']['top_level_count'] = {
        'pass': ck1,
        'detail': f'{top_count} (required {min_top_level}..{max_top_level})'
    }

    # Check 2: Branching per parent (levels 1..4)
    branching_violations = []
    for parent_path, children in parent_to_children.items():
        # parent level is len(parent_path)
        parent_level = len(parent_path)
        if parent_level >= 5:
            continue
        # If there are children, enforce limits
        child_count = len(distinct_nonempty(list(children)))
        if child_count > 0:
            if child_count < min_branch or child_count > max_branch:
                branching_violations.append({
                    'parent_path': list(parent_path),
                    'level': parent_level,
                    'child_count': child_count
                })
    report['checks']['branching_limits'] = {
        'pass': len(branching_violations) == 0,
        'violations': branching_violations[:50],  # limit preview
        'total_violations': len(branching_violations)
    }

    # Check 3: Name word count and formatting
    too_long_names = []
    bad_sep_names = []
    for name in all_names:
        tokens = name_words(name)
        if len(tokens) > max_name_words:
            too_long_names.append({'name': name, 'words': len(tokens)})
        if '|' in name and ' | ' not in name:
            bad_sep_names.append({'name': name})
    report['checks']['name_length'] = {
        'pass': len(too_long_names) == 0,
        'violations': too_long_names[:50],
        'total_violations': len(too_long_names)
    }
    # Separator style is advisory (warning) unless enforced externally
    if bad_sep_names:
        report['warnings'].append({'separator_style': f"{len(bad_sep_names)} names use '|' without spaces; consider ' | ' for readability."})

    # Check 4: Parent-child overlap
    pc_violations = []
    for lvl, parent, child in parent_child_edges:
        pw = words_set(parent)
        cw = words_set(child)
        ratio = child_overlap_ratio(pw, cw)
        if ratio > parent_child_overlap_threshold:
            pc_violations.append({'level': lvl, 'parent': parent, 'child': child, 'overlap': round(ratio, 3)})
    report['checks']['parent_child_overlap'] = {
        'pass': len(pc_violations) == 0,
        'violations': pc_violations[:50],
        'total_violations': len(pc_violations),
        'threshold': parent_child_overlap_threshold
    }

    # Check 5: Sibling distinctness
    sib_violations = []
    for parent_path, children in parent_to_children.items():
        child_list = sorted(distinct_nonempty(list(children)))
        words_map = {c: words_set(c) for c in child_list}
        for a, b in itertools.combinations(child_list, 2):
            r = pair_overlap_ratio(words_map[a], words_map[b])
            if r > sibling_overlap_threshold:
                sib_violations.append({
                    'parent_path': list(parent_path),
                    'a': a,
                    'b': b,
                    'overlap': round(r, 3)
                })
    report['checks']['sibling_distinctness'] = {
        'pass': len(sib_violations) == 0,
        'violations': sib_violations[:50],
        'total_violations': len(sib_violations),
        'threshold': sibling_overlap_threshold
    }

    # Advisory: Pyramid shape
    shape_nonmonotonic = []
    for i in range(4):
        if level_counts[i] > 0 and level_counts[i+1] > 0 and level_counts[i] > level_counts[i+1]:
            shape_nonmonotonic.append({'level': i+1, 'next_level': i+2, 'counts': (level_counts[i], level_counts[i+1])})
    if shape_nonmonotonic:
        report['warnings'].append({'pyramid_shape': shape_nonmonotonic})

    # Advisory: Source distribution across top-level
    top_coverage = [len(srcs) for _, srcs in source_per_top.items()]
    if top_coverage:
        report['metrics']['top_level_source_coverage'] = {
            'min_sources_in_top': int(min(top_coverage)),
            'max_sources_in_top': int(max(top_coverage)),
            'avg_sources_in_top': round(sum(top_coverage)/len(top_coverage), 3)
        }
        below = [c for c in top_coverage if c < min_sources_per_top]
        if below:
            report['warnings'].append({'source_distribution': f"{len(below)} top-level categories have < {min_sources_per_top} sources represented"})

    # Overall pass = all hard checks pass
    overall = all(
        report['checks'][k]['pass']
        for k in ['columns_present', 'top_level_count', 'branching_limits', 'name_length', 'parent_child_overlap', 'sibling_distinctness']
    )
    report['overall_pass'] = overall

    return overall, report


def main():
    ap = argparse.ArgumentParser(description='Validate a unified taxonomy against structural and naming constraints.')
    ap.add_argument('--full', required=True, help='Path to unified_taxonomy_full.csv')
    ap.add_argument('--hierarchy', help='Path to unified_taxonomy_hierarchy.csv (optional)')
    ap.add_argument('--min-top-level', type=int, default=10)
    ap.add_argument('--max-top-level', type=int, default=20)
    ap.add_argument('--min-branch', type=int, default=3)
    ap.add_argument('--max-branch', type=int, default=20)
    ap.add_argument('--parent-child-overlap-threshold', type=float, default=0.0)
    ap.add_argument('--sibling-overlap-threshold', type=float, default=0.3)
    ap.add_argument('--max-name-words', type=int, default=5)
    ap.add_argument('--min-sources-per-top', type=int, default=1, help='Advisory: minimum sources represented per top-level category')
    ap.add_argument('--json', action='store_true', help='Emit JSON report')
    args = ap.parse_args()

    overall, report = validate(
        full_path=args.full,
        hierarchy_path=args.hierarchy,
        min_top_level=args.min_top_level,
        max_top_level=args.max_top_level,
        min_branch=args.min_branch,
        max_branch=args.max_branch,
        parent_child_overlap_threshold=args.parent_child_overlap_threshold,
        sibling_overlap_threshold=args.sibling_overlap_threshold,
        max_name_words=args.max_name_words,
        min_sources_per_top=args.min_sources_per_top,
        json_mode=args.json,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Taxonomy Validation Summary")
        print("===========================")
        for k, v in report['checks'].items():
            status = 'PASS' if v.get('pass') else 'FAIL'
            detail = v.get('detail')
            total = v.get('total_violations')
            print(f"- {k}: {status}")
            if detail:
                print(f"  detail: {detail}")
            if total is not None:
                print(f"  violations: {total}")
        if report['warnings']:
            print("\nWarnings:")
            for w in report['warnings']:
                print(f"- {w}")
        if report.get('metrics'):
            print("\nMetrics:")
            for mk, mv in report['metrics'].items():
                print(f"- {mk}: {mv}")
        print(f"\nOVERALL: {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
