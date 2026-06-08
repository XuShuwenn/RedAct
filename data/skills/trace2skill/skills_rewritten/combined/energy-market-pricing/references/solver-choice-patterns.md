# Solver Choice Patterns

Use this reference when deciding whether the DC-OPF should be solved with a MATPOWER-aware OPF package, as an LP, or with a more general convex optimizer.

## Prefer native OPF workflows when available

When a reliable MATPOWER-aware solver/library is available, prefer it over rebuilding DC-OPF internals from scratch.

Benefits:
- Reduces indexing and formulation mistakes.
- Preserves standard handling of MATPOWER case data.
- May expose prices, flows, and limits directly in results.

Keep the task requirements unchanged:
- Solve the same DC-OPF market-clearing problem for base and counterfactual.
- Change only the specified line limit in the counterfactual.
- Validate that the solver run actually succeeded before reading outputs.

Environment/dependency selection pattern:
1. Before coding the full solution, probe the environment for the packages/solvers you plan to use.
2. Check which solver/modeling packages actually import successfully in the current runtime.
3. Prefer the strongest already-available exact workflow.
4. If a preferred package is absent, decide immediately whether to create an allowed local virtual environment or switch to another already-available exact workflow.
5. Do not design the whole solution around unverified dependencies or only discover the mismatch at first execution.

Practical rule:
- Validate imports / solver availability first, then commit to the implementation path.

Success pattern: if a hand-built model keeps failing or reporting infeasible despite input checks suggesting the case should solve, stop spending iterations on broad custom-formulation rewrites and switch to a standard domain OPF library that already implements the formulation robustly.

When that path is used successfully, prefer the library's solved-case economic/network fields directly, such as:
- bus LMP fields from the solved bus result table
- branch flow fields from the solved branch result table
- active branch limits from the solved case data used by that run

This is usually more reliable than reconstructing prices from dispatch or re-deriving congestion from separate debug arrays.

## Choose the model class from `gencost`

1. Inspect `gencost` directly.
2. Determine whether the production-cost objective is purely linear or includes quadratic/polynomial terms.
3. Match the solver to the actual objective; do not simplify the economics just to fit a preferred solver.

Use an LP workflow when:
- All generator cost functions are linear in output.
- In MATPOWER polynomial form, this commonly means the quadratic coefficient is zero for every generator.

Use a quadratic/general convex workflow when:
- Any generator has a nonzero quadratic term.
- The input encodes a higher-order or otherwise non-linear cost that must be preserved.

## Native outputs to prefer

Prefer solver-native fields for required report values whenever available:
- LMPs: bus shadow-price / lambda fields from the solved model.
- Reserve prices: reserve shadow-price / dual fields from the solved model.
- Branch flows: solver-reported branch flow fields.
- Thermal limits: active branch limit field used in the solved case.

Avoid:
- Reconstructing LMPs from generator dispatch or marginal costs.
- Recomputing branch flows only for reporting when the solver already provides them.
- Mixing solved outputs from one run with limits or metadata from another run.
- Dropping quadratic terms just to force an LP solver.
- Switching solvers before checking whether instability is caused by indexing, scaling, slack-bus treatment, or other formulation errors.

## Proven large-network pattern

For large MATPOWER-style DC-OPF instances:
- Build the exact DC-OPF with network constraints and reserve coupling.
- If `gencost` is linear, formulate the problem as a sparse LP.
- Prefer a sparse LP solver such as HiGHS when generic workflows show numerical trouble or poor scaling.

## Binding-line screening pattern

For each solved case:
1. Read branch flow magnitudes from solver output.
2. Read the corresponding active thermal limits.
3. Mark a line as binding when loading >= 99% of limit.
4. Confirm the reported constrained line matches the actual case definition after any counterfactual edits.

For this task's counterfactual claim, do one direct check on the edited line itself in addition to the full binding-line list: compare branch **64->1501** limit, flow magnitude, and `loading/limit` ratio in base vs counterfactual, and use that evidence when deciding whether congestion was relieved.

## Reporting guardrail

Before finalizing, confirm the report's prices and congestion indicators are traced to the solved case outputs, not to manual approximations, stale arrays, or debug-only calculations.

If two reported outputs conflict, write a tiny focused check script against the solved case rather than guessing which layer is wrong. Typical check: inspect the target line `64->1501` solved flow magnitude, loading ratio, limit, and binding classification in each scenario, then reconcile `binding_lines` and `congestion_relieved` with those exact values.