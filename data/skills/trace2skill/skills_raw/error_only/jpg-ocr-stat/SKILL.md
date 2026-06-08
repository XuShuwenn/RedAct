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

## Input

- `/app/workspace/dataset/img/`: Directory of receipt JPG images

## Output

Excel file `/app/workspace/stat_ocr.xlsx`:
- Sheet name: "results"
- Columns: filename, date (YYYY-MM-DD), total_amount (2 decimal places)
- 1-based page indexing

- Write only the required sheet and columns; do not add styling, bold headers, adjusted widths, extra sheets, or other presentation changes unless explicitly requested.

## Execution

- Run scripts with `python3`, not `python`, unless you have explicitly confirmed `python` exists.

## Validation Workflow

- After generating `stat_ocr.xlsx`, inspect the full `results` sheet for all rows; do not rely on truncated console previews.
- Verify the workbook contents programmatically: expected row count, sheet name, headers, and that every input JPG produced exactly one output row.
- Confirm the header row is exactly: `filename`, `date`, `total_amount`.
- Confirm `date` values are ISO `YYYY-MM-DD` or blank/null when extraction failed.
- Confirm `total_amount` values are numeric and formatted to 2 decimal places.
- If command output is truncated or stops mid-run, treat the run as unverified and rerun or inspect the workbook directly before concluding.
- If a candidate date or amount is weakly supported by OCR context, leave it null rather than guessing.

## Date Extraction

- Parse date from receipt text
- Convert to ISO format (YYYY-MM-DD)
- If extraction fails, set to null

- Prefer explicit full-date evidence actually present in OCR text.
- Prefer date-labeled text or a clear standalone date pattern near transaction details.
- Reject isolated numeric matches that may come from invoice numbers, reference IDs, item lines, quantities, pump data, or OCR noise.
- Do not force an ambiguous numeric date interpretation without checking OCR text context.
- Validate parsed dates before writing: require a real ISO date with month `01-12` and a valid day for that month.
- Do not write malformed dates like `2018-62-19`; if the parsed date is invalid or ambiguous, write `null`.
- Smoke-test date regex/pattern logic on 1-2 sample strings before running the full batch.
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

Enforce keyword priority strictly: if a higher-priority keyword is present, do not fall back to lower-priority groups for that receipt.

Accept an amount only when it is on the same line as, or immediately adjacent to, a total-related keyword. Treat next-line fallback after a keyword as high-risk; use it only when same-line extraction fails and the keyword line clearly indicates a payable final total, not a broad header/table label or metadata.

Treat exclusion terms as negative signals, not absolute blockers: do not discard a line just because it contains `GST`/`SST` if it also contains a high-priority total phrase like `TOTAL RM` or `GRAND TOTAL`.

Exclude or heavily penalize lines with: SUBTOTAL, DISCOUNT, CHANGE, CASH TENDERED, ROUNDING, tax-only summaries.

Treat generic words like `AMOUNT` or `TOTAL` alone as weak signals; prefer strong phrases such as `GRAND TOTAL`, `TOTAL RM`, `TOTAL AMOUNT`, or `TOTAL DUE`.

Prefer specific final-total phrases and stronger keyword matches over a larger numeric value elsewhere. Reject candidates near unrelated contexts such as litre/quantity/unit-price/item lines, even if the OCR text is noisy.

Do not invent decimals from ambiguous integers unless the receipt text gives strong explicit currency or decimal evidence. Prefer decimal amounts associated with total keywords; avoid plain integers unless the receipt clearly shows no cents.

Treat `0.00` as suspicious unless the OCR text explicitly shows a zero total; otherwise inspect the source line or fallback match and set to `null` if unresolved.

Do NOT let a later weak match override an earlier stronger total candidate just because it appears lower on the receipt.

If multiple total candidates conflict and context does not clearly disambiguate them, set `total_amount` to null.

Handle comma separators (1,234.56).


## Extraction Reliability

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
- Do not attempt package installation unless the environment explicitly allows it.
- Prefer a single Python script that scans all JPGs, runs OCR, parses fields, and writes `/app/workspace/stat_ocr.xlsx` directly; do not manually rebuild the workbook from copied terminal output.
- If extracted records are printed to stdout and the output is long or truncated, save structured output to disk first, then build Excel from that complete file.
- If a tool call returns empty or unusable output, switch methods and capture observable OCR text before claiming a date or total.
- Do not manually "correct" dates or totals unless the value is supported by explicit OCR text seen in the session.
- Prefer stable ranked rules over file-specific patches for individual receipts.
- When debugging specific images, use that only to improve the general parser, then rerun the full dataset and re-verify the final workbook.
- After writing the workbook, reopen it and validate the final contents programmatically instead of assuming the write succeeded.
- Spot-check anomalous outputs before finishing: `date = null`, malformed dates, zero totals, unusually large totals, or unusually many missing values.


## Execution and Recovery


## Final Verification

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