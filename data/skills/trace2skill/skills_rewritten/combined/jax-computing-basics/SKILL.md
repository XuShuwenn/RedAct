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

- Make this a hard preflight gate before any work: do not read files, write code, or run commands until you can restate the exact required wrapper/schema, the only allowed tool name(s), whether only one action is allowed per turn, whether commands must be concrete bash, and the exact final completion token.
- If the prompt exposes only one executable interface, assume every other wrapper/tool name is invalid unless the environment explicitly showed it as available. Do not improvise with XML-style tags, native tool wrappers, pseudo-tools, editor helpers, or ad hoc calls such as `Read(...)`, `Write(...)`, `TodoWrite`, or custom `Bash(...)` wrappers when those interfaces were not explicitly provided.

- Wait for each tool/action result before issuing the next action when the protocol requires turn-by-turn execution.
- Before the final response, re-check whether an exact completion token is required; if so, output exactly that token and nothing else.
- Do not substitute approximate formatting, alternate tool-call styles, equivalent-looking custom tags, native convenience wrappers, free-form summaries, or extra prose when an exact protocol is required.
- Treat protocol mismatch as a hard failure even if computations and output files are otherwise correct.
- Treat the required tool/action interface as an exact parser contract: match wrapper text, capitalization, allowed tool name(s), field names, JSON shape, bash invocation pattern, and one-action-per-turn requirements verbatim on every step.
- If the environment requires `Thought:`/`Action:` blocks or `Action:` followed by JSON, use only that exact schema; do not switch to XML-style tags, markdown code fences, pseudo-functions, native tool wrappers, or prose-described operations.
- If only shell/bash execution is allowed, send concrete executable commands with real arguments only. Do not send placeholders like `inspect files`, `run the script`, or `write and run a solver`.

- Translate intent into a literal executable command before acting. Bad: `inspect the input files`, `check outputs`, `run the solver`. Good: `find . -maxdepth 3 -type f`, `python3 solve.py`, `python3 - <<'PY'\nimport numpy as np; print(np.load('basic_reduce.npy'))\nPY`.
- In bash-only or strict `Thought:`/`Action:` JSON environments, every action payload must be executable as written or be a file write containing literal source text; never send English descriptions such as `write and run a script` in place of an actual command or file contents.

- When using a file-writing tool, provide the literal file contents exactly as they should be written. If creating a Python script, the written content must be executable source code, not a summary or pseudocode.
- Before each tool/action message, verify the wrapper, field names, payload shape, and command/content are exactly compliant.
- If an exact completion token is required (for example, `ACTION: TASK_COMPLETE`), output exactly that token and nothing else in the final response.

- Protocol self-check for every tool call: confirm the message uses the exact required wrapper text, allowed tool name, and required argument field names/object shape. Do not use XML-style tags, markdown-fenced calls, mixed tool syntaxes, pseudo-commands, or prose descriptions when a strict action schema is required.
- Treat completion as a separate final gate: after verification is finished, compare the planned final response against the required terminator character-for-character and emit that exact token alone, with no summary, heading, prefix, suffix, or extra formatting.


## Workflow

1. Read `problem.json` completely before coding; if the file view is truncated, partial, elided, paginated, or cut off mid-entry, stop and fetch the remainder before planning or implementing anything. Do not implement any task until every entry's `id`, `description`, `input`, and `output` fields are fully visible and the total task count is confirmed from the file itself.
   - Before this first read, also confirm the required action/tool protocol so the very first inspection step already uses the exact mandated wrapper and allowed tool syntax.
   - Do not proceed from a manifest read that cuts off mid-entry or mid-field (for example, stopping at an `"output"` key). Re-run inspection until the full JSON is visible, then confirm later tasks from the manifest itself before implementing any of them.

   - Do not create or edit solution code before this full-manifest read is complete.
   - Treat any truncated read of `problem.json`, input inspection, helper code, or execution logs as blocking: get the missing content before coding, running, validating, or claiming completion.
   - Do not infer unseen tasks, formulas, or output paths from filenames, neighboring files, task IDs, or common benchmark patterns when the manifest read was incomplete.
   - For any task using `.npz` or other structured inputs, inspect the archive keys before writing code that references field names; never assume keys like `X`, `y`, `W`, or `h0` without observing them.
2. Parse `problem.json` into a runtime manifest and treat it as the authoritative source for task count, computation requirements, input paths, and output paths.

   - Early in the run, inspect any relevant workspace helper module (for example, `jax_skills.py`) before reimplementing loaders, savers, manifest parsing, or task helpers; reuse helpers only after confirming the module exists and reading its real interface/behavior.
   - Treat inspected helper code as secondary authority after the manifest and task descriptions: use it to constrain implementation details, not to invent missing requirements.
   - Before writing the main solver, prefer a short inspection pass over all manifest inputs to record actual file types, archive keys, shapes, dtypes, and any initialization/metadata fields that will affect axis choices, formulas, or tensor orientation.
   - Write down or print a concrete per-task checklist from the parsed manifest before coding so every required computation, input, and output is accounted for end-to-end.

3. Iterate over every manifest entry programmatically; do not hardcode task IDs, filenames, paths, output names, or the number of tasks.
   - Build the task list directly from the parsed manifest itself; do not reconstruct missing entries from nearby files, prior examples, guessed conventions, or partial JSON content.
   - In code, read each task object's `input` and `output` fields from the parsed manifest; do not reconstruct filenames from `id` values or naming patterns.
   - Prefer one deterministic, rerunnable solver script (for example, `solve.py`) that processes all manifest entries in one run, writes every required output, and then performs a verification pass over all expected outputs; this is the default workflow for multi-task benchmark-style jobs unless instructions require another execution style.
   - A strong default is: (1) inspect helpers if present, (2) inspect each input schema, (3) write one solution script covering all manifest entries, (4) run it once, (5) verify every saved output against the manifest and task semantics.
   - If you create such a script, write and inspect the actual source text before execution; verify the file contains concrete executable code rather than a placeholder description.
   - Before implementing custom loaders or utilities, check whether the workspace provides helper modules (for example, `jax_skills.py` or similar support code) and reuse them when they already cover manifest parsing, loading, saving, or standard array operations.
  - Do not import or depend on helper modules, wrapper APIs, or convenience functions unless you have first verified in the workspace that they exist and inspected their actual paths, exported functions, signatures, and behavior. Reuse verified helpers when they clearly cover the task, but never invent calls such as custom `load`, `save`, `map_op`, gradient, scan, or model helpers from assumed support libraries.
  - When helper code is absent, unclear, or only partially observed, implement the task directly with standard Python/JAX/NumPy primitives rather than guessing a custom abstraction layer.
   - Before running any generated script, confirm the available interpreter/runner in the environment rather than assuming a command exists.
   - Use only literal, executable tool commands and exact file edits. Do not issue placeholder actions such as `list available input data files`, `python solution script`, or `check outputs`; instead run the exact shell command or write the exact code/text change.

   - If a command string contains explanatory prose rather than something the shell could execute verbatim, rewrite it into a concrete command before sending it.
   - Bad tool/action examples: `list available input data files`, `python solution script`, `check outputs`, `replace previous implementation`.
   - Good tool/action examples: `find . -maxdepth 3 -type f`, `python3 solve.py`, or an edit anchored to exact observed source lines.

   - When creating or editing code files, write runnable source code, not pseudocode, TODO markers, descriptive placeholders, or summarized intent.

   - Never write a file with content like `created a script ...`, `wrote JAX script to ...`, `implementation goes here`, or any prose summary of what the code would do. For any file-writing action, the payload must be the full literal executable source itself.

   - After each write/edit to a code file, immediately read the file back or otherwise inspect the saved contents to confirm the artifact on disk is the intended executable code before running it.

   - Treat this inspection as a hard gate: do not claim implementation, execute the file, or validate outputs until you have confirmed the saved artifact contains concrete code with real imports, definitions, and executable statements rather than placeholder narration.
   - Keep an observable implementation trail: if execution output appears inconsistent with the observed file contents, reopen the file and resolve the mismatch before proceeding.

   - If a command fails, produces empty/ambiguous output, or depends on an interpreter/runner that may not exist, stop and resolve that uncertainty first by inspecting stdout/stderr and rerunning with an unambiguous confirmed command.

   - When running the main script, require explicit end-to-end completion evidence: a clean exit status and logs or checks showing the run reached the final task/output. If stdout stops mid-task, is truncated, or lacks a final completion indication, treat the run as incomplete and rerun or verify the missing tasks individually before proceeding.

4. For each task from the parsed manifest:
   - Load input data from the exact `input` path specified for that task.
   - If instructions provide absolute paths or require absolute-path usage, preserve and use those exact absolute paths for reads, writes, and script invocation.
   - Re-read the task's exact `description` immediately before implementing that task and implement only what it explicitly requests.
   - Map the requested computation to the most direct JAX primitive that exactly matches it (for example: `jnp` reductions for sums/means, `vmap` for mapped independent work, `grad` for differentiation, `lax.scan` for recurrences, `jit` when compiled execution is requested or useful).
   - Inspect input schema before coding against it:

   - Do this inspection early, before finalizing formulas, tensor orientation, axes, broadcasting assumptions, or model wiring; for plain `.npy` inputs too, inspect shape/dtype and representative values when semantics could affect the implementation.
   - When available in the workspace, also inspect any reference/expected outputs or other authoritative artifacts to confirm target output shape/structure before coding; use them only to narrow plausible interpretations, not to replace the task description.

     - `.npy`: check shape, dtype, and representative values when needed to disambiguate semantics
     - `.npz`: list actual keys first, then load by confirmed key names; inspect shapes/dtypes of relevant arrays and any special fields such as `init` or other metadata/initialization parameters
   - For `.npz` or multi-tensor tasks, inspect and note keys, shapes, and dtypes before writing task logic; do not use guessed names unless they were observed.

   - Treat that inspection as the source of truth for field names and tensor layout; write code against the observed schema, not likely conventions.

   - Treat observed archive keys as authoritative. Do not code against guessed field names like `X`, `x_seq`, `h0`, or similar conventions before confirming they actually exist in the file.

   - If the observed keys differ from common conventions (for example `x` instead of `X`, `seq` instead of `x_seq`), follow the file contents exactly; do not silently substitute conventional variants such as `X`/`Y`/`W`.

   - For linear algebra, batching, reductions, sequence/model-style computations, broadcasting-sensitive logic, labels/targets, losses, or gradients, inspect operand shapes and target encoding first and choose axes, scan order, transpose/orientation behavior, and formulas from the observed data and the exact description, not from naming conventions.

   - Before implementing gradients, losses, or classification logic, inspect representative target/label values and encoding conventions (for example `{0,1}`, `{-1,1}`, class indices, or one-hot targets) and choose the matching formula/objective from the description and observed data.

   - Do not infer the required computation from task IDs, filenames, shapes, neighboring tasks, inspected keys, or common JAX/ML conventions.
   - Do not fill in unspecified mathematical or model details from habit or likely patterns. Loss definitions, label conventions, activation functions, recurrence equations, reduction choices/axes, returned state, and layer structure must come from the task's exact `description`, not from names like `grad_logistic`, `scan_rnn`, or `jit_mlp`.
   - If multiple interpretations remain plausible, test the smallest reasonable set of candidates against observed data, expected output structure, or other authoritative artifacts before choosing one; otherwise stop and recover/confirm the specification rather than guessing.

   - Keep candidate testing tight and evidence-based: vary only the ambiguous detail (for example sum vs. mean, axis choice, transpose/orientation, activation, recurrence update, or label convention), compare against simple recomputations or authoritative reference artifacts when available, and keep the variant that matches that evidence.
   - For multi-task manifests or unfamiliar operations, validate tricky computations in isolation first with a small direct script/snippet, then fold only the confirmed logic into the final all-tasks pipeline.

   - Before any matrix multiplication, batched linear algebra, scan, or neural-network layer, verify operand shapes explicitly and confirm whether weights are stored as `(in, out)` or `(out, in)` before adding any transpose.

   - For batched linear or MLP-style code, prefer batch-first equations that preserve the leading sample dimension (for example `x @ W + b` when shapes confirm `x` is `(batch, in)` and `W` is `(in, out)`); do not multiply weight-first unless inspected shapes require it.

   - If execution reveals missing keys, unexpected target encodings, shape mismatches, or other schema surprises, stop and re-inspect the input file; do not patch by guessing alternate key names or conventions.
   - When fixing an existing script after inspection or a runtime error, first open the current file and identify the exact lines to change.

   - Patch sequence: read the current file contents -> copy the exact existing snippet or line range to change -> apply the edit against that observed text -> read the file back and verify the saved code contains the intended change. Do not describe the target abstractly as `previous implementation` or similar placeholder text.

   - Anchor edits to concrete, observed source text from the file; do not issue placeholder replacements like `replace previous implementation` or patch from memory.
   - If the visible description is incomplete, ambiguous, or does not explicitly specify a needed formula/reduction/layout detail, stop and recover the authoritative task text before implementing.
   - Save the result to the exact `output` path specified for that task.
5. Before declaring success, perform a coverage check against the full manifest: confirm every entry in `problem.json` was processed, no entry was skipped because of truncated file views, and each required output was written to the exact specified filename/path.

   - Treat completion as blocked until every manifest entry has a matching verification record. Compare the manifest's expected output list against the verified output list one by one and resolve any missing item before proceeding.

   - Use an explicit per-task checklist keyed by manifest entries or output paths; do not rely on memory or a partial log scan.
   - Record verification for each expected output individually, and before the final response ensure the number of verified outputs matches the number of manifest entries exactly.

   - Do not treat a bulk directory listing, file-count match, or partial preview as completion evidence; each manifest entry needs its own output reload and requirement-level check.
   - Do not mark the run complete if execution logs stop mid-task, omit later manifest entries, or lack a clear final success/exit indication; rerun, inspect, or otherwise obtain end-to-end completion evidence first.

   - If output is truncated, do not infer that unseen later tasks succeeded from earlier progress messages or existing files. Obtain direct evidence for the missing tail of execution or rerun focused checks for the unconfirmed manifest entries.

6. Then validate semantics, not just execution: for each task, confirm the saved result matches the exact description's requested operation/formula, relevant axes, output shape/dtype, and target filename/path.
   - Minimum validation standard per task: (a) re-read the task description, (b) identify the exact formula/operation implied, (c) run a small recomputation, invariant check, or alternate direct calculation against the saved output, and (d) only accept the task if this value-level check agrees.
   - DO NOT stop at `file exists`, successful script exit, or plausible shape/dtype alone; those are necessary but not sufficient.
   - Do not treat `script ran`, truncated logs, file existence, a successful script exit, or a bulk `ls` check as sufficient evidence.
   - File presence alone is never sufficient proof of success: outputs may be stale from earlier runs or created before computation finished. Combine artifact checks with observed full execution completion and output reload/inspection before declaring success.

   - Distinguish fresh outputs from stale artifacts: overwrite prior outputs in the current run when feasible or verify freshness via the current execution path plus value-level validation; never use `ls` alone as proof that the corresponding task finished this time.

   - Also verify any generated scripts/artifacts themselves when they were created during the run: inspect the file contents to confirm they are executable code/configuration, not placeholders or summaries.
   - Reload each expected output path from the manifest and confirm the file exists, is readable, and has the expected shape/dtype or representative values implied by the task.

   - For multi-output runs, perform this reload-and-inspect check for every output file individually in manifest order and use the observed metadata as part of the per-task completion checklist.
   - If any verification output is truncated, partial, or ambiguous, rerun a more targeted inspection before declaring success.

   - Re-read each task description during validation and inspect representative output values, small recomputations, or candidate-formula checks when feasible to confirm the implemented formula matches the specification.
   - For floating-point validation, prefer tolerance-aware comparisons such as `np.allclose` unless the specification explicitly requires exact equality.

  - Prefer a simple independent check for validation: recompute with direct `numpy`/manual math on the same input, or check a task-specific invariant, and compare to the saved output after reloading it.
  - When one task fails validation but others pass, keep the verified outputs unchanged and debug only the failing task(s) instead of rewriting the whole solver.
  - Before final completion, perform a pre-response gate: confirm the full `problem.json` contents were obtained without truncation, every manifest entry has a corresponding verified output, and each task had at least one value-level semantic check beyond existence/shape/dtype or script exit status.

7. Before the final response, re-check any required interaction protocol from the task/system instructions and emit the exact mandated completion string or action format verbatim.

   - Separate result verification from formal completion: even if all outputs are correct, do not finish until the required response channel, action schema, and exact completion token have been satisfied.
   - If the environment specifies an exact completion token such as `ACTION: TASK_COMPLETE`, do a final literal-string check and output exactly that token with no surrounding prose, markdown, summaries, or recap.
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

- Proven workflow: read `problem.json` fully -> inspect any provided helper module such as `jax_skills.py` -> run a quick input-inspection pass for keys/shapes/dtypes -> write one consolidated solver -> check full execution logs -> run a lightweight verification pass over every manifest output.
- A strong default is: inspect keys/shapes/dtypes first, then inspect a few representative values that determine semantics such as label encoding, initialization fields, or tensor orientation.
- If several formulas or layouts are all shape-compatible, do not pick one by convention alone; run a tiny candidate check against observed data or authoritative reference artifacts to lock the exact convention before finalizing the implementation.
- During debugging, validate outputs one by one and use the passing tasks as evidence that the shared manifest/I/O flow is already correct.
