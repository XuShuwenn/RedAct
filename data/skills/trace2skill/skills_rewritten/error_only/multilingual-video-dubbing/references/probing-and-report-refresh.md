# Probing and Report Refresh

Use this when inline Python is failing repeatedly or when outputs were regenerated and all metadata must be refreshed.

## Prefer simple probes over multi-line inline Python

If you only need one numeric field, prefer a direct probe command:

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 /outputs/dubbed.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels -of default=nw=1 /outputs/dubbed.mp4
python -m json.tool /outputs/report.json >/dev/null
```

If an inline Python snippet fails twice with the same syntax or indentation issue:
1. stop retrying the same shape of snippet
2. switch to one-liners or saved scripts under `/outputs`
3. verify the produced file immediately

Safer saved-script pattern:

```bash
cat >/outputs/refresh_report.py <<'PY'
# minimal script only; keep it short and single-purpose
PY
python3 /outputs/refresh_report.py
```

## Full refresh rule after regeneration

Any time you replace `/outputs/tts_segments/seg_0.wav`, `/outputs/dubbed.mp4`, or the final normalized audio used for muxing, treat earlier metadata as stale.

Refresh in this order:
1. probe the current final segment/audio durations
2. probe `/root/input.mp4` and the current `/outputs/dubbed.mp4` duration
3. re-measure final loudness
4. rebuild all of `/outputs/report.json`
5. parse `/outputs/report.json` successfully and cross-check values against the probes

Do not update only `placed_end_sec` or only `measured_lufs` after regeneration. Recompute the entire report from one consistent artifact set.

## Final consistency checklist

Before completion, verify all are true:
- required final paths exist
- final response matches any exact completion token required by the runtime
- `new_duration_sec` matches the current `/outputs/dubbed.mp4`
- segment timing fields match the current delivered segment/timeline measurements
- `measured_lufs` comes from the latest successful measurement, not an earlier run
- `report.json` parses fully and uses the required schema
