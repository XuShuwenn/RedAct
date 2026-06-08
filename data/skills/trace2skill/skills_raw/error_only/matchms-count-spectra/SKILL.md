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

## Using matchms

```python
from matchms.importing import load_msp_file
spectra = load_msp_file("input.msp")
```

## Calculations

1. Count total spectra in file
2. For each spectrum, count peaks (len(spectrum.peaks))
3. Find spectrum with most peaks
4. Sum all peaks across all spectra

## Edge Cases

If file is empty/unparseable:
```
Total spectra: 0
Spectrum with most peaks: N/A (0 peaks)
Total peaks across all spectra: 0
```

## Tips

- matchms for MSP parsing
- Handle metadata.name field for spectrum names
- Check for peaks data structure
