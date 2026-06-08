#!/usr/bin/env python3
"""Branch flow utilities for AC pi-model with transformer tap and phase shift.

Functions are per-unit and compatible with MATPOWER-like data arrays.

- build_bus_id_to_idx(buses): map BUS_I to row index
- compute_branch_flows_pu(Vm, Va, branch_row, bus_map): returns (P_ij, Q_ij, P_ji, Q_ji)

Conventions:
- buses columns: [BUS_I, TYPE, PD, QD, GS, BS, AREA, VM, VA, BASEKV, ZONE, VMAX, VMIN]
- branch columns: [F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, RATE_C, TAP, SHIFT, BR_STATUS, ANGMIN, ANGMAX]
- Vm in pu, Va in radians
- SHIFT in degrees (in input); converted internally to radians for flows
- BR_B is total line charging susceptance; BR_B/2 is added to each side
"""
from __future__ import annotations
import math
from typing import Dict, Tuple
import numpy as np


def build_bus_id_to_idx(buses: np.ndarray) -> Dict[int, int]:
    """Return map from BUS_I to row index.
    buses: shape (n_bus, >=13)
    """
    return {int(buses[i, 0]): int(i) for i in range(buses.shape[0])}


def compute_branch_flows_pu(
    Vm: np.ndarray,
    Va: np.ndarray,
    branch_row: np.ndarray,
    bus_id_to_idx: Dict[int, int],
) -> Tuple[float, float, float, float]:
    """Compute per-unit branch flows (P_ij, Q_ij, P_ji, Q_ji).

    Uses the standard AC pi-model with transformer tap and phase shift.
    - If TAP is 0 (MATPOWER convention), use 1.0
    - SHIFT is in degrees; converted to radians
    - Series admittance computed safely (zero-impedance guarded)

    Returns:
      P_ij, Q_ij from i->j; P_ji, Q_ji from j->i (all in pu)
    """
    fi = int(branch_row[0])
    ti = int(branch_row[1])
    r = float(branch_row[2])
    br_x = float(branch_row[3])  # avoid name clash with decision vector 'x'
    bc = float(branch_row[4])
    tap = float(branch_row[8])
    shift_deg = float(branch_row[9])

    if abs(tap) < 1e-12:
        tap = 1.0
    shift = math.radians(shift_deg)

    # Series admittance
    if abs(r) < 1e-12 and abs(br_x) < 1e-12:
        g = 0.0
        b = 0.0
    else:
        denom = r * r + br_x * br_x
        g = r / denom
        b = -br_x / denom

    i = bus_id_to_idx[fi]
    j = bus_id_to_idx[ti]

    Vi = float(Vm[i])
    Vj = float(Vm[j])
    ai = float(Va[i])
    aj = float(Va[j])

    inv_t = 1.0 / tap
    inv_t2 = inv_t * inv_t

    d_ij = ai - aj - shift
    d_ji = aj - ai + shift  # = -d_ij

    cos_ij = math.cos(d_ij)
    sin_ij = math.sin(d_ij)
    cos_ji = math.cos(d_ji)
    sin_ji = math.sin(d_ji)

    ViVj = Vi * Vj

    # From-side (i -> j)
    P_ij = g * Vi * Vi * inv_t2 - ViVj * inv_t * (g * cos_ij + b * sin_ij)
    Q_ij = -(b + bc / 2.0) * Vi * Vi * inv_t2 - ViVj * inv_t * (g * sin_ij - b * cos_ij)

    # To-side (j -> i)
    P_ji = g * Vj * Vj - ViVj * inv_t * (g * cos_ji + b * sin_ji)
    Q_ji = -(b + bc / 2.0) * Vj * Vj - ViVj * inv_t * (g * sin_ji - b * cos_ji)

    return P_ij, Q_ij, P_ji, Q_ji
