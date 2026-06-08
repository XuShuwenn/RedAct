---
name: latex-formula-extraction-guardrails
description: "Use when extracting display-mode LaTeX formulas from PDFs to avoid tool timeouts, hallucinated content, and syntax mistakes."
---

# Robust Guardrails for Extracting Display LaTeX from PDFs

This skill provides a failure-avoidance workflow for extracting standalone (display-mode) LaTeX formulas from PDFs. It focuses on preventing tool timeouts, avoiding fabricated content, and ensuring syntactic validity of the final `$$ ... $$` output.

## When to Use

Activate this skill when the user asks to:
- extract all display-mode (standalone) formulas from a PDF
- output one formula per line wrapped in `$$ ... $$`
- remove trailing punctuation and equation tags
- append fixed lines only for syntax/typo corrections

## Core Workflow

1) Prepare and Bound the Plan
- Confirm the input PDF exists and is readable.
- Set short per-attempt timeouts (e.g., tens of seconds, not minutes) for any conversion; do not leave long-running background processes.
- Plan fallbacks before running anything: prefer lightweight text extraction over heavy PDF-to-markdown conversions that tend to hang.

2) Use Lightweight, Fallback-Friendly Text Extraction
- First try a layout-preserving text extractor if available (e.g., a system `pdftotext -layout`).
- If unavailable, try a Python-based text reader with minimal dependencies.
- Keep strict timeouts. If an attempt produces no output or hangs, abort and immediately switch to the next fallback—do not keep retrying the same approach with longer timeouts.

3) Keep Page Boundaries and Identify Display Candidates
- Retain per-page text segmentation during extraction.
- Identify likely display-formula lines by combining these signals:
  - Center-aligned or low surrounding text density on the page.
  - High math-token density (e.g., `=`, `+`, `-`, `*`, `/`, `^`, `_`, `\`-commands, `∑`, `∫`, `√`, `⋅`).
  - Equation-number adjacency (e.g., nearby lines with `(n)`), but do not include the number itself.
- If a formula is split across lines, join lines only when there is clear syntactic continuation (e.g., unmatched brackets or trailing operators). Avoid over-joining surrounding body text.

4) Reconstruct Minimal LaTeX Without Inventing Content
- Use only symbols you observed in the extracted text. Do not guess missing terms.
- Normalize obvious encodings (e.g., replace unicode minus `−` with `-`, middle dot `·` or `⋅` with `\cdot`).
- Remove trailing punctuation (commas, periods, semicolons, colons) after the formula, not internal punctuation.
- Remove equation tags/labels from the formula (e.g., `(1)` at the end or start), but keep all mathematical content.
- Wrap each finalized formula as a single line in `$$ ... $$`.

5) Syntax Verification Before Finalizing
- For each formula string between the `$$` delimiters, verify:
  - Balanced brackets: `()`, `[]`, `{}`.
  - `\left`/`\right` pairing; if mismatched, either add the partner or remove both to plain delimiters, preserving the intended grouping.
  - No trailing punctuation after cleanup.
  - Non-empty content with at least one math indicator (operator or LaTeX command) to reduce false positives from body text.
- If a formula requires a purely syntactic correction (e.g., missing brace, mismatched `\left/\right`), append a fixed version as a new line after the original. Do not change mathematical meaning or restyle unless it is a clear syntax/typo correction.

6) Final Output and Self-Check
- Ensure one formula per line, each wrapped in `$$ ... $$`.
- Re-read the output file contents and check that there are no placeholders, no duplicated equation numbers, and no inline/body-text inclusions.
- Only claim completion after verifying that the output file matches the above criteria.

## Verification

Use this checklist before finalizing:
- Extraction logic:
  - Did a lightweight extractor produce page text within bounded time?
  - Did you avoid re-running a hanging tool and pivot to a fallback?
- Candidate picking:
  - Do lines look like standalone equations (centered/isolated, math-token dense)?
  - Were equation numbers excluded from the formulas?
- LaTeX validity:
  - Are `()[]{}` balanced?
  - Are `\left` and `\right` pairs balanced?
  - Are trailing commas/periods removed?
  - Is each formula non-empty and wrapped in `$$ ... $$`?
- Fix-only additions:
  - Are added extra lines limited to syntax/typo fixes for previously listed formulas?

Success criteria:
- Every output line is a single display formula `$$ ... $$` without trailing punctuation or equation labels.
- All LaTeX delimiters are balanced; no placeholders or invented content.
- If a syntax issue existed, a fixed version is appended after the original.

## Common Pitfalls and How to Avoid Them

- Hanging conversions and busy-waiting:
  - Symptom: Long-running PDF-to-markdown processes with no output.
  - Avoidance: Impose short timeouts, switch to a simpler text extractor, and never retry the same failing approach with longer waits.

- Fabricated formulas or placeholders:
  - Symptom: Writing `...` or content not grounded in extracted text.
  - Avoidance: Only emit formulas observed from the document. If you cannot extract reliably, report limitations rather than invent content.

- Including inline math or equation numbers:
  - Symptom: Lines that are part of continuous text or that contain `(12)` as part of the output.
  - Avoidance: Use isolation and math-density signals; strip numbering and keep only the mathematical expression.

- Broken or mismatched delimiters:
  - Symptom: Unbalanced `{}`, `[]`, `()`, or `\left` without `\right`.
  - Avoidance: Run bracket and `\left/\right` checks; minimally repair or convert to plain delimiters.

- Trailing punctuation and tags:
  - Symptom: Ending with `,` or `.` or retaining "Eq. (n)".
  - Avoidance: Strip trailing punctuation and tags after mathematical content only.

- Over-editing beyond syntax fixes:
  - Symptom: Changing mathematical structure or improving style.
  - Avoidance: Only fix clear syntax/typo issues; do not alter meaning or layout unnecessarily.

## Optional Script Usage

Two optional helper scripts are provided:
- scripts/pdf_text_extract.py: Attempts bounded, fallback text extraction by page and prints likely display-candidate lines (heuristic). Use to inspect candidates, not as a final extractor.
- scripts/latex_sanity.py: Checks bracket balance and simple LaTeX hygiene on `$$...$$` lines and proposes minimal syntax-only fixes.

Example usages:
- Inspect PDF text and candidate lines:
  - python scripts/pdf_text_extract.py path/to/paper.pdf --timeout 20 --show-candidates
- Validate and normalize formula lines (from a file of `$$...$$` lines):
  - python scripts/latex_sanity.py --file extracted_formulas.md --suggest-fixes

These scripts are conservative utilities to reduce common errors; they do not replace careful, page-aware human verification.
