# DC-OPF Guardrails

Use this reference when implementing the market-clearing model or constructing network matrices.

## Faithful formulation

Required outputs must come from the specified DC-OPF with reserve co-optimization, not from approximations.

Do:
- Solve base and counterfactual with the same model, changing only the specified line limit.
- Compute LMPs from the optimization model solution.
- Report binding lines from solved flows versus thermal limits.

Do not:
- Substitute economic dispatch plus guessed congestion effects.
- Infer flows from load differences or other heuristics.
- Hard-code reserve MCP or assign identical/flat LMPs without model support.

- Include the slack/reference bus in the nodal balance equations just like every other bus.
- Add the reference-angle fixing constraint separately rather than using it as a substitute for nodal balance.
- Keep one shared parsing/model-building code path, then run it twice: once with original data and once with only the **64→1501** thermal limit increased by 20%.
- Keep direct references to the bus-balance constraints and reserve-requirement constraint so their duals can be read reliably after solving.
- Verify dual sign conventions, and if the formulation uses per-unit physics, verify any needed `baseMVA` conversion before reporting LMPs or reserve MCP.
- If exact market prices are required, use a solver/modeling path that exposes the needed duals or equivalent exact prices; otherwise change the implementation instead of inventing proxy prices.
- For large systems, assemble sparse matrices (`generator-to-bus`, `Bbus`, `Bf`, or PTDF if used) instead of dense arrays.
- If packages are missing, recover with a local virtual environment instead of replacing the DC-OPF with a heuristic shortcut.

## MATPOWER indexing

MATPOWER bus identifiers are labels, not guaranteed zero-based or contiguous array indices.

Pattern:
1. Extract bus IDs in model order.
2. Build `bus_to_idx = {bus_id: i for i, bus_id in enumerate(bus_ids)}`.
3. Convert every branch endpoint and generator bus from bus ID to internal index before filling matrices.
4. Build `Bbus`, `Bf`, or PTDF only with internal indices.

Wrong:
- `Y[f_bus, t_bus] += ...` using raw bus numbers.

Right:
- `i = bus_to_idx[f_bus]`
- `j = bus_to_idx[t_bus]`
- `Y[i, j] += ...`


Also inspect the source data before coding matrices: print bus IDs, generator-bus assignments, branch endpoints, status flags, rating fields, and the target **64→1501** branch row so indexing and field assumptions are validated against the actual case.

Quick validation pattern before full matrix assembly:
1. Print the number of buses and the max/min raw bus IDs.
2. Check whether raw IDs are contiguous; assume they are not unless proven otherwise.
3. Pick a few generators and branches and verify `bus_to_idx[row_bus_id]` succeeds before building `Bbus`/`Bf`/PTDF.
4. Fail fast on any unmapped endpoint or out-of-range internal index instead of continuing to a large solve.

If integrating another network library, also test one minimal branch or line creation call with all required arguments before attempting whole-case conversion.


## Efficient input inspection

When `network.json` is too large to read comfortably, inspect only what you need first.

Pattern:
1. Read top-level keys and array sizes.
2. Inspect `column_info` / metadata if present.
3. Pull only the relevant rows/fields for `bus`, `gen`, `branch`, `gencost`, reserve data, and the target branch **64→1501**.
4. Confirm the exact thermal-limit field and branch row for **64→1501** before implementing the counterfactual.
5. Keep this inspection separate from the optimization code so the model uses verified mappings rather than guesses.
## Minimum sanity checks before reporting

Before trusting results, check:
- Objective/total generation cost is positive and within a plausible range.
- Power balance holds.
- Number of binding lines is not wildly implausible.
- Counterfactual changes at least the modified line limit and any dependent outputs when that constraint is active.
- If results look broken, stop and debug the formulation; do not write the final report from those outputs.

- Verify solve logs are complete enough to show a normal optimizer exit; do not trust runs with abruptly truncated console output unless a fresh rerun confirms successful completion.
- Distinguish schema validation from model validation: confirmed JSON structure or field counts do not prove the OPF/reserve formulation, prices, or counterfactual impacts are correct.
- If reserve inputs are missing or ambiguous, do not fabricate reserve costs or coupling rules; return to the input schema and metadata first.
- If debugging, prefer a reduced but still exact DC-OPF/reserve model to test data mapping, balances, line constraints, and price extraction; never switch to heuristic pricing or flow approximations as a substitute for the required market-clearing model.
- Confirm required input data for the chosen formulation exists before solving, especially generator cost data and any reserve-capacity / reserve-requirement fields.
- For the target counterfactual, record the original limit of branch `64->1501`, then verify the edited limit is exactly `1.2x` that value and that no other branch limit changed.
- If one suitable solver fails, rerun the same formulation with a fallback solver before changing the model.
- Accept results only from solved statuses with complete primal and dual information needed for reporting.
- Inspect a few representative LMPs and the reserve MCP immediately after solving; if they are implausibly scaled, inspect `baseMVA` and convert optimization duals to reported `$ / MWh` units consistently before writing the report.
- Check the scenario-specific claim on the modified line: whether it is binding in the base case, whether that changes in the counterfactual, and whether `congestion_relieved` agrees with those solved flows.
- When the report is long, confirm deliverables by reading targeted sections/keys instead of assuming a truncated full-file print proves completeness.

Add an explicit post-solve validation pass before trusting results:
1. Confirm solver termination is successful **and** not flagged inaccurate or numerically unreliable.
2. Compute maximum nodal balance residual from the solved dispatch/flows.
3. Compute maximum branch thermal-limit violation from solved flows and active limits.
4. Check generator outputs remain within min/max bounds and reserve requirements are satisfied.
5. Reject the run if any of the above fail beyond tolerance; do not finalize from a merely existing report file.

Do not downgrade these checks to optional sanity tests. They are acceptance criteria for whether the reported prices, congestion, and impact analysis are usable.

- If you generated a script to run the OPF, quickly read back the saved file before execution to confirm the on-disk contents are real source code and include the intended solve/report logic.
- If you notice implausible prices or scaling red flags during review, stop treating the outputs as final; debug units, `baseMVA`, dual conversion, and constraint activity first, or explicitly report that the results remain unvalidated.