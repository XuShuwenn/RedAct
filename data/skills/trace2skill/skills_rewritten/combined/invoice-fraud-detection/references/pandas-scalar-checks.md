# Pandas Scalar Checks

## When to use
Use this when classification logic touches pandas Series/DataFrames, especially after errors like `ValueError: The truth value of a Series is ambiguous` or after a fix that changes flag counts sharply.

## Core rule
Never branch on a Series or DataFrame directly.

Use one of these instead:
- test emptiness with `.empty`
- select one row/value, then compare that scalar
- reduce boolean Series with `.any()` or `.all()`

Examples:

```python
po_rows = po_df[po_df['PO Number'] == po_number]
if po_rows.empty:
    invalid_po = True
else:
    po_amount = float(po_rows.iloc[0]['Amount'])
    amount_mismatch = abs(invoice_amount - po_amount) > 0.01
```

```python
vendor_match = vendors_df['Vendor ID'].eq(vendor_id)
if vendor_match.any():
    vendor_row = vendors_df.loc[vendor_match].iloc[0]
```

## After a fix
Do not stop at "script runs now".
1. Re-run the full pipeline.
2. Check a case that must enter the repaired branch.
3. Re-open `/root/fraud_report.json` and confirm the affected page now has the expected first-applicable reason.
4. If totals shift sharply, audit several pages from the dominant outcome plus at least one contrary case.
