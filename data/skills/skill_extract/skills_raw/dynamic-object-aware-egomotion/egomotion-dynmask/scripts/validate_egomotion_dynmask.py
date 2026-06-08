#!/usr/bin/env python3
import argparse
import json
import sys

import cv2
import numpy as np

ALLOWED = {
    "Stay",
    "Dolly In", "Dolly Out",
    "Pan Left", "Pan Right",
    "Tilt Up", "Tilt Down",
    "Roll Left", "Roll Right",
}

def compute_expected_samples(video_path: str, target_fps: float) -> tuple[int, int, int]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise SystemExit(f"Failed to open video: {video_path}")
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap.release()

    if n <= 0:
        raise SystemExit("Video has no frames")

    if not np.isfinite(fps) or fps <= 0:
        fps = target_fps

    step = max(1, int(round(fps / target_fps)))
    sample_ids = list(range(0, n, step))
    if sample_ids[-1] != n - 1:
        sample_ids.append(n - 1)
    return len(sample_ids), H, W

def validate_json(json_path: str, n_samples: int) -> list[str]:
    errors: list[str] = []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"Failed to read JSON: {e}"]

    if not isinstance(data, dict):
        return ["JSON must be an object mapping 'start->end' to label lists"]

    covered = set()
    for k, v in data.items():
        if not isinstance(k, str) or "->" not in k:
            errors.append(f"Invalid key format (missing '->'): {k}")
            continue
        s_str, e_str = k.split("->", 1)
        if not (s_str.isdigit() and e_str.isdigit()):
            errors.append(f"Key parts not integers: {k}")
            continue
        s = int(s_str); e = int(e_str)
        if not (0 <= s <= e < n_samples):
            errors.append(f"Key out of range: {k} (n_samples={n_samples})")
        if not isinstance(v, list) or len(v) == 0:
            errors.append(f"Value for {k} must be a non-empty list")
            continue
        for lbl in v:
            if not isinstance(lbl, str):
                errors.append(f"Label not string in {k}: {lbl}")
            elif lbl not in ALLOWED:
                errors.append(f"Invalid label in {k}: {lbl}")
        for i in range(s, e + 1):
            covered.add(i)

    # Coverage check
    expected = set(range(n_samples))
    missing = expected - covered
    if missing:
        errors.append(f"Missing sample indices in intervals: {sorted(missing)[:10]}{'...' if len(missing)>10 else ''}")

    return errors

def validate_npz(npz_path: str, H: int, W: int, n_samples: int) -> list[str]:
    errors: list[str] = []
    try:
        npz = np.load(npz_path)
    except Exception as e:
        return [f"Failed to read NPZ: {e}"]

    if "shape" not in npz:
        errors.append("Missing 'shape' key in NPZ")
    else:
        shape = npz["shape"]
        if int(shape[0]) != H or int(shape[1]) != W:
            errors.append(f"Shape mismatch: npz shape={shape} vs video [{H}, {W}]")

    # Count frames in NPZ by scanning consecutive keys
    frames = 0
    while f"f_{frames}_data" in npz:
        frames += 1
    if frames != n_samples:
        errors.append(f"NPZ frames {frames} != expected samples {n_samples}")

    # CSR integrity checks
    for i in range(frames):
        dk = f"f_{i}_data"; ik = f"f_{i}_indices"; pk = f"f_{i}_indptr"
        for key in (dk, ik, pk):
            if key not in npz:
                errors.append(f"Missing key in NPZ: {key}")
                continue
        data = npz.get(dk)
        indices = npz.get(ik)
        indptr = npz.get(pk)
        if data is None or indices is None or indptr is None:
            # already reported missing
            continue
        if indptr.shape[0] != H + 1:
            errors.append(f"Frame {i}: indptr length {indptr.shape[0]} != {H+1}")
        if indptr[-1] != indices.size:
            errors.append(f"Frame {i}: indptr[-1]={indptr[-1]} != len(indices)={indices.size}")
        if indices.size > 0:
            if indices.min() < 0 or indices.max() >= W:
                errors.append(f"Frame {i}: indices out of range [0, {W})")
        if data.size != indices.size:
            errors.append(f"Frame {i}: len(data) {data.size} != len(indices) {indices.size}")
    return errors

def main():
    ap = argparse.ArgumentParser(description="Validate egomotion JSON and CSR masks NPZ against a video and target FPS")
    ap.add_argument("--video", required=True, help="Path to input video")
    ap.add_argument("--json", required=True, help="Path to pred_instructions.json")
    ap.add_argument("--npz", required=True, help="Path to pred_dyn_masks.npz")
    ap.add_argument("--fps", type=float, default=6.0, help="Target sampling FPS (default 6)")
    args = ap.parse_args()

    n_samples, H, W = compute_expected_samples(args.video, args.fps)

    json_errors = validate_json(args.json, n_samples)
    npz_errors = validate_npz(args.npz, H, W, n_samples)

    if json_errors:
        print("JSON validation errors:")
        for e in json_errors:
            print("  -", e)
    else:
        print("JSON validation: OK")

    if npz_errors:
        print("NPZ validation errors:")
        for e in npz_errors:
            print("  -", e)
    else:
        print("NPZ validation: OK")

    ok = not json_errors and not npz_errors
    print(f"\nSummary: {'PASS' if ok else 'FAIL'} (samples={n_samples}, H={H}, W={W})")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
