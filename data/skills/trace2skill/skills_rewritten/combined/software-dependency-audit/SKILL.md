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

1. Read `/root/package-lock.json` for dependency tree.
1a. Before scanning, confirm the chosen offline scanner is usable in the current environment: verify the binary exists and, when applicable, that any required local vulnerability DB/cache is present so the scan can complete without network access and setup/download logs are not mistaken for finished results.
1a.ii. Also confirm the scanner supports the actual target artifact you plan to scan (for example a lockfile vs. a source directory/image) and that the chosen mode emits vulnerability results for that artifact type; do not assume any installed scanner/subcommand can audit `package-lock.json` directly.
1a.iii. If a scanner does not cleanly support scanning a single lockfile path, fall back to scanning the containing project directory/filesystem so the tool can auto-detect the lockfile/manifests; still save structured output under `/root/...` and validate it before parsing.
1a.i. Record concrete preflight evidence before scanning: capture the exact scanner command/version and the specific local DB/cache path you verified. In restricted/offline environments, use offline/cache-preserving flags only when that local cache evidence is actually present; if no usable local DB/cache exists for the chosen tool, treat that as a blocker and switch to another allowed offline-capable scanner or report the limitation rather than proceeding as if scanning succeeded.
1b. Prefer machine-readable scan output written under `/root/...` so findings can be filtered and mapped reliably into the required CSV schema.
1c. If the environment mandates a specific tool-action format, perform a protocol preflight before doing any work: confirm the exact syntax/schema for tool invocations, the exact tool name/wrapper to use on every call, and the exact required completion string.
1d. Use this default offline workflow unless the task explicitly requires another tool: verify `package-lock.json`, scanner binary, and local DB/cache exist; run one scan that writes structured JSON under `/root/...`; inspect the saved JSON schema and one real vulnerability object; then run a separate short script to filter HIGH/CRITICAL findings and write the CSV.
2. Scan for vulnerabilities using offline tools (trivy, npm audit)
2a. In restricted/offline environments, first check for a local scanner cache/database and prefer offline scan flags when cached data is available; for example, use options such as `--skip-db-update` and `--offline-scan` when supported.
2a.i. For Trivy in offline/restricted environments, prefer an explicit cache-aware invocation such as `--offline-scan --skip-db-update` and, when needed, an explicit cache directory so the run uses local vulnerability data deterministically rather than attempting network refreshes.
2a.ii. Prefer scanner modes that are lockfile-aware or project-directory aware for Node.js inputs so findings map cleanly back to installed dependencies from `package-lock.json`.
2a1. Proven pattern for restricted environments: when using Trivy with an available local DB/cache, prefer an explicit offline invocation such as `trivy fs --scanners vuln --format json --output /root/trivy_report.json --offline-scan --skip-db-update --cache-dir <local-cache> /root` (adjust target/path as needed for the task).
2b. Prefer a two-stage workflow: save a full machine-readable scan artifact (for example JSON under `/root/...`) first, then transform that saved artifact into the final CSV with a short script rather than extracting fields from terminal text.
2b.i. Keep scanning and report-shaping as separate steps: use the saved structured artifact as the single source of truth for both the HIGH/CRITICAL finding count and every CSV row; do not mix counts from terminal summaries with row data parsed from JSON.
2b1. When machine-readable JSON output is needed, configure the scanner/command to emit clean structured JSON if possible; if logs or progress lines are mixed in, redirect/suppress them or extract the JSON payload into a separate clean file before parsing.
2b1a. If the saved output starts with log prefixes such as `INFO`, banners, or progress text, treat it as contaminated capture: create a clean JSON-only artifact first, verify that artifact parses, and only then run `jq`/Python on it.
2b2. Do not call a JSON parser on a file or stdout stream until you have confirmed it contains real JSON rather than scanner log lines such as `INFO`, progress text, or banners.
2c. Before writing extraction logic, inspect the actual saved scan output structure/schema and at least one real vulnerability object so you confirm the field names/nesting you will map.
2c1. If the structured scan artifact is too large to read in one shot, switch immediately to scripted/structured inspection (`jq` or a short Python script) to verify the vulnerability object structure and extract only the key fields you need; do not rely on repeated manual chunk-reading as the main workflow.
2c2. Do not write a parser from an assumed schema or from a failed/truncated read of the scan artifact.
2d. After the scan completes, confirm the saved structured artifact exists at the exact expected path, is non-empty, readable, and valid before parsing it.
2d1. Treat scan completion as unverified until you have concrete evidence such as a successful exit status and an existing, readable, non-empty structured report at the expected path.
2d2. If the visible tool output only shows DB download, initialization, or progress logs, treat the scan as incomplete; do not state that it finished or parse the expected output file until completion is evidenced.
2d3. For JSON artifacts, explicitly verify that they parse successfully before writing or running any transformation script that depends on them; if parsing fails, treat the artifact as invalid capture and regenerate it rather than coding around the error.
2d4. Do not create or execute a parser/export script against an expected scan file until you have directly confirmed the file exists at the exact path, is non-empty, and successfully parses as real JSON or the intended structured format.
2d5. Inspect the parsed artifact long enough to confirm it actually contains vulnerability findings for dependencies (with package/advisory/severity fields) rather than only metadata, dependency inventory, or other scanner result types. Do not build the CSV from a report whose result type/scope you have not verified.
2e. Before counting or reporting findings, fully enumerate the scanner results; if output is large, page through the complete vulnerability list or parse the JSON with tools such as `jq` or Python until no entries remain.
2e.a. It is fine to first inspect a scanner-provided summary/severity breakdown to confirm whether HIGH/CRITICAL findings exist and to narrow follow-up parsing, but treat that summary only as a navigation aid. Derive the final included findings and counts from the full structured artifact, not from the summary alone.
2e.i. If the artifact is too large to inspect manually, use structured parsing to enumerate all HIGH/CRITICAL entries directly from the saved artifact instead of inferring totals from headers, grep hits, first-entry snippets, or terminal summaries.
2e.i.1. For large reports, derive the final HIGH/CRITICAL count with a parser/query over the full saved artifact and keep that query/result as the evidence for CSV row generation and reconciliation.
2e.i.2. Do not treat a header, a single vulnerability snippet, or the first grep match as evidence that the entire result set has been enumerated.
2e.ii. Do not claim a final count or write the CSV until you have concrete evidence of completeness, such as a parser-produced total from the full artifact or exhaustive chunked reads covering the entire relevant section.
2f. Do not infer missing findings from truncated snippets, partial previews, or terminal summaries.
2g. Ground every CSV row in allowed offline scanner output; do not use memory, internet lookups, hand-built GHSA↔CVE mappings, or manual version-range reasoning to fill vulnerability metadata.
2h. Keep the raw structured scan artifact as the source of truth until CSV validation is complete.
2i. In every follow-up read/parse step, reuse the exact output path produced by the scan step or script output; never substitute a descriptive label, inferred filename, or placeholder path.
2i1. Copy the exact observed absolute path from the prior step into each subsequent command or script argument. Do not paraphrase it or replace it with an inferred filename, descriptive label, or guessed location unless you have directly verified that exact path exists.
2j. Immediately after the scan command returns, check that exact expected report path directly for existence, readability, and non-zero size before attempting any parse step.
3. Filter for HIGH and CRITICAL severity only
3a. Apply the severity filter immediately after parsing the scanner results so counting, extraction, and CSV writing all operate only on in-scope HIGH/CRITICAL findings.
3b. Build a normalized intermediate list/object containing exactly `Package, Version, CVE_ID, Severity, CVSS_Score, Fixed_Version, Title, Url` before writing CSV rows; use that normalized structure as the basis for both row counting and final CSV generation.
4. Extract: Package, Version, CVE_ID, Severity, CVSS_Score, Fixed_Version, Title, Url
4a. If the scanner output does not already match the required schema, use a small normalization script to convert the structured report into the exact CSV columns with deterministic field ordering and `N/A` fallbacks instead of reshaping terminal text manually.
4a.i. Keep the transformation script focused: load the saved JSON artifact, filter only HIGH/CRITICAL findings, map directly into the required 8 CSV columns, write `/root/security_audit.csv`, then read that CSV back for validation.
4b. Apply explicit metadata fallbacks when fields are incomplete: prefer NVD v3 CVSS, then GHSA v3, then Red Hat v3, then other available scanner-provided scores; prefer advisory Title then Description-like text; prefer the primary advisory URL then a reference URL.
4c. If you create an intermediate parser/normalization script, write actual executable code, then open the saved file and verify it contains real code rather than a placeholder description before running it or relying on its output.
4c1. Verification means reading the saved script contents directly and confirming the file itself contains executable syntax implementing the intended logic (for example imports, code statements, parsing/filtering, field mapping, and file writes), not a prose note, comments-only file, TODO, or narrative summary.
4c2. Keep the transformation auditable in the log by reading back the executable script contents and the produced output artifact before claiming the CSV was generated correctly.
4d. After running any generated script, validate the produced artifact directly; do not rely on the script's stdout, claimed row count, or success banner as proof that the output is correct.
5. Write CSV to `/root/security_audit.csv`
6. If you create intermediate artifacts, keep them in allowed task directories (prefer `/root/...`), not `/tmp` or other unapproved paths.
6a. Do not delete scan artifacts, generated scripts, or intermediate reports before the task is fully finalized. Keep them until all validations pass and the required completion signal has been emitted exactly as instructed; only clean up if the task explicitly asks for cleanup after completion.
6b. Make the scan command, output path, and export script inspectable from the log so another reader can verify exactly what ran.
7. Before parsing scan output or declaring success, confirm the scanner actually finished successfully; do not treat DB-download, progress, or initialization logs as a completed scan.
7a. Verify completion with concrete evidence such as a zero exit status and a finished, readable output artifact; if you only see startup, download, or progress logs, wait, rerun, or inspect further before continuing.
7b. If an expected scan output file is missing, empty, unreadable, or contains only startup/progress output, treat that as scan failure and fix/rerun the scan instead of inferring results.
7c. DO NOT say the scan is complete just because you saw messages like `Need to update DB`, download percentages, initialization logs, or an assumed output path. Only proceed when the scan process has actually ended successfully and the saved report exists and parses as real scan output.
7d. If the scan command output shows only DB update/download progress or startup logs, stop and wait/rerun/check status; do not attempt to open or parse the expected report path yet.
7e. Do not describe a scan as finished in narration unless both completion evidence and the output artifact have been directly verified.
8. Preserve the task's requested audit scope; do not silently broaden or narrow coverage such as including or excluding dev dependencies unless the task says to.
9. Re-open `/root/security_audit.csv` before finishing and verify end-to-end by parsing the full file, not just a preview: confirm the header is exactly `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`, every row has all 8 fields populated with a real value or `N/A`, and no rows are truncated or malformed.
9.i. Treat this read-back as mandatory artifact verification: validate the saved CSV's actual contents match the requested scope and severity filter by inspecting parsed rows from the file itself, not command success, script banners, file existence alone, or a shortened display.
9a. Do not treat `cat`, `head`, a shortened tool response, clipped terminal output, or a visually truncated rendering as sufficient validation. Use a parser, full-file read, paging, or targeted row checks until every row is confirmed complete through the last byte of the file.
9a1. As a quick sanity check, inspect at least the header plus one real data row from the saved CSV after writing it, then complete the full parser-based validation; use this spot check to catch obvious column-order or extraction mistakes early, but never as a substitute for full-file validation.
9a2. If the CSV is longer than one screen, any row preview is cut off mid-field, or fewer complete rows are visible than expected, switch immediately to structured full-file validation such as `csv.DictReader`, parsed row counts, per-row field counts, and targeted reads of unseen later rows.
9b. If any displayed row appears cut off mid-field or the terminal preview ends early, assume validation is incomplete and re-parse the file programmatically before declaring success.
9c. A visibly cut-off value such as a URL ending mid-string is proof that the read was truncated, not proof that the CSV is valid. Continue with structured parsing or offset/chunked reads until the final byte is verified.
9d. Do not mention specific vulnerabilities, row counts, or claim the CSV is complete if those claims came only from script stdout, terminal summaries, or a partial/truncated file view; verify them directly from the saved CSV or the saved structured scan artifact first.
10. Reconcile the number of HIGH/CRITICAL findings with the number of CSV data rows; if counts differ or any preview is partial, inspect the source scan data and regenerate/fix the CSV before reporting completion.
10a. When validating row counts, count actual CSV data rows with a parser or another structured method that accounts for the header; do not rely on terminal previews or stdout summaries.
10a1. Reconcile counts only from the fully parsed final CSV and the fully enumerated HIGH/CRITICAL findings from the saved scan artifact; if those totals disagree or any preview was partial, treat validation as failed and regenerate/fix the CSV before finishing.
10aa. If a file read is truncated, paginated, or preview-only, treat validation as incomplete. Re-open the entire CSV with a parser and confirm every data row has all 8 populated columns or `N/A` values and that no trailing field such as `Url` is missing.
10ab. If any row appears malformed, truncated, or fewer rows are visible than expected, treat validation as failed and regenerate/fix the CSV before finishing.
10b. If you regenerate, overwrite, or post-process the CSV at any later step, repeat the full end-to-end validation on that final file version.
10c. In the final response, mention counts or specific vulnerabilities only if they were directly confirmed from the fully validated CSV or the fully inspected offline scan artifact used to build it.
10d. If any file view, terminal printout, or tool read is truncated, do not summarize from it. Re-open the file with a parser, read additional ranges/chunks, or use targeted extraction until the entire relevant content is directly verified.
10e. Once `/root/security_audit.csv` has been fully validated and any required output artifact exists, stop. Do not delete intermediate files, rerun scans, perform extra cleanup, or start new verification commands unless the task explicitly asks for that additional work.
10f. Do not delete intermediate scan artifacts or generated helper scripts before emitting the required final response. Keep them available through finalization unless the task explicitly requires cleanup.
11. Confirm `Version` is the installed version from `package-lock.json` and `CVE_ID` is a real `CVE-...` value or `N/A`.
11a. Immediately before finishing, perform a final protocol check: verify both the tool-call format actually used throughout execution and the exact required final response string match the task/environment instructions.
11a1. Confirm every prior tool call used the mandated interface, contained concrete executable commands, and referenced exact observed artifact paths; if any step used placeholder text or the wrong wrapper, correct it by rerunning that step properly before finalizing.
11a2. If an exact completion token is required, output that token verbatim and nothing else—no prose summary, no prefix/suffix, and no extra line before or after it.
11b. Finalization checklist: (1) required output file validated, (2) needed artifacts still available for inspection, (3) every tool call matched the mandated interface from the first action onward, and (4) final response is exactly the required completion string with no extra narration.
11c. If any one of those four checks is not directly evidenced, do not finalize yet; gather the missing evidence first rather than assuming compliance.
12. If the task specifies an exact completion marker or final response format, output it verbatim as the final response and nothing else.
12a. Do not append summaries, explanations, offers for follow-up work, or conversational sign-offs after the required completion marker.

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

- Parse package-lock.json to get installed versions when practical; first identify the ecosystem from the lockfile itself, and if the lockfile is too large or awkward to inspect directly, prefer scanning it with an installed offline tool and extract needed evidence from the structured scan artifact instead of forcing full manual review
- Run `trivy` or `npm audit --json` for vulnerability scanning
- In offline environments, prefer Trivy with explicit local-only flags such as `--offline-scan --skip-db-update` (and `--cache-dir` when needed) so update/setup behavior is controlled and easier to distinguish from completed scan results
- If direct lockfile scanning is awkward or unsupported, scan the project directory/filesystem instead so the scanner can auto-detect `package-lock.json` and related manifests
- Start with a quick capability preflight such as checking scanner availability/version before committing to flags or output formats
- Prefer scanner-native file output over capturing mixed stdout/stderr text
- Filter by severity: `if severity in ['HIGH', 'CRITICAL']`
- Extract CVSS from nested JSON: `cvss['nvd']['V3Score']` or `cvss['ghsa']['V3Score']`


- Resolve installed package versions from the lockfile/dependency tree, not from vulnerability metadata fields like `range` or `affectedVersions`
- Treat parsed offline tool output as the source of truth; do not infer advisory applicability or package/advisory relationships from memory or manual version-range reasoning alone
- If a field cannot be verified from allowed evidence, keep the row only if the vulnerability itself is evidenced and set the unknown field to `N/A`

- Preferred workflow: verify offline tool/cache readiness, run a lockfile-aware scan that emits structured JSON under `/root/...`, inspect the actual JSON schema briefly, use a short script to filter HIGH/CRITICAL findings and map them into the exact CSV schema, then read the CSV back for validation
- Treat that JSON artifact as the single source of truth for filtering, counting, and CSV row generation; avoid mixing terminal summaries or ad-hoc manual extraction into the reporting path.
- Keep scanning and report shaping separate: first save the raw scanner JSON (for example `/root/trivy_report.json`), then run a small dedicated script that filters HIGH/CRITICAL findings and writes `/root/security_audit.csv`.
- Before committing to a scanner, confirm it is lockfile-aware for this task and that its JSON schema includes actual vulnerability objects for Node dependencies; if not, switch tools/modes early instead of adapting downstream parsing around an unsupported scan result.
- Prefer parsing structured scanner output files over scraping human-readable console output
- Use the parsed JSON report, not terminal summaries, as the authoritative source for package/advisory rows
- When normalizing scanner results, map advisory `range` / `affectedVersions` fields to neither `Version` nor `CVE_ID`; use them only as advisory metadata if needed
- If `jq` or similar tooling is unavailable, use a short Python script to load the saved scanner JSON, inspect at least one real finding object, filter HIGH/CRITICAL findings, write the CSV, and validate it end-to-end

## Tips

- Use offline vulnerability databases when network unavailable
- Handle missing CVSS scores with 'N/A'
- Sort output by severity (CRITICAL first)


- Do not rely only on script stdout or messages such as "Found N vulnerabilities" or "wrote N vulnerabilities"; reconcile those counts against the final validated CSV
- Do not treat scanner startup, DB-download, or initialization logs as finished results
- Prefer full-file validation over `head`-style previews when checking deliverables; if terminal output truncates long Title or Url fields, use another command or a parser to inspect the remaining content
- When a required field is unavailable, preserve schema semantics and use `N/A` rather than filling it with a different kind of value

- When the environment requires an exact action protocol, substantive correctness is not enough; protocol violations still fail the task.
- For oversized JSON or scan artifacts, prefer targeted parsing against the saved file path (for example `jq` filters or a short Python script) over raw full-file reads.
- Do not treat a generated script, a tool's success banner, or a partial file preview as sufficient evidence. Read back the actual script/output artifact and verify it completely before reporting success.
- If a read is truncated or size-limited, switch immediately to structured/targeted inspection rather than summarizing from the partial preview.
- Do not claim a vulnerability count from memory, prior stdout, or a truncated preview; derive the final count from the fully parsed scan artifact and the fully parsed final CSV.

- In strict tool environments, treat interface compliance as a blocking requirement: before each tool use, ensure the call still matches the mandated schema exactly.
- Never use natural-language command placeholders in tool calls. Every logged action should be independently executable by a reviewer and should include the real command plus exact file path.
- After any long-running scanner command, verify the exact report file path exists and is non-empty before reading it; do not infer success from download percentages, startup logs, or initialization banners.
- Keep the proven artifact-first workflow: verify offline scanner/cache readiness, write a structured JSON report under `/root/...`, inspect the actual schema briefly, use a small transformation script, and validate the final CSV end-to-end.
- Python is an acceptable primary fallback for JSON inspection, transformation, and validation when shell parsers are missing or inconvenient.
- Treat the saved scanner JSON/report file as the canonical input to the CSV transform, not the console transcript.
- Keep reports and helper scripts available until the task is conclusively finished with the exact required completion signal; premature cleanup can make recovery impossible if final checks fail.