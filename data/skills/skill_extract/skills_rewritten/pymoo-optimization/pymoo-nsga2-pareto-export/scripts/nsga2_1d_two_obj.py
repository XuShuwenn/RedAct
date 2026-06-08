#!/usr/bin/env python3
"""Run NSGA-II (pymoo) for a 1D two-objective minimization problem and export.

This script accepts Python expressions for f1(x) and f2(x), decision variable
bounds, and NSGA-II parameters, then writes the non-dominated set sorted by x
as lines "{x}={f1},{f2}".

Example:
    python scripts/nsga2_1d_two_obj.py \
        --f1 '(x-2)**2' --f2 '(x+2)**2' \
        --xl -10 --xu 10 --pop 50 --gen 3 \
        --out output.txt --round-x 3

Note: This uses eval() for the provided expressions; use only with trusted input.
"""

import argparse
import sys
from typing import Callable, Optional

import numpy as np

try:
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.termination import get_termination
    from pymoo.optimize import minimize
except ImportError as e:
    print("ERROR: pymoo is required for this script.", file=sys.stderr)
    raise

# Local utilities (fallback if pareto_utils is not importable)

def is_nondominated(F: np.ndarray) -> np.ndarray:
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


def format_lines(X: np.ndarray, F: np.ndarray, round_x_decimals: int = 3,
                 round_f_decimals: Optional[int] = None):
    X = np.asarray(X, dtype=float).reshape(-1)
    F = np.asarray(F, dtype=float)
    lines = []
    for xi, fv in zip(X, F):
        xi_str = f"{xi:.{round_x_decimals}f}"
        f1, f2 = float(fv[0]), float(fv[1])
        if round_f_decimals is not None:
            f1_str = f"{f1:.{round_f_decimals}f}"
            f2_str = f"{f2:.{round_f_decimals}f}"
        else:
            f1_str = str(f1)
            f2_str = str(f2)
        lines.append(f"{xi_str}={f1_str},{f2_str}")
    return lines


def build_expr_func(expr: str) -> Callable[[float], float]:
    # Safe locals: expose math and numpy, plus x
    import math
    safe_globals = {"__builtins__": {}}
    safe_locals = {"math": math, "np": np}
    code = compile(expr, "<expr>", "eval")
    def f(x: float) -> float:
        safe_locals["x"] = x
        return float(eval(code, safe_globals, safe_locals))
    return f


class TwoObj1D(ElementwiseProblem):
    def __init__(self, xl: float, xu: float, f1: Callable[[float], float], f2: Callable[[float], float]):
        super().__init__(n_var=1, n_obj=2, n_constr=0, xl=xl, xu=xu)
        self._f1 = f1
        self._f2 = f2
    def _evaluate(self, x, out, *args, **kwargs):
        xi = float(x[0])
        out["F"] = np.array([self._f1(xi), self._f2(xi)], dtype=float)


def main():
    parser = argparse.ArgumentParser(description="NSGA-II for 1D, two objectives (minimization)")
    parser.add_argument("--f1", required=True, help="Python expression for f1(x)")
    parser.add_argument("--f2", required=True, help="Python expression for f2(x)")
    parser.add_argument("--xl", type=float, required=True, help="Lower bound for x")
    parser.add_argument("--xu", type=float, required=True, help="Upper bound for x")
    parser.add_argument("--pop", type=int, default=50, help="Population size")
    parser.add_argument("--gen", type=int, default=3, help="Number of generations")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument("--round-x", type=int, default=3, help="Decimals to round x for display")
    parser.add_argument("--round-f", type=int, default=None, help="Decimals to round objectives for display (optional)")
    args = parser.parse_args()

    f1 = build_expr_func(args.f1)
    f2 = build_expr_func(args.f2)

    problem = TwoObj1D(args.xl, args.xu, f1, f2)

    algorithm = NSGA2(pop_size=args.pop)
    termination = get_termination("n_gen", args.gen)

    res = minimize(problem, algorithm, termination=termination,
                   seed=args.seed if args.seed is not None else None,
                   save_history=False, verbose=False)

    X = np.array(res.X).reshape(-1)
    F = np.array(res.F).reshape(-1, 2)

    # Filter nondominated
    mask = is_nondominated(F)
    X = X[mask]
    F = F[mask]

    # Sort by raw x
    order = np.argsort(X)
    X_sorted = X[order]
    F_sorted = F[order]

    lines = format_lines(X_sorted, F_sorted, round_x_decimals=args.round_x, round_f_decimals=args.round_f)

    # Write file
    with open(args.out, "w") as fh:
        for line in lines:
            fh.write(line + "\n")

    # Basic verification
    if not np.all(np.diff(X_sorted) >= 0):
        print("WARNING: Exported lines are not strictly sorted ascending by x.", file=sys.stderr)
    print(f"Exported {len(lines)} non-dominated solutions to: {args.out}")


if __name__ == "__main__":
    main()
