#!/usr/bin/env python3
"""
Suricata offline test helper: validate rules, run on pcaps, and summarize alerts.

Requirements:
- Suricata available in PATH
- Python 3.7+

Examples:
  python scripts/suri_offline_test.py \
      --config suricata.yaml --rules local.rules --pcap pos.pcap --sid 1234567

  python scripts/suri_offline_test.py \
      --config suricata.yaml --rules local.rules \
      --pcap pos.pcap --pcap neg.pcap --sid 1234567 \
      --runmode single --set stream.memcap=32mb --set defrag.memcap=8mb
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import List, Tuple


def run(cmd: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return proc.returncode, out, err


def validate_rules(config: str, rules: str) -> None:
    code, out, err = run(["suricata", "-T", "-c", config, "-S", rules])
    if code != 0:
        sys.stderr.write("[ERROR] Suricata validation failed.\n")
        sys.stderr.write(err or out)
        sys.exit(code)
    sys.stdout.write("[OK] Suricata configuration and rules validated.\n")


def run_offline(config: str, rules: str, pcap: str, runmode: str, sets: List[str]) -> Tuple[str, int, int]:
    outdir = tempfile.mkdtemp(prefix="suri_test_")
    try:
        cmd = ["suricata", "-c", config, "-S", rules, "-r", pcap, "-l", outdir]
        if runmode:
            cmd.extend(["--runmode", runmode])
        for s in sets:
            cmd.extend(["--set", s])
        code, out, err = run(cmd)
        if code != 0:
            sys.stderr.write(f"[ERROR] Suricata run failed for {pcap}.\n")
            sys.stderr.write(err or out)
            return outdir, -1, -1
        eve = os.path.join(outdir, "eve.json")
        total_alerts = 0
        sid_alerts = 0
        return outdir, total_alerts, sid_alerts
    except Exception as e:
        sys.stderr.write(f"[ERROR] Exception during Suricata run: {e}\n")
        return outdir, -1, -1


def summarize_alerts(eve_path: str, sid: str = None) -> Tuple[int, int]:
    total = 0
    sid_total = 0
    if not os.path.isfile(eve_path):
        return total, sid_total
    with open(eve_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("event_type") == "alert":
                total += 1
                if sid is not None:
                    a = obj.get("alert", {})
                    if str(a.get("sid")) == str(sid):
                        sid_total += 1
    return total, sid_total


def main():
    parser = argparse.ArgumentParser(description="Suricata offline test helper")
    parser.add_argument("--config", required=True, help="Path to suricata.yaml")
    parser.add_argument("--rules", required=True, help="Path to Suricata rules file (e.g., local.rules)")
    parser.add_argument("--pcap", action="append", required=True, help="Path to pcap (repeat for multiple)")
    parser.add_argument("--sid", help="Alert SID to filter (optional)")
    parser.add_argument("--runmode", help="Suricata runmode (e.g., single, workers)")
    parser.add_argument("--set", dest="sets", action="append", default=[], help="Runtime override key=value (repeatable)")
    args = parser.parse_args()

    # Validate rules first
    validate_rules(args.config, args.rules)

    overall_rc = 0
    for pcap in args.pcap:
        outdir, total_alerts, sid_alerts = run_offline(args.config, args.rules, pcap, args.runmode or "", args.sets)
        if total_alerts == -1:
            overall_rc = 1
            continue
        eve = os.path.join(outdir, "eve.json")
        total_alerts, sid_alerts = summarize_alerts(eve, args.sid)
        summary = {
            "pcap": pcap,
            "output_dir": outdir,
            "alerts_total": total_alerts,
            "alerts_for_sid": sid_alerts if args.sid else None,
        }
        print(json.dumps(summary))
    sys.exit(overall_rc)


if __name__ == "__main__":
    main()
