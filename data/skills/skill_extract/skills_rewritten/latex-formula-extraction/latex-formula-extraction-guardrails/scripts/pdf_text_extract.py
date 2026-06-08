#!/usr/bin/env python3
"""
Lightweight, bounded PDF text extraction with simple display-formula candidate hints.

- Tries system `pdftotext -layout` if available; else falls back to PyPDF2.
- Preserves page boundaries.
- Optionally prints heuristic display-formula candidates (non-binding hints).

Usage:
  python scripts/pdf_text_extract.py input.pdf --timeout 20 --show-candidates

Notes:
- This script is for inspection and triage. Do not rely on it to produce final LaTeX.
- If both backends are unavailable, it reports the limitation and exits nonzero.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import time

try:
    from PyPDF2 import PdfReader  # Fallback backend
except Exception:
    PdfReader = None

MATH_CHARS = set("=+-*/^_\\∑∫√≈≃≤≥∞→←↔⋅·")


def run_pdftotext(pdf_path: str, timeout: int) -> str:
    if shutil.which("pdftotext") is None:
        return None
    # -layout to preserve columns/centering hints, -q to minimize noise
    cmd = ["pdftotext", "-layout", "-q", pdf_path, "-"]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.decode(errors="replace")
        return None
    except subprocess.TimeoutExpired:
        return None


def run_pypdf2(pdf_path: str, timeout: int) -> str:
    if PdfReader is None:
        return None
    start = time.time()
    try:
        reader = PdfReader(pdf_path)
        texts = []
        for page in reader.pages:
            if time.time() - start > timeout:
                return None
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                texts.append("")
        # Separate pages by form feed so downstream logic can split
        return "\f".join(texts)
    except Exception:
        return None


def split_pages(text: str):
    # pdftotext uses form feeds between pages
    return text.split("\f") if text else []


def looks_centered(line: str) -> bool:
    # Heuristic: high leading space ratio suggests centered content in monospaced layout
    if not line:
        return False
    total = len(line)
    lead = len(line) - len(line.lstrip())
    return total > 0 and (lead / max(total, 1)) > 0.2


def math_density(line: str) -> float:
    if not line:
        return 0.0
    s = line.strip()
    if not s:
        return 0.0
    return sum(1 for c in s if c in MATH_CHARS) / len(s)


def is_equation_number_only(line: str) -> bool:
    s = line.strip()
    return bool(re.fullmatch(r"\(?\d+\)?", s))


def likely_display_candidate(line: str) -> bool:
    s = line.strip()
    if not s or is_equation_number_only(s):
        return False
    dense = math_density(s) >= 0.15
    has_eq = "=" in s or "\\" in s or any(ch in s for ch in ("∑", "∫"))
    return (dense and has_eq) or (has_eq and looks_centered(line))


def main():
    ap = argparse.ArgumentParser(description="Bounded PDF text extraction with candidate hints")
    ap.add_argument("pdf", help="Input PDF path")
    ap.add_argument("--timeout", type=int, default=20, help="Per-backend timeout in seconds")
    ap.add_argument("--show-candidates", action="store_true", help="Print heuristic display-formula candidates")
    args = ap.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"ERROR: File not found: {args.pdf}", file=sys.stderr)
        sys.exit(2)

    text = run_pdftotext(args.pdf, args.timeout)
    if not text:
        text = run_pypdf2(args.pdf, args.timeout)

    if not text:
        print("ERROR: Could not extract text with available backends within timeout.", file=sys.stderr)
        sys.exit(1)

    pages = split_pages(text)
    for i, page in enumerate(pages, start=1):
        print(f"\n===== PAGE {i} =====")
        if args.show-candidates:
            for raw in page.splitlines():
                if likely_display_candidate(raw):
                    print(f"[CANDIDATE] {raw.strip()}")
        else:
            print(page)


if __name__ == "__main__":
    main()
