---
name: invoice-fraud-detection
description: "Detect invoice fraud by checking vendor approval, IBAN matching, PO validity, and amount consistency."
---

# Invoice Fraud Detection

## When to Use

- Detect fraudulent invoices from PDF documents
- Cross-check invoices against vendor databases
- Validate purchase orders and amount matching


## When to Use

## Execution Protocol

- Follow the current environment's required tool-call/action schema exactly. If the environment specifies a strict invocation format, argument structure, executable name, or completion token, use that exact format verbatim for every tool call and for the final completion signal.
- Use only tools and file-access methods that are explicitly available in the current runtime. If only a bash-style interface is provided, inspect files and run scripts through bash commands rather than assuming separate read/edit tools exist.
- Before each tool use, send a concrete, executable command or payload for the exposed tool. Do **not** substitute natural-language descriptions, alternate wrappers, pseudo-calls, or unsupported call styles in place of executable actions.
- Treat interface compliance as mandatory even when the analysis logic is otherwise correct.

## Input Files

- `/root/invoices.pdf`: One invoice per page
- `/root/vendors.xlsx`: Approved vendors (Vendor ID, Name, IBAN)
- `/root/purchase_orders.csv`: Valid POs (PO Number, Amount, Vendor ID)

## Required Workflow

1. Inspect the real schemas of `vendors.xlsx` and `purchase_orders.csv` before writing lookup logic; verify actual column names, types, and a few sample rows instead of assuming headers from this skill.
- Preserve a short evidence trail from schema inspection: record the actual headers, row counts, and one or two representative records you will use for joins/comparisons so later code changes stay grounded in the real data.
- Do not claim full-invoice, full-vendor, or full-PO analysis from sample-only inspection. If you have only viewed a subset, a truncated preview, or an early-page sample, explicitly treat coverage as incomplete and continue with chunked or programmatic inspection until every PDF page and the full reference tables are accounted for.
- Prefer one saved Python script that loads all three inputs, builds vendor/PO lookups, evaluates the five fraud rules in priority order, and writes `/root/fraud_report.json` in one auditable pass. Use ad hoc shell inspection only for debugging or narrow spot checks, not as the primary classification workflow.
- In that workflow, print or save the loaded row counts and key column names for `vendors.xlsx` and `purchase_orders.csv`, and inspect at least one late/end-of-file record before trusting joins or fraud decisions.

- Use only concrete, executable analysis steps. Do not write placeholder actions like “extract the PDF” or “run fraud analysis”; save and run an actual script or exact shell command so the parsing and classification logic is inspectable and repeatable.
- Do not use placeholder script-generation steps, prose summaries, or opaque "did the analysis" descriptions in place of code. The saved analysis script or command must contain the actual implemented parsing, matching, classification, and output-writing logic, and you must inspect that real content before trusting its results.
- If using bash, make the command itself inspectable and sufficient to reproduce the result. Do not rely on high-level prose such as "loaded files, matched vendors, wrote report" as evidence that the logic actually ran.
- Before running any newly created or edited analysis script, inspect the saved file and confirm it contains executable Python code rather than prose, TODOs, comments-only scaffolding, or placeholder instructions.

- Keep the analysis auditable: preserve the exact script/commands that produced `/root/fraud_report.json`, and do not claim fuzzy matching, priority handling, null handling, or other logic unless the executed code actually implements and demonstrates them.
- Before any join, lookup, or rule evaluation, inspect the loaded invoice/vendor/PO records and confirm the real field names and representative values in memory or in saved intermediate data. If required fields are `null`, missing, or unexpectedly renamed, fix extraction/loading first rather than guessing schema.


- Use format-specific readers for each input type and prefer a short Python pipeline over ad hoc file reads: use a PDF parser for `/root/invoices.pdf` (for example `pdfplumber` or PyMuPDF), and structured-data readers for `vendors.xlsx` and `purchase_orders.csv` (for example `pandas`/`openpyxl`). Do not treat these files as plain text or rely on generic reads when a dedicated parser is available.
- Match the tool to the file type on the first attempt: use a PDF parser for `.pdf`, spreadsheet readers for `.xlsx`, and CSV readers for `.csv`. Do not treat structured or binary files as plain-text evidence.
- For mixed binary/business inputs, switch quickly to format-appropriate extraction and convert them into structured records early. Prefer a small saved Python script that loads the PDF/XLSX/CSV into in-memory tables; use shell/text inspection only for narrow spot checks, not as the main analysis method.

- Confirm the reference datasets were loaded completely before using them for decisions: record row counts, verify the full vendor/PO tables are readable end-to-end, inspect targeted records from different parts of each dataset, and confirm the columns required for each rule are actually present and populated rather than inferred from truncated previews.
- Record concrete completeness evidence such as `len(...)`, dataframe `.shape`, worksheet dimensions, or CSV row counts and keep those values available for audit. For large structured sources, use a two-step workflow: inspect a small schema/sample slice for orientation, then run code that loads the full table and validates row counts plus targeted beginning/middle/end records before making any fraud decision. A sample slice is not final evidence.

- Inspect structured sources with format-appropriate tools only: use pandas/openpyxl for `.xlsx` and pandas/csv readers for `.csv`. Do **not** use `grep`, raw text search, or other plain-text inspection methods as evidence for spreadsheet contents.
- Before any fraud classification run, prove the reference data is usable end to end: inspect the actual vendor and PO column names, total row counts, and a few targeted records that exercise the fields used in matching (`Vendor ID`, vendor name, IBAN, PO number, amount). Do not rely on a script claim that the files loaded successfully.
- If the first attempt to read `vendors.xlsx` or `purchase_orders.csv` fails, is truncated, or uses the wrong reader, switch methods and then re-run schema inspection and sample-record checks before continuing.
- If any tool, terminal, notebook, or file viewer shows only a preview, clipping, or a message such as "output too large" / "full output saved to ...", do **not** treat that preview as having inspected the dataset. Re-open the original source files or the saved full output, or run a script that reads the complete table and prints targeted summaries from it before building joins or making fraud claims.
- Treat any malformed, truncated, syntax-broken, empty, or format-inappropriate diagnostic command as **no evidence**. Re-run a working check with the correct tool before concluding that a field, match, vendor case, or fraud reason is absent.
- If invoices are first converted to an intermediate format such as JSON, JSONL, or CSV, inspect that intermediate schema and representative records before writing downstream logic. Do not start matching or classification from assumed keys or records where core fields are still null or malformed.


- If any schema inspection errors, is truncated, or later fails on a column lookup/join, re-open the source files and inspect the real headers and representative values again before editing logic. Do not continue on guessed headers or inferred column names from tracebacks or conventions.
- Also inspect the actual PDF text labels and layout on representative pages before coding field extraction; do not assume labels such as `Vendor`, `Amount`, `IBAN`, or `PO` without seeing them in the source.

2. Extract and inspect sample text from multiple invoice pages before applying fraud rules; confirm how vendor name, IBAN, PO number, amount, and any Vendor ID actually appear, and whether layouts vary.
- Use sampled page text to design the parser around observed labels/layout, not assumed field names. When parsed values look implausible, print the raw extracted text for a representative page and align the parser to the actual labels before changing downstream fraud logic.
- Convert every source into structured records before cross-file validation: one record per invoice page from the PDF, tabular vendor records from `vendors.xlsx`, and tabular PO records from `purchase_orders.csv`.

3. Validate extraction quality before matching: inspect representative pages from early, middle, and late portions of the PDF.
4. Treat truncated, garbled, or partial extraction as incomplete evidence. If any page looks malformed or fields are missing unexpectedly, fix extraction first or use a fallback method; do not assume the field is absent from the invoice.
5. Parse defensively: initialize missing values to `null`, guard all field lookups, and do not silently skip pages. Confirm expected page count matches extracted invoice records and that every page is accounted for.

- Use an explicit completeness gate before fraud classification: for every page, confirm the extraction path can recover `vendor_name`, `iban`, `po_number` or a justified missing PO, and `invoice_amount`. If any page fails this gate because extraction is truncated or malformed, stop classification for that page set until extraction is repaired or a fallback method is used.
- Convert each invoice page into one structured, auditable record before classification, with fixed fields `invoice_page_number`, `vendor_name`, `iban`, `po_number`, `invoice_amount`, and optional `vendor_id` if present. Preserve exact extracted values first, then normalize only for matching.
- Keep a per-page extraction audit during parsing (at minimum: page number, extracted key fields, and whether parsing was complete) so malformed pages are investigated instead of implicitly treated as clean invoices.
- While debugging or validating extraction, save the parsed per-page invoice records to an intermediate artifact and re-open a few records from that artifact before classification. This creates an auditable boundary between parsing and fraud logic and helps catch page-level extraction defects.


- Do not rely on marker counts, page counts, or a few text previews as proof that extraction is good enough. Programmatically review the per-page extracted records across the full PDF and identify every page where any key field is blank, truncated, malformed, or suspicious before running fraud rules.
- Build or inspect a per-page structured extraction table for the entire PDF and verify every page has complete key fields or is explicitly marked for reprocessing. Do not substitute page-marker counts, PO-marker counts, or a few sampled page dumps for full per-page extraction review.

- Treat visibly clipped samples such as partial PO numbers, IBANs, or labels as extraction failures, not harmless display artifacts. Re-extract those pages with a fallback method and confirm the repaired values in the structured records before classification.
- Record incomplete or malformed pages explicitly during parsing and reprocess them; never let pages disappear from the dataset because a strict pattern, field lookup, or label assumption failed.
- If any inspection output, table preview, page sample, PDF dump, or command output is truncated, cut off, or only a preview, treat it as incomplete evidence. Re-run extraction in smaller chunks or with a fallback method until you can confirm full per-page results, parse success/failure status, and page-count coverage before applying fraud rules.
- Build normalized lookup structures before batch validation: vendor lookups keyed by stable identifiers and normalized names, and PO lookups keyed by PO number. Use these maps for per-invoice checks instead of repeatedly scanning raw files.

6. Before classifying fraud, inspect parsed `vendor_name`, `iban`, `po_number`, and `invoice_amount` on representative pages, including at least one flagged and one unflagged invoice when available.

7. Compare parsed field values against raw PDF text on representative pages and require exact agreement for key fields before trusting classification. For labeled fields such as `Payment IBAN: ...`, preserve the full visible value; any truncation or malformed capture means extraction is not ready.
8. If any targeted check exposes a logic gap, parser defect, or source-to-output mismatch, stop classification, fix the logic or extraction, regenerate the report, and re-run verification on the affected cases before concluding.
9. Do not promote page-specific regexes or field labels to document-wide logic until they succeed on representative pages from across the PDF, including pages with different layouts or missing fields.
10. Prefer a saved Python script over long shell-embedded Python when logic is nontrivial. If you do use inline code, inspect the exact command for quoting, regex, or comparison corruption before trusting the result.
- When you create a `.py` analysis script, write executable Python code, not plan text, comments-only scaffolding, or natural-language placeholders. Before relying on the script, open the file or otherwise inspect its contents enough to confirm it contains real imports, logic, and output code.
- Do not accept a tool message like "created/ran the script" as evidence. Inspect the saved `.py` file contents directly, confirm the key extraction, matching, classification, and output-writing logic is present, and keep the exact execution command auditable before using any claimed results.
- If a required code file contains prose, a summary, or placeholder text instead of runnable Python, treat that as a blocking failure: rewrite the file with executable code, reopen it to confirm, then run it.

- Run any newly written analysis script once on a small check or the real inputs and confirm it executes without syntax or runtime failure before using its results for fraud conclusions. If the first run fails, inspect the traceback and the actual file contents, fix the script, and re-run before continuing.
- Record observable implementation evidence in the workflow: the actual script contents, the concrete command used to run it, and the resulting `/root/fraud_report.json` checks. Do not base completion on high-level summaries of unseen execution.

- When repairing extraction or classification code, inspect the relevant saved script sections first and edit the exact observed code. Do **not** apply placeholder-based replacements or broad search/replace operations against assumed text you have not confirmed is present.
- If you need to change a saved analysis script, first read the exact region you will edit and anchor the fix to observed code lines, variable names, field accesses, and real source headers. Do **not** use placeholder descriptions like "previous loading logic" or inferred text as replacement targets.
- If a script performs core extraction, matching, or fraud classification, inspect the saved script itself before trusting it: confirm it contains the actual rule logic, output-writing path, and key joins/lookups needed for this task rather than a placeholder wrapper or opaque delegation.

- After any runtime error such as a missing column/header/key, re-open the script and the source schema together before editing. Confirm the exact field names, joins, and code paths involved rather than patching from traceback guesses alone.
- Treat tracebacks as hypotheses, not proofs of root cause: inspect the failing script region and the real input headers/sample values together before choosing a fix.
- After repairing an execution error, rerun the script to a clean completion state and only then continue to report validation. Do not carry forward conclusions from a failed or partially failed run.
- After any schema, parsing, missing-key, or runtime error, switch to short inspectable commands or a saved script that shows the exact headers, sample rows, and revised logic. Do not continue from opaque natural-language summaries of what a command supposedly did.

11. Before trusting aggregate outputs such as reason counts or number of flagged invoices, verify that the executed code actually ran the intended fraud logic and that critical branches behaved as expected on representative pages.
12. Verify the format of every intermediate artifact before writing downstream logic against it. If you save extracted invoices, parsed records, or match candidates, re-open one or two records and confirm whether the file is JSON, JSONL, CSV, or another structure before indexing into it.
13. Prefer dependency-light methods first. If `rapidfuzz`, `fuzzywuzzy`, or another optional package is unavailable, do not stop to install packages into the environment; use a built-in fallback (for example normalized exact matching plus `difflib.SequenceMatcher` or `get_close_matches`) and continue with explicit manual review of ambiguous matches.
14. Do not treat package installation as part of the core workflow. In restricted environments, switch methods immediately instead of attempting environment modification.
- If an optional package import fails, treat that as a method-selection issue, not an installation task. Switch immediately to an available built-in or already-installed alternative and continue the analysis.

15. After any edit to extraction, matching, or classification code, run a targeted end-to-end check on the changed behavior before trusting the full report. Do not rely on assumed replacements; inspect the actual saved code and confirm it executes and produces the expected fields and reasons on representative invoices.
16. Treat repeated command failures, syntax errors, empty debug output, or unexpectedly blank parses as a stop signal. Fix the script, rerun it, and verify the affected pages or records directly before making further pipeline edits or fraud conclusions.
17. After any repair to the script or logic, discard conclusions drawn from earlier failed, partial, or pre-edit diagnostics. Regenerate `/root/fraud_report.json` and validate again using successful commands that read the actual saved outputs.
18. Do not describe extraction, normalization, fuzzy matching, null handling, priority order, exact JSON shape, or other implementation details unless you inspected the saved script/code or produced targeted validation output showing those behaviors actually ran.

17. Treat suspicious aggregate outcomes as a hard stop for reinspection, not a success signal. If most invoices are flagged, almost none are flagged, an expected fraud reason never appears, or one source-table inspection is only a header, tiny preview, or truncated snippet, re-open the underlying PDF and reference files, confirm full row counts and representative records, and re-check joins and lookups before accepting the result.

- A good default sequence is: inspect spreadsheet/CSV schemas -> inspect one representative invoice page -> write the analysis script -> run it -> inspect extracted records on representative pages -> validate `/root/fraud_report.json` programmatically.
- If any read of extracted invoices, intermediate records, or `/root/fraud_report.json` is truncated or preview-only, continue reading in chunks or parse the full file programmatically until you have complete evidence. Do not derive dataset-wide conclusions from partial records.
- If fraud results are extreme or highly concentrated, perform a source-backed audit before finalizing: inspect representative flagged invoices from the dominant reason, inspect at least one unflagged invoice when available, and show the exact vendor/PO evidence or absence of evidence that justifies the reported first-applicable reason.



## Fraud Criteria (in priority order)

1. **Unknown Vendor**: Vendor name not in vendors.xlsx (use fuzzy matching for typos)
2. **IBAN Mismatch**: Vendor exists but IBAN doesn't match
3. **Invalid PO**: PO number not in purchase_orders.csv
4. **Amount Mismatch**: PO exists but amount differs by > 0.01
5. **Vendor Mismatch**: PO linked to different Vendor ID


- Apply **only** the five criteria above. If none of them match, do not flag the invoice.
- Implement classification as a deterministic per-invoice evaluation: compute each applicable check independently as far as the data allows, then emit only the first failing reason in priority order. Do not use an `if/elif` chain that makes later PO, amount, or vendor-ID checks unreachable just because an earlier check was evaluated and passed.
- Use a per-invoice `checks` structure or named rule-result variables to store the outcome of all five criteria before selecting the final reason. Then choose the first failing criterion from that stored result set in priority order.
- Keep validation around independent reference checks after vendor resolution: use vendor data for vendor existence and IBAN, and PO data for PO validity, PO-linked vendor ownership, and amount consistency. Do not let one successful check imply the invoice is clean or make downstream checks unreachable.

- Derive fraud decisions only from the invoice contents cross-checked against `vendors.xlsx` and `purchase_orders.csv` using these five criteria. Do **not** add shortcut rules, hardcoded suspicious values, keyword-based fraud categories, or dataset-specific heuristics during final classification.
- Use the **first applicable reason only** according to the priority order above; do not emit multiple reasons for one invoice.
- Treat missing or blank PO numbers as `Invalid PO`; in the output set `po_number` to `null`.
- Implement the missing-PO rule literally: do not skip, drop, or treat such invoices as clean. Classify them as `Invalid PO` and emit the record with `po_number: null`.
- Before finalizing classification/output logic, inspect how missing PO values actually appear in parsed records (missing key, empty string, placeholder text, or `null`) and normalize them deliberately so the final JSON emits `po_number: null` for those invoices.

- Normalize vendor names before fuzzy matching (case, punctuation, whitespace, and common corporate suffixes like `inc`, `corp`, `llc`, `ltd`). Keep fuzzy matching conservative: use it only to find candidate vendor names for likely typos or formatting variants.
- Normalize common suffix variants before scoring on both invoice and vendor-list names (for example `limited`/`ltd`, `incorporated`/`inc`, `corporation`/`corp`, `co`). Resolve vendors in this order: exact Vendor ID match when present, then exact normalized name match, then conservative fuzzy matching only if exact matching fails.
- Treat fuzzy matching as candidate generation, not proof of identity. Accept a fuzzy match only when it is a clear minor variant of the same name after normalization, such as punctuation, spacing, corporate suffix, or a small typo/transposition. If multiple vendors score similarly, the score is borderline, tokens materially differ, extra distinctive words appear, or structured evidence conflicts, do not force the match; classify as `Unknown Vendor` unless direct inspection clearly confirms the vendor.
- Before using a fuzzy-matched vendor record for IBAN, PO, amount, or vendor-ID checks, compare the raw invoice name to the matched vendor name directly and confirm the difference is only minor formatting or spelling noise.
- Accept a non-exact vendor-name match only when linked structured evidence stays consistent with that vendor: the invoice IBAN should match the candidate vendor or, if IBAN is the suspected failing field, the PO number / amount / Vendor ID evidence should still line up with the same canonical vendor. If the fuzzy candidate is not supported by linked vendor/PO data, treat it as `Unknown Vendor` instead of forcing a lower-priority reason.

- Choose any fuzzy-match cutoff only after reviewing names just below and just above the cutoff. Confirm that legitimate formatting/spelling variants still match while unrelated vendors do not.
- If the invoice contains a Vendor ID, use it to confirm or disambiguate the vendor before applying IBAN or PO-related checks. Do not let a name-only fuzzy match override a structured identifier.
- Do not accept a fuzzy match just because it is the closest name in the vendor table. If identity is not clearly the same vendor, report `Unknown Vendor` rather than a lower-priority reason.
- Evaluate the checks in order, but do not structure the pipeline so that a known vendor with matching IBAN skips later PO, amount, or vendor-ID validation. Later checks must still run when earlier checks pass without finding fraud.
- Do not assign `IBAN Mismatch`, `Invalid PO`, `Amount Mismatch`, or `Vendor Mismatch` from partially parsed pages; fix parsing first if key fields are missing or truncated.
- If a normalized or fuzzy match is still ambiguous, investigate the invoice and vendor record directly rather than forcing a weak match.
- Before finalizing vendor-resolution logic, run a targeted check on at least one borderline or normalized-name variation and confirm the accepted match is only a minor formatting/spelling variant of the same vendor.
- Keep a short review list of accepted non-exact vendor matches and inspect them individually before trusting downstream IBAN, PO, amount, or Vendor ID checks.


- Review the logic path on at least one invoice with a known vendor and matching IBAN to confirm the code still reaches PO validation, amount comparison, and PO/vendor-ID consistency checks.
- After a likely vendor-name match is found, validate IBAN, PO, amount, and Vendor ID only against the matched canonical vendor record; never treat fuzzy name similarity itself as evidence that these linked fields are valid.
- Read [references/rule-evaluation-pattern.md](references/rule-evaluation-pattern.md) when implementing or reviewing the fraud-classification pipeline.
- If you adjust normalization, fuzzy thresholds, accepted candidate matches, or vendor-resolution rules during debugging, rerun the full invoice set through the final pipeline and confirm the affected pages changed appropriately in `/root/fraud_report.json` before concluding.

- Before finalizing, explicitly verify rule reachability for all five reasons against the final pipeline: for each reason, either confirm at least one supporting invoice in the dataset or document from source-backed inspection why no invoice qualifies. Do not treat a missing category in `/root/fraud_report.json` as proof the implementation is correct.
- If a reason never appears, or appears only after recent code changes, audit the extraction, vendor resolution, and control flow for that rule and then regenerate `/root/fraud_report.json` before concluding.
- Do not assume normalization or fuzzy matching is active just because helper code or an exploratory check exists. Prove it on edge-case invoice names by rerunning the end-to-end classifier and checking the final saved JSON for those exact invoices.
- After implementing classification, run at least one targeted overlap-case check where more than one rule could plausibly apply and confirm the saved result uses the earliest applicable reason only.



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
- A quick preview can help spot obvious shape problems, but final format validation must be programmatic on the full saved file: parse `/root/fraud_report.json`, confirm the top-level array, and verify every record has exactly the required keys.


- Do not assert that the saved file meets these format requirements from a preview alone; parse the full file and verify the top-level type, exact key set, and allowed values mechanically.
- Do not report flagged pages, record counts, or example entries from `/root/fraud_report.json` unless you have re-read the saved file in a way that shows the full contents or validated it programmatically. If any file read cuts off mid-record or is preview-only, treat all report details as unverified until you fetch the remainder.

## Verification Before Finalizing

- Do not stop at reading a few output rows, counts, or a JSON prefix. Programmatically validate the full report against the parsed invoice records: no page was silently skipped, every flagged page satisfies its reported reason, and every unflagged page fails all five fraud criteria.

- Base final claims only on evidence you actually checked. Do not claim the report handled all pages, used the correct priority order, applied fuzzy matching or normalization, or satisfied the exact output schema unless you directly inspected the code or ran explicit validation for those properties.
- Do not accept a truncated console preview, `head` output, a script's self-reported success message, or aggregate reason counts as final verification. Re-open `/root/fraud_report.json` directly, parse the entire file, and compute counts from that parsed content before concluding.
- A single `grep`, one reason-specific spot check, or a visibly truncated `read_file`/console preview is never enough to validate `/root/fraud_report.json`. Re-read or parse the full saved file and base final claims only on that complete check.
- If any output view ends mid-record or only shows the first few items, treat verification as failed. Fetch the remainder or run a programmatic full-file validation before concluding.
- After generating `/root/fraud_report.json`, perform one explicit full-dataset reconciliation before finalizing: compare total PDF pages, parsed invoice records, flagged pages in the saved JSON, and unflagged pages that were checked to fail all five criteria. Any unexplained page gap is a blocker.
- Never state exact flagged-invoice totals, page lists, or example records from `/root/fraud_report.json` unless they come from a successful full-file parse or equivalent programmatic validation over the complete file.

- Verify the saved report against the implemented decision logic, not just structure or counts: confirm the first-applicable-rule ordering is actually reflected in `/root/fraud_report.json`, including cases where vendor is known and IBAN matches but PO, amount, or PO/vendor consistency should still be checked.
- For representative flagged invoices, explicitly test whether any higher-priority rule should have fired before the reported reason. If a sampled record reported as `IBAN Mismatch`, `Invalid PO`, `Amount Mismatch`, or `Vendor Mismatch` also satisfies an earlier rule when checked against the exact matched vendor and PO records, treat the report as wrong, fix the logic, regenerate the file, and re-verify.
- During verification, inspect at least one representative invoice where earlier checks pass (known vendor and matching IBAN) and confirm the stored per-invoice rule results still allow downstream PO, amount, and vendor-mismatch evaluation before the final reason is chosen.

- If you mention totals in your final response, derive them from the re-read saved JSON and ensure they match exactly; if they do not, treat verification as failed and investigate before finishing.- Validate the parser itself before trusting classifications: inspect extracted `vendor_name`, `iban`, `po_number`, and `invoice_amount` for representative early, middle, and late pages, including malformed pages, borderline fuzzy matches, suspicious pages, and at least one clean page absent from the output.
- Verify representative examples for each fraud reason that appears in the dataset end to end against the invoice page, vendor table, and PO table, confirming extracted fields, priority ordering, and missing-PO-to-`null` handling. If a reason never appears or one reason dominates unexpectedly, re-check whether extraction, fuzzy matching, or rule ordering suppressed valid outcomes.
- Sanity-check rule reachability, not just output validity: confirm the implementation can actually produce all five specified reasons when the data warrants them, and that known-vendor + matching-IBAN invoices are still evaluated for `Invalid PO`, `Amount Mismatch`, and `Vendor Mismatch`.
- If terminal or tool output is clipped, truncated, or only partially visible, treat verification as incomplete. Re-open the saved files directly, inspect smaller chunks if needed, or run explicit validation commands until the relevant content is fully checked.

- Treat any reconciliation gap as a blocker: if a coverage check, "not flagged pages" list, parsed-page count, or per-page audit reveals pages that were omitted, unexpectedly absent, or not fully explained, do **not** finalize. Fix the cause, regenerate `/root/fraud_report.json`, and rerun full verification until every page is explicitly reconciled.
- When reading `/root/fraud_report.json` for final checks, treat any truncated display, preview, or mid-record cutoff as a failed verification. Re-open the file in smaller chunks or parse it in Python and compute counts/pages from the parsed data before stating totals or naming specific flagged invoices.
- Verify the saved artifact directly with a full-file programmatic check, not a prefix/sample read: load `/root/fraud_report.json`, confirm it parses successfully, confirm the top-level value is an array, and validate every record's exact key set and allowed `reason` value.
- Do not treat failed commands, partial diagnostics, `head`, a single `grep`, or one-category spot checks as verification of the whole report. Replace them with a working full-report check and complete the validation before concluding.
- After any debug edit, instrumentation change, schema fix, extraction change, or edge-case investigation, regenerate the report and rerun verification on both the affected cases and the final saved file.
- Treat any contradiction discovered during verification as a blocking failure of the current report, not a minor note. Trace it back to the extraction or classification logic, repair the code, regenerate the report, and only then continue validation.
- After **any** edit to parsing or classification code, rerun the pipeline and then reopen `/root/fraud_report.json` from disk for fresh validation. Do not rely on checks, counts, or spot results gathered before the edit.
- If any later investigation changes extraction, vendor resolution, fuzzy-match acceptance, normalization behavior, or the interpretation of a specific invoice, you must rebuild the final report after that discovery. Analysis-only findings do not count unless they are propagated into the saved JSON and re-verified there.
- If a preferred verification tool is unavailable, switch to another method immediately and complete the check rather than skipping it.
- Keep intermediate scripts, extracted samples, analysis code, and debugging artifacts until verification is complete; delete temporary files only after all checks pass.
- Keep the exact producing script on disk until the final report is accepted. Do not delete or overwrite it after exploratory checks; you may need to inspect, repair, rerun, and compare it when validation exposes contradictions.

- Do a last consistency check between the saved JSON and the final response: any mentioned flagged-invoice count, reason count, file status, or other aggregate must match what you just re-read from disk.

- Separate spot checks from exhaustive validation. A grep result, a few sampled pages, a sorted page-number list, or seeing that some reasons appear or do not appear is **not** enough to prove overall correctness; use programmatic checks that directly test the claimed property across the full dataset.
- If you used a script for extraction or classification, verify both the implementation and the artifact on disk before finishing: inspect the script itself or emit targeted intermediate outputs showing vendor resolution, PO lookup, and first-applicable-reason selection on representative invoices.
- Verify semantic correctness, not just file shape: compare representative saved JSON records end to end against the source PDF text and the exact matched vendor/PO rows. A structurally valid report is still wrong if extracted values are truncated, misread, or matched to the wrong vendor.
- For each sampled flagged invoice, confirm the parsed `vendor_name`, `iban`, `po_number`, and `invoice_amount` exactly match the visible invoice text before trusting the reported fraud reason.
- If any sampled fraud reason conflicts with the referenced vendor or PO data, or suggests a higher-priority contradiction than the reported reason, stop and audit vendor resolution plus downstream rule logic before finalizing.
- Explicitly review rule reachability across all five fraud criteria before finalizing. For each reason, either verify at least one supporting case in the dataset or justify with source-backed inspection why no invoice qualifies; do not assume a missing reason means the implementation is correct.
- If one expected reason never appears, investigate whether extraction, matching, joins, or control flow suppressed it before concluding the dataset simply lacks that case.
- Treat extreme outcomes as a mandatory audit trigger. If nearly all invoices are flagged, almost none are flagged, or one reason dominates, stop and inspect representative invoices from the dominant outcome plus at least one contrary case directly against the PDF, vendor table, and PO table before finalizing.
- Do not accept aggregate counts alone as evidence that reference joins worked. For a few flagged invoices, show the exact matched vendor record and PO record, or the absence of one, that justify the reported first-applicable reason.
- If using pandas, make scalar truth tests explicit. Do not write conditions that depend on the truth value of a Series or DataFrame; reduce them with an explicit scalar check such as `.any()`, `.all()`, row selection, or a concrete extracted value before branching.
- After fixing any pandas conditional, join, or filtering bug, rerun a targeted check that exercises the repaired branch and verify the resulting fraud reason on disk in `/root/fraud_report.json`; do not assume the fix is correct from a successful script run alone.

- Do not delete scripts, extracted intermediates, debug outputs, or other regeneration artifacts until verification is complete and final handoff is imminent.

- Treat any source-to-output contradiction as a blocking failure. If a saved field differs from the visible invoice text or a reported reason conflicts with the matched vendor/PO row, stop, fix extraction or matching, regenerate `/root/fraud_report.json`, and re-verify before concluding.
- For at least one sampled record per reported reason, inspect the exact canonical vendor row and PO row used by the code so the final reason is supported by the same joined records the pipeline actually used, not by a nearby sample or aggregate summary.
- If a script produced `/root/fraud_report.json`, inspect the saved script or emit rule-specific intermediate checks so there is observable evidence that the implemented logic actually performed vendor resolution, PO validation, and first-applicable-reason selection as required.
- Prefer one executable validation path for the final check: use the same saved script or a small companion script to read `/root/fraud_report.json` back from disk, verify schema and reasons mechanically, and reconcile flagged vs. unflagged pages against the parsed invoice set.
- Verify both exceptions and passes: inspect at least one clean invoice absent from `/root/fraud_report.json` and confirm it fails all five fraud criteria using the same final pipeline outputs.
- Include at least one boundary-case audit before finalizing: inspect one or more invoices from the end of the PDF/page range, especially if earlier source inspection was truncated.
- If aggregate review shows a suspicious pattern — for example nearly every invoice flagged, one reason heavily dominating, an expected reason never appearing, sampled clean pages missing from the output, or sampled suspicious pages absent for an unexpected reason — treat that as a blocking anomaly, not a note. Trace it back to extraction, vendor resolution, joins, or rule ordering; fix the cause; regenerate `/root/fraud_report.json`; and rerun full-file validation before finishing.
- If you report totals, reason breakdowns, dominant patterns, recurring vendors, specific flagged invoices, or other final summary claims, derive them from a full re-read of `/root/fraud_report.json` or another explicitly inspected artifact and keep that derivation auditable. Do not state them from a clipped preview, a few JSON entries, or memory of earlier exploratory runs.


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
## Completion Discipline

- Do not treat script execution, file existence, or a partial preview of `/root/fraud_report.json` as task completion.
- Before finishing, perform and keep visible a requirement-based validation of the saved file itself: parse the full JSON from disk, confirm it is a top-level array, verify each record has exactly the required keys, and check that reported reasons are from the allowed set.
- Validate the output against the task requirements, not just against your script's expectations: confirm only flagged invoices are included, page numbers are 1-based, missing PO values are emitted as `null`, and the first-applicable reason ordering is respected.
- If any terminal output is truncated, re-open the saved file or rerun narrower checks until the relevant evidence is visible; do not declare success from an abbreviated preview.
- Make the final success claim only after these checks have been run on the final saved `/root/fraud_report.json`.

- Re-open `/root/fraud_report.json` after generation and base final claims on that disk artifact rather than on a script success message or in-memory objects.
- Separate report generation from final correctness claims. After writing `/root/fraud_report.json`, do not state that the report satisfies priority order, exact schema, page coverage, or other task requirements until you have run explicit full-report validation for each claimed property.
- Do not conclude from file existence, a plausible-looking JSON prefix, one or two spot checks, `grep`, header-only reads, clipped table previews, `head`, or `tail`. Use those only for debugging; final claims about coverage, priority, missing-PO handling, or clean vs flagged pages must come from explicit full-dataset checks.
- Treat regeneration as a fresh artifact boundary: if you rewrite or recreate the script or `/root/fraud_report.json`, discard earlier validation results, rerun the pipeline, then re-parse the newly saved JSON from disk before making any final claim.
- Before any final response, reconcile headline claims with the most recent programmatic verification of `/root/fraud_report.json`. Use verified aggregates from the parsed full file, not previewed/sample records.
- Keep the main analysis script and any regeneration or debug artifacts until the task is fully validated and formally complete. Do not delete files you may need to inspect, rerun, or correct before final handoff.
- If the environment mandates an exact final completion string or token, output that exact string and nothing else in place of a narrative completion message.
- If you cannot show evidence of full-report validation on the final saved file, do not declare the task complete yet.

## Tips

- pdfplumber for PDF extraction
- openpyxl for Excel reading
- fuzzywuzzy or rapidfuzz for string matching

- If optional fuzzy-matching libraries are unavailable, use Python's `difflib` as a fallback rather than installing packages.
- pandas for CSV processing

- Read [references/pandas-scalar-checks.md](references/pandas-scalar-checks.md) when writing or debugging pandas-based rule logic, especially after `Series is ambiguous` errors or unexpectedly broad flagging.



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

- If you persist parsed output to a temporary file for inspection, confirm the actual serialization format before loading it later; do not assume a preview file is JSON just because it contains structured-looking text.
- Read [references/dependency-light-execution.md](references/dependency-light-execution.md) when optional libraries are missing, when inspecting saved intermediate artifacts, or when choosing a fallback matching method.

