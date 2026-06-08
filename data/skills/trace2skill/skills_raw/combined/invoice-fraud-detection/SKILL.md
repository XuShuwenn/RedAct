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

- Use format-specific readers for each input type and prefer a short Python pipeline over ad hoc file reads: use a PDF parser for `/root/invoices.pdf` (for example `pdfplumber` or PyMuPDF), and structured-data readers for `vendors.xlsx` and `purchase_orders.csv` (for example `pandas`/`openpyxl`). Do not treat these files as plain text or rely on generic reads when a dedicated parser is available.
- Confirm the reference datasets were loaded completely before using them for decisions: record row counts, verify the full vendor/PO tables are readable end-to-end, inspect targeted records from different parts of each dataset, and confirm the columns required for each rule are actually present and populated rather than inferred from truncated previews.
- If any schema inspection errors, is truncated, or later fails on a column lookup/join, re-open the source files and inspect the real headers and representative values again before editing logic. Do not continue on guessed headers or inferred column names from tracebacks or conventions.
- Also inspect the actual PDF text labels and layout on representative pages before coding field extraction; do not assume labels such as `Vendor`, `Amount`, `IBAN`, or `PO` without seeing them in the source.

2. Extract and inspect sample text from multiple invoice pages before applying fraud rules; confirm how vendor name, IBAN, PO number, amount, and any Vendor ID actually appear, and whether layouts vary.
3. Validate extraction quality before matching: inspect representative pages from early, middle, and late portions of the PDF.
4. Treat truncated, garbled, or partial extraction as incomplete evidence. If any page looks malformed or fields are missing unexpectedly, fix extraction first or use a fallback method; do not assume the field is absent from the invoice.
5. Parse defensively: initialize missing values to `null`, guard all field lookups, and do not silently skip pages. Confirm expected page count matches extracted invoice records and that every page is accounted for.

- Use an explicit completeness gate before fraud classification: for every page, confirm the extraction path can recover `vendor_name`, `iban`, `po_number` or a justified missing PO, and `invoice_amount`. If any page fails this gate because extraction is truncated or malformed, stop classification for that page set until extraction is repaired or a fallback method is used.
- Convert each invoice page into one structured, auditable record before classification, with fixed fields `invoice_page_number`, `vendor_name`, `iban`, `po_number`, `invoice_amount`, and optional `vendor_id` if present. Preserve exact extracted values first, then normalize only for matching.
- Keep a per-page extraction audit during parsing (at minimum: page number, extracted key fields, and whether parsing was complete) so malformed pages are investigated instead of implicitly treated as clean invoices.
- Record incomplete or malformed pages explicitly during parsing and reprocess them; never let pages disappear from the dataset because a strict pattern, field lookup, or label assumption failed.
- If any inspection output, table preview, page sample, PDF dump, or command output is truncated, cut off, or only a preview, treat it as incomplete evidence. Re-run extraction in smaller chunks or with a fallback method until you can confirm full per-page results, parse success/failure status, and page-count coverage before applying fraud rules.
- Build normalized lookup structures before batch validation: vendor lookups keyed by stable identifiers and normalized names, and PO lookups keyed by PO number. Use these maps for per-invoice checks instead of repeatedly scanning raw files.

6. Before classifying fraud, inspect parsed `vendor_name`, `iban`, `po_number`, and `invoice_amount` on representative pages, including at least one flagged and one unflagged invoice when available.

7. Compare parsed field values against raw PDF text on representative pages and require exact agreement for key fields before trusting classification. For labeled fields such as `Payment IBAN: ...`, preserve the full visible value; any truncation or malformed capture means extraction is not ready.
8. If any targeted check exposes a logic gap, parser defect, or source-to-output mismatch, stop classification, fix the logic or extraction, regenerate the report, and re-run verification on the affected cases before concluding.
9. Do not promote page-specific regexes or field labels to document-wide logic until they succeed on representative pages from across the PDF, including pages with different layouts or missing fields.
10. Prefer a saved Python script over long shell-embedded Python when logic is nontrivial. If you do use inline code, inspect the exact command for quoting, regex, or comparison corruption before trusting the result.
11. Before trusting aggregate outputs such as reason counts or number of flagged invoices, verify that the executed code actually ran the intended fraud logic and that critical branches behaved as expected on representative pages.


## Fraud Criteria (in priority order)

1. **Unknown Vendor**: Vendor name not in vendors.xlsx (use fuzzy matching for typos)
2. **IBAN Mismatch**: Vendor exists but IBAN doesn't match
3. **Invalid PO**: PO number not in purchase_orders.csv
4. **Amount Mismatch**: PO exists but amount differs by > 0.01
5. **Vendor Mismatch**: PO linked to different Vendor ID


- Apply **only** the five criteria above. If none of them match, do not flag the invoice.
- Implement classification as a deterministic per-invoice evaluation: compute each applicable check independently as far as the data allows, then emit only the first failing reason in priority order. Do not use an `if/elif` chain that makes later PO, amount, or vendor-ID checks unreachable just because an earlier check was evaluated and passed.
- Derive fraud decisions only from the invoice contents cross-checked against `vendors.xlsx` and `purchase_orders.csv` using these five criteria. Do **not** add shortcut rules, hardcoded suspicious values, keyword-based fraud categories, or dataset-specific heuristics during final classification.
- Use the **first applicable reason only** according to the priority order above; do not emit multiple reasons for one invoice.
- Treat missing or blank PO numbers as `Invalid PO`; in the output set `po_number` to `null`.
- Implement the missing-PO rule literally: do not skip, drop, or treat such invoices as clean. Classify them as `Invalid PO` and emit the record with `po_number: null`.
- Normalize vendor names before fuzzy matching (case, punctuation, whitespace, and common corporate suffixes like `inc`, `corp`, `llc`, `ltd`). Keep fuzzy matching conservative: use it only to find candidate vendor names for likely typos or formatting variants.
- Normalize common suffix variants before scoring on both invoice and vendor-list names (for example `limited`/`ltd`, `incorporated`/`inc`, `corporation`/`corp`, `co`). Resolve vendors in this order: exact Vendor ID match when present, then exact normalized name match, then conservative fuzzy matching only if exact matching fails.
- Treat fuzzy matching as candidate generation, not proof of identity. Accept a fuzzy match only when it is a clear minor variant of the same name after normalization, such as punctuation, spacing, corporate suffix, or a small typo/transposition. If multiple vendors score similarly, the score is borderline, tokens materially differ, extra distinctive words appear, or structured evidence conflicts, do not force the match; classify as `Unknown Vendor` unless direct inspection clearly confirms the vendor.
- Before using a fuzzy-matched vendor record for IBAN, PO, amount, or vendor-ID checks, compare the raw invoice name to the matched vendor name directly and confirm the difference is only minor formatting or spelling noise.
- Choose any fuzzy-match cutoff only after reviewing names just below and just above the cutoff. Confirm that legitimate formatting/spelling variants still match while unrelated vendors do not.
- If the invoice contains a Vendor ID, use it to confirm or disambiguate the vendor before applying IBAN or PO-related checks. Do not let a name-only fuzzy match override a structured identifier.
- Do not accept a fuzzy match just because it is the closest name in the vendor table. If identity is not clearly the same vendor, report `Unknown Vendor` rather than a lower-priority reason.
- Evaluate the checks in order, but do not structure the pipeline so that a known vendor with matching IBAN skips later PO, amount, or vendor-ID validation. Later checks must still run when earlier checks pass without finding fraud.
- Do not assign `IBAN Mismatch`, `Invalid PO`, `Amount Mismatch`, or `Vendor Mismatch` from partially parsed pages; fix parsing first if key fields are missing or truncated.
- If a normalized or fuzzy match is still ambiguous, investigate the invoice and vendor record directly rather than forcing a weak match.

- Review the logic path on at least one invoice with a known vendor and matching IBAN to confirm the code still reaches PO validation, amount comparison, and PO/vendor-ID consistency checks.
- After a likely vendor-name match is found, validate IBAN, PO, amount, and Vendor ID only against the matched canonical vendor record; never treat fuzzy name similarity itself as evidence that these linked fields are valid.
- Read [references/rule-evaluation-pattern.md](references/rule-evaluation-pattern.md) when implementing or reviewing the fraud-classification pipeline.


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

- Do not stop at reading a few output rows, counts, or a JSON prefix. Programmatically validate the full report against the parsed invoice records: no page was silently skipped, every flagged page satisfies its reported reason, and every unflagged page fails all five fraud criteria.
- Validate the parser itself before trusting classifications: inspect extracted `vendor_name`, `iban`, `po_number`, and `invoice_amount` for representative early, middle, and late pages, including malformed pages, borderline fuzzy matches, suspicious pages, and at least one clean page absent from the output.
- Verify representative examples for each fraud reason that appears in the dataset end to end against the invoice page, vendor table, and PO table, confirming extracted fields, priority ordering, and missing-PO-to-`null` handling. If a reason never appears or one reason dominates unexpectedly, re-check whether extraction, fuzzy matching, or rule ordering suppressed valid outcomes.
- Sanity-check rule reachability, not just output validity: confirm the implementation can actually produce all five specified reasons when the data warrants them, and that known-vendor + matching-IBAN invoices are still evaluated for `Invalid PO`, `Amount Mismatch`, and `Vendor Mismatch`.
- If terminal or tool output is clipped, truncated, or only partially visible, treat verification as incomplete. Re-open the saved files directly, inspect smaller chunks if needed, or run explicit validation commands until the relevant content is fully checked.
- After any debug edit, instrumentation change, schema fix, extraction change, or edge-case investigation, regenerate the report and rerun verification on both the affected cases and the final saved file.
- If a preferred verification tool is unavailable, switch to another method immediately and complete the check rather than skipping it.
- Keep intermediate scripts, extracted samples, analysis code, and debugging artifacts until verification is complete; delete temporary files only after all checks pass.
- Do a last consistency check between the saved JSON and the final response: any mentioned flagged-invoice count, reason count, file status, or other aggregate must match what you just re-read from disk.

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
- Read [references/validation-checks.md](references/validation-checks.md) when calibrating fuzzy matching, handling ambiguous vendor matches, or sanity-checking parsed fields and final fraud reasons.

- Before finalizing extraction logic, print or inspect raw text from a few representative pages and align your field selectors to the actual labels seen on the page (for example `From:`, `Payment IBAN:`, or layout-specific variants).
- If you write regex- or string-heavy extraction code, inspect the final code before trusting it: look for malformed quotes, broken escapes, corrupted comparison operators, or brittle label assumptions, then run a small test that prints extracted `vendor_name`, `iban`, `po_number`, and `invoice_amount` for representative pages.
- Do not proceed to fraud classification when extraction code itself looks syntactically suspicious or parsed fields are obviously garbled; fix the parser first and re-test on sample pages.
- If parsed fields disagree with the visible page text on a spot check, treat the parser as wrong and fix extraction before applying fraud criteria.
- After extraction, print or inspect representative parsed records across the full page range, not just a few samples, so malformed page-specific parsing does not survive to final classification.
