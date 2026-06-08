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

**Mandatory workspace/protocol gate before creating files or acting:**
- Before writing any script, temp file, or output artifact, identify the environment's allowed writable directories, required absolute output paths, required action wrapper/schema, allowed tool names/casing, argument shape, observation ordering, and any exact completion token/string.
- If the environment requires a specific action format (for example `Thought:` / `Action:` with a JSON object), copy it literally on every action; do not switch to XML/custom tags, markdown pseudo-calls, undeclared tools, alternate wrappers, or free-form command narration.
- Treat the environment's declared tool interface as exclusive unless the task explicitly says otherwise; do not invent alternate tools or helper channels.
- Put the real executable command or literal script body inside the required action payload; do not replace it with placeholders like `run analysis`, `check outputs`, `inspect files`, or narrative intent statements.
- If the environment requires an exact completion string (for example `ACTION: TASK_COMPLETE`), reserve the final response for that exact string only, with matching casing/punctuation and nothing before or after it.
- Do not assume `/root` or any convenient directory is writable for scripts/intermediates; use only task-provided or explicitly allowed locations, while still writing fixed deliverables to their required paths when the environment permits them.
- Treat protocol or path-scope violations as task failure even if the artifacts are otherwise correct.
- Before the first action and again before finalizing, compare your planned action/final response against the required schema/token literally; if it does not match character-for-character, fix the format before sending it.


**Mandatory protocol gate before acting:**
- Before the first tool/action and again before the final response, verify the exact environment-required interaction contract: allowed tool names/casing, required wrapper or action schema, argument format, observation sequencing, and any exact completion token/string.
- If the environment mandates a specific tool-call schema (for example `Thought:`/`Action:` with JSON arguments), mirror that schema literally for every tool interaction.
- If the environment mandates an exact completion token/string, end with that exact string and nothing else.
- Do not improvise alternate wrappers such as XML/custom tags, markdown-fenced pseudo tool calls, unsupported tool names, or narrative substitutes when a strict protocol is specified.
- Treat protocol violations as task failure even if the output files are otherwise correct.
- Treat the concrete task statement as the source of truth before implementation: confirm artifact paths, schema, indexing convention, and completion requirements from the task/environment rather than inferring them loosely.
- A preprocessing-only run is a failure: metadata checks, sampled-frame dumps, package inspection, or validator setup do not satisfy the task unless they are followed by actual motion inference, dynamic-mask generation, and writing both required output files.
- Make every action auditable and concrete: issue fully spelled-out executable commands or actual script contents, not placeholders like "run analysis", "fix the OpenCV call", or "validate outputs".
- Hard stop against exploration-only failure: once you have confirmed the input path and a workable execution path, stop reconnaissance and run the analysis; do not spend additional turns on inventorying, planning-only updates, or readiness summaries.

- Before the first tool call and before the final response, identify any mandated action/tool-call schema, allowed tool names, observation sequencing, message wrapper, argument format, or exact completion token/string and follow that protocol literally.
- Do not substitute alternate tool syntax, custom tags, wrappers, or a conversational closing message when a strict protocol is required.
- Before the final response, confirm both required files exist and have been validated, then emit the exact required completion signal and nothing else if the environment instructs that.
- Do not declare success from truncated, ambiguous, or narrative-only output. Helper artifacts such as sampled-frame dumps, frame lists, or metadata reports never satisfy the task by themselves.
- Do not end with an exploration report, package summary, or plan. Once input access and usable libraries are confirmed, move immediately to running the analysis pipeline and generating the required files.
- Do not delete analysis scripts, validation scripts, logs, or other diagnostic artifacts before the task is fully accepted; keep the workflow auditable and rerunnable through handoff.

- If you create a plan, todo list, or milestone checklist, use it as a hard termination gate: before stopping, re-open it and confirm every core analysis step is completed or explicitly blocked.
- Treat sampling metadata, extracted/sample frames, debug dumps, and setup artifacts as intermediate only. They never replace `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz`.
- If either deliverable or any verification output is truncated, cut off mid-object/string, or only partially displayed, treat completion as unproven. Re-open the artifacts with parser-based checks (`json.load` for JSON, `np.load` for NPZ) and regenerate if parsing/loading fails.
- Do not treat `exit code 0`, `Done`, or similar logs as completion evidence by themselves; completion requires successful parser-based validation of both regenerated deliverables in their final on-disk form.
- Do not rewrite outputs based on guessed validator complaints. First obtain the concrete failed check, parse error, or mismatch, then patch only the confirmed issue and rerun validation.



## Output Files

1. `/root/pred_instructions.json` - Frame intervals to motion labels
2. `/root/pred_dyn_masks.npz` - Binary masks for dynamic objects

**Important indexing and coverage rules:**

- Inspect source-video metadata first (FPS, frame count, width, height) and derive the exact sampled-frame index sequence for 6 fps before generating labels or masks.
- Compute and freeze the authoritative sampled-frame sequence once from observed metadata before inference, then reuse that same list for decoding, motion intervals, NPZ keys, and validation.
- Record `expected_sample_count = len(sample_ids)` and use it in final checks so JSON coverage reaches `expected_sample_count - 1` and NPZ coverage includes every sampled frame `0..expected_sample_count - 1`.
- If output structure is wrong but upstream inference looks reasonable, fix the narrow formatting/post-processing step responsible (for example interval compression or sampled-index remapping) instead of rewriting frame extraction, motion estimation, and mask generation.

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

When smoothing, voting, or merging per-transition motion labels, handle boundary transitions explicitly. Do not let neighbor-based smoothing erase or invent the first or last valid transition just because one side lacks context.


`Stay` is mutually exclusive with all active motion labels; do not emit `Stay` together with `Pan`, `Tilt`, `Roll`, or `Dolly` for the same interval.

Prefer the smallest plausible label set per interval. Treat motion prediction as selecting the single dominant camera-motion label by default unless the task specification explicitly permits multi-label intervals with clear visual evidence. After any smoothing, merging, or voting, re-enforce that if `Stay` is present, it is the only label for that interval.


When compressing consecutive sampled-frame motions into intervals, ensure coverage spans the full sampled sequence, including the final sampled frame. Example: if 22 sampled frames all share one motion label, use `"0->21"`.

- Build interval keys from sampled-frame positions only. If `N` sampled frames were exported, merged interval coverage must end at `N-1`, not at a raw source-video frame number and not one step early.
- If you compress consecutive motions, compress in sampled-index space after conversion. Example: sampled source frames `[0, 10, 20, 30]` with one shared label become `"0->3"`, not `"0->30"`.

- If you merge/compress intervals, run an explicit coordinate-system audit before saving: derive `N` sampled frames, confirm the elementary transitions would be `0->1` through `N-2->N-1`, then confirm the merged intervals still live in sampled-index space and collectively end at `N-1`.
- Do not silently switch semantics during post-processing from sampled-frame positions to raw source-frame IDs or timestamps.


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
- Use an explicit conversion right before strict OpenCV calls, e.g. `mask_u8 = (mask > 0).astype(np.uint8)`.
- For `cv2.connectedComponentsWithStats`, pass a single-channel 8-bit image, e.g. `num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)`.
- **Wrong:** `cv2.connectedComponentsWithStats(mask > 0, connectivity=8)` on a boolean array.
- If unsure, run a tiny smoke test on one representative mask before the full pipeline.
- Immediately before any `connectedComponentsWithStats`, morphology, or contour call, assert/inspect that the actual array passed is single-channel `uint8`; do not rely on an earlier conversion surviving later boolean expressions.
- Safe pattern:
  ```python
  mask_u8 = (mask > 0).astype(np.uint8)
  num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
  assert mask_u8.dtype == np.uint8 and mask_u8.ndim == 2
  ```
- Before the first full run, smoke-test the exact connected-components or morphology signature you plan to use on a tiny `uint8` binary mask; do not launch the end-to-end run until that call shape works.
- If a full run crashes on an OpenCV mask-processing call, inspect the exact saved call site, patch that concrete line, and rerun before trusting any written outputs.


- Prefer already-available libraries. Do not import or install SciPy just to serialize CSR masks; write the required NPZ keys (`data`, `indices`, `indptr`, `shape`) directly with NumPy/plain Python arrays unless the task explicitly requires SciPy.


Dynamic-object detection default: when the camera moves, estimate global inter-frame motion first, warp one frame into the other view, then threshold residual differences rather than relying on raw frame differencing.

CSR serialization hint: when writing keys without SciPy, derive `indices` and `indptr` from the binary mask row-by-row so `indices`, `data`, and `indptr` stay internally consistent even for empty rows or fully empty frames.

After saving the NPZ, run a quick programmatic validation that checks key presence, shared `shape`, and CSR consistency before finalizing.



## Key Parameters

- Sample rate: fps = 6
- Default to `python3`, not `python`, unless you have explicitly confirmed another interpreter exists and is required.

- Do not assume deep-learning models or extra packages are available. Default to a NumPy/OpenCV pipeline unless the task explicitly requires another model and you have confirmed the dependency imports successfully.


- Prefer implementations that work with already-available packages before adding new dependencies.
- Confirm the available Python interpreter before the first full run and use the working executable consistently.
- Before the main run, smoke-test the critical imports you plan to rely on (at minimum NumPy and OpenCV) so runtime assumptions are verified before debugging pipeline logic.

- Before committing to an implementation, probe whether planned imports are available and basically compatible.
- If a package is missing, incompatible, or unnecessary for the spec, revise the implementation toward available NumPy/OpenCV/plain-Python paths before attempting installation.
- Do not make SciPy a default dependency for mask serialization or post-processing unless the task explicitly requires it and you have confirmed it imports successfully.
- In constrained or managed environments, treat package installation as disfavored when an OpenCV/NumPy path can satisfy the spec.

- Before using SciPy/scikit-image or installing packages, check whether they are already importable; if not, prefer a simpler OpenCV/NumPy path unless the task explicitly requires those libraries.
- Decide dependency strategy before writing the main pipeline: run tiny import/version smoke tests for planned libraries and commit to the simplest path that already works.
- Do not choose SciPy solely for CSR writing convenience. Default to direct NumPy/plain-Python NPZ serialization for `data`/`indices`/`indptr` unless SciPy is explicitly required and confirmed importable.
- If `import scipy` fails, installation is blocked, or the environment reports incompatibility, remove SciPy from the pipeline immediately and rerun with direct NumPy/OpenCV CSR serialization rather than continuing to launch scripts that still depend on SciPy.
- Treat package installation or environment mutation as a last resort in managed environments when an available NumPy/OpenCV/plain-Python path can satisfy the spec.


- Prefer a motion model that can drive both outputs from the same estimate: track sparse features (`cv2.goodFeaturesToTrack` + `cv2.calcOpticalFlowPyrLK`), fit a robust global transform (`cv2.estimateAffinePartial2D` or similar), and reuse that transform for both motion labeling and motion compensation before foreground differencing.
- For motion labels, decompose the fitted transform into translation / rotation / scale signals, smooth short-term noise, then map the smoothed signals to the allowed discrete labels before merging intervals.
- In managed or locked-down environments, prefer a NumPy/OpenCV-only path for mask generation and CSR serialization unless another dependency is already importable.




## Required Workflow and Done Criteria

6. At startup, check for any task-specific protocol constraints on tool calls or final signaling; protocol compliance is part of completion.
7. After brief reconnaissance, switch to execution. If you catch yourself preparing a report before both artifacts exist, stop and resume the pipeline.
8. Prefer one end-to-end pipeline/script that samples frames once and produces both deliverables from the same sampled-frame sequence; reuse shared decoding, tracking, and motion estimates so JSON intervals and NPZ mask indices stay aligned.
8a. Prefer a single saved script that reads metadata, freezes `sample_ids`, runs motion inference, generates masks, writes both artifacts, and then invokes a lightweight validator/check. This integrated pattern reduces cross-file indexing drift.
8b. Keep that single pipeline authoritative: derive sampled-frame count, sampled-index mapping, and frame shape once, then reuse those exact values for both JSON interval export and NPZ mask serialization instead of recomputing them in separate code paths.

9. If a traceback identifies a concrete fix, inspect the surrounding code for the reported line/function, patch the exact failing line or call, verify the edit is present, then rerun.
9a. Make edits against exact observed source text only; do not use descriptive placeholders such as "fix boolean input", "remove unavailable import", or "adjust mask code" as patch targets.
9b. After a dependency, API, or OpenCV error, confirm the specific failing import/call site in the saved script, patch that concrete code, then rerun to verify the original error is gone.
9c. Before editing after a traceback, open the saved script and inspect the exact reported line plus nearby lines/functions. Edit against the observed file contents; do not apply placeholder or prose-described replacements without first reading the code on disk.
9d. Do not say you "fixed" or "patched" anything unless the transcript shows an actual edit command between the failing run and the rerun.
9e. Do not use placeholder patch targets such as `remove unavailable import`, `fix boolean input`, or `adjust mask code`.
9f. After editing, re-open, print, or diff the relevant snippet from the saved script so the transcript shows the concrete change before rerunning.
9g. If the same traceback appears after a claimed fix, stop patching by description. Re-open the saved script at the reported line/function, inspect the exact call and arguments, make a text-grounded edit, then verify the edited code before rerunning.
9h. If the failing path involved masks, dtypes, or OpenCV image-processing calls, add a targeted post-fix check on regenerated outputs: reload the NPZ and verify CSR lengths, key coverage, and binary-valued mask data rather than treating a clean rerun alone as proof.


10. After any failed run, treat existing `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz` as stale until a later successful run regenerates them.
11. If transform estimation fails on some interval, handle that interval explicitly rather than silently skipping frames or leaving coverage gaps.
12. Before writing outputs, run a spec-first validation pass independent of the generator: confirm JSON interval endpoints are sampled-frame indices, NPZ keys are `f_0_*` through `f_{N-1}_*` for the same sampled-frame sequence, and no raw source-frame numbers appear in either file.
13. Explicitly compare counts before finalizing: if there are `N` sampled frames, the NPZ must contain mask entries for all indices `0..N-1`, and the motion JSON must cover the same sampled-frame index sequence through `N-1`.
14. Treat boundary indices as mandatory checks: verify frame 0 and the final sampled frame are both represented in the exported outputs.
15. Treat file-format validation as necessary but insufficient: inspect representative sampled frames or clips, confirm motion labels match visible camera motion, and confirm masks isolate moving objects rather than camera-motion residuals.
16. Keep the script or command sequence that produced the outputs until final semantic validation and any protocol-specific completion handoff are complete; do not delete debugging artifacts immediately after the first successful run.


17. Before the first real command, make a short preflight checklist covering: exact required tool-call syntax, exact completion string, intended interpreter, planned dependency imports, and the exact artifact paths/schema you must produce.
17a. Include allowed read/write locations in that preflight checklist. Confirm where intermediates may be created before saving scripts, validators, logs, or caches.
17b. If a strict action schema is specified, write down one literal example of the required wrapper before issuing the first action, then mirror that format exactly for every subsequent tool call.
17c. Include in that preflight the exact allowed tool names/casing, planned dependency import checks, and the input media properties you will rely on (at minimum width, height, FPS, and frame count).
17d. Before the first implementation edit, explicitly reconcile the live task instructions with this skill: verify the exact artifact paths, schema/indexing rules, and required final completion signal from the task/environment itself.
17e. Quickly check for task-local guidance already present in the environment, then stop reconnaissance; do not spend multiple turns re-reading docs or inventorying the environment once the contract is known.
17f. In that preflight, write down the exact next executable action in the mandated schema, and on the very next turn send that real command rather than a readiness summary or prose handoff.

18. After reconnaissance confirms the video path and usable libraries, execute an end-to-end run immediately; do not end the turn with a readiness report, exploration report, or implementation plan.
19. Every tool invocation must contain a concrete executable command or literal script body. Do **not** send placeholders such as `run the pipeline`, `install required Python packages`, `check outputs`, or `inspect NPZ keys`.
19a. Treat natural-language intent strings as invalid tool input. Replace them with the exact command you will execute, including executable name, script path, flags, redirections, and concrete file paths.
19b. Do not use abbreviated or ellipsis-style stand-ins such as `ffprobe ...`, `python ...`, `inspect the generated JSON file`, or `remove temporary scripts`.
19c. The command text itself must perform the claimed check. Do not issue descriptive no-op commands such as `python3 -c "validated the JSON and NPZ outputs"`; include real code that loads the artifacts and asserts the required properties.
19d. If the environment exposes only one permitted execution tool/schema, route all command execution through that exact interface rather than mixing tool-call styles.

20. If you create a script via heredoc or redirection, write the full executable code into the file; do not substitute placeholder text or a prose summary for code.

20a. The same rule applies to heredocs, JSON/config/data files, and scripted actions: write the actual executable or parseable content, not descriptive text.
20b. After any nontrivial write/edit, reopen the file around the changed lines or parse it directly to confirm the exact code/data now on disk before rerunning.
21. After writing or heavily editing a script, run a lightweight validation before the first full execution: inspect the saved file and/or run `python3 -m py_compile <script>` (or the confirmed interpreter equivalent), then fix any reported syntax errors before the end-to-end run.
21a. If `python` fails or is unavailable, switch immediately to the confirmed interpreter (typically `python3`) instead of retrying with the missing command.
21b. Before the first full run, smoke-test fragile assumptions: confirm the intended interpreter works, confirm each non-stdlib import actually imports, confirm OpenCV calls use the installed signature (for example `calcOpticalFlowPyrLK(..., prev_pts, None, ...)`), and confirm mask-processing inputs reaching OpenCV are `uint8` single-channel arrays rather than `bool`.
21c. If any dependency or API smoke test fails, immediately revise the pipeline toward the documented NumPy/OpenCV-only path and rerun the smoke test before attempting the end-to-end job.

22. Smoke-test fragile APIs with tiny inputs before the first full run. In particular, verify the exact OpenCV signatures you will use and confirm connected-components/morphology inputs are `uint8`, not `bool`.
23. If a planned dependency import fails or an API smoke test fails, revise the implementation immediately instead of launching the full script and hoping later stages will work.
24. Do not say a fix was applied unless the transcript shows an actual code edit between the failing run and the rerun.
25. After any substantial run, confirm completion explicitly before trusting outputs: check normal process termination, and if stdout is truncated, cut off, or ambiguous, rerun with a quieter command, redirected log, or targeted post-run check until completion is unambiguous.

25a. Treat long or noisy pipeline stdout as inconclusive by default. If output stops mid-line, is truncated by the interface, or lacks a clear shell exit signal, do not proceed to artifact validation until you have confirmed the process ended successfully.
25b. If a run exits nonzero or output is truncated before the exception is visible, first rerun to capture the full traceback before editing code.
25c. Treat any verification command that exits nonzero, raises an exception, or depends on a missing import as failed/incomplete verification. Do not summarize that check as passed unless a later successful command explicitly covers the same requirement.
25d. If a helper validator fails because of an unnecessary dependency, replace it with a dependency-light parser/check that verifies the same requirement and base your summary only on the successful replacement check.
25e. After an edit, claim only the exact change the transcript proves; do not claim the whole bug is fixed until a rerun confirms the original failure is gone.
26. After any traceback-driven fix and rerun, treat the task as unfinished until you revalidate both artifacts end-to-end; file existence or a helper validator's summary line is not enough.
27. If you change JSON interval indexing, mask key naming, sampling logic, or any shared schema assumption, regenerate the outputs and revalidate **both** `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz`; never inspect only the artifact that first exposed the issue.
28. Reconcile indexing semantics across the whole run before finalizing: metadata-derived sampled-frame IDs, per-transition motion analysis, merged JSON intervals, and NPZ frame keys must all refer to the same declared sampled-frame output coordinate system.
29. If validation output is structurally green but semantically surprising — for example unexpectedly few intervals, suspiciously dense masks, or a sudden switch between raw frame IDs and sampled indices — reopen the written files and inspect the mapping/merge logic before declaring success.
30. Do not delete the main analysis script or validator before final semantic validation and any required completion handoff are finished.
31. Immediately before the final response, perform one last contract audit: required files exist and were regenerated successfully in this run, validation is complete, every tool call followed the mandated schema, and the final response matches the exact required completion token/string if one is specified.
32. If you used a todo list or multi-step plan earlier in the run, revisit it during the final audit and confirm no core task items remain pending. An unfinished plan means the task is unfinished.
33. If you change indexing, interval semantics, mask key naming, or any shared output schema, rerun the generator and then re-open and validate both `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz` in the same post-fix cycle; do not stop after checking only the artifact that first revealed the bug.
34. Record concise run metadata after generation and before finalizing: source video properties, sampled-frame count `N`, and resulting motion-interval count. Use these counts to sanity-check that JSON coverage and NPZ frame entries align with the same sampled sequence.
35. Do not delete the main pipeline script, validator, logs, or other generated diagnostic artifacts during wrap-up unless the task explicitly instructs you to remove them.
36. If the environment specifies an exact termination token/string, the final response must be that exact string and nothing else; do not append explanations, file summaries, or confidence statements.



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
- Do not infer from that default input path that `/root` is an allowed general workspace; verify allowed write locations separately before creating scripts or intermediates there.
- A reliable opening move is: inspect video metadata first, confirm OpenCV/NumPy imports, then implement against those observed constraints.
- A reliable closing move is: reopen the written JSON and NPZ and inspect their actual schema/keys before trusting the run.

- Keep sampled-frame indices and original frame IDs in separate variables; build final outputs from sampled-frame indices only.
- Keep exploration brief: verify the input and available libraries, then perform egomotion estimation and dynamic-object masking.
- Do **not** replace the required files with an exploration report or status summary.
- If you generate a script, inspect it or run a quick syntax check before executing the full pipeline.

- When using a shell/bash tool, issue concrete executable commands only. Do not send placeholders such as `run the video analysis pipeline`, `install required packages`, or other natural-language task descriptions.
- Every shell command should name the real executable, script/file path, and arguments. Example: `python3 /root/run_pipeline.py --input /root/input.mp4` is valid; `run analysis` is not.
- Bad tool/action examples to avoid: `Write`, `Read`, `Edit`, `Bash(command='run the pipeline')`, `check outputs`, or any prose-only pseudo command.
- Good actions are literal executable commands or full script bodies placed through the environment's allowed tool schema.
- Before sending a shell action, sanity-check that the string begins with a real executable or shell builtin (`python3`, `bash`, `ls`, `cat`, `ffprobe`, etc.). If it reads like a task description instead of a command, rewrite it.
- Apply the same concreteness rule to validation: use executable checks such as a real validator script or a literal parser snippet, not natural-language shell lines like `inspect outputs` or `run validation script`.
- If writable locations are restricted, save helper scripts in an allowed workspace directory and reserve fixed output paths only for the required deliverables.

- Before committing to SciPy/scikit-image or similar imports, run a tiny import smoke test; if unavailable, keep the pipeline dependency-light and adapt the serialization/processing code.
- If you save a script, config, or validator, inspect it immediately after writing to confirm it contains real code/JSON rather than a descriptive sentence.
- Treat script creation as evidence, not intent: the file-write command itself should visibly contain the implementation you plan to run.
- After a traceback, make the repair sequence explicit and ordered: inspect failing code, edit file, verify the edit exists, rerun. Skipping the visible edit step and only rerunning counts as no fix.
- Use a tiny executable preflight for fragile dependencies/APIs before the main run, and if the environment requires `Thought:` / `Action:` formatting or an exact completion string, mirror that syntax literally on every turn.



- After writing a script, verify the saved file is complete before full execution: inspect the first/last lines or run `python3 -m py_compile <script>` (or an equivalent syntax check), then proceed.
- Before launching a large inline script, confirm which interpreter exists (`python3` vs `python`) and prefer a saved `.py` file or simple heredoc over brittle nested shell quoting.
- Run a tiny interpreter smoke test first when shell quoting or f-strings are involved; fix syntax/quoting issues before the full end-to-end run.

- Validate fragile OpenCV calls before building the pipeline around them. For Farneback optical flow, use a known-good signature such as:
- For Lucas-Kanade tracking, use the OpenCV call shape explicitly: `next_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, next_gray, prev_pts, None, **lk_params)`. Do not omit the `None` placeholder for `nextPts`.
- Before using SciPy-based sparse helpers, verify `import scipy` succeeds; if not, serialize CSR NPZ fields directly with NumPy/Python as described above rather than adding a hard SciPy dependency.

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

- Prefer minimal dependencies already available in the environment; default to `python3` for scripts/one-liners unless you have explicitly confirmed that `python` exists and is the correct interpreter.
- Do not start the main pipeline with `python` on assumption alone. If interpreter availability is uncertain, run a tiny version check first and then use the confirmed executable consistently.

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

### Protocol Compliance Check

Before finalizing, verify interaction compliance separately from artifact correctness:
Treat protocol review as a hard stop and a literal checklist:
- compare your actual prior tool turns against the environment-required wrapper/schema
- verify every tool-use turn used the required wrapper/name/casing and no placeholder command text was used where executable code/commands were required
- if a strict wrapper or specific tool name/casing was required, verify you used it literally on every action from the first call onward
- verify the final response is exactly the mandated completion token/string, with no added natural-language success message
- confirm any required directory/file-scope restrictions were respected throughout the run
If any of those checks fail, do not finalize even when both files validate.

- confirm all tool invocations matched the environment-required syntax exactly
- confirm no alternate wrappers, pseudo-calls, or undeclared tool names were used when a strict schema was specified
- confirm the final response is the exact required completion string/action, with no added summary or explanation when exact termination is required

If protocol compliance and artifact correctness disagree, protocol compliance still governs task success.


Before declaring completion, open and inspect the deliverables, not just their file paths.
Read the generated files back in their final serialized form: parse the full JSON with `json.load(...)` and load the NPZ with NumPy. Base any final fixes on what was actually written to disk, not only on in-memory structures or intended logic. Inspect the written interval keys and NPZ key set directly so post-processing bugs in compression/remapping are caught before finalizing.


Use this final stop-check:
- Have I produced both required deliverables, not just setup artifacts?
- Did I complete motion estimation and dynamic-mask generation, not merely sampling/extraction?
- Am I about to use the exact required completion syntax/token for this environment?
If any answer is no, do not finalize.

Treat validation levels separately:
- **Structural validation**: files exist, parse/load, have expected keys, counts, and CSR consistency.
- **Task-level validation**: motion labels match visible camera motion on representative intervals, and dynamic masks isolate moving objects rather than camera-motion residuals.
- **Protocol validation**: tool-call format and final completion signaling match the environment's exact requirements.

Bound all status claims to observed evidence:
- If validation output is partial, say it is partial and continue validating; do not summarize it as a pass.
- Distinguish clearly between `edited`, `reran`, and `verified passed`; only the last one supports completion.
- Keep completion claims proportional to evidence. Structural checks alone support only structural claims unless semantic inspection was also performed.

Validation must be spec-driven, not only self-defined.
- If you write a helper validator, make it explicitly check the task's stated requirements: exact filenames/paths, sampled-index conventions, allowed labels, full interval/frame coverage, NPZ key schema, CSR consistency, and any mandated completion protocol.
- Do not treat a self-authored/helper validator as sufficient evidence by itself. After it passes, still run at least one independent parser-based check that reopens the actual JSON and NPZ outputs directly and compares them to the external task contract.

- Do not treat messages like `validated N frames`, `passed`, or spot-checking a snippet as sufficient unless those checks are directly tied to the external task specification.
- Base the success decision on the original task contract plus semantic inspection, not on internal consistency checks alone.

Use parser-based checks as the default evidence standard:
- Do not rely on `head`, partial `cat`, truncated stdout, or one representative NPZ key as evidence of correctness.
- Preserve the proven closeout pattern: generate both artifacts, run a lightweight validator/programmatic check, then inspect the real deliverables directly before finalizing.
- Validation is only sufficient when it covers the full written artifacts end-to-end after the latest successful rerun.

- Parse `/root/pred_instructions.json` programmatically with `json.load(...)` and validate the complete structure; do not rely on `head`, `sed`, `cat`, or partial stdout.

- Validate the full JSON content, including complete interval coverage through the final sampled-frame index, allowed-label legality, and `Stay` exclusivity; partial prefix inspection is insufficient.
- Load `/root/pred_dyn_masks.npz` with NumPy and enumerate/check the full key set, `shape`, representative dtypes, and CSR consistency programmatically.

- Confirm full contiguous per-frame coverage and mask plausibility programmatically; checking only that a few expected-looking keys exist is insufficient.
- Do not treat inspection of one representative NPZ key or a partial file print as sufficient validation.
- If any validation output is truncated, cut off mid-string, or only shows a sample, treat validation as incomplete; rerun a narrower parser-based check that finishes cleanly and explicitly reports full-file success/failure.
- After an OpenCV/mask-processing fix, validate not just NPZ key counts but also the affected mask encoding path: confirm CSR `data` is binary in meaning, indices are in range, and empty/full-frame masks are not being produced systematically without justification.

- If a command output shows a cut-off string, unterminated fragment, or otherwise truncated content, assume validation is incomplete and rerun with a direct parser or narrower explicit check.


Also verify the interaction contract is complete: if the task required a specific action syntax or exact completion token, ensure your final response uses that exact form rather than a narrative summary.
Hard-stop final-response rule:
- If an exact completion token/string is required, do not end with a success summary, artifact recap, or validator result.
- End with the exact required token/string and nothing else.
- Before sending it, explicitly confirm to yourself that all prior tool calls used the required schema/tool names exactly; successful self-validation of outputs never overrides protocol requirements.

If either required artifact is missing, unreadable, stale from an earlier failed run, or replaced by preprocessing outputs, do not finalize; resume the pipeline and regenerate the true deliverables first.


- Do not claim success from truncated/partial stdout or from output-file existence alone; confirm the main analysis run completed successfully end-to-end.
- If any displayed JSON/text output appears cut off mid-string, mid-list, or mid-object, treat that as a validation failure until you re-read the full file and successfully parse it.
- Treat `exit code 0`, `Done`, or similar logs as preliminary only. Final success requires successful parser-based validation of both artifacts after the last rerun.
- Treat any verification command that exits nonzero or raises an exception as failed/incomplete verification, not a pass.
- If a check fails because of a missing dependency or other error, rerun with a dependency-free check that covers the same requirement or continue fixing the issue.


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
- CSR invariants hold for every sampled frame: `indptr` length is `H + 1`, `indptr` is nondecreasing, `indptr[-1] == len(indices) == len(data)`, and all `indices` lie in `[0, W)`

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
- Prefer one focused local validator script/command for repeatability instead of ad hoc spot checks. Make it recompute or accept the metadata-derived sampled-frame count, parse the full JSON, enumerate all NPZ keys, and fail closed on any mismatch in coverage, indexing, labels, CSR consistency, or cross-file count/shape alignment.
- After that validator passes, produce a concise human-readable audit summary: sampled-frame count, number of merged JSON intervals, last covered sampled index, and confirmation that NPZ keys span `f_0_*` through `f_{N-1}_*`. If this summary looks inconsistent with the parsed files, treat the run as failed and investigate.

- Perform one cross-check tying both outputs together: if there are `N` sampled frames, JSON intervals must cover sampled indices through the final frame and NPZ must contain `f_0_*` through `f_{N-1}_*`.
- Do not trust a terminal/file-view snippet as proof of correctness; displayed output may be truncated. Prefer full parser-based checks over spot checks.
- Perform an independent indexing audit against the task specification, not your internal sampling list.
- If the previous execution failed, first confirm a later run completed successfully for the current code before trusting any existing output files.
- Confirm completion by evidence, not intent: the log should show actual commands that generated `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz`, followed by inspection of those files.
- If the runtime environment mandates a strict action format or final completion string, verify your response format before every tool call and end exactly as required.


- Perform a protocol-compliance check before finishing: confirm every tool call used the required schema exactly, confirm commands were explicit and auditable, and confirm the final message will be the exact required completion token/string.
- Do not finalize from file existence, a head/tail print, a few sampled entries, or a helper validator's summary line alone.
- Minimum acceptance checks are mandatory: parse the full JSON programmatically and verify all interval keys, label values, legality rules, and full coverage through the final sampled-frame index; enumerate NPZ keys programmatically and verify the complete contiguous set `f_0_*` through `f_{N-1}_*`, plus CSR consistency for every frame; cross-check that the sampled-frame count used for JSON coverage matches the NPZ frame count.
- Validation commands must be real executable checks, not placeholder prose inside `python -c` or shell comments. If you claim to have checked keys, shapes, coverage, or consistency, the issued command should visibly perform those checks.
- Treat helper validation as assistance, not authority: after any helper validator passes, still reopen the real deliverables directly and compare them to the explicit task requirements.
- Keep claims strictly bounded to observed evidence. If output was truncated or a check was partial, rerun a narrower parser-based validation and do not claim full success yet.
- If a generated script crashed on an OpenCV or mask-processing call, patch the exact failing API usage, rerun successfully, and verify the stored masks on the affected path are binary in meaning and serialize to internally consistent CSR arrays before trusting regenerated artifacts.
- Make the validator fail closed: if JSON parsing raises an error, NPZ loading raises an error, any check is ambiguous because output was truncated/noisy, or visible evidence covers only part of the required checks, regenerate or revalidate before finalizing.
- If you corrected a format, indexing, naming, or shared-schema bug, re-open and validate the JSON **and** the NPZ after the rerun; do not assume a fix propagated to the other artifact.
- Before finalizing, ask: did I actually run the analysis pipeline that generated `/root/pred_instructions.json` and `/root/pred_dyn_masks.npz` in this session, and did I directly inspect those regenerated artifacts? If not, the task is not complete.

- For compressed motion output, perform one explicit reconciliation check: derive `N` sampled frames from metadata, verify uncompressed transitions would total `N-1`, and verify the written merged intervals are in sampled-index space and collectively span the same sequence through `N-1`.
- Fail closed on incomplete verification evidence. If validation output is truncated, cut off, paged, or stops before proving the required fact set, do not infer success; rerun a narrower parser-based check that completes visibly.
- Apply the same rule to any motion-analysis or semantic-inspection output: if a printed interval list, label summary, or validator report is truncated, do not convert it into a definitive narrative until you obtain complete evidence.
- Add one explicit transcript-level audit before finishing: verify that the observed commands included the real analysis pipeline producing motion labels and dynamic masks, not just reconnaissance or preparation commands.
- Confirm the final artifact paths used during the run were explicitly authorized by the task/environment, especially if they are under `/root`, and verify that every file you created during the run was written in an allowed directory under the environment's filesystem rules.
- Add a final yes/no contract audit before concluding: did every tool interaction use the exact environment-mandated wrapper/tool name/schema, and will the final response be exactly the required completion token/string with no extra text? If either answer is not an explicit yes, do not finalize.



