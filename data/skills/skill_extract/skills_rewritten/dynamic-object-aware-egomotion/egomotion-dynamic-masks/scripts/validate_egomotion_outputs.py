#!/usr/bin/env python3
import argparse
import json
import re
import sys
from typing import Dict, List, Tuple
import numpy as np

ALLOWED_LABELS = {
    "Stay",
    "Dolly In", "Dolly Out",
    "Pan Left", "Pan Right",
    "Tilt Up", "Tilt Down",
    "Roll Left", "Roll Right",
}

INTERVAL_RE = re.compile(r"^(\d+)->(\d+)$")


def load_npz(npz_path: str):
    try:
        npz = np.load(npz_path, allow_pickle=False)
    except Exception as e:
        return None, [f"Failed to load NPZ: {e}"]
    return npz, []


def infer_num_frames(npz: np.lib.npyio.NpzFile) -> Tuple[int, List[int]]:
    frame_indices = set()
    for k in npz.files:
        if k.startswith('f_') and k.endswith('_data'):
            try:
                idx = int(k[2:-5])
                frame_indices.add(idx)
            except Exception:
                pass
    if not frame_indices:
        return 0, []
    max_idx = max(frame_indices)
    missing = [i for i in range(max_idx + 1) if i not in frame_indices]
    return max_idx + 1, missing


def validate_csr(npz: np.lib.npyio.NpzFile) -> List[str]:
    errs = []
    if 'shape' not in npz.files:
        return ["NPZ missing 'shape' key"]
    shape = np.array(npz['shape']).tolist()
    if not (isinstance(shape, list) and len(shape) == 2):
        errs.append("'shape' must be a length-2 list/array [H, W]")
        return errs
    H, W = shape
    if not (isinstance(H, (int, np.integer)) and isinstance(W, (int, np.integer)) and H > 0 and W > 0):
        errs.append("Invalid shape: H and W must be positive integers")
        return errs

    N, missing = infer_num_frames(npz)
    if N == 0:
        errs.append("No frames found in NPZ (no f_{i}_data keys)")
        return errs
    if missing:
        errs.append(f"Missing CSR entries for frames: {missing}")

    for i in range(N):
        base = f"f_{i}_"
        for suffix in ("data", "indices", "indptr"):
            key = base + suffix
            if key not in npz.files:
                errs.append(f"Missing key: {key}")
                continue
        # If any key is missing, skip deeper checks for this frame
        if any((base + s) not in npz.files for s in ("data", "indices", "indptr")):
            continue

        data = npz[base + "data"]
        indices = npz[base + "indices"]
        indptr = npz[base + "indptr"]

        # Shape checks
        if data.ndim != 1:
            errs.append(f"{base}data must be 1D")
        if indices.ndim != 1:
            errs.append(f"{base}indices must be 1D")
        if indptr.ndim != 1:
            errs.append(f"{base}indptr must be 1D")
        if indptr.size != H + 1:
            errs.append(f"{base}indptr length must be H+1 ({H+1}), got {indptr.size}")

        # Consistency checks
        if indptr.size >= 1:
            last = int(indptr[-1])
            if last != int(indices.size):
                errs.append(f"{base}indptr[-1] ({last}) != len(indices) ({indices.size})")
        # Monotonic indptr
        if not np.all(indptr[:-1] <= indptr[1:]):
            errs.append(f"{base}indptr must be non-decreasing")
        # Bounds for indices
        if indices.size:
            if np.min(indices) < 0 or np.max(indices) >= W:
                errs.append(f"{base}indices contain out-of-bounds column indices [0,{W-1}]")
        # data length equals indices length
        if data.size != indices.size:
            errs.append(f"{base}data and indices length mismatch: {data.size} vs {indices.size}")

    return errs


def validate_json(json_path: str, num_frames: int) -> List[str]:
    errs = []
    try:
        with open(json_path, 'r') as f:
            obj = json.load(f)
    except Exception as e:
        return [f"Failed to load JSON: {e}"]

    if not isinstance(obj, dict):
        return ["Top-level JSON must be an object mapping 'start->end' to [labels]"]

    intervals: List[Tuple[int, int, List[str]]] = []
    for k, v in obj.items():
        m = INTERVAL_RE.match(k)
        if not m:
            errs.append(f"Invalid interval key format: {k}")
            continue
        s, e = int(m.group(1)), int(m.group(2))
        if s >= e:
            errs.append(f"Interval start must be < end: {k}")
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            errs.append(f"Labels for {k} must be a list of strings")
        else:
            for lab in v:
                if lab not in ALLOWED_LABELS:
                    errs.append(f"Invalid label '{lab}' in {k}")
        intervals.append((s, e, v if isinstance(v, list) else []))

    if not intervals:
        errs.append("No intervals present in JSON")
        return errs

    # Sort and check overlaps/gaps and bounds
    intervals.sort(key=lambda x: (x[0], x[1]))

    # Bounds check against num_frames (if available)
    if num_frames > 0:
        max_allowed = num_frames - 1  # intervals end at last sampled frame index
        for (s, e, _) in intervals:
            if s < 0 or e < 0:
                errs.append(f"Negative indices in interval {s}->{e}")
            if s > max_allowed or e > max_allowed:
                errs.append(f"Interval {s}->{e} exceeds sampled frame index range [0,{max_allowed}]")

    # Overlap/gap diagnostics
    prev_end = None
    for (s, e, _) in intervals:
        if prev_end is None:
            prev_end = e
            continue
        if s < prev_end:
            errs.append(f"Overlapping intervals detected at boundary {s} < {prev_end}")
        prev_end = e if e > prev_end else prev_end

    # Recommend starting at 0
    first_start = intervals[0][0]
    if first_start != 0:
        errs.append(f"First interval should start at 0 (found {first_start})")

    return errs


def main():
    p = argparse.ArgumentParser(description="Validate egomotion JSON and CSR mask NPZ outputs")
    p.add_argument("--json", default="pred_instructions.json", help="Path to motion-label JSON")
    p.add_argument("--npz", default="pred_dyn_masks.npz", help="Path to CSR masks NPZ")
    args = p.parse_args()

    all_errs: List[str] = []

    # NPZ validation
    npz, npz_errs = load_npz(args.npz)
    if npz is None:
        all_errs.extend(npz_errs)
        num_frames = 0
    else:
        csr_errs = validate_csr(npz)
        all_errs.extend(csr_errs)
        num_frames, _ = infer_num_frames(npz)

    # JSON validation
    json_errs = validate_json(args.json, num_frames)
    all_errs.extend(json_errs)

    if all_errs:
        print("Validation FAILED:")
        for e in all_errs:
            print(f" - {e}")
        sys.exit(2)

    # Summary
    shape = np.array(npz['shape']).tolist() if npz is not None and 'shape' in npz.files else None
    print("Validation OK")
    if shape is not None:
        print(f" - Image shape: {shape}")
    print(f" - Sampled frames (NPZ): {num_frames}")
    print(" - JSON and NPZ structures are consistent and valid")


if __name__ == "__main__":
    main()
