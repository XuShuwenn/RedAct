---
name: tts-dub-align
description: "Create target-language TTS, align it to subtitle windows, normalize to broadcast loudness, mux into the original video, and produce a verification report."
---

# TTS Dubbing: Timing Alignment and Loudness Compliance

This skill provides a reusable workflow to synthesize target-language speech, fit it to specified time windows from subtitles, normalize to broadcast loudness (ITU-R BS.1770 loudness via loudnorm/ebur128), mux with the original video, and verify timing and format constraints.

Use it for tasks requiring:
- replacing or overlaying source audio with TTS in another language
- precise segment alignment to subtitle/timecode windows
- ITU-R BS.1770 loudness compliance (e.g., target −23 LUFS)
- output audio at 48000 Hz, mono
- generating a JSON report with language codes, timing, loudness, and duration-control method

## When to Use
- You have a video and subtitles (e.g., SRT) describing speech windows.
- You must produce a dubbed audio segment and a muxed video with the new audio.
- You need broadcast-style loudness normalization and strict timing tolerance.

## Core Workflow

1) Ingest and Inspect Inputs
- Read subtitle segments (e.g., SRT) that define window_start_sec and window_end_sec.
- Read the source transcript and the target language text for synthesis.
- Probe the input video with media tools (e.g., ffprobe) to obtain duration and stream properties.

2) Generate Target-Language Speech (TTS)
- Use a high-quality TTS engine available in the environment.
- Prefer neural/offline options when connectivity is an issue; implement fallback to an alternative engine if the first choice fails.
- Export initial raw audio (WAV or lossless) for further processing.

3) Decide Duration Control Strategy
Given:
- window_duration = window_end_sec − window_start_sec
- tts_raw_duration = measured duration of the raw TTS
Choose one of:
- rate_adjust: if raw TTS duration differs materially from the window (typical case). Compute tempo_ratio = tts_raw_duration / window_duration and time-stretch to fit the window.
- pad_silence: if tts_raw_duration ≤ window_duration and the shortfall is small (e.g., ≤ 0.2 s). Add trailing silence to reach exact window length.
- trim: if tts_raw_duration just exceeds the window slightly (e.g., ≤ 0.2 s). Trim the end to the exact window length.

Notes:
- Adjust thresholds to meet required drift tolerances. Re-measure after processing.
- If tempo_ratio is outside the single-pass atempo range [0.5, 2.0], chain multiple atempo filters whose product equals the desired ratio.

4) Process Audio to Exact Specs
- Filter order matters. A robust recipe:
  - Apply timing transformation (rate_adjust/pad/trim) to hit the exact window duration.
  - Resample and set channels on the final export step (48 kHz, mono).
- Ensure the processed segment duration equals the window_duration within tight tolerance.

5) Loudness Normalization (Standards-Based)
- Use a two-pass loudness normalization (ffmpeg loudnorm) targeting broadcast values (e.g., I = −23 LUFS, TP = −2 dB, LRA = 11).
- Measure first pass to obtain measured_I/TP/LRA/threshold/offset.
- Apply second pass with those measured parameters for accurate normalization.
- Re-measure final LUFS and store it for the report.

6) Mux Audio with Video
- Align the segment to the exact window start using a precise offset (e.g., itsoffset or adelay). Convert seconds to milliseconds and ensure placement within 10 ms tolerance.
- Map video from the source without re-encoding when possible; write a new audio track at 48 kHz mono.
- Verify the muxed output audio properties (sample rate, channels) and durations.

7) Verification and Report
- Verify:
  - Audio: 48000 Hz, mono; measured LUFS near the target; file integrity.
  - Timing: placed_start_sec within 0.01 s (10 ms) of window start; drift_sec = |placed_end_sec − window_end_sec| ≤ 0.2 s.
  - Video: original visuals preserved; audio stream present and correct.
- Produce a JSON report including:
  - source_language (code), target_language (code)
  - audio_sample_rate_hz, audio_channels
  - original_duration_sec, new_duration_sec (from probes)
  - measured_lufs (integrated LUFS)
  - speech_segments[] entries with window times, placed times, source/target text, computed durations, drift_sec, and duration_control (rate_adjust/pad_silence/trim)

## Verification Checklist
- Inputs parsed (subtitles, language codes) without errors.
- TTS generated successfully (fallback used if needed), and its raw duration measured.
- Duration-control strategy chosen with documented rationale.
- Final segment duration exactly equals window duration (pad/trim) or after time-stretch.
- Final audio exported as 48 kHz mono WAV.
- Loudness normalized using a two-pass method; measured final LUFS recorded.
- Muxed video created with new audio; verify placed start within 10 ms and end drift ≤ 0.2 s.
- Report JSON contains language codes (e.g., en, ja) rather than language names.

## Common Pitfalls and How to Avoid Them
- Skipping measurement after processing: Always re-measure duration and loudness after time-stretch/pad/trim.
- Misordered filter chain: Do timing adjustments first, then finalize sample rate/channels; trim last to exact duration.
- atempo out-of-range: Chain factors within [0.5, 2.0] to achieve large ratios.
- Endless padding: If using apad, always follow with atrim to enforce exact duration.
- Wrong placement offset: Convert window_start_sec to milliseconds and apply precise offset; verify placed_start_sec within 10 ms.
- Incorrect audio format: Explicitly set -ar 48000 -ac 1 on the final export/mux; verify with ffprobe.
- Not using language codes: Normalize to ISO codes (e.g., en, ja) in the report.
- Over-trimming or under-padding: Keep drift ≤ 0.2 s; choose rate_adjust when differences are larger than your pad/trim threshold.

## Optional Script Usage
A helper script is provided to align and normalize a single segment. It:
- measures raw TTS duration
- selects duration control (auto) or uses a specified strategy
- applies timing adjustment and exports 48 kHz mono WAV
- performs two-pass loudness normalization to a target LUFS
- outputs a sidecar JSON with measured metadata for report assembly

Example:
- Align and normalize a segment to a window [start, end]:
  scripts/align_and_normalize.py \
    --in raw_tts.wav \
    --out seg_0.wav \
    --window-start 0.00 \
    --window-end 2.10 \
    --target-lufs -23.0

Then mux into the video at the precise offset (example command):
- ffmpeg -y -i input.mp4 -itsoffset 0.00 -i seg_0.wav -map 0:v:0 -map 1:a:0 -c:v copy -ar 48000 -ac 1 -shortest dubbed.mp4

After muxing, probe durations and loudness, compute placed_start_sec/placed_end_sec, and write the report JSON.
