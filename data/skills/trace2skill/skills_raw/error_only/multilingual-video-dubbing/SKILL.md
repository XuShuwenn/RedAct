---
name: multilingual-video-dubbing
description: "Create multilingual video dubbing with TTS, audio normalization to ITU-R BS.1770-4, and synced video output."
---

# Multilingual Video Dubbing

## When to Use

- Dub video with translated speech

## Critical Requirement

- Generate new target-language speech audio for the dub; do not reuse or extract the original source speech as a fallback.
- Use `/root/reference_target_text.srt` and `/root/target_language.txt` in the actual TTS generation pipeline, not only in `report.json`.
- If you cannot produce target-language speech, stop and report the blocker rather than shipping source-audio output as a dubbed result.

- Normalize audio to ITU-R BS.1770-4 standard
- Sync audio with video within tight tolerances

## Input Files

- `/root/input.mp4`: Source video
- `/root/segments.srt`: Time windows for speech
- `/root/source_text.srt`: Original transcript
- `/root/target_language.txt`: Target language code
- `/root/reference_target_text.srt`: Reference translation

## Required Workflow

1. Choose a TTS path only after confirming it works with local assets already present.
2. Run a tiny smoke test first: synthesize one very short utterance and prove you can produce `/outputs/tts_segments/seg_0.wav` as 48000 Hz mono WAV.
3. Validate a minimal end-to-end path before scaling up: place the sample on the timeline, mux `/outputs/dubbed.mp4`, measure LUFS, and write `/outputs/report.json`.
4. As soon as one acceptable TTS path works, stop retrying alternative engines unless the result is unusable.
5. If a synthesis command times out twice, hangs, or cannot quickly list voices, load models, or produce a short sample, treat it as non-viable in the current environment and switch to a simpler proven local method.
6. Prefer direct available CLI or tool workflows for the first pass; add wrappers or broader automation only after the full pipeline is confirmed.
7. Fit each segment to its subtitle window using `rate_adjust`, `pad_silence`, or `trim`, then normalize and mux the final dubbed audio.
8. Do not stop at intermediate artifacts; finish all listed outputs.



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



## Execution Guardrails

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
- Do not claim LUFS compliance until you have a successful measurement result in tool output.
- If loudness analysis or parsing fails, treat loudness as unverified, fix the command, and rerun before writing `measured_lufs` to `/outputs/report.json`.
- Measure the finished output and bring integrated loudness to the intended target (typically about -23 LUFS); do not accept clearly off-target results without another correction pass.
- Re-measure after normalization or muxing as needed to confirm the final delivered artifact, not an intermediate file, is compliant.


- For FFmpeg `loudnorm`, use a real two-pass workflow: run pass 1, capture the reported JSON stats, then run pass 2 with those exact measured values. Do not invent or reuse `measured_*` parameters.


## Timing Constraints

- placed_start_sec matches window start within 10ms
- End drift (drift_sec) < 0.2 seconds
- Prefer content-preserving duration_control: "rate_adjust" or "pad_silence"
- Use "trim" only to remove leading/trailing silence, never to cut spoken content to fit a window


- Do not emit any other `duration_control` value in code or `report.json`; never use placeholders like `no_adjust`.
- Treat start alignment and end drift as separate checks: start placement must be within 0.01 s of the window start, while end drift must be < 0.2 s relative to the window end.
- Build the final dubbed track on an absolute timeline using each segment's window start time; do not assume segments are contiguous.
- Insert silence or mix each segment at its offset before muxing to video.
- If segment windows have gaps or start after 0, simple concat is incorrect.
- Derive each target window from `/root/segments.srt`; do not hardcode segment or video durations.
- Compute `placed_start_sec`, `placed_end_sec`, and `drift_sec` from the final adjusted audio actually muxed into the video, not from raw TTS output before trimming, padding, or rate adjustment.
- After any transform that can change duration or placement (normalization, resampling, encoding, padding or trimming, muxing), re-measure the final artifact and base report values on that measurement, not on intermediate files.
- Do not assume loudness normalization preserves exact duration; verify the final WAV duration after normalization before computing `placed_end_sec` or `drift_sec`.
- Preserve the full required delivery duration when muxing dubbed audio back into video; do not use options such as `-shortest` if they can truncate the output below the latest placed speech end or shorten the visual stream.
- If the source video is too short for the required placement window, extend or freeze-pad the video or otherwise lengthen the container, then remux and re-measure.
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

