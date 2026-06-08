---
name: timed-tts-dubbing
description: "Generate and align TTS audio to subtitle windows, loudness-normalize to ITU-R BS.1770-4 (-23 LUFS), and mux into a video with tight timing tolerances."
---

# Precise Timed TTS Dubbing

A reusable workflow for multilingual dubbing where synthesized speech must align to subtitle windows, meet broadcast loudness (-23 LUFS, ITU-R BS.1770-4), and be muxed into a video with strict start and end drift limits.

## When to Use

Use this skill when you must:
- generate TTS in a target language from reference text
- place audio within given time windows from subtitles (e.g., SRT)
- normalize loudness to ITU-R BS.1770-4 (-23 LUFS)
- deliver a video with the new audio at 48 kHz, mono, and tight timing constraints between placed audio and window timings

## Core Workflow

1. Inputs and Targets
   - Inputs: video file, segment windows (e.g., segments.srt), source/target text SRTs, target language code.
   - Targets: 48 kHz, mono audio; -23 LUFS (BS.1770-4); precise window placement.

2. Parse SRT windows and texts
   - Extract start_sec, end_sec, duration, and text for each segment.
   - Validate segments are sorted by start time and non-overlapping (or handle overlaps with mixing).

3. Synthesize TTS per segment
   - Preferred: high-quality TTS (neural) when available.
   - Fallback chain idea: neural TTS → simpler online TTS → offline TTS (e.g., espeak-ng).
   - Always convert output to WAV 48 kHz, mono early in the pipeline.

4. Match segment duration
   - Compute current_duration (measured) and target_duration (window_end - window_start).
   - Decide duration control:
     - rate_adjust: change tempo when the speed ratio is reasonable.
       - Formula: ratio = current_duration / target_duration.
         - ratio < 1.0 → slow down (lengthen)
         - ratio > 1.0 → speed up (shorten)
       - Use FFmpeg atempo filter. atempo accepts ~0.5–2.0 per filter; chain when outside this range.
     - pad_silence: if current < target and required ratio < 0.5, append silence to reach target.
     - trim: if current > target and required ratio > 2.0, trim to target.
   - After adjustment, remeasure duration.

5. Loudness normalization to -23 LUFS
   - Use two-pass FFmpeg loudnorm for precision:
     - Pass 1 (measure): loudnorm with print_format=json; parse JSON from stderr for input_i, input_lra, input_tp, input_thresh, target_offset.
     - Pass 2 (apply): feed measured values back into loudnorm with linear=true. Resample and force mono: -ar 48000 -ac 1.
   - Verify with a measurement pass and ensure result is close to -23 LUFS (minor deviations can occur).

6. Placement and mixing
   - Single segment starting at 0: direct mux (place start at 0). If start > 0, delay the segment with adelay before mux or overlay on a silence bed.
   - Multiple segments or non-zero starts:
     - Create a silence bed of the original video duration: anullsrc=r=48000:cl=mono:d={video_duration}.
     - For each segment: delay by placed_start_ms using adelay and mix all with amix. Keep mono and 48 kHz.
   - Start drift check: |placed_start_sec - window_start_sec| ≤ tolerance (e.g., ≤ 0.010 s).
   - End drift check: |placed_end_sec - window_end_sec| ≤ tolerance (e.g., ≤ 0.2 s). Adjust if needed.

7. Mux new audio into the video
   - -map 0:v -map 1:a, -c:v copy, -c:a aac (or pcm_s16le), -ar 48000, -ac 1, -shortest.

8. Reporting and validation
   - Include in a JSON report: source/target language codes, sample rate, channels, original/new durations, measured LUFS.
   - For each segment: window times, placed times, window and final TTS durations, computed drift, and chosen duration_control (rate_adjust, pad_silence, or trim).

## Verification

- Audio format checks (ffprobe): sample_rate=48000, channels=1.
- Loudness measurement: use loudnorm with print_format=json and read input_i from stderr; expect ≈ -23.0 LUFS.
- Timing checks:
  - Start drift = |placed_start_sec - window_start_sec|; ensure ≤ target threshold (e.g., 10 ms).
  - End drift = |(placed_start_sec + tts_duration_sec) - window_end_sec|; ensure ≤ target threshold (e.g., 0.2 s).
- Visual integrity: -c:v copy and -shortest to prevent extending video beyond visuals.

## Common Pitfalls and How to Avoid Them

- Wrong tempo ratio: atempo expects a speed factor; use ratio = current_duration / target_duration.
  - Example: current=10s, target=12s → ratio=0.8333 (slower).
- atempo range violation: atempo accepts ~0.5–2.0 per filter. Chain filters or switch to pad/trim as needed.
- Incorrect placement method: concatenating segments ignores absolute window times. Use an anullsrc bed with adelay per segment and amix.
- Not forcing 48 kHz mono: always set -ar 48000 -ac 1 after filtering/normalization.
- Using ebur128 for final spec compliance: prefer loudnorm two-pass and verify via its measurement JSON from stderr.
- Parsing loudnorm JSON from stdout: FFmpeg writes loudnorm JSON to stderr; parse stderr.
- Relying on a single online TTS: implement fallback to alternative or offline TTS.

## Optional Script Usage

This skill includes a helper script with reusable utilities.

Examples:

- Plan duration control and build atempo chain
  - python scripts/av_dubbing_tools.py plan-duration --current 10.272 --target 12.116

- Normalize to -23 LUFS (two-pass)
  - python scripts/av_dubbing_tools.py loudnorm-two-pass input.wav output.wav --target-lufs -23

- Measure LUFS
  - python scripts/av_dubbing_tools.py measure-lufs output.wav

- Mix delayed segments on a silence bed
  - Prepare a JSON file segments.json like:
    {
      "base_duration_sec": 12.05,
      "segments": [
        {"path": "seg_0.wav", "start_sec": 0.0},
        {"path": "seg_1.wav", "start_sec": 3.5}
      ]
    }
  - python scripts/av_dubbing_tools.py mix-segments segments.json mixed.wav

Success criteria:
- Audio: 48 kHz, mono; LUFS ≈ -23.
- Start alignment within the prescribed tolerance (e.g., ≤10 ms) and end drift within tolerance (e.g., ≤0.2 s).
- Output video: original visuals preserved, dubbed audio muxed correctly.
