---
name: pddl-tpp-planning
description: "Solve travelling purchase problem (TPP) tasks using PDDL planning, generating valid plans from domain and problem files."
---

# PDDL Planning for TPP Tasks

## When to Use

- Solve Travelling Purchase Problem using PDDL
- Generate valid plans from domain and problem files
- Execute planning tasks from problem.json specification

## Execution Protocol

- Follow the task/runtime's required tool-call or action schema exactly; do not invent alternate tool syntax, wrappers, or helper APIs.
- Do not assume extra tools, planner wrappers, or libraries are available unless explicitly provided.
- If the environment requires one action per turn or a bash-only workflow, obey that constraint throughout.
- Treat completion signaling as part of correctness: if an exact final string or completion token is required, emit it verbatim.

- Before the first tool/action, extract the exact runtime interaction contract from the task instructions: required tool/action syntax, whether only one tool family is allowed, whether exactly one action is allowed per turn, whether you must wait for an observation after each action, and any exact final completion string/token.
- If a specific `Action:` block, JSON/tool schema, message structure, or bash-only workflow is required, use that format verbatim for every step; do not switch to alternate wrappers, XML/markdown tags, helper APIs, unsupported libraries, or habitual native tool-call styles mid-task.
- If the protocol requires one action per turn or waiting for an observation, issue exactly one compliant action and wait before proceeding.
- If you need planner/validator libraries beyond a shell command, first inspect the actual installed interface with a minimal probe and use only behaviors you directly observed.
- Do not describe a tool, planner, validator, or skill as invoked unless the invocation appears in the actual transcript and you have its result.
- Before the final response, re-check the completion requirement and emit the exact required token/string verbatim; if the runtime requires the final turn to contain only that string, output nothing else.


## Input Format

problem.json entries:
```json
{
  "id": "problem_id",
  "domain": ".../xxx.pddl",
  "problem": ".../yyy.pddl",
  "plan_output": "xxx/problem_id.txt"
}
```

**Manifest discipline**
- Treat `problem.json` as the authoritative list of tasks to execute.
- Process only the entries present in `problem.json`; do not infer extra tasks from other files.
- Read input specification files (`problem.json`, domain, problem files) but do not modify them unless explicitly instructed.


## Workflow

1. Read the task instructions for execution constraints before acting; confirm available tools, the exact required tool-call/action schema, whether one-action-per-turn or observation waits are required, and any exact completion signal
1a. Explicitly note the required tool/action schema and exact final completion text before making any tool call.
1b. If using an external planner/validator/library interface, run a minimal inspection first to confirm import path, callable names, return shape, and how success is reported before writing larger scripts.
2. Load the full PDDL domain file and inspect complete action schemas
3. Load the full PDDL problem file and inspect complete initial facts and goals
4. If any file/tool output is truncated, cut off, or ends mid-line/mid-token, fetch the missing content before reasoning further
4a. Treat truncated or incomplete domain/problem output as a hard stop for planning: do not guess missing `:action`, `:init`, `:goal`, objects, predicates, parameter meanings, or goals from examples, memory, prior TPP patterns, or planner-output snippets.
4b. A domain is not ready for planning until the full schemas of every action you may use are visible, and a problem is not ready until the complete relevant initial facts and full `:goal` section have been explicitly inspected.
4c. Do not generate, write, validate, or describe a plan until the complete action schemas you rely on and the complete relevant problem `:init` and `:goal` sections have been directly observed.
5. Verify action names, parameter order, preconditions/effects, predicate meanings, and any level-transition arguments from the actual domain before instantiating actions
5a. Never assume standard TPP actions such as `drive`, `buy`, `load`, or `unload` exist or use familiar parameter orders until you have directly observed their schemas in the current domain file.
5b. For every action you plan to use, extract its full schema from the domain and map each concrete argument position back to that schema exactly; do not reuse level/count arguments from examples or prior tasks.
5c. Cross-check your intended plan against literals actually observed in the full problem file; if any planned step conflicts with the visible initial state, depends on unseen facts, or a claimed goal/fact was not directly seen, stop and inspect further before proceeding.
6. Generate plan using planner, or manually derive one only after complete inspection of the full domain and problem
6a. If using a planner/skill, confirm the call actually ran and inspect its returned result or generated files before proceeding.
6b. If planner output is only banners/setup text, warnings, missing, or truncated, do not treat that as a found or validated plan; capture more reliable output or debug the invocation/result.
6c. If expected plan files are missing, do not assume silent success.
6d. Switch to manual derivation only if planner use is unavailable or failing, and then keep the same semantic-validation standard.
7. Check each planned action is applicable from the current accumulated state and update the state step by step
7a. Keep a small state trace while planning: after each action, update truck location, where each good is, possession, and any before/after symbolic level values touched by buy/load/unload so later steps use the post-state from earlier actions.
7b. Compare the planned steps against the observed initial state before writing: if a fact such as a good already being loaded, available, or otherwise satisfied is already true, do not add redundant setup actions unless the full domain and goal show they are still required.
7c. Check the final accumulated state against the explicit problem goal literals before writing or claiming success.
7d. If a generated plan file already exists, inspect it completely first and overwrite it only after confirming a specific defect, incompleteness, or mismatch with the validated plan.
8. Write plan to output path
8a. After writing, obtain direct confirmation by reading back the saved file or otherwise observing the write result; do not declare success based only on an attempted write command.
9. Read back and verify each written plan file completely before concluding success; if any read/output is truncated, ambiguous, or cut off, re-read with targeted per-file reads, line counts, or final-line inspection until completeness is explicit.
9a. If any saved plan file is truncated, malformed, empty, or ends mid-line/mid-token, treat the task as unresolved: regenerate or repair the plan, then reread the corrected file before continuing.
9b. If planner/validator output, your notes, and the saved file contents disagree on action count, final actions, or completion, treat the task as unresolved and debug/regenerate from the saved artifact instead of narrating unobserved actions.
10. Confirm outputs were produced only for tasks listed in `problem.json` and that each expected `plan_output` exists, is non-empty, and ends with a complete action line.
10a. For each task in `problem.json`, gather direct evidence for that specific output file; do not infer batch success from partial run logs, startup banners, warnings, or the mere presence of multiple files.
10b. Verify each saved plan contains the actual final goal-achieving step(s) required by the problem; never infer a missing final unload/delivery or other goal step from planner intent.
10c. If any expected file is missing, malformed, truncated, or lacks a required goal step, treat the run as incomplete and regenerate/debug instead of reporting success.
11. Distinguish `planner produced a plan` from `plan was validated`; only use validation language if you actually observed a successful validator/planner check or another explicit validity check.
12. Before the final response, re-check the runtime instructions so the last message matches any required completion token or final-response schema exactly.

## Plan Format

One action per line:
```
drive(truck1, depot1, market1)
buy(truck1, goods1, market1, level0, level1, level0, level1)
load(goods1, truck1, market1, level0, level1, level0, level1)
drive(truck1, market1, depot1)
unload(goods1, truck1, depot1, level0, level1, level0, level1)
```


Malformed example to reject:
```
buy(truck1, goods2, market1, level0, level1, level0, leve
```
Never accept a plan file that ends with a partial action line.


## Requirements

- Plan must be syntactically correct PDDL
- Plan must be valid (solves problem)
- Action/object names must match domain and problem


- Plan must be based on complete, non-truncated domain and problem content
- Do not infer action arguments, parameter order, preconditions/effects, level transitions, initial facts, or goals from examples, memory, or partial reads; if the relevant domain/problem section is incomplete, gather more content before planning
- Track state progression step by step across the plan, especially when actions encode symbolic quantity/level changes
- For multi-good plans, update before/after levels after each buy/load/unload instead of reusing the same arguments blindly
- Respect task scope: solve exactly the tasks listed in `problem.json`
- Do not rewrite `problem.json` or other input files unless explicitly instructed
- Do not call a plan valid unless you checked it against the complete domain/problem contents or observed a successful planner/validator result
- Do not claim success from partial or truncated planner output, banners, warnings, setup text, or incomplete console logs
- Verify success from the saved output artifacts, not just stdout/stderr
- Do not overwrite an existing plan file unless you have inspected it and confirmed a specific error requiring correction

- Treat unseen domain `:action` blocks, truncated problem `:init`, or missing `:goal` content as hard blockers; stop and retrieve the missing content instead of drafting a tentative plan.
- Follow the task environment's exact tool-call/action schema throughout; unsupported interaction formats are task failures even if the plan itself is correct.
- When writing solver or validation scripts, do not assume planner API names, enum members, status constants, return shapes, or callable interfaces; inspect and confirm them first.
- Treat syntax checks, file existence, readable action strings, or successful parsing as insufficient for semantic validity.
- If planner or validator logs are truncated, interrupted, ambiguous, or stop before an explicit success message, do not claim validation/completion from those logs alone.
- Treat direct evidence of malformed saved output files as a blocking failure; do not report completion until the artifact has been corrected and rechecked.
- Do not transcribe, rewrite, or "clean up" an existing/generated plan from a partial read; first obtain the full file or targeted evidence that a specific line is wrong or incomplete.
- Existing plan files prove artifacts exist, not that planner/script/validator execution completed as claimed for all tasks; claims about execution completion require directly observed confirming output.
- If execution logs are incomplete or contradict the saved artifact, reconcile the mismatch from direct file inspection before claiming success.
- Do not claim you "confirmed" action behavior, goal satisfaction, or plan validity unless the confirming file contents or validator/planner output were actually observed.
- End with the exact required completion signal when one is specified; do not replace it with a natural-language summary.



## Verification Checklist

- If stdout/stderr or combined file output is truncated, inspect each expected `plan_output` separately before claiming batch success.
- Confirm you observed complete domain action schemas and complete problem `:init`/`:goal` content for each solved task; otherwise do not claim the plan is valid.
- Confirm your actual tool usage matched the runtime-required invocation schema throughout the task; no mixed formats, and observation waits were respected when required.
- If you used any external library API, verify your implementation against directly observed probe results rather than assumptions.
- For each distinct action schema used in the plan, compare a grounded instance against the domain parameter order before saving the file.
- Reject any plan where the written level/count arguments do not match the state transition you are relying on.
- Check the last line of each saved plan file; it must be a complete action, not a cut-off fragment.
- Before declaring success, reread each saved plan file and confirm it still matches the checked action schemas and accumulated state trace.
- If any saved plan read shows fewer actions than expected, ends earlier than the generated plan, or the tool output is cut off, inspect the file again before claiming success.
- For each task, verify the saved file contains the required final goal-achieving action(s); a plan ending at `drive(...)` is not enough when an `unload(...)` or other delivery step is still required.
- Reconcile contradictions before finishing: if logs, notes, or saved files disagree on plan length, ending, or validation status, investigate and verify again instead of trusting partial evidence.
- Distinguish artifact checks from execution checks: saved plan files confirm outputs, while planner/validator/script completion claims require directly observed command output or an explicit manual applicability/goal check.
- Base final claims on observed artifacts only: say the planner produced/wrote a plan unless you also observed a separate successful validation check.
- If no validator/planner confirmation is available, only report success after a manual step-by-step applicability check against the complete domain and problem.
- For multi-good or repeated resource actions, review the state trace and ensure each later level/count argument reflects the updated post-state.
- Confirm your own tool/action messages followed the required schema throughout, and if an exact completion token is required, make the final response exactly that token.

## Verification Checklist

- Inspect every `plan_output` file fully or use unambiguous completeness checks such as targeted reads, line counts, or confirming the final line/action is complete.
- If any file is truncated, ends mid-line, or contains an incomplete action, treat the task as failed and regenerate/debug it.
- Cross-check the actual saved file contents against what you will report.
- For TPP tasks, ensure the written plan includes the required goal-achieving steps, especially needed deliveries/unloads.
- For batch runs, verify each expected output file exists and is non-empty before finishing.
- Final reporting must match directly observed evidence only.

## Tips

- Use FastDownward or similar planner
- Validate plan syntax before writing
- Handle multiple tasks from problem.json


- Treat example plan lines in this skill as format examples only, not proof of action semantics for a new domain file
- If a file view ends mid-token, mid-line, or before `:goal`, treat it as incomplete and read more
- Before writing a plan, extract each action schema actually used and verify argument order against the domain
- Keep a small state trace while planning: after each action, update truck location, possession, and any level/count symbols so the next action starts from the previous action's result
- After generating a plan, inspect the saved plan file itself, not just planner stdout
- If logs are cut off, interrupted, or ambiguous, gather more evidence instead of inferring completion
- For multiple tasks from `problem.json`, verify each output file separately and report only checks whose confirming output you actually observed

- When using `buy`/`load`/`unload` with symbolic levels, copy the argument order from the domain schema and update those level arguments from the evolving state after each step.
- When validation tooling fails, do not promote planner output into a stronger claim of validity; either rerun validation successfully or report the narrower observed result.
- Treat final-response protocol as a verification item: immediately before finishing, compare your closing message against the task's required completion format.

