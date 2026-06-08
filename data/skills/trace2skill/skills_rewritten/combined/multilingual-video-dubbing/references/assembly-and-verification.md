# Timeline Assembly and Verification

Use this when segment windows may be non-contiguous or when you need to prove timing and loudness compliance.

## Timeline assembly

Preferred pattern:
1. Generate each TTS segment as a mono 48 kHz WAV.
2. Measure its duration.
3. Place it on an absolute timeline at `window_start_sec` by either:
   - inserting leading silence, then mixing all segments together, or
   - using ffmpeg `adelay` per segment and `amix`.
4. After assembly, verify actual placement from the rendered timeline.

Do not build the final dub with plain sequential concat unless the task explicitly guarantees back-to-back windows from 0 with no gaps.
Sequential concat is only valid when windows are explicitly contiguous with no gaps and begin at 0; otherwise use offset placement.
When `/root/reference_target_text.srt` is supplied and usable, synthesize its target-language text directly instead of generating a new translation.
Do **not** set `placed_start_sec` equal to `window_start_sec` unless you actually placed the audio there in the rendered timeline and verified it from the assembled output.

If a segment must fit a subtitle window, a simple working pattern is:
- compute `target_window_duration = window_end_sec - window_start_sec`
- if the segment is short, keep `placed_start_sec = window_start_sec` and pad trailing silence to the target window duration
- if spoken content would overrun, compute `duration_ratio = current_duration / target_window_duration` and use that ratio for tempo retiming (`rate_adjust`)
- re-measure the adjusted segment and use the measured post-adjustment duration in placement checks, `placed_end_sec`, and `drift_sec`

Do not write timing fields from intended ratios alone; always use the final measured adjusted audio.

## Loudness normalization

Normalize, then measure integrated loudness separately. Do not treat a normalization command itself as proof.

Required evidence before claiming compliance:
- numeric integrated loudness value in LUFS
- sample rate = 48000 Hz
- channels = 1

If measurement output is blank, non-numeric, or crashes, the file is not yet verified.

Two-pass `ffmpeg loudnorm` rule:
1. Run pass 1 and capture the full stderr or JSON output.
2. Extract the reported measured fields from that successful pass.
3. Run pass 2 with those exact extracted values.
4. Measure the delivered final file again and record that numeric result.

Never supply second-pass measured values from memory, prior runs, or silent parsing failures.

Practical verification pattern:
- run the measurement so the complete final summary is captured, with stdout or stderr redirected if needed
- parse the captured final values only after confirming the command exited successfully
- if the summary is truncated or missing, treat loudness as unverified and rerun

## Final checks

Before reporting success, explicitly check:
- `abs(placed_start_sec - window_start_sec) <= 0.01` for each segment
- `drift_sec < 0.2`
- measured LUFS is numeric and at target or tolerance required by the task
- final muxed output uses the verified dubbed audio

- Confirm the final container duration reaches at least the latest required speech end; if muxing shortened the file, the timing check fails even if intermediate audio was correct.
- Avoid `-shortest` unless you have separately proven it cannot truncate required dubbed speech or video duration.
- Do not verify by reading back `report.json` alone; measure the actual rendered output timeline.
- After resampling, normalization, or muxing, re-probe durations and recompute placement values from the final artifacts.
- Base `placed_start_sec`, `placed_end_sec`, and `drift_sec` on the final rendered timeline or muxed output, not on pre-mux segment metadata.
- Keep at least millisecond precision during verification; do not round to 2 decimals before checking tolerances.
- If final probes disagree with previously computed metadata, fix the pipeline or rewrite the report from the measured outputs before reporting success.
