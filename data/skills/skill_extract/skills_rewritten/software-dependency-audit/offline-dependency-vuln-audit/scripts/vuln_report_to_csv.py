#!/usr/bin/env python3
"""
Convert a dependency vulnerability scan JSON report into a CSV containing only HIGH/CRITICAL issues.

Extracted columns:
  Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url

Usage:
  python3 vuln_report_to_csv.py --input scan.json --output security_audit.csv \
      [--severities HIGH,CRITICAL] [--allow-non-cve]

Notes:
- Designed to parse common scanner JSON formats (e.g., Trivy-like), where:
  - Top-level has Results[], each with Vulnerabilities[] entries, or
  - Direct list/dict of vulnerabilities.
- CVSS score priority: NVD > GHSA > RedHat, prefer v3 base score.
- Deduplicates by (Package, Version, CVE_ID).
"""

import argparse
import csv
import json
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


def load_json(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def iter_vulnerabilities(data: Any) -> Iterable[Dict[str, Any]]:
    # Try common structures: {'Results': [{'Vulnerabilities': [...]}, ...]}
    if isinstance(data, dict):
        if 'Results' in data and isinstance(data['Results'], list):
            for result in data['Results']:
                vulns = result.get('Vulnerabilities') or result.get('vulnerabilities')
                if isinstance(vulns, list):
                    for v in vulns:
                        if isinstance(v, dict):
                            yield v
        elif 'Vulnerabilities' in data and isinstance(data['Vulnerabilities'], list):
            for v in data['Vulnerabilities']:
                if isinstance(v, dict):
                    yield v
        else:
            # Fallback: if dict resembles a single vulnerability entry
            if any(k in data for k in ('VulnerabilityID', 'PkgName', 'InstalledVersion')):
                yield data
    elif isinstance(data, list):
        # Direct list may be vulnerabilities or results
        for item in data:
            if isinstance(item, dict) and 'Vulnerabilities' in item:
                vulns = item.get('Vulnerabilities')
                if isinstance(vulns, list):
                    for v in vulns:
                        if isinstance(v, dict):
                            yield v
            elif isinstance(item, dict):
                # Assume it's a vulnerability-like dict
                yield item
    # else: nothing to yield


_CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)


def extract_cve_id(v: Dict[str, Any]) -> Optional[str]:
    # Common key names
    cve = v.get('VulnerabilityID') or v.get('CVE') or v.get('cve')
    if isinstance(cve, str) and _CVE_PATTERN.search(cve):
        return _CVE_PATTERN.search(cve).group(0).upper()
    # Some scanners put CVE IDs in aliases or identifiers lists
    aliases = v.get('Aliases') or v.get('aliases') or v.get('Identifiers') or v.get('identifiers')
    if isinstance(aliases, list):
        for item in aliases:
            if isinstance(item, str):
                m = _CVE_PATTERN.search(item)
                if m:
                    return m.group(0).upper()
    # Try references/URLs text
    for key in ('PrimaryURL', 'primaryURL', 'URL', 'url'):
        val = v.get(key)
        if isinstance(val, str):
            m = _CVE_PATTERN.search(val)
            if m:
                return m.group(0).upper()
    return None


def extract_pkg(v: Dict[str, Any]) -> str:
    return (
        v.get('PkgName') or v.get('PackageName') or v.get('packageName') or
        v.get('Package') or v.get('package') or v.get('Name') or v.get('name') or ''
    )


def extract_version(v: Dict[str, Any]) -> str:
    return (
        v.get('InstalledVersion') or v.get('Version') or v.get('version') or v.get('Installed') or ''
    )


def extract_severity(v: Dict[str, Any]) -> str:
    sev = v.get('Severity') or v.get('severity') or ''
    if isinstance(sev, str):
        return sev.strip().upper()
    return ''


def _score_from_cvss_obj(obj: Any) -> Optional[float]:
    if not isinstance(obj, dict):
        return None
    for k in ('V3Score', 'v3Score', 'V31Score', 'V30Score', 'BaseScore', 'baseScore', 'Score', 'score'):
        val = obj.get(k)
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                return float(val)
            except ValueError:
                continue
    return None


def extract_cvss_score(v: Dict[str, Any]) -> Optional[float]:
    # Priority order: NVD > GHSA > RedHat
    priorities = ['nvd', 'ghsa', 'redhat']
    cvss = v.get('CVSS') or v.get('cvss')

    # Case 1: mapping of source -> score object
    if isinstance(cvss, dict):
        # Some scanners use lowercase keys; handle case-insensitively
        lower = {k.lower(): val for k, val in cvss.items()}
        for source in priorities:
            if source in lower:
                score = _score_from_cvss_obj(lower[source])
                if score is not None:
                    return score
        # Try any nested object with a usable score
        for val in lower.values():
            score = _score_from_cvss_obj(val)
            if score is not None:
                return score

    # Case 2: list of entries with source names
    if isinstance(cvss, list):
        # Build map by source
        by_source: Dict[str, Any] = {}
        for entry in cvss:
            if isinstance(entry, dict):
                src = (entry.get('Source') or entry.get('source') or '')
                by_source[src.lower()] = entry
        for source in priorities:
            if source in by_source:
                score = _score_from_cvss_obj(by_source[source])
                if score is not None:
                    return score
        # Try any list entry
        for entry in cvss:
            score = _score_from_cvss_obj(entry)
            if score is not None:
                return score

    # Fallback: flat fields
    for key in ('CVSSScore', 'cvssScore', 'CVSS', 'cvss'):
        val = v.get(key)
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                return float(val)
            except ValueError:
                continue
    return None


def extract_fixed_version(v: Dict[str, Any]) -> str:
    # Common keys
    candidates = [
        v.get('FixedVersion'), v.get('fixedVersion'),
        v.get('FixedVersions'), v.get('fixedVersions'),
        v.get('PatchedVersions'), v.get('patchedVersions'),
        v.get('FirstPatchedVersion'), v.get('firstPatchedVersion'),
    ]
    values: List[str] = []
    for c in candidates:
        if isinstance(c, str) and c.strip():
            values.append(c.strip())
        elif isinstance(c, list):
            for item in c:
                if isinstance(item, str) and item.strip():
                    values.append(item.strip())
        elif isinstance(c, dict):
            # Some advisories use {"identifier": "x.y.z"}
            for key in ('Identifier', 'identifier', 'Version', 'version'):
                val = c.get(key)
                if isinstance(val, str) and val.strip():
                    values.append(val.strip())
    # Deduplicate while preserving order
    seen: Set[str] = set()
    uniq = [x for x in values if not (x in seen or seen.add(x))]
    return "; ".join(uniq) if uniq else 'N/A'


def extract_title(v: Dict[str, Any]) -> str:
    title = v.get('Title') or v.get('title')
    if isinstance(title, str) and title.strip():
        return title.strip()
    desc = v.get('Description') or v.get('description') or ''
    if isinstance(desc, str):
        # Use first sentence-ish fallback
        short = desc.strip().split('\n', 1)[0]
        return short[:300]
    return ''


def extract_url(v: Dict[str, Any]) -> str:
    for key in ('PrimaryURL', 'primaryURL', 'URL', 'url'):
        val = v.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    refs = v.get('References') or v.get('references') or v.get('URLs') or v.get('urls')
    if isinstance(refs, list):
        for r in refs:
            if isinstance(r, str) and r.strip():
                return r.strip()
    return ''


def normalize_score(score: Optional[float]) -> str:
    if score is None:
        return 'N/A'
    # Format with up to one decimal if integer-ish
    return f"{score:.1f}" if abs(score - round(score, 1)) < 1e-9 else str(score)


def main() -> None:
    ap = argparse.ArgumentParser(description='Convert vulnerability scan JSON to CSV (HIGH/CRITICAL only).')
    ap.add_argument('--input', required=True, help='Path to scanner JSON report')
    ap.add_argument('--output', required=True, help='Path to output CSV file')
    ap.add_argument('--severities', default='HIGH,CRITICAL', help='Comma-separated severities to include')
    ap.add_argument('--allow-non-cve', action='store_true', help='Include entries lacking a CVE ID (CVE_ID will be empty)')
    args = ap.parse_args()

    wanted = {s.strip().upper() for s in args.severities.split(',') if s.strip()}
    data = load_json(args.input)

    rows: List[List[str]] = []
    seen_keys: Set[Tuple[str, str, str]] = set()

    for v in iter_vulnerabilities(data):
        severity = extract_severity(v)
        if severity not in wanted:
            continue

        pkg = extract_pkg(v)
        ver = extract_version(v)
        cve = extract_cve_id(v)

        if not args.allow_non_cve and not cve:
            continue

        cve_id = cve or ''
        key = (pkg, ver, cve_id)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        score = normalize_score(extract_cvss_score(v))
        fixed = extract_fixed_version(v)
        title = extract_title(v)
        url = extract_url(v)

        rows.append([pkg, ver, cve_id, severity, score, fixed, title, url])

    # Write CSV
    header = ['Package', 'Version', 'CVE_ID', 'Severity', 'CVSS_Score', 'Fixed_Version', 'Title', 'Url']
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for r in rows:
            writer.writerow(r)

    # Basic stderr summary for verification purposes
    print(f"Wrote {len(rows)} rows to {args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
