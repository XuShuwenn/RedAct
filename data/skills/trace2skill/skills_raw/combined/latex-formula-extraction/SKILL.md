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

- Treat `/root/latex_formula_extraction.md` as the primary deliverable from the start; judge progress by whether you are identifying verified formulas and updating that file, not by whether a preferred converter eventually works.
- Treat long-running or opaque full-document converters as low priority unless they quickly produce inspectable page text, page regions, or formula text.
- Validate a candidate method on 1-2 sample pages early; continue only if displayed equations remain clearly separable from prose and preserve enough structure for faithful transcription.
- Do not spend more than 1-2 failed or non-inspectable attempts on the same extractor, command family, pipeline, wrapper, or background-job variant. Timeouts, empty outputs, zero-byte files, unchanged no-output status, blank renders/OCR, or other non-inspectable results are failure evidence; pivot to a materially different method.
- Once any method yields verified formula evidence, write `/root/latex_formula_extraction.md` immediately and keep updating it as coverage improves.
- Obey any task-specific or host-environment action/completion protocol exactly as stated when one is explicitly required.


## Input

- `/root/latex_paper.pdf`: Research paper PDF

## Runtime Checks

- Before running any script, verify the executable exists (`which python3`, `which python`, tool binary path).
- Prefer `python3` when invoking Python scripts unless you have confirmed another interpreter exists.
- If a command fails, capture the full stderr/traceback before retrying; do not make decisions from `Exit code 1` alone.

- At the start, do a brief capability survey: confirm available PDF tools, Python interpreter, and whether needed modules/binaries are already usable before designing the pipeline.
- When invoking a Python-based tool, resolve the interpreter first (`which python3 || which python`) and use the one that actually exists; do not assume `python` is available.
- Before choosing an extraction path, verify the specific command/library you plan to use is actually available; for Python-based fallbacks, test imports explicitly before writing a larger script.
- Before adopting a tool as the main path, run a minimal viability test on a sample page or small slice that produces inspectable output.
- Before investing more time in a tool, confirm where its output should appear and what inspectable artifact it should produce.
- If a command fails or exits nonzero, make at most one diagnostic rerun that preserves stderr/traceback or logs; if that still does not yield actionable evidence, pivot to another method.
- If a whole-file read fails due to size limits or produces no inspectable content, switch immediately to page-by-page, chunked, search-based, or region-level extraction instead of repeating the same full read.
- Treat empty `Read(...)`, blank renders, failed crops, wrong-region captures, blank OCR, truncated page text, or missing output files as extraction failure, not as inspection.


## Extraction Steps

1. Review the PDF page by page and identify every standalone display formula candidate, including unnumbered and multi-line formulas.
1a. Keep an explicit page inventory while scanning: for each page, record whether it has zero or more standalone display formulas and whether the page evidence was readable. Do not infer completeness from grep, equation numbering, regex hits, or a single flattened text dump.
1b. For each retained formula, record a stable source reference from the current run: page number plus the text extraction, OCR result, or crop/region that actually showed it.
1c. If a page read, crop, render, or OCR result is empty, wrong-region, unreadable, or truncated, treat that as insufficient evidence and switch methods rather than transcribing from memory, context, or prior guesses.
2. Extract each formula as raw LaTeX in `$$ ... $$`.
3. Preserve the exact displayed content from the PDF only when symbols and structure are clearly supported by readable extraction output or direct page inspection.
3a. Apply an evidence gate before keeping any formula: only write it if a specific page/region shows the full displayed expression in readable text extraction, OCR, or direct visual inspection.
3b. Do not identify formulas by symbol density, line length, centering, equation-number regexes, or similar heuristics unless a human-verifiable page view already confirmed those lines are actual display equations.
3c. If extraction is partial, fragmented, page-misaligned, truncated, merged with prose, drops superscripts/subscripts/operators, shows Unicode fragments/OCR noise, reorders symbols, breaks fractions, or is otherwise ambiguous, treat it only as a lead for where to inspect next; re-extract, switch methods, or omit the formula rather than reconstructing missing math from context.
4. Remove equation tags, commas, and periods at the end of formulas only when they are not part of the math content.
5. Check each extracted formula for syntax/display issues only after the displayed formula has been reliably identified from the PDF.
6. Append corrected versions only for formulas with clear syntax/display problems.
6a. Before concluding that no fixes are needed, run an explicit formula-by-formula validation pass for delimiter balance and obvious LaTeX display syntax problems; bracket counting or successful rendering alone does not prove fidelity or completeness.
7. If output is blank, truncated, garbled, fragmented, or mixes prose into equations, switch methods instead of inferring missing math.
7a. If a tool fails twice for the same structural reason (for example timeout, missing dependency, unreadable output, flattened math, or no inspectable files), stop retrying it and pivot to a materially different method.
7b. Do not keep rerunning near-identical converter or command variants, adding long wait loops, or primarily polling `ps`/`pgrep`/output directories once a method has not produced usable text quickly.
7c. Prefer direct page-level extraction, page rendering plus visual inspection, OCR, or manual transcription from verified page regions over continued process management.
7d. If delegation is used, require the subtask to try a materially different extraction path rather than retrying the same failing workflow.
8. As soon as you have a workable draft, write `/root/latex_formula_extraction.md`, then verify the file exists and that each formula is in its own `$$...$$` block.
9. After writing, reopen and read back the saved file contents in manageable chunks if needed; confirm the contents match the intended formulas, the last formula closes with `$$`, and no line is cut off.
10. If extraction is incomplete but evidence-backed, still write the verified formulas you have now rather than delaying file creation while debugging one failing toolchain.
11. Do not declare completion until all pages have been inspected or explicitly ruled out and every page containing standalone formulas has been accounted for.

## Evidence and Verification

- Extract formulas only from content you actually observed in readable PDF text extraction, OCR output, or page render/crop inspection.
- Do NOT claim a formula was seen or verified if the tool output was empty, unreadable, truncated, or from the wrong page region.
- Keep a one-to-one mapping between each final formula and a specific observed page/region.
- Do NOT invent missing symbols, operators, indices, bounds, fractions, delimiters, or whole formulas from context or standard notation.
- If any symbol or structure is unclear, re-extract or inspect the page again; if evidence remains insufficient, leave the formula out rather than guessing.

- For each final formula, be able to point to a specific successful observation: readable extracted text, OCR output, or visible page/region content from a tool result.
- Empty image reads, blank OCR, failed renders/crops, wrong-region captures, truncated previews, broken line fragments, encoding artifacts, mixed prose/math output, or partial front-matter text do not support exact formula transcription.
- Do NOT claim to "see," "read," "verify," or "confirm" a formula unless the corresponding extraction or page/region inspection actually exposed readable content.
- Do NOT reconstruct or promote partial snippets into complete formulas from sparse prose, OCR fragments, flattened layout text, domain knowledge, or expected paper structure.
- Do NOT add or rewrite mathematical structure unless that exact structure is visibly supported by the PDF.
- Numbered-equation search, regex hits, symbol searches, and short-line heuristics are triage only; they do not replace direct review for unnumbered, multi-line, split, or layout-sensitive display formulas.
- Do NOT add a "fixed" version unless the underlying source formula was itself observed and the syntax/display problem is directly evidenced in that observed content.
- Syntax checks, balanced delimiters, and successful rendering are secondary only; they validate form, not faithfulness to the PDF.
- Do NOT claim "all formulas found" unless you completed a page-by-page coverage pass across the whole PDF and checked each page for zero-or-more display formulas.

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
Verification must inspect the actual `/root/latex_formula_extraction.md` contents on disk and confirm the saved formulas are the ones you intend to submit; reading the saved file verifies persistence only, not fidelity to the PDF.

Do not leave the final content in JSON, Python, scratch notes, or alternate output files. If you used intermediate structures, convert them into the required markdown-only `$$...$$` lines in `/root/latex_formula_extraction.md` before finishing.

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

- Treat bracket counts, syntax checks, and successful rendering as format validation only; they never replace source-based verification of every symbol against the PDF.
- Avoid opaque long-running conversion pipelines unless they quickly yield inspectable artifacts; prefer tools where you can immediately read page text or render page images.
- If sample pages show merged prose+equation text, truncated formulas, or only equation numbers/labels, escalate immediately to page-level layout inspection, rendering/cropping, OCR, or manual transcription from the visible formula region.
- When using rendered pages or crops, require legible OCR/text output or another inspectable signal before transcribing symbols from the image.
- If only one page or snippet extracts cleanly, limit output to formulas supported by that evidence rather than extrapolating unseen pages or missing symbols.



## Completion Checklist

- Do not let tool debugging, environment probing, logs, or intermediate scripts substitute for delivering `/root/latex_formula_extraction.md`.
- Verify the final formulas are saved at exactly `/root/latex_formula_extraction.md`, not only in scratch, temp, converted markdown, or other intermediate files.
- Confirm completeness from the page inventory: every page reviewed or explicitly ruled out, pages with no standalone formulas accounted for, and no final formula coming only from inference, memory, or a truncated/ambiguous observation.
- Confirm every saved formula still has a one-to-one verified page/source mapping; remove anything unsupported or derived from an invalid page region.
- Before finishing, reopen `/root/latex_formula_extraction.md` and confirm it is non-empty, contains one `$$...$$` formula per line, and that no formula or final line ending remains truncated or unverified.
- If extraction is partial, still save the verified formulas you could recover rather than ending with only diagnostics, scripts, or notes.
- If you identify a late correction, rewrite `/root/latex_formula_extraction.md`, then reread the saved file and confirm the corrected formula text appears on disk.
- If the environment specifies an exact completion string, emit it exactly as the last line after all file checks pass.

## Completion Checklist

- Write the final formulas to exactly `/root/latex_formula_extraction.md`.
- If extraction is partial, save the formulas you could verify rather than ending without the file.
- Confirm the file exists, is non-empty, and contains extracted display formulas in `$$...$$` format.
- After making corrections, re-open the file to confirm the saved contents match the intended final formulas.

## Execution Workflow

7. Before writing helper scripts, confirm the approach is viable in this runtime and preserves formula fidelity on a small sample.
8. Treat any new extraction tool as untrusted until it produces inspectable output on disk or in stdout/stderr; verify that first.
9. Do not keep polling, rerunning, or extending timeouts on the same failing conversion pipeline once you have two clear failures or no inspectable output.
10. For opaque converters or background jobs, allow at most one diagnostic foreground rerun to capture stderr or a traceback before abandoning that path.
11. After each major step, ask whether it produced readable formula evidence or updated `/root/latex_formula_extraction.md`; if not, change approach.
12. Keep a simple coverage log: page number, whether it contains standalone display math, and which extraction/viewing method verified each retained formula.
13. Once any verified formulas are available, start writing `/root/latex_formula_extraction.md` immediately and continue filling it as you inspect remaining pages.
14. When output is clipped by the shell or tool display, save the extraction to a file or inspect smaller page/region chunks; do not treat clipped console text as complete evidence.
15. If multiple tools fail or only part of the paper is recoverable, still save every directly verified formula, verify the file on disk, and continue expanding coverage only if time permits.

## Execution Workflow

1. Start with a lightweight, inspectable method first (for example, pdfplumber or PyMuPDF).
2. Validate on 1-2 sample pages before scaling up: confirm displayed formulas are readable and not corrupted prose, Unicode fragments, or flattened layout.
3. If direct/full-file reading hits size limits, switch to page-by-page, chunked, or region-level extraction instead of retrying the same full read.
4. If a tool produces empty output, stalls, times out, or gives unusable formula text after 1-2 attempts, stop retrying it and switch to a materially different method.
5. If text extraction loses equation structure, use page rendering, OCR, or manual page-level transcription from verified PDF evidence rather than adding more heuristics.
6. Track which pages have been inspected so completeness claims are evidence-based.
