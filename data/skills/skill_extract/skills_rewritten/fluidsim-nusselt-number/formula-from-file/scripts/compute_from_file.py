#!/usr/bin/env python3
"""Compute a scalar result from parameters in a text file and write a
precisely formatted, rounded output line.

Features:
- Flexible parameter parsing: supports lines like `key: value`, `key = value`, or `key value`.
- Ignores comments and non-numeric suffixes (e.g., units) after the first numeric token.
- Safe expression evaluation over parsed variables with +, -, *, /, parentheses.
- Deterministic decimal rounding with trailing zeros preserved.

Usage:
  python scripts/compute_from_file.py --input INPUT --output OUTPUT --expr "h * D / k" --label "Nusselt number" --round 2
  python scripts/compute_from_file.py --input INPUT --expr "h * D / k" --round 2 --dry-run

Exit codes:
  0 on success, 1 on error.
"""

from __future__ import annotations

import argparse
import ast
import io
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, getcontext
from typing import Dict, Any

NUM_REGEX = re.compile(r"[-+]?((\d+(\.\d*)?)|(\.\d+))([eE][-+]?\d+)?")
COMMENT_SPLITS = ("#", "//", ";")


def parse_params(text: str) -> Dict[str, Decimal]:
    params: Dict[str, Decimal] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Strip comments
        for token in COMMENT_SPLITS:
            if token in line:
                line = line.split(token, 1)[0].strip()
        if not line:
            continue
        # Try key: value / key = value / key value
        key = None
        value_part = None
        if ":" in line:
            left, right = line.split(":", 1)
            key, value_part = left.strip(), right.strip()
        elif "=" in line:
            left, right = line.split("=", 1)
            key, value_part = left.strip(), right.strip()
        else:
            parts = line.split()
            if len(parts) >= 2:
                key, value_part = parts[0], " ".join(parts[1:])
        if not key or value_part is None:
            continue
        key_norm = key.strip().lower()
        m = NUM_REGEX.search(value_part)
        if not m:
            continue
        num_str = m.group(0)
        try:
            # Use Decimal for deterministic rounding and precision
            val = Decimal(num_str)
        except InvalidOperation:
            continue
        params[key_norm] = val
    return params


class SafeEvaluator(ast.NodeVisitor):
    """Safely evaluate arithmetic expressions using Decimal values.

    Allowed:
      - Binary ops: +, -, *, /
      - Unary ops: +, -
      - Parentheses
      - Names: variables from provided mapping (case-insensitive)
      - Numeric literals
    Disallowed: power, modulo, function calls, attributes, subscripts, etc.
    """

    def __init__(self, vars_map: Dict[str, Decimal]):
        self.vars = {k.lower(): v for k, v in vars_map.items()}

    def visit_Expression(self, node: ast.Expression) -> Decimal:
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp) -> Decimal:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("division by zero in expression")
            # Ensure sufficient precision for division
            getcontext().prec = max(getcontext().prec, 28)
            return left / right
        raise ValueError("Operator not allowed. Allowed operators: +, -, *, /")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Decimal:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unary operator not allowed")

    def visit_Name(self, node: ast.Name) -> Decimal:
        key = node.id.lower()
        if key not in self.vars:
            raise KeyError(f"Missing variable: {node.id}")
        return self.vars[key]

    def visit_Constant(self, node: ast.Constant) -> Decimal:  # py>=3.8
        if isinstance(node.value, (int, float)):
            return Decimal(str(node.value))
        raise ValueError("Only numeric literals are allowed")

    # For older Python versions that use Num nodes, keep compatibility
    def visit_Num(self, node: ast.Num) -> Decimal:  # type: ignore[attr-defined]
        return Decimal(str(node.n))

    def generic_visit(self, node: ast.AST) -> Decimal:
        raise ValueError("Unsupported expression element")


def safe_eval_decimal(expr: str, vars_map: Dict[str, Decimal]) -> Decimal:
    tree = ast.parse(expr, mode='eval')
    evaluator = SafeEvaluator(vars_map)
    return evaluator.visit(tree)


def format_decimal(val: Decimal, digits: int) -> str:
    if digits < 0:
        raise ValueError("digits must be >= 0")
    q = Decimal('1') if digits == 0 else Decimal('1.' + ('0' * digits))
    rounded = val.quantize(q, rounding=ROUND_HALF_UP)
    fmt = f".{digits}f"
    return format(rounded, fmt)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute a formula result from a parameter file with strict formatting.")
    parser.add_argument("--input", required=True, help="Path to input file with parameters")
    parser.add_argument("--expr", required=True, help="Arithmetic expression using parsed variables (e.g., 'h * D / k')")
    parser.add_argument("--round", type=int, default=2, help="Number of decimal places to round to (default: 2)")
    parser.add_argument("--label", default="Result", help="Label prefix for the output line (default: 'Result')")
    parser.add_argument("--output", help="Path to the output file to write the formatted result")
    parser.add_argument("--dry-run", action="store_true", help="Compute and print to stdout without writing output file")
    args = parser.parse_args()

    try:
        with io.open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"ERROR: Failed to read input file: {e}", file=sys.stderr)
        return 1

    params = parse_params(text)
    if not params:
        print("ERROR: No parameters parsed from input file.", file=sys.stderr)
        return 1

    # Evaluate expression
    try:
        value = safe_eval_decimal(args.expr, params)
    except Exception as e:
        print(f"ERROR: Failed to evaluate expression: {e}", file=sys.stderr)
        return 1

    try:
        number_str = format_decimal(value, args.round)
    except Exception as e:
        print(f"ERROR: Rounding/formatting failed: {e}", file=sys.stderr)
        return 1

    line = f"{args.label}: {number_str}\n"

    if args.dry_run or not args.output:
        # Show what would be written and the parsed params
        print(line, end="")
        return 0

    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with io.open(args.output, 'w', encoding='utf-8', newline='') as f:
            f.write(line)
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}", file=sys.stderr)
        return 1

    # Verify written content
    try:
        with io.open(args.output, 'r', encoding='utf-8') as f:
            written = f.read()
    except Exception as e:
        print(f"ERROR: Failed to verify output file: {e}", file=sys.stderr)
        return 1

    if written != line:
        print("ERROR: Output verification failed: content mismatch.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
