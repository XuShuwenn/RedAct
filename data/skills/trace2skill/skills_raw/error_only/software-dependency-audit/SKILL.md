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
2. Scan for vulnerabilities using offline tools (trivy, npm audit)
2a. Before counting or reporting findings, fully enumerate the scanner results; if output is large, page through the complete vulnerability list or parse the JSON with tools such as `jq` until no entries remain.
2b. Do not infer missing findings from truncated snippets or partial previews.
2c. Ground every CSV row in allowed offline scanner output; do not use memory or internet lookups to fill vulnerability metadata.
3. Filter for HIGH and CRITICAL severity only
4. Extract: Package, Version, CVE_ID, Severity, CVSS_Score, Fixed_Version, Title, Url
5. Write CSV to `/root/security_audit.csv`
6. If you create intermediate artifacts, keep them in allowed task directories (prefer `/root/...`), not `/tmp` or other unapproved paths.
7. Before parsing scan output or declaring success, confirm the scanner actually finished successfully; do not treat DB-download, progress, or initialization logs as a completed scan.
8. Preserve the task's requested audit scope; do not silently broaden or narrow coverage such as including or excluding dev dependencies unless the task says to.
9. Re-open `/root/security_audit.csv` before finishing and verify end-to-end: the header is exactly `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`, every row has all 8 fields populated with a real value or `N/A`, and no rows are truncated or malformed.
10. Reconcile the number of HIGH/CRITICAL findings with the number of CSV data rows; if counts differ or any preview is partial, inspect the source scan data and regenerate/fix the CSV before reporting completion.
11. Confirm `Version` is the installed version from `package-lock.json` and `CVE_ID` is a real `CVE-...` value or `N/A`.
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

## Common Patterns

- Parse package-lock.json to get installed versions
- Run `trivy` or `npm audit --json` for vulnerability scanning
- Filter by severity: `if severity in ['HIGH', 'CRITICAL']`
- Extract CVSS from nested JSON: `cvss['nvd']['V3Score']` or `cvss['ghsa']['V3Score']`


- Resolve installed package versions from the lockfile/dependency tree, not from vulnerability metadata fields like `range` or `affectedVersions`
- Treat parsed offline tool output as the source of truth; do not infer advisory applicability or package/advisory relationships from memory or manual version-range reasoning alone
- If a field cannot be verified from allowed evidence, keep the row only if the vulnerability itself is evidenced and set the unknown field to `N/A`

## Tips

- Use offline vulnerability databases when network unavailable
- Handle missing CVSS scores with 'N/A'
- Sort output by severity (CRITICAL first)


- Do not rely only on script stdout or messages such as "Found N vulnerabilities" or "wrote N vulnerabilities"; reconcile those counts against the final validated CSV
- Do not treat scanner startup, DB-download, or initialization logs as finished results
- Prefer full-file validation over `head`-style previews when checking deliverables; if terminal output truncates long Title or Url fields, use another command or a parser to inspect the remaining content
- When a required field is unavailable, preserve schema semantics and use `N/A` rather than filling it with a different kind of value