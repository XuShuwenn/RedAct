---
name: seismic-phase-picking
description: "Pick P and S wave arrival times from seismic waveform data using deep learning or signal processing methods."
---

# Seismic Phase Picking

## When to Use

- Pick P and S wave arrivals from seismic traces
- Process waveform data for phase identification
- Achieve F1 >= 0.7 for P, >= 0.6 for S

## Input Data

- `/root/data/*.npz`: 100 earthquake trace files
- Each contains:
  - data: 12000 samples × 3 channels
  - dt: sampling interval (seconds)
  - channels: comma-separated names (e.g., DPE,DPN,DPZ)

- Use the provided absolute paths exactly (`/root/data/*.npz`, `/root/results.csv`); do not switch to relative paths during inspection or output.
- First inspect one or two `.npz` files for extra keys beyond `data`, `dt`, and `channels`.
- If files include phase-related metadata (for example `p_*`, `s_*`, remarks, weights, labels, or annotation-like fields), use it to calibrate thresholds or sanity-check picks before building a waveform-only solution.
- Verify actual array shapes before changing channel-handling logic; treat the `data` array as authoritative if metadata conflicts.

## Output Format

CSV at `/root/results.csv`:
```
file_name,phase,pick_idx
```

- phase: "P" or "S"
- pick_idx: sample index of arrival

## Performance Requirements

- P wave F1 >= 0.7
- S wave F1 >= 0.6
- Tolerance: 0.1s (convert to index tolerance)

- Convert every time-based rule to samples using each file's `dt` (for example `tol_idx = round(0.1 / dt)`); do not assume a fixed sampling interval.

## Approaches

1. Use SeisBench deep learning models (PhaseNet, EQTransformer)
2. STA/LTA (short-term average / long-term average)
3. Energy-based detection


4. Recommended order under uncertainty: inspect sample files and metadata first, build a lightweight STA/LTA or energy-based baseline that can write the required CSV, then try SeisBench/ObsPy only if dependencies are already available or quick to verify.
5. Pure NumPy/SciPy fallback: use vertical-dominant onset evidence for P and horizontal-energy or envelope increase after P for S.
6. Prefer component-aware picking over a single collapsed trace: when channel orientation is available, use `Z`-like vertical channels for **P** candidates and `N`/`E`-like horizontal channels for **S** candidates.
7. If using heuristics, score candidate onsets separately for P and S rather than detecting both phases from one fully collapsed RMS/mean signal.


## Execution Workflow

## Execution Workflow

1. Inspect 1-5 `.npz` files first and confirm actual keys, shapes, `dt`, how `channels` is encoded, and channel ordering.
2. Check which Python packages are already available before depending on heavy libraries; treat SeisBench and ObsPy as optional accelerators, not mandatory dependencies.
3. Start with the lightest workable end-to-end method on one file, validate that it produces plausible `pick_idx` values, then scale to all files.
4. Handle `channels` defensively: it may be a comma-separated string or another array/object form; normalize it once and reuse that logic.
5. Do not assume fixed arrival windows such as "P in first half" or "S in second half" unless inspection or metadata supports them.
6. If a method returns many candidate peaks, debug the final selection rule before changing sensitivity; do not blindly take the first detected peak or judge revisions only by total pick counts.
7. If optional-package setup is slow, failing, or unverified after a concrete check, pivot immediately to the fallback method instead of spending the run on installs.
8. Time-box single-file debugging: validate on a few files, then implement batch processing across all `/root/data/*.npz` files and write `/root/results.csv` in the required schema.

## Tips

- Use ObsPy for waveform handling
- SeisBench for ML-based picking
- Multiple picks per file allowed
- scipy for signal processing


- Prioritize making picks and writing `/root/results.csv` over package-management loops.
- Prefer `numpy`-only or `numpy`+`scipy` baselines when the environment is limited; a complete heuristic baseline is better than an unfinished ML setup.
- Validate imports before choosing SeisBench or ObsPy-heavy workflows, and use `numpy.load` directly for `.npz` inspection when needed.
- Implement batch processing early: test on a small sample first, print candidate peaks and chosen `pick_idx` values for several traces, then run all files.
- Do not force exactly one P and one S pick per file; zero picks for a phase is allowed when evidence is weak.
- Avoid fallback logic that manufactures picks from maxima or fixed default windows when thresholds fail.
- If heuristic outputs are unstable (for example many picks at index 0, S before P, or unchanged chosen indices despite code changes), recalibrate from observed data or metadata instead of guessing new thresholds.
- Before finishing, sanity-check that `/root/results.csv` exists, is non-empty, has header `file_name,phase,pick_idx`, and stores integer sample indices rather than seconds.


## Tips

## Validation and Finalization

- Before finalizing, inspect picks across a sample of files; treat these patterns as failure signals:
  - many P picks at or near the first few samples
  - nearly identical P/S offsets across many different files
  - widespread S picks with weak or no visible energy change after the P pick
- If those artifacts appear, adjust the method or thresholds before scaling or finalizing.
- Do minimal final checks: `/root/results.csv` exists, header is exactly `file_name,phase,pick_idx`, phases are only `P`/`S`, and `pick_idx` values are plausible sample indices.
- Once the CSV is produced and these checks pass, stop iterating unless a blocking quality issue remains.
