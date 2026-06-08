#!/usr/bin/env python3
"""
Reusable helpers for repairing flexible job shop (FJSP) baselines under
machine downtime and policy budgets.

This module does not assume file paths; it operates on in-memory data
structures so it can be integrated into various environments.

Data shape expectations:
- allowed: dict mapping (job, op) -> {machine: duration, ...}
- baseline_schedule: list of dicts with keys: job, op, machine, start, end, dur
- downtime: dict mapping machine -> list of (start, end) half-open intervals
- policy: dict with at least keys:
  - change_budget: {"max_machine_changes": int, "max_total_start_shift_L1": int}
  - guards: {"max_makespan_ratio": float} (optional)
  - freeze: {"enabled": bool, "freeze_until": int, "lock_fields": [..]} (optional)

Functions:
- overlap, has_conflict, earliest_feasible_time
- precedence_aware_order
- schedule_greedy
- enumerate_assignments (optional small-instance search)
- validate_schedule
"""
from typing import Dict, List, Tuple, Any
from collections import defaultdict

Interval = Tuple[int, int]


def normalize_downtime(downtime: Dict[int, List[Interval]]) -> Dict[int, List[Interval]]:
    for m in downtime:
        downtime[m] = sorted(downtime[m])
    return downtime


def overlap(s: int, e: int, a: int, b: int) -> bool:
    """Return True if [s,e) overlaps [a,b)."""
    return s < b and a < e


def has_conflict(m: int, st: int, en: int,
                 machine_intervals: Dict[int, List[Interval]],
                 downtime: Dict[int, List[Interval]]) -> bool:
    for a, b in machine_intervals.get(m, []):
        if overlap(st, en, a, b):
            return True
    for a, b in downtime.get(m, []):
        if overlap(st, en, a, b):
            return True
    return False


def earliest_feasible_time(m: int, anchor: int, dur: int,
                           machine_intervals: Dict[int, List[Interval]],
                           downtime: Dict[int, List[Interval]],
                           safety: int = 200000) -> int:
    """Find the earliest t >= anchor such that [t,t+dur) has no conflicts on machine m.
    Use half-open intervals and linear scan. For moderate horizons this is robust and simple.
    """
    t = int(anchor)
    for _ in range(safety):
        if not has_conflict(m, t, t + dur, machine_intervals, downtime):
            return t
        t += 1
    return t  # Fallback; caller should still validate


def precedence_aware_order(baseline_schedule: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
    """Sort operations by (op index, baseline start, baseline array index)."""
    base_index = {(r["job"], r["op"]): i for i, r in enumerate(baseline_schedule)}
    base_map = {(r["job"], r["op"]): r for r in baseline_schedule}
    keys = list(base_map.keys())
    keys.sort(key=lambda k: (k[1], base_map[k]["start"], base_index[k]))
    return keys


def build_frozen_set(baseline_schedule: List[Dict[str, Any]],
                     downtime: Dict[int, List[Interval]],
                     freeze_cfg: Dict[str, Any]) -> set:
    """Return set of (job, op) to treat as frozen, using baseline array order.
    Exclude ops that would violate downtime at their baseline start/end.
    """
    froz = set()
    if not freeze_cfg or not freeze_cfg.get("enabled"):
        return froz
    N = freeze_cfg.get("freeze_until", 0)
    lock_fields = set(freeze_cfg.get("lock_fields", []))
    if not ("machine" in lock_fields and "start" in lock_fields):
        return froz
    for i in range(min(N, len(baseline_schedule))):
        rec = baseline_schedule[i]
        m = rec["machine"]
        st, en = rec["start"], rec["end"]
        # Only keep frozen if it doesn't violate downtime. Conflicting frozen ops will be repaired.
        violates = False
        for a, b in downtime.get(m, []):
            if overlap(st, en, a, b):
                violates = True
                break
        if not violates:
            froz.add((rec["job"], rec["op"]))
    return froz


def schedule_greedy(allowed: Dict[Tuple[int, int], Dict[int, int]],
                    baseline_schedule: List[Dict[str, Any]],
                    downtime: Dict[int, List[Interval]],
                    policy: Dict[str, Any],
                    anchor_policy: str = "baseline",  # "baseline" or "precedence-only-for-non-frozen"
                    prioritize: str = "start_then_shift_then_mc",
                    ) -> Dict[str, Any]:
    """Repair schedule greedily under budgets and downtime.

    Returns dict: { status, makespan, schedule, metrics }
    where metrics contains mc_used and shift_used.
    """
    downtime = normalize_downtime(downtime)
    base_map = {(r["job"], r["op"]): r for r in baseline_schedule}
    order = precedence_aware_order(baseline_schedule)

    max_mc = policy.get("change_budget", {}).get("max_machine_changes", float("inf"))
    max_shift = policy.get("change_budget", {}).get("max_total_start_shift_L1", float("inf"))

    freeze_cfg = policy.get("freeze", {})
    frozen_ops = build_frozen_set(baseline_schedule, downtime, freeze_cfg)

    machine_intervals: Dict[int, List[Interval]] = defaultdict(list)
    end_time: Dict[Tuple[int, int], int] = {}
    mc_used = 0
    shift_used = 0
    result_schedule: List[Dict[str, Any]] = []

    for (j, o) in order:
        base = base_map[(j, o)]
        base_start = base["start"]
        base_m_orig = base["machine"]
        # allowed machine set and durations
        choices = allowed[(j, o)]

        # Anchor computation
        prev_end = end_time.get((j, o - 1), base_start if o == 0 else 0)
        if anchor_policy == "precedence-only-for-non-frozen" and (j, o) not in frozen_ops:
            anchor = prev_end
        else:
            anchor = max(base_start, prev_end)

        # Attempt frozen placement if applicable
        if (j, o) in frozen_ops:
            m = base_m_orig
            d = choices.get(m, base["dur"])  # default to baseline dur if missing
            st = base_start
            en = st + d
            if not has_conflict(m, st, en, machine_intervals, downtime):
                # Place frozen op as-is
                result_schedule.append({"job": j, "op": o, "machine": m, "start": st, "end": en, "dur": d})
                machine_intervals[m].append((st, en))
                end_time[(j, o)] = en
                # budgets (no change if same machine/start)
                if m != base_m_orig:
                    mc_used += 1
                shift_used += abs(st - base_start)
                continue
            # If conflict, fall through to repair logic

        # Generate candidates under budgets
        candidates = []
        for m, d in choices.items():
            st = earliest_feasible_time(m, anchor, d, machine_intervals, downtime)
            en = st + d
            mc = 1 if m != base_m_orig else 0
            sh = abs(st - base_start)
            if mc_used + mc <= max_mc and shift_used + sh <= max_shift:
                candidates.append((st, en, sh, mc, m, d))

        # If no candidates within budgets, relax and choose the least harmful
        if not candidates:
            for m, d in choices.items():
                st = earliest_feasible_time(m, anchor, d, machine_intervals, downtime)
                en = st + d
                mc = 1 if m != base_m_orig else 0
                sh = abs(st - base_start)
                candidates.append((st, en, sh, mc, m, d))

        # Scoring
        if prioritize == "start_then_shift_then_mc":
            candidates.sort(key=lambda x: (x[0], x[2], x[3], x[4]))
        else:  # fallback
            candidates.sort(key=lambda x: (x[0], x[3], x[2], x[4]))

        st, en, sh, mc, m, d = candidates[0]
        mc_used += mc
        shift_used += sh
        result_schedule.append({"job": j, "op": o, "machine": m, "start": st, "end": en, "dur": d})
        machine_intervals[m].append((st, en))
        end_time[(j, o)] = en

    makespan = max(rec["end"] for rec in result_schedule)
    result_schedule.sort(key=lambda r: (r["job"], r["op"]))
    return {
        "status": "REPAIRED",
        "makespan": makespan,
        "schedule": result_schedule,
        "metrics": {"machine_changes": mc_used, "start_shift_L1": shift_used}
    }


def enumerate_assignments(allowed: Dict[Tuple[int, int], Dict[int, int]],
                          baseline_schedule: List[Dict[str, Any]],
                          downtime: Dict[int, List[Interval]],
                          policy: Dict[str, Any],
                          max_combos: int = 5000) -> Dict[str, Any]:
    """Enumerate machine assignments for small instances to find a better schedule.
    Uses greedy earliest-placement under a fixed machine assignment vector.
    """
    from itertools import product

    downtime = normalize_downtime(downtime)
    base_map = {(r["job"], r["op"]): r for r in baseline_schedule}
    order = precedence_aware_order(baseline_schedule)
    max_mc = policy.get("change_budget", {}).get("max_machine_changes", float("inf"))
    max_shift = policy.get("change_budget", {}).get("max_total_start_shift_L1", float("inf"))

    choices_list = []
    total = 1
    for k in order:
        machines = list(allowed[k].keys())
        choices_list.append(machines)
        total *= len(machines)
        if total > max_combos:
            return {"status": "SKIPPED", "reason": "Too many combinations"}

    best = None
    for combo in product(*choices_list):
        machine_intervals: Dict[int, List[Interval]] = defaultdict(list)
        end_time: Dict[Tuple[int, int], int] = {}
        schedule: List[Dict[str, Any]] = []
        mc_used = 0
        shift_used = 0
        feasible = True
        for idx, key in enumerate(order):
            j, o = key
            m = combo[idx]
            d = allowed[key][m]
            base = base_map[key]
            base_start = base["start"]
            prev_end = end_time.get((j, o - 1), base_start if o == 0 else 0)
            anchor = max(base_start, prev_end)
            st = earliest_feasible_time(m, anchor, d, machine_intervals, downtime)
            en = st + d
            mc_used += (1 if m != base["machine"] else 0)
            shift_used += abs(st - base_start)
            if mc_used > max_mc or shift_used > max_shift:
                feasible = False
                break
            schedule.append({"job": j, "op": o, "machine": m, "start": st, "end": en, "dur": d})
            machine_intervals[m].append((st, en))
            end_time[(j, o)] = en
        if not feasible:
            continue
        ms = max(r["end"] for r in schedule)
        if best is None or ms < best["makespan"]:
            best = {
                "status": "REPAIRED",
                "makespan": ms,
                "schedule": sorted(schedule, key=lambda r: (r["job"], r["op"])) ,
                "metrics": {"machine_changes": mc_used, "start_shift_L1": shift_used},
            }
    return best if best else {"status": "NO_SOLUTION"}


def validate_schedule(schedule: List[Dict[str, Any]],
                      allowed: Dict[Tuple[int, int], Dict[int, int]],
                      downtime: Dict[int, List[Interval]],
                      baseline_schedule: List[Dict[str, Any]],
                      policy: Dict[str, Any]) -> Dict[str, Any]:
    """Return a report of constraint checks: precedence, machine overlaps, downtime, budgets, durations."""
    report = {"issues": [], "warnings": []}
    base_map = {(r["job"], r["op"]): r for r in baseline_schedule}
    downtime = normalize_downtime(downtime)

    # Duration and machine validity
    for rec in schedule:
        j, o, m, st, en, d = rec["job"], rec["op"], rec["machine"], rec["start"], rec["end"], rec["dur"]
        if m not in allowed[(j, o)]:
            report["issues"].append(f"Invalid machine for ({j},{o}): {m}")
        else:
            exp_d = allowed[(j, o)][m]
            if d != exp_d or en != st + d:
                report["issues"].append(f"Wrong duration/end for ({j},{o}) on M{m}: dur={d} exp={exp_d}")

    # Precedence
    by_job = defaultdict(list)
    for rec in schedule:
        by_job[rec["job"]].append(rec)
    for j, ops in by_job.items():
        ops.sort(key=lambda r: r["op"])
        for i in range(len(ops) - 1):
            if ops[i]["end"] > ops[i + 1]["start"]:
                report["issues"].append(f"Precedence violation in job {j}: op {ops[i]['op']} -> op {ops[i+1]['op']}")

    # Machine overlaps
    by_m = defaultdict(list)
    for rec in schedule:
        by_m[rec["machine"]].append(rec)
    for m, ops in by_m.items():
        ops.sort(key=lambda r: r["start"])
        for i in range(len(ops) - 1):
            if ops[i]["end"] > ops[i + 1]["start"]:
                report["issues"].append(f"Machine {m} overlap between ({ops[i]['job']},{ops[i]['op']}) and ({ops[i+1]['job']},{ops[i+1]['op']})")

    # Downtime overlaps
    for rec in schedule:
        m, st, en = rec["machine"], rec["start"], rec["end"]
        for a, b in downtime.get(m, []):
            if overlap(st, en, a, b):
                report["issues"].append(f"Downtime overlap on M{m}: ({rec['job']},{rec['op']}) [{st},{en}) vs [{a},{b})")

    # Budgets
    mc = 0
    shift_sum = 0
    for rec in schedule:
        base = base_map[(rec["job"], rec["op"])]
        if rec["machine"] != base["machine"]:
            mc += 1
        shift_sum += abs(rec["start"] - base["start"])
    max_mc = policy.get("change_budget", {}).get("max_machine_changes", float("inf"))
    max_shift = policy.get("change_budget", {}).get("max_total_start_shift_L1", float("inf"))
    if mc > max_mc:
        report["issues"].append(f"Machine changes {mc} exceed budget {max_mc}")
    if shift_sum > max_shift:
        report["issues"].append(f"Total start shift {shift_sum} exceeds budget {max_shift}")

    report["budget_usage"] = {"machine_changes": mc, "start_shift_L1": shift_sum}

    return report
