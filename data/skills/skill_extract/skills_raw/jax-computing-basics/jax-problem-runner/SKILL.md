---
name: jax-problem-runner
description: "Read problem.json, load .npy/.npz inputs, perform JAX computations (reductions, elementwise maps, gradients, scans, and JIT models), verify shapes, and save outputs."
---

# JAX Problem Runner

A reusable workflow for executing small JAX computations described by a JSON task list. Covers typical patterns: reductions, elementwise maps, logistic gradients, recurrent scans, and simple JIT-compiled MLPs. Includes robust data loading from .npy/.npz, shape validation, numerically stable formulas, and reliable saving.

## When to Use

Use this skill when you are given a list of tasks in a JSON file (e.g., problem.json) that specify:
- the input file to read (.npy or .npz)
- the operation to perform (by an ID/description)
- the output file to write

This skill applies to small JAX exercises or pipelines where data inspection, shape checks, and correct JAX idioms (grad, lax.scan, jit) are required.

## Core Workflow

1. Inspect tasks
   - Read problem.json and iterate tasks. For each task, capture id, input, output.
   - Resolve relative vs absolute paths.

2. Load inputs safely
   - If input ends with .npy: load a single array.
   - If input ends with .npz: load the archive and explicitly select keys.
   - Discover keys programmatically: list available keys and choose from a set of expected aliases (e.g., x/X, init/h0, seq/x, Wx/Wxh, Wh/Whh, b/bh).

3. Convert to JAX arrays
   - Convert numpy arrays to device arrays with jnp.asarray before JAX math.
   - Keep parameters (weights/bias) and inputs as JAX arrays for computation; convert results back to numpy just before saving.

4. Task patterns (common examples)
   - Reduce (row mean): result = jnp.mean(x, axis=1) if x is 2D; otherwise reduce along the last axis.
   - Elementwise map: result = jnp.square(x) or any pure elementwise op; avoid unnecessary vmap for dense arrays.
   - Logistic gradient (y in {0,1} or {-1,1}):
     - If y in {0,1}, convert via y_pm = 2*y - 1; if y already in {-1,1}, use as-is.
     - Use numerically stable loss: mean(logaddexp(0, -y_pm * (x @ w))). Compute grad with jax.grad.
   - Recurrent scan (simple RNN):
     - Expected dims: seq[T, D], Wx[D, H], Wh[H, H], b[H], init[H]. Use h_next = tanh(x_t @ Wx + h_prev @ Wh + b).
     - Implement with lax.scan(step, init, seq) where step returns (carry, out) = (h_next, h_next).
   - JIT MLP (2-layer):
     - y = (act(x @ W1 + b1)) @ W2 + b2, where act is typically relu for hidden units.
     - Compile the forward with jax.jit for performance.

5. Save outputs reliably
   - Convert JAX arrays to numpy with np.asarray and save via np.save to the specified path. Ensure parent directories exist.

## Verification

Perform these checks for each task before saving:
- Shape checks
  - Reductions: confirm the output dimension matches the non-reduced dimension.
  - Elementwise maps: output shape equals input shape.
  - Logistic gradient: gradient shape matches weight vector shape.
  - RNN scan: hidden sequence shape equals (T, H) given T from seq length and H from Wh shape.
  - MLP: output batch dimension equals input batch dimension; last dimension equals W2's second dimension.
- Numerical checks
  - Ensure no NaNs or Infs in outputs (use jnp.isfinite on results).
- Consistency checks
  - For logistic: verify label domain; convert {0,1} to {-1,1} if needed.
  - For RNN: confirm bias is added, and matrix multiply orientation is consistent with dims (x_t @ Wx, h @ Wh).
- File checks
  - Verify output file exists after saving and can be reloaded.

If reference outputs are available, compare with np.allclose using a small tolerance.

## Common Pitfalls

- Wrong .npz keys
  - Do not assume key capitalization. Inspect data.files and pick from alias lists (e.g., 'x' or 'X', 'init' or 'h0').
- Logistic loss variant mismatch
  - Using {0,1} labels directly in a {-1,1} formula, or vice versa. Detect domain and convert if necessary.
  - Use jnp.logaddexp for stability instead of naive log(1 + exp()).
- Matrix multiply orientation
  - Confusing x @ W vs W @ x. Align shapes: if x_t has shape (D,), Wx should be (D, H); prefer x_t @ Wx.
- Missing bias or wrong init in RNN
  - Omitting bias in the step or ignoring provided init. Use provided init when available; only default to zeros if explicitly required.
- Misusing vmap
  - For simple elementwise operations, vmap is unnecessary and slower; use jnp.square and broadcasting.
- Saving device arrays directly
  - Always convert to numpy before np.save.

## Optional Script Usage

This skill provides a generic runner script that supports common task IDs and safe key resolution.

Example:
- Place your problem.json in the working directory.
- Run: `python3 scripts/jax_problem_runner.py --problem problem.json`

The script will:
- Read tasks from problem.json
- Load inputs (npy/npz)
- Dispatch to a matching handler by task id (basic_reduce, map_square, grad_logistic, scan_rnn, jit_mlp)
- Perform shape validations and numerical checks
- Save outputs to the specified paths

You can extend the handler map for new task IDs following the same validation and saving conventions.
