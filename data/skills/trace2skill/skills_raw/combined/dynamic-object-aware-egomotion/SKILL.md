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

Treat protocol requirements as hard correctness constraints.
- Before the first tool call and before the final response, identify any mandated action/tool-call schema, allowed tool names, observation sequencing, message wrapper, argument format, or exact completion token/string and follow that protocol literally.
- Do not substitute alternate tool syntax, custom tags, wrappers, or a conversational closing message when a strict protocol is required.
- Before the final response, confirm both required files exist and have been validated, then emit the exact required completion signal and nothing else if the environment instructs that.
- Do not declare success from truncated, ambiguous, or narrative-only output. Helper artifacts such as sampled-frame dumps, frame lists, or metadata reports never satisfy the task by themselves.
- Do not end with an exploration report, package summary, or plan. Once input access and usable libraries are confirmed, move immediately to running the analysis pipeline and generating the required files.
- Do not delete analysis scripts, validation scripts, logs, or other diagnostic artifacts before the task is fully accepted; keep the workflow auditable and rerunnable through handoff.



## Output Files

1. `/root/pred_instructions.json` - Frame intervals to motion labels
2. `/root/pred_dyn_masks.npz` - Binary masks for dynamic objects

**Important indexing and coverage rules:**

- Inspect source-video metadata first (FPS, frame count, width, height) and derive the exact sampled-frame index sequence for 6 fps before generating labels or masks.
- Maintain two separate variables throughout the pipeline: `sample_idx` for sampled-frame position (`0..N-1`) and `source_frame_id` for the original video frame number. Use raw frame IDs only for decoding, tracking, or debugging.
- Use the same authoritative sampled-frame index sequence for both JSON intervals and NPZ mask keys, and use the video resolution metadata to set the NPZ `shape` entry.
- Add a final serialization check or conversion step before writing outputs: if any internal intervals or masks are keyed by raw frame IDs or timestamps, remap them onto contiguous sampled-frame indices.

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

Treat motion predictions as labels for transitions between consecutive sampled frames, not labels for individual frames. If you have `N` sampled frames, there are `N-1` adjacent transitions; a per-transition label at position `i` maps to interval `"i->i+1"` before any compression/merging. Do not assign a standalone motion label to frame 0 by itself.


`Stay` is mutually exclusive with all active motion labels; do not emit `Stay` together with `Pan`, `Tilt`, `Roll`, or `Dolly` for the same interval.

Prefer the smallest plausible label set per interval. Treat motion prediction as selecting the single dominant camera-motion label by default unless the task specification explicitly permits multi-label intervals with clear visual evidence. After any smoothing, merging, or voting, re-enforce that if `Stay` is present, it is the only label for that interval.


When compressing consecutive sampled-frame motions into intervals, ensure coverage spans the full sampled sequence, including the final sampled frame. Example: if 22 sampled frames all share one motion label, use `"0->21"`.

- Build interval keys from sampled-frame positions only. If `N` sampled frames were exported, merged interval coverage must end at `N-1`, not at a raw source-video frame number and not one step early.
- If you compress consecutive motions, compress in sampled-index space after conversion. Example: sampled source frames `[0, 10, 20, 30]` with one shared label become `"0->3"`, not `"0->30"`.


Do not use a reduced classifier that can only emit pan/tilt/stay. The task label space includes `Dolly In`, `Dolly Out`, `Roll Left`, and `Roll Right`.

Before writing JSON, verify that interval keys use sampled-frame index space and that every label is one of: `Stay`, `Dolly In`, `Dolly Out`, `Pan Left`, `Pan Right`, `Tilt Up`, `Tilt Down`, `Roll Left`, `Roll Right`.

- Build interval keys from sampled-frame positions, not from `sample_ids`, source-video frame numbers, or timestamps.
- Run an explicit semantic check before declaring success: confirm every interval value is a list of allowed labels, confirm `Stay` never appears with any active motion label, and treat repeated multi-label combinations across many intervals as suspicious unless the spec clearly allows them.
- Do not convert final interval keys back to source-video frame numbers during post-processing; keep the final JSON in sampled-frame index space end-to-end.


Proven baseline for motion inference: estimate a global partial affine transform between consecutive sampled frames from tracked features (for example with `goodFeaturesToTrack` + `calcOpticalFlowPyrLK` + `estimateAffinePartial2D`), then map translation, scale, and rotation to the allowed motion labels.


## Mask Format (CSR Sparse)

For frame i, store in NPZ:
- `f_{i}_data`: True pixel values
- `f_{i}_indices`: Column indices
- `f_{i}_indptr`: Row pointers
- `shape`: [H, W] resolution


Index mask entries by sampled-frame position.

- Frame 0 is required. Initialize per-frame mask serialization from sampled-frame index `0`, not `1`.
- A common failure is looping from `range(1, len(frames))` and omitting `f_0_*`; do not do this.

- Correct NPZ keys: `f_0_data`, `f_0_indices`, `f_0_indptr`, `f_1_*`, ...
- Do not key masks by original frame numbers such as `f_10_*` unless the task explicitly requests raw frame IDs.
- For `N` sampled frames, write `f_0_*` through `f_{N-1}_*`. If a frame has no dynamic pixels, still serialize an empty CSR mask for that frame rather than skipping the key.

- If masks are first computed for sampled source frames like `[0, 10, 20]`, rename/reindex them to `f_0_*`, `f_1_*`, `f_2_*` before serialization; do not preserve raw frame numbers in NPZ keys.
- Do not build masks only for frame pairs with `range(len(frames) - 1)` and stop there; the final sampled frame still needs its own `f_{N-1}_*` entry.


Implementation guardrails:
- Convert predicted binary/boolean masks to `uint8` before OpenCV post-processing, e.g. `(mask > 0).astype(np.uint8)`.
- Do not pass raw boolean arrays into `cv2.connectedComponentsWithStats`, morphology, or contour functions; validate dtype and shape at the OpenCV boundary.
- Prefer already-available libraries. Do not import or install SciPy just to serialize CSR masks; write the required NPZ keys (`data`, `indices`, `indptr`, `shape`) directly with NumPy/plain Python arrays unless the task explicitly requires SciPy.


Dynamic-object detection default: when the camera moves, estimate global inter-frame motion first, warp one frame into the other view, then threshold residual differences rather than relying on raw frame differencing.

CSR serialization hint: when writing keys without SciPy, derive `indices` and `indptr` from the binary mask row-by-row so `indices`, `data`, and `indptr` stay internally consistent even for empty rows or fully empty frames.

After saving the NPZ, run a quick programmatic validation that checks key presence, shared `shape`, and CSR consistency before finalizing.



## Key Parameters

- Sample rate: fps = 6
- Use deep learning models for motion estimation


- Prefer implementations that work with already-available packages before adding new dependencies.
- Before using SciPy/scikit-image or installing packages, check whether they are already importable; if not, prefer a simpler OpenCV/NumPy path unless the task explicitly requires those libraries.

- Prefer a motion model that can drive both outputs from the same estimate: track sparse features (`cv2.goodFeaturesToTrack` + `cv2.calcOpticalFlowPyrLK`), fit a robust global transform (`cv2.estimateAffinePartial2D` or similar), and reuse that transform for both motion labeling and motion compensation before foreground differencing.
- For motion labels, decompose the fitted transform into translation / rotation / scale signals, smooth short-term noise, then map the smoothed signals to the allowed discrete labels before merging intervals.
- In managed or locked-down environments, prefer a NumPy/OpenCV-only path for mask generation and CSR serialization unless another dependency is already importable.




## Required Workflow and Done Criteria

6. At startup, check for any task-specific protocol constraints on tool calls or final signaling; protocol compliance is part of completion.
7. After brief reconnaissance, switch to execution. If you catch yourself preparing a report before both artifacts exist, stop and resume the pipeline.
8. Prefer one end-to-end pipeline/script that samples frames once and produces both deliverables from the same sampled-frame sequence; reuse shared decoding, tracking, and motion estimates so JSON intervals and NPZ mask indices stay aligned.
9. If a traceback identifies a concrete fix, inspect the surrounding code for the reported line/function, patch the exact failing line or call, verify the edit is present, then rerun.
10. After any failed run, treat existing `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz` as stale until a later successful run regenerates them.
11. If transform estimation fails on some interval, handle that interval explicitly rather than silently skipping frames or leaving coverage gaps.
12. Before writing outputs, run a spec-first validation pass independent of the generator: confirm JSON interval endpoints are sampled-frame indices, NPZ keys are `f_0_*` through `f_{N-1}_*` for the same sampled-frame sequence, and no raw source-frame numbers appear in either file.
13. Explicitly compare counts before finalizing: if there are `N` sampled frames, the NPZ must contain mask entries for all indices `0..N-1`, and the motion JSON must cover the same sampled-frame index sequence through `N-1`.
14. Treat boundary indices as mandatory checks: verify frame 0 and the final sampled frame are both represented in the exported outputs.
15. Treat file-format validation as necessary but insufficient: inspect representative sampled frames or clips, confirm motion labels match visible camera motion, and confirm masks isolate moving objects rather than camera-motion residuals.
16. Keep the script or command sequence that produced the outputs until final semantic validation and any protocol-specific completion handoff are complete; do not delete debugging artifacts immediately after the first successful run.


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

- After writing a script, verify the saved file is complete before full execution: inspect the first/last lines or run `python3 -m py_compile <script>` (or an equivalent syntax check), then proceed.
- Before launching a large inline script, confirm which interpreter exists (`python3` vs `python`) and prefer a saved `.py` file or simple heredoc over brittle nested shell quoting.
- Run a tiny interpreter smoke test first when shell quoting or f-strings are involved; fix syntax/quoting issues before the full end-to-end run.

- Validate fragile OpenCV calls before building the pipeline around them. For Farneback optical flow, use a known-good signature such as:
  ```python
  flow = cv2.calcOpticalFlowFarneback(
      prev_gray, next_gray, None,
      pyr_scale=0.5, levels=3, winsize=15,
      iterations=3, poly_n=5, poly_sigma=1.2, flags=0
  )
  ```
- Do not invent OpenCV keyword arguments; if unsure, inspect the function signature or run a minimal test first.

- Before the first full run, verify fragile library calls against the installed API (for example with `help(...)`, `inspect.signature(...)`, or a 2-frame smoke test). This is especially important for OpenCV calls with many positional parameters such as Farneback optical flow.
- At OpenCV boundaries, explicitly convert masks/images to the dtype expected by the called function; for connected components and morphology, prefer `uint8` binary images over boolean arrays.

- When fixing runtime errors, patch the exact failing line or function call named in the traceback, then rerun the relevant command.

- Before editing after a traceback, inspect the surrounding code for the reported line/function first; avoid blind search-and-replace patches on unseen code.
- Make the patch observable: save the file change, then rerun, then confirm the previous error no longer occurs before inspecting outputs.

- Prefer minimal dependencies already available in the environment; use `python3` if `python` is unavailable.
- After writing code, run a small smoke test or inspect representative intermediate outputs before the full export step.
- After writing outputs, sanity-check a few sampled intervals and masks against the video content; do not rely on JSON/NPZ structure alone.

- For dynamic masks under camera motion, prefer egomotion compensation over raw frame differencing: estimate a global affine transform, warp one frame against the next, compute residual differences, then refine with thresholding, morphology, and connected-component area filtering.
- Reuse the same sampled frames and pairwise motion estimates for both motion labeling and mask generation instead of running separate indexing pipelines.
- If you use ffprobe/OpenCV metadata to compute a sampling step, preserve that mapping explicitly so interval compression and final-frame coverage stay correct.
- If you use a heuristic dynamic-mask pipeline, treat it as provisional until you inspect representative masks and coverage statistics.
- Check for over-detection patterns before finalizing: masks that stay large across many frames, look like camera-motion residuals, or remain similarly sized regardless of scene content usually indicate failed egomotion compensation.
- After generation, run a lightweight validator that checks JSON label set and interval syntax, NPZ `shape`, presence of every `f_{i}_*` triplet, and basic CSR consistency before declaring completion.




## Tips

## Final Validation

Before declaring completion, open and inspect the deliverables, not just their file paths.

Also verify the interaction contract is complete: if the task required a specific action syntax or exact completion token, ensure your final response uses that exact form rather than a narrative summary.
If either required artifact is missing, unreadable, stale from an earlier failed run, or replaced by preprocessing outputs, do not finalize; resume the pipeline and regenerate the true deliverables first.


- Do not claim success from truncated/partial stdout or from output-file existence alone; confirm the main analysis run completed successfully end-to-end.

- Confirm execution evidence, not inference: capture a clear success condition such as normal process exit, expected final log lines, or an explicit post-run check that the pipeline completed.
- If the main run output or any verification output is truncated, incomplete, noisy, or ambiguous, rerun with a narrower check or targeted log capture; partial inspection does not count.
- If you changed output indexing or naming late in the run, reopen both `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz` after the rerun; do not assume one file was fixed because the other was.
- Use targeted validation commands instead of partial file prints for large artifacts. Parse the full JSON programmatically and enumerate NPZ keys/counts programmatically.

- Inspect `/root/pred_instructions.json` and confirm:

  - the number of elementary transitions implied by the labels matches `sampled_frame_count - 1` before any interval compression
  - validation includes semantic rules, not just JSON parseability and interval coverage
  - it is valid JSON
  - every key is an interval string over sampled-frame indices such as `0->1`
  - each value is a list of allowed motion labels

  - no interval combines `Stay` with any active motion label; if you see combinations such as `["Pan Right", "Stay"]`, treat the JSON as invalid and fix the labeling/merge logic before finalizing
  - if any interval contains multiple active motion labels, verify the specification explicitly permits that combination; otherwise revise the output
  - `Stay` does not co-occur with active motion labels
  - intervals cover the intended sampled-frame sequence, including the final sampled frame after any compression/merging logic

  - no key boundary is a raw source-frame number unless the task explicitly asked for raw frame IDs
  - if your internal data used raw frame IDs, confirm the written keys are contiguous sampled-index positions (`0..N-1`) after conversion
  - if you merged intervals, verify the last interval ends at `N-1`, not one step early
  - motion labels describe transitions only; confirm there is no standalone baseline/frame-0 motion record

- Inspect `/root/pred_dyn_masks.npz` and confirm:
  - `shape` exists and is `[H, W]`
  - for each sampled frame `i`, `f_{i}_data`, `f_{i}_indices`, and `f_{i}_indptr` are present, including the final sampled frame
  - mask data is binary and frame coverage is complete, including empty masks where appropriate
  - NPZ frame keys are contiguous sampled indices (`f_0_*` through `f_{N-1}_*`), not keys derived from sampled source-frame numbers such as `f_10_*`
  - enumerate or programmatically check the NPZ keys so you confirm full per-frame coverage, not just one representative entry
  - each `f_{i}_indptr` has length `H + 1`, is nondecreasing, and satisfies `indptr[-1] == len(indices) == len(data)` with indices within `[0, W)`

- Confirm indexing alignment at `fps = 6`: sampled-frame count, JSON interval coverage, and NPZ per-frame entries must all refer to the same sampled-frame index sequence.
- Verify semantics, not just schema: inspect representative frames or clips and confirm motion labels match visible camera motion, while masks isolate genuinely moving objects rather than static background or camera-motion residuals.

- Review enough of `/root/pred_instructions.json` to catch systematic labeling errors, not just the first line or file header. If the pattern suggests blanket over-labeling or many intervals with several active labels at once, rerun with corrected logic or thresholds.
- Quantify mask plausibility during inspection: compute per-sampled-frame foreground fraction and review min/median/max. Persistent large or near-uniform coverage across many sampled frames is a warning sign unless visually justified; retune thresholds or compensation and rerun.
- Treat suspicious outputs as failures to investigate, not acceptable edge cases. Examples: many intervals with 3+ simultaneous motion labels, contradictory-looking combinations across most intervals, masks that are nearly full-frame, or highly similar dense masks repeated across many frames.
- If semantic inspection contradicts the schema checks, treat the run as failed and revise/rerun rather than declaring completion from file validity alone.

- If masks are unexpectedly large, nearly full-frame, or uniform across many frames, treat that as a likely failure to separate dynamic objects from egomotion and revise the pipeline before finalizing.

- Run a short programmatic validator before finishing: reload the JSON and NPZ, check interval-key syntax, label legality, CSR field presence for every sampled frame, and consistency between the metadata-derived sampled-frame count, interval coverage, and NPZ entries.
- Perform one cross-check tying both outputs together: if there are `N` sampled frames, JSON intervals must cover sampled indices through the final frame and NPZ must contain `f_0_*` through `f_{N-1}_*`.
- Do not trust a terminal/file-view snippet as proof of correctness; displayed output may be truncated. Prefer full parser-based checks over spot checks.
- Perform an independent indexing audit against the task specification, not your internal sampling list.
- If the previous execution failed, first confirm a later run completed successfully for the current code before trusting any existing output files.
- Confirm completion by evidence, not intent: the log should show actual commands that generated `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz`, followed by inspection of those files.
- If the runtime environment mandates a strict action format or final completion string, verify your response format before every tool call and end exactly as required.

