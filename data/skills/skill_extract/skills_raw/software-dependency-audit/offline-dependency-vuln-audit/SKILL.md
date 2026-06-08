---
name: offline-dependency-vuln-audit
description: "Scan dependency lockfiles with Trivy in offline mode and export a CSV of HIGH/CRITICAL vulnerabilities with CVSS scores."
---

# Offline Dependency Vulnerability Audit

Audit third-party dependencies from lockfiles or project directories using Trivy in offline mode. Filter results to HIGH and CRITICAL severities, extract CVSS scores with source priority, and export a CSV report with consistent columns.

## When to Use

Use this skill when you need to:
- audit a dependency lockfile or project tree without network access
- focus on HIGH and CRITICAL vulnerabilities
- produce a CSV summary containing package, version, CVE, severity, CVSS, fixed version, title, and reference URL

Works well for lockfiles such as npm package-lock.json, yarn.lock, poetry.lock, Pipfile.lock, etc., when Trivy can scan the filesystem manifest.

## Core Workflow

1. Verify prerequisites
   - Ensure Trivy is installed: `trivy --version`
   - Confirm an offline database exists (typical cache path): look for a `trivy.db` under `~/.cache/trivy/` or the configured `--cache-dir`.
   - If no offline DB is present, either use a pre-seeded cache or request permission to update the DB online before running offline.

2. Run the offline scan
   - Run Trivy in filesystem mode against the lockfile or project folder:
     - Example (replace <input_path>):
       - `trivy fs <input_path> --format json --output <trivy_report.json> --scanners vuln --skip-db-update --offline-scan --cache-dir <cache_dir>`
   - Notes:
     - Using `--skip-db-update` and `--offline-scan` prevents network calls.
     - You may scan the entire project dir or a specific lockfile. For large projects, scanning just the lockfile is often faster.
     - You can omit Trivy's `--severity` filter and do filtering in the parsing step to keep full detail.

3. Parse and filter results
   - Use the provided helper script to transform Trivy JSON into a CSV with required columns.
   - Filtering: include only HIGH and CRITICAL severities.
   - CVSS score extraction priority: NVD V3 > GHSA V3 > RedHat V3; fallback to NVD V2 if V3 is unavailable; otherwise "N/A".

4. Export CSV
   - Write the report with the exact header:
     - `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`
   - Ensure values are normalized and missing data is represented as `N/A`.

## Verification

After generating the CSV:
- File checks:
  - The CSV exists and starts with the exact header line.
  - All rows have exactly 8 fields.
- Content checks:
  - Severity is only HIGH or CRITICAL (uppercase).
  - CVSS_Score is numeric when available; otherwise `N/A`.
  - No duplicate entries for the same (Package, CVE_ID) pair.
  - Title is a single line (no embedded newlines) and non-empty (or `No description`).
  - Url is present; if `PrimaryURL` wasn’t available, a fallback reference is used or `N/A`.

## Common Pitfalls and How to Avoid Them

- Missing offline DB
  - Symptom: Trivy attempts to update or fails in offline mode.
  - Avoidance: Use `--skip-db-update --offline-scan` and point `--cache-dir` to a seeded cache. Verify presence of the DB before scanning.

- Scanning the wrong path
  - Symptom: Empty results or irrelevant findings.
  - Avoidance: Confirm the correct lockfile or project directory path and re-run.

- Relying on a single CVSS source
  - Symptom: `N/A` scores even when other sources have data.
  - Avoidance: Use source priority (NVD > GHSA > RedHat) and fallback to V2 when V3 is missing.

- Filtering only at scan time
  - Symptom: Inconsistent filtering or missed items due to tool-specific severity behavior.
  - Avoidance: Prefer filtering in the parsing step. If you filter during scan, still verify in parsing.

- Duplicates and incomplete fields
  - Symptom: Multiple identical (Package, CVE) rows or missing Version/Title.
  - Avoidance: De-duplicate by (Package, CVE_ID). Default missing fields to `N/A` and compress Title whitespace.

- Using incompatible tools for the format
  - Symptom: Parsing errors or mismatched fields (e.g., using `npm audit` JSON structure with Trivy expectations).
  - Avoidance: Keep scanner and parser aligned (Trivy JSON → this parser). If using another tool, adapt parsing accordingly.

## Optional Script Usage

A helper script is included to parse Trivy JSON and produce the CSV.

- Example:
  - `python3 scripts/trivy_json_to_csv.py -i trivy_report.json -o security_audit.csv --severities HIGH,CRITICAL`

- Script behavior:
  - Reads Trivy JSON (object or list formats) and iterates all results.
  - Filters vulnerabilities by the provided severities (default HIGH,CRITICAL).
  - Extracts fields and resolves CVSS score with fallback logic.
  - De-duplicates by (Package, CVE_ID) and writes the CSV with the required header.

## Success Criteria

- The CSV exists and contains only HIGH/CRITICAL entries with the exact header:
  - `Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`
- CVSS scores reflect NVD/ GHSA/ RedHat with correct priority and V2 fallback.
- All fields are present; missing values are `N/A`.
- The process completes without network access when an offline DB is available.
