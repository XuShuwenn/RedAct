---
name: latex-formula-extraction
description: "Extract LaTeX formulas from PDF research papers, fixing display syntax errors while preserving original content."
---

# LaTeX Formula Extraction from PDF

## When to Use

- Extract mathematical formulas from academic papers
- Parse and clean LaTeX expressions
- Fix bracket/syntax display errors

## Execution Priorities

- Produce the required artifact even if extraction is partial; do not spend the whole session debugging one tool.
- Time-box extraction attempts: if a tool fails, hangs, or produces no inspectable text/files after a small number of tries, pivot to another method.
- Prefer direct, inspectable page-text extraction (for example pdfplumber or PyMuPDF) over opaque long-running conversion pipelines.
- As soon as any method yields usable page text, extract displayed formulas from that output and start writing `/root/latex_formula_extraction.md`.


## Input

- `/root/latex_paper.pdf`: Research paper PDF

## Runtime Checks

- Before running any script, verify the executable exists (`which python3`, `which python`, tool binary path).
- Prefer `python3` when invoking Python scripts unless you have confirmed another interpreter exists.
- If a command fails, capture the full stderr/traceback before retrying; do not make decisions from `Exit code 1` alone.


## Extraction Steps

1. Review the PDF page by page and identify every standalone display formula candidate, including unnumbered and multi-line formulas.
2. Extract each formula as raw LaTeX in `$$ ... $$`.
3. Preserve the exact displayed content from the PDF only when symbols and structure are clearly supported by readable extraction output or direct page inspection.
4. Remove equation tags, commas, and periods at the end of formulas only when they are not part of the math content.
5. Check each extracted formula for syntax/display issues only after the displayed formula has been reliably identified from the PDF.
6. Append corrected versions only for formulas with clear syntax/display problems.
7. If output is blank, truncated, garbled, fragmented, or mixes prose into equations, switch methods instead of inferring missing math.
8. As soon as you have a workable draft, write `/root/latex_formula_extraction.md`, then verify the file exists and that each formula is in its own `$$...$$` block.
9. Do not declare completion until all pages containing standalone formulas have been inspected.

## Evidence and Verification

- Extract formulas only from content you actually observed in readable PDF text extraction, OCR output, or page render/crop inspection.
- Do NOT claim a formula was seen or verified if the tool output was empty, unreadable, truncated, or from the wrong page region.
- Keep a one-to-one mapping between each final formula and a specific observed page/region.
- Do NOT invent missing symbols, operators, indices, bounds, fractions, delimiters, or whole formulas from context or standard notation.
- If any symbol or structure is unclear, re-extract or inspect the page again; if evidence remains insufficient, leave the formula out rather than guessing.

## Output Format

Markdown file `/root/latex_formula_extraction.md`:
```md
$$original_formula_1$$
$$original_formula_2$$

$$fixed_formula_1$$
$$fixed_formula_2$$
...
```


Write the final result to exactly `/root/latex_formula_extraction.md`; do not substitute JSON, reports, or code files for this artifact.
Write one formula per line in `$$...$$` markdown display form, with extracted originals first and fixed versions after them only when needed.
Before finishing, verify the file exists, is non-empty, and contains only the extracted display formulas in the required `$$...$$` format.

## Fix Types

- Bracket matching: (, ), [, ], {, }
- Common conversions: \ldots → ..., \cdot → ×, etc.
- Do NOT fix physics meaning, only syntax errors


- Only apply syntax/display fixes after formula fidelity is established from the PDF.
- Only fix clear display/syntax issues that are observable in the source.
- Do NOT infer unreadable or missing math from context; preserve meaning and only correct clearly visible syntax/display issues.
- If a formula is only partially recoverable, keep the directly supported text and apply only minimal syntax cleanup needed for valid display LaTeX.
- Validate extraction completeness before syntax cleanup: bracket counting alone is not enough to prove a formula is correct or fully captured.

## Tips

- Use pdfplumber or PyMuPDF for text extraction.
- Use regex only as a helper after verifying extraction quality; never rely on heuristics alone to decide a line is a formula.
- Handle multi-line formulas.
- Prefer paginated or layout-preserving extraction over flattened full-page text when formulas are mixed with prose.
- Treat OCR/text extraction as evidence gathering, not interpretation; verify finalized formulas against a visible source region when symbols, superscripts, or line breaks are unclear.
- LaTeX syntax checks can catch malformed output, but they do not confirm fidelity to the PDF; use them only as a secondary check.
- If pdfplumber is poor on a page, try PyMuPDF (or vice versa) instead of repeatedly debugging the same library.
- Manual page-by-page extraction from verified PDF evidence is an acceptable fallback.
- Use a coverage check before finishing: every page inspected, every display formula accounted for, and each extracted formula checked for balanced delimiters/braces and obvious LaTeX syntax issues.
- After extraction, read the markdown file back or otherwise confirm its contents on disk.



## Completion Checklist

## Completion Checklist

- Write the final formulas to exactly `/root/latex_formula_extraction.md`.
- If extraction is partial, save the formulas you could verify rather than ending without the file.
- Confirm the file exists, is non-empty, and contains extracted display formulas in `$$...$$` format.
- After making corrections, re-open the file to confirm the saved contents match the intended final formulas.

## Execution Workflow

## Execution Workflow

1. Start with a lightweight, inspectable method first (for example, pdfplumber or PyMuPDF).
2. Validate on 1-2 sample pages before scaling up: confirm displayed formulas are readable and not corrupted prose, Unicode fragments, or flattened layout.
3. If direct/full-file reading hits size limits, switch to page-by-page, chunked, or region-level extraction instead of retrying the same full read.
4. If a tool produces empty output, stalls, times out, or gives unusable formula text after 1-2 attempts, stop retrying it and switch to a materially different method.
5. If text extraction loses equation structure, use page rendering, OCR, or manual page-level transcription from verified PDF evidence rather than adding more heuristics.
6. Track which pages have been inspected so completeness claims are evidence-based.
