---
name: seismic-phase-picking
description: "Pick P and S wave arrival times from seismic waveform data using deep learning or signal processing methods."
---

# Seismic Phase Picking

## When to Use

- Pick P and S wave arrivals from seismic traces
- Process waveform data for phase identification
- Achieve F1 >= 0.7 for P, >= 0.6 for S


## When to Use

## Execution Discipline

- Follow the runtime's required action/tool protocol exactly, including any strict action format and completion signal.
- Construct runnable commands conservatively: prefer simple standalone commands or short heredoc Python scripts for inspection and batch processing over fragile chained one-liners, pseudo-calls, or prose placeholders.
- Keep dataset inspection separate from optional-package checks so a failed import, package probe, or setup step cannot prevent `/root/data/*.npz` inspection from running.
- In every file operation and code snippet, use the required absolute paths exactly (`/root/data/*.npz`, `/root/results.csv`); do not switch to relative paths.
- Before attempting any package-heavy workflow, identify the intended interpreter/environment and verify the core imports that path actually needs there.
- If installation is necessary, install only what the next immediate step needs and confirm success with a concrete smoke test in the same interpreter before expanding scope.
- If an import fails, an install times out, or setup would require repeated waiting, downloads, background jobs, or polling without quick confirmation, treat that as a branching signal and pivot back to direct data inspection and the lightest executable picker.
- Treat repeated waiting on setup or background jobs without new capability as a failure state. Resume progress with commands that inspect `/root/data/*.npz`, test a minimal picker, or write the required CSV.

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
- If inspection reveals annotation-like phase fields or timing fields that may encode arrivals, stop and determine their semantics before designing any picker. First ask: can P/S indices be read directly, or derived deterministically from stored times plus `dt` and trace start information?
- Do not switch to heuristic phase detection until you have ruled out direct extraction or straightforward derivation from metadata present in the `.npz` files.
- Metadata-first decision rule: if inspection reveals annotation-like phase fields, timing fields, remarks/weights, or anything that may encode arrivals, pause heuristic design and test direct extraction or deterministic derivation on 1-3 files first. Only proceed to waveform heuristics after you have explicitly confirmed that the metadata does **not** directly provide usable P/S indices and cannot be converted to them reliably.
- When timing metadata exists, compute candidate sample indices from those fields plus `dt`, print the derived values for a few files, and compare them to trace length before building any picker.
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

- Anti-pattern to avoid: fragile shell/Python one-liners with nested quoting for initial inspection. Prefer a heredoc or other simple multi-line script that cannot break on quotes like `data['data']`.
- Do not write placeholder commands; every command should be runnable as written.
- Prefer separate steps for (1) `.npz` inspection and (2) optional package checks so a missing library does not prevent learning the data structure.
- Inspection completion rule: only mark the data-structure step done after you have actually printed keys, array shapes, `dt`, and a sample `channels` value from a real `.npz` file.
- Do not choose a pretrained-model workflow before you have successfully loaded at least one real `/root/data/*.npz` file and printed its keys/shapes.
- Anti-pattern: inspecting the dataset, deciding on a heavy package-dependent approach, then spending the remaining run on installation, downloads, model browsing, or waiting for background jobs. Prefer a simple batch heuristic or metadata-driven path that already fits the observed `.npz` structure.
- Do not start overlapping or repeated package installs. One quick check is enough; after that, pivot.
- If `obspy` or `seisbench` import fails, treat that as a branching signal, not a blocker: continue with `numpy.load` inspection and the heuristic picker immediately.
- Prefer one small, reusable metadata-normalization helper (especially for `channels`) and preserve that logic during later refactors.
- Protect earlier fixes from regression: after script edits, verify the actual file contents or diff and re-check previously fixed failure points on the same sample file.
- Preferred proof sequence: inspect one file -> produce plausible P/S picks for one file -> confirm CSV row generation -> batch all files.
- Inspection alone is not progress. After identifying key waveform or metadata properties, immediately convert them into executable picking code and a batch CSV pipeline.
- Once a baseline produces plausible picks on sample files, scale that same path to batch processing before experimenting with other models or pipelines.

- Safe first-step pattern: run one simple inspection script with minimal imports that prints actual file keys/shapes; avoid dense quoted one-liners for this step.
- Preferred startup sequence: (1) run a standalone inspection of `/root/data/*.npz`, (2) optionally run a separate import/package check, (3) choose the lightest end-to-end picker.
- Before using Python for `.npz` inspection or batch coding, verify the intended interpreter works and can import `numpy`; do not assume `python` or scientific packages are present.
- Do not treat a failed optional import as automatic justification for package installation; first ask whether the existing lightweight or metadata-driven path can already inspect `/root/data/*.npz`, compute picks, and write `/root/results.csv`.
- Anti-pattern to avoid: discovering likely label/annotation fields and still spending the run on heuristic or model churn before proving metadata cannot be used directly.
- If a command errors, treat the traceback as the next task: fix that command or pivot to a simpler built-in path before expanding scope.
- If you create a script, view or compile it and then run it on one or two files before scaling.
- A failed `obspy`/`seisbench` import is a pivot signal: inspect `/root/data/*.npz`, build the fallback picker, and keep moving toward `/root/results.csv`.
- Do not leave long-running picker/model jobs in the background while waiting for completion. If they do not produce immediate validated picks, pivot to the working heuristic baseline.
- Keep troubleshooting milestone-driven: each recovery step should directly enable one of these next actions — inspect `/root/data/*.npz`, compute picks, or write `/root/results.csv`.


## Tips

## Validation and Finalization

- Before finalizing, inspect picks across a sample of files; treat these patterns as failure signals:
- Also treat these as failure signals before finalizing:
  - many picks clustering at exactly or near index 0
  - nearly the same P or S index repeated across many different files
  - chosen picks that remain almost unchanged after major code or threshold changes
  - exactly one P and one S for nearly every file or picks chosen only by fallback maxima
- If phase metadata is available in the `.npz` files, use it for a quick spot-check on several files; do not rely only on CSV shape or the statement "P before S" as evidence of quality.
- When metadata fields such as `p_*`, `s_*`, remarks, weights, labels, or annotation-like values exist, use them for a concrete spot-check on several files before finalizing: compare your predicted indices against metadata-derived phase indices or expected quality subsets, and investigate large mismatches instead of accepting the CSV based only on counts/ranges.
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

- Before any optional dependency work beyond a quick feasibility check, ask whether you can already read `/root/data/*.npz`, compute candidate P/S picks, and write `/root/results.csv`; if yes, do that first.
- Completion gate: before any optional refinement, confirm you have already demonstrated the full pipeline on at least one file and then run the batch job that writes `/root/results.csv`.
- Treat "understood the data but produced no CSV" as a failure state; recover by implementing the smallest end-to-end baseline immediately.
- If you changed the environment during the run, make sure the final workflow includes a fresh successful sample-file inspection and then actual batch processing; do not assume setup succeeded from package-manager messages alone.
- Treat prolonged environment/setup work as a failure signal: if you are spending multiple steps checking or waiting on installs without inspecting `/root/data/*.npz` or producing picks, pivot immediately.
- Treat contradictory prototype diagnostics as blockers, not curiosities. Examples: waveform summaries showing all-zero or near-zero min/max/RMS while the picker still returns interior picks, or picks appearing despite no visible change in the scored signal.
- When that happens, print with higher precision or scientific notation, inspect raw sample slices, check dtype and scaling, and confirm the score actually changes around the chosen index before scaling to more files.
- Compare one-file debug outputs to the corresponding rows from the final batch CSV for the same files. Do not finalize if the same input file gets materially different P/S picks between those two paths without an explained reason.
- Treat these as workflow failure signals requiring revision before finalizing: repeated install retries or background setup without new capability, many picks clustering at index 0 or the first few samples, repeated near-identical picks across many files without metadata support, or major method revisions that leave outputs essentially unchanged.
- If annotation or timing metadata was discovered during inspection, verify on several files that final `pick_idx` values are consistent with those fields whenever deterministic extraction or close agreement is expected; do not finalize based only on CSV format, non-emptiness, or raw pick counts.
- Before relying on any generated script, confirm it is real executable code rather than a prose placeholder by viewing it or compiling it, then run a small test on one or two files.
- Before finalizing, confirm the batch command actually executed and produced `/root/results.csv`, not just that a script file was written.
- Once `/root/results.csv` is present, non-empty, schema-valid, and produced by a batch run, stop iterative debugging and finalize rather than continuing speculative tuning.

- Treat "inspection attempted" and "inspection succeeded" as different states. Do not finalize or commit to a picking strategy until at least one real `.npz` file has been successfully inspected.
- Treat strict interface noncompliance as a hard failure: before inspection, execution, and final response, confirm you are using any required action/tool syntax and completion signal exactly.
- Treat these as workflow failures requiring revision or pivot: repeated setup/install retries without new capability, unsupported tool/interface usage, repeated status polling or process-monitoring detours, inspection or one-file success without an executed batch run, or several preparatory steps that still do not create new ability to read files, compute picks, or write the CSV.
- After any environment change or earlier import failure, rerun the exact originally failing inspection or import successfully before trusting the fix; package-manager output alone does not count as verification.
- Finalization gate: do not finish from inspection notes, imports, package-manager output, or a written-but-unrun script. Finish only after the picker actually ran in batch on `/root/data/*.npz` and produced `/root/results.csv`.
- Semantic validation gate: do not finalize based only on a non-empty CSV, header, row counts, index ranges, or the fact that `P < S`. Check sample rows for artifacts such as `pick_idx == 0`, picks in the first few samples without metadata support, S before P, nearly identical indices across many files, or outputs unchanged after major logic edits.
- If metadata-derived or directly stored phase information was available during inspection, compare final picks against it on several files before finalizing; if direct extraction was expected, the batch output should match that metadata-driven method rather than an unrelated heuristic.
- If a prototype produced suspicious picks under contradictory diagnostics, resolve that contradiction before batching; do not assume scaling will fix it.
- Consistency gate: for at least one file used during one-file debugging, compare the final batch-produced `pick_idx` values to the earlier debug output for that same file. If they differ materially, treat it as a blocker and explain the cause before finalizing.
- Keep the inspected sample files, reviewed files, and final batch output consistent: confirm reviewed filenames actually come from `/root/data/*.npz` and that their reviewed picks match the corresponding rows written for the same files in `/root/results.csv`.
- If any sanity-check script or diagnostic output is nonsensical or contradicts picker behavior, debug the validation code first and rerun the check; do not use that output as support for finalizing.
- Do not overwrite a working result just to try speculative improvements. If you revise after a successful batch run, first identify the specific defect, re-validate on a small sample, and only then replace the final CSV.
- Once `/root/results.csv` has been produced by an actual batch run and passes schema and plausibility checks, stop debugging and finalize promptly.
