---
name: r2r-mpc-control
description: "Implement MPC controller for roll-to-roll manufacturing to stabilize web tensions during roller changes."
---

# Roll-to-Roll MPC Controller

## When to Use

- Control web tensions in manufacturing
- Implement Model Predictive Control
- Handle roller change disturbances


## Execution Protocol

## Execution Protocol

- Follow any task- or environment-specific interaction/tool protocol exactly; those instructions override this skill's default workflow.
- If the environment mandates a tool/action format, JSON schema, path convention, single-action cadence, or exact completion string, use it literally and consistently.
- Treat procedural compliance as part of correctness: technically correct controller work can still fail if the required interaction/completion format is wrong.
- Do not declare success from partial stdout, initialization messages, or truncated output alone; verify results from saved artifacts first.
- If an exact completion token is required, output that token verbatim as the final response and nothing else.

## Problem

- 6-section manufacturing line
- Section 3 roller changes from 20N to 44N at t=0.5
- Must stabilize tensions with MPC

## Workflow

1. Derive linearized state-space model at reference operating point
1a. Inspect `r2r_simulator.py` enough to confirm the actual class/interface before coding: constructor, state representation, how to advance simulation, what outputs are returned, and how disturbances/reference values are exposed. Do not assume methods or return signatures from naming alone.
2. Design an actual MPC controller with horizon N in [3, 30]: formulate a finite-horizon receding-horizon optimization and solve it at each control step. Do not substitute a fixed LQR/state-feedback law and label it MPC.
3. Run controller for at least 5 seconds
3a. Treat the full 5-second closed-loop simulation as the acceptance test. Use short smoke tests only for debugging; make final tuning and validation decisions from the required full simulation and reported metrics.
4. Log tensions and compute metrics
5. Reopen generated artifacts and verify that `controller_params.json`, `control_log.json`, and `metrics.json` were created from the latest successful run, are populated, and are structurally correct.
6. Compare computed metrics against every stated target before declaring success; if any requirement fails or output is truncated/unverified, rerun or continue debugging.
7. If behavior is unstable, biased, produces `nan`/`inf`, or suspicious metrics, validate the model/control formulation before further retuning.

## Required Outputs

### controller_params.json
```json
{
  "horizon_N": 9,
  "Q_diag": [100.0, ...],
  "R_diag": [0.033, ...],
  "K_lqr": [[...], ...],
  "A_matrix": [[...], ...],
  "B_matrix": [[...], ...]
}
```

### control_log.json
```json
{"phase": "control", "data": [{"time": 0.01, "tensions": [...], ...}]}
```

### metrics.json
```json
{"steady_state_error": 0.5, "settling_time": 1.0, ...}
```


- Generate `controller_params.json`, `control_log.json`, and `metrics.json` from the final selected controller run, not from earlier trial scripts or stale artifacts.
- Keep artifacts internally consistent with the implemented controller. If runtime control is MPC/state-feedback, export matching parameters; do not label a PI/heuristic or fixed LQR controller as MPC.
- `control_log.json` must contain control-phase data spanning **at least 5.00 seconds**; do not treat 4.99 s as acceptable unless the task explicitly allows tolerance.
- Before completion, validate each artifact against the spec: confirm required top-level keys are present, matrices/vectors have plausible dimensions, and reported metrics are consistent with the logged trajectories.
- Do not change metric definitions, thresholds, or settling-time rules to make a weak controller look acceptable; fix controller behavior instead.

## Performance Targets

- Mean steady-state error < 2.0N
- Settling time < 4.0s
- Max tension < 50N, Min tension > 5N


- Treat these thresholds as pass/fail acceptance criteria for completion; do not declare success if observed metrics miss a required threshold.
- Measure settling time from the disturbance time (`t = 0.5`) to when the affected tensions enter and remain within the chosen tolerance band, unless the task explicitly specifies a different definition.
- If computed metrics conflict with the logged trajectory, treat the result as invalid and debug the controller/model before claiming success.

## Tips

- Use r2r_simulator.py (don't modify it)
- Linearize around operating point
- Use scipy for control design


- Implement actual MPC: discretize the linearized model, define prediction horizon `N`, construct stage/terminal costs, solve the finite-horizon problem each control step, and apply only the first control move.
- LQR may be useful for terminal cost or comparison, but do not present pure fixed-gain LQR/state-feedback as MPC.
- When runs show `nan`, extreme tensions, persistent offsets, or instability, check the linearization operating point, discretization, equilibrium/input offsets, and feedback sign/structure before more tuning.
- Validate that the linearized model predicts simulator behavior qualitatively near the reference point.
- Prefer reading `metrics.json` and `control_log.json` over abbreviated console output; cross-check metrics against raw trajectories before reporting success.
- For fixed-step runs, verify whether logging occurs before or after each simulator step and confirm first/last timestamps explicitly to avoid off-by-one duration mistakes.
- Do not clamp or overwrite simulator state/tension values after stepping just to keep logs or metrics in range; fix the controller/model instead.
