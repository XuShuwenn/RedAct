---
name: software-dependency-audit
description: "Perform security audits on package-lock.json files to identify and report HIGH/CRITICAL severity vulnerabilities in CSV format."
---

# Software Dependency Audit

## When to Use

- Audit Node.js package-lock.json for security vulnerabilities
- Generate CSV security audit reports
- Filter vulnerabilities by severity (HIGH/CRITICAL only)
- Extract CVE information and CVSS scores


## Execution Protocol

## Execution Protocol

- Follow any task- or system-specific execution/tool-use protocol exactly when provided.
- Use the exact required tool invocation or response format; do not substitute alternate wrappers, schemas, or natural-language closings when an exact protocol is required.
- If the task requires an exact completion token or final line, output that exact string verbatim as the final response.

## Key Steps

1. Read `/root/package-lock.json` for dependency tree
1a. Before scanning, confirm the chosen offline scanner is usable in the current environment: verify the binary exists and, when applicable, that any required local vulnerability DB/cache is present so the scan can complete without network access and setup/download logs are not mistaken for finished results.
1b. Prefer machine-readable scan output written under `/root/...` so findings can be filtered and mapped reliably into the required CSV schema.
2. Scan for vulnerabilities using offline tools (trivy, npm audit)
2a. In restricted/offline environments, first check for a local scanner cache/database and prefer offline scan flags when cached data is available; for example, use options such as `--skip-db-update` and `--offline-scan` when supported.
2b. Prefer a two-stage workflow: save a full machine-readable scan artifact (for example JSON under `/root/...`) first, then transform that saved artifact into the final CSV with a short script rather than extracting fields from terminal text.
2c. Before writing extraction logic, inspect the actual saved scan output structure/schema and confirm the field names/nesting you will map.
2d. After the scan completes, confirm the saved structured artifact is valid, non-empty, and readable before parsing it.
2e. Before counting or reporting findings, fully enumerate the scanner results; if output is large, page through the complete vulnerability list or parse the JSON with tools such as `jq` or Python until no entries remain.
2f. Do not infer missing findings from truncated snippets, partial previews, or terminal summaries.
2g. Ground every CSV row in allowed offline scanner output; do not use memory, internet lookups, hand-built GHSA↔CVE mappings, or manual version-range reasoning to fill vulnerability metadata.
2h. Keep the raw structured scan artifact as the source of truth until CSV validation is complete.
3. Filter for HIGH and CRITICAL severity only
3a. Apply the severity filter immediately after parsing the scanner results so counting, extraction, and CSV writing all operate only on in-scope HIGH/CRITICAL findings.
4. Extract: Package, Version, CVE_ID, Severity, CVSS_Score, Fixed_Version, Title, Url
4a. If the scanner output does not already match the required schema, use a small normalization script to convert the structured report into the exact CSV columns with deterministic field ordering and `N/A` fallbacks instead of reshaping terminal text manually.
4b. Apply explicit metadata fallbacks when fields are incomplete: prefer NVD v3 CVSS, then GHSA v3, then Red Hat v3, then other available scanner-provided scores; prefer advisory Title then Description-like text; prefer the primary advisory URL then a reference URL.
5. Write CSV to `/root/security_audit.csv`
6. If you create intermediate artifacts, keep them in allowed task directories (prefer `/root/...`), not `/tmp` or other unapproved paths.
7. Before parsing scan output or declaring success, confirm the scanner actually finished successfully; do not treat DB-download, progress, or initialization logs as a completed scan.
7a. Verify completion with concrete evidence such as a zero exit status and a finished, readable output artifact; if you only see startup, download, or progress logs, wait, rerun, or inspect further before continuing.
7b. If an expected scan output file is missing, empty, unreadable, or contains only startup/progress output, treat that as scan failure and fix/rerun the scan instead of inferring results.
8. Preserve the task's requested audit scope; do not silently broaden or narrow coverage such as including or excluding dev dependencies unless the task says to.
9. Re-open `/root/security_audit.csv` before finishing and verify end-to-end by parsing the full file, not just a preview: confirm the header is exactly `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`, every row has all 8 fields populated with a real value or `N/A`, and no rows are truncated or malformed.
10. Reconcile the number of HIGH/CRITICAL findings with the number of CSV data rows; if counts differ or any preview is partial, inspect the source scan data and regenerate/fix the CSV before reporting completion.
10a. When validating row counts, count actual CSV data rows with a parser or another structured method that accounts for the header; do not rely on terminal previews or stdout summaries.
10b. If you regenerate, overwrite, or post-process the CSV at any later step, repeat the full end-to-end validation on that final file version.
10c. In the final response, mention counts or specific vulnerabilities only if they were directly confirmed from the fully validated CSV or the fully inspected offline scan artifact used to build it.
11. Confirm `Version` is the installed version from `package-lock.json` and `CVE_ID` is a real `CVE-...` value or `N/A`.
11a. Immediately before finishing, perform a final protocol check: verify both the tool-call format used during execution and the exact required final response string match the task/environment instructions.
12. If the task specifies an exact completion marker or final response format, output it verbatim as the final response.

## CSV Output Format

Columns: `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`

- Use `N/A` for unavailable fields (especially Fixed_Version and CVSS_Score)
- Use csv.DictWriter with fieldnames parameter
- Set `newline=''` and `encoding='utf-8'`


- After writing, read the CSV back with `csv.DictReader` (or equivalent) and confirm each row contains exactly these keys: `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`
- `Version` means the resolved installed package version from `package-lock.json`; do not use advisory ranges such as `<7.23.2` or `0.8.0 - 0.8.3`
- `CVE_ID` must contain a real `CVE-...` identifier only; if the advisory has only a GHSA or other identifier, write `N/A`
- Keep GHSA identifiers or advisory links in `Title` or `Url`; do not substitute them into `CVE_ID`
- Treat any truncated line, missing column, malformed quoting, incomplete last row, or mismatch between expected findings and CSV row count as a blocking error that must be fixed before finishing

- Inspect at least one real vulnerability object from the scanner output before coding the export so you map actual keys rather than assumed names
- Use an explicit source mapping for each CSV column before writing rows: package/version from installed dependency data and the scan finding, CVE from a real `CVE-...` identifier only, severity from the scanner finding, fixed version from the scanner/advisory field, title from the advisory title (or description/summary if no title is present), and URL from an advisory/reference link
- When multiple CVSS sources exist, use a deterministic priority order: prefer NVD v3, then GHSA v3, then Red Hat v3, then NVD v2; otherwise write `N/A`
- When scanner metadata is incomplete, use deterministic fallbacks from other scanner-provided fields or references before using `N/A`; never guess from memory or online sources

## Common Patterns

- Parse package-lock.json to get installed versions
- Run `trivy` or `npm audit --json` for vulnerability scanning
- Filter by severity: `if severity in ['HIGH', 'CRITICAL']`
- Extract CVSS from nested JSON: `cvss['nvd']['V3Score']` or `cvss['ghsa']['V3Score']`


- Resolve installed package versions from the lockfile/dependency tree, not from vulnerability metadata fields like `range` or `affectedVersions`
- Treat parsed offline tool output as the source of truth; do not infer advisory applicability or package/advisory relationships from memory or manual version-range reasoning alone
- If a field cannot be verified from allowed evidence, keep the row only if the vulnerability itself is evidenced and set the unknown field to `N/A`

- Preferred workflow: verify offline tool/cache readiness, run a lockfile-aware scan that emits structured JSON under `/root/...`, inspect the actual JSON schema briefly, use a short script to filter HIGH/CRITICAL findings and map them into the exact CSV schema, then read the CSV back for validation
- Prefer parsing structured scanner output files over scraping human-readable console output
- Use the parsed JSON report, not terminal summaries, as the authoritative source for package/advisory rows
- When normalizing scanner results, map advisory `range` / `affectedVersions` fields to neither `Version` nor `CVE_ID`; use them only as advisory metadata if needed
- If `jq` or similar tooling is unavailable, use a short Python script to load the scanner JSON, filter HIGH/CRITICAL findings, write the CSV, and validate it end-to-end

## Tips

- Use offline vulnerability databases when network unavailable
- Handle missing CVSS scores with 'N/A'
- Sort output by severity (CRITICAL first)


- Do not rely only on script stdout or messages such as "Found N vulnerabilities" or "wrote N vulnerabilities"; reconcile those counts against the final validated CSV
- Do not treat scanner startup, DB-download, or initialization logs as finished results
- Prefer full-file validation over `head`-style previews when checking deliverables; if terminal output truncates long Title or Url fields, use another command or a parser to inspect the remaining content
- When a required field is unavailable, preserve schema semantics and use `N/A` rather than filling it with a different kind of value