#!/usr/bin/env python3
"""
Validate an ACOPF report JSON for schema and internal consistency.

Usage:
  python scripts/validate_acopf_report.py /path/to/report.json

This validator checks:
- required sections and fields exist
- numeric types and absence of NaN
- totals match sums within tolerance
- losses = total_generation_MW - total_load_MW (within tolerance)
- bus voltages respect bounds (or are reflected in max_voltage_violation_pu)
- branch loading_pct consistent with flows and limits
- feasibility metrics are numeric

Exit codes:
- 0 on pass
- 1 on validation failure
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, List

TOL_P = 1e-3           # MW tolerance for totals
TOL_Q = 1e-3           # MVAr tolerance for totals
TOL_MVA = 1e-3         # MVA tolerance for branch checks
TOL_PCT = 1e-2         # percentage tolerance for loading_pct
TOL_VOLT = 1e-6        # pu tolerance for voltage bound consistency

ALLOWED_STATUSES = {"optimal", "infeasible", "error", "unknown"}


def is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))


def approx(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


def validate_summary(summary: Dict[str, Any], problems: List[str]) -> None:
    required = [
        "total_cost_per_hour",
        "total_load_MW",
        "total_load_MVAr",
        "total_generation_MW",
        "total_generation_MVAr",
        "total_losses_MW",
        "solver_status",
    ]
    for k in required:
        if k not in summary:
            problems.append(f"summary missing field: {k}")
    for k in [x for x in required if x != "solver_status"]:
        if k in summary and not is_num(summary[k]):
            problems.append(f"summary field not numeric: {k}")
    if "solver_status" in summary:
        status = summary["solver_status"]
        if not isinstance(status, str):
            problems.append("summary.solver_status must be a string")
        elif status.lower() not in ALLOWED_STATUSES:
            problems.append(f"summary.solver_status not in allowed set: {status}")


def validate_generators(gens: List[Dict[str, Any]], summary: Dict[str, Any], problems: List[str]) -> None:
    pg_sum = 0.0
    qg_sum = 0.0
    for i, g in enumerate(gens):
        for fld in ["id", "bus", "pg_MW", "qg_MVAr", "pmin_MW", "pmax_MW", "qmin_MVAr", "qmax_MVAr"]:
            if fld not in g:
                problems.append(f"generator[{i}] missing field: {fld}")
        for nf in ["pg_MW", "qg_MVAr", "pmin_MW", "pmax_MW", "qmin_MVAr", "qmax_MVAr"]:
            if nf in g and not is_num(g[nf]):
                problems.append(f"generator[{i}].{nf} not numeric")
        if is_num(g.get("pg_MW", float("nan"))):
            pg_sum += float(g["pg_MW"])
        if is_num(g.get("qg_MVAr", float("nan"))):
            qg_sum += float(g["qg_MVAr"])
    # Cross-check sums vs summary
    if "total_generation_MW" in summary and not approx(pg_sum, float(summary["total_generation_MW"]), TOL_P):
        problems.append(f"sum(pg_MW) != summary.total_generation_MW (diff={pg_sum - float(summary['total_generation_MW']):.6f})")
    if "total_generation_MVAr" in summary and not approx(qg_sum, float(summary["total_generation_MVAr"]), TOL_Q):
        problems.append(f"sum(qg_MVAr) != summary.total_generation_MVAr (diff={qg_sum - float(summary['total_generation_MVAr']):.6f})")


def validate_buses(buses: List[Dict[str, Any]], feasibility: Dict[str, Any], problems: List[str]) -> None:
    max_violation = 0.0
    for i, b in enumerate(buses):
        for fld in ["id", "vm_pu", "va_deg", "vmin_pu", "vmax_pu"]:
            if fld not in b:
                problems.append(f"bus[{i}] missing field: {fld}")
        for nf in ["vm_pu", "va_deg", "vmin_pu", "vmax_pu"]:
            if nf in b and not is_num(b[nf]):
                problems.append(f"bus[{i}].{nf} not numeric")
        if all(nf in b for nf in ["vm_pu", "vmin_pu", "vmax_pu"]) and all(is_num(b[nf]) for nf in ["vm_pu", "vmin_pu", "vmax_pu"]):
            vm = float(b["vm_pu"]) 
            vmin = float(b["vmin_pu"]) 
            vmax = float(b["vmax_pu"]) 
            if vm < vmin:
                max_violation = max(max_violation, vmin - vm)
            elif vm > vmax:
                max_violation = max(max_violation, vm - vmax)
    if "max_voltage_violation_pu" in feasibility and not approx(max_violation, float(feasibility["max_voltage_violation_pu"]), TOL_VOLT):
        problems.append(f"feasibility.max_voltage_violation_pu inconsistent with bus bounds (computed={max_violation:.6f}, reported={float(feasibility['max_voltage_violation_pu']):.6f})")


def validate_branches(branches: List[Dict[str, Any]], feasibility: Dict[str, Any], problems: List[str]) -> None:
    max_over = 0.0
    for i, br in enumerate(branches):
        for fld in ["from_bus", "to_bus", "loading_pct", "flow_from_MVA", "flow_to_MVA", "limit_MVA"]:
            if fld not in br:
                problems.append(f"branch[{i}] missing field: {fld}")
        for nf in ["loading_pct", "flow_from_MVA", "flow_to_MVA", "limit_MVA"]:
            if nf in br and not is_num(br[nf]):
                problems.append(f"branch[{i}].{nf} not numeric")
        if all(f in br for f in ["flow_from_MVA", "flow_to_MVA", "limit_MVA", "loading_pct"]):
            s_from = float(br["flow_from_MVA"]) 
            s_to = float(br["flow_to_MVA"]) 
            limit = float(br["limit_MVA"]) 
            if limit <= 0:
                problems.append(f"branch[{i}] limit_MVA must be > 0")
                continue
            loading_calc = 100.0 * max(s_from, s_to) / limit
            if not approx(loading_calc, float(br["loading_pct"]), TOL_PCT):
                problems.append(f"branch[{i}] loading_pct inconsistent (calc={loading_calc:.4f}, reported={float(br['loading_pct']):.4f})")
            over = max(0.0, max(s_from, s_to) - limit)
            max_over = max(max_over, over)
    if "max_branch_overload_MVA" in feasibility and not approx(max_over, float(feasibility["max_branch_overload_MVA"]), TOL_MVA):
        problems.append(f"feasibility.max_branch_overload_MVA inconsistent (computed={max_over:.6f}, reported={float(feasibility['max_branch_overload_MVA']):.6f})")


def validate_losses(summary: Dict[str, Any], problems: List[str]) -> None:
    if all(k in summary for k in ["total_generation_MW", "total_load_MW", "total_losses_MW"]):
        gen = float(summary["total_generation_MW"]) 
        load = float(summary["total_load_MW"]) 
        losses = float(summary["total_losses_MW"]) 
        if not approx(gen - load, losses, TOL_P):
            problems.append(f"losses mismatch: (gen-load)={gen - load:.6f} vs losses={losses:.6f}")
        if losses < -TOL_P:
            problems.append("total_losses_MW must be non-negative")


def validate_feasibility(feas: Dict[str, Any], problems: List[str]) -> None:
    for fld in ["max_p_mismatch_MW", "max_q_mismatch_MVAr", "max_voltage_violation_pu", "max_branch_overload_MVA"]:
        if fld not in feas:
            problems.append(f"feasibility_check missing field: {fld}")
        elif not is_num(feas[fld]):
            problems.append(f"feasibility_check field not numeric: {fld}")


def main():
    ap = argparse.ArgumentParser(description="Validate ACOPF report JSON")
    ap.add_argument("path", help="Path to report.json")
    args = ap.parse_args()

    problems: List[str] = []

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: failed to read JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Top-level sections
    for sec in ["summary", "generators", "buses", "most_loaded_branches", "feasibility_check"]:
        if sec not in data:
            problems.append(f"missing top-level section: {sec}")

    summary = data.get("summary", {})
    generators = data.get("generators", [])
    buses = data.get("buses", [])
    branches = data.get("most_loaded_branches", [])
    feas = data.get("feasibility_check", {})

    # Section validations
    validate_summary(summary, problems)
    validate_feasibility(feas, problems)
    if isinstance(generators, list):
        validate_generators(generators, summary, problems)
    else:
        problems.append("generators must be a list")
    if isinstance(buses, list):
        validate_buses(buses, feas, problems)
    else:
        problems.append("buses must be a list")
    if isinstance(branches, list):
        validate_branches(branches, feas, problems)
    else:
        problems.append("most_loaded_branches must be a list")
    validate_losses(summary, problems)

    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        # Provide a brief consistency echo
        tg = summary.get("total_generation_MW")
        tl = summary.get("total_load_MW")
        ls = summary.get("total_losses_MW")
        if is_num(tg) and is_num(tl) and is_num(ls):
            print(f"  totals: gen={tg} MW, load={tl} MW, losses={ls} MW")
        print(f"  solver_status: {summary.get('solver_status')}")
        sys.exit(0)

if __name__ == "__main__":
    main()
