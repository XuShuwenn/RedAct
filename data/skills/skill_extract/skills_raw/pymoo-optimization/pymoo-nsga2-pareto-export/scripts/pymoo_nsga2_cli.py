#!/usr/bin/env python3
"""
Generic NSGA-II runner for two-objective, one-variable problems using pymoo.

Usage:
  python pymoo_nsga2_cli.py \
    --f1 "(x1 - 2)**2" \
    --f2 "(x1 + 2)**2" \
    --xl -10 --xu 10 \
    --pop-size 50 --n-gen 3 \
    --seed 1 \
    --round-x 3 \
    --out /root/output.txt

Notes:
- Objectives are minimized by default.
- `f1` and `f2` are Python expressions in terms of `x1` and functions from the `math` module (e.g., sin, cos, exp). Example: "(x1-2)**2".
- Only one decision variable `x1` is supported to keep the interface simple.
- The script filters dominated points, sorts by x1 ascending, and writes lines as "{x1_rounded}={f1},{f2}".
"""

import argparse
import math
import sys
from typing import Callable, List, Tuple

import numpy as np

try:
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.optimize import minimize
except Exception as e:
    print("ERROR: pymoo is required to run this script.", file=sys.stderr)
    raise


# Safe evaluation of expressions in terms of x1 and math
ALLOWED_NAMES = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
ALLOWED_NAMES.update({
    # Common aliases
    "abs": abs,
    "min": min,
    "max": max,
})


def make_objective(expr: str) -> Callable[[float], float]:
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty objective expression provided.")

    def _obj(x1: float) -> float:
        # Evaluate with restricted globals and local x1
        return float(eval(expr, {"__builtins__": {}}, {**ALLOWED_NAMES, "x1": float(x1)}))

    return _obj


class OneVarTwoObjProblem(ElementwiseProblem):
    def __init__(self, f1: Callable[[float], float], f2: Callable[[float], float], xl: float, xu: float):
        super().__init__(n_var=1, n_obj=2, xl=np.array([float(xl)]), xu=np.array([float(xu)]))
        self._f1 = f1
        self._f2 = f2

    def _evaluate(self, x, out, **kwargs):
        x1 = float(x[0])
        out["F"] = [self._f1(x1), self._f2(x1)]


def dominates(a: np.ndarray, b: np.ndarray) -> bool:
    """Return True if vector a dominates vector b (minimization)."""
    return np.all(a <= b) and np.any(a < b)


def nondominated_filter(F: np.ndarray) -> np.ndarray:
    """Return boolean mask for nondominated rows of F (shape: n_points x n_obj)."""
    n = F.shape[0]
    mask = np.ones(n, dtype=bool)
    for i in range(n):
        if not mask[i]:
            continue
        for j in range(n):
            if i == j or not mask[j]:
                continue
            if dominates(F[j], F[i]):
                mask[i] = False
                break
    return mask


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="NSGA-II Pareto front exporter (1D, 2 objectives)")
    p.add_argument("--f1", required=True, help="Objective 1 expression in terms of x1")
    p.add_argument("--f2", required=True, help="Objective 2 expression in terms of x1")
    p.add_argument("--xl", type=float, required=True, help="Lower bound for x1")
    p.add_argument("--xu", type=float, required=True, help="Upper bound for x1")
    p.add_argument("--pop-size", type=int, default=50, help="NSGA-II population size")
    p.add_argument("--n-gen", type=int, default=3, help="Number of generations")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    p.add_argument("--round-x", type=int, default=3, help="Decimals for x1 display")
    p.add_argument("--out", default="/root/output.txt", help="Output file path")
    return p.parse_args()


def main():
    args = parse_args()

    if args.xl > args.xu:
        print("ERROR: xl must be <= xu", file=sys.stderr)
        sys.exit(1)

    f1 = make_objective(args.f1)
    f2 = make_objective(args.f2)

    problem = OneVarTwoObjProblem(f1, f2, args.xl, args.xu)
    algorithm = NSGA2(pop_size=args.pop_size)

    res = minimize(
        problem,
        algorithm,
        termination=("n_gen", args.n_gen),
        seed=args.seed,
        verbose=False,
    )

    X = np.asarray(res.X, dtype=float).reshape(-1, 1)
    F = np.asarray(res.F, dtype=float).reshape(-1, 2)

    # Remove dominated points if any
    mask = nondominated_filter(F)
    X = X[mask]
    F = F[mask]

    # Pair and sort by x1 ascending
    records: List[Tuple[float, float, float]] = [(float(x[0]), float(f[0]), float(f[1])) for x, f in zip(X, F)]
    records.sort(key=lambda t: t[0])

    # Write output
    try:
        with open(args.out, "w", encoding="utf-8") as fh:
            for x1, f1_val, f2_val in records:
                fh.write(f"{x1:.{args.round_x}f}={f1_val},{f2_val}\n")
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
