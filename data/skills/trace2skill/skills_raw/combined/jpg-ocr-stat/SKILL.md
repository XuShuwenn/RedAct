---
name: jpg-ocr-stat
description: "Extract date and total amount from receipt JPG images using OCR, and write results to Excel file."
---

# Receipt OCR and Statistics

## When to Use

- Extract text from receipt images using OCR
- Parse dates and monetary amounts from scanned receipts
- Write structured data to Excel files

- Use actual OCR output as the evidence source; do not infer receipt contents from empty image/file reads.
- Follow any task-specific tool-call, action, or completion protocol exactly if the task/environment prescribes one.
- If the environment or task specifies an exact interaction schema, tool-call wrapper, action format, or completion token, treat it as mandatory and higher priority than this skill's generic workflow.
- Before the first tool call, match the required schema exactly and use it consistently for every invocation; do not substitute alternate wrappers, ad-hoc formats, summaries, or termination phrases.
- If an exact completion token/string is required, reserve it for the very last response and emit it verbatim with no extra prose unless explicitly allowed.

## Input

- `/app/workspace/dataset/img/`: Directory of receipt JPG images

- Do not use plain text/file readers on `.jpg` receipts as evidence. If a JPG read returns empty, binary, or non-visual output, treat that as no evidence and switch to OCR or image preprocessing that produces observable text.

## Output

Excel file `/app/workspace/stat_ocr.xlsx`:
- Sheet name: "results"
- Columns: filename, date (YYYY-MM-DD), total_amount (2 decimal places)
- 1-based page indexing

- Write only the required sheet and columns; do not add styling, bold headers, adjusted widths, extra sheets, or other presentation changes unless explicitly requested.

- Keep the workbook plain: write only the required sheet and cell values. Do not apply bold headers, column widths, styling, formulas, filters, or other presentation changes unless explicitly requested.

## Execution

- Run scripts with `python3`, not `python`, unless you have explicitly confirmed `python` exists.

- Default to `python3` for scripts and one-liners; use `python` only after explicitly confirming it exists.
- For Excel output, prefer `openpyxl` directly. Do not use `pandas` unless you have first confirmed it imports successfully in this environment.
- Decide and sanity-check the workbook-writing path early so the task cannot fail at the final export step.
- Do not treat a launched command as success. Require observable completion evidence such as an exit status, a final summary/count, or a direct readback of the produced artifact.

## Validation Workflow

- After generating `stat_ocr.xlsx`, inspect the full `results` sheet for all rows; do not rely on truncated console previews.
- Verify the workbook contents programmatically: expected row count, sheet name, headers, and that every input JPG produced exactly one output row.
- Confirm the header row is exactly: `filename`, `date`, `total_amount`.
- Confirm `date` values are ISO `YYYY-MM-DD` or blank/null when extraction failed.
- Confirm `total_amount` values are numeric and formatted to 2 decimal places.
- If command output is truncated or stops mid-run, treat the run as unverified and rerun or inspect the workbook directly before concluding.
- If a candidate date or amount is weakly supported by OCR context, leave it null rather than guessing.

- Treat the extraction as incomplete unless the full dataset run clearly finishes and `/app/workspace/stat_ocr.xlsx` is successfully written; do not infer success from partial per-file logs, workbook existence alone, or truncated stdout.
- Require positive completion evidence before trusting outputs: a clean process exit, an explicit final success/save message, or verified workbook side effects produced after the full dataset run.
- Ground verification in observable outputs only: OCR text, script output, parser logs, or workbook contents visible in the session. Do not create manual "expected vs got" tables from guessed receipt values or unsupported visual assumptions.
- Do not validate from `grep`, `head`, tuple dumps, or other truncated summaries alone. Read the workbook programmatically and iterate all rows in `results` to completion.
- Verify the complete dataset, not just structure: row count equals the number of input JPGs, every filename appears exactly once, ordering is deterministic, and every row's field values are checked or summarized without truncation.
- Treat empty, binary, or otherwise unusable tool output as no evidence. Every non-null field written to Excel must be traceable to observed OCR text or program output from the current run.
- If a workbook-inspection script crashes, stops early, or output truncates mid-row or omits trailing files, treat validation as failed; fix the inspection path and rerun until every row is confirmed.
- Treat validation as a decision gate: if you observe malformed dates, suspicious totals (especially `0.00`), missing rows, duplicate filenames, visible `None`/null outputs, unstable values across reruns, weak total matches, or obvious outliers, do not finalize; inspect OCR evidence or parsing logic, fix the issue, rerun, and re-check the workbook.
- When you change OCR preprocessing, regexes, scoring, fallback behavior, normalization rules, or exclusion keywords, test on captured OCR lines when relevant, then rerun the full dataset, compare against the previous full run, and reject or narrow the change if it introduces regressions.
- If any earlier run exposed specific bad files or malformed outputs, include those filenames in a targeted readback check after the next full rerun before concluding the fix worked.

## Date Extraction

- Parse date from receipt text
- Convert to ISO format (YYYY-MM-DD)
- If extraction fails, set to null

- Prefer explicit full-date evidence actually present in OCR text.
- Accept a date only when supported by a clear full-date pattern or date-labeled context in OCR text; reject isolated numeric fragments that could come from invoice numbers, receipt numbers, reference IDs, quantities, litre readings, or other non-date content.
- Do not broaden date logic to parse digits embedded inside longer identifiers just to reduce nulls unless surrounding OCR text clearly marks the field as a date or another structured fallback is explicitly supported by OCR evidence.
- Prefer date-labeled text or a clear standalone date pattern near transaction details.
- Reject isolated numeric matches that may come from invoice numbers, reference IDs, item lines, quantities, pump data, or OCR noise.
- Do not force an ambiguous numeric date interpretation without checking OCR text context.
- Validate parsed dates before writing: require a real ISO date with month `01-12` and a valid day for that month.
- Normalize lightly corrupted OCR date strings before final validation when the date evidence is otherwise clear (for example extra spaces, mixed separators, or a date embedded inside a longer supported field), but still require a valid final ISO date and supporting OCR context.
- Use tolerant parsing only to recover an OCR-supported date, not to invent one from weak numeric fragments.
- After checking explicit printed dates, allow a structured fallback from alternate encoded fields only when the OCR text clearly supports the pattern (for example, an invoice/reference number that embeds `YYYYMMDD`).
- Use structured date fallbacks only if they decode to a valid calendar date and are more reliable than the visible date text; otherwise write `null`.
- Apply the same date validation again during final workbook readback; if any written date is invalid, rewrite that value to `null` or fix extraction and regenerate the workbook before finishing.
- Do not write malformed dates like `2018-62-19`; if the parsed date is invalid or ambiguous, write `null`.
- Smoke-test date regex/pattern logic on 1-2 sample strings before running the full batch.
- Before the full batch, verify regexes compile and match simple known examples; if you changed parsing code, run a tiny script or REPL check first so malformed patterns fail early.
- When writing regex character classes for separators, place `-` at the start/end or escape it (for example `[./-]`); avoid invalid ranges such as `[/-.]`.
- If the OCR evidence is ambiguous or weak, set the date to null rather than guessing.
- If several receipts return null dates, inspect the raw OCR text for those files and broaden preprocessing/parsing rather than accepting the first pass.

## Total Amount Extraction

Keywords (priority order):
1. GRAND TOTAL
2. TOTAL RM, TOTAL: RM
3. TOTAL AMOUNT
4. TOTAL, AMOUNT, TOTAL DUE, etc.

Use candidate scoring, not just "last number on a matched line". Prefer lines with strong final-total phrases and penalize headers/summary labels such as `Description Amount`, `Sales`, `Qty`, `QTY ITEM TOTAL`, or non-final tax summaries.
Build the total decision in two phases: (1) collect candidate amounts from same-line or clearly adjacent total-related text, then (2) rank candidates by positive and negative context. Do not use a raw "keyword hit + last number" rule as the final selector.

When choosing between nearby totals, prefer the payable/final-total line over tax-inclusive sales summaries or table/header lines. Examples to penalize unless they clearly indicate the final payable amount: `Total Sales Incl GST`, `Description Amount`, `Amount`, `Sales`, item-table headers, and intermediate summary lines.

Enforce keyword priority strictly: if a higher-priority keyword is present, do not fall back to lower-priority groups for that receipt.
If implementing grouped scans in code, track whether any higher-priority group matched at all; once matched, either return an amount from that group or return `null` for unresolved total rather than continuing to lower-priority groups.

Accept an amount only when it is on the same line as, or immediately adjacent to, a total-related keyword. Treat next-line fallback after a keyword as high-risk; use it only when same-line extraction fails and the keyword line clearly indicates a payable final total, not a broad header/table label or metadata.
Before accepting a total candidate, check nearby OCR text for conflicting numeric contexts (for example litres, quantities, unit prices, item lines, reference numbers, or header/table labels). If the candidate is not clearly the payable final total, set it to `null` instead of forcing a match.

Treat exclusion terms as negative signals, not absolute blockers: do not discard a line just because it contains `GST`/`SST` if it also contains a high-priority total phrase like `TOTAL RM` or `GRAND TOTAL`.

Exclude or heavily penalize lines with: SUBTOTAL, DISCOUNT, CHANGE, CASH TENDERED, ROUNDING, tax-only summaries.

Treat generic words like `AMOUNT` or `TOTAL` alone as weak signals; prefer strong phrases such as `GRAND TOTAL`, `TOTAL RM`, `TOTAL AMOUNT`, or `TOTAL DUE`.

Prefer specific final-total phrases and stronger keyword matches over a larger numeric value elsewhere. Reject candidates near unrelated contexts such as litre/quantity/unit-price/item lines, even if the OCR text is noisy.

Do not invent decimals from ambiguous integers unless the receipt text gives strong explicit currency or decimal evidence. Prefer decimal amounts associated with total keywords; avoid plain integers unless the receipt clearly shows no cents.

Treat `0.00` as suspicious unless the OCR text explicitly shows a zero total; otherwise inspect the source line or fallback match and set to `null` if unresolved.

Do NOT let a later weak match override an earlier stronger total candidate just because it appears lower on the receipt.
Evaluate all OCR variants before choosing `total_amount`; do not stop at the first non-null match.

Use a ranked selection pattern:
1. collect total candidates from every OCR/preprocessing variant
2. normalize lightly corrupted amount strings only when strong nearby total context supports it (for example `85. 54` -> `85.54`, `538 00` -> `538.00`, `99,80` -> `99.80`, and standard comma-thousands cleanup)
3. score by keyword strength, same-line proximity, final-total context, and plausibility
4. prefer repeated non-zero candidates across variants over one-off weak matches
5. write `null` if candidates conflict and no clear winner remains

Do not lock in `0.00`, `null`, or another weak value from an early variant while later variants contain a stronger supported total.
- Use normalization only to recover a candidate already supported by a nearby total keyword; do not use it to invent a number from weak or unrelated text.

If multiple total candidates conflict and context does not clearly disambiguate them, set `total_amount` to null.

Handle comma separators (1,234.56).

- Before changing amount regexes or exclusion keywords, test them on a few captured OCR lines that include both true final totals and known non-total/header lines; keep the change only if it improves target cases without removing valid strong-keyword totals.
- Apply exclusions narrowly: a line containing `GST`/`SST` can still be the correct final total when paired with strong total phrases such as `TOTAL SALES`, `TOTAL RM`, `GRAND TOTAL`, or `TOTAL AMOUNT`.
- Do not normalize ambiguous integers into decimal currency amounts unless the OCR line itself clearly presents that exact value as the final payable amount with strong total context; otherwise prefer a decimal candidate or `null`.
- Before treating a line with `AMOUNT` or `TOTAL` as a trigger, check whether it is a table header or metadata label (for example `Description Amount`, `Amount TX`, column headings, SKU/code headers). If so, do not extract from that line or its next line.
- Use next-line fallback only when the keyword line contains a strong payable-total phrase (`GRAND TOTAL`, `TOTAL RM`, `TOTAL AMOUNT`, `TOTAL DUE`) and is not a header/table label.
- Do not let broad generic keywords such as `AMOUNT` alone activate extraction from adjacent product-code or item-description lines.
- Within the same keyword priority, do not prefer a later line solely because it is lower on the receipt; keep the candidate with stronger total context and leave the value null if competing matches are not clearly resolved.


## Extraction Reliability

- If a file read, direct `.jpg` binary read, image preview, inspection call, or OCR attempt returns empty or otherwise unusable output, treat that as no evidence. Switch to another valid method; do not claim specific receipt contents from the empty result.
- When raw OCR misses fields, use a focused recovery loop for failed files: save or print OCR text, try preprocessing variants (grayscale, threshold, resize, sharpen/denoise, crop, alternate `--psm`), then rerun parsing.
- If alternate OCR variants disagree, build a candidate set per field and rank it instead of using first-valid-match selection.
- For dates, prefer candidates supported by clearer full-date text, repeated across OCR variants, or attached to date-like labels; for totals, prefer candidates nearest strong final-total phrases and repeated across variants.
- When debugging a specific receipt, capture or quote the OCR text/lines and extracted candidates that support the chosen date and total; if no supporting OCR text is available, leave the field null rather than inferring the value.
- Treat many first-pass nulls or weak fields as a signal to iterate, not to finish. Inspect OCR text for representative failed files, adjust preprocessing/`--psm`/parsing, rerun the full dataset, and keep the change only if overall results improve.
- Accept `null` only after a deliberate recovery attempt or after confirming the OCR evidence remains unreadable or ambiguous.
- Start with a small OCR spot-check on a few varied receipts before trusting a batch-wide regex/keyword strategy.
- Treat anomalous outputs as mandatory review triggers, especially `total_amount = 0.00`, missing dates, malformed dates, truncated amounts, or obvious outliers.
- After any targeted refinement, rerun the full dataset and keep the change only if flagged cases improve without introducing broader regressions.

## Extraction Reliability

- Treat OCR text as the source of truth; only report a value if some OCR line supports it.
- Preprocess difficult receipts before OCR when results are weak: grayscale, contrast boost, thresholding, resize, sharpening/denoising, cropping, or different Tesseract `--psm` modes.
- If multiple OCR variants produce different dates or totals, arbitrate instead of using first-match selection:
  - prefer candidates repeated across variants
  - prefer totals closest to strong keywords like `GRAND TOTAL`, `TOTAL RM`, or `TOTAL AMOUNT`
  - prefer clearer full dates over noisier partial or ambiguous parses
- If conflict remains unresolved, continue improving OCR or preprocessing rather than silently choosing one unsupported value.
## Tips

- Use pytesseract for OCR
- PIL for image preprocessing
- openpyxl for Excel writing
- Handle multi-line keyword/amount fallbacks

- Prefer guaranteed/preinstalled libraries first. Use standard library + `openpyxl` for Excel output; do not assume `pandas` is available.
- If you are considering any non-guaranteed library, verify it is importable before relying on it; otherwise redesign around guaranteed/preinstalled tools.
- Do not attempt package installation unless the environment explicitly allows it.
- Prefer a single Python script that scans all JPGs, runs OCR, parses fields, and writes `/app/workspace/stat_ocr.xlsx` directly; do not manually rebuild the workbook from copied terminal output.
- If extracted records are printed to stdout and the output is long or truncated, save structured output to disk first, then build Excel from that complete file.
- Never manually reconstruct the final workbook from partially visible terminal/stdout output. Either write Excel in the same extraction script or persist the complete structured dataset to a file and build from that file.
- If a tool call returns empty or unusable output, switch methods and capture observable OCR text before claiming a date or total.
- Do not manually "correct" dates or totals unless the value is supported by explicit OCR text seen in the session.
- Prefer stable ranked rules over file-specific patches for individual receipts.
- When debugging specific images, use that only to improve the general parser, then rerun the full dataset and re-verify the final workbook.
- After writing the workbook, reopen it and validate the final contents programmatically instead of assuming the write succeeded.
- Spot-check anomalous outputs before finishing: `date = null`, malformed dates, zero totals, unusually large totals, or unusually many missing values.

- Keep the proven workflow: OCR the receipt text first, then run rule-based parsing for date and total extraction; avoid relying on OCR output alone without field-specific ranking and validation.
- Avoid ad hoc per-file guesswork driven by a few suspicious receipts. Improve general OCR/preprocessing/parsing rules from observed evidence, rerun the full dataset, and keep the change only if the final verified workbook improves.


## Execution and Recovery

- Make parser changes incrementally when possible; avoid broad rewrites unless necessary. After each non-trivial edit, rerun a focused check, then rerun the full pipeline before trusting the result.
- Treat empty image/file reads as no evidence, not partial understanding; do not claim you visually inspected a receipt unless the session produced usable image or OCR output.
- When debugging a specific file, capture the OCR lines that support the suspected date/total and use those observations to refine general rules.
- Use targeted debugging on a few receipts only to diagnose patterns; do not accept the fix until a full-batch rerun shows no unacceptable regressions.
- Preserve a previous full-run result snapshot before major heuristic changes so you can diff outputs and detect regressions across filenames.
- After any heuristic, parser, regex, OCR, preprocessing, fallback, normalization, or exclusion change, save a full before/after result set by filename, inspect changed rows for regressions, rerun the full dataset, regenerate `/app/workspace/stat_ocr.xlsx`, and re-verify the final workbook before finishing.
- If a rule change fixes one receipt but alters other previously acceptable rows without clear evidence of improvement, revert or refine the change before finalizing.
- If a write/export command or dependency path fails, immediately switch to a confirmed available path (typically direct `openpyxl` writing), produce `/app/workspace/stat_ocr.xlsx`, and verify that it exists.
- After the last code change, perform one fresh end-to-end run and one fresh workbook verification pass; do not rely on checks performed before the final edit.
- Do not end on an intended next edit, a pending rerun, or partial diagnosis; end only after a completed run, successful verification, production of the required artifact, and any exact required completion token or protocol.


## Final Verification

- Do not declare completion from truncated logs, partial workbook previews, structural checks alone, or partial spot checks; run a full-sheet readback or programmatic check that covers every output row.
- Use a full-sheet validation script for the final check: assert row count, filename set/order, headers, sheet name, and inspect every row's `date`/`total_amount` values rather than relying on console previews.
- Do not stop at workbook existence, sheet/header checks, or a small sample preview. Review all rows and specifically re-check suspicious outputs (`null` dates, malformed dates, `0.00`, blanks, truncated values, or obvious outliers) before finishing.
- Wait for the final rerun to finish completely and verify that `/app/workspace/stat_ocr.xlsx` was actually written by that last full run before doing narrower spot checks or declaring success.
- If command output is truncated, inspect the workbook directly or run narrower complete checks instead of assuming unseen files are correct.
- If any suspicious row remains unexplained after inspection, the task is not done; revise OCR/preprocessing or parsing rules, rerun the full dataset, and verify the corrected workbook again.
- If you discover an issue during final verification and edit the script again, restart the final verification checklist from the beginning.
- Before concluding, confirm the final workbook on disk is the artifact produced by the last full run, not an earlier partial/debug version.
- Only conclude after both conditions hold: the run completed end-to-end and the saved workbook passes row-count, sheet-name, header, filename-coverage, and one-row-per-input checks.
- Treat the final response format as part of verification: if the task or environment specifies an exact completion string or termination token, compare your planned final response against it and output that exact text only, with no added prose unless explicitly allowed.
- Do not announce success in natural language before the final accepted completion step.

## Final Verification

- After the last script or heuristic change, rerun the full extraction; do not stop after editing.
- Open `/app/workspace/stat_ocr.xlsx` and verify sheet name `results`.
- Verify the workbook contains exactly the required columns in order: `filename`, `date`, `total_amount`.
- Confirm every input filename appears exactly once, with one data row per JPG in `/app/workspace/dataset/img/`.
- Confirm rows are ordered consistently by filename.
- Check date values are `YYYY-MM-DD` or null when extraction fails.
- Check `total_amount` values are numeric with 2 decimal places and are not taken from excluded or heavily penalized lines such as SUBTOTAL, DISCOUNT, CHANGE, CASH TENDERED, ROUNDING, or tax-only summaries.
- Validate suspicious rows such as null dates, malformed dates, `0.00`, missing totals, truncated values, or obvious outliers.
- If command output is truncated, inspect the workbook directly or run narrower workbook-read checks instead of assuming unseen files are correct.
- If reruns or rule changes produce conflicting values for the same file, treat that as unresolved; investigate regressions, regenerate the workbook, and re-check all outputs.
- Do not finish immediately after launching the final run; wait for completion and inspect the final artifact.
- If the task or system instructions require an exact completion token or protocol, output it verbatim at the end.
## Execution and Recovery

- Run OCR on the actual image files; do not claim you "saw" receipt values unless they appear in OCR or program output.
- Base corrections on observed OCR output, not guessed receipt values.
- Do not hard-code per-file corrections unless the task explicitly provides a gold label source.
- After writing or overwriting any Python script, read it back once to confirm the file is complete and not truncated.
- After any targeted edit or replacement, run a syntax check before executing: `python3 -m py_compile <script>.py`.
- Run the full pipeline across all receipt images; do not stop after debugging only a few sample files.
- If an export/write attempt fails, use an available fallback immediately and actually produce `/app/workspace/stat_ocr.xlsx`.
- After changing OCR preprocessing, regexes, amount/date heuristics, or exclusion keywords, rerun extraction on the full dataset and compare results; keep the change only if it improves target cases without unacceptable regressions.
- Only consider the task complete after a successful end-to-end run with no syntax/runtime errors and a readable Excel artifact.