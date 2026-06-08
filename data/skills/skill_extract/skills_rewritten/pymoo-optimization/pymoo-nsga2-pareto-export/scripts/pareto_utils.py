#!/usr/bin/env python3
"""Pareto utilities: nondomination check, sorting assertions, and formatting.

This module is generic for minimization of two or more objectives.
"""

import re
from typing import Iterable, List, Optional, Tuple

import numpy as np


def is_nondominated(F: np.ndarray) -> np.ndarray:
    """Return a boolean mask of points that are non-dominated (minimization).

    A point i is dominated if there exists j such that F[j] <= F[i] for all
    objectives and F[j] < F[i] for at least one objective.
    """
    F = np.asarray(F, dtype=float)
    n = len(F)
    keep = np.ones(n, dtype=bool)
    for i in range(n):
        if not keep[i]:
            continue
        for j in range(n):
            if i == j:
                continue
            if np.all(F[j] <= F[i]) and np.any(F[j] < F[i]):
                keep[i] = False
                break
    return keep


def assert_sorted_by_x(X: np.ndarray) -> None:
    """Raise AssertionError if X is not sorted ascending."""
    X = np.asarray(X, dtype=float).reshape(-1)
    if not np.all(np.diff(X) >= 0):
        raise AssertionError("Decision variable values are not sorted ascending.")


def format_lines(X: np.ndarray, F: np.ndarray, round_x_decimals: int = 3,
                 round_f_decimals: Optional[int] = None) -> List[str]:
    """Format lines as "{x}={f1},{f2}" with x rounded and optional rounding for F.

    Parameters:
        X: (n,) decision variable values
        F: (n, m) objective values; if m != 2, only the first two will be used
        round_x_decimals: decimals for x rounding
        round_f_decimals: if provided, round f1 and f2 to this many decimals
    """
    X = np.asarray(X, dtype=float).reshape(-1)
    F = np.asarray(F, dtype=float)
    if F.ndim != 2 or F.shape[0] != X.shape[0]:
        raise ValueError("F must be 2D with same number of rows as X.")

    lines = []
    for xi, fvals in zip(X, F):
        f1, f2 = fvals[0], fvals[1]
        xi_str = f"{xi:.{round_x_decimals}f}"
        if round_f_decimals is not None:
            f1_str = f"{f1:.{round_f_decimals}f}"
            f2_str = f"{f2:.{round_f_decimals}f}"
        else:
            # Use repr-like formatting for robustness without forcing decimals
            f1_str = f"{f1}"
            f2_str = f"{f2}"
        lines.append(f"{xi_str}={f1_str},{f2_str}")
    return lines


LINE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*=\s*(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\s*$")


def parse_line(line: str) -> Tuple[float, float, float]:
    """Parse a line "x=f1,f2" and return (x, f1, f2).
    Raises ValueError if the format is invalid.
    """
    m = LINE_RE.match(line)
    if not m:
        raise ValueError(f"Invalid line format: {line!r}")
    x_str, f1_str, f2_str = m.groups()
    return float(x_str), float(f1_str), float(f2_str)


def verify_export_lines(lines: Iterable[str]) -> None:
    """Validate that lines adhere to the schema and are sorted ascending by x."""
    xs: List[float] = []
    for line in lines:
        x, f1, f2 = parse_line(line)
        xs.append(x)
    assert_sorted_by_x(np.array(xs))
