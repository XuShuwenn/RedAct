---
name: matchms
description: "Parse MSP (mass spectrometry) files and count spectral data: spectrum count, peak count per spectrum, and total peak count. Use when users ask about mass spectrometry data parsing, spectral counting, or MSP file analysis."
---

# Matchms: Mass Spectrometry Data Parsing

## Overview

Matchms is a Python library for mass spectrometry data processing. This skill focuses on loading MSP (NIST Mass Spectral Library) files and extracting spectral information.

## Loading MSP Files

```python
from matchms.importing import load_from_msp

# Load MSP file
spectra = list(load_from_msp("/root/input.msp"))
```

## Accessing Spectrum Data

Each spectrum has accessible properties. The MSP `Name:` field is stored in the `compound_name` metadata field:

```python
for spectrum in spectra:
    # IMPORTANT: Use 'compound_name' not 'name' for MSP 'Name:' field
    name = spectrum.get("compound_name", "Unknown")
    peaks_mz = spectrum.peaks.mz          # Array of m/z values
    peaks_intensities = spectrum.peaks.intensities  # Array of intensities
    num_peaks = len(spectrum.peaks.mz)    # Number of peaks
```

## Counting Spectra and Peaks

```python
# Total number of spectra
total_spectra = len(spectra)

# Find spectrum with most peaks
max_peaks = 0
spectrum_with_most = None
for spectrum in spectra:
    peak_count = len(spectrum.peaks.mz)
    if peak_count > max_peaks:
        max_peaks = peak_count
        # Use 'compound_name' for the MSP Name: field
        spectrum_with_most = spectrum.get("compound_name", "Unknown")

# Total peaks across all spectra
total_peaks = sum(len(spectrum.peaks.mz) for spectrum in spectra)
```

## Key Reference

- `load_from_msp(filename)` — Load MSP format files
- `spectrum.peaks.mz` — m/z values array
- `spectrum.peaks.intensities` — intensity values array
- `spectrum.get("compound_name")` — spectrum name from MSP `Name:` field
- `spectrum.get("name")` — may return None for MSP files, use `compound_name` instead
