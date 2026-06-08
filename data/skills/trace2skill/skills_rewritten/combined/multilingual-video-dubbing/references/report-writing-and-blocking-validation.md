# Report Writing and Blocking Validation

Use this when generating `/outputs/report.json` or when any verification step has failed.

## Write the report as real JSON

Required rule: the file content itself must be valid JSON.

Do:
1. Collect final measured values from the delivered artifacts.
2. Build one in-memory object using the required schema.
3. Serialize it with a JSON writer.
4. Parse the written file back successfully.

Do not:
- write placeholder text
- write a prose description of the schema
- assume a successful file write means the JSON is valid

Minimal safe pattern:

```python
import json

report = {
    "source_language": source_language,
    "target_language": target_language,
    "audio_sample_rate_hz": 48000,
    "audio_channels": 1,
    "original_duration_sec": original_duration_sec,
    "new_duration_sec": new_duration_sec,
    "measured_lufs": measured_lufs,
    "speech_segments": speech_segments,
}

with open('/outputs/report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

with open('/outputs/report.json', 'r', encoding='utf-8') as f:
    json.load(f)
```

## Blocking validation rule

If any verification step fails, the task is not complete.

Examples of blocker signals:
- JSON decode error
- zero-byte output
- unreadable media file
- missing numeric loudness result
- failed `ffprobe` or parse step
- truncated or incomplete output where the needed value is absent

Required response:
1. Repair or regenerate the artifact.
2. Rerun the verification command on the final saved path.
3. Only then use that result in `report.json` or completion claims.

- If the loudness command prints only a label such as `Integrated loudness:` with no numeric result, that is a failed verification, not a near-success. Re-run with captured complete output or another measurement path; do not report BS.1770 compliance or a LUFS number until you have the numeric result.
- If the file content is placeholder-like, prose-only, or merely a schema description instead of populated JSON, the report is invalid even if the path exists. Rebuild it from measured values, then parse it successfully before completion.

## Evidence standard

Only claim success from positive evidence:
- JSON: successful parse
- loudness: actual numeric LUFS result
- media properties: parseable `ffprobe` or equivalent output
- timing: measured values from final artifacts

Do not infer success from partial banners, command launch messages, or earlier failed runs.
