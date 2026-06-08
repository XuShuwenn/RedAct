# Network Input Inspection for MATPOWER-Style JSON

Use this before writing or patching the AC-OPF model when `network.json` stores compact arrays such as `bus`, `gen`, `branch`, and `gencost`.

## Goal
Prevent formulation mistakes caused by guessing array meanings, bus roles, or cost-table layout.

## Inspect before modeling
1. Read enough of `network.json` to confirm which top-level tables exist.
2. Record the shape of `bus`, `gen`, `branch`, and `gencost`.
3. Identify the bus-type column and determine which bus is the slack/reference bus.
4. Confirm which columns provide:
   - bus voltage limits and demand
   - generator bus mapping, `Pmin/Pmax`, `Qmin/Qmax`, voltage setpoint, status
   - branch endpoints, status, series parameters, tap/shift if present, and thermal ratings
   - generator cost model type and coefficient ordering
5. Only then map variables, bounds, and objective terms into code.

## Minimum sanity checks
- Number of buses, generators, and branches is consistent with indexing used in code.
- Every online generator maps to a valid bus.
- Exactly the intended reference/slack treatment is used.
- `gencost` rows align with generator rows before computing the objective.
- Units/per-unit conversions are explicit before balancing MW/MVAr quantities.

## Do not
- Do not infer column meanings from memory alone when the file can be inspected.
- Do not assume the first bus is the slack/reference bus without checking the bus-type data.
- Do not build the objective before confirming how `gencost` rows align to generators.
- Do not start debugging nonlinear convergence until this structural mapping is confirmed.