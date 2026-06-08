---
name: receipt-ocr-extract
description: "Extract receipt dates and final totals from images via Tesseract OCR and write a single-sheet Excel report with deterministic formatting."
---

# Receipt OCR Extraction and Excel Reporting

This skill extracts two key fields from scanned receipt images:
- date (ISO format YYYY-MM-DD)
- total_amount (string with exactly two decimal places)

It uses Tesseract OCR with light image preprocessing and a prioritized keyword-and-exclusion parsing strategy to identify the final payable total, then writes results to a single-sheet Excel file with strict schema.

## When to Use

Activate this skill when a user asks to:
- OCR scanned receipts/invoices to extract the receipt date and final total
- Generate a deterministic Excel report from a folder of receipt images
- Handle OCR quirks like spaced or comma decimals, missing dots, or misread digits

## Core Workflow

1. Collect inputs
   - Image directory path containing JPG/PNG receipt scans
   - Output Excel path
   - Assume filenames should be sorted lexicographically and processed in that order

2. OCR preprocessing and extraction
   - Preprocess each image with:
     - Grayscale
     - Autocontrast
     - Optional upscaling for small images (e.g., 2×)
   - Extract text with Tesseract using `--psm 6` (assumes a uniform block of text)
   - For difficult dates, optionally try a second pass with a digit/separator whitelist

3. Date parsing
   - Prioritize lines containing "Date" (case-insensitive) for date extraction
   - Support patterns:
     - DD/MM/YYYY or DD-MM-YYYY
     - YYYY/MM/DD or YYYY-MM-DD
     - DD.MM.YYYY
     - DD/MM/YY or DD-MM-YY (interpret YY in 2000–2099)
   - Validate month/day ranges; output `YYYY-MM-DD`
   - Fallback: scan all lines if no "Date" line works
   - Optional fallback: extract `YYYYMMDD` from long numeric strings on lines containing invoice identifiers when typical patterns fail

4. Total amount parsing (final payable total)
   - Split OCR text into lines; normalize each line for numeric patterns:
     - Fix spaced decimals: "85. 54" → "85.54"
     - Fix space instead of decimal at line end: "538 00" → "538.00"
     - Convert comma decimals: "99,80" → "99.80" when no dot present
     - Remove thousands separators before float conversion
   - Search lines using a prioritized keyword list (highest to lowest):
     - "GRAND TOTAL"
     - "TOTAL AFTER ADJ", "TOTAL AFTER ROUNDING"
     - "TOTAL INCL" (e.g., "Total incl. of tax/GST")
     - "TOTAL AMT ROUNDED", "TOTAL ROUNDED", "NET TOTAL", "NETT TOTAL"
     - "TOTAL (RM)", "TOTAL(RM)"
     - "TOTAL RM", "TOTAL: RM"
     - "TOTAL:", "TOTAL "
     - "TOTAL" (generic, guarded by exclusions below)
   - Exclude lines with subtotal/tender/tax keywords unless specifically allowed:
     - Exclusions include e.g. "SUBTOTAL", "SUB TOTAL", "DISCOUNT", "CHANGE", "CASH TENDERED", card brands, "TOTAL GROSS", counts, etc.
     - Allowlist overrides exclusions for final-total-like lines (e.g., lines containing "TOTAL AFTER ADJ", "TOTAL ROUNDED", or "TOTAL INCL")
   - On keyword match:
     - Try to extract the last amount on the same line; if none, check the immediate next line
     - If OCR missed the decimal and only a 3–4 digit integer is present at line end, infer cents by splitting last two digits as decimal places (e.g., "1000" → "10.00") for high-priority keywords only
   - Always format amounts as strings with exactly two decimal places

5. Excel output
   - Create exactly one sheet named "results"
   - Columns (in order): filename, date, total_amount
   - First row is the header; subsequent rows are the extracted values (date or total_amount set to null if not found)
   - Ensure written amounts are strings, not numbers, to preserve formatting (e.g., "17.70")

## Verification

Before delivering results:
- Structure
  - Confirm the workbook has exactly one sheet named "results"
  - Verify columns are exactly: filename, date, total_amount
  - Check rows are sorted by filename
- Values
  - Each date is either null or matches YYYY-MM-DD (ISO)
  - Each total_amount is either null or matches the regex `^\d+\.\d{2}$`
  - Ensure total_amount cell type is string when using openpyxl (or explicitly cast to str when writing)

## Common Pitfalls and Mitigations

- Pitfall: Capturing "SUBTOTAL" or tax lines under generic "TOTAL".
  - Mitigation: Apply robust exclusion keywords and only allow exceptions for final-total phrases (e.g., "TOTAL AFTER ADJ", "TOTAL ROUNDED", "TOTAL INCL"). Enforce priority ordering.

- Pitfall: Mis-parsing spaced decimals or comma decimals (e.g., "92 80", "99,80").
  - Mitigation: Normalize lines before parsing: fix spaced decimals, transform comma decimals to dots when no dot is present, and strip thousands separators.

- Pitfall: OCR misses the decimal entirely (e.g., "1000" instead of "10.00").
  - Mitigation: For high-priority lines (e.g., GRAND TOTAL), if only a 3–4 digit integer is present at line end, infer cents by splitting the last two digits as decimal places.

- Pitfall: Matching "TOTAL" inside "SUBTOTAL".
  - Mitigation: Check exclusions before keyword matching; use boundaries and skip the line if it contains excluded tokens.

- Pitfall: Ambiguous totals (e.g., "TOTAL RM INCL." vs. final "TOTAL RM").
  - Mitigation: Use a prioritized keyword list and, if necessary, ignore lines with "INCL" for certain generic patterns unless they are explicitly allowed (e.g., "TOTAL INCL"), to prefer the final payable value.

- Pitfall: Dates not found, or OCR misreads month (e.g., 62 instead of 02).
  - Mitigation: Prioritize lines containing "Date". Support multiple date patterns and 2-digit years. As a fallback, parse YYYYMMDD from long numeric strings on invoice-number lines when present.

- Pitfall: Excel writes numeric types for amounts, causing loss of trailing zeros.
  - Mitigation: Always write amounts as strings (e.g., using openpyxl and `str(value)`), not numeric types. Avoid libraries that coerce datatypes unless carefully configured.

## Optional Script Usage

A reusable script is provided under `scripts/receipt_ocr_to_excel.py`.

Usage:
- python3 scripts/receipt_ocr_to_excel.py --image-dir /path/to/images --out-xlsx /path/to/output.xlsx

Notes:
- Requires Tesseract OCR, pytesseract, Pillow, and openpyxl
- By default uses `--psm 6` and light preprocessing
- Writes a single sheet named "results" with the required columns
