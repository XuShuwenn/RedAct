---
name: egomotion-dynamic-masks
description: "Estimate camera egomotion and detect dynamic objects from sampled video frames, then export motion labels and CSR-encoded masks with validation."
---

# Egomotion and Dynamic-Object Masks

This skill provides a reusable workflow to analyze camera motion (egomotion) and detect dynamic objects from a video at a specified sampling rate. It also defines robust output formats and validation checks for a motion-label JSON and a CSR-encoded mask archive.

## When to Use

Activate this skill when asked to:
- classify camera motion between sampled frames (e.g., Stay, Dolly In/Out, Pan, Tilt, Roll)
- output interval-based motion labels over sampled frame indices
- detect dynamic objects per sampled frame and write masks in CSR sparse format
- ensure outputs conform to a strict schema and pass validation

## Core Workflow

1) Inspect video metadata and sampling
- Read video resolution, native fps, and frame count (via OpenCV or ffprobe).
- Compute sampled-frame indices for the target fps:
  - step = native_fps / target_fps
  - indices = unique, sorted round(k * step) within [0, total_frames-1]
  - ensure the last frame is included when applicable (append if not present)
- Decode frames sequentially and collect only sampled indices to avoid seek jitter.

2) Egomotion estimation (pairwise between consecutive sampled frames)
- Convert frames to grayscale.
- Detect and track features (e.g., Shi–Tomasi + pyramidal LK). Alternatively, use dense flow for initialization.
- Estimate a robust global motion model (e.g., affine partial 2D or homography) with RANSAC on matched points.
- Derive motion metrics from the model between frame i and i+1:
  - translation (dx, dy)
  - scale change (s)
  - in-plane rotation (theta)
  - inlier ratio (quality check)

3) Motion label classification per interval
- Allowed labels: Stay, Dolly In, Dolly Out, Pan Left, Pan Right, Tilt Up, Tilt Down, Roll Left, Roll Right.
- Normalize metrics by frame size:
  - tx = dx / width, ty = dy / height
  - scale_delta = s - 1
  - rotation_deg from theta (radians → degrees)
- Classify using robust thresholds with hysteresis or percentile-based rules:
  - Stay if all magnitudes are below small thresholds and/or inlier ratio is too low
  - Dolly In if scale_delta > +threshold; Dolly Out if scale_delta < -threshold
  - Pan Left if tx < -threshold; Pan Right if tx > +threshold
  - Tilt Up if ty < -threshold; Tilt Down if ty > +threshold
  - Roll Left if rotation_deg > +threshold; Roll Right if rotation_deg < -threshold
- Combine labels if multiple metrics exceed thresholds (e.g., Dolly In + Pan Right).
- Special case: the first sampled frame itself has no prior frame; the first interval 0->1 uses motion between frames 0 and 1. Do not infer a motion label for an isolated first frame.

4) Temporal smoothing and interval merging
- Apply windowed smoothing on the per-interval label sets to reduce flicker, but:
  - preserve the first and last intervals from being overwritten by neighboring labels
  - do not merge away genuine short stationary segments (Stay)
- Merge consecutive intervals if they have identical label sets. Represent merged ranges as "start->end" using sampled-frame indices.

5) Dynamic object mask generation (per sampled frame)
- For frames i and i+1, warp frame i into i+1 using the estimated global transform (motion compensation).
- Compute residuals (e.g., absolute intensity difference). Use a robust threshold (e.g., median + k*MAD or percentile-based) to produce an initial foreground mask.
- Post-process:
  - ensure mask is uint8 or bool as needed by image ops
  - denoise (e.g., median filter) and apply morphology (open/close) to clean noise and fill holes
  - remove small connected components below an area threshold
- Edge case: for the first sampled frame, emit an empty mask (no previous frame) or reuse the i→i+1 residual convention consistently across the sequence.

6) CSR encoding of binary masks
- Let mask be H×W boolean or {0,1} uint8.
- Build CSR arrays row-wise:
  - indptr[0] = 0
  - For each row r: find col indices where mask[r, c] is True; append to indices; append ones to data; indptr[r+1] = indptr[r] + number_of_true_cols
- Save arrays per frame i as keys: f_{i}_data, f_{i}_indices, f_{i}_indptr. Also save shape as [H, W].
- Validate invariants before saving: len(indptr) == H+1, indptr is non-decreasing, indptr[-1] == len(indices), all 0 ≤ indices < W.

7) Write outputs
- Motion JSON: a dict mapping "start->end" (sampled indices) to a list of labels (strings from the allowed set).
- Mask NPZ: an archive with key "shape" = [H, W], and three CSR arrays per sampled frame index i.

## Verification

Perform these checks before finalizing:
- Sampling and indexing
  - sampled indices are strictly increasing and within source bounds
  - intervals in the JSON use sampled indices, not raw video frame numbers
  - merged intervals are non-overlapping and monotonically increasing
- Motion labels
  - each interval maps to a list of labels drawn only from the allowed set
  - Stay is used when motion metrics are all below thresholds for that interval
- CSR mask archive
  - contains shape [H, W]
  - for every sampled frame i, keys f_{i}_data, f_{i}_indices, f_{i}_indptr exist
  - for each i: len(indptr) == H+1; all indices in [0, W); indptr non-decreasing; indptr[-1] == len(indices); len(data) == len(indices)
- Cross-file consistency
  - all interval endpoints are within [0, N-1], where N is the number of sampled frames (deduced from mask keys)
  - first interval starts at 0; last interval end ≤ N-1

## Common Pitfalls
- Off-by-one sampling
  - rounding drift can skip or duplicate sampled frames; deduplicate indices and explicitly include the last frame if desired
- Smoothing that corrupts boundaries
  - do not let smoothing override the first interval or merge away true stationary segments
- Misuse of data types in image ops
  - many OpenCV morphology and connected-components ops require uint8 input; convert masks appropriately and only convert back to bool for CSR
- Incorrect label basis
  - ensure intervals are between sampled frames; do not use absolute frame numbers
  - combine labels only when their metrics exceed thresholds; otherwise label as Stay
- Fragile dependencies
  - avoid non-essential sparse libraries; CSR arrays are easy to write with NumPy alone
- Invalid CSR encoding
  - wrong indptr length, out-of-range indices, or mismatched counts will break consumers; validate before saving

## Success Criteria
- Motion JSON contains valid, non-overlapping, monotonically increasing intervals over sampled indices with labels from the allowed set
- NPZ archive has shape and per-frame CSR arrays that pass structural checks
- Optional validator reports no errors

## Optional Script Usage
- Use scripts/validate_egomotion_outputs.py to validate the two outputs:
  - python scripts/validate_egomotion_outputs.py --json pred_instructions.json --npz pred_dyn_masks.npz
- The validator checks label sets, interval formatting, and CSR integrity and returns a non-zero exit code on failure.
