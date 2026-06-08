# Multi-Objective Optimization with pymoo Task

Given a simple multi-objective optimization problem with two objectives:
- f1(x) = (x1 - 2)^2
- f2(x) = (x1 + 2)^2

Subject to: -10 <= x1 <= 10

Use the `pymoo` Python library to find the Pareto front solutions. Use NSGA-II algorithm with a population of 50 and 3 generations.

Write results to `/root/output.txt` with the Pareto front points (x1, f1, f2), one per line:
```
{x1_value}={f1_value},{f2_value}
```

For example:
```
-1.966=15.73,0.001
```

Sort the output by x1 value in ascending order. Round x1 to 3 decimal places.