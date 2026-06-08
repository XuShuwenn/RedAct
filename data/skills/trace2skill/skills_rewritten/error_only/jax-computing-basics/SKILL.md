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
- Treat protocol mismatch as a hard failure even if computations and output files are otherwise correct.
- Treat the required tool/action interface as an exact parser contract: match wrapper text, capitalization, allowed tool name(s), field names, JSON shape, bash invocation pattern, and one-action-per-turn requirements verbatim on every step.
- If the environment requires `Thought:`/`Action:` blocks or `Action:` followed by JSON, use only that exact schema; do not switch to XML-style tags, markdown code fences, pseudo-functions, native tool wrappers, or prose-described operations.
- If only shell/bash execution is allowed, send concrete executable commands with real arguments only. Do not send placeholders like `inspect files`, `run the script`, or `write and run a solver`.
- When using a file-writing tool, provide the literal file contents exactly as they should be written. If creating a Python script, the written content must be executable source code, not a summary or pseudocode.
- Before each tool/action message, verify the wrapper, field names, payload shape, and command/content are exactly compliant.
- If an exact completion token is required (for example, `ACTION: TASK_COMPLETE`), output exactly that token and nothing else in the final response.

## Workflow

1. Read `problem.json` completely before coding; if the file view is truncated, partial, elided, paginated, or cut off mid-entry, stop and fetch the remainder before planning or implementing anything. Do not implement any task until every entry's `id`, `description`, `input`, and `output` fields are fully visible and the total task count is confirmed from the file itself.
   - Do not create or edit solution code before this full-manifest read is complete.
   - Treat any truncated read of `problem.json`, input inspection, helper code, or execution logs as blocking: get the missing content before coding, running, validating, or claiming completion.
   - Do not infer unseen tasks, formulas, or output paths from filenames, neighboring files, task IDs, or common benchmark patterns when the manifest read was incomplete.
   - For any task using `.npz` or other structured inputs, inspect the archive keys before writing code that references field names; never assume keys like `X`, `y`, `W`, or `h0` without observing them.
2. Parse `problem.json` into a runtime manifest and treat it as the authoritative source for task count, computation requirements, input paths, and output paths.
3. Iterate over every manifest entry programmatically; do not hardcode task IDs, filenames, paths, output names, or the number of tasks.
   - Build the task list directly from the parsed manifest itself; do not reconstruct missing entries from nearby files, prior examples, guessed conventions, or partial JSON content.
   - In code, read each task object's `input` and `output` fields from the parsed manifest; do not reconstruct filenames from `id` values or naming patterns.
   - Prefer one deterministic, rerunnable script that processes all manifest entries in one run, writes every required output, and then performs a verification pass over all expected outputs.
   - If you create such a script, write and inspect the actual source text before execution; verify the file contains concrete executable code rather than a placeholder description.
   - Before implementing custom loaders or utilities, check whether the workspace provides helper modules (for example, `jax_skills.py` or similar support code) and reuse them when they already cover manifest parsing, loading, saving, or standard array operations.
  - Do not import or depend on helper modules, wrapper APIs, or convenience functions unless you have first verified in the workspace that they exist and inspected their actual interfaces and behavior. Never invent calls such as custom `load`, `save`, `map_op`, gradient, scan, or model helpers from assumed support libraries.
  - When helper code is absent, unclear, or only partially observed, implement the task directly with standard Python/JAX/NumPy primitives rather than guessing a custom abstraction layer.
   - Before running any generated script, confirm the available interpreter/runner in the environment rather than assuming a command exists.
   - Use only literal, executable tool commands and exact file edits. Do not issue placeholder actions such as `list available input data files`, `python solution script`, or `check outputs`; instead run the exact shell command or write the exact code/text change.
   - When creating or editing code files, write runnable source code, not pseudocode, TODO markers, descriptive placeholders, or summarized intent.
   - After each write/edit to a code file, immediately read the file back or otherwise inspect the saved contents to confirm the artifact on disk is the intended executable code before running it.
   - If a command fails, produces empty/ambiguous output, or depends on an interpreter/runner that may not exist, stop and resolve that uncertainty first by inspecting stdout/stderr and rerunning with an unambiguous confirmed command.
4. For each task from the parsed manifest:
   - Load input data from the exact `input` path specified for that task.
   - If instructions provide absolute paths or require absolute-path usage, preserve and use those exact absolute paths for reads, writes, and script invocation.
   - Re-read the task's exact `description` immediately before implementing that task and implement only what it explicitly requests.
   - Map the requested computation to the most direct JAX primitive that exactly matches it (for example: `jnp` reductions for sums/means, `vmap` for mapped independent work, `grad` for differentiation, `lax.scan` for recurrences, `jit` when compiled execution is requested or useful).
   - Inspect input schema before coding against it:
     - `.npy`: check shape, dtype, and representative values when needed to disambiguate semantics
     - `.npz`: list actual keys first, then load by confirmed key names; inspect shapes/dtypes of relevant arrays and any special fields such as `init` or other metadata/initialization parameters
   - For `.npz` or multi-tensor tasks, inspect and note keys, shapes, and dtypes before writing task logic; do not use guessed names unless they were observed.
   - Treat observed archive keys as authoritative. Do not code against guessed field names like `X`, `x_seq`, `h0`, or similar conventions before confirming they actually exist in the file.
   - For linear algebra, batching, reductions, sequence/model-style computations, broadcasting-sensitive logic, labels/targets, losses, or gradients, inspect operand shapes and target encoding first and choose axes, scan order, transpose/orientation behavior, and formulas from the observed data and the exact description, not from naming conventions.
   - Do not infer the required computation from task IDs, filenames, shapes, neighboring tasks, inspected keys, or common JAX/ML conventions.
   - Do not fill in unspecified mathematical or model details from habit or likely patterns. Loss definitions, label conventions, activation functions, recurrence equations, reduction choices/axes, returned state, and layer structure must come from the task's exact `description`, not from names like `grad_logistic`, `scan_rnn`, or `jit_mlp`.
   - If multiple interpretations remain plausible, test the smallest reasonable set of candidates against observed data, expected output structure, or other authoritative artifacts before choosing one; otherwise stop and recover/confirm the specification rather than guessing.
   - Before any matrix multiplication, batched linear algebra, scan, or neural-network layer, verify operand shapes explicitly and confirm whether weights are stored as `(in, out)` or `(out, in)` before adding any transpose.
   - If execution reveals missing keys, unexpected target encodings, shape mismatches, or other schema surprises, stop and re-inspect the input file; do not patch by guessing alternate key names or conventions.
   - When fixing an existing script after inspection or a runtime error, first open the current file and identify the exact lines to change.
   - Anchor edits to concrete, observed source text from the file; do not issue placeholder replacements like `replace previous implementation` or patch from memory.
   - If the visible description is incomplete, ambiguous, or does not explicitly specify a needed formula/reduction/layout detail, stop and recover the authoritative task text before implementing.
   - Save the result to the exact `output` path specified for that task.
5. Before declaring success, perform a coverage check against the full manifest: confirm every entry in `problem.json` was processed, no entry was skipped because of truncated file views, and each required output was written to the exact specified filename/path.
   - Use an explicit per-task checklist keyed by manifest entries or output paths; do not rely on memory or a partial log scan.
   - Record verification for each expected output individually, and before the final response ensure the number of verified outputs matches the number of manifest entries exactly.
   - Do not mark the run complete if execution logs stop mid-task, omit later manifest entries, or lack a clear final success/exit indication; rerun, inspect, or otherwise obtain end-to-end completion evidence first.
6. Then validate semantics, not just execution: for each task, confirm the saved result matches the exact description's requested operation/formula, relevant axes, output shape/dtype, and target filename/path.
   - Minimum validation standard per task: (a) re-read the task description, (b) identify the exact formula/operation implied, (c) run a small recomputation, invariant check, or alternate direct calculation against the saved output, and (d) only accept the task if this value-level check agrees.
   - DO NOT stop at `file exists`, successful script exit, or plausible shape/dtype alone; those are necessary but not sufficient.
   - Do not treat `script ran`, truncated logs, file existence, a successful script exit, or a bulk `ls` check as sufficient evidence.
   - File presence alone is never sufficient proof of success: outputs may be stale from earlier runs or created before computation finished. Combine artifact checks with observed full execution completion and output reload/inspection before declaring success.
   - Also verify any generated scripts/artifacts themselves when they were created during the run: inspect the file contents to confirm they are executable code/configuration, not placeholders or summaries.
   - Reload each expected output path from the manifest and confirm the file exists, is readable, and has the expected shape/dtype or representative values implied by the task.
   - Re-read each task description during validation and inspect representative output values, small recomputations, or candidate-formula checks when feasible to confirm the implemented formula matches the specification.
   - For floating-point validation, prefer tolerance-aware comparisons such as `np.allclose` unless the specification explicitly requires exact equality.
7. Before the final response, re-check any required interaction protocol from the task/system instructions and emit the exact mandated completion string or action format verbatim.
   - Final-response checklist: verify outputs, stop using tools, re-read the required termination instruction, and output the exact required completion token or close through the required action channel only.
   - Do not append a narrative wrap-up such as `done`, `completed all tasks`, tables, or file summaries after the required completion token.
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
