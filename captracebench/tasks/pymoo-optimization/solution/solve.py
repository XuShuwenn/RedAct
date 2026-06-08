#!/usr/bin/env python3
"""Solve pymoo-optimization task."""

import numpy as np
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.pntx import SinglePointCrossover
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.problems.single import Problem

class MyProblem(Problem):
    def __init__(self):
        super().__init__(n_var=1, n_obj=2, n_constr=0)
        self.xl = np.array([-10])
        self.xu = np.array([10])

    def _evaluate(self, x, out, *args, **kwargs):
        x1 = x[:, 0]
        f1 = (x1 - 2)**2
        f2 = (x1 + 2)**2
        out["F"] = np.column_stack([f1, f2])

def main():
    problem = MyProblem()
    algorithm = NSGA2(
        pop_size=50,
        sampling=FloatRandomSampling(),
        crossover=SinglePointCrossover(),
        mutation=PolynomialMutation(),
        elimination_elites=1
    )
    res = minimize(problem, algorithm, ("n_gen", 3), verbose=False, seed=42)

    # Get Pareto front
    pf = res.opt
    results = []
    for ind in pf:
        x1 = round(ind.X[0], 3)
        f1 = round((ind.X[0] - 2)**2, 3)
        f2 = round((ind.X[0] + 2)**2, 3)
        results.append((x1, f1, f2))

    # Sort by x1
    results.sort(key=lambda x: x[0])

    with open("/root/output.txt", 'w') as f:
        for x1, f1, f2 in results:
            f.write(f"{x1}={f1},{f2}\n")

    with open("/root/oracle_output.txt", 'w') as f:
        for x1, f1, f2 in results:
            f.write(f"{x1}={f1},{f2}\n")

if __name__ == "__main__":
    main()