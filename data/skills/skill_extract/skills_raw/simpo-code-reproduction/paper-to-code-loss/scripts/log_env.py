#!/usr/bin/env python3
"""Write Python version and pip freeze to a file for reproducibility.

Usage:
  python log_env.py --out /path/to/python_info.txt

This script captures `python -VV` and `python -m pip freeze` from the current
interpreter and writes them to the specified output file.
"""

from __future__ import annotations
import argparse
import subprocess
import sys


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.stdout


def main() -> int:
    p = argparse.ArgumentParser(description="Log Python version and pip freeze")
    p.add_argument("--out", required=True, help="Output file path")
    args = p.parse_args()

    py_ver = run([sys.executable, "-VV"]).strip()
    try:
        pip_freeze = run([sys.executable, "-m", "pip", "freeze"]).strip()
    except Exception as e:
        pip_freeze = f"pip freeze failed: {e}"

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(py_ver + "\n\n")
        f.write(pip_freeze + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
