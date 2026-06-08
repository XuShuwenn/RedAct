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
from matchms.importing import load_msp_file

try:
    spectra = list(load_msp_file("/root/input.msp"))
except Exception:
    spectra = []
```

- Use `matchms` directly for MSP parsing; do not manually parse raw MSP text.
- Convert the parser output to a list before counting or iterating multiple times.
- Treat parser warnings as non-fatal if spectra are still returned.
- Use one script to parse, aggregate, and write `/root/output.txt`.

## Calculations

1. If parsing fails or no spectra are returned, write the documented zero-result output.
2. Otherwise, compute all summary statistics in one pass over the spectra.
3. Count peaks for each spectrum with `len(spectrum.peaks.mz)` when available; if peak data is missing or malformed for an individual record, treat that spectrum as having `0` peaks and continue.
4. For the spectrum label, use `compound_name` first and fall back to `name`, then `N/A`.
5. Track total spectra, total peaks, and the spectrum with the most peaks in that same loop.
6. Write `/root/output.txt` in the exact required three-line format.

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
- After writing `/root/output.txt`, read it back once to confirm the exact three-line format and values before finishing.
