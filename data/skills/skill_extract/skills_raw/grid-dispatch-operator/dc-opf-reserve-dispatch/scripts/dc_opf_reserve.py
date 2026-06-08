#!/usr/bin/env python3
"""
DC Optimal Power Flow with Spinning Reserve Co-Optimization (MATPOWER JSON input).

Usage:
  python scripts/dc_opf_reserve.py --input network.json --output report.json

Requirements:
  - Python 3
  - numpy, scipy, cvxpy (with a QP solver like CLARABEL/ECOS/OSQP/SCS)

This script:
  - Parses a MATPOWER-style network snapshot in JSON
  - Builds a sparse DC-OPF with generator/reserve constraints
  - Solves for minimum energy cost subject to power balance, line limits, and reserves
  - Writes a report JSON with dispatch, totals, top three most loaded lines, and operating margin
"""

import argparse
import json
import sys
from typing import List, Tuple

try:
    import numpy as np
    from scipy import sparse
    import cvxpy as cp
except Exception as e:
    print("Missing required packages (numpy, scipy, cvxpy). Please install them.", file=sys.stderr)
    sys.exit(1)


def load_network(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    # Basic validation
    for key in ['baseMVA', 'bus', 'gen', 'branch', 'gencost']:
        if key not in data:
            raise ValueError(f"Missing key '{key}' in network JSON")
    return data


def build_bus_index(buses: np.ndarray) -> dict:
    return {int(buses[i, 0]): i for i in range(buses.shape[0])}


def find_slack_index(buses: np.ndarray) -> int:
    # bus type column index 1; 3 indicates slack/reference
    for i in range(buses.shape[0]):
        if int(buses[i, 1]) == 3:
            return i
    return 0


def build_B_and_branches(branches: np.ndarray, bus_num_to_idx: dict, n_bus: int) -> Tuple[sparse.csr_matrix, List[Tuple[int,int,int,int,float,float]]]:
    # Returns B matrix and branch_info list:
    # branch_info entries: (from_bus_num, to_bus_num, from_idx, to_idx, b_susceptance, rateA)
    rows = []
    cols = []
    vals = []
    branch_info = []
    for k in range(branches.shape[0]):
        br = branches[k]
        status = int(br[10]) if br.shape[0] > 10 else 1
        if status != 1:
            continue
        x = float(br[3])
        if x == 0.0:
            continue  # skip zero reactance lines
        f_num = int(br[0])
        t_num = int(br[1])
        if f_num not in bus_num_to_idx or t_num not in bus_num_to_idx:
            continue
        f_idx = bus_num_to_idx[f_num]
        t_idx = bus_num_to_idx[t_num]
        b = 1.0 / x
        # Diagonal contributions
        rows += [f_idx, t_idx]
        cols += [f_idx, t_idx]
        vals += [b, b]
        # Off-diagonal
        rows += [f_idx, t_idx]
        cols += [t_idx, f_idx]
        vals += [-b, -b]
        rate = float(br[5]) if br.shape[0] > 5 else 0.0
        branch_info.append((f_num, t_num, f_idx, t_idx, b, rate))
    B = sparse.coo_matrix((vals, (rows, cols)), shape=(n_bus, n_bus)).tocsr()
    return B, branch_info


def solve_dc_opf_with_reserves(data: dict):
    baseMVA = float(data['baseMVA'])
    buses = np.array(data['bus'], dtype=float)
    gens = np.array(data['gen'], dtype=float)
    branches = np.array(data['branch'], dtype=float)
    gencost = np.array(data['gencost'], dtype=float)

    n_bus = buses.shape[0]
    n_gen = gens.shape[0]

    # Optional reserve data
    if 'reserve_capacity' in data and isinstance(data['reserve_capacity'], list):
        reserve_capacity = np.array(data['reserve_capacity'], dtype=float)
        # Pad or trim to n_gen if needed
        if reserve_capacity.shape[0] != n_gen:
            reserve_capacity = np.resize(reserve_capacity, n_gen)
    else:
        reserve_capacity = np.zeros(n_gen)
    reserve_requirement = float(data.get('reserve_requirement', 0.0))

    # Bus mapping and slack
    bus_num_to_idx = build_bus_index(buses)
    slack_idx = find_slack_index(buses)

    # Build B and branch info
    B, branch_info = build_B_and_branches(branches, bus_num_to_idx, n_bus)

    # Generator incidence S (n_bus x n_gen)
    S_rows, S_cols, S_vals = [], [], []
    for i in range(n_gen):
        bnum = int(gens[i, 0])
        if bnum not in bus_num_to_idx:
            continue
        S_rows.append(bus_num_to_idx[bnum])
        S_cols.append(i)
        S_vals.append(1.0)
    S = sparse.coo_matrix((S_vals, (S_rows, S_cols)), shape=(n_bus, n_gen)).tocsr()

    Pd = buses[:, 2]  # MW

    # Decision variables
    Pg = cp.Variable(n_gen)  # MW
    Rg = cp.Variable(n_gen)  # MW
    Theta = cp.Variable(n_bus)  # radians

    constraints = []

    # Slack angle
    constraints.append(Theta[slack_idx] == 0)

    # Generator and reserve constraints
    for i in range(n_gen):
        status = int(gens[i, 7]) if gens.shape[1] > 7 else 1
        pmax = float(gens[i, 8])
        pmin = float(gens[i, 9])
        if status == 0:
            constraints += [Pg[i] == 0, Rg[i] == 0]
            continue
        constraints += [Pg[i] >= pmin, Pg[i] <= pmax]
        constraints += [Rg[i] >= 0, Rg[i] <= reserve_capacity[i]]
        constraints += [Pg[i] + Rg[i] <= pmax]

    # System reserve requirement
    constraints.append(cp.sum(Rg) >= reserve_requirement)

    # Nodal balance: S·Pg − Pd = baseMVA · (B · Theta)
    constraints.append(S @ Pg - Pd == (B @ Theta) * baseMVA)

    # Line limits (only for in-service branches with positive rating)
    for (f_num, t_num, f_idx, t_idx, b, rate) in branch_info:
        if rate is None or rate <= 0:
            continue
        flow = b * (Theta[f_idx] - Theta[t_idx]) * baseMVA
        constraints += [flow <= rate, flow >= -rate]

    # Objective: generation cost
    cost = 0
    for i in range(n_gen):
        status = int(gens[i, 7]) if gens.shape[1] > 7 else 1
        if status == 0:
            continue
        ncost = int(gencost[i, 3]) if gencost.shape[1] > 3 else 0
        if ncost >= 3:
            c2 = float(gencost[i, 4])
            c1 = float(gencost[i, 5])
            c0 = float(gencost[i, 6])
            cost += c2 * cp.square(Pg[i]) + c1 * Pg[i] + c0
        elif ncost == 2:
            c1 = float(gencost[i, 4])
            c0 = float(gencost[i, 5])
            cost += c1 * Pg[i] + c0
        elif ncost == 1:
            c0 = float(gencost[i, 4])
            cost += c0
        else:
            # If cost format unrecognized, ignore to keep convexity
            cost += 0

    problem = cp.Problem(cp.Minimize(cost), constraints)

    # Try multiple solvers for robustness
    solved = False
    for solver in [getattr(cp, 'CLARABEL', None), getattr(cp, 'OSQP', None), getattr(cp, 'ECOS', None), getattr(cp, 'SCS', None)]:
        if solver is None:
            continue
        try:
            problem.solve(solver=solver, verbose=False)
        except Exception:
            continue
        if problem.status in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
            solved = True
            break
    if not solved:
        raise RuntimeError(f"Optimization failed with status: {problem.status}")

    Pg_MW = np.array(Pg.value).astype(float)
    Rg_MW = np.array(Rg.value).astype(float)
    theta_val = np.array(Theta.value).astype(float)

    # Report components
    generator_dispatch = []
    for i in range(n_gen):
        generator_dispatch.append({
            "id": int(i + 1),
            "bus": int(gens[i, 0]),
            "output_MW": round(float(Pg_MW[i]), 2),
            "reserve_MW": round(float(Rg_MW[i]), 2),
            "pmax_MW": round(float(gens[i, 8]), 2),
        })

    load_MW = float(np.sum(Pd))
    generation_MW = float(np.sum(Pg_MW))
    reserve_MW = float(np.sum(Rg_MW))

    # Line loadings
    loadings = []
    for (f_num, t_num, f_idx, t_idx, b, rate) in branch_info:
        if rate is None or rate <= 0:
            continue
        flow = b * (theta_val[f_idx] - theta_val[t_idx]) * baseMVA
        pct = abs(flow) / rate * 100.0 if rate > 0 else 0.0
        loadings.append({
            "from": int(f_num),
            "to": int(t_num),
            "loading_pct": float(pct),
        })
    loadings.sort(key=lambda x: x["loading_pct"], reverse=True)
    most_loaded = [
        {"from": l["from"], "to": l["to"], "loading_pct": round(l["loading_pct"], 2)}
        for l in loadings[:3]
    ]

    # Operating margin (online units only)
    operating_margin = 0.0
    for i in range(n_gen):
        status = int(gens[i, 7]) if gens.shape[1] > 7 else 1
        if status != 1:
            continue
        pmax = float(gens[i, 8])
        margin = pmax - Pg_MW[i] - Rg_MW[i]
        if margin > 0:
            operating_margin += margin

    report = {
        "generator_dispatch": generator_dispatch,
        "totals": {
            "cost_dollars_per_hour": round(float(problem.value), 2),
            "load_MW": round(load_MW, 2),
            "generation_MW": round(generation_MW, 2),
            "reserve_MW": round(reserve_MW, 2),
        },
        "most_loaded_lines": most_loaded,
        "operating_margin_MW": round(float(operating_margin), 2),
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="DC-OPF with reserve co-optimization")
    parser.add_argument("--input", required=True, help="Path to MATPOWER JSON network file")
    parser.add_argument("--output", required=True, help="Path to write report JSON")
    args = parser.parse_args()

    data = load_network(args.input)
    report = solve_dc_opf_with_reserves(data)

    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)

    # Quick verification printout
    print(f"Report written to {args.output}")
    print(f"Totals: {report['totals']}")


if __name__ == "__main__":
    main()
