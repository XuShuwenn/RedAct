---
name: invoice-fraud-detection
description: "Detect invoice fraud by checking vendor approval, IBAN matching, PO validity, and amount consistency."
---

# Invoice Fraud Detection

## When to Use

- Detect fraudulent invoices from PDF documents
- Cross-check invoices against vendor databases
- Validate purchase orders and amount matching

## Input Files

- `/root/invoices.pdf`: One invoice per page
- `/root/vendors.xlsx`: Approved vendors (Vendor ID, Name, IBAN)
- `/root/purchase_orders.csv`: Valid POs (PO Number, Amount, Vendor ID)

## Required Workflow

1. Inspect the real schemas of `vendors.xlsx` and `purchase_orders.csv` before writing lookup logic; verify actual column names, types, and a few sample rows instead of assuming headers from this skill.
2. Extract and inspect sample text from multiple invoice pages before applying fraud rules; confirm how vendor name, IBAN, PO number, amount, and any Vendor ID actually appear, and whether layouts vary.
3. Validate extraction quality before matching: inspect representative pages from early, middle, and late portions of the PDF.
4. Treat truncated, garbled, or partial extraction as incomplete evidence. If any page looks malformed or fields are missing unexpectedly, fix extraction first or use a fallback method; do not assume the field is absent from the invoice.
5. Parse defensively: initialize missing values to `null`, guard all field lookups, and do not silently skip pages. Confirm expected page count matches extracted invoice records and that every page is accounted for.
6. Before classifying fraud, inspect parsed `vendor_name`, `iban`, `po_number`, and `invoice_amount` on representative pages, including at least one flagged and one unflagged invoice when available.


## Fraud Criteria (in priority order)

1. **Unknown Vendor**: Vendor name not in vendors.xlsx (use fuzzy matching for typos)
2. **IBAN Mismatch**: Vendor exists but IBAN doesn't match
3. **Invalid PO**: PO number not in purchase_orders.csv
4. **Amount Mismatch**: PO exists but amount differs by > 0.01
5. **Vendor Mismatch**: PO linked to different Vendor ID


- Apply **only** the five criteria above. If none of them match, do not flag the invoice.
- Use the **first applicable reason only** according to the priority order above; do not emit multiple reasons for one invoice.
- Treat missing or blank PO numbers as `Invalid PO`; in the output set `po_number` to `null`.
- Normalize vendor names before fuzzy matching (case, punctuation, whitespace, and common corporate suffixes like `inc`, `corp`, `llc`, `ltd`). Keep fuzzy matching conservative: use it only to find candidate vendor names for likely typos or formatting variants.
- If the invoice contains a Vendor ID, use it to confirm or disambiguate the vendor before applying IBAN or PO-related checks. Do not let a name-only fuzzy match override a structured identifier.
- Do not accept a fuzzy match just because it is the closest name in the vendor table. If identity is not clearly the same vendor, report `Unknown Vendor` rather than a lower-priority reason.
- Evaluate the checks in order, but do not structure the pipeline so that a known vendor with matching IBAN skips later PO, amount, or vendor-ID validation. Later checks must still run when earlier checks pass without finding fraud.
- Do not assign `IBAN Mismatch`, `Invalid PO`, `Amount Mismatch`, or `Vendor Mismatch` from partially parsed pages; fix parsing first if key fields are missing or truncated.
- If a normalized or fuzzy match is still ambiguous, investigate the invoice and vendor record directly rather than forcing a weak match.


## Output Format

JSON at `/root/fraud_report.json`:
```json
[
  {
    "invoice_page_number": 1,
    "vendor_name": "Acme Corp",
    "invoice_amount": 5000.00,
    "iban": "US1234567890",
    "po_number": "PO-1001",
    "reason": "IBAN Mismatch"
  }
]
```

- 1-based page indexing
- If PO missing, set to `null`
- Only include flagged invoices
- Use first applicable reason


- The file must be a **top-level JSON array** (`[...]`), not an object wrapper.
- Each element must contain exactly these fields: `invoice_page_number`, `vendor_name`, `invoice_amount`, `iban`, `po_number`, `reason`.
- Do **not** add wrapper keys such as `flagged_invoices`, `summary`, `results`, or other extra metadata.


## Verification Before Finalizing

## Verification Before Finalizing

- Validate the entire `/root/fraud_report.json`, not just a sample or existence check: confirm it is valid JSON, uses a top-level array, includes only flagged invoices, uses 1-based `invoice_page_number`, and sets `po_number` to `null` when missing.
- Confirm every reported entry has the required fields: `invoice_page_number`, `vendor_name`, `invoice_amount`, `iban`, `po_number`, and `reason`.
- Verify page coverage end-to-end: every invoice page was processed exactly once, and any page with missing extracted fields was reviewed rather than silently omitted.
- Perform source-backed spot checks against the PDF text, `vendors.xlsx`, and `purchase_orders.csv` for representative records, covering tricky cases such as fuzzy vendor matches, missing PO, amount differences near `0.01`, IBAN mismatch, and vendor/PO mismatch.
- Confirm each flagged invoice uses exactly one first-applicable reason in the stated priority order: Unknown Vendor, IBAN Mismatch, Invalid PO, Amount Mismatch, then Vendor Mismatch.
- If a vendor-name match is uncertain or not a minor variant, use `Unknown Vendor` instead of any lower-priority reason.
- If results are highly skewed, expected reason types never appear, contradictory results appear, or nearly all invoices are flagged, treat that as a warning sign and audit representative invoices plus parsing quality.
- Check the whole dataset programmatically, not just a sample: every reported page is truly fraudulent, no clean page is included, and no fraudulent page is omitted.
- If validation reveals suspicious counts, ambiguous matches, or parsing failures, fix the logic, regenerate `/root/fraud_report.json`, and re-verify before finishing.
- Keep intermediate artifacts until verification is complete; delete temporary files only after all checks pass.
## Tips

- pdfplumber for PDF extraction
- openpyxl for Excel reading
- fuzzywuzzy or rapidfuzz for string matching
- pandas for CSV processing


## Extraction Rules

- Parse invoice fields conservatively and preserve the exact visible value for vendor name, PO number, amount, and IBAN/payment account.
- Do not use overly restrictive regexes that can truncate valid identifiers. If the source shows `Payment IBAN: FRADULENT_IBAN`, extract `FRADULENT_IBAN`, not `FRADULENT`.
- When a field label is present, prefer capturing the full token after the label up to line end or a clear delimiter, then normalize whitespace only.
- Treat regex extraction and fuzzy matching as provisional until validated on edge cases.

- Prefer simple, testable extraction and normalization over brittle parsing. If you use regexes, inspect the final patterns and test them on a few pages before trusting downstream matching.
- Do not rely on a single `page.extract_text()` pass if a page looks truncated; inspect problematic pages and use alternate extraction or targeted recovery as needed.
- Spot-check both flagged and unflagged invoices rather than trusting aggregate counts alone.
- Read [references/validation-checks.md](references/validation-checks.md) when calibrating fuzzy matching or sanity-checking parsed fields and final fraud reasons.
