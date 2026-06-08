---
name: latex-formula-extraction
description: "Extract LaTeX formulas from PDF research papers, fixing display syntax errors while preserving original content."
---

# LaTeX Formula Extraction from PDF

## When to Use

- Extract mathematical formulas from academic papers
- Parse and clean LaTeX expressions
- Fix bracket/syntax display errors


## When to Use

## Environment Protocol and Deliverable Discipline

- If the host environment specifies an exact action/tool-call syntax, response wrapper, JSON schema, or completion string, follow it exactly on every step.
- Treat environment-interface compliance as blocking: invalid tool-call syntax or unofficial wrappers can prevent all extraction work from executing.
- Before the first tool call, identify any mandated action/tool schema, wrapper, or exact completion string; use that protocol verbatim for every tool call and for the final response.
- Before the first tool/action message, do a literal preflight: identify the exact required action wrapper/schema, whether only one action is allowed per turn, any exact completion string, and the runnable Python interpreter with `which python3 || which python`; make the first real command use the discovered executable name literally.
- If the host requires a specific tool name, `Thought:`/`Action:` wrapper, JSON shape, or other exact syntax, mirror that format literally from the first tool call onward; do not improvise alternate wrappers, pseudo-tool formats, or equivalent-looking schemas.
- Treat protocol mismatch as a blocking failure mode: extraction progress does not compensate for invalid action syntax or a missing exact completion line.
- In shell/tool fields, send only literal executable commands with real binaries/scripts and arguments; do not send placeholders or natural-language descriptions of intended actions.
- Never submit placeholder tool content or planning text such as `check processes`, `inspect tool location`, `Bash(...)`, or "run the converter"; every tool field must be a directly runnable command.
- If you cannot yet name the executable and arguments, do one capability-check command first, then issue the concrete command.
- Emit at most one tool/action request per assistant turn unless the environment explicitly permits batching; wait for the observation before the next action.
- Treat the observation boundary as mandatory: after one action, stop and wait. Do not include backup actions, chained separate tool requests, or a second tool call in the same assistant turn unless the host explicitly authorizes batching.
- Keep diagnostics bounded by the deliverable: after each probe, ask whether it directly helps produce or update `/root/latex_formula_extraction.md`; if not, pivot.
- Do not end on an intention statement such as "I will rerun" or "next I would investigate"; either execute the next step now or finish with the required completion protocol after writing the deliverable.
- End with the exact required completion signal when the environment explicitly requires one.
- Reserve any required completion token for the very end: after `/root/latex_formula_extraction.md` is written and verified, compare the token/string character-for-character and emit it exactly once as the last line, with nothing after it.

## Execution Priorities

- Produce the required artifact even if extraction is partial; do not spend the whole session debugging one tool.
- If you already have enough verified formula evidence to populate `/root/latex_formula_extraction.md`, switch immediately from investigation to file assembly/readback instead of continuing tool experiments.
- Treat process polling as a dead end unless it reveals a concrete new error or a new inspectable artifact; otherwise it does not count as progress toward completion.
- Time-box extraction attempts: if a tool fails, hangs, or produces no inspectable text/files after a small number of tries, pivot to another method.
- Stall threshold: after 2 failures from one extraction family (for example nonzero exit, timeout, empty output file, missing dependency, unreadable output, repeated silent termination, or repeated blank OCR/render results), abandon that family and execute the next confirmed-available method rather than monitoring or rerunning it again.
- Prefer direct, inspectable page-text extraction (for example pdfplumber or PyMuPDF) over opaque long-running conversion pipelines.
- If the environment already exposes direct PDF reads/search/chunked inspection, treat that as a primary extraction path after at most one failed converter attempt; do not keep retrying a broken conversion workflow when readable source access is already available.
- Do not center the workflow on full-PDF markdown conversion unless it very quickly yields inspectable formula-bearing text; conversion-to-markdown is only a means, not the task.
- As soon as any method yields usable page text, extract displayed formulas from that output and start writing `/root/latex_formula_extraction.md`.

- Treat `/root/latex_formula_extraction.md` as the primary deliverable from the start; judge progress by whether you are identifying verified formulas and updating that file, not by whether a preferred converter eventually works.
- Treat long-running or opaque full-document converters as low priority unless they quickly produce inspectable page text, page regions, or formula text.
- Validate a candidate method on 1-2 sample pages early; continue only if displayed equations remain clearly separable from prose and preserve enough structure for faithful transcription.
- Do not spend more than 1-2 failed or non-inspectable attempts on the same extractor, command family, pipeline, wrapper, or background-job variant. Timeouts, empty outputs, zero-byte files, unchanged no-output status, blank renders/OCR, or other non-inspectable results are failure evidence; pivot to a materially different method.
- Count timeout extension, foreground/background reruns, wrapper swaps, extra polling, and direct invocation of the same converter family as the same failing path unless they produce a new concrete diagnostic.
- After one foreground diagnostic rerun and at most one targeted follow-up status/output check, abandon the stalled path and switch extraction families.
- Once any method yields verified formula evidence, write `/root/latex_formula_extraction.md` immediately and keep updating it as coverage improves.
- Obey any task-specific or host-environment action/completion protocol exactly as stated when one is explicitly required.

- If the runtime already provides native file access to the PDF or its extracted text (for example a built-in reader, chunked reads, or search), use that as an early primary path before attempting external converters, installs, or custom pipelines.
- Treat confirmed working in-environment access as higher priority than speculative setup; do not defer extraction while exploring alternative converters if you can already inspect the document.
- Anti-stall rule: if several turns or repeated status checks have not produced readable page text, a visible page render/crop, OCR output, or an updated `/root/latex_formula_extraction.md`, stop setup/polling work and switch to the simplest executable extraction path.
- Once any single page yields a verified formula, immediately write that formula to `/root/latex_formula_extraction.md` and continue expanding coverage from there.

- Do not use generic whole-file reads on `/root/latex_paper.pdf` as if it were plain text; treat the PDF as binary and use PDF-aware extraction, rendering, OCR, or page-inspection methods instead.
- If a method has already produced enough verified formulas to write the required artifact, do that and finish; do not keep the task open waiting on a slower extractor unless it is clearly improving coverage.
- Before starting any heavyweight or stateful converter, define a concrete stop condition: what inspectable artifact must appear, how soon it should appear on a sample page, and which materially different fallback you will execute if it does not.
- Do not let planning a fallback count as progress. After deciding a fallback, run it in the very next action and inspect its output.



## Input

- `/root/latex_paper.pdf`: Research paper PDF

## Runtime Checks

- Before running any script, verify the executable exists (`which python3`, `which python`, tool binary path).

- If `python` is missing but `python3` exists, immediately rewrite the command to use `python3`; do not leave the correction implied.
- Make the correction explicit in the very next tool call. After observing `python: command not found`, the next command should literally invoke `python3 ...` (or the discovered interpreter path), not a vague statement that you will rerun or retry.
- Wrong: `python tool.py ...` after seeing `python: command not found`.
- Right: `python3 tool.py ...` (or the exact discovered interpreter path).
- Prefer `python3` when invoking Python scripts unless you have confirmed another interpreter exists.
- If a command fails, capture the full stderr/traceback before retrying; do not make decisions from `Exit code 1` alone.
- If the first failure output is truncated, rerun once in the simplest foreground form that exposes complete stderr/stdout or writes them to an inspectable log, then use that concrete error to choose the next step.
- Do not respond to a timeout, silent exit, or truncated traceback by only increasing timeout, backgrounding the same command, or switching to a near-identical wrapper. First run one controlled foreground reproduction that preserves full stderr/stdout and exit status.
- After that single evidence-gathering rerun, either make one targeted fix justified by the captured error or pivot to a materially different extraction family.

- Prefer one simple foreground diagnostic rerun that exposes full stderr/traceback or writes it to an immediately inspectable log before trying timeout changes, background execution, wrappers, or near-identical variants.
- When an error reveals an environment fact (missing executable, missing module, wrong path), make the very next command reflect that fact explicitly.
- If an expected log file, stderr stream, or output artifact is missing or incomplete, inspect that exact artifact directly before changing strategy; do not treat an empty directory listing or generic nonzero exit as a diagnosis.
- Before retrying a failed converter, script, or command family, state the specific failure hypothesis you are testing. If nothing material changed, do not rerun that path.
- If a background job exits silently, produces empty logs, or leaves no output artifact, rerun the exact command once in the foreground to capture stderr/stdout before doing more indirect diagnostics.
- Do not spend more than a small bounded diagnostic budget on one failing tool path: after 1 foreground reproduction and at most 1 additional targeted check, either pivot to a materially different extraction method or proceed with partial evidence-backed extraction.
- Do not spend multiple turns on `ps`/`pgrep`, file-size checks, help text, or version output unless those checks directly explain a failure and unlock the next extraction step.

- At the start, do a brief capability survey: confirm available PDF tools, Python interpreter, and whether needed modules/binaries are already usable before designing the pipeline.
- Capability survey order: (1) resolve the Python interpreter you will actually use, (2) check candidate PDF binaries with `which`/`command -v`, (3) test candidate Python imports with that same interpreter, then (4) choose the first confirmed-available path.
- Do not write a helper script or name a fallback tool as the next plan until its executable/import has already been confirmed in this runtime.

- Make the capability survey explicit before choosing a path: check candidate binaries with `which`/`command -v` and candidate Python libraries with a tiny import test using the interpreter you will actually run.
- Do not write a helper script that depends on a library until that import test has succeeded.
- When invoking a Python-based tool, resolve the interpreter first (`which python3 || which python`) and use the one that actually exists; do not assume `python` is available.
- Before choosing an extraction path, verify the specific command/library you plan to use is actually available; for Python-based fallbacks, test imports explicitly before writing a larger script.
- Before adopting a tool as the main path, run a minimal viability test on a sample page or small slice that produces inspectable output.

- Treat toolchain validation as end-to-end, not binary-exists-only: confirm the executable, required interpreter/modules, and that a tiny smoke test can actually produce inspectable output.
- If you discover an installed fallback extractor and its help/usage is readable, immediately run the simplest command that emits inspectable page text or writes an inspectable text file; do not abandon that proven path for a new unverified library/tool.
- Treat a discovered, documented fallback extractor as the default next step: after `which` or `--help` succeeds, execute one minimal real extraction command immediately and inspect its stdout or output file before considering any new script or library path.
- Do not switch away from that confirmed fallback to another speculative tool unless the fallback itself has now produced unusable or non-inspectable output.
- After any extraction command, verify actual text output or a non-empty output file before proceeding. Warnings, empty logs, empty directories, or process status alone do not count as successful extraction.
- Before investing more time in a tool, confirm where its output should appear and what inspectable artifact it should produce.
- If a command fails or exits nonzero, make at most one diagnostic rerun that preserves stderr/traceback or logs; if that still does not yield actionable evidence, pivot to another method.
- If a whole-file read fails due to size limits or produces no inspectable content, switch immediately to page-by-page, chunked, search-based, or region-level extraction instead of repeating the same full read.
- Treat empty `Read(...)`, blank renders, failed crops, wrong-region captures, blank OCR, truncated page text, or missing output files as extraction failure, not as inspection.

- Complete the capability survey before committing to a workflow: verify the actual Python executable name, available PDF utilities, and importability of any Python libraries you plan to use.
- If dependency installation, virtualenv creation, or common PDF binaries are unavailable, treat that as a planning constraint immediately; stop environment bootstrapping and continue with only confirmed-available tools.
- Identify the file type before choosing tools: for a `.pdf`, do not call generic whole-file `Read(...)`/cat-style inspection on the source document except for metadata checks; inspect text/images produced by PDF-aware tools instead.
- If you must inspect content manually, inspect page-level or region-level outputs from a PDF extractor or renderer, not the raw PDF byte stream.
- When using a PDF library or CLI you have not already confirmed, inspect its actual installed interface first (`python3 -c "import pkg; print(pkg)"`, `dir(...)`, `help(...)`, `tool --help`) before writing larger scripts around guessed method names.
- After one missing-method, constructor, or import mismatch on a PDF library, stop guessing APIs. Do one quick introspection check (`dir`, `help`, minimal sample call) and then either use the confirmed interface or pivot to another already-available tool.
- Do not spend multiple iterations trying renamed constructors or text methods on the same package without inspecting the installed API first.
- After one API mismatch or import failure, do a quick introspection check or switch tools; do not spend multiple iterations guessing constructor or extraction method names.
- If you write a helper script that is material to extraction, immediately read the file back or print it to confirm the saved contents are actual executable code implementing the intended logic.
- Minimum script validation rule: after creating a helper script, inspect its saved contents and run a tiny smoke test or syntax/import check before using its results as evidence.
- Do not describe a script generically and then rely on it; verify the literal file contents or execution behavior first.
- Before trusting a new script on the full PDF, run a minimal smoke test on a small sample page or input and inspect the output; if the file contents or behavior are not verified, do not rely on it.
- For a converter that may run for a while, the smoke test must be end-to-end: on a tiny scope or sample page, confirm it actually finishes and produces readable text, visible regions, or another inspectable artifact before adopting it as the main workflow.
- If that smoke test does not complete or produce inspectable output within the bounded trial, abandon that converter family instead of escalating to longer waits, more polling, or duplicate runs.



## Extraction Steps

1. Review the PDF page by page and identify every standalone display formula candidate, including unnumbered and multi-line formulas.
1a. Keep an explicit page inventory while scanning: for each page, record whether it has zero or more standalone display formulas and whether the page evidence was readable. Do not infer completeness from grep, equation numbering, regex hits, or a single flattened text dump.

1aa. Do not claim complete extraction from a sample page, truncated preview, or initial chunk alone. For a completeness claim, the workflow must show a full document coverage pass or an explicit page-by-page accounting.
1ab. If a built-in reader/search tool can already access the PDF contents, use page-sized or chunked reads plus targeted search to drive that inventory before attempting external conversion.
1ac. When chunked native reading works, keep using it systematically across the document instead of returning to converter experimentation; use search hits only as navigation aids, then read enough surrounding content to verify the full displayed formula and record its page/source evidence.
1b. For each retained formula, record a stable source reference from the current run: page number plus the text extraction, OCR result, or crop/region that actually showed it.
1c. If a page read, crop, render, or OCR result is empty, wrong-region, unreadable, or truncated, treat that as insufficient evidence and switch methods rather than transcribing from memory, context, or prior guesses.
1d. If an image file exists but reading or inspection returns empty, blank, non-informative, or non-readable content, treat that exactly like a failed extraction path; do not claim you "inspected," "saw," "read," or "verified" formulas from that image.
1e. Do not treat successful file creation, page rendering, image export, or crop generation as evidence by itself; evidence requires readable formula content from the actual tool output or direct inspectable page/region content.
1f. If an image read, render/crop inspection, or preview returns blank content, only metadata, or no readable symbols, you have not visually verified the formula. Do not say you can "see," "read," or "confirm" it from that image; switch to OCR, another crop/render path, page-text extraction, or a different extractor.
1g. Before saying a formula was identified, found, or verified, ensure the current run contains the exact supporting observation that exposed it. If no tool output in the session actually shows the formula text, omit that formula and continue with another extraction path.

2. Extract each formula as raw LaTeX in `$$ ... $$`.

2a. Never use placeholder formulas such as `$$...$$`, `TODO`, dummy text, guessed stand-ins, or scaffold lines. Every saved formula line must contain an evidence-backed transcription of an actually observed displayed formula.
2b. If a formula cannot yet be reconstructed faithfully, leave it out until you obtain better evidence; partial progress is acceptable, placeholder output is not.
2c. Do not create `/root/latex_formula_extraction.md` with scaffold content such as `$$...$$`, empty blocks, or provisional stand-ins just to satisfy the artifact requirement. Wait until you have at least one evidence-backed formula, then write only real verified `$$...$$` lines.
2d. Before any write to `/root/latex_formula_extraction.md`, inspect the exact payload you are about to save and confirm every line contains a concrete evidence-backed formula, not placeholders, filler, ellipses, or guessed stand-ins.
3. Preserve the exact displayed content from the PDF only when symbols and structure are clearly supported by readable extraction output or direct page inspection.
3a. Apply an evidence gate before keeping any formula: only write it if a specific page/region shows the full displayed expression in readable text extraction, OCR, or direct visual inspection.
3a.i. Before scaling automation or writing helper scripts around an extractor, verify on 1-2 sample pages that equation boundaries and symbols are preserved well enough to separate display math from surrounding prose. If sample output merges prose with equations, drops equations, or corrupts layout, treat that extractor as unfit for direct transcription and pivot.

3aa. If an image/file read shows only metadata, blank content, or no readable symbols, treat that as no visual evidence. Do not say you can "see," "read," or "verify" the formula from that observation; switch to OCR, a different render/crop, or another extraction path.
3b. Do not identify formulas by symbol density, line length, centering, equation-number regexes, or similar heuristics unless a human-verifiable page view already confirmed those lines are actual display equations.
3c. If extraction is partial, fragmented, page-misaligned, truncated, merged with prose, drops superscripts/subscripts/operators, shows Unicode fragments/OCR noise, reorders symbols, breaks fractions, or is otherwise ambiguous, treat it only as a lead for where to inspect next; re-extract, switch methods, or omit the formula rather than reconstructing missing math from context.
3d. Do not write a formula to `/root/latex_formula_extraction.md` unless the session has a concrete supporting observation for it: readable page text, OCR output, or visible page/region content that exposes that formula.
3e. If all attempted source-inspection paths are empty, unreadable, truncated, wrong-region, or mixed with metadata/prose in a way that obscures the formula, do not claim the formula was identified or verified; switch methods or omit it.
3f. If any earlier step showed truncation, encoding artifacts, cut-off formulas, missing operators, or other reliability warnings, do NOT promote a later reconstructed or "cleaned" formula into the final file unless you directly re-check that exact formula against readable page text, OCR, or visible page/region evidence.
3g. Treat post-processed outputs (for example "corrected", "rendered", or reformatted formulas produced by your own scripts/tools) as unverified drafts unless the underlying source formula was independently observed from the PDF evidence in the current run.
3h. If earlier steps showed truncation, encoding artifacts, cut-off equations, or other noisy extraction signals for a formula, do not save a later reconstructed, syntax-checked, or corrected version until you re-check that exact full formula against a direct source observation from the PDF in the current run.

4. Remove equation tags, commas, and periods at the end of formulas only when they are not part of the math content.
5. Check each extracted formula for syntax/display issues only after the displayed formula has been reliably identified from the PDF.
6. Append corrected versions only for formulas with clear syntax/display problems.
6a. Before concluding that no fixes are needed, run an explicit formula-by-formula validation pass for delimiter balance and obvious LaTeX display syntax problems; bracket counting or successful rendering alone does not prove fidelity or completeness.
6aa. Treat syntax/render validation as a secondary negative check only: balanced braces, successful parsing, or plausible LaTeX never justify choosing a disputed symbol, subscript, left-hand side, or bound.
6ab. If OCR/text extraction is noisy and two plausible readings exist, do not pick the more conventional-looking reconstruction. Re-inspect the source page/region or omit that formula until one reading is directly supported.

6b. Before writing or overwriting `/root/latex_formula_extraction.md`, require a final evidence check for every formula: the full expression must be directly supported by a readable page/region observation from the current run.
6c. Do NOT complete a truncated, fragmented, or OCR-corrupted formula from neighboring prose, prior knowledge, equation numbering, or a later guess; re-extract it or omit it.
6d. Do not replace source math with a conventionally "fixed" version based on assumption. If a delimiter, operator, or symbol looks wrong but is not clearly readable in the source evidence, preserve only what is directly supported or omit the formula rather than normalizing it from domain expectations.
7. If output is blank, truncated, garbled, fragmented, or mixes prose into equations, switch methods instead of inferring missing math.
7x. If repeated candidate "formulas" contain author names, metadata, full prose sentences, or other clearly non-equation text, stop tuning regexes/heuristics on that output. Treat the underlying representation as untrustworthy and move to a different extraction family or direct page/region inspection.
7a. If a tool fails twice for the same structural reason (for example timeout, missing dependency, unreadable output, flattened math, or no inspectable files), stop retrying it and pivot to a materially different method.

7aa. Materially different means a different extraction family, not the same converter rerun in background/foreground, with longer timeout, extra polling, minor flag changes, or a near-identical wrapper.
7ab. Treat repeated zero-byte outputs, repeated timeouts, background jobs that keep running without producing inspectable artifacts, repeated non-readable conversions, or help-only/probe-only runs without extracted text as decisive failure evidence; once those signals accumulate, switch tool families entirely.
7ac. When a fallback tool is confirmed present, prefer executing that direct extractor next over introducing another untested script or dependency path.
7b. Do not keep rerunning near-identical converter or command variants, adding long wait loops, or primarily polling `ps`/`pgrep`/output directories once a method has not produced usable text quickly.
7b.i. After one diagnostic rerun confirms the same stall/no-output condition, stop monitoring that pipeline; repeated status checks without new inspectable artifacts do not count as progress.
7b.ii. Replace vague intentions with explicit fallback actions: run a different extractor, inspect a specific page with another library, render a page image, or write verified formulas already recovered.

7c. Prefer direct page-level extraction, page rendering plus visual inspection, OCR, or manual transcription from verified page regions over continued process management.
7d. If delegation is used, require the subtask to try a materially different extraction path rather than retrying the same failing workflow.

7e. Maintain at most one active stateful conversion job per input/output target. Before any restart, confirm the prior run has finished or been intentionally terminated; do not launch overlapping runs of the same converter against the same files.
7f. When an alternate path already yields readable page text or visible formula regions, promote that path to the main workflow immediately instead of waiting for the original pipeline to finish.
8. As soon as you have a workable draft, write `/root/latex_formula_extraction.md`, then verify the file exists and that each formula is in its own `$$...$$` block.
9. After writing, reopen and read back the saved file contents in manageable chunks if needed; confirm the contents match the intended formulas, the last formula closes with `$$`, and no line is cut off.
9a. Make the final artifact auditable: ensure the actual `$$...$$` lines written to `/root/latex_formula_extraction.md` are visible in the workflow, either by printing the constructed content before writing or by reading back the saved file contents fully enough to expose every formula line.
9b. Do not rely on opaque statements like "formatted formula lines" or on uninspected writes as evidence that the correct formulas were saved.

10. If extraction is incomplete but evidence-backed, still write the verified formulas you have now rather than delaying file creation while debugging one failing toolchain.
11. Do not declare completion until all pages have been inspected or explicitly ruled out and every page containing standalone formulas has been accounted for.

11a. Do NOT say or imply "all formulas found," "complete extraction," or equivalent unless your actions established whole-document coverage by page-by-page inspection, source-wide search with follow-up inspection, or another observable full-source review.
11b. If coverage is incomplete, state that the output is partial and limited to the formulas directly verified from the inspected pages/regions.
11c. Do not upgrade a partial recovery into a completeness claim just because numbered-equation searches, syntax checks, or reconstructed drafts seem to account for the likely formulas. Completeness requires observable whole-document coverage evidence plus direct support for each retained formula.
11d. If any page remains unreadable, uninspected, or only fragmentarily extracted, do not say or imply that all formulas were found; deliver the verified subset and label it partial.

## Evidence and Verification

- Extract formulas only from content you actually observed in readable PDF text extraction, OCR output, or page render/crop inspection.
- Do NOT claim a formula was seen or verified if the tool output was empty, unreadable, truncated, or from the wrong page region.

- Do NOT claim to have visually inspected a rendered page or image unless the corresponding image/file read actually returned usable visible content in the tool output.
- Empty image reads, blank previews, failed crops, blank OCR, or missing rendered content mean the visual-inspection attempt failed; switch methods or regenerate inspectable output before making any source-grounded claim.
- Keep a one-to-one mapping between each final formula and a specific observed page/region.
- Before finalizing, ensure the session visibly contains the supporting observation for every saved formula line (for example extracted text, OCR text, or a successful readable page/region inspection). If the observation is not present in the session output, omit that formula.

- Before writing any formula to `/root/latex_formula_extraction.md`, confirm the session contains an explicit supporting observation for that exact formula text: readable extracted text, OCR output, or a successful page/region inspection result.
- If you cannot point to that supporting observation in the current session, omit the formula; do not fill gaps from expectation, context, or prior knowledge.
- Do NOT invent missing symbols, operators, indices, bounds, fractions, delimiters, or whole formulas from context or standard notation.
- When noisy OCR exposes nearby tokens but does not clearly bind them into one formula term, do not merge them into a polished LaTeX expression. In particular, do not upgrade surrounding index/context text into a definite left-hand side or subscript unless the page evidence clearly shows that structure.
- If a later inspection changes your interpretation of any symbol or index, treat the formula as unverified until you re-check the full expression against readable source evidence; do not keep claiming it is already confirmed because the LaTeX is syntactically valid.

- Do NOT promote fragmented extraction into a polished final formula. If the visible evidence is split, truncated, clipped, OCR-corrupted, or ambiguous, treat it as incomplete and keep searching for a fuller observation or omit that formula.
- For complex formulas, keep an auditable observation trail before finalizing: page number plus the specific successful text/region/view that exposed the complete expression.
- If any symbol or structure is unclear, re-extract or inspect the page again; if evidence remains insufficient, leave the formula out rather than guessing.

- For each final formula, be able to point to a specific successful observation: readable extracted text, OCR output, or visible page/region content from a tool result.
- Empty image reads, blank OCR, failed renders/crops, wrong-region captures, truncated previews, broken line fragments, encoding artifacts, mixed prose/math output, or partial front-matter text do not support exact formula transcription.
- Do NOT claim to "see," "read," "verify," or "confirm" a formula unless the corresponding extraction or page/region inspection actually exposed readable content.
- Do NOT reconstruct or promote partial snippets into complete formulas from sparse prose, OCR fragments, flattened layout text, domain knowledge, or expected paper structure.
- Do NOT add or rewrite mathematical structure unless that exact structure is visibly supported by the PDF.
- Numbered-equation search, regex hits, symbol searches, and short-line heuristics are triage only; they do not replace direct review for unnumbered, multi-line, split, or layout-sensitive display formulas.
- Do NOT add a "fixed" version unless the underlying source formula was itself observed and the syntax/display problem is directly evidenced in that observed content.
- Syntax checks, balanced delimiters, and successful rendering are secondary only; they validate form, not faithfulness to the PDF.
- Separate source verification from file verification: source verification means comparing each formula against PDF-derived evidence in the current run; file verification means rereading `/root/latex_formula_extraction.md` to confirm persistence and formatting.
- Do not conclude that formulas match the PDF, that none were missed, or that extraction is complete from syntax-check success alone. Make those claims only after source-grounded page/region verification and document-coverage review.

- Do NOT promote an ambiguous OCR/text fragment into a complete formula just because it can be normalized into plausible LaTeX.
- Treat syntax validation, delimiter balance, and successful rendering as a negative check only: they can catch malformed LaTeX, but they never justify changing symbols, indices, left-hand sides, operators, or bounds that were not clearly observed in the PDF.
- Do NOT claim "all formulas found" unless you completed a page-by-page coverage pass across the whole PDF and checked each page for zero-or-more display formulas.

- A sample extraction, first-page preview, or partial text dump is evidence only for those inspected pages/regions; it does not justify whole-document completion claims.
- Do NOT state or imply completeness unless your run artifacts support it: a page inventory exists for the whole PDF, each page is marked reviewed or explicitly ruled out, and each retained formula has direct evidence from a specific page/region.

- Treat any truncated extraction, clipped preview, partial OCR, shortened syntax-check output, or formula tail cut off in logs as unresolved evidence. Do NOT mark that formula verified, complete, matched, or syntax-checked until you obtain a full readable observation of the entire expression.
- Do NOT write a complete-looking formula to `/root/latex_formula_extraction.md` if any part of it was reconstructed from context, notation expectations, nearby prose, or partial checker output. Recover the missing source text with another page/region extraction method or omit that formula.
- If one formula remains partial while others are verified, keep only the fully supported formulas and explicitly treat the partial one as excluded rather than silently completing it.

- Treat truncated extraction output and truncated syntax-check output the same way: they are incomplete evidence. Do not mark the formula verified, complete, matched to the PDF, or syntax-checked until the full expression has been observed end-to-end.
- If any formula remains partial at the end of a pass, either recover the missing source text with another page/region extraction method or omit that formula from `/root/latex_formula_extraction.md`; do not write a complete-looking reconstruction from inference.


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
When writing `/root/latex_formula_extraction.md`, the file content must be the actual formula lines themselves. Do NOT write placeholders, dummy `$$...$$` blocks, summaries, prose notes, ellipses standing in for unresolved content, or descriptions such as "wrote the extracted formulas".
Treat the write payload as literal deliverable content: before executing the write, check that the body already contains the full `$$...$$` formula lines and not a description of them.
If you accidentally wrote descriptive or placeholder text, overwrite the file immediately with the actual formulas, then reread the saved file before continuing.
If the file would otherwise contain only placeholders or unresolved stand-ins, do not write that draft as the final artifact; continue extracting or save only the smaller set of formulas that are fully evidenced.

Before finishing, verify the file exists, is non-empty, and contains only the extracted display formulas in the required `$$...$$` format.

After any write or rewrite, read back the entire saved file (in chunks if needed), checking every line for truncation, unmatched delimiters, unfinished `$$...$$` blocks, and mismatches with the verified source evidence.
Make the actual formula payload auditable: either print/show the exact `$$...$$` lines before writing or immediately read back the saved file in full so the concrete written formulas are visible in the workflow.
If any readback shows placeholder text, prose such as "wrote the extracted formulas", truncated lines, or a mismatch with the intended formulas, treat the write as failed: rewrite `/root/latex_formula_extraction.md` with the literal formula lines and reread the full file before finishing.
If you rewrite `/root/latex_formula_extraction.md` late in the workflow, do not finalize from a partial preview. Re-read the full saved file after that last rewrite, covering every formula line through end of file, before emitting the completion signal.
Verification must inspect the actual `/root/latex_formula_extraction.md` contents on disk and confirm the saved formulas are the ones you intend to submit; reading the saved file verifies persistence only, not fidelity to the PDF.

Treat the readback literally: check for placeholders, stray markers, extra lines, numbering prefixes, shell artifacts, truncated fragments, or unrelated trailing text. If any unexpected text appears, rewrite the file and reread it before finishing.
Do not describe formulas in the final response that are not literally present in `/root/latex_formula_extraction.md` when you reread it.

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

- After any rewrite or late edit, reread the entire saved `/root/latex_formula_extraction.md` in full or in consecutive chunks that cover the whole file; do not rely on a truncated preview or partial snippet.
- Do not finalize while any readback is empty, clipped, or incomplete; repeat the read in smaller chunks until the full final file has been verified on disk.
- If the environment specifies an exact completion string, emit it exactly as the last line after all file checks pass.
- Before the final response, do a two-part completion gate: (1) confirm artifact checks passed and whole-document coverage was actually established before using words like "complete," "all formulas found," or "matches the PDF"; otherwise use partial-language only, and (2) confirm the final response uses the exact required completion wrapper/token with no extra natural-language substitute.
- Once the file contains all currently verified formulas, stop investigating and finalize: do the required readback check, then emit the exact completion string immediately rather than continuing optional extraction experiments.
- Do not stop on an intention such as "next I will verify" or "I will rerun". Either execute that step now or, if the artifact and checks are complete, emit the exact required completion signal immediately.

- Before finalizing, check that every formula in `/root/latex_formula_extraction.md` has a traceable evidence chain in the session: source PDF page/region -> successful readable extraction/inspection -> final `$$...$$` line.
- Confirm no line in the file is a placeholder such as `$$...$$`, empty math delimiters, `TODO`, or other non-formula filler.
- Confirm any claimed verification includes a successful check against PDF source evidence, not only rereading the generated markdown file.
- Re-read the original task/system instructions immediately before the last response and confirm both parts are satisfied: the artifact exists at `/root/latex_formula_extraction.md` and any required action/completion protocol is obeyed exactly.
- Treat file writes as high-risk: ensure the write payload is the exact final formula text, then read the saved file back to confirm it does not contain placeholder, descriptive, truncated, or otherwise unverified content.
- Before claiming "verified," "complete," or "matches the PDF," check that every such formula has full-page/full-region evidence and that no extraction, OCR, or syntax-check output for it was truncated.
- If the host environment requires an exact action format or exact completion string, verify your final response matches it literally before finishing and emit that exact required string as the last line.
- Do not finish the session with only conversion attempts, process checks, or fallback plans; execute the fallback and save any verified formulas, even if coverage is partial.


## Completion Checklist

- Write the final formulas to exactly `/root/latex_formula_extraction.md`.
- If extraction is partial, save the formulas you could verify rather than ending without the file.
- Confirm the file exists, is non-empty, and contains extracted display formulas in `$$...$$` format.
- After making corrections, re-open the file to confirm the saved contents match the intended final formulas.

## Execution Workflow

7. Before writing helper scripts, confirm the approach is viable in this runtime and preserves formula fidelity on a small sample.
8. Treat any new extraction tool as untrusted until it produces inspectable output on disk or in stdout/stderr; verify that first.
8a. If you just confirmed a tool exists via `which` or `--help`, the next step should usually be a real extraction command on the PDF or a sample page, followed by inspection of its output.
8b. Do not spend additional turns on process checks, wrapper variants, or alternate scripts when a documented installed extractor is already available and not yet actually tried.

9. Do not keep polling, rerunning, or extending timeouts on the same failing conversion pipeline once you have two clear failures or no inspectable output.
10. For opaque converters or background jobs, allow at most one diagnostic foreground rerun to capture stderr or a traceback before abandoning that path.
11. After each major step, ask whether it produced readable formula evidence or updated `/root/latex_formula_extraction.md`; if not, change approach.
11c. If the current path is only improving an intermediate artifact (for example markdown conversion output) without exposing verified formulas or updating `/root/latex_formula_extraction.md`, demote that path and switch to a more direct extractor.

11a. If two consecutive diagnostic actions still do not reveal a concrete error or produce readable formula evidence, stop investigating that path and switch to a different extraction method.
11b. Prefer the next action that can create or append to `/root/latex_formula_extraction.md` over additional peripheral diagnostics.
12. Keep a simple coverage log: page number, whether it contains standalone display math, and which extraction/viewing method verified each retained formula.
13. Once any verified formulas are available, start writing `/root/latex_formula_extraction.md` immediately and continue filling it as you inspect remaining pages.
14. When output is clipped by the shell or tool display, save the extraction to a file or inspect smaller page/region chunks; do not treat clipped console text as complete evidence.
15. If multiple tools fail or only part of the paper is recoverable, still save every directly verified formula, verify the file on disk, and continue expanding coverage only if time permits.

16. Before locking in a plan, run a minimal end-to-end viability probe with the exact toolchain you intend to use: executable present, library import succeeds if needed, sample page access works, and output is inspectable.
17. If the environment exposes a working built-in file reader or search facility for the PDF, use it first for chunked/page-level inspection and formula discovery; only escalate if that path is demonstrably insufficient for readable formula evidence.
18. If you create a helper script intended to produce `/root/latex_formula_extraction.md`, execute it promptly unless a concrete runtime error blocks execution.
18a. Do not return to open-ended tool exploration after writing such a script until you have either run it once and inspected `/root/latex_formula_extraction.md` or observed a concrete execution error that forces a change of plan.
18b. Use the checkpoint: script saved -> script executed -> output file created/updated -> file read back. Treat anything short of that as incomplete progress, not completion.
19. Treat "script written" as incomplete progress; the checkpoint is: script run, `/root/latex_formula_extraction.md` created or updated, file read back, contents verified.
20. When you decide on a fallback or corrective plan, execute that next step immediately and validate its result; do not stop at describing the new plan.
21. If a backgrounded converter/job disappears quickly, has empty logs, or creates no inspectable output, immediately rerun the same command in the foreground once; use that result to decide whether to abandon the tool.
22. If smoke testing and environment checks leave no credible path for that converter family, abandon it early and move to a simpler inspectable method rather than managing retries.
23. Never start a second run of the same converter on the same document/output location just to see if it behaves differently; inspect or terminate the first run before deciding the next step.
24. If no new artifact has appeared after a brief wait, do one diagnostic check at most, then pivot; do not spend the session monitoring a stuck job.
25. Anti-stall fallback sequence: (a) run one simple inspectable extractor on a sample page, (b) if it yields readable formula evidence, start or update `/root/latex_formula_extraction.md` immediately, (c) if it fails twice or produces no inspectable output, switch to a materially different extraction family rather than more diagnostics.
26. If a long-running converter still has not produced an inspectable artifact after the predeclared stop point, terminate or abandon it and immediately execute the fallback extraction path; do not end the turn with more monitoring.
27. Never start a second instance of the same converter for the same PDF or output target while the first is still active or unresolved; first inspect artifacts, then either keep exactly one run or pivot away from that tool family entirely.
28. Prefer the next action that can expose page text or a visible formula region over any action that only reports process state, tool metadata, or converter status.
29. If coverage is still limited, write the verified formulas already recovered to `/root/latex_formula_extraction.md` before any further experimentation.


## Execution Workflow

1. Start with a lightweight, inspectable method first (for example, pdfplumber or PyMuPDF).
2. Validate on 1-2 sample pages before scaling up: confirm displayed formulas are readable and not corrupted prose, Unicode fragments, or flattened layout.
3. If direct/full-file reading hits size limits, switch to page-by-page, chunked, or region-level extraction instead of retrying the same full read.
4. If a tool produces empty output, stalls, times out, or gives unusable formula text after 1-2 attempts, stop retrying it and switch to a materially different method.
5. If text extraction loses equation structure, use page rendering, OCR, or manual page-level transcription from verified PDF evidence rather than adding more heuristics.
6. Track which pages have been inspected so completeness claims are evidence-based.
