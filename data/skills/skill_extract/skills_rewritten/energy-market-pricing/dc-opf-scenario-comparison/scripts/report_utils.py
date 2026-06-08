#!/usr/bin/env python3
"""Utilities for DC-OPF scenario report post-processing and validation.

This module provides generic helpers to:
- Identify binding (near-limit) lines
- Compute top-k LMP drops between scenarios
- Match branches by unordered bus pairs (orientation-robust)
- Validate a report object matches the expected schema

All functions are deterministic and independent of any specific case.
"""
from typing import List, Dict, Tuple, Any


def _to_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        # If conversion fails, raise for caller to handle
        raise


def bus_pair_key(a: int, b: int) -> Tuple[int, int]:
    """Return an orientation-agnostic key for a bus pair."""
    return (a, b) if a <= b else (b, a)


def match_branches_by_buses(branches: List[Dict[str, Any]], bus_u: int, bus_v: int,
                             f_key: str = 'from', t_key: str = 'to') -> List[Dict[str, Any]]:
    """Return all branch records connecting bus_u and bus_v (unordered match).

    branches: list of dicts with at least keys f_key and t_key containing external bus IDs.
    """
    target = bus_pair_key(int(bus_u), int(bus_v))
    out = []
    for br in branches:
        a = int(br[f_key])
        b = int(br[t_key])
        if bus_pair_key(a, b) == target:
            out.append(br)
    return out


def binding_lines(records: List[Dict[str, Any]], threshold: float = 0.99,
                  f_key: str = 'from', t_key: str = 'to',
                  flow_key: str = 'flow_MW', limit_key: str = 'limit_MW') -> List[Dict[str, Any]]:
    """Filter line records to those at or above the loading threshold.

    records: list of dicts with keys for endpoints, flow (MW), and limit (MW).
    Returns new list with the same schema for lines where |flow|/limit >= threshold and limit > 0.
    """
    out = []
    for r in records:
        flow = abs(_to_float(r[flow_key]))
        limit = _to_float(r[limit_key])
        if limit <= 0:
            continue
        loading = flow / limit
        if loading >= threshold:
            out.append({
                f_key: int(r[f_key]),
                t_key: int(r[t_key]),
                flow_key: float(_to_float(r[flow_key])),
                limit_key: float(limit),
            })
    return out


def top_k_lmp_drops(base_lmps: List[Dict[str, Any]], cf_lmps: List[Dict[str, Any]], k: int = 3,
                    bus_key: str = 'bus', price_key: str = 'lmp_dollars_per_MWh') -> List[Dict[str, Any]]:
    """Compute the k buses with the largest LMP reductions from base to counterfactual.

    Returns a list of dicts: {bus, base_lmp, cf_lmp, delta}, sorted by most negative delta.
    """
    base_map = {int(d[bus_key]): _to_float(d[price_key]) for d in base_lmps}
    cf_map = {int(d[bus_key]): _to_float(d[price_key]) for d in cf_lmps}
    common = base_map.keys() & cf_map.keys()
    changes = []
    for b in common:
        base_p = base_map[b]
        cf_p = cf_map[b]
        delta = cf_p - base_p
        changes.append({
            'bus': int(b),
            'base_lmp': float(base_p),
            'cf_lmp': float(cf_p),
            'delta': float(delta),
        })
    # Sort by largest drop (most negative delta)
    changes.sort(key=lambda x: x['delta'])
    return changes[:max(0, k)]


def congestion_relieved(target_branches: List[Dict[str, Any]],
                        cf_binding: List[Dict[str, Any]],
                        f_key: str = 'from', t_key: str = 'to') -> bool:
    """Return True if none of the target branches appear in the counterfactual binding list.

    Matching is orientation-agnostic using external bus IDs.
    """
    target_pairs = {bus_pair_key(int(b[f_key]), int(b[t_key])) for b in target_branches}
    cf_pairs = {bus_pair_key(int(b[f_key]), int(b[t_key])) for b in cf_binding}
    # Congestion is relieved if there's no intersection
    return target_pairs.isdisjoint(cf_pairs)


def validate_report_structure(report: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate the report structure required by the scenario-comparison tasks.

    Returns (ok, errors). This validates keys/types but not numerical values.
    """
    errors: List[str] = []
    root_keys = ['base_case', 'counterfactual', 'impact_analysis']
    for k in root_keys:
        if k not in report:
            errors.append(f"Missing top-level key: {k}")

    def _check_case(case: Dict[str, Any], name: str) -> None:
        if not isinstance(case, dict):
            errors.append(f"{name} must be an object")
            return
        req = ['total_cost_dollars_per_hour', 'lmp_by_bus', 'reserve_mcp_dollars_per_MWh', 'binding_lines']
        for r in req:
            if r not in case:
                errors.append(f"{name} missing field: {r}")
        # Basic type checks
        try:
            _ = float(case.get('total_cost_dollars_per_hour', 0.0))
        except Exception:
            errors.append(f"{name}.total_cost_dollars_per_hour must be numeric")
        if not isinstance(case.get('lmp_by_bus', []), list):
            errors.append(f"{name}.lmp_by_bus must be a list")
        if not isinstance(case.get('binding_lines', []), list):
            errors.append(f"{name}.binding_lines must be a list")
        try:
            _ = float(case.get('reserve_mcp_dollars_per_MWh', 0.0))
        except Exception:
            errors.append(f"{name}.reserve_mcp_dollars_per_MWh must be numeric")

    if 'base_case' in report:
        _check_case(report['base_case'], 'base_case')
    if 'counterfactual' in report:
        _check_case(report['counterfactual'], 'counterfactual')

    if 'impact_analysis' in report and isinstance(report['impact_analysis'], dict):
        ia = report['impact_analysis']
        for r in ['cost_reduction_dollars_per_hour', 'buses_with_largest_lmp_drop', 'congestion_relieved']:
            if r not in ia:
                errors.append(f"impact_analysis missing field: {r}")
        try:
            _ = float(ia.get('cost_reduction_dollars_per_hour', 0.0))
        except Exception:
            errors.append("impact_analysis.cost_reduction_dollars_per_hour must be numeric")
        if not isinstance(ia.get('buses_with_largest_lmp_drop', []), list):
            errors.append("impact_analysis.buses_with_largest_lmp_drop must be a list")
        if not isinstance(ia.get('congestion_relieved', False), bool):
            errors.append("impact_analysis.congestion_relieved must be boolean")
    else:
        if 'impact_analysis' in report:
            errors.append("impact_analysis must be an object")

    return (len(errors) == 0, errors)
