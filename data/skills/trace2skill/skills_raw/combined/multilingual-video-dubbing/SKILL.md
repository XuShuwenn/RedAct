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

## Critical Requirement

- Generate new target-language speech audio for the dub; do not reuse or extract the original source speech as a fallback.
- Use `/root/reference_target_text.srt` and `/root/target_language.txt` in the actual TTS generation pipeline, not only in `report.json`.
- If you cannot produce target-language speech, stop and report the blocker rather than shipping source-audio output as a dubbed result.

- Normalize audio to ITU-R BS.1770-4 standard
- Sync audio with video within tight tolerances

- Do not present the task as completed if the only available TTS path that actually runs is below the requested human-level quality; stop and report that human-level dubbing is blocked in the current environment rather than shipping a nominal final dub.

## Input Files

- `/root/input.mp4`: Source video
- `/root/segments.srt`: Time windows for speech
- `/root/source_text.srt`: Original transcript
- `/root/target_language.txt`: Target language code
- `/root/reference_target_text.srt`: Reference translation

## Required Workflow

1. Choose a TTS path only after confirming it works with local assets already present.
2. Before writing a full generation script, verify the actual local TTS API and assets: import the package or run its CLI help, list available voices or languages if possible, and complete one minimal synthesis call with the exact voice, language, and settings you plan to use. Do not guess parameter names, language codes, or voice IDs from filenames, help text, or cache contents alone.
3. Use `/root/reference_target_text.srt` as the TTS text source for dubbed speech; use `/root/source_text.srt` only for source-language understanding and context, not as text to translate again during dubbing.
4. Run a tiny smoke test first using the actual delivery path: synthesize one very short utterance from the provided target-language content and prove you can produce `/outputs/tts_segments/seg_0.wav` as a readable 48000 Hz mono WAV.
5. Do not write orchestration scripts or launch a full multi-segment run until that smoke test has executed successfully and the file has been probed as readable.
6. The smoke-tested path must include all core stages on one short sample: synthesize target-language speech, convert or resample to 48 kHz mono WAV if needed, place it at the subtitle start time, mux a playable `/outputs/dubbed.mp4`, run a real loudness measurement, and generate a schema-valid `/outputs/report.json`.
7. Validate that minimal end-to-end path before scaling up.
8. As soon as one acceptable TTS path works, stop retrying alternative engines unless the result is unusable.
9. Treat a readable target-language segment WAV as the pivot point: immediately complete resample or mono conversion, timeline placement, loudness normalization, muxing, and `/outputs/report.json` before attempting any optional engine comparison.
10. If a synthesis command times out, hangs, writes an empty file, produces an unreadable file, or cannot quickly list voices, load models, or produce a short sample, do not rerun the same path unchanged more than once. Make one meaningful mitigation first or switch to a materially different proven local method.
11. If a candidate fallback is known to be robotic, synthetic, or otherwise below human-level quality, do not use it for final deliverables; stop and report the blocker instead of shipping non-compliant dubbed audio.
12. Prefer direct available CLI or tool workflows for the first pass; add wrappers or broader automation only after the full pipeline is confirmed.
13. If a tool is visibly available, try the simplest direct synthesis invocation for one short utterance before writing a Python wrapper around it.
14. Inspect generated shell commands, ffmpeg invocations, and helper scripts before execution. If a command or file write looks truncated, malformed, or partially emitted, rewrite it before running.
15. If any synthesis, `ffmpeg`, `ffprobe`, or loudness command returns an error, warning, or visibly truncated output, stop and verify the expected artifact immediately with `test -s`, `ffprobe`, or a readable parse before using it downstream.
16. Fit each segment to its subtitle window using `rate_adjust`, `pad_silence`, or `trim`, then normalize and mux the final dubbed audio.
17. Build the dubbed track on an absolute timeline from `/root/segments.srt` using silence insertion or offset-based mixing, not default sequential concat.
18. After any duration-changing step on a segment or final mix, re-probe the written file and update all downstream timing from that probe before continuing.
19. Use one verified timing basis throughout: subtitle windows from `/root/segments.srt` for target placement, and final probed delivered artifacts for actual `placed_*`, `drift_sec`, and duration values in `/outputs/report.json`.
20. After any regeneration of `/outputs/tts_segments/seg_0.wav`, `/outputs/dubbed.mp4`, or `/outputs/report.json`, rerun final verification on those exact saved paths before finishing.
21. Keep debugging bounded: every TTS investigation should either prove a working short sample quickly or be abandoned so the full delivery pipeline can continue.
22. Do not stop at intermediate artifacts; finish all listed outputs.



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



## Final Validation

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

