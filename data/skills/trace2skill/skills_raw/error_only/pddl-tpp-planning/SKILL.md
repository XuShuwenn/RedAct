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

1. Read the task instructions for execution constraints before acting; confirm available tools, required call format, and any exact completion signal
2. Load the full PDDL domain file and inspect complete action schemas
3. Load the full PDDL problem file and inspect complete initial facts and goals
4. If any file/tool output is truncated, cut off, or ends mid-line/mid-token, fetch the missing content before reasoning further
5. Verify action names, parameter order, preconditions/effects, predicate meanings, and any level-transition arguments from the actual domain before instantiating actions
6. Generate plan using planner, or manually derive one only after complete inspection of the full domain and problem
7. Check each planned action is applicable from the current accumulated state and update the state step by step
8. Write plan to output path
9. Read back and verify each written plan file completely before concluding success
10. Confirm outputs were produced only for tasks listed in `problem.json` and that each expected `plan_output` exists, is non-empty, and ends with a complete action line
11. Only claim validation if you actually observed successful validator/planner output or another explicit validity check

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
- Do not infer action arguments, parameter order, preconditions/effects, level transitions, initial facts, or goals from examples, memory, or partial reads
- Track state progression step by step across the plan, especially when actions encode symbolic quantity/level changes
- For multi-good plans, update before/after levels after each buy/load/unload instead of reusing the same arguments blindly
- Respect task scope: solve exactly the tasks listed in `problem.json`
- Do not rewrite `problem.json` or other input files unless explicitly instructed
- Do not call a plan valid unless you checked it against the complete domain/problem contents or observed a successful planner/validator result
- Do not claim success from partial or truncated planner output, banners, warnings, setup text, or incomplete console logs
- Verify success from the saved output artifacts, not just stdout/stderr
- Do not overwrite an existing plan file unless you have inspected it and confirmed a specific error requiring correction



## Verification Checklist

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

