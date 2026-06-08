#!/usr/bin/env python3
"""Run Suricata offline on one or more PCAPs with resource-aware defaults and
summarize alerts by SID from eve.json.

Usage:
  python3 scripts/suri_offline_runner.py \
    --config /path/to/suricata.yaml \
    --rules /path/to/local.rules \
    --pcaps /path/to/a.pcap /path/to/b.pcap \
    --outdir /tmp/suri-out \
    --runmode-single --low-mem

Options:
  --runmode-single  Use single-threaded run mode to reduce memory usage.
  --low-mem         Apply conservative memcaps suitable for constrained environments.
  --extra-set KEY=VALUE  Additional --set overrides, may be specified multiple times.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


def run(cmd: list, env=None) -> int:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    stdout, _ = proc.communicate()
    sys.stdout.write(stdout.decode(errors='replace'))
    return proc.returncode


def parse_eve_alerts(eve_path: Path):
    """Yield alert dicts from eve.json (one JSON per line)."""
    if not eve_path.exists():
        return
    with eve_path.open('r', encoding='utf-8', errors='replace') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except Exception:
                continue
            if evt.get('event_type') == 'alert':
                yield evt.get('alert', {})


def summarize_alerts(eve_path: Path):
    by_sid = {}
    total = 0
    for alert in parse_eve_alerts(eve_path):
        sid = alert.get('signature_id')
        sig = alert.get('signature')
        total += 1
        by_sid.setdefault(sid, {'count': 0, 'signature': sig})
        by_sid[sid]['count'] += 1
    return total, by_sid


def main():
    ap = argparse.ArgumentParser(description='Suricata offline runner with alert summary')
    ap.add_argument('--config', required=True, help='Path to suricata.yaml')
    ap.add_argument('--rules', required=True, help='Path to rules file (e.g., local.rules)')
    ap.add_argument('--pcaps', required=True, nargs='+', help='PCAP files to process')
    ap.add_argument('--outdir', required=True, help='Base output directory')
    ap.add_argument('--runmode-single', action='store_true', help='Use single-threaded runmode')
    ap.add_argument('--low-mem', action='store_true', help='Apply conservative memcaps')
    ap.add_argument('--extra-set', action='append', default=[], help='Additional --set KEY=VALUE options')

    args = ap.parse_args()

    base_out = Path(args.outdir)
    base_out.mkdir(parents=True, exist_ok=True)

    for pcap in args.pcaps:
        pcap_path = Path(pcap)
        if not pcap_path.exists():
            print(f"[WARN] PCAP not found: {pcap_path}")
            continue

        safe_name = pcap_path.stem.replace(' ', '_')
        out_dir = base_out / f"suri-{safe_name}"
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            'suricata',
            '-c', args.config,
            '-S', args.rules,
            '-k', 'none',
            '-r', str(pcap_path),
            '-l', str(out_dir),
        ]
        if args.runmode_single:
            cmd += ['--runmode', 'single']
        if args.low-mem:
            # Conservative defaults for constrained environments; adjust as needed.
            cmd += [
                '--set', 'stream.memcap=8mb',
                '--set', 'stream.reassembly.memcap=16mb',
                '--set', 'flow.memcap=8mb',
                '--set', 'host.memcap=8mb',
            ]
        for kv in args.extra_set:
            if '=' not in kv:
                print(f"[WARN] Ignoring malformed --extra-set: {kv}")
                continue
            cmd += ['--set', kv]

        print(f"\n[INFO] Running Suricata on {pcap_path} -> {out_dir}")
        print('[INFO] Command:', ' '.join(shlex.quote(c) for c in cmd))
        rc = run(cmd)
        if rc != 0:
            print(f"[ERROR] Suricata exited with code {rc} for {pcap_path}")

        eve = out_dir / 'eve.json'
        total, by_sid = summarize_alerts(eve)
        print(f"[INFO] Alerts in {eve}: {total}")
        if total:
            for sid, info in sorted(by_sid.items(), key=lambda x: (str(x[0]))):
                print(f"  SID {sid}: count={info['count']} signature={info.get('signature')}")
        else:
            print("  No alerts.")


if __name__ == '__main__':
    main()
