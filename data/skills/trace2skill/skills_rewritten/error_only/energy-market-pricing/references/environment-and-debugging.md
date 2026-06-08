# Environment and Debugging

Use this reference when the runtime may lack optimization libraries or when the first implementation attempt fails.

## Environment-first probe

Before committing to a solver stack:
1. Check imports for the exact packages you expect to use.
2. Check which solvers are actually callable from that stack.
3. If needed, create a local virtual environment and install dependencies there.
4. Re-run the probe before writing the full workflow.

Do not:
- Assume `numpy`, optimization packages, or power-system libraries are preinstalled.
- Start a large end-to-end solver build before confirming the chosen stack can run.
- Keep escalating implementation complexity after confirming the required tooling is unavailable.

## Strategy gate

Choose a path the environment can support:
- Preferred: MATPOWER-aware OPF workflow if available and it exposes exact required outputs.
- Otherwise: exact sparse LP/QP workflow supported by available packages/solvers.
- If dependencies are missing but installable: fix the environment first, then continue.

Do not replace the required market-clearing model with heuristics just because the environment is inconvenient.

## Debug-first rule

When the first concrete run fails, inspect that failure directly before redesigning the solution.

Examples of failures to debug in place:
- `ModuleNotFoundError`: fix environment or imports.
- `KeyError` / missing field: re-inspect `network.json` schema and metadata.
- Infeasibility: check statuses, slack-bus balance, reserve coupling, units, and line limits.
- Missing duals/prices: use a solver path that exposes them rather than inventing proxies.

Preferred sequence:
1. Reproduce the failure with a small, direct command.
2. Identify whether it is environment, schema, indexing, units, or formulation.
3. Fix that layer.
4. Re-run the same small test.
5. Only then resume the full two-scenario workflow.

## Incremental validation pattern

For complex cases, validate in this order:
1. Input schema and column mapping.
2. Status filtering and target branch identification.
3. Cost-model parsing from `gencost`.
4. One mathematically faithful small solve or formulation check.
5. Full base-case solve.
6. Counterfactual with only the verified `64->1501` limit change.

If a reduced model or small test already fails, do not launch a larger implementation until that failure is resolved.