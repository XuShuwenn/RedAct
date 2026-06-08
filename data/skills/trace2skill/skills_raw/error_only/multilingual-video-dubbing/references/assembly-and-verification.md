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

## Loudness normalization

Normalize, then measure integrated loudness separately. Do not treat a normalization command itself as proof.

Required evidence before claiming compliance:
- numeric integrated loudness value in LUFS
- sample rate = 48000 Hz
- channels = 1

If measurement output is blank, non-numeric, or crashes, the file is not yet verified.

## Final checks

Before reporting success, explicitly check:
- `abs(placed_start_sec - window_start_sec) <= 0.01` for each segment
- `drift_sec < 0.2`
- measured LUFS is numeric and at target or tolerance required by the task
- final muxed output uses the verified dubbed audio
