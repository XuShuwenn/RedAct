---
name: pddl-upf-robust-planning
description: "Generate, validate, and save PDDL plans reliably using unified_planning with correct API usage, result handling, and file-path hygiene."
---

# Robust PDDL Planning with unified_planning

A reusable workflow to load PDDL domain/problem pairs, generate a plan, validate it, and save the plan to disk. Focused on avoiding common API, status-handling, and path-handling pitfalls often seen with unified_planning.

## When to Use

Use this skill when you must:
- Read a task list (e.g., problem.json) that references PDDL domain and problem files
- Generate a PDDL plan per task using unified_planning
- Validate the plan before saving
- Write one action per line to an output file

## Core Workflow

1. Read task list
- Parse the JSON list of tasks that includes: id, domain, problem, plan_output.
- Resolve all paths relative to the JSON file’s directory unless already absolute.

2. Parse PDDL
- Use PDDLReader.parse_problem(domain_path, problem_path).
- Inspect problem metadata using supported attributes:
  - problem.name
  - problem.goals
  - list(problem.actions)
  - list(problem.all_objects)

3. Select and run a planner
- Prefer OneshotPlanner(problem_kind=problem.kind). If planner selection fails or returns no plan, optionally try a small fallback list of available planners by name (only if present in the environment).
- Solve with result = planner.solve(problem).

4. Treat result robustly
- Do not rely on exact status names. Plans may be returned with statuses like SOLVED_SATISFICING or SOLVED_OPTIMALLY.
- Robust rule: if result.plan is not None → proceed; otherwise, treat as failure.

5. Validate the plan
- Use PlanValidator(): validation = validator.validate(problem, plan).
- Success criterion: validation.status.name == "VALID".
- If unavailable, do not substitute unsupported classes; instead, surface a clear error.

6. Save the plan
- Create parent directories for the output path.
- Write exactly one action per line using str(action_instance). Do not include numbering, extra commentary, or logging in the plan file.

## Verification

Before finalizing:
- Check that domain/problem files exist and are readable.
- Confirm result.plan is not None and validator returns VALID.
- Ensure the output file contains only action lines (no prefixes, counts, or extra prints).
- Confirm action names/objects align with domain/problem symbols (stringified action instances produced by unified_planning typically satisfy this).

## Common Pitfalls and How to Avoid Them

- Wrong validator class or signature:
  - Pitfall: Importing/using non-existent or deprecated classes (e.g., SequentialPlanValidator) or calling validate with wrong arguments.
  - Avoid: Use from unified_planning.shortcuts import PlanValidator and call validator.validate(problem, plan). Check that validation.status.name == "VALID".

- Overly strict status checks:
  - Pitfall: Requiring status == "SOLVED" and discarding satisficing/optimal solutions.
  - Avoid: Accept any result with result.plan is not None.

- Incorrect problem attribute access:
  - Pitfall: Accessing non-existent attributes like problem.domain_name, or using methods/properties incorrectly (e.g., objects vs all_objects).
  - Avoid: Use problem.name, problem.goals, list(problem.actions), list(problem.all_objects).

- Path mishandling:
  - Pitfall: Prepending fixed prefixes to paths from JSON (e.g., always adding "/..."), breaking valid relative/absolute paths.
  - Avoid: Resolve paths relative to the JSON file directory and honor absolute paths as-is.

- Polluting plan files:
  - Pitfall: Writing debug output, numbering, or planner credits into the plan file.
  - Avoid: Only write str(action_instance) per line. Suppress planner credits to stdout if needed; never redirect such output into the plan file.

- Planner availability assumptions:
  - Pitfall: Hard-coding unavailable planners or not providing a fallback.
  - Avoid: Start with OneshotPlanner(problem_kind=problem.kind). If plan is None, try a short, environment-aware fallback list (only if installed).

## Success Criteria

- For each task: a plan file is created at the specified path.
- Each line contains a single action instance in PDDL-like syntax (action_name(object1, object2, ...)).
- The plan validates with status VALID against the given domain/problem.

## Optional Script Usage

A reference runner script is included under scripts/ to implement this workflow end-to-end. It:
- Loads tasks from a JSON file
- Resolves paths safely
- Parses PDDL
- Plans with robust result handling
- Validates with PlanValidator
- Writes one action per line in the specified output file

Run example:
- python3 scripts/pddl_plan_runner.py --tasks problem.json
