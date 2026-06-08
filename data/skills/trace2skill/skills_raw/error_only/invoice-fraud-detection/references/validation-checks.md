# Validation Checks

## When to use
Use this after writing extraction code and before finalizing `/root/fraud_report.json`.

## Extraction sanity checks

- Check several pages directly against the PDF text, not just aggregate counts.
- Confirm each sampled page has correct values for all four fields:
  - `vendor_name`
  - `iban`
  - `po_number`
  - `invoice_amount`
- Include both:
  - at least one invoice that will be flagged
  - at least one invoice that should remain unflagged
- If regexes contain heavy quoting or escaping, inspect parsed outputs extra carefully; silent misparses are common.

## Fuzzy matching checks

- Do not choose a vendor-name cutoff from counts alone.
- Inspect names just below and just above the proposed threshold.
- Verify two things before locking the cutoff:
  1. legitimate vendor spelling or format variations still match
  2. unrelated names are rejected
- If a name has multiple close candidates or the top score is borderline, treat it as ambiguous and inspect manually.

## Final sanity check

Before finishing, confirm the first-applicable reason rule is still respected:
1. Unknown Vendor
2. IBAN Mismatch
3. Invalid PO
4. Amount Mismatch
5. Vendor Mismatch

A wrong parse can create false IBAN, PO, or amount failures, so verify extraction first, then classify.