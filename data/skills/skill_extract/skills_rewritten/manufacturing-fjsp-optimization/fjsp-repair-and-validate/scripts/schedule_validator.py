#!/usr/bin/env python3
"""
Generic schedule validator for flexible job shop repair tasks.

Validates:
- Precedence: within each job, op k must start >= end of op k-1
- Machine capacity: no overlaps per machine
- Downtime: no overlap of any operation interval with downtime windows
- Budgets (optional, if baseline and policy provided):
  * Machine changes: count of ops where scheduled machine != baseline machine
  * L1 start shift: sum over ops of |scheduled start - baseline start|
  * Makespan guard: schedule makespan <= baseline_makespan * guard (if provided)
- Output consistency: JSON schedule matches CSV rows exactly

Usage:
  python scripts/schedule_validator.py \
      --schedule-json /path/to/solution.json \
      --schedule-csv /path/to/schedule.csv \
      --downtime-csv /path/to/downtime.csv \
      --baseline-json /path/to/baseline.json \
      --policy-json /path/to/policy.json

All arguments except schedule-json and downtime-csv are optional but recommended.
Exits with code 0 on success, 1 on any validation failure.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

Interval = Tuple[float, float]


def read_json(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def read_downtime_csv(path: str) -> Dict[int, List[Interval]]:
    dt: Dict[int, List[Interval]] = defaultdict(list)
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        # Expect columns: machine,start,end (case-insensitive allowed)
        for row in reader:
            try:
                m = int(row.get('machine') or row.get('MACHINE') or row.get('Machine'))
                s = float(row.get('start') or row.get('START') or row.get('Start'))
                e = float(row.get('end') or row.get('END') or row.get('End'))
            except Exception:
                raise ValueError('Downtime CSV must have numeric machine,start,end columns')
            if e <= s:
                raise ValueError(f'Downtime window has non-positive length: machine={m}, start={s}, end={e}')
            dt[m].append((s, e))
    # Sort for efficiency
    for m in dt:
        dt[m].sort()
    return dt


def schedule_from_json(sol: dict) -> List[dict]:
    if 'schedule' not in sol:
        raise ValueError('schedule-json missing "schedule" key')
    sched = []
    for row in sol['schedule']:
        try:
            sched.append({
                'job': int(row['job']),
                'op': int(row['op']),
                'machine': int(row['machine']),
                'start': float(row['start']),
                'end': float(row['end']),
                'dur': float(row['dur']),
            })
        except Exception:
            raise ValueError('schedule-json contains non-numeric fields or missing keys')
    return sched


def read_csv_schedule(path: str) -> List[dict]:
    items = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        expected = {'job', 'op', 'machine', 'start', 'end', 'dur'}
        if set(reader.fieldnames or []) != expected:
            raise ValueError(f'schedule.csv must have columns exactly {sorted(expected)}')
        for row in reader:
            items.append({
                'job': int(row['job']),
                'op': int(row['op']),
                'machine': int(row['machine']),
                'start': float(row['start']),
                'end': float(row['end']),
                'dur': float(row['dur'])
            })
    return items


def intervals_overlap(a: Interval, b: Interval) -> bool:
    # half-open [s,e)
    return a[0] < b[1] and a[1] > b[0]


def validate_precedence(schedule: List[dict]) -> List[str]:
    errs = []
    # For each job, map op -> (start,end)
    by_job: Dict[int, Dict[int, Tuple[float, float]]] = defaultdict(dict)
    for r in schedule:
        by_job[r['job']][r['op']] = (r['start'], r['end'])
    for job, ops in by_job.items():
        max_op = max(ops)
        for k in range(1, max_op + 1):
            if k not in ops or (k-1) not in ops:
                errs.append(f'Precedence data missing for job {job}, op {k} or {k-1}')
                continue
            prev_end = ops[k-1][1]
            start_k = ops[k][0]
            if start_k < prev_end - 1e-9:
                errs.append(f'Precedence violation: job {job} op {k} starts {start_k} before prev end {prev_end}')
    return errs


def validate_capacity(schedule: List[dict]) -> List[str]:
    errs = []
    by_machine: Dict[int, List[Interval]] = defaultdict(list)
    for r in schedule:
        by_machine[r['machine']].append((r['start'], r['end']))
    for m, intervals in by_machine.items():
        # sort by start and check neighbors
        intervals.sort()
        for i in range(1, len(intervals)):
            if intervals_overlap(intervals[i-1], intervals[i]):
                errs.append(f'Machine {m} overlap between {intervals[i-1]} and {intervals[i]}')
    return errs


def validate_downtime(schedule: List[dict], downtime: Dict[int, List[Interval]]) -> List[str]:
    errs = []
    for r in schedule:
        m = r['machine']
        seg = (r['start'], r['end'])
        for win in downtime.get(m, []):
            if intervals_overlap(seg, win):
                errs.append(f'Downtime violation: job {r['job']} op {r['op']} on machine {m} overlaps {win}')
                break
    return errs


def compute_makespan(schedule: List[dict]) -> float:
    return max((r['end'] for r in schedule), default=0.0)


def compute_budgets(schedule: List[dict], baseline: List[dict]) -> Dict[str, float]:
    # Build maps keyed by (job,op)
    S = {(r['job'], r['op']): r for r in schedule}
    B = {(r['job'], r['op']): r for r in baseline}
    missing = [(k) for k in B.keys() if k not in S]
    if missing:
        raise ValueError(f'Schedule missing operations present in baseline: {missing[:5]}...')
    machine_changes = 0
    l1_shift = 0.0
    for key, b in B.items():
        s = S[key]
        if int(s['machine']) != int(b['machine']):
            machine_changes += 1
        l1_shift += abs(float(s['start']) - float(b['start']))
    return {"machine_changes": machine_changes, "l1_shift": l1_shift}


def apply_policy_checks(policy: dict, sched_ms: float, base_ms: float, budgets: Dict[str, float]) -> List[str]:
    errs = []
    # Optional fields: max_machine_changes, max_l1_shift, makespan_guard
    mmc = policy.get('max_machine_changes')
    if mmc is not None and budgets['machine_changes'] > mmc:
        errs.append(f'Machine changes {budgets['machine_changes']} exceed limit {mmc}')
    mls = policy.get('max_l1_shift') or policy.get('max_total_shift')
    if mls is not None and budgets['l1_shift'] > mls:
        errs.append(f'L1 shift {budgets['l1_shift']} exceeds limit {mls}')
    guard = policy.get('makespan_guard')
    if guard is not None and base_ms is not None:
        if sched_ms > guard * base_ms + 1e-9:
            errs.append(f'Makespan {sched_ms} exceeds guard {guard} * baseline {base_ms}')
    return errs


def compare_json_csv(json_sched: List[dict], csv_sched: List[dict]) -> List[str]:
    errs = []
    if len(json_sched) != len(csv_sched):
        errs.append(f'Row count mismatch JSON {len(json_sched)} vs CSV {len(csv_sched)}')
        return errs
    # Compare row-wise after sorting on (job,op)
    key = lambda r: (r['job'], r['op'])
    a = sorted(json_sched, key=key)
    b = sorted(csv_sched, key=key)
    for i, (ra, rb) in enumerate(zip(a, b)):
        for fld in ('job', 'op', 'machine', 'start', 'end', 'dur'):
            va, vb = ra[fld], rb[fld]
            if fld in ('start', 'end', 'dur'):
                if abs(float(va) - float(vb)) > 1e-9:
                    errs.append(f'Row {i} field {fld} mismatch: {va} vs {vb}')
            else:
                if int(va) != int(vb):
                    errs.append(f'Row {i} field {fld} mismatch: {va} vs {vb}')
    return errs


def main():
    p = argparse.ArgumentParser(description='Validate FJSP schedule outputs against downtime and policy budgets')
    p.add_argument('--schedule-json', required=True)
    p.add_argument('--schedule-csv', required=False)
    p.add_argument('--downtime-csv', required=True)
    p.add_argument('--baseline-json', required=False)
    p.add_argument('--policy-json', required=False)
    args = p.parse_args()

    try:
        sol = read_json(args.schedule_json)
        schedule = schedule_from_json(sol)
        downtime = read_downtime_csv(args.downtime_csv)
        csv_sched = read_csv_schedule(args.schedule_csv) if args.schedule_csv else None
        baseline = None
        if args.baseline_json:
            base = read_json(args.baseline_json)
            baseline = schedule_from_json(base) if 'schedule' in base else schedule_from_json({'schedule': base})
        policy = read_json(args.policy_json) if args.policy_json else {}
    except Exception as e:
        print(f'ERROR: failed to load inputs: {e}', file=sys.stderr)
        sys.exit(1)

    errors: List[str] = []

    # Output consistency
    if csv_sched is not None:
        errors += compare_json_csv(schedule, csv_sched)

    # Feasibility checks
    errors += validate_precedence(schedule)
    errors += validate_capacity(schedule)
    errors += validate_downtime(schedule, downtime)

    # Makespan recompute
    sched_ms = compute_makespan(schedule)
    # If solution.json provides makespan, verify consistency
    if 'makespan' in sol:
        try:
            reported = float(sol['makespan'])
            if abs(reported - sched_ms) > 1e-9:
                errors.append(f'Makespan mismatch: reported {reported} vs computed {sched_ms}')
        except Exception:
            errors.append('Reported makespan is not numeric')

    # Budgets (optional)
    if baseline is not None:
        try:
            budgets = compute_budgets(schedule, baseline)
            base_ms = compute_makespan(baseline)
            errors += apply_policy_checks(policy, sched_ms, base_ms, budgets)
        except Exception as e:
            errors.append(f'Budget computation failed: {e}')

    if errors:
        print('VALIDATION FAILED:')
        for e in errors:
            print(f' - {e}')
        sys.exit(1)
    else:
        print('VALIDATION PASSED')
        print(f'Computed makespan: {sched_ms}')
        if baseline is not None:
            budgets = compute_budgets(schedule, baseline)
            print(f"Machine changes: {budgets['machine_changes']}")
            print(f"Total L1 shift: {budgets['l1_shift']}")
        sys.exit(0)


if __name__ == '__main__':
    main()
