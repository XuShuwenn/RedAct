---
name: pymoo-optimization
description: "Solve multi-objective optimization problems using pymoo with NSGA-II to find Pareto front solutions."
---

# Multi-Objective Optimization with pymoo

## When to Use

- Find Pareto front for multi-objective problems
- Use NSGA-II algorithm for optimization
- Handle multiple objectives and bounds

## Problem Example

- f1(x) = (x1 - 2)²
- f2(x) = (x1 + 2)²
- Subject to: -10 ≤ x1 ≤ 10

## Using pymoo

```python
from pymoo.optimize import minimize
from pymoo.algorithms.nsga2 import NSGA2

# Define problem with 2 objectives
# Run NSGA-II: population=50, generations=3
```

## Output Format

To `/root/output.txt`:
```
{x1_value}={f1_value},{f2_value}
```

Sorted by x1 ascending, x1 to 3 decimal places.


## Pareto Front

- Non-dominated solutions
- Trade-off between objectives
- NSGA-II finds Pareto-optimal set

## Tips

- Use pymoo.algorithms.nsga2
- Set proper population and generations
- Extract Pareto front from results
