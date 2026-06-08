#!/usr/bin/env python3
"""
PDDL plan static checker: validates plan formatting, action existence & arity, and object existence.

Usage:
  python scripts/pddl_plan_check.py --domain DOMAIN.PDDL --problem PROBLEM.PDDL --plan PLAN.TXT

What it checks:
- Each plan line matches: action_name(arg1, arg2, ..., argN)
- action_name is defined in the domain
- number of arguments equals the domain's action parameter count
- each arg is an object present in the problem's :objects or a domain :constant

Limitations:
- Does not perform semantic validation (state progression); use a validator if available.
- PDDL parsing here is heuristic and aimed at common layouts.
"""

import argparse
import os
import re
from typing import Dict, List, Set, Tuple

ACTION_DEF_RE = re.compile(r"\(\s*:action\s+([a-zA-Z0-9_\-]+)", re.IGNORECASE)
PARAMS_START_RE = re.compile(r"\s*:parameters\s*\(", re.IGNORECASE)
PLAN_LINE_RE = re.compile(r"^\s*([a-zA-Z0-9_\-]+)\(([^)]*)\)\s*$")


def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def tokenize(s: str) -> List[str]:
    # Simple whitespace tokenization for PDDL sections
    return re.findall(r"[()\-]|[^\s()]+", s)


def parse_domain_actions(domain_path: str) -> Dict[str, int]:
    """Return mapping: action_name -> number of parameters (arity)."""
    text = read_text(domain_path)
    actions: Dict[str, int] = {}

    idx = 0
    lines = text.splitlines()
    while idx < len(lines):
        line = lines[idx]
        m = ACTION_DEF_RE.search(line)
        if not m:
            idx += 1
            continue
        action_name = m.group(1)
        # Find parameters section possibly spanning multiple lines
        params_str = ""
        found_params = False
        # scan forward for ":parameters (" then collect until matching ")"
        j = idx
        paren_depth = 0
        while j < len(lines):
            l2 = lines[j]
            if not found_params:
                if PARAMS_START_RE.search(l2):
                    found_params = True
                    # collect from this line onward
                    # find opening paren position and take substring
                    start_pos = l2.lower().find(':parameters')
                    params_str += l2[start_pos:] + "\n"
                    # initialize paren depth counting only after '(' following :parameters
                    # We'll count all parentheses in subsequent lines until we see a closing ')' that balances
                j += 1
                continue
            else:
                params_str += l2 + "\n"
                # crude but effective: track parentheses after we encountered :parameters
                paren_depth += l2.count('(') - l2.count(')')
                # Stop when we've seen net closing that returns to non-positive; we ensure at least one ')'
                if paren_depth <= -1:
                    break
                j += 1
        # Extract variables starting with '?' within the collected params block
        var_count = 0
        if params_str:
            # Extract content between first '(' after :parameters and its matching ')' by regex
            mparams = re.search(r":parameters\s*\((.*?)\)", params_str, flags=re.IGNORECASE | re.DOTALL)
            if mparams:
                inner = mparams.group(1)
                # Count variables beginning with '?'
                # Handle typed lists: ?x - type ?y - type2
                tokens = tokenize(inner)
                k = 0
                while k < len(tokens):
                    tok = tokens[k]
                    if tok.startswith('?'):
                        var_count += 1
                        # Skip possible typing: '-' type
                        if k + 2 < len(tokens) and tokens[k + 1] == '-':
                            k += 3
                            continue
                    k += 1
        if action_name and action_name not in actions:
            actions[action_name] = var_count
        idx = j + 1 if j > idx else idx + 1

    return actions


def parse_domain_constants(domain_path: str) -> Set[str]:
    """Parse domain :constants into a set of names."""
    text = read_text(domain_path)
    consts: Set[str] = set()
    # Find :constants blocks, possibly multiple
    for m in re.finditer(r"\(\s*:constants(.*?)\)", text, flags=re.IGNORECASE | re.DOTALL):
        section = m.group(1)
        tokens = tokenize(section)
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == '-':
                # next token is a type; skip
                i += 2
                continue
            if tok not in ('(', ')'):
                consts.add(tok)
            i += 1
    return consts


def parse_problem_objects(problem_path: str) -> Set[str]:
    """Parse problem :objects into a set of object names."""
    text = read_text(problem_path)
    objs: Set[str] = set()
    m = re.search(r"\(\s*:objects(.*?)\)", text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return objs
    section = m.group(1)
    tokens = tokenize(section)
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == '-':
            # skip type token
            i += 2
            continue
        if tok not in ('(', ')'):
            objs.add(tok)
        i += 1
    return objs


def parse_plan(plan_path: str) -> List[Tuple[str, List[str]]]:
    """Parse plan lines of the form action(arg1, arg2, ..., argN)."""
    items: List[Tuple[str, List[str]]] = []
    with open(plan_path, 'r', encoding='utf-8') as f:
        for ln, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                # skip empty lines but record as warning
                continue
            m = PLAN_LINE_RE.match(line)
            if not m:
                raise ValueError(f"Line {ln}: invalid format; expected name(arg1, ..., argN)")
            name = m.group(1)
            args_str = m.group(2).strip()
            if args_str == "":
                args = []
            else:
                args = [a.strip() for a in args_str.split(',')]
            items.append((name, args))
    return items


def check_plan(domain_path: str, problem_path: str, plan_path: str) -> List[str]:
    errors: List[str] = []
    if not os.path.exists(domain_path):
        errors.append(f"Domain file not found: {domain_path}")
        return errors
    if not os.path.exists(problem_path):
        errors.append(f"Problem file not found: {problem_path}")
        return errors
    if not os.path.exists(plan_path):
        errors.append(f"Plan file not found: {plan_path}")
        return errors

    try:
        actions = parse_domain_actions(domain_path)
    except Exception as e:
        errors.append(f"Failed to parse domain actions: {e}")
        return errors

    try:
        domain_consts = parse_domain_constants(domain_path)
    except Exception as e:
        errors.append(f"Failed to parse domain constants: {e}")
        domain_consts = set()

    try:
        objects = parse_problem_objects(problem_path)
    except Exception as e:
        errors.append(f"Failed to parse problem objects: {e}")
        objects = set()

    try:
        plan_items = parse_plan(plan_path)
    except Exception as e:
        errors.append(str(e))
        return errors

    if not plan_items:
        errors.append("Plan is empty or contains only blank lines.")
        return errors

    allowed_objects: Set[str] = set(objects) | set(domain_consts)

    for idx, (name, args) in enumerate(plan_items, start=1):
        if name not in actions:
            errors.append(f"Line {idx}: unknown action '{name}' (not found in domain)")
            continue
        expected_arity = actions[name]
        if len(args) != expected_arity:
            errors.append(
                f"Line {idx}: action '{name}' expects {expected_arity} args, found {len(args)}: {args}"
            )
        for a in args:
            # Accept hyphens/underscores; check existence if objects known
            if allowed_objects and a not in allowed_objects:
                errors.append(f"Line {idx}: object '{a}' not found in problem :objects or domain :constants")

    return errors


def main():
    ap = argparse.ArgumentParser(description="Static checker for PDDL-style plans.")
    ap.add_argument("--domain", required=True, help="Path to domain PDDL file")
    ap.add_argument("--problem", required=True, help="Path to problem PDDL file")
    ap.add_argument("--plan", required=True, help="Path to plan file")
    args = ap.parse_args()

    errs = check_plan(args.domain, args.problem, args.plan)
    if errs:
        print("PLAN CHECK: FAILED")
        for e in errs:
            print(f"- {e}")
        raise SystemExit(1)
    else:
        print("PLAN CHECK: OK")


if __name__ == "__main__":
    main()
