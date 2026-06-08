# Rule Evaluation Pattern

## When to use
Use this when implementing or reviewing the fraud-classification logic so ordered reasons do not block required downstream checks.

## Safe pattern

For each invoice:
1. Resolve vendor identity first using structured identifiers when available, then conservative name matching.
2. Compute each rule result independently as far as the data allows:
   - unknown vendor?
   - iban mismatch?
   - invalid po?
   - amount mismatch?
   - vendor mismatch?
3. Emit only the first failing reason in priority order.

This preserves the "first applicable reason" requirement without making later checks unreachable.

## Avoid

Do not write control flow like:
- `if unknown_vendor: ...`
- `elif known_vendor and iban_matches: ...`
- `elif invalid_po: ...`

That pattern can skip PO, amount, and vendor-mismatch checks whenever the IBAN branch is entered but does not fail.

## Quick review

Test one path explicitly:
- vendor is known
- IBAN matches
- PO is missing or invalid

Expected result: the code still reaches PO validation and returns `Invalid PO`.

- After implementing the pipeline, inspect the code path or emit targeted debug output that shows which condition produced the final reason for a few representative invoices. Verify this for at least one known-vendor/matching-IBAN invoice so PO, amount, and vendor-mismatch checks remain reachable.
- Do not accept summary counts alone. Confirm from implementation or targeted record-level output that each rule is computed independently and the first failing rule is the one emitted.
- Test one invoice or synthetic case where multiple failures are simultaneously possible.
- Example expectation: if vendor is known, IBAN mismatches, and PO is also invalid, the emitted reason must be `IBAN Mismatch`, not `Invalid PO`.
- Example expectation: if vendor is known, IBAN matches, PO is invalid, and amount would also differ, the emitted reason must be `Invalid PO`, not `Amount Mismatch`.

