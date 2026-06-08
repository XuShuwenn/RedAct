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
- If the environment mandates a specific tool-call schema, message format, or exact completion string, follow it exactly.
- Do not substitute approximate formatting, free-form summaries, or extra prose when an exact protocol is required.

## Workflow

1. Read `problem.json` completely before coding; if the file view is truncated or partial, fetch the remainder until every task's `id`, `description`, `input`, and `output` fields are visible.
2. Treat `problem.json` as the authoritative task manifest for task count, computation requirements, input paths, and output paths.
3. Iterate over every manifest entry programmatically; do not hardcode task IDs, filenames, paths, or the number of tasks.
4. For each task:
   - Load input data from the exact `input` path specified for that task.
   - Re-read the task's exact `description` and implement only what it explicitly requests.
   - Inspect input schema before coding against it:
     - `.npy`: check shape and dtype
     - `.npz`: list actual keys first, then load by confirmed key names
   - Do not infer the required computation from task IDs, filenames, shapes, neighboring tasks, or common JAX/ML conventions.
   - Save the result to the exact `output` path specified for that task.
5. Before declaring success, verify every manifest entry was processed and each saved output matches the task description, including the requested operation/formula, relevant axes, output shape/dtype, and target filename/path.
6. Use `jax.numpy` for array operations.

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
