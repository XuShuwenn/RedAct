---
name: egomotion-dynmask
description: "Estimate camera egomotion between sampled video frames and produce dynamic-object masks with CSR storage; validates outputs for downstream use."
---

# Dynamic-Object-Aware Egomotion

This skill provides a reusable workflow to:
- sample video frames at a target FPS
- estimate camera egomotion (pan/tilt/dolly/roll) between consecutive samples
- detect dynamic objects after compensating for global motion
- serialize masks in CSR sparse format
- validate the two required outputs

Use this when a task requests camera-motion labeling over frame intervals and sparse dynamic masks per sampled frame.

Valid motion labels:
- Stay
- Dolly In, Dolly Out
- Pan Left, Pan Right
- Tilt Up, Tilt Down
- Roll Left, Roll Right

Key outputs expected:
- pred_instructions.json: mapping "start->end" (sample-index intervals, inclusive) to a non-empty list of labels
- pred_dyn_masks.npz: CSR masks per sampled frame with shape=[H, W]

## Core Workflow

Phase 1 — Sample at target FPS (default 6):
- Read video metadata (frame count n, fps, width W, height H)
- Compute stride step = max(1, round(fps / target_fps)); if fps <= 0, assume fps = target_fps
- sample_ids = [0, step, 2*step, ...] strictly increasing and < n
- If the last frame (n-1) is not included, append it
- Work in sample-index space (0..len(sample_ids)-1). Do not use original frame indices in the JSON keys.

Phase 2 — Egomotion estimation between consecutive samples:
- For each pair (i-1, i) of sampled frames:
  1) Convert to grayscale
  2) Detect features (e.g., goodFeaturesToTrack)
  3) Track with calcOpticalFlowPyrLK
  4) Estimate global transform with RANSAC (estimateAffinePartial2D); optional: try homography for strong parallax
  5) Extract parameters from affine M:
     - tx = M[0,2], ty = M[1,2]
     - scale = sqrt(M[0,0]^2 + M[1,0]^2)
     - rot = atan2(M[1,0], M[0,0])
- Classify motion with thresholds scaled to resolution:
  - th_trans ≈ 1% of max(H, W) in pixels
  - th_scale ≈ 1% (|scale-1|)
  - th_rot ≈ 1 degree in radians
- Label conventions (image-space):
  - scale > 1 → Dolly In; scale < 1 → Dolly Out
  - rot > +th_rot → Roll Right; rot < -th_rot → Roll Left (choose a convention and keep it consistent)
  - |tx| > th_trans and |tx| ≥ |ty| → Pan Left if tx > 0 else Pan Right
  - |ty| > th_trans and |ty| > |tx| → Tilt Up if ty > 0 else Tilt Down
- Multiple labels may apply (e.g., Dolly + Pan). If none pass thresholds → Stay
- Optional smoothing:
  - Median filter the sequences [tx], [ty], [scale], [rot] with window=3; or
  - Majority vote smoothing on labels over a 3-frame window
  - Preserve frame 0’s special case as Stay (no prior pair)

Phase 3 — Dynamic mask per sampled frame (motion-compensated differencing):
- For each sampled frame i:
  - i=0: empty mask
  - i>0: use the previously estimated transform (prev→curr)
    1) Warp previous gray to current using the transform
    2) Build a valid region mask by warping an all-ones image (avoid border artifacts)
    3) Compute diff = abs(curr_gray - warped_prev)
    4) Robust threshold on valid pixels:
       thr = max(20, median + k * 1.4826 * MAD), with k≈3 (increase to ≈5 in strong parallax scenes)
    5) raw = (diff > thr) within valid region
    6) Morphological open then close (e.g., 3×3 then 7×7)
    7) Connected components; keep regions with area ≥ max(50, area_ratio * H * W), with area_ratio in [0.0005, 0.005] depending on noise/parallax

Phase 4 — Interval compression and serialization:
- Build per-sample labels L[i] (i from 0..n_samples-1), with L[0] = ["Stay"]
- Merge consecutive indices with identical label sets:
  - For a run starting at s and ending at e (inclusive), emit key f"{s}->{e}" with value L[s]
- Save pred_instructions.json with pretty JSON; values are non-empty lists of strings from the allowed set
- Convert boolean mask to CSR per frame i:
  - rows, cols = np.nonzero(mask)
  - data = ones(len(rows), uint8)
  - counts = bincount(rows, minlength=H)
  - indptr = concat([0], cumsum(counts)) → length H+1, last equals len(indices)
  - Store keys f"f_{i}_data", f"f_{i}_indices", f"f_{i}_indptr"
  - Store shape as int32 array [H, W]
- Save pred_dyn_masks.npz (compressed or uncompressed)

Phase 5 — Verification (must pass before delivery):
- JSON:
  - Keys match "start->end" with integers, 0 ≤ start ≤ end < n_samples
  - Values are non-empty lists of allowed labels (strings)
  - Coverage: union of all intervals fully covers indices 0..n_samples-1 without gaps
- NPZ:
  - shape matches video H, W
  - Frames present for all i=0..n_samples-1
  - For each i: len(indptr) == H+1; indptr[-1] == len(indices); 0 ≤ indices < W; len(data) == len(indices)

## Common Pitfalls and How to Avoid Them
- Mixing index spaces:
  - Pitfall: Using original frame IDs in JSON keys. Fix: Always use sample-index space (0..n_samples-1) for intervals.
- Missing last frame:
  - Pitfall: Omitting n-1 from sampling. Fix: Append n-1 if not included after stepping.
- Fragile FPS handling:
  - Pitfall: fps=0 or invalid. Fix: Fall back to target_fps and step=1 minimum.
- Wrong label conventions:
  - Pitfall: Inconsistent roll direction or pan/tilt sign. Fix: Pick a convention and keep it consistent; document it in the code.
- Over-detection in dynamic masks due to parallax:
  - Pitfall: Affine model cannot explain dolly-in through 3D scenes, yielding large false positives. Fix: Consider homography alignment, erode valid region, raise MAD multiplier and min-area threshold.
- Incorrect image types for morphology/CC:
  - Pitfall: Passing bool to connectedComponentsWithStats. Fix: Cast to uint8 (0/255) before CC.
- Broken CSR encoding:
  - Pitfall: Wrong indptr length or terminal value. Fix: indptr length must be H+1; final value equals number of indices; indices within [0, W).
- Smoothing contaminates first label:
  - Pitfall: Windowed smoothing alters L[0]. Fix: Keep L[0] as ["Stay"].

## Success Criteria
- pred_instructions.json covers all sampled indices with valid labels; intervals are contiguous runs over sample-index space
- pred_dyn_masks.npz contains CSR masks for every sampled frame; frame 0 empty
- Validation script reports OK on JSON and NPZ integrity

## Optional Script Usage
A validator is provided to check both outputs against the video and target FPS.

Example:
- python scripts/validate_egomotion_dynmask.py --video /path/to/video.mp4 --json /root/pred_instructions.json --npz /root/pred_dyn_masks.npz --fps 6

It verifies JSON key/value format, interval coverage against the sampled frame count, NPZ shape, per-frame CSR integrity, and frame count consistency.
