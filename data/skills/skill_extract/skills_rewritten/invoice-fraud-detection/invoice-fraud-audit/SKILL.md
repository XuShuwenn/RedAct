---
name: invoice-fraud-audit
description: "Cross-check invoices against vendor and purchase-order records with fuzzy vendor matching and prioritized fraud reasons."
---

# Invoice Fraud Audit

Reusable workflow for auditing invoice documents by extracting key fields per page and validating them against approved vendor and purchase order (PO) records. Applies vendor-name fuzzy matching and flags fraud using a strict, prioritized rule set.

## When to Use

Activate this skill when you need to:
- Parse invoices (one per page) from a PDF or image-to-text source
- Validate vendor identity using approximate/fuzzy name matching
- Verify IBANs against approved vendor records
- Check PO existence, amounts, and vendor linkage
- Produce a JSON report of only the flagged invoices with 1-based page numbers

## Inputs and Expected Fields

You should have three data sources:
- Invoices: one invoice per page extracted to fields per page:
  - vendor_name (string)
  - invoice_amount (numeric, 2-decimal precision)
  - iban (string, may be missing)
  - po_number (string, may be missing)
- Vendors reference (e.g., spreadsheet):
  - vendor_id (string)
  - vendor_name (string)
  - iban (string)
- Purchase orders reference (e.g., CSV):
  - po_number (string)
  - amount (numeric, 2-decimal precision)
  - vendor_id (string)

Note: Column names vary; normalize and map them to the above logical fields.

## Core Workflow

1. Preflight and Data Loading
   - Confirm you can read the vendor and PO reference files (correct sheet/headers, no hidden trailing spaces).
   - Read the entire invoice PDF and determine the total number of pages.
   - Decide how you will extract per-page fields (vendor name, amount, IBAN, PO). Validate patterns on a few pages before full extraction.

2. Normalize Reference Data
   - Vendor names: lowercase, strip punctuation, normalize company suffixes (e.g., ltd ↔ limited, inc ↔ incorporated, corp ↔ corporation, co ↔ company), collapse whitespace.
   - IBAN: remove spaces, uppercase.
   - Amounts: use decimal arithmetic to avoid floating-point errors.
   - Build indices:
     - vendors_by_id: vendor_id → {vendor_id, vendor_name, iban}
     - vendor_name_list: list of {vendor_id, vendor_name_normalized, iban_normalized}
     - po_by_number: po_number_normalized → {po_number, amount, vendor_id}

3. Extract and Normalize Invoice Fields (per page)
   - Parse text for:
     - Vendor name (look for consistent labels or headings)
     - IBAN (normalize by removing spaces and uppercasing)
     - PO number (strip whitespace, unify format)
     - Amount (strip currency symbols/commas; parse as Decimal with 2 decimals)
   - If a field is missing (e.g., no PO), record it as None/null for downstream checks.

4. Vendor Matching (Fuzzy)
   - Normalize the invoice vendor name using the same normalization as reference.
   - Compute a similarity score against known vendor names (e.g., difflib SequenceMatcher ratio) and select the best match.
   - Use a threshold (e.g., 0.80–0.90). Tune after sampling: too high → false "Unknown Vendor"; too low → wrong vendor matches.

5. Apply Fraud Rules in Strict Priority
   Evaluate each invoice in the following order and stop at the first applicable rule:
   - Unknown Vendor: no vendor match meets the threshold.
   - IBAN Mismatch: vendor matched, but invoice IBAN is missing/malformed or normalized IBAN ≠ approved vendor IBAN.
   - Invalid PO: PO number is missing or not found in the purchase order reference.
   - Amount Mismatch: PO exists; absolute(invoice_amount − po_amount) > 0.01.
   - Vendor Mismatch: PO exists and amounts match tolerance, but PO.vendor_id ≠ matched vendor.vendor_id.

6. Produce the Output
   - Only include flagged invoices.
   - Use 1-based page indexing.
   - If the PO is missing on the invoice, set po_number to null in the output.
   - Use exactly one reason per invoice: the first rule that applies from the list above.
   - Save to the requested JSON path with objects having:
     - invoice_page_number (int, 1-based)
     - vendor_name (string from invoice)
     - invoice_amount (number, two decimals)
     - iban (string from invoice, normalized formatting optional)
     - po_number (string or null)
     - reason (one of: "Unknown Vendor", "IBAN Mismatch", "Invalid PO", "Amount Mismatch", "Vendor Mismatch")

## Verification

Run these checks before finalizing:
- Coverage
  - Count PDF pages and confirm you processed all of them.
  - Spot-check early, middle, and last pages for correct field extraction.
- Vendor Matching Sanity
  - Test a near-match vendor name and confirm it crosses the threshold and resolves to the correct approved vendor.
  - Inspect the top similarity scores for a few matches to ensure threshold is reasonable.
- IBAN Normalization
  - Confirm IBANs are compared after removing spaces and uppercasing.
  - Treat missing invoice IBANs as mismatches for known vendors.
- PO Validation
  - Confirm missing or unparseable PO numbers result in po_number = null and the reason "Invalid PO" when reached in the rule order.
- Amount Precision
  - Compare amounts using Decimal; verify that absolute difference > 0.01 triggers "Amount Mismatch".
- Rule Precedence
  - Create or identify a case that could trigger multiple reasons and confirm only the first applicable reason is assigned.
- Output Structure
  - Validate the JSON schema and confirm only flagged invoices are present.
  - Confirm page numbers are 1-based.

## Common Pitfalls and How to Avoid Them

- Brittle PDF Parsing
  - Pitfall: Assuming fixed field positions or labels and missing pages with slight format shifts.
  - Fix: Inspect representative pages and implement multiple regex patterns per field.
- Poor Vendor Matching
  - Pitfall: No normalization (punctuation, suffixes) or inappropriate threshold.
  - Fix: Normalize both sides; start with a moderate threshold (e.g., ~0.85) and adjust after sampling.
- IBAN Comparison Errors
  - Pitfall: Comparing unnormalized strings or ignoring missing IBANs.
  - Fix: Remove spaces, uppercase; treat missing invoice IBAN as mismatch for matched vendors.
- Floating-Point Rounding Issues
  - Pitfall: Using binary float for amount differences causes off-by-cent errors.
  - Fix: Use Decimal with quantization; compare against Decimal("0.01").
- Rule Ordering Mistakes
  - Pitfall: Emitting "Amount Mismatch" or "Vendor Mismatch" when earlier rules should have fired.
  - Fix: Enforce the exact priority order and short-circuit on first match.
- Page Indexing Off-by-One
  - Pitfall: Using 0-based page numbers in the output.
  - Fix: Always add 1 to the internal index when writing invoice_page_number.
- Missing PO Handling
  - Pitfall: Treating missing PO as non-fraudulent or writing empty strings instead of null.
  - Fix: If PO is missing, set po_number to null and, if earlier rules didn’t trigger, flag "Invalid PO".
- Reference File Assumptions
  - Pitfall: Wrong sheet name/headers or hidden whitespace in keys.
  - Fix: Explicitly set sheet name, strip header strings, and standardize keys.

## Optional Script Usage

The included helper provides reusable normalization, fuzzy matching, and rule evaluation. It expects already-extracted invoice records and reference datasets.

Example (pseudocode):

- Build reference structures:
  - vendors = [{"vendor_id": "...", "vendor_name": "...", "iban": "..."}, ...]
  - pos = [{"po_number": "...", "amount": 123.45, "vendor_id": "..."}, ...]
- For each invoice page (index i):
  - invoice = {"vendor_name": "...", "invoice_amount": 123.45, "iban": "...", "po_number": "... or None"}
  - reason, resolved_po = evaluate using script
  - If reason is not None, write a JSON entry with 1-based page index and the first applicable reason

See scripts/fraud_rules.py for callable utilities.
