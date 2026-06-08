---
name: dynamic-object-aware-egomotion
description: "Analyze video files for camera motion (egomotion) and detect dynamic objects, outputting motion labels and binary masks."
---

# Dynamic Object Aware Egomotion Detection

## When to Use

- Analyze camera motion from video files
- Detect moving objects in video frames
- Generate motion labels and binary masks for video analysis

## Completion Rule

Treat the task as incomplete until **both** output files exist at the required paths:
- `/root/pred_instructions.json`
- `/root/pred_dyn_masks.npz`

Do not stop at environment exploration, package inspection, frame extraction, or a written summary. Use reconnaissance only to unblock execution, then run the analysis and save the artifacts.

If the environment or task specifies a required runtime/tool-call protocol or exact completion string, follow it exactly.


## Output Files

1. `/root/pred_instructions.json` - Frame intervals to motion labels
2. `/root/pred_dyn_masks.npz` - Binary masks for dynamic objects

**Important indexing and coverage rules:**
- Unless the task explicitly requests raw frame IDs, use **sampled-frame indices** (`0, 1, 2, ...`) after sampling at 6 fps for all outputs, not original source-video frame numbers.
- Include one mask entry for **every** sampled frame, including frame 0 and the final sampled frame.
- Before finishing, write both files to the exact paths above and ensure the JSON is valid and the NPZ is readable.


## Motion Labels

Valid labels: Stay, Dolly In, Dolly Out, Pan Left, Pan Right, Tilt Up, Tilt Down, Roll Left, Roll Right

Format:
```json
{
  "0->1": ["Pan Right"]
}
```

Use interval keys over sampled-frame positions, not raw frame IDs. If sampled frames are `[0, 10, 20, 30]` in the source video, transitions are keyed as `"0->1"`, `"1->2"`, `"2->3"` — **not** `"0->10"`, `"10->20"`.

`Stay` is mutually exclusive with all active motion labels; do not emit `Stay` together with `Pan`, `Tilt`, `Roll`, or `Dolly` for the same interval.

When compressing consecutive sampled-frame motions into intervals, ensure coverage spans the full sampled sequence, including the final sampled frame. Example: if 22 sampled frames all share one motion label, use `"0->21"`.

Do not use a reduced classifier that can only emit pan/tilt/stay. The task label space includes `Dolly In`, `Dolly Out`, `Roll Left`, and `Roll Right`.

Before writing JSON, verify that interval keys use sampled-frame index space and that every label is one of: `Stay`, `Dolly In`, `Dolly Out`, `Pan Left`, `Pan Right`, `Tilt Up`, `Tilt Down`, `Roll Left`, `Roll Right`.

## Mask Format (CSR Sparse)

For frame i, store in NPZ:
- `f_{i}_data`: True pixel values
- `f_{i}_indices`: Column indices
- `f_{i}_indptr`: Row pointers
- `shape`: [H, W] resolution


Index mask entries by sampled-frame position.
- Correct NPZ keys: `f_0_data`, `f_0_indices`, `f_0_indptr`, `f_1_*`, ...
- Do not key masks by original frame numbers such as `f_10_*` unless the task explicitly requests raw frame IDs.
- For `N` sampled frames, write `f_0_*` through `f_{N-1}_*`. If a frame has no dynamic pixels, still serialize an empty CSR mask for that frame rather than skipping the key.

Implementation guardrails:
- Convert predicted binary/boolean masks to `uint8` before OpenCV post-processing, e.g. `(mask > 0).astype(np.uint8)`.
- Do not pass raw boolean arrays into `cv2.connectedComponentsWithStats`, morphology, or contour functions; validate dtype and shape at the OpenCV boundary.
- Prefer already-available libraries. If SciPy is unavailable, do not add it just to serialize CSR; write the required NPZ keys (`data`, `indices`, `indptr`, `shape`) directly with NumPy/plain Python arrays.


## Key Parameters

- Sample rate: fps = 6
- Use deep learning models for motion estimation


- Prefer implementations that work with already-available packages before adding new dependencies.
- Before using SciPy/scikit-image or installing packages, check whether they are already importable; if not, prefer a simpler OpenCV/NumPy path unless the task explicitly requires those libraries.



## Required Workflow and Done Criteria

## Required Workflow and Done Criteria

1. Read/sample the video at the target rate.
2. Infer camera motion for sampled-frame intervals and write `/root/pred_instructions.json`.
3. Detect dynamic objects for each sampled frame and write `/root/pred_dyn_masks.npz` in the required CSR key format.
4. Treat frame extraction, sampling metadata, and environment inspection as preparation only; they are not task completion.
5. If a run fails and you identify a fix, rerun after applying the fix; treat outputs from earlier failed runs as stale until regenerated successfully.

## Tips

- Use OpenCV or FFmpeg for video reading
- Store masks as scipy sparse CSR matrices


- Start from `/root/input.mp4` unless the task specifies another video path.
- Keep sampled-frame indices and original frame IDs in separate variables; build final outputs from sampled-frame indices only.
- Keep exploration brief: verify the input and available libraries, then perform egomotion estimation and dynamic-object masking.
- Do **not** replace the required files with an exploration report or status summary.
- If you generate a script, inspect it or run a quick syntax check before executing the full pipeline.
- Validate fragile OpenCV calls before building the pipeline around them. For Farneback optical flow, use a known-good signature such as:
  ```python
  flow = cv2.calcOpticalFlowFarneback(
      prev_gray, next_gray, None,
      pyr_scale=0.5, levels=3, winsize=15,
      iterations=3, poly_n=5, poly_sigma=1.2, flags=0
  )
  ```
- Do not invent OpenCV keyword arguments; if unsure, inspect the function signature or run a minimal test first.
- When fixing runtime errors, patch the exact failing line or function call named in the traceback, then rerun the relevant command.
- Prefer minimal dependencies already available in the environment; use `python3` if `python` is unavailable.
- After writing code, run a small smoke test or inspect representative intermediate outputs before the full export step.
- After writing outputs, sanity-check a few sampled intervals and masks against the video content; do not rely on JSON/NPZ structure alone.



## Tips

## Final Validation

Before declaring completion, open and inspect the deliverables, not just their file paths.

- Do not claim success from truncated/partial stdout or from output-file existence alone; confirm the main analysis run completed successfully end-to-end.
- Inspect `/root/pred_instructions.json` and confirm:
  - it is valid JSON
  - every key is an interval string over sampled-frame indices such as `0->1`
  - each value is a list of allowed motion labels
  - `Stay` does not co-occur with active motion labels
  - intervals cover the intended sampled-frame sequence, including the final sampled frame after any compression/merging logic
- Inspect `/root/pred_dyn_masks.npz` and confirm:
  - `shape` exists and is `[H, W]`
  - for each sampled frame `i`, `f_{i}_data`, `f_{i}_indices`, and `f_{i}_indptr` are present, including the final sampled frame
  - mask data is binary and frame coverage is complete, including empty masks where appropriate
- Confirm indexing alignment at `fps = 6`: sampled-frame count, JSON interval coverage, and NPZ per-frame entries must all refer to the same sampled-frame index sequence.
- Verify semantics, not just schema: inspect representative frames or clips and confirm motion labels match visible camera motion, while masks isolate genuinely moving objects rather than static background or camera-motion residuals.
- If masks are unexpectedly large, nearly full-frame, or uniform across many frames, treat that as a likely failure to separate dynamic objects from egomotion and revise the pipeline before finalizing.
