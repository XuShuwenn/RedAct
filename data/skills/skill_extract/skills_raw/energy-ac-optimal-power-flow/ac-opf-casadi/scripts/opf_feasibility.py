#!/usr/bin/env python3
"""Feasibility metrics for AC OPF solutions.

Given network arrays and a solution (Vm, Va, Pg, Qg), compute:
- Max real/reactive power mismatches (MW/MVAr)
- Max voltage violation (pu)
- Max branch overload (MVA)

Inputs follow MATPOWER-like conventions. All inputs are numpy arrays.
"""
from __future__ import annotations
import math
from typing import Dict, Tuple
import numpy as np
from .branch_flows import build_bus_id_to_idx, compute_branch_flows_pu


def feasibility_metrics(
    buses: np.ndarray,
    branches: np.ndarray,
    Vm: np.ndarray,
    Va: np.ndarray,
    Pg_pu: np.ndarray,
    Qg_pu: np.ndarray,
    gen_bus_idx: np.ndarray,
    baseMVA: float,
) -> Dict[str, float]:
    """Compute feasibility metrics from high-precision solution values.

    Parameters
    - buses: (n_bus, 13+)
    - branches: (n_branch, 13+)
    - Vm: (n_bus,) voltage magnitudes in pu
    - Va: (n_bus,) voltage angles in radians
    - Pg_pu, Qg_pu: (n_gen,) gen injections in pu
    - gen_bus_idx: (n_gen,) mapped bus indices for each generator
    - baseMVA: system base in MVA

    Returns dict with keys:
      max_p_mismatch_MW, max_q_mismatch_MVAr, max_voltage_violation_pu, max_branch_overload_MVA
    """
    n_bus = buses.shape[0]
    bus_map = build_bus_id_to_idx(buses)

    Pd_pu = buses[:, 2] / baseMVA
    Qd_pu = buses[:, 3] / baseMVA
    Gs_pu = buses[:, 4] / baseMVA
    Bs_pu = buses[:, 5] / baseMVA

    # Gen aggregation per bus
    Pg_bus = np.zeros(n_bus)
    Qg_bus = np.zeros(n_bus)
    for k in range(Pg_pu.size):
        i = int(gen_bus_idx[k])
        Pg_bus[i] += float(Pg_pu[k])
        Qg_bus[i] += float(Qg_pu[k])

    # Branch flow sums
    P_out = np.zeros(n_bus)
    Q_out = np.zeros(n_bus)
    max_overload = 0.0

    for l in range(branches.shape[0]):
        if int(branches[l, 10]) != 1:
            continue
        br = branches[l]
        P_ij, Q_ij, P_ji, Q_ji = compute_branch_flows_pu(Vm, Va, br, bus_map)
        fi = bus_map[int(br[0])]
        ti = bus_map[int(br[1])]
        P_out[fi] += P_ij
        Q_out[fi] += Q_ij
        P_out[ti] += P_ji
        Q_out[ti] += Q_ji

        rateA = float(br[5])
        if rateA > 0:
            Sij = math.hypot(P_ij, Q_ij) * baseMVA
            Sji = math.hypot(P_ji, Q_ji) * baseMVA
            overload = max(0.0, max(Sij, Sji) - rateA)
            if overload > max_overload:
                max_overload = overload

    # Mismatches
    P_mis = (Pg_bus - Pd_pu - Gs_pu * Vm * Vm) - P_out
    Q_mis = (Qg_bus - Qd_pu + Bs_pu * Vm * Vm) - Q_out

    max_p_mismatch_MW = float(np.max(np.abs(P_mis)) * baseMVA)
    max_q_mismatch_MVAr = float(np.max(np.abs(Q_mis)) * baseMVA)

    # Voltage violations
    Vmin = buses[:, 12]
    Vmax = buses[:, 11]
    v_over = np.maximum(Vm - Vmax, 0.0)
    v_under = np.maximum(Vmin - Vm, 0.0)
    max_v_violation = float(np.max(np.maximum(v_over, v_under)))

    return {
        "max_p_mismatch_MW": max_p_mismatch_MW,
        "max_q_mismatch_MVAr": max_q_mismatch_MVAr,
        "max_voltage_violation_pu": max_v_violation,
        "max_branch_overload_MVA": float(max_overload),
    }
