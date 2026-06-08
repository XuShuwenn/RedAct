---
name: multilingual-video-dubbing
description: "Create multilingual video dubbing with TTS, audio normalization to ITU-R BS.1770-4, and synced video output."
---

# Multilingual Video Dubbing

## When to Use

- Dub video with translated speech


## When to Use

## Task-Specific Runtime Protocol

- If the task message specifies a required tool/action syntax, JSON envelope, waiting behavior, or exact completion token, follow that runtime protocol exactly for the entire run.
- Do not substitute alternate tool-call formats or a natural-language finish when the task requires a specific completion string.
- Treat interface/protocol compliance as a blocking requirement equal to the media deliverables.
- Before the first tool/action, identify the exact task-required action syntax, message envelope, waiting behavior, and completion token, then use that exact format for the entire run.
- If the runtime specifies one allowed action schema or wrapper, use only that exact format on every step; do **not** switch to alternate tool-call syntaxes, undeclared tools, XML-style tags, pseudo-tool markup, markdown-wrapped pseudo-actions, or default assistant narration.
- For shell actions, provide full concrete executable commands with real paths and arguments; do **not** send placeholders or prose such as `inspect metadata`, `run TTS generation`, or `ffmpeg ...`.
- Keep any required progress or state payloads syntactically valid and current; do not emit truncated JSON, partial strings, or stale status.
- Treat protocol drift as fatal: an otherwise correct dub does not count if tool calls, progress payloads, or the completion message use the wrong format.
- End the run only with the exact completion token or final action required by the task after verification is complete, with no extra prose when an exact terminator is required.

## Critical Requirement

- Generate new target-language speech audio for the dub; do not reuse or extract the original source speech as a fallback.
- Use `/root/reference_target_text.srt` and `/root/target_language.txt` in the actual TTS generation pipeline, not only in `report.json`.
- If you cannot produce target-language speech, stop and report the blocker rather than shipping source-audio output as a dubbed result.

- Normalize audio to ITU-R BS.1770-4 standard
- Sync audio with video within tight tolerances

- Do not present the task as completed if the only available TTS path that actually runs is below the requested human-level quality; stop and report that human-level dubbing is blocked in the current environment rather than shipping a nominal final dub.

- Do **not** start from a fallback plan that reuses, extracts, normalizes, or remuxes source speech from `/root/input.mp4` as the dubbed track. The dubbed speech must be newly generated from `/root/reference_target_text.srt` in the target language.
- Source audio may be inspected for reference only; it is never an acceptable substitute for target-language speech content.
- If no validated human-quality target-language TTS path is feasible locally, stop and report that dubbing is blocked. Do **not** ship source-derived audio plus metadata as a nominal dub.

## Input Files

- `/root/input.mp4`: Source video
- `/root/segments.srt`: Time windows for speech
- `/root/source_text.srt`: Original transcript
- `/root/target_language.txt`: Target language code
- `/root/reference_target_text.srt`: Reference translation


## Input Files

## Task Grounding Before Workflow

- Before inspecting tools or launching TTS, confirm the current task actually requires multilingual dubbing and identify the exact required deliverables, required paths, and any acceptance constraints stated in the task message.
- Ground your plan in the task's explicit requirements plus the provided canonical inputs/outputs in this skill; do not assume extra deliverables or a different objective.
- If the task message adds or overrides filenames, output names, protocol, waiting behavior, or completion rules, adopt those exact requirements before starting the media pipeline.
- If the visible context is insufficient to identify the deliverable, stop and resolve that ambiguity before spending time on engine setup or long generation runs.
## Required Workflow

1. Choose a TTS path only after confirming it works with local assets already present.
2. Before writing a full generation script, verify the actual local TTS API and assets: import the package or run its CLI help, list available voices or languages if possible, and complete one minimal synthesis call with the exact voice, language, and settings you plan to use. Do not guess parameter names, language codes, or voice IDs from filenames, help text, or cache contents alone.
2a. That verification is not complete until it writes an actual readable audio file for a tiny target-language utterance. Import success, help output, or a voice-listing call alone does **not** prove the synthesis path works.
2b. Treat partial help text, source inspection, or model-file presence as insufficient proof. Before any full synthesis run, capture concrete evidence of the exact runnable command or API call, the selected voice or speaker ID, and target-language support for that installed tool.
2c. Treat local asset sufficiency as a decision gate. If expected model weights, voice data, tokenizer files, or config pieces for a candidate engine are missing, ambiguous, or mismatched, do not build a pipeline around that engine until you prove the discovered files are enough for offline synthesis with a real short sample.
2d. Use the smallest possible synthesis probe first: a very short utterance, the exact intended voice/language settings, visible progress or separated setup/inference steps if needed, and an immediate file probe on the written WAV.
2e. If you cannot list voices cleanly, then prove the exact intended configuration with a successful one-line short utterance using the same voice, language, and output format you plan to use later.
3. Use `/root/reference_target_text.srt` as the TTS text source for dubbed speech; use `/root/source_text.srt` only for source-language understanding and context, not as text to translate again during dubbing.
4. Run a tiny smoke test first using the actual delivery path: synthesize one very short utterance from the provided target-language content and prove you can produce `/outputs/tts_segments/seg_0.wav` as a readable 48000 Hz mono WAV.
4a. Make the first synthesis run timeout-aware and observable: use a very short utterance, emit progress around model load and synthesis, capture full stderr/stdout, and prefer a bounded command over an open-ended full-segment run.
4b. For the first smoke test, avoid long inline `python -c` one-liners for nontrivial TTS calls; use the tool's direct CLI or a tiny standalone script under `/outputs` so quoting and syntax are inspectable.
4c. If the first smoke test fails with a syntax error, malformed command, import error, hang, or attempted downloads, treat that as a blocker for the smoke test itself: fix that exact invocation or change approach before writing larger orchestration code.
5. Do not write orchestration scripts or launch a full multi-segment run until that smoke test has executed successfully and the file has been probed as readable.
6. The smoke-tested path must include all core stages on one short sample: synthesize target-language speech, convert or resample to 48 kHz mono WAV if needed, place it at the subtitle start time, mux a playable `/outputs/dubbed.mp4`, run a real loudness measurement, and generate a schema-valid `/outputs/report.json`.
7. Validate that minimal end-to-end path before scaling up.
8. As soon as one acceptable TTS path works, stop retrying alternative engines unless the result is unusable.
8a. Once one path has produced a readable target-language sample and can satisfy the task's stated quality requirement, treat that path as the default completion route and finish the end-to-end deliverables before any optional comparison.
8b. Do not reopen engine exploration after a successful fallback just to seek marginal quality improvement; only switch if the current proven path clearly fails a stated requirement such as target language, intelligibility, or explicit human-level quality.
9. Treat a readable target-language segment WAV as the pivot point: immediately complete resample or mono conversion, timeline placement, loudness normalization, muxing, and `/outputs/report.json` before attempting any optional engine comparison.
10. If a synthesis command times out, hangs, writes an empty file, produces an unreadable file, or cannot quickly list voices, load models, or produce a short sample, do not rerun the same path unchanged more than once. Make one meaningful mitigation first or switch to a materially different proven local method.
10a. Treat a timeout with no output artifact as a failed path, not as evidence the next identical rerun will work.
10b. Before any retry, inspect the failure point with a bounded check such as: import the library alone, load the model alone, list voices or languages, inspect the written script, capture full stderr, or synthesize a 1-line utterance with visible logging and a short timeout.
10c. A meaningful mitigation must change the evidence or execution path: for example shorter utterance, explicit voice ID, captured full stderr, a direct CLI invocation instead of a wrapper, observable progress around model load or voice listing, or a different verified engine. Reissuing the same hanging command with the same arguments is not a mitigation.
10d. After any failed or timed-out synthesis attempt, immediately check whether the expected artifact exists and is readable, inspect the captured error output, then either apply one concrete mitigation or abandon that path.
10e. After editing a script to add a fallback or disable a failing engine, prove the failing path is no longer active before a full rerun: inspect the changed invocation, run a tiny targeted test, and compare logs for a different code path.
10f. If the rerun shows the same traceback, same failing engine name, or same call stack, assume the original path is still executing. Stop, fix the control flow, and verify the branch change instead of repeating the run again.
10g. A failed smoke test is a blocking event for that engine. Do not proceed to full orchestration scripts, multi-segment generation, or final-pipeline assumptions until the short sample path is proven.
10h. A second timeout or hang on the same TTS path is a pivot point, not a cue for another near-identical rerun. Change strategy immediately: reduce scope to a tiny direct sample, switch to a lighter validated local method, or stop and report the blocker if no compliant human-quality path works.
10i. When switching to a fallback engine or CLI, prove it first with the smallest direct invocation available before writing a new wrapper or orchestration script.
10j. If an inline Python snippet fails twice with the same syntax or indentation error, stop retrying that pattern. Switch to a simpler validated method such as `ffprobe`, `jq`, shell arithmetic, or a tiny saved script under `/outputs`.
11. If a candidate fallback is known to be robotic, synthetic, or otherwise below human-level quality, do not use it for final deliverables; stop and report the blocker instead of shipping non-compliant dubbed audio.
12. Prefer direct available CLI or tool workflows for the first pass; add wrappers or broader automation only after the full pipeline is confirmed.
13. If a tool is visibly available, try the simplest direct synthesis invocation for one short utterance before writing a Python wrapper around it.
14. Inspect generated shell commands, ffmpeg invocations, and helper scripts before execution. If a command or file write looks truncated, malformed, or partially emitted, rewrite it before running.
14a. When you create or edit a helper script, first read back the saved file contents from disk before patching or rerunning it.
14b. Do not apply edits against placeholders, summaries, or assumed prior code; ground every fix in the actual visible file contents and current traceback.
15. If any synthesis, `ffmpeg`, `ffprobe`, or loudness command returns an error, warning, or visibly truncated output, stop and verify the expected artifact immediately with `test -s`, `ffprobe`, or a readable parse before using it downstream.
16. Fit each segment to its subtitle window using `rate_adjust`, `pad_silence`, or `trim`, then normalize and mux the final dubbed audio.
17. Build the dubbed track on an absolute timeline from `/root/segments.srt` using silence insertion or offset-based mixing, not default sequential concat.
18. After any duration-changing step on a segment or final mix, re-probe the written file and update all downstream timing from that probe before continuing.
19. Use one verified timing basis throughout: subtitle windows from `/root/segments.srt` for target placement, and final probed delivered artifacts for actual `placed_*`, `drift_sec`, and duration values in `/outputs/report.json`.
20. After any regeneration of `/outputs/tts_segments/seg_0.wav`, `/outputs/dubbed.mp4`, or `/outputs/report.json`, rerun final verification on those exact saved paths before finishing.
21. Keep debugging bounded: every TTS investigation should either prove a working short sample quickly or be abandoned so the full delivery pipeline can continue.
22. Do not stop at intermediate artifacts; finish all listed outputs.

23. After any recovery, fallback, package change, or engine switch, immediately re-probe the regenerated artifact and confirm the actual container or codec, sample rate, channels, duration, and readability match the pipeline assumptions before using it downstream.
24. If the recovered file format differs from the expected working format, either convert and re-probe it first or change the pipeline explicitly; do not continue on stale assumptions.
25. Treat `file exists` as insufficient recovery evidence. Require a successful probe of the exact saved file before any `ffmpeg` filter, timing, normalization, or mux step that depends on it.
26. Before rerunning any script, inspect it for truncation, placeholder text, quoting problems, or indentation issues; prefer short one-purpose commands over multi-line inline Python for durations, JSON updates, and report calculations.
27. If you regenerate any delivered artifact after a prior verification pass, invalidate all previously derived metadata and rerun the full final probe, measurement, and report-generation sequence from the new files.
28. When you create or edit a helper script, write literal executable code to disk. Do not use placeholder text or meta-descriptions in file contents.
29. Before executing any newly written helper script, open or print the saved file and confirm it contains real code rather than placeholders, truncated text, or partial content; if possible, run a lightweight validation such as `python -m py_compile` first.
30. Keep one canonical script path per approach during debugging. If you switch approaches, either overwrite the same tracked script path or explicitly retire the old one; do not reason about one filename while executing another.
31. If any pipeline run exits nonzero or its output stops before an explicit completion signal from the script, treat the run as failed or incomplete. Capture the real stderr/stdout, inspect the relevant code, and debug from that evidence before editing.
32. An empty `/outputs/tts_segments/` directory or unreadable `seg_0.wav` means the TTS path is still unproven; stop downstream assembly work until that prerequisite is satisfied.
33. Before declaring success, validate semantics as well as structure: inspect representative target text passed into TTS and compare at least one generated segment or logged utterance against `/root/reference_target_text.srt` to catch truncation, wrong-language output, or partial-text bugs.
34. If any visible output suggests truncated or semantically wrong dubbing content, stop and fix text handling before relying on file existence, codec, duration, or stream checks.
35. After preflight confirms the inputs and one local TTS path exists, prioritize the smallest end-to-end pipeline that can create the required deliverables; do not spend the run on package inspection, model archaeology, or multiple diagnostic scripts.



## Required Preflight

## Required Preflight

- Read every listed input file before generating anything: `segments.srt`, `source_text.srt`, `target_language.txt`, and `reference_target_text.srt`.
- Derive source-language and transcript context from `source_text.srt`; do not rely only on the translated reference text.
- Confirm segment count and timing windows up front so `report.json` can be filled completely.

## Output Files

1. `/outputs/tts_segments/seg_0.wav`: TTS audio (48000 Hz, Mono, human quality)
2. `/outputs/dubbed.mp4`: Video with dubbed audio
3. `/outputs/report.json`: Dubbing report

- Treat these paths as canonical deliverables. Create and report exactly these files unless the task explicitly requests different names.
- Reuse the same absolute paths in commands, validation, and final reporting; do not invent alternate output locations or renamed files at the end.
- Store any intermediate artifacts only under allowed task directories (for example `/outputs/tts_segments/`); do not use `/tmp` or other unapproved paths.

- Keep one canonical path map for deliverables from the start and reuse those exact paths in every command, probe, `report.json` write, and final response.
- Do not relocate, rename, or duplicate required deliverables to alternate top-level paths during handoff. In particular, keep `seg_0.wav` at `/outputs/tts_segments/seg_0.wav` and write `dubbed.mp4` and `report.json` directly to `/outputs/`, not under `/outputs/tts_segments/`.
- Use a final path checklist before completion: probe exactly `/outputs/tts_segments/seg_0.wav`, `/outputs/dubbed.mp4`, and `/outputs/report.json` and ensure those are the files referenced in validation and the final response.



## Execution Guardrails

- Keep every intermediate media file, helper script, probe output, and scratch artifact inside permitted task directories such as `/outputs` and its subdirectories. Never use `/tmp` for convenience staging, and never place generated scripts, reports, temp code, or convenience files under input locations such as `/root` unless explicitly allowed.
- After each expensive generation step, check for the expected output file immediately before planning downstream steps.

- Treat input locations and writable locations separately. Do not assume a readable input directory is also writable.
- Every shell invocation must be a concrete executable command with full arguments and absolute paths. Do **not** issue narrative placeholders such as `ffmpeg ... normalize audio ...`, `ffprobe ...`, or `run the workflow`.
- Every file you create must contain actual executable code or actual final JSON/text, not prose like `script that reads SRT and generates TTS`.
- Before creating any helper script, temp file, or edited artifact, confirm the destination is inside an explicitly allowed writable directory. If write permission is not clearly allowed, use `/outputs` or another task-approved workspace only.
- Do not create convenience scripts, temp files, or rewritten assets under `/root` unless the task explicitly says `/root` is writable.
- Before running a generated script, inspect it once for placeholders, ellipses, TODO text, truncated quoting, or pseudo-instructions and rewrite it if any appear.
- Immediately after each edit to a helper script or command file, re-open the modified region and run a targeted validation appropriate to the file, such as `python -m py_compile`, `bash -n`, or a direct readback, before continuing.
- If an edit result looks truncated, malformed, or unexpectedly unchanged, stop and repair the file before rerunning the pipeline.
- Name helper scripts descriptively and keep one canonical script path per purpose under `/outputs` (for example `/outputs/run_tts_probe.py`). After writing a script, verify the saved path and invoke that exact same path.
- For any slow synthesis or probe command, redirect stdout/stderr to a known log file under `/outputs`, print progress markers before expensive stages, and inspect the log plus exit status after the run instead of rerunning blindly.
- Do not let debugging sprawl into multiple partially overlapping test files. Replace or update the existing canonical helper script unless a new file is materially different and necessary.


## Failure Diagnosis

## Failure Diagnosis

- When a script or media command fails, first capture the complete stderr or traceback to a file in an allowed directory and inspect the referenced line numbers or failing command before editing code.
- Do not patch based on truncated console output, partial traceback lines, or guesses about which stage failed.
- Use a short loop: rerun with full error capture -> inspect the exact failing code or command -> make one targeted fix -> rerun verification.
## Execution Guardrails

- Create any helper scripts or temporary artifacts only in explicitly writable directories (typically under `/outputs` if allowed by the task). Do not write convenience files under restricted locations such as `/root` unless the task explicitly permits it.
- Use the exact absolute input/output paths provided by the task.

## Audio Requirements

- ITU-R BS.1770-4 standard (LUFS measurement)
- Sample rate: 48000 Hz
- Channels: Mono
- Human-level quality

- If your available TTS method is known to be robotic or below human-level quality, do **not** use it as the final deliverable. Treat that as a blocker and report that the quality requirement cannot be satisfied with the available tool.
- Do **not** knowingly ship low-quality fallbacks such as basic system voices when the task explicitly requires human-level dubbing.
- If you explicitly determine a voice or engine does not meet the required quality, do not later use that same method as the final pipeline unless you have new concrete evidence that the quality issue was resolved.
- Do not claim LUFS compliance until you have a successful measurement result in tool output.
- Extract `measured_lufs` from a completed final measurement on the delivered audio and parse that numeric result directly into `/outputs/report.json`; do not copy a guessed value from rolling logs, truncated console output, or an earlier intermediate pass.
- If loudness analysis or parsing fails, treat loudness as unverified, fix the command, and rerun before writing `measured_lufs` to `/outputs/report.json`.
- Measure the finished output and bring integrated loudness to the intended target (typically about -23 LUFS); do not accept clearly off-target results without another correction pass.
- Re-measure after normalization or muxing as needed to confirm the final delivered artifact, not an intermediate file, is compliant.
- Do **not** claim normalization success from intended filter settings alone. Require a separate post-normalization measurement that returns a numeric integrated LUFS value before reporting compliance.
- If final integrated loudness is materially off the intended target, do not accept it as compliant; adjust gain or rerun normalization, then re-measure the delivered artifact.
- For FFmpeg `loudnorm`, use a real two-pass workflow: run pass 1, capture the reported JSON stats, then run pass 2 with those exact measured values. Do not invent or reuse `measured_*` parameters.
- Preferred normalization pattern: run pass 1 on the assembled pre-final dub, parse the emitted loudnorm JSON, run pass 2 with those exact measured fields, then measure the delivered final artifact again and record that numeric LUFS result in `report.json`.
- Never use fallback constants, guessed LUFS values, or parser defaults such as `-23.0` when measurement fails. Leave compliance unverified, fix the command or parsing, and re-measure.
- Do not replace BS.1770 loudness normalization with simple gain changes such as `volume=...` and still claim BS.1770-4 compliance.

- If the measurement output shows an empty label such as `Integrated loudness:` with no numeric value, treat loudness as unverified and rerun or change the measurement method.
- Do not write `measured_lufs`, `-23.0`, or any other fallback value into `/outputs/report.json` unless the verification output explicitly returned that numeric result for the delivered artifact.
- Do not claim BS.1770-4 compliance from partial `ebur128` progress lines, rolling console updates, or an analyzer run whose final summary is truncated.
- Require one confirmed final numeric integrated loudness result for the delivered artifact before writing `measured_lufs` or stating compliance; if needed, redirect the analyzer output to a file and parse that complete result.
- Treat the loudness check as a release gate, not a reporting field. If the final measured loudness is still materially off target after a correction pass, do **not** finalize the deliverable as compliant; either correct it or explicitly report that compliance was not achieved.
- If loudness output is truncated, missing, or non-numeric, do **not** substitute a plausible LUFS number. Rerun measurement with redirected or captured output until you obtain a parseable numeric value from the delivered artifact.
- Never repair an incorrect `measured_lufs` by hand-editing `report.json`; regenerate the value from a successful measurement of the final output.


## Timing Constraints

- placed_start_sec matches window start within 10ms
- End drift (drift_sec) < 0.2 seconds
- Prefer content-preserving duration_control: "rate_adjust" or "pad_silence"
- Choose the least invasive duration control that satisfies the window: if speech is short, prefer `pad_silence`; if slightly long, prefer `rate_adjust`; use `trim` only for removable leading/trailing silence.
- Use "trim" only to remove leading/trailing silence, never to cut spoken content to fit a window.
- If TTS exceeds the subtitle window, do not force-fit by truncating words; instead use rate adjustment, re-synthesis with shorter phrasing, or split delivery while preserving the full target utterance.
- Do not emit any other `duration_control` value in code or `report.json`; never use placeholders like `no_adjust`.
- Treat start alignment and end drift as separate checks: start placement must be within 0.01 s of the window start, while end drift must be < 0.2 s relative to the window end.
- Do not describe end drift as the 10 ms tolerance. The 10 ms rule applies only to start alignment; end drift has its own < 0.2 s requirement.
- Build the final dubbed track on an absolute timeline using each segment's window start time; do not assume segments are contiguous.
- Insert silence or mix each segment at its offset before muxing to video.
- If segment windows have gaps or start after 0, simple concat is incorrect.
- Derive each target window from `/root/segments.srt`; do not hardcode segment or video durations.
- Compute `placed_start_sec`, `placed_end_sec`, and `drift_sec` from the final adjusted audio actually muxed into the video, not from raw TTS output before trimming, padding, or rate adjustment.
- After any transform that can change duration or placement (normalization, resampling, encoding, padding or trimming, muxing), re-measure the final artifact and base report values on that measurement, not on intermediate files.
- Do not assume loudness normalization preserves exact duration; verify the final WAV duration after normalization before computing `placed_end_sec` or `drift_sec`.
- Preserve the full required delivery duration when muxing dubbed audio back into video; do not use options such as `-shortest` if they can truncate the output below the latest placed speech end or shorten the visual stream.
- If final probing shows the container ends before the latest required `placed_end_sec` or `window_end_sec`, the deliverable is invalid. Extend or freeze-pad the video or otherwise lengthen the output, remux, and re-measure before continuing.
- Compare the final `/outputs/dubbed.mp4` duration to `/root/input.mp4` after muxing and do not accept a shortened visual duration caused by audio-length-driven truncation.
- Never mix timing taken from an intermediate WAV with duration taken from the muxed MP4 in the same report row or summary fields.
- Do not validate timing by rereading `report.json` fields you wrote earlier. Measure actual rendered media or final segment files, then compute `placed_start_sec`, `placed_end_sec`, `tts_duration_sec`, and `drift_sec` from those measurements.
- Preserve millisecond-level precision in outputs and `report.json`; do not round timing fields to 2 decimals. Keep at least 3 decimal places for `window_start_sec`, `window_end_sec`, `placed_start_sec`, `placed_end_sec`, `window_duration_sec`, `tts_duration_sec`, and `drift_sec`.
- Do not describe sync as exact or perfect unless you measured the final output and it meets both constraints.

- Do not stop at `close enough` if measured end drift still violates the required target window behavior. If padding, retiming, or re-synthesis can reduce the remaining mismatch without cutting speech, apply it and then re-measure from the saved final artifact.
- After any timing-affecting regeneration, recompute `placed_end_sec` and `drift_sec` from the final delivered media; never keep earlier timing values because they were previously within tolerance.


## report.json Fields

```json
{
  "source_language": "en",
  "target_language": "ja",
  "audio_sample_rate_hz": 48000,
  "audio_channels": 1,
  "original_duration_sec": 12.34,
  "new_duration_sec": 12.34,
  "measured_lufs": -23.0,
  "speech_segments": [...]
}
```

Use this top-level schema exactly. Do not replace it with custom keys such as `workflow_metadata`, `video_info`, `audio_info`, or `segments`.

- Treat `report.json` as a summary derived from final outputs, not as evidence that requirements are met.
- Populate report values from the final written artifacts only (`/outputs/tts_segments/*.wav` and `/outputs/dubbed.mp4`), not from intermediate adjusted, normalized, or temp files.
- Re-probe after the last normalization, resample, encode, and mux step before writing `report.json`.
- Populate `tts_duration_sec`, `placed_start_sec`, `placed_end_sec`, `drift_sec`, sample rate, channel count, `original_duration_sec`, and `new_duration_sec` from those final probes; do not leave stale or nominal pre-transform values in the report.
- For each item in `speech_segments`, record the delivered segment data using the required field names and final values after any `rate_adjust`, `pad_silence`, or `trim`. In particular, use `duration_control` and no other value set.
- Populate `measured_lufs` only from a successful post-normalization measurement of the delivered output audio.
- Do not manually overwrite `report.json` metrics to match expected targets; if a value is implausible, rerun or fix the measurement or parsing step and record the real result.

- Build `report.json` from the required top-level schema first; map any internal variables into exactly these keys before writing the file.
- Do not write alternate top-level objects such as `workflow_metadata`, `video_info`, `audio_info`, or `segments`.
- Build `/outputs/report.json` only after a last-pass probe of the final deliverables. Prefer parseable commands whose numeric output you can read back directly.
- Probe the actual final deliverables directly: read `original_duration_sec` from `/root/input.mp4`, `new_duration_sec` from `/outputs/dubbed.mp4`, and per-segment delivered timing fields from the final `/outputs/tts_segments/*.wav` or final rendered timeline after all transforms.
- Do not copy duration or placement values forward from earlier ffmpeg logs, adjusted intermediates, or pre-normalization files.
- In each `speech_segments` entry, use the required field names exactly; use `duration_control`, never aliases such as `duration_strategy`.
- Enforce allowed `duration_control` values on every code path and final validation: only `rate_adjust`, `pad_silence`, or `trim` are permitted.
- Compute each segment's `tts_duration_sec`, `placed_end_sec`, and `drift_sec` only after the final rate adjustment, padding, or trimming step for the exact audio that is placed on the timeline.
- Copy numeric report values directly from final probe or measurement output or computed final placement data; do not hand-round, truncate, retype approximate values, or leave placeholder compliance values such as `-23.0` when the actual measured result differs.
- Preserve exact measured values internally, then write report timing fields with at least 3 decimal places.
- If a later verification pass yields updated loudness, duration, sample rate, channel, or timing values, regenerate `/outputs/report.json` from those final measured values before finishing.
- Check internal consistency before saving: top-level durations and each segment's `tts_duration_sec`, `placed_end_sec`, and `drift_sec` must agree with the final verified media measurements.

- Write `/outputs/report.json` as actual serialized JSON only; never write prose placeholders, summaries, TODO text, schema descriptions, or planning notes in its place.
- Build the full report object in memory from measured final values, then serialize that object to `/outputs/report.json` in one write.
- Immediately validate the written file with a real parser such as `python -m json.tool /outputs/report.json` or equivalent before any completion claim.
- If JSON parsing fails, the report is invalid. Rewrite the file with valid serialized JSON and rerun validation; do not treat file existence alone as success.
- Do **not** patch `/outputs/report.json` with raw string replacement such as `.read().replace(...)`. Load the JSON, recompute or re-read the intended field from final measured artifacts, update that key structurally, then write the full file back.
- If `/outputs/dubbed.mp4`, any final segment WAV, or the measured loudness value changes, rebuild the entire `report.json` from fresh probes of the current artifacts. Do not patch only one or two fields while leaving earlier top-level durations or segment timings in place.
- If any report field is wrong or stale, regenerate the affected values from final probes or measurements; do not perform blind textual substitutions in the serialized JSON.
- When fixing one field, validate the whole JSON after rewriting so the report remains schema-valid and internally consistent.
- Before finishing, perform a consistency pass: `new_duration_sec`, `measured_lufs`, and every segment timing field must all come from the latest generated outputs from the same run.



## Final Validation

- Treat protocol compliance as part of final validation: before the final response, re-read the task/runtime instructions and confirm the required completion format. If an exact terminator string is specified, use it exactly with no extra summary, explanation, recommendations, bullet points, or file listings after it unless the task explicitly allows that.
- Treat any nonzero exit code, traceback, parse failure, unreadable required output, empty verification output, missing tool, omitted required field, or truncated terminal view during final checks as a blocking failure. Rerun the failed validation itself on the canonical saved path and require a passing result before finishing.
- Do not state a numeric loudness result unless the measurement command completed successfully and emitted that numeric value in captured output.
- If a validation or parsing helper is unavailable, switch to another concrete verifier available in the environment rather than assuming success.
- After any late fix or regeneration of required deliverables, re-verify those exact saved paths again and regenerate `/outputs/report.json` if the new measurements differ.
- Validate report contents, not just existence: confirm the saved file is valid JSON, uses the required top-level schema, and contains populated measured values rather than placeholders, TODO text, template language, or free text.
- If you created helper scripts used in the pipeline, inspect their saved contents directly before relying on them.
- Use a final two-part checklist: first verify required artifacts, JSON parsing, media probes, loudness, timing, directory restrictions, and report consistency; then perform the exact runtime-required completion action or token.
- Verify that any helper script you executed is the same file you most recently wrote; if needed, print the script path, checksum, or read back the first lines before running.
- If a script crashed, inspect the full traceback or captured stderr before editing or changing tools; do not continue from a summary such as 'timed out' or 'failed'.
- Use your own verification results as blocking gates: if target-language synthesis did not occur, if the final audio is source-derived, or if measured loudness is still outside the required target or tolerance, do **not** declare success.
- Require positive evidence that the main dubbing pipeline completed successfully: zero exit status and an explicit final success or completion signal from the script or command, not just partial progress logs plus existing files.
- Perform one semantic spot-check before completion: compare a representative subtitle line from `/root/reference_target_text.srt` to the text actually fed to synthesis or any logged/generated transcript snippet, and reject outputs showing truncation or obvious mismatch.
- If the only working synthesis path is known, stated, or strongly suspected to be below the required human-level quality, do not present the outputs as ready or compliant; report the blocker instead.
- Do not end on a plan or pending retry. Either produce the required outputs and completion token, or explicitly report the blocker in the required runtime format.

## Final Validation

Before declaring success, verify the delivered final files `/outputs/dubbed.mp4` and `/outputs/report.json`, not intermediate renders.

- Verify every critical media command (especially `ffmpeg`) actually succeeded before proceeding. Do not treat truncated progress output as success; confirm a zero exit status and or probe the produced file.
- Verify `/outputs/report.json` with a full parse, not a partial terminal view. Prefer `python -m json.tool /outputs/report.json` or equivalent JSON parsing.
- If a `cat` or console display is truncated, do **not** assume the file is correct; re-check with a method that guarantees complete validation.
- Before finishing, confirm all required outputs exist and are readable: `/outputs/tts_segments/seg_0.wav`, `/outputs/dubbed.mp4`, and `/outputs/report.json`.
- After the final mux, re-probe `/outputs/dubbed.mp4` and confirm it exists, is readable, has the expected streams, and contains 48 kHz mono audio.
- Measure `/outputs/dubbed.mp4` duration and confirm it preserves the required delivery duration and covers the latest segment end.
- Measure loudness on the final normalized audio used in `/outputs/dubbed.mp4` and write that value to `measured_lufs`.
- Recompute each segment's actual duration, `placed_start_sec`, `placed_end_sec`, and `drift_sec` after all duration adjustments, and check placement against the SRT windows on the finished output.
- Confirm `/outputs/report.json` matches the required schema and field names exactly.
- Confirm all created files, including intermediates, stayed within permitted directories.
- If you use FFmpeg options such as `-shortest`, verify they did not truncate required dubbed speech before accepting the output.
- If loudness measurement, timing verification, or target-language synthesis fails, report the limitation explicitly instead of claiming compliance.
- If any check fails, fix the media pipeline and re-run verification before finishing.

## Tips

- Use TTS engine for speech synthesis

- Start with one very short synthesis probe to verify the chosen TTS stack and confirm the WAV is created and readable before full generation.
- If a TTS command fails, times out, or produces no file, do not rerun it unchanged; inspect the full error output and add visible progress or split the step so stalls are diagnosable.
- For implementation patterns for timeline assembly and loudness verification, read [references/assembly-and-verification.md](references/assembly-and-verification.md).
- For safer patterns that avoid fragile inline Python when probing durations or rebuilding `report.json`, read [references/probing-and-report-refresh.md](references/probing-and-report-refresh.md).

- pyloudnorm for LUFS normalization
- FFmpeg for audio/video mixing
- Check timing with soundfile/pydub


- Use `ffprobe`, soundfile, or equivalent probe tools after final render steps and treat those measurements as the source of truth for durations, sample rate, channels, streams, and other values written to `report.json`.
- Keep full-precision internal values for timing checks and `drift_sec`; round only for presentation if needed.
- If TTS is too long for a subtitle window, preserve full speech: adjust rate, split or re-synthesize phrasing, or pad or retime placement; do not declare success after cutting off words.
- Validate exact local assets before committing to a model: required weights, voice definitions, and target-language support must all be present.
- Do not assume nearby `.pth`, config, or partial model files are sufficient; prove the engine can actually synthesize the target language with the selected voice.
- Avoid long blocking generation as the first real test. Use a short timeout-safe sample run first; if initialization hangs or tries to download assets, abandon that path and use a confirmed local alternative.
- Prefer a minimal end-to-end pipeline: generate segment audio, validate duration and sample rate, assemble the final mix, mux video, then write `report.json`.
- Prefer one working end-to-end pipeline over repeated tool or library probing.
- When a fallback path has already produced valid speech and the remaining work is assembly, normalization, muxing, and reporting, finish those downstream steps immediately instead of returning to TTS experimentation.
- Use additional engine exploration only when the current proven path cannot meet an explicit task requirement; otherwise completion takes priority over optional improvement.
- Before finalizing, verify each required input influenced the output: target text and language to synthesized speech, subtitles to placement, normalization step to measured loudness.
- Keep compliance claims literal: only say "ITU-R BS.1770-4 compliant" when you used a BS.1770-4 loudness method and verified the final output.
- Do not use fallback constants or hand-edited values for measured loudness, drift, or durations.
- If a verification command does not return a numeric or parseable value, treat the requirement as unverified and fix the pipeline before reporting completion.
- If an error traceback or analysis log is truncated, rerun in a way that captures full stderr or the final loudness summary before changing tools or reporting results.
- Before finishing, cross-check that `/outputs/tts_segments/seg_0.wav`, `/outputs/dubbed.mp4`, and `/outputs/report.json` actually exist.
- After TTS succeeds, explicitly finish the downstream steps: convert or resample to 48 kHz mono if needed, measure and normalize LUFS, mux audio with video, and write `/outputs/report.json`.

- Do not infer a voice or language configuration from help text, aliases, or partial source inspection alone; prove it with a short synthesis using the exact intended settings.
- Treat a 0-byte or unreadable TTS output the same as a failed run: inspect the error once, then change approach rather than repeating the same generation command.
- Prefer writing probe and loudness outputs to files, then parsing those files, when terminal logs may truncate long JSON or analyzer summaries.
- If a direct CLI path already demonstrates target-language support or available voices, prefer proving one short synthesis with that CLI over immediately writing a wrapper script.
- Keep the first probe timeout-safe and diagnostic: use a very short utterance, capture full stderr, and confirm whether the engine is loading locally or attempting network-dependent initialization.
- For long-running model or media jobs, make the first real run observable: emit progress around model load, voice listing, and sample synthesis so you can tell where it stalls before spending another full timeout window.
- Prefer a probe-driven verification loop: after each critical render or mux step, use `ffprobe` or equivalent to read back duration, sample rate, channels, and stream presence before continuing.
- A proven path is: synthesize from `/root/reference_target_text.srt` -> measure raw segment duration with `ffprobe` -> apply `pad_silence` or `rate_adjust` as needed -> run two-pass `loudnorm` -> verify final muxed output and report from final probes.
- A compact pipeline script is often the safest implementation pattern for this task because it keeps parsing, synthesis, timing adjustments, final probes, and JSON reporting derived from the same source of truth.
- Prefer FFmpeg for duration control and absolute timeline placement: adjust speech length, then place segments with offsets rather than manual concatenation logic.
- Once one short utterance succeeds, spend the next steps on resampling, placement, loudness verification, muxing, and report generation rather than additional engine exploration.

- For shell-based tasks, write the exact command you want executed, including concrete paths and arguments. Never substitute descriptive placeholders for executable commands.
- If a full synthesis script times out before creating `/outputs/tts_segments/seg_0.wav`, do not rerun that same script unchanged. First reduce it to the smallest observable check: import only, model-load only, or one very short synthesis call with the exact intended settings.
- When a command stalls, make the next probe more observable rather than bigger: use a one-line utterance, add progress prints around model load and synthesis, and capture full stderr/stdout.
- Do not treat cached weights, config files, or package presence as proof the engine is usable. Prove the actual inference path with a tiny readable output before launching the full script.
- For a compact safe pattern for writing and validating the report file, read [references/report-writing-and-blocking-validation.md](references/report-writing-and-blocking-validation.md).

