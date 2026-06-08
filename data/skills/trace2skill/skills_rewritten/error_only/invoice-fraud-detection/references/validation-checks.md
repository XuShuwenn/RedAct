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

- Inspect parsed field values produced by the code, not just raw source text. A page can look readable while the parser still truncates or corrupts values.
- Compare parsed values to the exact visible source values for sampled pages. Do not accept partial captures that merely look plausible.
- For labeled fields such as `Payment IBAN: ...`, verify the extractor preserves the entire token shown on the page, including non-alphanumeric characters like underscores when present.
- Include early, middle, and late pages, and expand the sample if any page has missing, blank, truncated, or malformed fields.
- After a bulk parse, review the set of pages where any extracted field is `null`, blank, or obviously truncated before trusting downstream fraud classification.
- If one sampled page is truncated or malformed, treat it as a dataset-level warning, not an isolated anomaly.
- If parsing code contains unusual quoting/escaping or custom regexes/string comparisons, quickly review the literal patterns and operators themselves. Broken quotes, escapes, or comparison syntax can produce plausible-looking but wrong reports.


## Fuzzy matching checks

- Do not choose a vendor-name cutoff from counts alone.
- Inspect names just below and just above the proposed threshold.
- Verify two things before locking the cutoff:
  1. legitimate vendor spelling or format variations still match
  2. unrelated names are rejected
- If a name has multiple close candidates or the top score is borderline, treat it as ambiguous and inspect manually.

- Normalize names first and attempt exact lookup before any fuzzy comparison.
- Explicitly test corporate-suffix variants such as `Acme Inc.` vs `Acme`, `Globex LLC` vs `Globex`, and confirm the normalization collapses the suffix before fuzzy scoring.
- Prefer programmatic review over raw file browsing when the vendor or PO source is large: load the table, inspect candidate matches and linked canonical fields in code, then decide.
- Use fuzzy matching only to propose a candidate vendor. Accept it only when it is a minor spelling/format variant and no structured evidence conflicts.
- If Vendor ID is present on the invoice, use it to confirm or reject the candidate vendor before accepting a fuzzy name match.
- List the non-exact accepted matches and inspect them one by one before finalizing.
- Pay extra attention to matches accepted only after normalization or suffix removal; these can over-collapse distinct vendor names.
- Inspect names just below and just above the proposed threshold. Verify that legitimate spelling/format variants still match while unrelated names are rejected.
- If a legitimate suffix or formatting variant still fails to match, stop and repair normalization or matching logic before continuing.
- If a candidate would change the reason from `Unknown Vendor` to a lower-priority fraud reason, require clear evidence that it is the same vendor.
- If inspection output truncates the compared names or scores, rerun with a narrower query until the full values are visible.
- Once a vendor candidate is accepted, use that vendor's canonical IBAN and Vendor ID for all downstream checks instead of re-matching by name later.

## Final sanity check

Before finishing, confirm the first-applicable reason rule is still respected:
1. Unknown Vendor
2. IBAN Mismatch
3. Invalid PO
4. Amount Mismatch
5. Vendor Mismatch

A wrong parse can create false IBAN, PO, or amount failures, so verify extraction first, then classify.

- Validate the saved JSON file by parsing it directly; do not trust a shell display that truncates mid-record.
- Before finishing, parse `/root/fraud_report.json` end to end and verify every emitted record has exactly the required fields and one allowed reason.
- Do not stop at aggregate totals. For each fraud reason present in `/root/fraud_report.json`, inspect one or more actual records and confirm the source invoice plus vendor/PO data support that exact first-applicable reason.
- Do not stop at spot checks once the JSON exists. Read the full `/root/fraud_report.json`, compute any counts from the file itself, and make sure any summary you give matches those computed results.
- Validate the final JSON mechanically, not just by sampling: top-level array, exact key set per record, allowed `reason` values, and `po_number: null` when PO is missing.
- Validate both directions across the full dataset:
  - every reported page is truly fraudulent for the stated first-applicable reason
  - no omitted page satisfies an earlier fraud criterion
- Check for any invoice records with missing or blank PO values. These must not be filtered out; they should be tested and usually reported as `Invalid PO` with `po_number: null`.
- Reconcile invoice-page count, parsed-record count, and reviewed malformed-page count so every PDF page is accounted for exactly once.
- For each fraud reason present in the final JSON, verify at least one invoice end to end against the invoice page, vendor table, and PO table. Also verify at least one clean page that is absent from the output.
- If the result count looks suspicious, the fraud rate is unusually high, or one reason is heavily concentrated, do not finalize until you re-check classification logic and several source-backed examples across the dataset.
- If any extraction output you used was truncated or preview-only, re-run it before trusting the classification results.
- If any console or file output was truncated, inspect the full saved records before asserting totals, fraud counts, or that specific pages are clean.
- After any schema-related error, re-read the spreadsheet/CSV headers directly before changing column names or join keys.
- If you implemented classification in code, verify the priority is explicit and first-match-only so one invoice cannot emit multiple reasons or a lower-priority reason before a higher-priority one.
- Keep analysis code and debug artifacts until this final review is finished and the report is accepted.

- If your data inspection came from a clipped console preview or a message that full output was saved elsewhere, fetch and inspect the full underlying content before asserting comprehensive coverage or match quality.
- Before stating that the report uses fuzzy matching, first-applicable priority, exact key sets, or missing-PO-to-`null` handling, verify those behaviors from the executed script and by reading the saved JSON directly.
- Never infer unseen trailing records from a truncated `read_file` or console preview. If the output stops mid-record, parse the saved JSON directly or re-read in smaller chunks, then derive page lists, counts, and example records only from that fully observed data.
- If you changed the script after reviewing earlier outputs, discard those earlier conclusions until you rerun the script and re-read the newly written `/root/fraud_report.json`.
- Treat any page list produced during validation as a required reconciliation list. Before finalizing, verify each listed page through the saved `/root/fraud_report.json` or rerun the pipeline until the list is resolved.
- If you manually confirm an edge-case normalization or fuzzy match, check that the final production run actually used that logic: regenerate the report, then inspect the exact affected pages in the saved JSON instead of assuming the earlier exploratory check carried through.
- If you need to repair analysis code after an error, read the relevant script region first and make evidence-backed edits to the exact observed lines. Avoid placeholder replacements against text you have not verified exists.
- A targeted search such as `grep` can help investigate one hypothesis, but it is never sufficient as final validation for the whole report. Always pair it with full-file parsing/validation of `/root/fraud_report.json`.
- Do not treat a failed utility, syntax-broken one-liner, clipped console output, or partial printout as validation. Re-run with a simpler command, smaller chunk, or direct file read until the verification succeeds cleanly.
