---
name: offline-dependency-vuln-audit
description: "Audit dependency lockfiles with an offline scanner, filter HIGH/CRITICAL issues, and generate a clean CSV report."
---

# Offline Dependency Vulnerability Audit

Use this skill to scan a project's dependency lockfile with an offline vulnerability database, extract only HIGH and CRITICAL issues, and produce a CSV report with standardized fields.

## When to Use

Activate this skill when you need to:
- Audit third-party dependencies from a lockfile without internet access
- Report only HIGH and CRITICAL vulnerabilities
- Produce a CSV with fields: Package, Version, CVE_ID, Severity, CVSS_Score, Fixed_Version, Title, Url

## Core Workflow

1. Identify the target and scope
   - Confirm the dependency file type (e.g., npm lockfile) and scan the lockfile (or appropriate manifest) to include transitive dependencies.
   - Ensure the scanner supports offline operation and a local vulnerability database is present.

2. Run an offline scan and save JSON output
   - Use the scanner's offline mode and include dependency scanning features.
   - Either:
     - Scan with no severity filter and filter later in parsing, or
     - Scan with a HIGH/CRITICAL severity filter and still verify severities in parsing.
   - Save the full JSON report to a stable path for deterministic parsing.

3. Parse, filter, and normalize fields
   - Process the JSON and keep only HIGH or CRITICAL severities (case-insensitive).
   - Deduplicate by the composite key (Package, Version, CVE_ID) to avoid repeated entries across targets/components.
   - Extract fields per vulnerability:
     - Package: PkgName/PackageName/etc.
     - Version: InstalledVersion/Version/etc.
     - CVE_ID: Prefer canonical CVE identifier (e.g., from VulnerabilityID). If no CVE is present, omit the entry if a CVE is strictly required.
     - Severity: Normalize to uppercase (HIGH, CRITICAL).
     - CVSS_Score: Prefer sources in priority order NVD > GHSA > RedHat; use CVSS v3 base score when available. If absent, set to "N/A".
     - Fixed_Version: Prefer FixedVersion/FirstPatchedVersion/PatchedVersions; if multiple, join; if none, set to "N/A".
     - Title: Prefer Title; fallback to a concise Description.
     - Url: Prefer PrimaryURL; fallback to the first References/URLs entry.

4. Generate the CSV
   - Write CSV with header exactly:
     - Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url
   - Ensure proper CSV quoting to handle commas and special characters in text fields.

5. Verification and cross-checks
   - Confirm the CSV file exists and begins with the exact header.
   - Recompute severity counts from the JSON to confirm only HIGH/CRITICAL entries are present.
   - Validate there are no duplicate (Package, Version, CVE_ID) rows.
   - Spot-check a few entries: CVSS score source priority applied, Fixed_Version populated or "N/A", Title/Url present.

## Verification

Use these concrete checks before finalizing:
- Structural: CSV header matches exactly and every row has 8 columns.
- Severity filter: Set of severities in CSV is a subset of {HIGH, CRITICAL}.
- Deduplication: Number of unique (Package, Version, CVE_ID) in CSV equals total rows (excluding header).
- Scores: For sampled rows, verify CVSS_Score came from the preferred source order (NVD > GHSA > RedHat) when multiple are available.
- Fixed versions: When present, they correspond to the scanner/advisory data; if not present, the field is "N/A".

## Common Pitfalls

- Scanning the wrong target: Running a repository-wide scan without focusing on the lockfile may inflate findings or miss intended scope.
- Not saving JSON: Parsing transient console output is brittle; always save structured JSON to a stable file path first.
- Duplicate counting: The same CVE can appear under multiple targets/components—deduplicate by (Package, Version, CVE_ID).
- Incorrect severity filtering: Ensure filtering applies to the vulnerability's severity, not a package-wide or vendor-specific label.
- CVSS source ambiguity: Mixing sources leads to inconsistent scores; consistently prefer NVD, then GHSA, then RedHat, falling back to "N/A" if none are present.
- Missing CVE IDs: If the report requires CVE IDs, skip entries without a CVE rather than substituting non-CVE identifiers.
- CSV formatting issues: Missing header, wrong column order, or unquoted commas in Title/Url fields cause parsing errors downstream.

## Optional Script Usage

A helper script is provided to convert a scanner JSON report into the required CSV.

- Input: JSON report from a common offline dependency scanner
- Output: CSV with the required header and fields
- Severity filter: Defaults to HIGH,CRITICAL
- CVE requirement: Enabled by default; entries without a CVE are skipped

Example:
- Run your offline scan and save JSON to a file.
- Generate the CSV:
  - python3 scripts/vuln_report_to_csv.py --input scan.json --output security_audit.csv
  - Optional flags:
    - --severities HIGH,CRITICAL
    - --allow-non-cve (include entries lacking CVE, leaving CVE_ID blank)

Success criteria: The CSV exists, uses the exact header, contains only HIGH/CRITICAL rows, and is deduplicated by (Package, Version, CVE_ID).
