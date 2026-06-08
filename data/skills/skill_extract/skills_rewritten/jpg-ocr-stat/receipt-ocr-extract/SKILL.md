---
name: receipt-ocr-extract
description: "Extract dates and final totals from OCR text of receipts and produce a strict single-sheet spreadsheet."
---

# Receipt OCR Extraction and Strict Spreadsheet Output

This skill provides a reusable workflow to OCR scanned receipts, robustly parse the transaction date and final total amount, and write a single-sheet spreadsheet that exactly matches strict format requirements.

Use this when you need to:
- OCR one or more receipt images
- Extract a canonical date (ISO: YYYY-MM-DD)
- Extract the final total amount (two decimal places as a string)
- Produce a spreadsheet with a single sheet and precisely specified columns

## When to Use
- The input is a set of receipt images (scans, photos).
- You must identify the final total among many amounts (subtotal, tax, change, etc.).
- You must normalize dates into ISO format.
- The output must be strictly formatted (one sheet, exact headers, types, order).

## Core Workflow

1. Inspect a few sample receipts
   - Manually open several images to understand layouts, labels, and common OCR issues.
   - Note common total labels and exclusion cues.

2. OCR pipeline per image
   - Preprocess: grayscale, binarize, and resize as needed to improve OCR quality.
   - Run Tesseract (e.g., with PSM 6) and capture text.
   - Normalize text: unify case, trim whitespace, standardize spacing and punctuation.

3. Parse date
   - Search for dates in multiple formats (e.g., YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, D Mon YYYY, compact numeric patterns) and convert to ISO.
   - Prefer matches with a 4-digit year. If ambiguous (MM/DD vs DD/MM), attempt both orders and keep a valid calendar date.
   - If primary patterns fail, allow a fallback for compact forms (e.g., YYYYMMDD or DDMMYYYY) that can be deterministically split.

4. Parse final total amount using prioritized keyword matching
   - Scan lines top-to-bottom, accumulating candidates with scores:
     - High priority labels (examples): "GRAND TOTAL" (highest), "TOTAL RM"/"TOTAL: RM", "TOTAL AMOUNT".
     - Medium/low priority labels: "TOTAL", "AMOUNT", "TOTAL DUE", "AMOUNT DUE", "BALANCE DUE", "NETT TOTAL", "NET TOTAL".
   - Exclude lines that likely do not represent the final total (examples): "SUBTOTAL", "SUB TOTAL", "TAX", "GST", "SST", "DISCOUNT", "CHANGE", "CASH TENDERED".
   - For each labeled line:
     - Try to parse an amount on the same line (last numeric token).
     - If none, look at the next non-empty line and take its last numeric token as a fallback.
   - Normalize amounts by removing thousands separators/spaces and ensuring exactly two decimal places.
     - If OCR omits the decimal but digits are plausible (e.g., "2000"), optionally insert a decimal before the last two digits, but only when the label confidence is high.
   - If multiple candidates remain, prefer:
     - Higher-priority labels
     - Later occurrences in the document (final totals tend to appear near the bottom)

5. Assemble results
   - For each image, produce: filename, date (ISO or null), total_amount (two-decimal string or null).
   - Sort rows by filename ascending.

6. Write the spreadsheet
   - Create a single sheet named "results".
   - First row headers exactly: filename, date, total_amount
   - Write date and total_amount as strings; if missing, write null (None) so consumer shows blank/null.
   - Ensure no extra sheets, columns, or rows.

## Verification
Perform programmatic checks before finalizing:
- Sheet count is exactly 1 and named "results".
- Header row equals ["filename", "date", "total_amount"] exactly (case-sensitive, order preserved).
- Rows are sorted by filename ascending.
- Values:
  - date is either a string in YYYY-MM-DD or null.
  - total_amount is either a string matching the regex ^\d+\.\d{2}$ or null. Ensure cells are written as strings, not numeric types.
- Count of rows equals count of input images.

Suggested quick verification snippet (Python, pseudo-structure):
- Load workbook using a library that preserves cell types.
- Assert sheet names and headers.
- For each row:
  - Assert filename non-empty.
  - If date not None: match YYYY-MM-DD and validate a real date.
  - If total_amount not None: match ^\d+\.\d{2}$ and confirm cell is a string.

## Common Pitfalls and Concrete Avoidance Steps
- Pitfall: Selecting subtotal/tax lines as totals.
  - Avoidance: Maintain an exclusion list and check it before accepting a candidate.
- Pitfall: Choosing an early total-like line instead of the final total.
  - Avoidance: Score by priority and prefer later occurrences; boost "GRAND TOTAL" and similar conclusive labels.
- Pitfall: Amount split across lines or OCR merges/splits decimal places.
  - Avoidance: After a matching label, look to the next non-empty line for the last number. Normalize by removing spaces/commas; if no decimal but digits are sufficient, consider inserting a decimal before the last two digits only for strong labels.
- Pitfall: Overly aggressive exclusions that hide legitimate totals.
  - Avoidance: Apply exclusions narrowly; test against problem cases and ensure valid totals remain eligible.
- Pitfall: Date misreads (e.g., OCR noise, ambiguous separators).
  - Avoidance: Try multiple patterns in order; prefer 4-digit years; validate calendars and convert to ISO. Add a compact-number fallback.
- Pitfall: Spreadsheet mismatches (extra sheets, wrong headers, numeric cell types).
  - Avoidance: Explicitly create one sheet named "results" with exact headers; coerce output values to strings; do not auto-format.
- Pitfall: Unsorted output.
  - Avoidance: Sort the row list by filename before writing.

## Optional Script Usage
This repository includes a generic helper module that encapsulates OCR, date parsing, and total extraction logic. You can import it into your task-specific runner script.

Example (pseudo):
- Use `ocr_image(path)` to get text.
- Use `find_date_iso(text)` for ISO date or None.
- Split text into lines and use `find_final_total(lines)` for the two-decimal string or None.
- Accumulate rows, sort by filename, and write the workbook with exact headers and sheet name.

The helper functions implement prioritized keyword matching, exclusions, next-line fallback, and amount normalization.
