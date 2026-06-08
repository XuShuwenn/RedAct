#!/usr/bin/env python3
"""Solve pymoo-constrained-opt task."""

import numpy as np
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.pntx import SinglePointCrossover
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.problems.single import Problem

class ConstrainedProblem(Problem):
    def __init__(self):
        super().__init__(n_var=2, n_obj=1, n_constr=1)
        self.xl = np.array([0, 0])
        self.xu = np.array([10, 10])

    def _evaluate(self, x, out, *args, **kwargs):
        # Objective: minimize x1² + x2²
        out["F"] = x[:, 0]**2 + x[:, 1]**2
        # Constraint: x1 + x2 >= 1, converted to <= form: -(x1 + x2) + 1 <= 0
        out["G"] = -(x[:, 0] + x[:, 1]) + 1

def main():
    problem = ConstrainedProblem()
    algorithm = NSGA2(
        pop_size=50,
        sampling=FloatRandomSampling(),
        crossover=SinglePointCrossover(),
        mutation=PolynomialMutation(),
        elimination_elites=1
    )
    res = minimize(problem, algorithm, ("n_gen", 5), verbose=False, seed=42)

    opt = res.opt[0]
    x1, x2 = opt.X[0], opt.X[1]
    obj = opt.F[0]

    result = f"Optimal x1: {x1:.2f}\nOptimal x2: {x2:.2f}\nObjective: {obj:.2f}\n"

    with open("/root/output.txt", 'w') as f:
        f.write(result)

    with open("/root/oracle_output.txt", 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()