#!/usr/bin/env python3
"""
Convert Trivy JSON output to a CSV of HIGH/CRITICAL vulnerabilities.

Usage:
  python3 trivy_json_to_csv.py -i trivy_report.json -o security_audit.csv \
      --severities HIGH,CRITICAL

CSV columns (exact header required by consumers):
  Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url

Notes:
- CVSS score priority: NVD V3 > GHSA V3 > RedHat V3, fallback to NVD V2, else 'N/A'.
- De-duplicates by (Package, CVE_ID).
- Safe defaults for missing fields.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

HEADER = [
    "Package",
    "Version",
    "CVE_ID",
    "Severity",
    "CVSS_Score",
    "Fixed_Version",
    "Title",
    "Url",
]

SEVERITY_DEFAULT = ("HIGH", "CRITICAL")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Trivy JSON to CSV (HIGH/CRITICAL)")
    p.add_argument("-i", "--input", required=True, help="Path to Trivy JSON report")
    p.add_argument("-o", "--output", required=True, help="Path to CSV output")
    p.add_argument(
        "--severities",
        default=",".join(SEVERITY_DEFAULT),
        help="Comma-separated severities to include (default: HIGH,CRITICAL)",
    )
    return p.parse_args()


def _to_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _norm_severity(s: Any) -> str:
    return (s or "").strip().upper()


def _compress_ws(s: str) -> str:
    return " ".join((s or "").split())


def _get_first_url(vuln: Dict[str, Any]) -> str:
    url = vuln.get("PrimaryURL")
    if url:
        return url
    refs = vuln.get("References")
    if isinstance(refs, list) and refs:
        return refs[0]
    return "N/A"


def _get_cvss_score(vuln: Dict[str, Any]) -> Any:
    cvss = vuln.get("CVSS")
    if not isinstance(cvss, dict):
        return "N/A"

    # Support both lower/upper keys just in case
    def get_source(d: Dict[str, Any], k: str) -> Dict[str, Any]:
        if not isinstance(d, dict):
            return {}
        if k in d:
            return d[k] or {}
        # try uppercase variant
        return d.get(k.upper(), {}) or {}

    for source in ("nvd", "ghsa", "redhat"):
        entry = get_source(cvss, source)
        if isinstance(entry, dict):
            v3 = entry.get("V3Score")
            if isinstance(v3, (int, float)) and not math.isnan(v3):
                return v3
    # Fallback to NVD V2
    nvd = get_source(cvss, "nvd")
    if isinstance(nvd, dict):
        v2 = nvd.get("V2Score")
        if isinstance(v2, (int, float)) and not math.isnan(v2):
            return v2
    return "N/A"


def _iter_results(data: Any) -> Iterable[Dict[str, Any]]:
    # Trivy JSON is typically a dict with Results; sometimes tools wrap differently.
    if isinstance(data, dict):
        for res in _to_list(data.get("Results")):
            if isinstance(res, dict):
                yield res
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for res in _to_list(item.get("Results")):
                    if isinstance(res, dict):
                        yield res


def _row_from_vuln(vuln: Dict[str, Any]) -> Dict[str, Any]:
    title = vuln.get("Title") or vuln.get("Description") or "No description"
    return {
        "Package": vuln.get("PkgName") or vuln.get("PkgID") or "Unknown",
        "Version": vuln.get("InstalledVersion") or "Unknown",
        "CVE_ID": vuln.get("VulnerabilityID") or "N/A",
        "Severity": _norm_severity(vuln.get("Severity")) or "UNKNOWN",
        "CVSS_Score": _get_cvss_score(vuln),
        "Fixed_Version": vuln.get("FixedVersion") or "N/A",
        "Title": _compress_ws(title),
        "Url": _get_first_url(vuln),
    }


def main() -> int:
    args = parse_args()
    severities = {s.strip().upper() for s in (args.severities or "").split(",") if s.strip()}
    if not severities:
        severities = set(SEVERITY_DEFAULT)

    in_path = Path(args.input)
    out_path = Path(args.output)

    try:
        with in_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: failed to read JSON from {in_path}: {e}", file=sys.stderr)
        return 2

    rows: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str]] = set()

    for result in _iter_results(data):
        vulns = result.get("Vulnerabilities") or []
        if not isinstance(vulns, list):
            continue
        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue
            sev = _norm_severity(vuln.get("Severity"))
            if sev not in severities:
                continue
            row = _row_from_vuln(vuln)
            key = (row["Package"], row["CVE_ID"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)

    try:
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            w.writerows(rows)
    except Exception as e:
        print(f"ERROR: failed to write CSV to {out_path}: {e}", file=sys.stderr)
        return 3

    print(f"Wrote {len(rows)} records to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
