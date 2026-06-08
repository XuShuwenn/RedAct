#!/usr/bin/env python3
"""
Robust PDDL planning runner using unified_planning.
- Loads tasks from a JSON file (list of objects with keys: id, domain, problem, plan_output)
- Resolves paths relative to the JSON file unless already absolute
- Parses PDDL, plans, validates, and writes one action per line to the output file
"""
import argparse
import json
import sys
from pathlib import Path


def resolve_path(base_dir: Path, p: str) -> Path:
    path = Path(p)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_upf():
    try:
        from unified_planning.io import PDDLReader
        from unified_planning.shortcuts import OneshotPlanner, PlanValidator, get_environment
    except Exception as e:
        print(f"ERROR: unified_planning not available or import failed: {e}", file=sys.stderr)
        sys.exit(1)
    # Optional: suppress credits/noise (stdout), never write to plan files
    try:
        get_environment().credits_stream = None
    except Exception:
        pass
    return PDDLReader, OneshotPlanner, PlanValidator


def parse_problem(reader_cls, domain_path: Path, problem_path: Path):
    reader = reader_cls()
    return reader.parse_problem(str(domain_path), str(problem_path))


def get_plan(PlannerCls, problem):
    # Primary attempt: capability-based selection
    try:
        with PlannerCls(problem_kind=problem.kind) as planner:
            result = planner.solve(problem)
            if getattr(result, 'plan', None) is not None:
                return result.plan
    except Exception:
        pass
    # Fallback: try a small set of common planners if available in the environment
    fallback_names = [
        'pyperplan',
        'fast-downward',
    ]
    for name in fallback_names:
        try:
            with PlannerCls(name=name, problem_kind=problem.kind) as planner:
                result = planner.solve(problem)
                if getattr(result, 'plan', None) is not None:
                    return result.plan
        except Exception:
            continue
    return None


def validate_plan(ValidatorCls, problem, plan) -> bool:
    try:
        validator = ValidatorCls()
        vres = validator.validate(problem, plan)
        status_name = getattr(getattr(vres, 'status', None), 'name', None)
        return status_name == 'VALID'
    except Exception as e:
        print(f"ERROR: Plan validation failed: {e}", file=sys.stderr)
        return False


def save_plan(plan, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Expect sequential plan; write one action per line
    actions = getattr(plan, 'actions', None)
    if actions is None:
        # Fallback: iterate plan if it supports iteration
        try:
            actions = list(iter(plan))
        except TypeError:
            raise RuntimeError('Plan object does not expose actions; cannot save.')
    with output_path.open('w') as f:
        for act in actions:
            f.write(str(act).strip() + '\n')


def main():
    ap = argparse.ArgumentParser(description='Robust PDDL plan generator and validator (unified_planning)')
    ap.add_argument('--tasks', required=True, help='Path to JSON file listing tasks')
    args = ap.parse_args()

    tasks_path = Path(args.tasks).resolve()
    if not tasks_path.exists():
        print(f"ERROR: Tasks file not found: {tasks_path}", file=sys.stderr)
        return 1

    try:
        tasks = json.loads(tasks_path.read_text())
    except Exception as e:
        print(f"ERROR: Failed to parse tasks JSON: {e}", file=sys.stderr)
        return 1

    PDDLReader, OneshotPlanner, PlanValidator = load_upf()
    base_dir = tasks_path.parent

    successes = 0
    total = 0
    for t in tasks:
        total += 1
        tid = t.get('id') or f'task-{total}'
        domain = t.get('domain')
        problem = t.get('problem')
        out = t.get('plan_output')

        if not domain or not problem or not out:
            print(f"[{tid}] ERROR: Missing domain/problem/plan_output in task entry", file=sys.stderr)
            continue

        dpath = resolve_path(base_dir, domain)
        ppath = resolve_path(base_dir, problem)
        opath = resolve_path(base_dir, out)

        if not dpath.exists() or not ppath.exists():
            print(f"[{tid}] ERROR: Domain or problem file not found:\n  domain={dpath}\n  problem={ppath}", file=sys.stderr)
            continue

        try:
            prob = parse_problem(PDDLReader, dpath, ppath)
        except Exception as e:
            print(f"[{tid}] ERROR: Failed to parse PDDL: {e}", file=sys.stderr)
            continue

        # Optional brief info (stdout only)
        try:
            actions_preview = [a.name for a in list(getattr(prob, 'actions', []))[:5]]
            print(f"[{tid}] Loaded problem: {getattr(prob, 'name', '')} | actions(sample)={actions_preview}")
        except Exception:
            pass

        plan = get_plan(OneshotPlanner, prob)
        if plan is None:
            print(f"[{tid}] ERROR: No plan found by available planners", file=sys.stderr)
            continue

        if not validate_plan(PlanValidator, prob, plan):
            print(f"[{tid}] ERROR: Plan validation failed", file=sys.stderr)
            continue

        try:
            save_plan(plan, opath)
        except Exception as e:
            print(f"[{tid}] ERROR: Failed to save plan: {e}", file=sys.stderr)
            continue

        print(f"[{tid}] OK: Plan saved to {opath}")
        successes += 1

    print(f"Done. {successes}/{total} tasks solved.")
    return 0 if successes == total and total > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
