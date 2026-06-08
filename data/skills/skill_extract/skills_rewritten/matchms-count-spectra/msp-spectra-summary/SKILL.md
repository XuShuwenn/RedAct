---
name: msp-spectra-summary
description: "Summarize MSP mass spectrometry files with matchms: count spectra, find the spectrum with most peaks, and compute total peaks with robust fallbacks and exact output formatting."
---

# MSP Spectra Summary with matchms

Use this skill to parse an MSP file of mass spectra using the matchms library, count the total number of spectra, identify the spectrum with the most peaks, compute the total number of peaks across all spectra, and write the results in an exact, line-based format. Includes robust handling for empty or unparsable files.

## When to Use

Activate this skill when tasks require:
- Parsing an MSP file and counting how many spectra it contains
- Finding the spectrum with the most peaks (with clear tie handling)
- Computing the total number of peaks across all spectra
- Writing a strict, line-based summary output
- Providing a defined fallback when the input is empty or cannot be parsed

## Core Workflow

1. Prepare the environment
   - Ensure Python is available and the matchms library can be imported.
   - If matchms cannot be imported or the file cannot be parsed, follow the fallback output rule.

2. Load spectra from MSP
   - Use matchms.importing.load_from_msp(input_path) to obtain spectra as an iterable.
   - Iterate once over the spectra; do not rely on reusing the generator without reloading.

3. For each spectrum, compute peak counts and track the max
   - Extract the spectrum name from metadata. Try keys in order: name, compound_name, spectrum_id. If none are present, use "N/A".
   - Count the number of peaks robustly:
     - Prefer len(spectrum.peaks.mz) if available.
     - If peaks is a list-like object, fall back to len(spectrum.peaks).
     - If neither is available or an error occurs, count as 0.
   - Maintain running totals:
     - spectra_count: increment for each spectrum.
     - total_peaks: add each spectrum's peak count.
     - most_peaks and most_peaks_name: update only when a strictly larger peak count is found (ties keep the first encountered spectrum deterministically).

4. Fallback behavior
   - If the file is empty, does not exist, matchms cannot be imported, or parsing raises an exception, produce the fallback output with zeros and "N/A".

5. Write exact output
   - Write three lines, each on its own line, exactly in this form:
     - Total spectra: N
     - Spectrum with most peaks: NAME (K peaks)
     - Total peaks across all spectra: M
   - For the zero/fallback case, use NAME = "N/A" and K = 0.

## Verification

Perform these checks before finalizing:
- Sanity checks:
  - N >= 0, K >= 0, M >= 0.
  - M >= K (the total across all spectra should be at least the maximum of any single spectrum).
  - If N == 0 then K == 0 and NAME == "N/A".
- Consistency checks:
  - Sum of per-spectrum peak counts equals M.
  - The spectrum identified as NAME indeed has K peaks.
- Output format checks:
  - Exactly three lines with the specified labels and punctuation.
  - No extra prefix/suffix text, no additional whitespace, and includes newline terminations.

## Common Pitfalls

- Skipping exception handling on parse errors:
  - Always catch import or parsing exceptions and emit the fallback output.
- Miscounting peaks due to API assumptions:
  - Some matchms versions expose peaks via spectrum.peaks.mz/intensities; others may provide list-like peaks. Always check both and handle None safely.
- Missing names in metadata:
  - Do not assume "name" exists. Check alternative keys and default to "N/A".
- Tie handling for most peaks:
  - Use strictly greater (>) to update the max so the first max stays selected deterministically.
- Consuming the generator multiple times:
  - load_from_msp returns an iterable/generator. Convert to a list or compute in a single pass to avoid losing data on a second iteration.
- Output format drift:
  - Do not add extra lines or formatting (e.g., JSON, bullet points). Match the exact three lines.

## Success Criteria

- Output contains exactly three lines with the required labels and values.
- Counts are internally consistent (sanity and consistency checks pass).
- Fallback output is used when the file is empty or cannot be parsed.

## Optional Script Usage

A reusable CLI script is provided to load an MSP file, compute the summary, and write the exact output format.

Examples:
- Write summary to a file:
  - python scripts/msp_summary.py --input path/to/input.msp --output path/to/output.txt
- Print to stdout without writing a file:
  - python scripts/msp_summary.py --input path/to/input.msp --stdout
- Validate an existing output file's format:
  - python scripts/msp_summary.py --validate-output path/to/output.txt
