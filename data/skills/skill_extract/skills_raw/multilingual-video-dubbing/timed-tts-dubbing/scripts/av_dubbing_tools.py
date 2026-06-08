#!/usr/bin/env python3
"""
Reusable helpers for timed TTS dubbing:
- SRT parsing
- Duration control planning (rate_adjust, pad_silence, trim)
- atempo chain builder (handles >2.0 or <0.5 ratios)
- Loudness normalization to -23 LUFS (two-pass loudnorm)
- LUFS measurement
- Mixing delayed segments onto a silence bed

CLI usage examples:
1) Plan duration control and atempo chain
   python av_dubbing_tools.py plan-duration --current 10.272 --target 12.116

2) Two-pass loudness normalization and resample/mono
   python av_dubbing_tools.py loudnorm-two-pass input.wav output.wav --target-lufs -23

3) Measure LUFS
   python av_dubbing_tools.py measure-lufs input.wav

4) Mix delayed segments onto a silence bed
   python av_dubbing_tools.py mix-segments segments.json output.wav
   where segments.json:
   {
     "base_duration_sec": 12.05,
     "segments": [
       {"path": "seg_0.wav", "start_sec": 0.0},
       {"path": "seg_1.wav", "start_sec": 3.5}
     ]
   }
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple

# ---------- Generic utilities ----------

def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def ffprobe_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    proc = run(cmd)
    return float(proc.stdout.strip())

# ---------- SRT parsing ----------

def srt_time_to_sec(ts: str) -> float:
    # 00:00:12,116 -> 12.116
    h, m, rest = ts.strip().split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(path: str) -> List[Dict]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    segments = []
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit() and i + 1 < len(lines):
            timing = lines[i + 1].strip()
            if "-->" in timing:
                start_str, end_str = [s.strip() for s in timing.split("-->")]
                start = srt_time_to_sec(start_str)
                end = srt_time_to_sec(end_str)
                # Collect text until blank
                text_lines = []
                j = i + 2
                while j < len(lines) and lines[j].strip() != "":
                    text_lines.append(lines[j].strip())
                    j += 1
                text = " ".join(text_lines)
                segments.append({
                    "start": start,
                    "end": end,
                    "duration": max(0.0, end - start),
                    "text": text,
                })
                i = j + 1
                continue
        i += 1
    # Optional sanity check: ensure non-decreasing start times
    segments.sort(key=lambda x: x["start"])
    return segments

# ---------- Duration control planning ----------

def plan_duration_control(current: float, target: float) -> Tuple[str, float]:
    """Return (method, ratio) where method in {rate_adjust, pad_silence, trim}.
    ratio is the atempo factor if method==rate_adjust.
    """
    if current <= 0 or target <= 0:
        return ("pad_silence" if target > current else "trim", 1.0)
    ratio = current / target
    # Prefer rate_adjust if ratio is not extreme
    if 0.5 <= ratio <= 2.0:
        return ("rate_adjust", ratio)
    # If current < target and too small ratio, pad
    if ratio < 0.5:
        return ("pad_silence", ratio)
    # If current > target and too large ratio, trim
    return ("trim", ratio)


def atempo_chain(ratio: float) -> str:
    """Build a chain of atempo filters whose product approximates ratio within [0.5,2] steps."""
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    filters: List[float] = []
    r = ratio
    # Decompose into allowed ranges by halving/doubling
    while r > 2.0:
        filters.append(2.0)
        r /= 2.0
    while r < 0.5:
        filters.append(0.5)
        r /= 0.5
    filters.append(r)
    return ",".join(f"atempo={f:.6f}" for f in filters)

# ---------- Loudness normalization ----------

def _extract_json_from_stderr(stderr: str) -> Dict:
    match = re.search(r"\{.*\}", stderr, re.S)
    if not match:
        raise RuntimeError("Failed to parse loudnorm JSON from ffmpeg stderr")
    return json.loads(match.group(0))


def loudnorm_two_pass(input_path: str, output_path: str, target_lufs: float = -23.0,
                      true_peak: float = -1.5, lra: float = 11.0) -> None:
    """Apply two-pass loudnorm to reach target LUFS and force 48k mono."""
    # Pass 1: measure
    cmd1 = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:print_format=json",
        "-f", "null", "-",
    ]
    proc1 = run(cmd1)
    stats = _extract_json_from_stderr(proc1.stderr)
    # Pass 2: apply
    cmd2 = [
        "ffmpeg", "-y", "-i", input_path,
        "-af",
        (
            f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:"
            f"measured_I={stats['input_i']}:"
            f"measured_TP={stats['input_tp']}:"
            f"measured_LRA={stats['input_lra']}:"
            f"measured_thresh={stats['input_thresh']}:"
            f"offset={stats['target_offset']}:"
            "linear=true:print_format=summary"
        ),
        "-ar", "48000", "-ac", "1",
        output_path,
    ]
    run(cmd2)


def measure_lufs(input_path: str, target_lufs: float = -23.0,
                 true_peak: float = -1.5, lra: float = 11.0) -> float:
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:print_format=json",
        "-f", "null", "-",
    ]
    proc = run(cmd)
    stats = _extract_json_from_stderr(proc.stderr)
    # 'input_i' is the measured integrated loudness of the input to this filter
    return float(stats.get("input_i", target_lufs))

# ---------- Mixing helpers ----------

def mix_segments_on_silence(config_json_path: str, output_path: str) -> None:
    """Create a silence bed and overlay delayed segments using adelay + amix.

    config JSON format:
    {
      "base_duration_sec": float,
      "segments": [ {"path": str, "start_sec": float}, ... ]
    }
    """
    cfg = json.loads(Path(config_json_path).read_text(encoding="utf-8"))
    base_duration = float(cfg["base_duration_sec"])
    segs = cfg.get("segments", [])

    # Create silence bed (48k mono)
    silence_path = Path(output_path).with_suffix(".silence.wav")
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={base_duration}",
        str(silence_path),
    ])

    # Build filter_complex
    # Input 0: silence; inputs 1..N: segment waves
    ff_inputs = ["-i", str(silence_path)]
    for seg in segs:
        ff_inputs += ["-i", str(seg["path"])]

    filter_parts = []
    labels = []
    for idx, seg in enumerate(segs, start=1):
        delay_ms = int(round(float(seg["start_sec"]) * 1000.0))
        label = f"a{idx}"
        # For mono, adelay with single value is sufficient
        filter_parts.append(f"[{idx}:a]adelay={delay_ms}[{label}]")
        labels.append(f"[{label}]")

    # Mix: silence + delayed segments
    mix_inputs = "[0:a]" + "".join(labels)
    filter_parts.append(f"{mix_inputs}amix=inputs={len(segs)+1}:duration=first:dropout_transition=0[aout]")

    cmd = [
        "ffmpeg", "-y",
        *ff_inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[aout]",
        "-ar", "48000", "-ac", "1",
        output_path,
    ]
    run(cmd)

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser(description="Timed TTS dubbing helper tools")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("plan-duration", help="Plan duration control and atempo chain")
    ps.add_argument("--current", type=float, required=True, help="Current audio duration (s)")
    ps.add_argument("--target", type=float, required=True, help="Target window duration (s)")

    ln = sub.add_parser("loudnorm-two-pass", help="Two-pass -23 LUFS normalization")
    ln.add_argument("input", help="Input WAV/Audio")
    ln.add_argument("output", help="Output WAV path")
    ln.add_argument("--target-lufs", type=float, default=-23.0)

    ml = sub.add_parser("measure-lufs", help="Measure integrated LUFS via loudnorm")
    ml.add_argument("input", help="Input WAV/Audio")

    mx = sub.add_parser("mix-segments", help="Create silence bed and mix delayed segments")
    mx.add_argument("config", help="JSON config with base_duration_sec and segments list")
    mx.add_argument("output", help="Output mixed WAV path")

    args = ap.parse_args()

    if args.cmd == "plan-duration":
        method, ratio = plan_duration_control(args.current, args.target)
        print(f"method: {method}")
        if method == "rate_adjust":
            chain = atempo_chain(ratio)
            print(f"ratio: {ratio:.6f}")
            print(f"atempo_chain: {chain}")
        else:
            print(f"ratio (info): {ratio:.6f}")
    elif args.cmd == "loudnorm-two-pass":
        loudnorm_two_pass(args.input, args.output, target_lufs=args.target_lufs)
        measured = measure_lufs(args.output, target_lufs=args.target_lufs)
        print(json.dumps({"measured_lufs": round(measured, 2)}, indent=2))
    elif args.cmd == "measure-lufs":
        measured = measure_lufs(args.input)
        print(json.dumps({"measured_lufs": round(measured, 2)}, indent=2))
    elif args.cmd == "mix-segments":
        mix_segments_on_silence(args.config, args.output)
        dur = ffprobe_duration(args.output)
        print(json.dumps({"mixed_duration_sec": round(dur, 3)}, indent=2))


if __name__ == "__main__":
    main()
