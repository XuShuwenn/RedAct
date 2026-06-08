---
name: jax-computing-basics
description: "Execute multiple JAX-based computing tasks from problem.json specification, loading inputs and saving outputs."
---

# JAX Computing Basics

## When to Use

- Execute multiple computation tasks defined in JSON
- Use JAX for numerical computing (GPU/TPU acceleration)
- Load/save numpy arrays and perform array operations

## Input Format

`problem.json` structure:
```json
[
  {
    "id": "task_id",
    "description": "task description",
    "input": "data/x.npy",
    "output": "basic_reduce.npy"
  }
]
```

## Execution Protocol

- Before doing any computation, read task/system instructions for any required interaction protocol.
- Treat protocol requirements as blocking task requirements: required tool-call schema, allowed tools, message wrappers, path form, turn-by-turn execution rules, and any exact completion string override default habits.
- Before the first tool call, identify the mandated action format; if the environment requires a specific `Action:`/JSON schema, wrapper, field names, bash invocation pattern, or a single allowed tool, use only that exact interface throughout.
- Wait for each tool/action result before issuing the next action when the protocol requires turn-by-turn execution.
- Before the final response, re-check whether an exact completion token is required; if so, output exactly that token and nothing else.
- Do not substitute approximate formatting, alternate tool-call styles, equivalent-looking custom tags, native convenience wrappers, free-form summaries, or extra prose when an exact protocol is required.

## Workflow

1. Read `problem.json` completely before coding; if the file view is truncated, partial, elided, paginated, or cut off mid-entry, stop and fetch the remainder before planning or implementing anything. Do not implement any task until every entry's `id`, `description`, `input`, and `output` fields are fully visible and the total task count is confirmed from the file itself.
2. Parse `problem.json` into a runtime manifest and treat it as the authoritative source for task count, computation requirements, input paths, and output paths.
3. Iterate over every manifest entry programmatically; do not hardcode task IDs, filenames, paths, output names, or the number of tasks.
   - Build the task list directly from the parsed manifest itself; do not reconstruct missing entries from nearby files, prior examples, guessed conventions, or partial JSON content.
   - In code, read each task object's `input` and `output` fields from the parsed manifest; do not reconstruct filenames from `id` values or naming patterns.
   - Prefer one deterministic, rerunnable script that processes all manifest entries in one run, writes every required output, and then performs a verification pass over all expected outputs.
   - Before implementing custom loaders or utilities, check whether the workspace provides helper modules (for example, `jax_skills.py` or similar support code) and reuse them when they already cover manifest parsing, loading, saving, or standard array operations.
   - Before running any generated script, confirm the available interpreter/runner in the environment rather than assuming a command exists.
4. For each task from the parsed manifest:
   - Load input data from the exact `input` path specified for that task.
   - If instructions provide absolute paths or require absolute-path usage, preserve and use those exact absolute paths for reads, writes, and script invocation.
   - Re-read the task's exact `description` immediately before implementing that task and implement only what it explicitly requests.
   - Map the requested computation to the most direct JAX primitive that exactly matches it (for example: `jnp` reductions for sums/means, `vmap` for mapped independent work, `grad` for differentiation, `lax.scan` for recurrences, `jit` when compiled execution is requested or useful).
   - Inspect input schema before coding against it:
     - `.npy`: check shape, dtype, and representative values when needed to disambiguate semantics
     - `.npz`: list actual keys first, then load by confirmed key names; inspect shapes/dtypes of relevant arrays and any special fields such as `init` or other metadata/initialization parameters
   - For `.npz` or multi-tensor tasks, inspect and note keys, shapes, and dtypes before writing task logic; do not use guessed names unless they were observed.
   - For linear algebra, batching, reductions, sequence/model-style computations, broadcasting-sensitive logic, labels/targets, losses, or gradients, inspect operand shapes and target encoding first and choose axes, scan order, transpose/orientation behavior, and formulas from the observed data and the exact description, not from naming conventions.
   - Do not infer the required computation from task IDs, filenames, shapes, neighboring tasks, inspected keys, or common JAX/ML conventions.
   - Do not fill in unspecified mathematical or model details from habit or likely patterns. Loss definitions, label conventions, activation functions, recurrence equations, reduction choices/axes, returned state, and layer structure must come from the task's exact `description`, not from names like `grad_logistic`, `scan_rnn`, or `jit_mlp`.
   - If multiple interpretations remain plausible, test the smallest reasonable set of candidates against observed data, expected output structure, or other authoritative artifacts before choosing one; otherwise stop and recover/confirm the specification rather than guessing.
   - Before any matrix multiplication, batched linear algebra, scan, or neural-network layer, verify operand shapes explicitly and confirm whether weights are stored as `(in, out)` or `(out, in)` before adding any transpose.
   - If execution reveals missing keys, unexpected target encodings, shape mismatches, or other schema surprises, stop and re-inspect the input file; do not patch by guessing alternate key names or conventions.
   - If the visible description is incomplete, ambiguous, or does not explicitly specify a needed formula/reduction/layout detail, stop and recover the authoritative task text before implementing.
   - Save the result to the exact `output` path specified for that task.
5. Before declaring success, perform a coverage check against the full manifest: confirm every entry in `problem.json` was processed, no entry was skipped because of truncated file views, and each required output was written to the exact specified filename/path.
6. Then validate semantics, not just execution: for each task, confirm the saved result matches the exact description's requested operation/formula, relevant axes, output shape/dtype, and target filename/path.
   - Do not treat `script ran`, truncated logs, file existence, a successful script exit, or a bulk `ls` check as sufficient evidence.
   - Reload each expected output path from the manifest and confirm the file exists, is readable, and has the expected shape/dtype or representative values implied by the task.
   - Re-read each task description during validation and inspect representative output values, small recomputations, or candidate-formula checks when feasible to confirm the implemented formula matches the specification.
   - For floating-point validation, prefer tolerance-aware comparisons such as `np.allclose` unless the specification explicitly requires exact equality.
7. Before the final response, re-check any required interaction protocol from the task/system instructions and emit the exact mandated completion string or action format verbatim.
8. Use `jax.numpy` for array operations.

## JAX Features

- `jax.numpy`: NumPy-compatible API on GPU/TPU
- `jax.jit`: JIT compilation for speed
- `jax.grad`: Automatic differentiation
- `jax.vmap`: Vectorization

## Tips

- Use `np.load()` for .npy files
- Ensure data types match for JAX
- Use `jax.block_until_ready()` for benchmarking

- For `.npz` files, check available keys with something like `np.load(path).files` before assuming names such as `X`, `y`, `x_seq`, or `h0`.
- Prefer a quick inspection step for unfamiliar inputs: keys, shapes, and dtypes before writing JAX logic.
- Before matrix multiplications or batched linear algebra, confirm operand shapes and whether weights are stored as `(in, out)` or `(out, in)`; do not add transposes unless inspected shapes require them.
- Do not hardcode output filenames unless they were parsed from the task metadata.
- Do not treat "file exists" or successful execution as sufficient validation; inspect representative values, shapes, or small recomputations to confirm the saved result matches the requested computation.
- If any part of the specification is ambiguous or not fully visible, stop and retrieve the authoritative JSON text instead of guessing.

- If `problem.json` or any instruction file is only partially visible, continue reading until the full authoritative text is available; never guess missing tasks, descriptions, formulas, or paths.
- A reliable pattern is: parse manifest -> loop over tasks -> load `task["input"]` -> compute only from `task["description"]` -> save to `task["output"]` -> verify coverage and semantics for all tasks.
- If the workspace includes helper code for JAX tasks, inspect it early and reuse compatible helpers for I/O or common operations instead of rewriting standard pieces differently.
- For every task input, prefer a quick inspection step: confirm keys, shapes, dtypes, and a few representative values before finalizing tensor conventions.
- For classification, loss, or gradient tasks, do not assume a standard objective from the task name alone; verify whether targets are encoded as `{0,1}`, `{-1,1}`, class indices, or one-hot vectors, and choose the matching formula.
- Treat protocol compliance as part of correctness: exact completion tokens and required action/message formats are mandatory, not optional.
- After saving an output, reload it and sanity-check shape, dtype, and representative values; for float results, prefer tolerance-aware comparison over raw exact equality.
