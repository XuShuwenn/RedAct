---
name: invoice-fraud-auditing
description: "Detect fraudulent invoices by parsing PDFs, fuzzy-matching vendor names, and cross-validating IBANs and purchase orders to produce a JSON report of flagged invoices."
---

# Invoice Fraud Auditing

Reusable workflow to extract invoice fields from PDFs, match vendor names (with fuzzy tolerance), cross-check IBAN and PO data, and output a JSON report of only the flagged invoices with prioritized reasons.

## When to Use

Use this skill when you must:
- Parse one-invoice-per-page PDFs and extract Vendor, Amount, IBAN, and PO Number
- Validate invoices against vendor and purchase order registries
- Handle vendor name typos or suffix variations (e.g., Ltd vs Limited)
- Apply ordered fraud checks and emit a structured JSON report of flagged invoices

## Core Workflow

1) Ingest all sources
- PDF: one invoice per page; plan to extract text per page and parse fields.
- Vendors: read the approved vendor registry (Excel/CSV); identify columns for vendor ID, Name, IBAN.
- Purchase Orders: read the PO registry (CSV/Excel); identify columns for PO Number, Amount, Vendor ID.

2) Extract invoice fields from PDF
- Use a robust PDF text extractor (e.g., pdfplumber or PyMuPDF) and parse with regex:
  - Vendor Name: anchor on a preceding label (e.g., "From:") and capture remainder of the line.
  - Total Amount: capture numeric with optional thousands separators and decimals; coerce to numeric.
  - IBAN: capture contiguous token after a label (e.g., "Payment IBAN:").
  - PO Number: capture non-whitespace token after a label (e.g., "PO Number:").
- Record 1-based page indices.
- Treat placeholders like obvious invalid PO tokens (e.g., "PO-INVALID") or missing PO as null; keep this configurable.

3) Normalize and fuzzy-match vendor names
- Normalize function (applies to both invoice and registry names):
  - lowercase; remove punctuation; collapse whitespace
  - map common suffix synonyms (e.g., limited->ltd, corporation->corp, incorporated->inc)
- Match strategy:
  - Try case-insensitive exact match
  - Try normalized exact match
  - Fuzzy match with a fixed threshold (e.g., 0.8) using either token-set or sequence similarity
- Return the best matching registry vendor name (and its ID) or None if below threshold.

4) Build lookups for constant-time checks
- Vendors: name->id, name->iban, id->(name, iban). Prefer name keys as the canonical registry names (not the normalized strings) to preserve original registry values.
- POs: po_number->(amount, vendor_id). Ensure amounts are numeric.

5) Apply fraud checks in strict priority order
For each invoice, evaluate in this order and stop at the first reason that applies:
- Unknown Vendor: no vendor match from fuzzy pipeline.
- IBAN Mismatch: matched vendor exists but invoice IBAN does not equal the registry IBAN.
- Invalid PO: PO missing/null or PO number not present in the PO registry.
- Amount Mismatch: absolute difference between invoice and PO amounts exceeds 0.01.
- Vendor Mismatch: the PO vendor_id differs from the matched vendor ID.

Notes:
- Use absolute numeric comparison with a fixed tolerance (0.01). Prefer precise arithmetic (e.g., Decimal) to avoid float rounding surprises.
- If the PO is missing or invalid, set po_number to null in the output entry.
- Only emit invoices that triggered a reason.

6) Output JSON report
- Emit only flagged invoices, each as an object with keys:
  - invoice_page_number (1-based integer)
  - vendor_name (verbatim from the invoice)
  - invoice_amount (number; not a string with currency symbols)
  - iban (verbatim from the invoice)
  - po_number (string or null if missing/invalid)
  - reason (one of: Unknown Vendor, IBAN Mismatch, Invalid PO, Amount Mismatch, Vendor Mismatch)

## Verification

Perform these checks before finalizing:
- Page-to-record check: number of parsed invoice objects equals number of PDF pages.
- Field sanity:
  - Amounts: no currency symbols or commas; numeric type; plausible range
  - IBAN: non-empty when present; treat missing IBAN carefully (only flag as IBAN Mismatch when a mismatching value exists)
  - PO: null only when missing/invalid
- Fuzzy threshold sanity: spot-check borderline matches and confirm normalization removes suffix/punctuation noise.
- Rule precedence: ensure only the first applicable reason is used; later checks must be skipped.
- Vendor mismatch uses vendor IDs, not names.
- JSON schema validation: required keys present, types correct, reasons within allowed set, 1-based page indices.

## Common Pitfalls (and Concrete Preventive Checks)

- Off-by-one pages: Always enumerate PDF pages starting at 1.
- Regex brittleness: Anchor on labels (e.g., "From:", "Total", "Payment IBAN:", "PO Number:") and allow flexible whitespace; strip commas from amounts before numeric conversion.
- Fuzzy matching drift: Without normalization (suffix synonyms, punctuation stripping), benign variations fail to match. Normalize both sides first.
- Wrong precedence: Running amount/vendor mismatch before "Invalid PO" violates requirements. Short-circuit as soon as a reason is assigned.
- Comparing vendor names for Vendor Mismatch: Must compare vendor IDs from the PO registry vs matched vendor ID.
- Float rounding errors: Use Decimal and compare with a strict > 0.01 threshold.
- Column name surprises: Vendor/PO files may have varied header cases or synonyms. Detect columns via case-insensitive, token-based matching.
- Forgetting to null invalid/missing PO: When reason is "Invalid PO", set po_number to null in the output.
- Treating missing IBAN as automatic mismatch: Only flag IBAN Mismatch when a mismatching non-empty invoice IBAN is present and the registry has an expected IBAN.

## Optional Script Usage

A reusable toolkit is provided in scripts/invoice_fraud_toolkit.py with CLI support.

Example:
- python3 scripts/invoice_fraud_toolkit.py --pdf /path/invoices.pdf --vendors /path/vendors.xlsx --pos /path/purchase_orders.csv --out /path/fraud_report.json --fuzzy-threshold 0.8 --fuzzy-method token

Key options:
- --pdf: Invoices PDF path
- --vendors: Vendors Excel/CSV path
- --pos: Purchase orders CSV/Excel path
- --out: Output JSON path
- --fuzzy-threshold: Match threshold (0-1)
- --fuzzy-method: sequence or token (token-set style)
- --invalid-po-token: Add one or more tokens considered invalid PO values (can repeat)

The script will:
- Extract and parse invoices
- Normalize and fuzzy-match vendor names
- Build registry lookups
- Apply fraud rules in the specified order
- Write only flagged invoices to JSON with the required schema
