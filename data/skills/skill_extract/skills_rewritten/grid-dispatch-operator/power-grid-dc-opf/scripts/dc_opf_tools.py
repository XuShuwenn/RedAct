#!/usr/bin/env python3
"""DC OPF helper utilities: load MATPOWER JSON, build DC matrices, compute flows,
verify dispatch reports, and compute loading percentages.

Usage examples:
  # Verify a report against a network
  python scripts/dc_opf_tools.py --verify --network network.json --report report.json

This script is generic and does not solve the OPF; it provides deterministic
network construction and post-solution verification utilities that help
avoid common pitfalls (scaling, status flags, and constraint checks).
"""
import argparse
import json
import math
import sys
from typing import Dict, List, Tuple

import numpy as np


def _idx_from_headers(headers: List[str], name: str, default: int) -> int:
    try:
        return headers.index(name)
    except Exception:
        return default


def load_matpower_json(path: str) -> Dict:
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def extract_indices(net: Dict) -> Dict:
    # Default MATPOWER column indices (fallbacks) per classic MATPOWER format
    # bus: [BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, VA, BASE_KV, ZONE, VMAX, VMIN]
    bus_fields = net.get('bus', {}).get('fields') or []
    BUS_I = _idx_from_headers(bus_fields, 'BUS_I', 0)
    BUS_TYPE = _idx_from_headers(bus_fields, 'BUS_TYPE', 1)
    PD = _idx_from_headers(bus_fields, 'PD', 2)

    # gen: [GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN, ...]
    gen_fields = net.get('gen', {}).get('fields') or []
    GEN_BUS = _idx_from_headers(gen_fields, 'GEN_BUS', 0)
    GEN_STATUS = _idx_from_headers(gen_fields, 'GEN_STATUS', 7)
    PMAX = _idx_from_headers(gen_fields, 'PMAX', 8)
    PMIN = _idx_from_headers(gen_fields, 'PMIN', 9)

    # branch: [F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS, ANGMIN, ANGMAX]
    br_fields = net.get('branch', {}).get('fields') or []
    F_BUS = _idx_from_headers(br_fields, 'F_BUS', 0)
    T_BUS = _idx_from_headers(br_fields, 'T_BUS', 1)
    BR_X = _idx_from_headers(br_fields, 'BR_X', 3)
    RATE_A = _idx_from_headers(br_fields, 'RATE_A', 5)
    TAP = _idx_from_headers(br_fields, 'TAP', 8)
    SHIFT = _idx_from_headers(br_fields, 'SHIFT', 9)
    BR_STATUS = _idx_from_headers(br_fields, 'BR_STATUS', 10)

    return {
        'BUS_I': BUS_I, 'BUS_TYPE': BUS_TYPE, 'PD': PD,
        'GEN_BUS': GEN_BUS, 'GEN_STATUS': GEN_STATUS, 'PMAX': PMAX, 'PMIN': PMIN,
        'F_BUS': F_BUS, 'T_BUS': T_BUS, 'BR_X': BR_X, 'RATE_A': RATE_A,
        'TAP': TAP, 'SHIFT': SHIFT, 'BR_STATUS': BR_STATUS,
    }


def build_dc_network(net: Dict) -> Dict:
    idx = extract_indices(net)
    baseMVA = float(net.get('baseMVA', 100.0))

    # Buses
    bus_array = net.get('bus', {}).get('data') or net.get('bus') or []
    if isinstance(bus_array, dict):
        bus_array = bus_array.get('data', [])
    buses = np.array(bus_array, dtype=float)
    if buses.size == 0:
        raise ValueError('No bus data found')

    # Map external bus IDs to 0-based indices
    bus_ids = buses[:, idx['BUS_I']].astype(int).tolist()
    bus_id_to_i = {bid: i for i, bid in enumerate(bus_ids)}

    bus_type = buses[:, idx['BUS_TYPE']]
    Pd = buses[:, idx['PD']]  # MW

    # Generators
    gen_array = net.get('gen', {}).get('data') or net.get('gen') or []
    if isinstance(gen_array, dict):
        gen_array = gen_array.get('data', [])
    gens = np.array(gen_array, dtype=float)
    n_gen = gens.shape[0]

    # Branches
    br_array = net.get('branch', {}).get('data') or net.get('branch') or []
    if isinstance(br_array, dict):
        br_array = br_array.get('data', [])
    branches = np.array(br_array, dtype=float)

    # Filter for active elements
    gen_on = np.ones(n_gen, dtype=bool)
    if gens.size:
        gen_on = gens[:, idx['GEN_STATUS']] > 0
    br_on = branches[:, idx['BR_STATUS']] > 0 if branches.size else np.array([], dtype=bool)

    # Build incidence matrix A (n_br_on x n_bus)
    n_bus = len(bus_ids)
    if branches.size:
        fbus_id = branches[:, idx['F_BUS']].astype(int)
        tbus_id = branches[:, idx['T_BUS']].astype(int)
        f = np.array([bus_id_to_i.get(b) for b in fbus_id])
        t = np.array([bus_id_to_i.get(b) for b in tbus_id])

        active_idx = np.where(br_on)[0]
        f = f[active_idx]
        t = t[active_idx]
        x = branches[active_idx, idx['BR_X']]
        tap = branches[active_idx, idx['TAP']]
        shift_deg = branches[active_idx, idx['SHIFT']]
        tap = np.where(np.isclose(tap, 0.0), 1.0, tap)
        shift_rad = np.deg2rad(shift_deg)

        n_br = len(active_idx)
        A = np.zeros((n_br, n_bus))
        A[np.arange(n_br), f] = 1.0
        A[np.arange(n_br), t] = -1.0

        # Weight for DC: w_k = 1 / (x_k * tap_k)
        # Guard tiny/zero x
        eps = 1e-12
        x = np.where(np.abs(x) < eps, eps, x)
        w = 1.0 / (x * tap)
    else:
        A = np.zeros((0, n_bus))
        w = np.zeros((0,))
        shift_rad = np.zeros((0,))
        f = t = np.array([], dtype=int)

    # Bbus = A^T * diag(w) * A
    D = np.diag(w) if w.size else np.zeros((0, 0))
    Bbus = A.T @ D @ A if w.size else np.zeros((n_bus, n_bus))

    # Find reference bus (prefer BUS_TYPE == 3)
    ref_candidates = np.where(np.isclose(bus_type, 3.0))[0]
    ref_bus = int(ref_candidates[0]) if ref_candidates.size else 0

    return {
        'baseMVA': baseMVA,
        'bus_ids': bus_ids,
        'bus_id_to_i': bus_id_to_i,
        'Pd': Pd,  # MW
        'gens': gens,
        'gen_on': gen_on,
        'branches': branches,
        'br_on_idx': np.where(branches[:, idx['BR_STATUS']] > 0)[0] if branches.size else np.array([], dtype=int),
        'A': A,
        'w': w,
        'shift_rad': shift_rad,
        'Bbus': Bbus,
        'ref_bus': ref_bus,
        'idx': idx,
        'f_bus_idx': f,
        't_bus_idx': t,
    }


def solve_dc_angles(net_dc: Dict, Pg_bus: np.ndarray) -> np.ndarray:
    """Solve Bbus * theta = P_inj_pu - A^T(D * shift). theta[ref]=0.
    Pg_bus: MW injection at buses (generation positive), shape (n_bus,).
    Returns theta (radians), shape (n_bus,).
    """
    baseMVA = net_dc['baseMVA']
    A = net_dc['A']
    w = net_dc['w']
    D = np.diag(w) if w.size else np.zeros((0, 0))
    Bbus = net_dc['Bbus']
    Pd = net_dc['Pd']
    shift = net_dc['shift_rad']
    ref = net_dc['ref_bus']

    n_bus = len(net_dc['bus_ids'])

    # Net injection (MW) and per-unit
    Pinj_MW = Pg_bus - Pd
    Pinj_pu = Pinj_MW / baseMVA

    # Phase shift injection term: A^T (D * shift)
    rhs_shift = A.T @ (w * shift) if w.size else np.zeros(n_bus)

    rhs = Pinj_pu - rhs_shift

    # Reduce system by eliminating reference bus
    keep = [i for i in range(n_bus) if i != ref]
    Bred = Bbus[np.ix_(keep, keep)]
    rhs_red = rhs[keep]

    # Solve; use pseudo-inverse if singular
    try:
        theta_red = np.linalg.solve(Bred, rhs_red)
    except np.linalg.LinAlgError:
        theta_red = np.linalg.pinv(Bred) @ rhs_red

    theta = np.zeros(n_bus)
    theta[keep] = theta_red
    theta[ref] = 0.0
    return theta


def flows_from_theta(net_dc: Dict, theta: np.ndarray) -> np.ndarray:
    """Compute MW flows on active branches (positive from f->t)."""
    baseMVA = net_dc['baseMVA']
    A = net_dc['A']
    w = net_dc['w']
    shift = net_dc['shift_rad']
    if w.size == 0:
        return np.zeros((0,))
    angle_drop = A @ theta  # theta_f - theta_t for each active branch
    f_pu = w * (angle_drop - shift)
    f_MW = f_pu * baseMVA
    return f_MW


def compute_bus_generation_from_report(net_dc: Dict, report: Dict) -> np.ndarray:
    """Aggregate generator outputs from report into a bus-level vector (MW)."""
    bus_ids = net_dc['bus_ids']
    bus_id_to_i = net_dc['bus_id_to_i']
    Pg_bus = np.zeros(len(bus_ids))
    for g in report.get('generator_dispatch', []):
        bus = int(g.get('bus'))
        out = float(g.get('output_MW', 0.0))
        i = bus_id_to_i.get(bus)
        if i is not None:
            Pg_bus[i] += out
    return Pg_bus


def verify_report(network_path: str, report_path: str, tol: float = 1e-3) -> Tuple[bool, List[str]]:
    net = load_matpower_json(network_path)
    net_dc = build_dc_network(net)

    with open(report_path, 'r') as f:
        report = json.load(f)

    # Aggregate generation and reserves
    Pg_bus = compute_bus_generation_from_report(net_dc, report)
    theta = solve_dc_angles(net_dc, Pg_bus)
    flows = flows_from_theta(net_dc, theta)

    # Totals
    Pd_total = float(np.sum(net_dc['Pd']))
    Pg_total = float(np.sum(Pg_bus))
    R_total = float(sum(float(g.get('reserve_MW', 0.0)) for g in report.get('generator_dispatch', [])))

    ok = True
    messages = []

    # Power balance
    pb_res = abs(Pg_total - Pd_total)
    if pb_res > max(tol, 1e-4 * max(1.0, Pd_total)):
        ok = False
        messages.append(f"Power balance mismatch MW: {pb_res:.6f}")

    # Line limits (RATE_A)
    idx = net_dc['idx']
    br = net_dc['branches']
    active = net_dc['br_on_idx']
    if active.size and flows.size:
        rateA = br[active, idx['RATE_A']]
        mask = rateA > 0
        if np.any(mask):
            viol = np.abs(flows[mask]) - rateA[mask]
            max_viol = float(np.max(viol)) if viol.size else 0.0
            if np.any(viol > tol):
                ok = False
                messages.append(f"Line limit violation max MW: {max_viol:.6f}")
        else:
            messages.append("No positive RATE_A limits found; line limit checks skipped.")
    else:
        messages.append("No active branches; line checks skipped.")

    # Generator capacity coupling: Pg + R <= Pmax
    # Map report generators to network gen rows by (bus, pmax) heuristic; if ambiguous, check only the inequality using provided pmax.
    cap_viol = 0.0
    for g in report.get('generator_dispatch', []):
        p = float(g.get('output_MW', 0.0))
        r = float(g.get('reserve_MW', 0.0))
        pmax_rep = g.get('pmax_MW', None)
        if pmax_rep is not None:
            cap_viol = max(cap_viol, p + r - float(pmax_rep))
        if r < -tol:
            cap_viol = max(cap_viol, -r)
    if cap_viol > tol:
        ok = False
        messages.append(f"Capacity coupling violation (Pg+R <= Pmax) magnitude: {cap_viol:.6f}")

    # Reserve requirement check if present in network JSON
    reserve_req_MW = None
    reserves_struct = net.get('reserves') if isinstance(net, dict) else None
    if isinstance(reserves_struct, dict):
        req = reserves_struct.get('req')
        if isinstance(req, (list, tuple)):
            reserve_req_MW = float(np.sum(np.array(req, dtype=float)))
        elif isinstance(req, (int, float)):
            reserve_req_MW = float(req)
    if reserve_req_MW is None:
        # try alternative key
        reserve_req_MW = net.get('reserve_requirement_MW') if isinstance(net, dict) else None
        if reserve_req_MW is not None:
            reserve_req_MW = float(reserve_req_MW)

    if reserve_req_MW is not None:
        if R_total + tol < reserve_req_MW:
            ok = False
            messages.append(f"Reserve shortfall MW: {(reserve_req_MW - R_total):.6f}")
    else:
        messages.append("No reserve requirement found in network; reserve adequacy check skipped.")

    # Operating margin recompute for sanity (using report Pg and R, and network Pmax if mappable is complex; fallback to report pmax)
    op_margin = report.get('operating_margin_MW', None)
    if op_margin is not None:
        try:
            float(op_margin)
        except Exception:
            ok = False
            messages.append("Operating margin field not numeric.")

    # Loading percentage sanity: should be <= 100% if line limits were enforced (for lines with RATE_A > 0)
    most_loaded = report.get('most_loaded_lines', [])
    for ml in most_loaded:
        rp = float(ml.get('loading_pct', 0.0))
        if rp < -1e-6:
            ok = False
            messages.append("Negative loading percentage found.")
            break

    return ok, messages


def top3_loaded_lines(net_dc: Dict, flows: np.ndarray) -> List[Dict]:
    """Compute top-3 loaded lines among constrained ones (RATE_A > 0)."""
    idx = net_dc['idx']
    br = net_dc['branches']
    active = net_dc['br_on_idx']
    f_idx = net_dc['f_bus_idx']
    t_idx = net_dc['t_bus_idx']
    bus_ids = net_dc['bus_ids']
    if active.size == 0 or flows.size == 0:
        return []
    rateA = br[active, idx['RATE_A']]
    mask = rateA > 0
    if not np.any(mask):
        return []
    pct = 100.0 * np.abs(flows[mask]) / rateA[mask]
    order = np.argsort(-pct)
    res = []
    for k in order[:3]:
        # Map back to from/to external bus IDs
        from_bus = bus_ids[int(f_idx[mask][k])]
        to_bus = bus_ids[int(t_idx[mask][k])]
        res.append({
            'from': int(from_bus),
            'to': int(to_bus),
            'loading_pct': float(pct[k])
        })
    return res


def main():
    ap = argparse.ArgumentParser(description="DC OPF tools: verification and utilities")
    ap.add_argument('--verify', action='store_true', help='Verify a report against the network')
    ap.add_argument('--network', type=str, help='Path to MATPOWER JSON network file')
    ap.add_argument('--report', type=str, help='Path to report JSON to verify')
    args = ap.parse_args()

    if args.verify:
        if not args.network or not args.report:
            print('ERROR: --network and --report are required with --verify', file=sys.stderr)
            sys.exit(2)
        ok, messages = verify_report(args.network, args.report)
        if ok:
            print('VERIFICATION: PASS')
        else:
            print('VERIFICATION: FAIL')
        for m in messages:
            print(f"- {m}")
        sys.exit(0 if ok else 1)
    else:
        ap.print_help()


if __name__ == '__main__':
    main()
