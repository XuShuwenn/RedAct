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

- Use the provided absolute paths exactly (`/root/data/*.npz`, `/root/results.csv`) in every command and code path; do not switch to relative paths during inspection, batch processing, or output writing.
- First inspect one or two `.npz` files for extra keys beyond `data`, `dt`, and `channels`.
- If files include phase-related metadata (for example `p_*`, `s_*`, remarks, weights, labels, or annotation-like fields), use it to calibrate thresholds or sanity-check picks before building a waveform-only solution.
- Do not spend time searching outside the provided `.npz` files for separate ground-truth or label files; use only the supplied waveform files and any metadata already inside them.
- When such metadata is present, quickly summarize realistic P/S index ranges or quality subsets from a few files before choosing search windows or thresholds.
- Read a few actual phase/timing metadata values immediately and decide whether they can directly inform picking, candidate windows, confidence filtering, or validation; if metadata already provides usable phase indices or near-direct labels, prefer a simple extraction/validation pipeline over installing external picking libraries.
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
4a. Treat package installation as a last resort: if imports are missing and a NumPy/SciPy heuristic can be implemented, prefer the heuristic and keep moving toward the required CSV.
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
- A partial but working NumPy/SciPy heuristic picker that writes the required CSV is preferable to an unfinished ML pipeline or prolonged dependency setup.
- Anti-pattern to avoid: one command that both inspects waveform files and probes optional packages; a missing package can abort before you learn the `.npz` structure.
- Measure progress against the deliverable: if a step is not getting you closer to reading `/root/data/*.npz`, choosing picks, and writing `/root/results.csv`, deprioritize it.
- Prefer `numpy`-only or `numpy`+`scipy` baselines when the environment is limited; a complete heuristic baseline is better than an unfinished ML setup.
- Validate imports in the intended interpreter before choosing SeisBench or ObsPy-heavy workflows, and use `numpy.load` directly for `.npz` inspection when needed.
- Treat missing optional ML/seismology packages as a reason to pivot, not as a reason to spend the run on environment repair.
- Implement batch processing early: test on a small sample first, print candidate peaks and chosen `pick_idx` values for several traces, then run all files.
- Do not force exactly one P and one S pick per file; zero picks for a phase is allowed when evidence is weak.
- Avoid fallback logic that manufactures picks from maxima or fixed default windows when thresholds fail.
- If heuristic outputs are unstable (for example many picks at index 0, S before P, or unchanged chosen indices despite code changes), recalibrate from observed data or metadata instead of guessing new thresholds.
- Before finishing, sanity-check that `/root/results.csv` exists, is non-empty, has header `file_name,phase,pick_idx`, and stores integer sample indices rather than seconds.

- Treat SeisBench/ObsPy as optional accelerators, not prerequisites. A simple end-to-end picker that writes the required CSV is preferred over unfinished dependency setup.
- Use a strict progress test: inspect sample files -> get plausible picks on one file -> batch all files -> write CSV.
- Prefer one verified inference path over repeated model switches: once a baseline works on one file, keep that path and scale it before experimenting.
- For `.npz` inspection, prefer short robust scripts that print keys, shapes, and small metadata fields.
- Fallback baseline when optional libraries are unavailable: inspect metadata, normalize channel names, pick P from vertical/onset evidence, then pick S from later horizontal-energy increase, and emit only confident picks.
- Treat optional-library checks as secondary to data inspection: a working `numpy.load` + heuristic picker is enough to complete the task.
- Use heavy libraries only when already available or confirmed quickly with a real import; otherwise continue with the lightweight baseline.
- Favor a complete heuristic batch run over extended tuning on one trace.
- If a command hangs, times out, or starts downloading models, pivot instead of waiting.


## Tips

## Validation and Finalization

- Before finalizing, inspect picks across a sample of files; treat these patterns as failure signals:
- Also treat these as failure signals before finalizing:
  - many picks clustering at exactly or near index 0
  - nearly the same P or S index repeated across many different files
  - chosen picks that remain almost unchanged after major code or threshold changes
  - exactly one P and one S for nearly every file or picks chosen only by fallback maxima
- If phase metadata is available in the `.npz` files, use it for a quick spot-check on several files; do not rely only on CSV shape or the statement "P before S" as evidence of quality.
  - many P picks at or near the first few samples
  - nearly identical P/S offsets across many different files
  - widespread S picks with weak or no visible energy change after the P pick
- If those artifacts appear, adjust the method or thresholds before scaling or finalizing.
- Do minimal final checks: `/root/results.csv` exists, header is exactly `file_name,phase,pick_idx`, phases are only `P`/`S`, and `pick_idx` values are plausible sample indices.
- Once the CSV is produced and these checks pass, finalize immediately; do not keep exploring alternative methods, extra model installs, or nonessential tuning.

- If progress stalls in package setup before any picks are produced, treat that as a workflow failure and pivot back to the lightweight baseline rather than continuing environment work.
- Before any extended tuning, confirm the batch script can actually produce `/root/results.csv`; if not, fix output generation first.
- Before finalizing, confirm you actually executed the picker across files and wrote `/root/results.csv` from batch processing rather than leaving the work at inspection or single-file experimentation.
- When metadata was available during inspection, do one final sanity check that your chosen P/S picks are not grossly inconsistent with the observed metadata-derived ranges or quality annotations.
- If optional ML libraries were unavailable or unproductive, finalize with the working heuristic baseline rather than returning to package setup.
- Before any optional refinement, confirm you can process the full `/root/data/*.npz` set and emit a valid `/root/results.csv` in batch.
- Check a small batch of files before finalizing: confirm picks are supported by component-specific behavior (for example stronger vertical onset evidence for P and stronger horizontal or envelope increase after P for S when orientations are available).
- If picks were generated from a collapsed all-channel RMS/mean trace, verify that phase-specific component evidence still supports them; otherwise switch to separate P/S scoring by component.
- Confirm that all file reads and writes used the required absolute paths (`/root/data/...`, `/root/results.csv`).
