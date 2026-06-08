---
name: matchms-msp-summary
description: "Use matchms to parse MSP files, count spectra, find the spectrum with the most peaks, and sum all peaks with robust fallbacks and exact formatting."
---

# Matchms MSP Summary

Summarize an MSP (mass spectrometry) file using the matchms library: count the number of spectra, identify the spectrum with the highest peak count, and compute the total number of peaks across all spectra. Includes robust handling for empty files and parse failures, and guidance for producing exact, line-based output.

## When to Use

Activate this skill when you need to:
- Parse an MSP file and summarize its contents using matchms
- Count spectra and peaks in each spectrum
- Identify the spectrum with the maximum number of peaks
- Output the results in an exact three-line format, with a defined fallback for empty/unparsable files

## Core Workflow

1. Load the MSP file with matchms.
   - Use `matchms.importing.load_from_msp(path)` to stream spectra.
   - Prefer streaming iteration to avoid loading very large files into memory.

2. Iterate once to compute aggregates and track the max.
   - Maintain:
     - `total_spectra` (count of spectra)
     - `total_peaks` (sum of peak counts across spectra)
     - `max_peaks` (largest peak count seen)
     - `top_name` (metadata name of the spectrum with `max_peaks`)

3. Count peaks safely per spectrum.
   - Use `len(spectrum.peaks.mz)` if available; if `peaks` or `mz` is missing, treat as 0.

4. Resolve spectrum name robustly.
   - MSP "Name" is commonly mapped to `compound_name` in matchms.
   - Try keys in order: preferred key (usually `compound_name`), then `name`, then fallback to `Unknown` if missing or empty.

5. Handle empty or unparsable inputs.
   - If parsing raises an exception, or if zero spectra are yielded, produce the fallback (all zeros and `N/A` for name).

6. Write results in the exact format required by the task.
   - Ensure three lines, with integers for counts, exact punctuation/spaces, and a trailing newline. Adapt the literal text to the task’s specification.

Example aggregation logic (pseudocode):
- Try to iterate `load_from_msp(path)`.
- For each spectrum:
  - `peaks = safe_len(s.peaks.mz)`
  - `total_spectra += 1; total_peaks += peaks`
  - If `peaks > max_peaks`: update `max_peaks` and `top_name`
- If `total_spectra == 0`: set fallback values
- Format and write the three lines exactly as requested

## Verification

- After writing the output file:
  - Re-open and read the file to confirm:
    - Exactly three lines are present
    - Line 1 starts with `Total spectra:` and contains a non-negative integer
    - Line 2 follows `Spectrum with most peaks: NAME (K peaks)` with K as a non-negative integer
    - Line 3 follows `Total peaks across all spectra: M` with M as a non-negative integer
  - Sanity checks:
    - `top_peaks <= total_peaks`
    - If `total_spectra == 0`, then `top_name == N/A`, `top_peaks == 0`, and `total_peaks == 0`
  - Confirm there are no extra spaces or missing parentheses compared to the required format

## Common Pitfalls

- Name key mismatch:
  - MSP `Name` is often normalized to `compound_name` in matchms. Do not rely only on `name`; try both (`compound_name` then `name`). Fallback to `Unknown` if missing.

- Counting peaks incorrectly:
  - Use `len(spectrum.peaks.mz)`. Do not count lines or assume intensities; `mz` and `intensities` arrays are paired and should have equal length.
  - Guard against missing `peaks` or `mz` attributes; treat as zero rather than crashing.

- Ignoring parse failures:
  - Wrap `load_from_msp` iteration in a try/except. On exception, emit the fallback output.

- Loading all spectra unnecessarily:
  - `list(load_from_msp(...))` works but may be memory-heavy. Prefer streaming iteration; it also simplifies empty-file handling (use `total_spectra` as the emptiness indicator).

- Output format drift:
  - Extra spaces, different capitalization, or missing parentheses will fail exact-match checks. Follow the exact strings required by the task prompt.

## Success Criteria

- Produces the three-line summary exactly as specified by the prompt
- Correctly handles empty/unparsable files by outputting the fallback lines
- Peak counts and totals are consistent and derived from the parsed data

## Optional Script Usage

A helper script is provided to perform the summary with robust defaults.

Example usage:
- Print summary to stdout:
  - `python scripts/msp_summary.py /path/to/input.msp`
- Write summary to a file:
  - `python scripts/msp_summary.py /path/to/input.msp --output /path/to/output.txt`
- Use a different name key (if metadata differs):
  - `python scripts/msp_summary.py /path/to/input.msp --name-key name`
