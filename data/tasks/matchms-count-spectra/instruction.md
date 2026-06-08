# Count Spectral Peaks Task

Given an MSP (mass spectrometry) file at `/root/input.msp`, count the number of spectra in it and find the spectrum with the most peaks. Then compute the total number of peaks across all spectra.

Write results to `/root/output.txt` with this exact format (each on its own line):
```
Total spectra: N
Spectrum with most peaks: NAME (K peaks)
Total peaks across all spectra: M
```

Use the `matchms` Python library to parse the MSP file. The MSP file contains multiple mass spectrometry records, each with a `name` field and `peaks` data.

If the file is empty or cannot be parsed, write:
```
Total spectra: 0
Spectrum with most peaks: N/A (0 peaks)
Total peaks across all spectra: 0
```