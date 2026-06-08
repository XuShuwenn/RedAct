#!/usr/bin/env python3
"""
statem_guard_audit.py

Audit Erlang gen_statem-style handlers to ensure privileged internal events
(e.g., {conn_msg, ...}) are guarded by authentication checks.

Usage examples:
  python scripts/statem_guard_audit.py --root /path/to/src \
      --events "{conn_msg" --require-guard CONNECTED authenticated

  python scripts/statem_guard_audit.py --files file1.erl file2.erl \
      --events "{conn_msg" "channel_request" --require-guard CONNECTED

Notes:
- This is a lightweight static scan based on regex; it won't parse Erlang AST.
- It is best-effort: review flagged results manually.
"""

import argparse
import os
import re
import sys
from typing import List, Tuple

HANDLE_EVENT_RE = re.compile(r"(^|\n)\s*handle_event\s*\((.*?)\)\s*(when\s*(.*?)\s*)?->", re.S)
CLAUSE_HEAD_RE = re.compile(r"handle_event\s*\((.*?)\)\s*(when\s*(.*?)\s*)?->", re.S)


def read_file(p: str) -> str:
    try:
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"ERROR: cannot read {p}: {e}", file=sys.stderr)
        return ""


def find_clauses(src: str) -> List[Tuple[int, str, str]]:
    """Return list of (line_no, head_text, guard_text)."""
    results = []
    for m in HANDLE_EVENT_RE.finditer(src):
        start = m.start()
        # Extract one clause head and guard
        head_guard = CLAUSE_HEAD_RE.search(src, pos=start, endpos=m.end())
        if not head_guard:
            continue
        head_text = head_guard.group(1) or ""
        guard_text = head_guard.group(3) or ""
        line_no = src.count("\n", 0, start) + 1
        results.append((line_no, head_text, guard_text))
    return results


def clause_mentions_event(head_text: str, events: List[str]) -> bool:
    ht = head_text.replace("\n", " ")
    return any(ev in ht for ev in events)


def guard_has_tokens(guard_text: str, tokens: List[str]) -> bool:
    gt = guard_text.replace("\n", " ")
    return all(tok in gt for tok in tokens) if tokens else (guard_text.strip() != "")


def audit_file(path: str, events: List[str], require_guard: List[str]) -> List[str]:
    src = read_file(path)
    if not src:
        return []
    reports = []
    for line_no, head_text, guard_text in find_clauses(src):
        if clause_mentions_event(head_text, events):
            has_guard = guard_has_tokens(guard_text, require_guard)
            if not has_guard:
                snippet = head_text.strip().split("\n")[0]
                reports.append(
                    f"{path}:{line_no}: Unguarded handle_event clause for target event. Head: {snippet}"
                )
    return reports


def collect_files(root: str, files: List[str]) -> List[str]:
    if files:
        return [f for f in files if os.path.isfile(f)]
    out = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith('.erl'):
                out.append(os.path.join(dirpath, fn))
    return out


def main():
    ap = argparse.ArgumentParser(description="Audit Erlang statem handlers for authentication guards")
    ap.add_argument('--root', default='.', help='Root directory to scan (ignored if --files provided)')
    ap.add_argument('--files', nargs='*', help='Specific Erlang files to scan')
    ap.add_argument('--events', nargs='+', required=True, help='Head tokens indicating target events (e.g., "{conn_msg" )')
    ap.add_argument('--require-guard', nargs='*', default=[], help='Guard tokens that must appear (e.g., CONNECTED authenticated)')
    args = ap.parse_args()

    files = collect_files(args.root, args.files or [])
    any_issue = False
    for p in files:
        reps = audit_file(p, args.events, args.require_guard)
        for r in reps:
            any_issue = True
            print(r)
    if any_issue:
        sys.exit(2)


if __name__ == '__main__':
    main()
