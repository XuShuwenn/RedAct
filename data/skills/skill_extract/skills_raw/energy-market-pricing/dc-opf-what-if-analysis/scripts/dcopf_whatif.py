#!/usr/bin/env python3
"""
DC-OPF with Reserve Co-optimization — Base vs Counterfactual

- MW units for power and $/MWh for costs (angles in radians)
- LP formulation using SciPy HiGHS (robust for linear costs)
- Extracts LMPs from equality duals and reserve MCP from inequality duals

Usage:
  python scripts/dcopf_whatif.py \
    --network network.json \
    --target 64,1501 --multiplier 1.2 \
    --output report.json

Multiple target lines may be specified with repeated --target and --multiplier flags
in the same order.
"""

import argparse
import json
import math
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix, csr_matrix, hstack, vstack, eye, diags


def parse_args():
    p = argparse.ArgumentParser(description="DC-OPF what-if analysis (LP)")
    p.add_argument("--network", required=True, help="Path to MATPOWER-format JSON")
    p.add_argument("--target", action="append", default=[], help="Target line as FROM,TO (repeatable)")
    p.add_argument("--multiplier", action="append", default=[], help="Capacity multiplier for target line (repeatable)")
    p.add_argument("--output", required=True, help="Path to write report.json")
    return p.parse_args()


def load_network(path: str) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


def build_bus_index(bus_array: np.ndarray) -> Dict[int, int]:
    return {int(bus_array[i, 0]): i for i in range(bus_array.shape[0])}


def build_B_matrix(branches: np.ndarray, bus_idx: Dict[int, int], n_bus: int, baseMVA: float) -> csr_matrix:
    # B in MW units: b_MW = baseMVA / x
    B = lil_matrix((n_bus, n_bus))
    for br in branches:
        fnum, tnum = int(br[0]), int(br[1])
        status = int(br[10]) if len(br) > 10 else 1
        if status != 1:
            continue
        x = float(br[3])
        if x == 0:
            continue
        f = bus_idx.get(fnum)
        t = bus_idx.get(tnum)
        if f is None or t is None:
            continue
        b = baseMVA / x
        B[f, f] += b
        B[t, t] += b
        B[f, t] -= b
        B[t, f] -= b
    return B.tocsr()


def build_Bf_matrix(branches: np.ndarray, bus_idx: Dict[int, int], n_bus: int, baseMVA: float) -> Tuple[csr_matrix, np.ndarray, np.ndarray, np.ndarray]:
    # flow_k (MW) = (baseMVA/x_k) * (theta_f - theta_t) = Bf[k,:] @ theta
    n_branch = branches.shape[0]
    Bf = lil_matrix((n_branch, n_bus))
    br_from = np.zeros(n_branch, dtype=int)
    br_to = np.zeros(n_branch, dtype=int)
    br_rate = np.zeros(n_branch, dtype=float)
    for k, br in enumerate(branches):
        fnum, tnum = int(br[0]), int(br[1])
        status = int(br[10]) if len(br) > 10 else 1
        br_from[k] = fnum
        br_to[k] = tnum
        br_rate[k] = float(br[5])
        if status != 1:
            continue
        x = float(br[3])
        if x == 0:
            continue
        f = bus_idx.get(fnum)
        t = bus_idx.get(tnum)
        if f is None or t is None:
            continue
        b = baseMVA / x
        Bf[k, f] += b
        Bf[k, t] -= b
    return Bf.tocsr(), br_from, br_to, br_rate


def extract_costs_linear(gencost: np.ndarray) -> np.ndarray:
    # gencost format: [model, startup, shutdown, ncost, c(n-1), ..., c0]
    # We use linear coefficient c1 when available; if only c0 present, use that as proxy (rare).
    n_gen = gencost.shape[0]
    c_lin = np.zeros(n_gen)
    for i in range(n_gen):
        model = int(gencost[i, 0])
        if model == 2:
            ncost = int(gencost[i, 3])
            # For ncost >= 2, linear term is the second to last coefficient
            if ncost >= 2:
                c_lin[i] = float(gencost[i, 4 + ncost - 2])
            elif ncost == 1:
                c_lin[i] = float(gencost[i, 4])
        else:
            # piecewise linear not explicitly handled; default to 0
            c_lin[i] = 0.0
    return c_lin


def apply_multipliers(branches: np.ndarray, targets: List[Tuple[int, int]], mults: List[float]) -> np.ndarray:
    cf = branches.copy()
    pair_to_mult = defaultdict(list)
    for (f, t), m in zip(targets, mults):
        pair_to_mult[(f, t)].append(m)
        pair_to_mult[(t, f)].append(m)
    # For each branch that matches any target pair, apply the product of multipliers
    for k in range(cf.shape[0]):
        fnum, tnum = int(cf[k, 0]), int(cf[k, 1])
        key = (fnum, tnum)
        if key in pair_to_mult and cf[k, 5] > 0:
            m_prod = 1.0
            for m in pair_to_mult[key]:
                m_prod *= m
            cf[k, 5] = float(cf[k, 5]) * m_prod
    return cf


def solve_lp(network: Dict, branches_override: np.ndarray = None) -> Dict:
    baseMVA = float(network["baseMVA"])
    buses = np.array(network["bus"], dtype=float)
    gens = np.array(network["gen"], dtype=float)
    branches = np.array(network["branch"], dtype=float)
    gencost = np.array(network["gencost"], dtype=float)
    reserve_capacity = np.array(network.get("reserve_capacity", [0.0]*len(gens)), dtype=float)
    reserve_requirement = float(network.get("reserve_requirement", 0.0))

    if branches_override is not None:
        branches = np.array(branches_override, dtype=float)

    n_bus = buses.shape[0]
    n_gen = gens.shape[0]
    n_branch = branches.shape[0]

    bus_idx = build_bus_index(buses)

    # Slack bus selection
    slack_idx = None
    for i in range(n_bus):
        if int(buses[i, 1]) == 3:
            slack_idx = i
            break
    if slack_idx is None:
        slack_idx = 0

    # Mappings
    gen_bus_idx = np.array([bus_idx[int(gens[i, 0]) ] for i in range(n_gen)], dtype=int)

    # Loads (MW)
    Pd = buses[:, 2]

    # Costs ($/MWh)
    c1 = extract_costs_linear(gencost)

    # Build matrices
    B = build_B_matrix(branches, bus_idx, n_bus, baseMVA)  # MW
    Bf, br_from, br_to, br_rate = build_Bf_matrix(branches, bus_idx, n_bus, baseMVA)

    # Variable layout: x = [Pg (n_gen, MW), theta (n_bus, rad), Rg (n_gen, MW)]
    PG_START = 0
    TH_START = n_gen
    RG_START = n_gen + n_bus
    n_vars = n_gen + n_bus + n_gen

    # Objective coefficients: c^T x ($/h)
    c = np.zeros(n_vars)
    c[PG_START:PG_START + n_gen] = c1
    # Reserve cost: if not provided, set to small constant (e.g., 0), or derive externally
    # Here we set to zero to avoid bias unless user encodes reserve costs into reserve_capacity
    # You may modify below to include a uniform reserve price proxy if needed
    c[RG_START:RG_START + n_gen] = 0.0

    # Equality constraints: A_eq x = b_eq
    # Nodal balance: Cg@Pg - Pd = B@theta  -> [Cg | -B | 0] x = Pd
    Cg = lil_matrix((n_bus, n_gen))
    for g in range(n_gen):
        Cg[gen_bus_idx[g], g] = 1.0
    Cg = Cg.tocsr()

    A_eq_bal = hstack([Cg, -B, csr_matrix((n_bus, n_gen))], format='csr')
    b_eq_bal = Pd

    # Slack angle: theta[slack] = 0
    A_eq_slack = lil_matrix((1, n_vars))
    A_eq_slack[0, TH_START + slack_idx] = 1.0
    A_eq_slack = A_eq_slack.tocsr()
    b_eq_slack = np.array([0.0])

    A_eq = vstack([A_eq_bal, A_eq_slack], format='csr')
    b_eq = np.concatenate([b_eq_bal, b_eq_slack])

    # Inequality constraints: A_ub x <= b_ub
    ineq_rows = []
    ineq_rhs = []

    # Line limits: -rate <= flow <= rate -> two sets
    rates = br_rate
    mask_valid = (rates > 0)

    # flow = Bf @ theta
    A_flow_pos = hstack([csr_matrix((n_branch, n_gen)), Bf, csr_matrix((n_branch, n_gen))], format='csr')
    A_flow_neg = hstack([csr_matrix((n_branch, n_gen)), -Bf, csr_matrix((n_branch, n_gen))], format='csr')

    b_flow_pos = rates.copy()
    b_flow_neg = rates.copy()

    # If branch is invalid for limit (rate<=0 or x==0), set large bounds so it's inactive
    # Achieve by overwriting RHS for those rows
    invalid = ~mask_valid
    b_flow_pos[invalid] = 1e20
    b_flow_neg[invalid] = 1e20

    ineq_rows.append(A_flow_pos)
    ineq_rhs.append(b_flow_pos)
    ineq_rows.append(A_flow_neg)
    ineq_rhs.append(b_flow_neg)

    # Capacity coupling: Pg + Rg <= Pmax
    A_coupling = lil_matrix((n_gen, n_vars))
    for i in range(n_gen):
        A_coupling[i, PG_START + i] = 1.0
        A_coupling[i, RG_START + i] = 1.0
    A_coupling = A_coupling.tocsr()
    b_coupling = gens[:, 8]  # Pmax (MW)
    ineq_rows.append(A_coupling)
    ineq_rhs.append(b_coupling)

    # Reserve requirement: -sum(Rg) <= -R_req  (i.e., sum(Rg) >= R_req)
    A_reserve = lil_matrix((1, n_vars))
    A_reserve[0, RG_START:RG_START + n_gen] = -1.0
    A_reserve = A_reserve.tocsr()
    b_reserve = np.array([-reserve_requirement])
    ineq_rows.append(A_reserve)
    ineq_rhs.append(b_reserve)

    A_ub = vstack(ineq_rows, format='csr')
    b_ub = np.concatenate(ineq_rhs)

    # Bounds
    bounds = []
    # Pg bounds
    for i in range(n_gen):
        pmin = float(gens[i, 9])
        pmax = float(gens[i, 8])
        status = int(gens[i, 7])
        if status != 1:
            bounds.append((0.0, 0.0))
        else:
            bounds.append((pmin, pmax))
    # theta bounds (slack fixed; others free)
    for i in range(n_bus):
        if i == slack_idx:
            bounds.append((0.0, 0.0))
        else:
            bounds.append((None, None))
    # Rg bounds
    for i in range(n_gen):
        status = int(gens[i, 7])
        if status != 1:
            bounds.append((0.0, 0.0))
        else:
            bounds.append((0.0, float(reserve_capacity[i]) if i < len(reserve_capacity) else 0.0))

    # Solve
    result = linprog(
        c,
        A_ub=A_ub, b_ub=b_ub,
        A_eq=A_eq, b_eq=b_eq,
        bounds=bounds, method='highs',
        options={'presolve': True}
    )

    if not result.success:
        raise RuntimeError(f"LP solver failed: {result.message}")

    # Extract variables
    x = result.x
    Pg = x[PG_START:PG_START + n_gen]
    theta = x[TH_START:TH_START + n_bus]
    Rg = x[RG_START:RG_START + n_gen]

    # LMPs from equality marginals (first n_bus are power balance constraints)
    lmps = []
    if hasattr(result, 'eqlin') and hasattr(result.eqlin, 'marginals'):
        lam = result.eqlin.marginals[:n_bus]
        for i in range(n_bus):
            lmps.append({
                "bus": int(buses[i, 0]),
                "lmp_dollars_per_MWh": float(round(lam[i], 6))
            })
    else:
        # Fallback: approximate using average marginal cost
        avg_c = float(np.mean(c1[c1 > 0])) if np.any(c1 > 0) else 0.0
        for i in range(n_bus):
            lmps.append({"bus": int(buses[i, 0]), "lmp_dollars_per_MWh": float(round(avg_c, 6))})

    # Reserve MCP from inequality marginals (last inequality is reserve)
    reserve_mcp = 0.0
    if hasattr(result, 'ineqlin') and hasattr(result.ineqlin, 'marginals'):
        ineq_m = result.ineqlin.marginals
        # Inequalities are stacked as: +flow, -flow, coupling, reserve
        # Count: 2*n_branch + n_gen + 1
        n_ineq_total = 2 * n_branch + n_gen + 1
        if len(ineq_m) >= n_ineq_total:
            reserve_marg = float(ineq_m[-1])
            # Constraint is -sum(Rg) <= -R_req; tightening R_req by 1 MW decreases b by 1 => cost increases by -reserve_marg
            reserve_mcp = -reserve_marg
            if reserve_mcp < 0:  # numerical noise
                reserve_mcp = 0.0

    # Binding lines (loading >= 99%)
    flows = (Bf @ theta)
    binding_lines = []
    for k in range(n_branch):
        rate = br_rate[k]
        x = float(branches[k, 3])
        status = int(branches[k, 10]) if len(branches[k]) > 10 else 1
        if status != 1 or rate <= 0 or x == 0:
            continue
        flow_MW = float(flows[k])
        loading_pct = abs(flow_MW) / rate * 100.0 if rate > 0 else 0.0
        if loading_pct >= 99.0:
            binding_lines.append({
                "from": int(br_from[k]),
                "to": int(br_to[k]),
                "flow_MW": float(round(flow_MW, 6)),
                "limit_MW": float(round(rate, 6))
            })

    total_cost = float(result.fun)
    return {
        "total_cost_dollars_per_hour": round(total_cost, 6),
        "lmp_by_bus": lmps,
        "reserve_mcp_dollars_per_MWh": round(reserve_mcp, 6),
        "binding_lines": binding_lines,
        "_theta": theta,  # internal for optional debugging
        "_Pg": Pg,
        "_Rg": Rg,
        "_br_rate": br_rate,
        "_br_from": br_from,
        "_br_to": br_to
    }


def main():
    args = parse_args()
    net = load_network(args.network)

    # Parse target lines and multipliers
    targets = []
    mults = []
    if len(args.target) != len(args.multiplier):
        raise ValueError("Number of --target and --multiplier arguments must match")
    for t, m in zip(args.target, args.multiplier):
        f_str, t_str = t.split(',')
        targets.append((int(f_str.strip()), int(t_str.strip())))
        mults.append(float(m))

    # Solve base
    base = solve_lp(net)

    # Apply multipliers to all matching lines (both directions, all parallels)
    if targets:
        branches_cf = apply_multipliers(np.array(net["branch"], dtype=float), targets, mults)
        cf = solve_lp(net, branches_override=branches_cf)
    else:
        cf = solve_lp(net)  # identical if no targets specified

    # Impact analysis
    cost_reduction = round(base["total_cost_dollars_per_hour"] - cf["total_cost_dollars_per_hour"], 6)

    base_map = {e["bus"]: e["lmp_dollars_per_MWh"] for e in base["lmp_by_bus"]}
    cf_map = {e["bus"]: e["lmp_dollars_per_MWh"] for e in cf["lmp_by_bus"]}

    deltas = []
    for b in base_map:
        delta = round(cf_map.get(b, 0.0) - base_map[b], 6)
        deltas.append({
            "bus": int(b),
            "base_lmp": round(base_map[b], 6),
            "cf_lmp": round(cf_map.get(b, 0.0), 6),
            "delta": round(delta, 6)
        })
    deltas.sort(key=lambda x: x["delta"])  # most negative first
    top3 = deltas[:3]

    # Determine if any adjusted line is binding in counterfactual
    cf_bind_pairs = {(l["from"], l["to"]) for l in cf["binding_lines"]}
    congestion_relieved = True
    for (f, t) in targets:
        if (f, t) in cf_bind_pairs or (t, f) in cf_bind_pairs:
            congestion_relieved = False
            break

    report = {
        "base_case": {
            "total_cost_dollars_per_hour": base["total_cost_dollars_per_hour"],
            "lmp_by_bus": base["lmp_by_bus"],
            "reserve_mcp_dollars_per_MWh": base["reserve_mcp_dollars_per_MWh"],
            "binding_lines": base["binding_lines"]
        },
        "counterfactual": {
            "total_cost_dollars_per_hour": cf["total_cost_dollars_per_hour"],
            "lmp_by_bus": cf["lmp_by_bus"],
            "reserve_mcp_dollars_per_MWh": cf["reserve_mcp_dollars_per_MWh"],
            "binding_lines": cf["binding_lines"]
        },
        "impact_analysis": {
            "cost_reduction_dollars_per_hour": cost_reduction,
            "buses_with_largest_lmp_drop": top3,
            "congestion_relieved": bool(congestion_relieved)
        }
    }

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
