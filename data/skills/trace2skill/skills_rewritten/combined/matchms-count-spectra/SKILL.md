---
name: matchms-count-spectra
description: "Parse MSP mass spectrometry files using matchms library to count spectra and find spectrum with most peaks."
---

# Mass Spectrometry Peak Counting

## When to Use

- Parse MSP (mass spectrometry) files
- Count spectral peaks
- Find spectrum with maximum peaks

## Input

- `/root/input.msp`: MSP mass spectrometry file

- Start by confirming the expected files/paths in `/root` so you do not make incorrect path assumptions before parsing.

## Output

To `/root/output.txt`:
```
Total spectra: N
Spectrum with most peaks: NAME (K peaks)
Total peaks across all spectra: M
```

Write `/root/output.txt` in the exact three-line format shown above. Preserve labels, punctuation, spacing, and line order exactly. Do not add extra commentary, warnings, or debug output. If the selected spectrum has no usable name, write `N/A` as the spectrum name.

## Using matchms

```python
try:
    from matchms.importing import load_msp_file as _load_msp
except ImportError:
    from matchms.importing import load_from_msp as _load_msp

try:
    spectra = list(_load_msp("/root/input.msp"))
except Exception:
    spectra = []
```

- Use `matchms` directly for MSP parsing; do not manually parse raw MSP text.
- Convert the parser output to a list before counting or iterating multiple times.
- Treat parser warnings as non-fatal if spectra are still returned.
- Use one script to parse, aggregate, and write `/root/output.txt`.

- Accept either `matchms.importing.load_msp_file` or `matchms.importing.load_from_msp`, depending on the installed version.
- If `matchms` cannot be imported at all, treat parsing as failed and write the documented zero-result output.
- Warnings about missing optional metadata (for example `precursor_mz`) are non-fatal when spectra are still returned; continue processing, do not switch to manual parsing, and only use the zero-result fallback when loading raises an exception or yields zero spectra.
- Prefer a short standalone Python script for this task: parse once, compute the requested aggregates from the parsed spectrum objects, and write `/root/output.txt` directly from those computed values.
- Do not require unrelated metadata such as `precursor_mz` for this task, and do not let warning or diagnostic text end up in the output file.

## Calculations

1. If parsing fails or no spectra are returned, write the documented zero-result output.
2. Otherwise, compute all summary statistics in one pass over the spectra.
3. Count peaks for each spectrum with `len(spectrum.peaks.mz)` when available; if peak data is missing or malformed for an individual record, treat that spectrum as having `0` peaks and continue.
4. For the spectrum label, use `compound_name` first and fall back to `name`, then `N/A`.
   - If the chosen label is unexpectedly missing, inspect a parsed spectrum's metadata keys before assuming the file lacks names; `matchms` may normalize the source field name.
   - Validate the selected winning spectrum's label separately from the numeric counts before writing the final output.
5. Track total spectra, total peaks, and the spectrum with the most peaks in that same loop.
6. Write `/root/output.txt` in the exact required three-line format.

0. Check whether `/root/input.msp` exists before parsing; if it is missing, write the documented zero-result output immediately.
7. Keep the aggregation compact: for each parsed spectrum, increment the spectrum count, derive that spectrum's peak count once, add it to the running total, and update the current maximum only when the new peak count is strictly larger.
8. Initialize the current maximum as `N/A` with `0` peaks so the first spectrum with the highest peak count remains the winner if later spectra tie it.
9. Read metadata defensively, e.g. via `spectrum.get("compound_name")` / `spectrum.get("name")` or equivalent normalized access, and normalize the chosen label to a usable string; if the selected value is missing, empty, malformed, or not string-like, write `N/A`.
10. For the zero-result fallback, still write the exact three-line output file instead of exiting early without creating `/root/output.txt`.

## Edge Cases

If file is empty/unparseable:
```
Total spectra: 0
Spectrum with most peaks: N/A (0 peaks)
Total peaks across all spectra: 0
```
Use the same fallback output for parsing exceptions, missing files, and successfully parsed files with zero spectra. If `matchms` emits warnings but still returns spectra, continue and compute the requested metrics. Only use the zero-valued fallback output when the file is unreadable, parsing raises an exception, or no spectra are parsed.

## Tips

- Use `matchms` for MSP parsing with the task's absolute paths: `/root/input.msp` and `/root/output.txt`.
- Prefer a single-loop aggregation pattern: update total spectra, total peaks, and the current maximum together while iterating.
- Prefer normalized metadata keys: `compound_name` first, then `name`, then `N/A`.
- Prefer `len(spectrum.peaks.mz)` over `len(spectrum.peaks)` or metadata-derived peak counts.
- Guard optional fields so one irregular spectrum does not abort the whole summary.
- After writing `/root/output.txt`, read it back once and confirm it exists, has exactly three non-empty lines, matches the required labels/order/punctuation/spacing, contains no warnings or extra text, and that the reported maximum-peak spectrum and totals match the computed aggregates before finishing.

- Keep the workflow minimal: use a short standalone Python script, reuse already-computed summary values from the same parsed result set when writing `/root/output.txt`, and avoid re-parsing, recomputing, or extra post-processing that could change spacing, labels, or line order.
- If a spectrum name seems absent, check a parsed spectrum's metadata dictionary to confirm which normalized key `matchms` produced before changing label-selection logic.
- Create helper scripts only in confirmed writable locations such as `/root`, and keep all task files on the required absolute paths.
