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
- Treat protocol extraction as a hard gate: before any tool call, write down the exact required action format, allowed tool family, whether you must wait after each action, and the exact completion token/string if one is required; then use that schema verbatim for the entire task.
- Before the first tool/action, also resolve every task-provided path/identifier into the exact concrete path strings you will use (for example from task metadata or `problem.json`). Do not issue reads/writes against placeholders like `domain file path`, `first problem file path`, or guessed path variants when the task supplied concrete paths.
- If the runtime requires `Action:` followed by a JSON object, or another exact wrapper, use that exact prefix and shape on every action turn. Do not substitute native tool-call markup, XML tags, markdown code fences, helper wrappers, placeholder calls, pseudo-functions, or prose descriptions of actions.
- Treat the runtime protocol as a hard gate on every turn: before each tool/action message, re-check that you are still using the exact required wrapper/schema and allowed tool names with no substitutions or mixed styles.
- If the runtime requires one action per turn or waiting after each action, send exactly one compliant action, then wait for the observation before adding reasoning, another action, or any success claim.
- For shell execution, emit an explicit auditable command line with the actual executable and arguments; do not use narrative placeholders like `run the planner` in place of a real command.
- If a specific `Action:` block, JSON/tool schema, message structure, or bash-only workflow is required, use that format verbatim for every step; do not switch to alternate wrappers, XML/markdown tags, helper APIs, unsupported libraries, or habitual native tool-call styles mid-task.
- If the protocol requires one action per turn or waiting for an observation, issue exactly one compliant action and wait before proceeding.
- If you need planner/validator libraries beyond a shell command, first inspect the actual installed interface with a minimal probe and use only behaviors you directly observed.
- Do not describe a tool, planner, validator, or skill as invoked unless the invocation appears in the actual transcript and you have its result.
- Before the final response, re-check the completion requirement and emit the exact required token/string verbatim; if the runtime requires the final turn to contain only that string, output nothing else.

**Protocol preflight and hard-stop**
- Treat runtime interaction schema as a per-turn invariant: do not mix formats anywhere in the run, and do not claim a read, write, validation, or completion unless the transcript shows a schema-compliant action and its observation.
- If you realize mid-task that an earlier tool/action message used the wrong schema, stop assuming the environment accepted it; switch to the required format and re-establish state from accepted observations only.
- Treat harness completion as separate from artifact creation: even if plan files are correct, the task is not complete until you emit the exact required completion signal in the exact required format.
- Before the final turn, compare your drafted response to the required completion token/string character-for-character; if the task requires a bare token, reserve the final message for exactly that token and nothing else.
- Once all required output files have been written and verified, stop making file changes unless a specific unresolved defect remains; transition directly to the required completion signal.


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

1c. Write down the concrete domain path, each concrete problem path, and each concrete output path before acting; then use those exact strings consistently in every command and tool call.
1d. Before any planning, file writing, or solution claim, explicitly gate on input completeness: if you have not yet seen the full relevant domain `:action` blocks and the full problem `:init`/`:goal` for that task, your next step must be another compliant read/inspect action.
1e. Before coding against a planner library, run a tiny probe to print the actual result/status object attributes or enum members you will compare against; do not guess import names, constants, or status members from memory.
1f. If you will edit or patch any existing script/file, inspect the current file text first and anchor each change to exact observed lines; do not use placeholder replacements or guessed surrounding code.
1g. If you claim to inspect or validate via shell/Python, use an actually executable command or script body; never place narrative text, placeholders, or descriptions inside a command string.
1h. Do not create placeholder or descriptive pseudo-code files as an intermediate step: when you write a solver or validator file, make the file immediately runnable.
2. Load the full PDDL domain file and inspect complete action schemas
3. Load the full PDDL problem file and inspect complete initial facts and goals
4. If any file/tool output is truncated, cut off, or ends mid-line/mid-token, fetch the missing content before reasoning further
4a. Treat truncated or incomplete domain/problem output as a hard stop for planning: do not guess missing `:action`, `:init`, `:goal`, objects, predicates, parameter meanings, or goals from examples, memory, prior TPP patterns, or planner-output snippets.
4b. A domain is not ready for planning until the full schemas of every action you may use are visible, and a problem is not ready until the complete relevant initial facts and full `:goal` section have been explicitly inspected.
4c. Do not generate, write, validate, or describe a plan until the complete action schemas you rely on and the complete relevant problem `:init` and `:goal` sections have been directly observed.

4d. Visible truncation markers, outputs ending mid-token/mid-line, or partial reads that stop before the full domain actions or problem goal are hard blockers. Do not infer a standard TPP plan from partial snippets; fetch the missing content first.
4e. Before drafting any action sequence, explicitly confirm from the observed files that for each planned action type: (a) its full domain schema was seen, (b) the supporting current-state facts were seen in `:init` or derived from prior steps, and (c) the target goal literals were seen in `:goal`.
4f. Do not call a plan `valid`, `goal-satisfying`, or even `supported by the domain` unless you either observed the full operator definitions and checked each step against them, or observed an explicit successful planner/validator result.
5. Verify action names, parameter order, preconditions/effects, predicate meanings, and any level-transition arguments from the actual domain before instantiating actions
5a. Never assume standard TPP actions such as `drive`, `buy`, `load`, or `unload` exist or use familiar parameter orders until you have directly observed their schemas in the current domain file.
5b. For every action you plan to use, extract its full schema from the domain and map each concrete argument position back to that schema exactly; do not reuse level/count arguments from examples or prior tasks.
5c. Cross-check your intended plan against literals actually observed in the full problem file; if any planned step conflicts with the visible initial state, depends on unseen facts, or a claimed goal/fact was not directly seen, stop and inspect further before proceeding.

5d. Before writing the plan, make an explicit operator check for each distinct action used: confirm the action name appears in the domain, the number of arguments matches the schema, and each grounded argument is placed in the same parameter position as in the domain definition.
5e. Perform a contradiction scan before drafting the plan: if the observed `:init` already shows a good loaded, stored, delivered, or otherwise satisfying part of your intended setup, do not add generic acquisition/loading steps unless the full domain and goal make an additional step explicitly necessary.
5f. State the task objective only from directly observed goal literals; do not restate it as generic TPP prose such as "buy then deliver" unless those steps are actually required by the current problem.
6. Generate plan using planner, or manually derive one only after complete inspection of the full domain and problem
6a. If using a planner/skill, confirm the call actually ran and inspect its returned result or generated files before proceeding.
6b. If planner output is only banners/setup text, warnings, missing, or truncated, do not treat that as a found or validated plan; capture more reliable output or debug the invocation/result.

6b1. Planner credits, startup banners, parser messages, or search statistics without the actual action sequence are not a plan; do not write any `plan_output` file from such output.
6b2. If the observed plan text is truncated even within a single action line, do not reconstruct or guess the missing suffix from context; rerun, read the saved planner output directly, or otherwise obtain the complete line first.
6b3. When invoking the planner via shell, ensure the transcript contains the concrete command you ran.
6b4. If solver/script output shows only startup text, planner banners, `Generating plan...`, the beginning of a batch run, or only some tasks, do not infer whole-run success from generated files alone; directly confirm completion for the full run via explicit end-of-run output, exit status, or a targeted rerun with clearer logging.
6c. If expected plan files are missing, do not assume silent success.
6d. Switch to manual derivation only if planner use is unavailable or failing, and then keep the same semantic-validation standard.

6e. If the first implementation fails because of an import, attribute, signature, or return-shape mismatch, stop and re-probe the installed API directly; do not continue by guessing alternate class names or object interfaces.
6f. Treat a solver/script/planner run as unverified until you observe end-of-run evidence such as an exit code, shell prompt return, explicit per-task completion message, or other clear indication the process finished; startup banners or early log lines are not enough.
6g. If you debug or modify a solver/script, first read the current file contents and identify the exact lines or logic causing the failure; after rerunning, verify the repaired path end-to-end from actual output artifacts rather than treating the absence of a crash as success.
6h. Do not treat a hand-derived plan as solved merely because it looks plausible or parses; after manual derivation, either obtain a real semantic applicability/goal check or keep the result labeled unconfirmed.
7. Check each planned action is applicable from the current accumulated state and update the state step by step
7a. Keep a small state trace while planning: after each action, update truck location, where each good is, possession, and any before/after symbolic level values touched by buy/load/unload so later steps use the post-state from earlier actions.
7b. Compare the planned steps against the observed initial state before writing: if a fact such as a good already being loaded, available, or otherwise satisfied is already true, do not add redundant setup actions unless the full domain and goal show they are still required.

7b-i. Do not default to a generic `buy -> load -> drive -> unload` template. If the observed initial state already contains facts showing a good is loaded, available, or otherwise already satisfies part of that sequence, do not add redundant `buy(...)` or `load(...)` actions unless the full domain/problem shows they are still required.
7c. Check the final accumulated state against the explicit problem goal literals before writing or claiming success.
7d. If a generated plan file already exists, inspect it completely first and overwrite it only after confirming a specific defect, incompleteness, or mismatch with the validated plan.
8. Write plan to output path
8a. After writing, obtain direct confirmation by reading back the saved file or otherwise observing the write result; do not declare success based only on an attempted write command.

8b. Claims about saved outputs must be traceable to observed evidence: send the actual write command in the required runtime format, wait for its observation, then confirm the file exists or read it back.
8c. Never narrate a write as completed inside the same turn that issues the write action, and if the transcript lacks both the write step and confirming observation for a file, treat that file as not yet proven written.
8d. After each write, read the saved plan file back completely or with unambiguous completeness checks such as line count plus final-line read before doing anything that signals completion.
8e. Write only concrete grounded action lines to each `plan_output`; never write summaries, placeholders, TODO notes, comments, or narration. If you cannot yet produce an actual action-by-action plan for a task, leave the task unresolved and continue debugging/inspection.
8f. If the environment is one-action-per-turn, write only one file per turn and wait for its observation before attempting the next file or verification read.
8g. After any rewrite meant to fix or reformat a plan file, reread the full saved file and confirm it still contains the intended action sequence rather than placeholder text or a partial copy.
9. Read back and verify each written plan file completely before concluding success; if any read/output is truncated, ambiguous, or cut off, re-read with targeted per-file reads, line counts, or final-line inspection until completeness is explicit.
9a. If any saved plan file is truncated, malformed, empty, or ends mid-line/mid-token, treat the task as unresolved: regenerate or repair the plan, then reread the corrected file before continuing.
9b. If planner/validator output, your notes, and the saved file contents disagree on action count, final actions, or completion, treat the task as unresolved and debug/regenerate from the saved artifact instead of narrating unobserved actions.

9c. If a planner reports N actions but the saved file readback shows fewer visible lines or ends earlier than the reported final action, do not declare success. Re-read the file with a targeted completeness check and repair/regenerate until the saved artifact and observed evidence agree.
10. Confirm outputs were produced only for tasks listed in `problem.json` and that each expected `plan_output` exists, is non-empty, and ends with a complete action line.
10a. For each task in `problem.json`, gather direct evidence for that specific output file; do not infer batch success from partial run logs, startup banners, warnings, or the mere presence of multiple files.

10aa. Do not use proxy checks such as `wc -l problem.json`, file size, or banner text to claim how many tasks exist or were completed; inspect or parse the actual manifest entries and cross-check each listed `plan_output` directly.
10b. Verify each saved plan contains the actual final goal-achieving step(s) required by the problem; never infer a missing final unload/delivery or other goal step from planner intent.
10c. If any expected file is missing, malformed, truncated, or lacks a required goal step, treat the run as incomplete and regenerate/debug instead of reporting success.

10d. When solving multiple tasks, track planner/validator evidence per task and per output file. Do not summarize all tasks as validated or confirmed unless you observed separate explicit evidence for each one.
10e. Do not mark a task solved or emit the final completion signal until you have directly inspected that task's saved `plan_output` and confirmed it contains actual action lines rather than prose or placeholders.
10f. If any inspected output file ends mid-token, mid-action, or otherwise contradicts your planned or claimed result, stop and debug from that artifact; do not make final success claims until the contradiction is resolved.
11. Distinguish `planner produced a plan` from `plan was validated`; only use validation language if you actually observed a successful validator/planner check or another explicit validity check.

11a. Do not say a plan is "syntactically correct," "valid," or "goal-satisfying" unless the transcript contains either an observed validator/planner success result or a complete manual step-by-step applicability and goal check against the full domain/problem.
11b. If validation tooling fails, imports fail, or the command is malformed, treat validation as not obtained; report the narrower observed fact only.
12. Before the final response, re-check the runtime instructions so the last message matches any required completion token or final-response schema exactly.

12a. Final gate before replying: confirm (i) every required output file was reread after writing, (ii) no plan was derived from truncated domain/problem views, (iii) any claimed validity is backed by observed validation or manual state/goal checking, and (iv) the final response text exactly matches the required completion protocol.
12b. If the environment responds after your apparent completion with a prompt such as `Please continue`, first assume the completion handshake may have failed; inspect your immediately previous turn against the required final token/string before doing any new task work.
12c. If all requested outputs already exist and were verified, do not reopen planning, inspect unrelated files, or expand scope after a rejected completion attempt; correct the final-response protocol and finish.

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

This section shows only a common textual layout. Do not assume these exact action names, argument counts, parameter orders, or syntax are valid for the current task until you have observed the full domain and any task-specific output requirements.



## Requirements

- Plan must be syntactically correct PDDL
- Plan must be valid (solves problem)
- Action/object names must match domain and problem


- Plan must be based on complete, non-truncated domain and problem content
- Do not infer action arguments, parameter order, preconditions/effects, level transitions, initial facts, or goals from examples, memory, or partial reads; if the relevant domain/problem section is incomplete, gather more content before planning

- Do not write grounded actions with guessed arity or argument order. If the domain output has not yet shown the relevant `:action` definition, you are not allowed to instantiate that operator in the plan.

- Track state progression step by step across the plan, especially when actions encode symbolic quantity/level changes
- For multi-good plans, update before/after levels after each buy/load/unload instead of reusing the same arguments blindly
- Respect task scope: solve exactly the tasks listed in `problem.json`

- Use the exact concrete domain/problem/output paths supplied by the task or manifest; never substitute placeholder labels, paraphrased names, or guessed path variants in tool calls.

- Do not rewrite `problem.json` or other input files unless explicitly instructed
- Do not call a plan valid unless you checked it against the complete domain/problem contents or observed a successful planner/validator result

- Do not state that a plan is syntactically correct, satisfies preconditions, achieves goals, or is valid unless you actually observed one of: (a) a successful planner/validator/checker result, or (b) a complete manual step-by-step applicability and goal check grounded in the full domain and problem files.
- If validator or semantic-check scripts fail, error out, never report success, or only show setup/banner text, do not replace that missing evidence with stronger wording such as `valid`, `confirmed`, or `matches all specifications`; report only the weaker observed facts.

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

- If the environment mandates a specific tool/action schema, use only that schema for all tool interactions and wait for each observation when required.
- When an exact completion token is required, the final turn should contain only that token/string unless the runtime instructions explicitly allow extra text.
- Do not claim completion after writing files unless you have reread the saved artifacts and performed an explicit validation or manual applicability/goal check.
- Do not derive or write a plan from any domain/problem view that is truncated, cut off before full action schemas, or missing relevant `:init`/`:goal` content.

- Treat protocol compliance as a hard requirement: if the environment mandates a specific action schema or an exact completion token, use that literal format throughout and do not replace it with native tool calls, alternate wrappers, or a narrative closing summary.
- Do not use narrative placeholder commands for planning or validation steps; every claimed check must correspond to a concrete executable command or required action payload whose result you observed.
- Saved `plan_output` files must contain actual plan lines only; do not write explanatory prose, placeholders, status messages, comments, or summaries into them.
- Do not create or edit solver code from a high-level description alone; read the actual file contents before modifying, and make the first saved version runnable rather than descriptive pseudo-code.
- If a validator import, command, or API call fails, treat validation as not obtained.
- If a saved plan ends with movement or another intermediate step, do not assume the goal is satisfied; compare the ending against the explicit goal literals and require the actual final goal-achieving step when needed.
- Do not claim that all tasks completed, that validation succeeded, or that plans contain N actions unless those outcomes are directly supported by visible command output or complete file inspection.
- Existing output files prove artifacts exist, not that a batch script processed every task or exited successfully; claims about execution completion require separate observed evidence.
- If the system rejects an apparent completion and asks to continue, diagnose the completion-format mismatch first; do not assume solved tasks need to be redone or broaden scope beyond `problem.json`.
- Do not write status checks like `... == SOME_GUESSED_CONSTANT` until you have directly observed the installed enum/status member names from a probe or REPL snippet.
- If you edit a script, ground each patch in the current file contents; never apply abstract or guessed replacements against unread code.
- When checking planner success, do not reject a result just because the status is a solved variant rather than one single exact string; verify against the observed API behavior.
- If planner output and your script's `no plan found` branch disagree, stop and inspect the returned status/result object before continuing.
- Never write placeholder text, summaries, comments, or meta-descriptions into a `plan_output` file; each non-empty line must be an actual plan action in the required syntax.
- A file existing at the right path is not enough: inspect the saved contents and verify they are concrete action lines before claiming the task is solved.




## Verification Checklist

- If stdout/stderr or combined file output is truncated, inspect each expected `plan_output` separately before claiming batch success.
- Confirm you observed complete domain action schemas and complete problem `:init`/`:goal` content for each solved task; otherwise do not claim the plan is valid.
- Confirm your actual tool usage matched the runtime-required invocation schema throughout the task; no mixed formats, and observation waits were respected when required.

- Check the transcript itself for protocol compliance: every tool turn must use the mandated schema, with no stray alternate tool-call formats anywhere in the run.
- Confirm every read/write/execute action used the exact concrete file paths from the task metadata or `problem.json`, not placeholders or shorthand descriptions.

- If you used any external library API, verify your implementation against directly observed probe results rather than assumptions.
- For each distinct action schema used in the plan, compare a grounded instance against the domain parameter order before saving the file.
- Reject any plan where the written level/count arguments do not match the state transition you are relying on.
- Check the last line of each saved plan file; it must be a complete action, not a cut-off fragment.
- Before declaring success, reread each saved plan file and confirm it still matches the checked action schemas and accumulated state trace.
- If any saved plan read shows fewer actions than expected, ends earlier than the generated plan, or the tool output is cut off, inspect the file again before claiming success.
- For each task, verify the saved file contains the required final goal-achieving action(s); a plan ending at `drive(...)` is not enough when an `unload(...)` or other delivery step is still required.
- Reconcile contradictions before finishing: if logs, notes, or saved files disagree on plan length, ending, or validation status, investigate and verify again instead of trusting partial evidence.
- Distinguish artifact checks from execution checks: saved plan files confirm outputs, while planner/validator/script completion claims require directly observed command output or an explicit manual applicability/goal check.

- If script output stops at setup text, planner banners, or messages like `Generating plan...`, treat validation/execution status as unconfirmed until you inspect clearer output, exit status, generated artifacts, or rerun with more explicit logging.

- Base final claims on observed artifacts only: say the planner produced/wrote a plan unless you also observed a separate successful validation check.
- If no validator/planner confirmation is available, only report success after a manual step-by-step applicability check against the complete domain and problem.

- If neither a successful checker run nor a complete manual applicability/goal trace was observed, do not claim the plan is correct; report the narrower observed result only, such as that a file was written in a given format.

- For multi-good or repeated resource actions, review the state trace and ensure each later level/count argument reflects the updated post-state.
- Confirm your own tool/action messages followed the required schema throughout, and if an exact completion token is required, make the final response exactly that token.

- If multiple tasks were solved, verify you have explicit observed validation or applicability evidence for each task before saying `all` or `both` are valid.
- If any validator/planner invocation failed earlier, confirm you reran verification with the corrected interface and directly observed a clean success result before finishing.
- Immediately before the last turn, compare your intended final message to the exact required completion string character-for-character; if the environment says the final turn must contain only that token, output only that token.

- Before the first tool/action, restate the exact runtime interaction contract to yourself: required message schema, allowed tool family, one-action-per-turn rule if any, wait-for-observation rule if any, and exact final completion token.
- Immediately before each tool/action turn, confirm the outgoing message still uses the exact required runtime syntax; a correct plan does not compensate for a malformed action message.
- Check transcript compliance, not just intent: each claimed read/write/validation step should correspond to a visible compliant action and a resulting observation.
- Before any code edit, confirm you have directly observed the file's current contents and the API names or text you are changing.
- If you wrote or edited a solver script, open it or run a syntax/basic execution check before relying on it.
- Confirm each `plan_output` file contains only plan actions, not prose, placeholders, summaries, or notes about what was supposedly generated.
- If planner output reports more actions than are visible in the saved file, trust the saved file readback over the planner summary and continue debugging instead of asserting unseen final steps.
- For batch runs, obtain direct evidence for each listed `plan_output` separately; truncated combined output is not enough to confirm completeness.
- Do not treat file counts, byte counts, or similar proxies as evidence of task count or completion; verify by reading/parsing `problem.json` entries and matching each one to an observed output file.
- If any critical input read or planner output was truncated, the next observed step should be another compliant read or rerun to obtain the missing content, not plan generation, file writing, or completion.
- Before the first tool call, confirm your next message uses the runtime-mandated invocation format exactly; if not, rewrite it before sending.
- If you did not directly observe complete domain action schemas and complete problem `:init`/`:goal` sections, do not write or save a plan yet.
- Before any script edit, reread the target file/section and ensure the replacement text matches strings or lines you actually observed.
- Before concluding `no plan found`, inspect the actual planner status value and confirm you are not ignoring a solved-status variant.
- Ask before finishing: did I directly observe a compliant read of all needed `:action`, `:init`, and `:goal` content, a compliant write for each output file, and a compliant readback/check for each file? If any answer is no, do not complete yet.
- Before saving or reporting a plan, verify every action in it passes this gate: observed schema, applicable from the observed/updated state, and relevant to an explicitly observed goal.
- Open each saved `plan_output` and sanity-check that every non-empty line is a grounded action, not explanatory prose, placeholders, or TODO text.
- If a planner/output log reported a final action that is not visible in the saved file readback, treat the file as unconfirmed; inspect that file again and do not claim it is complete until the missing final action is directly observed or the artifact is regenerated.
- For each good/object mentioned in the plan, compare the planned setup actions against the observed `:init`: if the file already shows that object loaded, at destination, or otherwise prepared, remove any redundant setup steps unless a directly observed goal or precondition still requires them.
- Before any final completion token/string, confirm every task marked complete has a directly inspected saved file with concrete plan content.
- If the system says `Please continue` right after a completion attempt, check whether the last message violated the completion protocol before doing any additional inspection or generation.


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

