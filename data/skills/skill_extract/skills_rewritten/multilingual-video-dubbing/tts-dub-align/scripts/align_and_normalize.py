#!/usr/bin/env python3
"""
Align a raw TTS file to a target subtitle window, export 48 kHz mono, and
normalize loudness to a target LUFS using two-pass loudnorm.

Usage:
  python scripts/align_and_normalize.py \
      --in raw_tts.wav \
      --out seg_0.wav \
      --window-start 0.00 \
      --window-end 2.10 \
      --target-lufs -23.0

Options:
  --strategy {auto,rate_adjust,pad_silence,trim}   Duration control selection (default: auto)
  --pad-threshold 0.2                              Max seconds to prefer pad/trim over rate_adjust (default: 0.2)
  --sr 48000                                       Output sample rate (default: 48000)
  --channels 1                                     Output channels (default: 1)
  --tp -2.0                                        True peak target for loudnorm (default: -2.0 dB)
  --lra 11.0                                       LRA target for loudnorm (default: 11.0)

Outputs:
  - --out (final WAV)
  - --out + ".json" (metadata: durations, strategy, loudness)

Requires: ffmpeg, ffprobe
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import List, Tuple, Optional


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def ffprobe_json(path: str) -> dict:
    cmd = [
        'ffprobe', '-v', 'error', '-print_format', 'json',
        '-show_format', '-show_streams', path
    ]
    p = run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {p.stderr[:300]}")
    return json.loads(p.stdout or '{}')


def media_duration_sec(path: str) -> float:
    info = ffprobe_json(path)
    # Prefer format.duration
    fmt = info.get('format', {})
    if 'duration' in fmt and fmt['duration']:
        return float(fmt['duration'])
    # Fallback to streams
    dur = 0.0
    for s in info.get('streams', []):
        d = s.get('duration')
        if d:
            dur = max(dur, float(d))
    return dur


def choose_strategy(tts_dur: float, win_dur: float, pad_threshold: float, requested: str) -> str:
    if requested in { 'rate_adjust', 'pad_silence', 'trim' }:
        return requested
    # auto
    diff = tts_dur - win_dur
    if abs(diff) <= pad_threshold:
        return 'pad_silence' if diff < 0 else 'trim'
    return 'rate_adjust'


def atempo_chain(ratio: float) -> List[float]:
    """Decompose ratio into factors in [0.5, 2.0] for ffmpeg atempo chain."""
    if ratio <= 0:
        raise ValueError('Invalid ratio')
    factors = []
    r = ratio
    # Use powers of 2 to bring ratio into range, then a final factor
    while r > 2.0:
        factors.append(2.0)
        r /= 2.0
    while r < 0.5:
        factors.append(0.5)
        r /= 0.5  # multiply by 2
    # Remaining r in [0.5, 2.0]
    if not math.isclose(r, 1.0, rel_tol=1e-6):
        factors.append(r)
    if not factors:
        factors = [1.0]
    return factors


def build_filter(strategy: str, win_dur: float, tts_dur: float, tempo_ratio: float) -> str:
    filt = []
    if strategy == 'rate_adjust':
        for f in atempo_chain(tempo_ratio):
            filt.append(f"atempo={f:.6f}")
        filt.append(f"atrim=0:{win_dur:.6f}")
        filt.append("asetpts=N/SR/TB")
    elif strategy == 'pad_silence':
        if tts_dur < win_dur:
            pad = win_dur - tts_dur
        else:
            pad = 0.0
        # Ensure exact window length with atrim after apad
        filt.append(f"apad=pad_dur={pad:.6f}")
        filt.append(f"atrim=0:{win_dur:.6f}")
        filt.append("asetpts=N/SR/TB")
    elif strategy == 'trim':
        filt.append(f"atrim=0:{win_dur:.6f}")
        filt.append("asetpts=N/SR/TB")
    else:
        raise ValueError('Unknown strategy')
    return ",".join(filt)


def loudnorm_measure_json(path: str, target_i: float, tp: float, lra: float) -> Optional[dict]:
    cmd = [
        'ffmpeg', '-hide_banner', '-nostdin', '-y', '-i', path,
        '-filter:a', f"loudnorm=I={target_i}:TP={tp}:LRA={lra}:print_format=json",
        '-f', 'null', '-'
    ]
    p = run(cmd)
    if p.returncode != 0:
        return None
    # Extract last JSON object from stderr
    text = p.stderr
    m = re.findall(r"\{[\s\S]*?\}", text)
    if not m:
        return None
    try:
        data = json.loads(m[-1])
        return data
    except json.JSONDecodeError:
        return None


def loudnorm_two_pass(in_path: str, out_path: str, target_i: float, tp: float, lra: float, sr: int, ch: int) -> Tuple[bool, Optional[float]]:
    m = loudnorm_measure_json(in_path, target_i, tp, lra)
    if not m or 'input_i' not in m:
        return False, None
    args = {
        'I': target_i, 'TP': tp, 'LRA': lra,
        'measured_I': m.get('input_i'),
        'measured_TP': m.get('input_tp'),
        'measured_LRA': m.get('input_lra'),
        'measured_thresh': m.get('input_thresh'),
        'offset': m.get('target_offset'),
        'linear': 'true',
        'print_format': 'summary'
    }
    filt = 'loudnorm=' + ':'.join(f"{k}={v}" for k, v in args.items())
    cmd2 = [
        'ffmpeg', '-hide_banner', '-nostdin', '-y', '-i', in_path,
        '-filter:a', filt, '-ar', str(sr), '-ac', str(ch), out_path
    ]
    p2 = run(cmd2)
    if p2.returncode != 0:
        return False, None
    # Measure integrated loudness of the result using ebur128
    cmd3 = [
        'ffmpeg', '-hide_banner', '-nostdin', '-i', out_path,
        '-filter_complex', 'ebur128=peak=true:framelog=verbose', '-f', 'null', '-'
    ]
    p3 = run(cmd3)
    ilufs = None
    # Parse 'I:' line (Integrated loudness)
    for line in (p3.stderr or '').splitlines():
        if 'Integrated loudness' in line or re.search(r'\bI:\s*-?\d+\.\d+\s*LUFS', line):
            m2 = re.search(r'I:\s*(-?\d+\.\d+)', line)
            if m2:
                ilufs = float(m2.group(1))
                break
    return True, ilufs


def main():
    ap = argparse.ArgumentParser(description='Align TTS to window, export 48kHz mono, and normalize loudness.')
    ap.add_argument('--in', dest='inp', required=True, help='Input raw TTS WAV')
    ap.add_argument('--out', dest='out', required=True, help='Output processed WAV')
    ap.add_argument('--window-start', type=float, required=True, help='Window start (seconds)')
    ap.add_argument('--window-end', type=float, required=True, help='Window end (seconds)')
    ap.add_argument('--strategy', choices=['auto','rate_adjust','pad_silence','trim'], default='auto')
    ap.add_argument('--pad-threshold', type=float, default=0.2, help='Seconds threshold for pad/trim vs rate_adjust')
    ap.add_argument('--target-lufs', type=float, default=-23.0)
    ap.add_argument('--tp', type=float, default=-2.0)
    ap.add_argument('--lra', type=float, default=11.0)
    ap.add_argument('--sr', type=int, default=48000)
    ap.add_argument('--channels', type=int, default=1)
    args = ap.parse_args()

    inp = args.inp
    out = args.out
    win_start = float(args.window_start)
    win_end = float(args.window_end)
    win_dur = max(0.0, win_end - win_start)
    if win_dur <= 0:
        print('ERROR: window_end must be > window_start', file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(inp):
        print('ERROR: input file not found', file=sys.stderr)
        sys.exit(1)

    try:
        tts_dur = media_duration_sec(inp)
    except Exception as e:
        print(f'ERROR: failed to probe input: {e}', file=sys.stderr)
        sys.exit(1)

    strategy = choose_strategy(tts_dur, win_dur, args.pad_threshold, args.strategy)

    tempo_ratio = (tts_dur / win_dur) if win_dur > 0 else 1.0
    filt = build_filter(strategy, win_dur, tts_dur, tempo_ratio)

    with tempfile.TemporaryDirectory() as td:
        tmp1 = os.path.join(td, 'timed.wav')
        # Timing + format pass (ensure exact duration; finalize SR/channels here or in loudnorm second pass)
        cmd1 = [
            'ffmpeg', '-hide_banner', '-nostdin', '-y', '-i', inp,
            '-filter:a', filt, '-ar', str(args.sr), '-ac', str(args.channels), tmp1
        ]
        p1 = run(cmd1)
        if p1.returncode != 0:
            print(p1.stderr, file=sys.stderr)
            print('ERROR: timing/format pass failed', file=sys.stderr)
            sys.exit(1)

        # Two-pass loudnorm
        ok, measured_lufs = loudnorm_two_pass(tmp1, out, args.target_lufs, args.tp, args.lra, args.sr, args.channels)
        if not ok:
            print('ERROR: loudness normalization failed', file=sys.stderr)
            sys.exit(1)

    # Verify duration
    final_dur = media_duration_sec(out)
    # Compute placed end assuming start at window_start and exact final duration
    placed_start_sec = win_start
    placed_end_sec = placed_start_sec + final_dur
    drift_sec = placed_end_sec - win_end

    meta = {
        'input_path': os.path.abspath(inp),
        'output_path': os.path.abspath(out),
        'audio_sample_rate_hz': args.sr,
        'audio_channels': args.channels,
        'window_start_sec': round(win_start, 3),
        'window_end_sec': round(win_end, 3),
        'window_duration_sec': round(win_dur, 3),
        'tts_raw_duration_sec': round(tts_dur, 3),
        'strategy': strategy,
        'tempo_ratio': round(tempo_ratio, 6),
        'final_duration_sec': round(final_dur, 3),
        'placed_start_sec': round(placed_start_sec, 3),
        'placed_end_sec': round(placed_end_sec, 3),
        'drift_sec': round(drift_sec, 3),
        'measured_lufs': measured_lufs,
        'notes': 'Place the segment at window_start_sec during muxing (e.g., using -itsoffset).'
    }

    sidecar = out + '.json'
    try:
        with open(sidecar, 'w') as f:
            json.dump(meta, f, indent=2)
    except Exception as e:
        print(f'WARNING: failed to write sidecar JSON: {e}', file=sys.stderr)

    # Console summary
    print(json.dumps({k: v for k, v in meta.items() if k in (
        'strategy','final_duration_sec','measured_lufs','drift_sec','placed_start_sec','placed_end_sec'
    )}, indent=2))


if __name__ == '__main__':
    # Check tool availability early
    for tool in ('ffmpeg', 'ffprobe'):
        if shutil.which(tool) is None:
            print(f'ERROR: required tool not found: {tool}', file=sys.stderr)
            sys.exit(1)
    main()
