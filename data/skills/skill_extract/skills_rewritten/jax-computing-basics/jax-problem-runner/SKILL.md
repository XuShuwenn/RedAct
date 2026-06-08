---
name: jax-problem-runner
description: "Process tasks listed in a config (e.g., problem.json), load inputs, apply JAX computations (reduce/map/grad/scan/jit), and save outputs with verification."
---

# JAX Configured Task Runner

Skill for reliably executing a list of JAX computations described in a configuration file (e.g., problem.json). It emphasizes robust input loading (.npy/.npz), correct use of JAX primitives (reductions, vectorized mapping, automatic differentiation, scans, and JIT), and deterministic output saving with verification.

## When to Use

Use this skill when you need to:
- Load multiple tasks from a config file specifying input paths, task descriptions, and output paths
- Implement JAX computations such as reductions, elementwise maps, gradients via autodiff, sequential computations via scan, and JIT-compiled model inference
- Save results deterministically to specified output files and verify shapes and existence

## Core Workflow

1. Read and validate the configuration
   - Load the JSON file. Expect a list of task objects with fields like id, description, input, output.
   - Validate required fields for each task. Log the task id and description.

2. Load inputs robustly
   - If input ends with .npy: load as a single array.
   - If input ends with .npz: load as a bundle; inspect available keys via .files and decide which arrays to use (e.g., X, y, params). Do not assume key names; inspect and assert shapes.
   - Convert NumPy arrays to JAX arrays immediately with jnp.array to ensure downstream JAX ops and grad work correctly.

3. Determine the computation pattern from the description
   - Parse the textual description for cues like reduce (mean/sum/max with axis), elementwise map (square, relu, etc.), gradient (e.g., logistic loss wrt weights), scan (RNN-like forward pass), JIT-compiled model (MLP forward pass).
   - Prefer pure, side-effect-free functions for core math. Keep I/O outside of JIT and grad.

4. Implement the computation with stable, shape-aware JAX code
   - Reduction: jnp.reduce ops with explicit axis and keepdims as needed. Example: row-wise mean is axis=1 on a 2D input.
   - Elementwise map: prefer vectorized primitives (e.g., jnp.square). If vectorization across batch is needed, use jax.vmap with explicit in_axes/out_axes.
   - Gradient: define loss(params, ...) that returns a scalar. Use numerically stable forms (e.g., softplus/logaddexp for logistic). Use jax.grad(loss) w.r.t. the intended parameter argument.
   - Scan: use jax.lax.scan with a step function (carry, x) -> (carry, y). Ensure carry and outputs have consistent dtypes/shapes. Initialize carry explicitly.
   - JIT: JIT only the pure compute function, not file I/O. Keep shapes static or treat dynamic dimensions as data.

5. Save outputs deterministically
   - Always convert device arrays to host with jax.device_get before saving.
   - Ensure the output directory exists; then save to the exact path requested using NumPy’s .npy format.

6. Verify
   - Confirm that each output file exists and can be reloaded.
   - Check shapes and dtypes match expectations based on the computation. For simple tasks, cross-check with a NumPy equivalent on small slices.

## Verification

Perform these checks per task:
- Input validation: paths exist; .npz keys inspected; shapes match the intended operation (e.g., matrix multiplication dimensions align, reduction axis is valid).
- Numeric correctness: 
  - For reductions and elementwise maps: spot-check a few entries using a NumPy equivalent on a small subset.
  - For gradients: run a finite-difference check on a tiny subset/dimension to verify grad sign/magnitude is plausible.
  - For scans: assert that the step function produces consistent shapes; optionally run a tiny T to inspect the first few states.
- Output integrity: file exists; reloadable via np.load; shape and dtype match the compute result.
- Determinism: rerun produces identical outputs (no RNG dependency unless required by task).

## Common Pitfalls and Remedies

- Misreading .npz contents
  - Pitfall: assuming key names. Remedy: inspect bundle.files and print shapes; select keys explicitly and assert shapes.

- Mixing NumPy and JAX in differentiable paths
  - Pitfall: using numpy ops in loss functions breaks grad. Remedy: convert to jnp arrays and use jnp/jax.nn everywhere in compute/grad functions.

- Incorrect matrix orientations
  - Pitfall: transposing arbitrarily to “make shapes work.” Remedy: reason from shapes; prefer x @ W where x is [..., D] and W is [D, H] for forward passes; add assertions to catch mismatches.

- Numeric instability in logistic loss
  - Pitfall: using log(1 + exp(z)) directly. Remedy: use jnp.logaddexp(0., z) or jax.nn.softplus for stability.

- Misusing vmap
  - Pitfall: wrong in_axes causing unexpected broadcasting or shape changes. Remedy: define the scalar function and specify in_axes matching the intended batched dimension; verify output shapes.

- lax.scan signature/shape errors
  - Pitfall: returning mismatched carry/output structures. Remedy: ensure step returns (new_carry, y) and that y’s shape is consistent across time steps.

- JIT around I/O or Python objects
  - Pitfall: jitting functions that open files or manipulate Python dicts. Remedy: JIT only pure numerical functions; pass arrays and parameter tensors as inputs.

- Saving without host transfer or missing directories
  - Pitfall: saving device arrays directly or to non-existent paths. Remedy: jax.device_get before np.save; os.makedirs(os.path.dirname(path), exist_ok=True).

## Success Criteria

- Every task’s output file is created at the specified path and reloadable.
- Output shapes/dtypes align with the computation intent and input shapes.
- Computations use appropriate JAX primitives (jnp, vmap, grad, lax.scan, jit) as required by the task description.
- Optional: spot-checks and finite-difference tests pass within reasonable tolerances on small subsets.

## Optional Script Usage

You can import helpers from scripts/jax_task_utils.py to streamline loading, computing, and saving:

- Robust I/O: load_input(path), save_output(path, arr)
- Common computations: row_reduce_mean(x, axis), elementwise_square(x)
- Differentiation: logistic_loss_grad(w, X, y)
- Sequential models: rnn_scan_tanh(params, xs, h0)
- JIT-compiled MLP: two_layer_mlp(params, x)

Example dispatcher outline:
1. Load tasks from config
2. For each task: load input(s), choose a computation pattern based on description keywords, run compute function, save result, verify

Adjust the mapping from description to compute functions to your specific tasks.
