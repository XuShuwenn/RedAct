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


Practical probe pattern before main coding:
- Run one short command that imports the intended package set and, if applicable, checks solver availability.
- If imports fail, avoid writing the whole workflow against that stack first.
- Prefer a verified exact stack already present in the runtime over trying multiple installation paths.
- Attempt environment setup only when it is likely to succeed quickly and is allowed by the runtime constraints.
- Print or otherwise confirm the interpreter path you will use for the final run so the solve does not silently switch back to system Python after package installation.
- In managed environments, prefer `python3 -m venv /root/.venv` (or equivalent local venv) over repeated system-package install attempts.
- After installation, verify the exact runtime you will use with a one-line import/solver probe from the venv before returning to the full workflow.

This preserves a proven workflow: when system installation is blocked, create `/root/.venv`, install there, verify imports from that interpreter, then run the full solve from the same interpreter.

## Strategy gate

Choose a path the environment can support:
- Preferred: MATPOWER-aware OPF workflow if available and it exposes exact required outputs.
- Otherwise: exact sparse LP/QP workflow supported by available packages/solvers.
- If dependencies are missing but installable: fix the environment first, then continue.

Do not replace the required market-clearing model with heuristics just because the environment is inconvenient.

Decision rule after the environment probe:
- If an exact workflow is supported now, use it and keep the first run small.
- If the preferred workflow is unsupported but a local venv is allowed, set it up once, re-probe, and then commit.
- If neither the current runtime nor a local venv supports an exact workflow, do **not** sink time into a hand-built large solver that has not been proven runnable; explicitly treat the environment as the blocker.

Anti-pattern to avoid:
- Discover missing packages, then continue writing the same full-scale implementation anyway.
- Let a long background run substitute for proof that the chosen path is actually viable.

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

- Do not respond to `ModuleNotFoundError` or managed-Python errors with vague commands like "install required packages." Use explicit, reproducible commands, then re-run a small import probe to confirm the environment is fixed.
- Do not treat solver infeasibility as a reason to rewrite the whole solution immediately. First isolate whether the issue is schema mapping, status filtering, bounds/units, slack-bus balance omission, reserve coupling, or another specific formulation bug.
- After writing or rewriting a driver script during debugging, read the on-disk file back once before execution to confirm the saved contents match the intended executable code.

## Incremental validation pattern

For complex cases, validate in this order:
1. Input schema and column mapping.
2. Status filtering and target branch identification.
3. Cost-model parsing from `gencost`.
4. One mathematically faithful small solve or formulation check.
5. Full base-case solve.
6. Counterfactual with only the verified `64->1501` limit change.

If a reduced model or small test already fails, do not launch a larger implementation until that failure is resolved.

7. Consolidate the final base solve, counterfactual solve, comparison metrics, and report writing into one reproducible script or driver once the small checks pass.

This reduces handoff mistakes between ad hoc commands and helps ensure the same parsed case, target branch identity, and reporting logic are used consistently across both scenarios.