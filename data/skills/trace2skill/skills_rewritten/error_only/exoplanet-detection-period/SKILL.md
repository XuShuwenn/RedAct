---
name: exoplanet-detection-period
description: "Detect exoplanet periods in TESS lightcurve data by filtering, removing stellar activity variability, and identifying orbital periods."
---

# Exoplanet Period Detection from Lightcurve

## Environment/Protocol First

- Before using this skill, read the task and environment instructions for required tool-call syntax, output format, and completion signaling.
- Follow any prescribed action/tool format literally for every tool call; do not substitute another style.
- If the task requires an exact final completion string or token, output it exactly when finishing.
- Treat protocol compliance as mandatory: a correct period in `/root/period.txt` does not complete the task if the interface contract is violated.

- Before the first tool call, extract the exact required tool/action schema and any exact final completion string from the environment instructions; treat both as hard requirements, not style preferences.
- If the environment prescribes a specific wrapper/schema, use that exact structure on every tool call and at handoff; do not improvise alternate tool names, wrappers, tags, pseudo-XML, markdown code-block tool calls, or a prose-only ending.
- Use only explicitly available tools, and send literal executable commands or complete code payloads only; do **not** send narrative placeholders such as "inspect the file" or "run the analysis" as if they were commands.
- Before any file write, confirm that the destination path is inside an explicitly allowed writable directory from the task/environment instructions; do **not** assume `/root` is writable just because the input file is under `/root/data/`.
- Wait for and inspect each tool observation before making claims about side effects or results; only say `/root/period.txt` was written or checked if the corresponding command actually ran successfully.
- Treat file paths as task-scoped constraints, not defaults from this skill. Use `/root/data/tess_lc.txt` and `/root/period.txt` only when the task/environment allows those paths; otherwise use the exact allowed absolute paths and keep helper outputs inside allowed directories.
- Do not let scientific progress override interface rules: a computed period is not a completed answer until both the required protocol and the required completion signal are satisfied.
- Do not continue with more tool calls after emitting the required completion signal.


## When to Use

- Find periodic signals hidden in stellar activity noise
- Analyze TESS space telescope lightcurve data
- Apply period-finding algorithms to astronomical time series

## Input Format

File `/root/data/tess_lc.txt` with columns:
- Time (MJD)
- Normalized flux
- Quality flag (0 = good)
- Flux uncertainty

## Key Steps

0. Reconcile task-specific path and completion rules before analysis.
   - If the environment explicitly restricts writable locations, obey that restriction even if this skill names `/root/period.txt` as the usual output path.
   - Only create scripts, temp files, summaries, and the final period file in confirmed-allowed locations.
   - If the task requires a different output path, tool-call schema, or exact completion token, treat that task-specific requirement as overriding this skill's defaults.

1. Filter data by quality flags and outliers
2. Remove stellar activity variability (rotational modulation, starspots)

   - Flatten long-timescale stellar variability with a gentle window/filter sized from the measured cadence, expected transit duration, and stellar-variability timescale so it suppresses rotation/starspot structure without erasing short transit dips.
   - If major time gaps are present, detrend segments separately or use a method that does not smooth across the gaps.
3. Inspect the dataset enough to estimate cadence, time span, variability amplitude, and plausible transit timescales before locking detrending or search settings
3a. Estimate any dominant stellar-variability/rotation timescale early (for example with a coarse Lomb-Scargle check) and use it to guide detrending and to avoid mistaking stellar modulation for a planet period.
   - If the file is large, use a quick script or summary statistics on the filtered data rather than relying on a tiny header sample.
4. Use a staged search: start with cheap diagnostics or coarse scans, then refine only promising periods

4a. For transiting exoplanets, use a transit-sensitive search (BLS/TLS) for the final candidate; use Lomb-Scargle only for variability/alias diagnostics, not as the sole final picker.
   - If a lightweight available method already gives a stable candidate and the required validation checks pass, finalize from that result rather than escalating to optional package installation or unfamiliar tooling.
   - Only switch to an optional transit package if it is genuinely needed and you can verify the exact installed API immediately.

5. Validate candidate periods before finalizing: inspect other strong peaks, check harmonic/alias relationships, and phase-fold plausible candidates

   - Do not write `/root/period.txt` from the first top-scoring peak alone.
   - For transit-search results, re-test candidates whose fitted duration/depth is physically implausible or pinned to the search-grid boundary.
   - If sigma clipping or other outlier rejection was used, compare at least one conservative/no-clipping variant when feasible so real transit dips were not removed.
   - Before finalizing, check at least one competing peak or harmonic candidate (for example `P/2`, `2P`, or a nearby strong peak) and confirm the chosen period gives the clearest repeated transit-like dips when phase-folded.

   - If the search method explicitly warns that the true period may be a multiple, harmonic, or alias of the reported peak, treat the result as unresolved and run a targeted comparison of those specific alternatives before writing `/root/period.txt`.
   - Match the verification action to the uncertainty: when testing whether a longer, shorter, or harmonic period is plausible, use phase-folds, local re-searches, or predicted-event checks at those candidate periods; do not use generic file inspection that cannot discriminate between them.
   - If transit-specific tooling is unavailable, only use a fallback candidate after a direct coherence check shows repeated transit-like dips at that period in the folded light curve and after checking obvious aliases/harmonics.
6. If detrending or search settings materially affect the result, compare a small number of reasonable alternatives and prefer a period that remains consistent

   - Do not rely on a single hard-coded detrending window or search range when stellar variability is strong; test at least one nearby reasonable alternative or justify the bounds from the observed baseline/cadence.
   - Treat a candidate that shifts substantially across reasonable detrending choices as unvalidated; keep testing rather than finalizing immediately.
   - After trying a small set of reasonable detrending/search variants, stop expanding the search space: choose the candidate that is most stable across those checks and move to output.
   - Once a candidate is validated enough for the task, write `/root/period.txt` and finish; do not let optional extra validation block delivery.

   - If two lightweight or moderate runs (for example coarse+refined BLS, or BLS under two reasonable detrendings) agree on the same candidate within small drift, treat that as convergence: do a cheap final check, write `/root/period.txt`, and stop.
   - Do not escalate to a heavier method such as TLS after convergence unless the task specifically requires it or the existing candidate failed validation.
7. Identify the most plausible validated exoplanet orbital period.
   - For transit-like signals, treat a validated BLS-derived candidate from the detrended lightcurve as the default primary result unless stronger transit-specific evidence favors another period.
8. Round to 5 decimal places and write exactly one numeric value to `/root/period.txt` as soon as a defensible result is available.
9. Re-open `/root/period.txt`, verify it exists and contains exactly one plausible numeric value, then finish instead of planning open-ended refinements.


   - Apply a stopping rule: once a candidate has passed the planned lightweight checks, `/root/period.txt` is verified, and any required completion syntax is known, stop and finish immediately.
   - Do not reopen the search just because another refinement might move the fifth decimal place.
   - If two reasonable validation runs disagree modestly, prefer the candidate from the earlier fully completed, transit-validated, stable run rather than continuing ad hoc script churn.

## Output Format

Single value to `/root/period.txt`.


Only write `/root/period.txt` after the period-search run has visibly completed and the selected period has been checked against the search diagnostics.


## Output Format

## Execution Checklist

- Verify the input file exists and inspect a few rows before analysis.
- Do not stop at a tiny header sample: also obtain full-file context with a lightweight command or script (for example row count, quality-flag distribution, time span, cadence, and major gaps) before locking preprocessing/search settings.
- If you create `/root/find_period.py` or any helper script, write actual executable Python code, not a prose plan or placeholder text.

- Validate incrementally before committing to a full pipeline: confirm schema and row count, estimate baseline/cadence/flux scatter, inspect dominant low-frequency variability, and check for major time gaps before fixing preprocessing/search settings.
- If the input is too large to print fully, inspect a small sample to confirm schema, then run a script or shell pipeline that reads the full file directly from disk; do not base the final result on the sample alone.
- Use quality-flag filtering and detrending before period search.
- Prefer BLS as the main detector for repeating transit dips; use Lomb-Scargle mainly as a supporting variability/alias diagnostic.
- Do not make the core detection step depend only on an unverified external package.
- If you try an unfamiliar transit-search library, first inspect the installed callable signature or a minimal confirmed example before wiring it into the full search; do not guess method names, positional arguments, or constructor kwargs.
- For unfamiliar transit-search packages, do the API check **before** writing the main pipeline around them: import the object, inspect its callable/signature/help, and confirm one minimal working call first.
- Spend at most one short API-inspection step and one minimal callable test on an unfamiliar optional package; if that does not yield a confirmed working call, abandon it and return to the verified fallback path.
- After one failed guessed call to an optional library, stop guessing. Use introspection results decisively to update the script to the observed API and run the end-to-end pipeline, or switch immediately to verified `astropy.timeseries.BoxLeastSquares`.
- Do not patch downstream extraction, plotting, or output code while the core search call is still failing. First obtain one successful search result, inspect its returned object/attributes, then wire result access and `/root/period.txt` writing.

- Confirm optional dependencies before making them part of the core search plan; otherwise start with standard available libraries (`numpy`, `scipy`, `astropy`) and use optional transit packages only after a quick import/API check.

- If dependency checks disagree, treat the package state as unresolved. Run one definitive minimal verification (for example a direct `python -c` import and, if needed, a signature check) and then either use it or abandon it.
- Do not treat ad hoc package installation or a script that prints installation/setup instructions and exits as the default recovery path. Prefer a same-invocation completed workflow using verified available tools (prefer `astropy.timeseries.BoxLeastSquares`) rather than a branch that requires a second manual run.
- After any failed package attempt, return to an end-to-end path within one short retry: use the corrected confirmed call or immediately switch to a verified fallback (prefer `astropy.timeseries.BoxLeastSquares`) instead of continuing open-ended library exploration.
- Wait for the analysis/search to actually finish before trusting logs or output files.
- Treat a run as incomplete unless you see a final search summary, a specific reported candidate period/statistic, or a confirmed clean completion plus final result lines; progress bars, initialization lines, partial output, or an existing `/root/period.txt` do not prove the detection step finished.
- If using a heavy search (for example TLS), cap parallelism first to reduce kill/memory risk.
- Do not stop at script creation or launch; inspect the completed run output, confirm a specific candidate period was returned, then verify `/root/period.txt`.
- If command output is truncated, rerun with reduced verbosity or save the summary/result to an allowed file under `/root/` rather than inferring success from partial logs.
- Treat `/root/period.txt` as valid only if you also observed a substantive completion signal from the run.
- If logs are partial, noisy, or truncated, rerun so the script prints or saves a short final summary under `/root/`, then verify that summary before trusting `/root/period.txt`.
- If you write or modify a script, inspect the saved file once before execution; fix truncation, malformed imports, or incomplete lines first.

- Re-open the saved script and confirm it contains the intended Python source, explicitly reads the real input file, computes a candidate period, and writes `/root/period.txt` before you run it.
- During that inspection, explicitly check for unfinished constructs such as `...`, `TODO`, `pass`, stub variables, missing required arguments, or placeholder method calls in the core analysis path.
- Run the exact file you created using its real path; after writing or editing it, do one quick filename/path consistency check so the created script, invoked script, and expected output path all match exactly.
- After inspecting the saved script, do one quick validity check before relying on it: at minimum confirm the first lines are real Python and, when feasible, run a syntax check such as `python3 -m py_compile /root/find_period.py` before the full execution.
- Do not execute a generated script until every essential step needed to compute the period is concretely implemented and syntactically runnable.
- After running the analysis, confirm `/root/period.txt` exists and contains exactly one numeric value rounded to 5 decimal places.
- Re-open `/root/period.txt` directly and inspect the exact contents; only trust it if the just-finished run visibly reached the file-writing code path.

- Before the final response, check the task instructions one last time and emit the exact required completion string/token with no extra prose if one is specified.
- When extracting the final best period from `numpy`/`astropy` results, convert it to a plain scalar before rounding or formatting (for example `best_period = float(np.asarray(candidate).item())` for a single-value result); do not call `round(...)` on a NumPy array.
- After that file check, do not create extra verification/refinement scripts unless a specific unresolved issue blocks completion.
- If the deliverable is ready, stop tool use and emit the exact required completion string immediately.
- If the first method fails, is too heavy, or the run is incomplete, switch promptly to a lighter verified fallback (prefer `astropy.timeseries.BoxLeastSquares` / BLS over prolonged debugging of heavier or optional transit packages), re-run end-to-end, and re-check the output file before concluding.

- Distinguish timeout from resource kill before retrying: if the process is killed (for example exit code 137 or `Killed`), do not rerun unchanged with a longer timeout.

- Treat exit code `137`, `Killed`, or similar termination messages as resource-failure evidence, not as proof the search merely needs more time.
- After a kill from TLS or another heavy search, the very next retry must change the workload or method: cap threads/workers, narrow the period range, reduce grid density, use a coarse first pass, downsample only if still transit-sensitive, or switch to `astropy.timeseries.BoxLeastSquares`.
- Do not repeat the same expensive search unchanged after a kill signal.
- If a heavy search is killed, stalls, or appears to overuse CPU/RAM, first reduce workload or cap workers/threads (for example via tool settings or environment variables such as `OMP_NUM_THREADS`), then rerun; if still blocked, switch to a lighter fallback that can finish in the current run.
- Ensure every search branch and fallback path ends in one of two states: it writes `/root/period.txt` with a single numeric value, or it raises a clear error that you then handle with another method.
- Do not read tool-exposed session/log paths outside the task's allowed directories, even if a command says full output was saved there.
- Do not treat script creation or launch as completion. Observe the run result, confirm `/root/period.txt`, and only then emit any exact required completion string.

- If the task interface mandates a specific action/tool syntax, check your next message against that syntax before every tool call.
- Convert each planned analysis step into a runnable command before calling the tool: use `python - <<'PY' ... PY`, a saved script, or a direct shell pipeline, not an English description of the step.
- If you inspect only a small sample to learn the schema, ensure the actual computation still loads the input file from disk and processes the full filtered dataset; a header/sample inspection is not the analysis.
- Before using search output to guide the next step, sanity-check that the reported best period, ranking list, score/power, and fitted duration are mutually consistent and numerically finite.
- If a refinement run is invalid but an earlier completed run produced a coherent candidate, revert to that earlier validated candidate instead of switching to a contradictory new one.
- If output is truncated or incomplete, rewrite the command/script to print only a compact final summary (for example best period, score, duration, and top few peaks) or save that summary under an allowed path, then base decisions only on that complete summary.
- If a tool prints warnings like ignored parameters, unchanged search bounds, or default behavior after you tried to modify settings, treat that run as invalid for decision-making until you confirm the intended settings actually took effect.
- Interface compliance check before finishing: confirm every tool call used the required schema from the task/system instructions; if not, correct course immediately instead of continuing in a noncompliant format.
- Do not claim a candidate period, comparison result, or completed search unless the current observed output explicitly shows that result or you have just verified it in an allowed saved file under `/root/`.
- If output is partial, still running, or truncated, describe it as partial/incomplete rather than as a finished finding.
- Do not end on an intention statement such as "I'll refine next." End only after an executed run or fallback has been checked, `/root/period.txt` is verified, and any required completion string has been emitted.

## Techniques

- Box least squares (BLS) algorithm for transit detection
- Lomb-Scargle periodogram for frequency analysis
- Filtering: sigma clipping, quality flag filtering
- Detrending: remove low-frequency stellar variability

- On activity-dominated light curves, explicitly flatten the light curve before transit search (for example median-filter detrending or `LightCurve.flatten(...)` when available); choose a window long enough to preserve short transits and convert from days to samples first when the API expects sample counts.

- Prefer transit-specific searches (Box Least Squares / BLS, or TLS when available) for orbital period detection

- If TLS is available and its API is confirmed quickly, use it to locate the candidate period region, then refine the final numeric value with a denser BLS scan around that region before writing `/root/period.txt`.
- Use Lomb-Scargle primarily as a supporting diagnostic for stellar variability or cross-checking, not as the sole final period picker for transit signals

- Do not finalize a transit period from Lomb-Scargle alone; treat it only as a hint for variability, aliases, or candidate windows to confirm with a transit-sensitive search or clear phase-folded transit evidence.
- Prefer a coarse-to-fine workflow: Lomb-Scargle or downsampled/coarse BLS first, then narrow-range refinement
- Detrend gently: remove low-frequency stellar variability while preserving short box-shaped transit features
- Compare the best period across a few reasonable detrending windows or duration ranges; only finalize when the candidate is consistent rather than drifting with preprocessing

- Do not select the final period solely because one detrending setup gives the highest BLS/TLS power; prefer candidates that remain present across reasonable preprocessing choices and pass an independent transit check.
- If the best-fit transit duration lands on the minimum or maximum searched duration, treat that solution as under-validated: adjust the duration grid or detrending and re-check before accepting the period.
- Treat BLS/TLS solutions whose best duration hits the search-grid maximum or minimum as suspicious; re-detrend or tighten to physically plausible durations instead of accepting the peak
- Use standard scientific Python tools first (`numpy`, `scipy`, `astropy`); if an optional transit package is unavailable, fall back to another valid period-search workflow that can complete in the current run
- If the lightcurve file is large, inspect a small sample to confirm the schema, then process the full file with a script or shell pipeline

- If a strong low-frequency or quasi-sinusoidal signal is present, measure its timescale explicitly and treat matching BLS/TLS peaks as suspect unless the phase-folded signal still looks like a narrow repeating transit.
- When stellar variability is strong, try a small set of detrending windows/scales tied to the measured variability timescale; prefer candidates that survive those changes and remain transit-plausible.
- After a coarse transit search identifies a promising peak, rerun a narrower or finer-resolution search around that period to improve precision before writing `/root/period.txt`.
- If a heavier transit search is slow, unstable, or killed, switch promptly to `astropy.timeseries.BoxLeastSquares` rather than retrying the heavy method repeatedly.
- For computationally heavy searches, set conservative worker/thread limits up front; prefer a completed lower-parallelism run over an aborted maximal-parallelism run.


## New Section

## Validation Before Final Answer

- Confirm the search actually completed and produced a candidate period; do not assume success from truncated logs, progress-only output, or from the mere existence of an output file.
- Treat command output as untrusted until you have evidence the run finished cleanly.
- Treat a submitted-but-unchecked command as no result. Finalize only from an observed completed run with a readable candidate period and a verified `/root/period.txt`.
- Treat invalid or unfinished search output as no result: examples include best power `-inf`, boundary-hit best periods exactly at the grid minimum/maximum, inconsistent summary fields, or missing final optimum reporting.

- Treat repeated API exceptions (`AttributeError`, unexpected kwargs, wrong result shape) as upstream failure. Stop editing summaries, plotting, or file-output extraction until one search call runs successfully and you have inspected the actual returned result object.
- Before finalizing, perform at least one sanity check: compare with a second method or detrending setting, inspect phase-folded behavior, or check obvious aliases/harmonics and stellar-rotation-like periods.
- Do not finalize the raw top BLS/TLS peak by itself. At minimum, compare it against one nearby competing peak or an obvious harmonic/alias candidate (`P`, `P/2`, `2P`), then inspect a phase-folded view or equivalent transit-shape check.
- Do not finalize from a single detrending+search configuration alone when a second reasonable check is feasible.
- If the measured stellar-variability period or its simple harmonics overlap the candidate, down-rank that period unless the folded signal still shows a clearly transit-like narrow dip.
- When a candidate period is found, check that predicted transit epochs recur at consistent times in the unfolded lightcurve; if an expected event is missing, verify whether it falls in a known data gap before rejecting the candidate.
- If a heavy method is killed or exceeds resources, do not just retry the same full-resolution search with minor runtime tweaks. Change strategy: cap threads/workers if appropriate, narrow the period range, reduce resolution safely, add a coarse first-pass scan, downsample only if transit sensitivity is still adequate, or switch to a lighter fallback.
- If a later exploratory run is invalid but an earlier valid run produced a strong candidate, fall back to the earlier valid candidate.
- Always have a fallback path that still writes the best available validated period estimate to `/root/period.txt` if the preferred search fails.

- For BLS/TLS-style searches, do not finalize from peak score alone; inspect the recovered duration (and depth when available) and treat implausibly broad events or boundary-hit durations as invalid until rechecked.
- If an earlier completed search produced a strong candidate and a later heavier run is killed, unavailable, or unfinished, keep the earlier validated candidate instead of blocking completion on the heavier method.
- If a later exploratory or refinement run is invalid but an earlier run produced a valid candidate, fall back to the earlier valid candidate rather than continuing open-ended optimization.
- If candidate periods disagree strongly across runs or preprocessing choices, do not finalize by picking one ad hoc; resolve the conflict with a narrowed transit-aware search or by checking harmonics/aliases explicitly.
- Use a stopping rule: once one candidate remains best after the planned lightweight checks, write `/root/period.txt` and finish instead of launching optional extra searches.

- If two completed runs or a coarse-plus-refined search converge closely on the same candidate and no stronger contradiction appears, treat that as sufficient support to finalize.
- Treat late-stage exploratory scripts as high risk: they can introduce implementation errors and conflicting periods without improving the deliverable.
- If you already have a completed validated result, do not replace it based only on a later exploratory run unless that later run is itself clean, completed, and clearly stronger by the same validation criteria.
- Do not block completion on upgrading from an already-supported candidate to a preferred package or method.
- Re-opening an existing `/root/period.txt` is only a format check, not validation of the producing analysis.

- Finalization requires an observed chain: executed analysis command -> completion/result observation -> `/root/period.txt` checked -> exact required completion signal.
- If any link in that chain is missing from the transcript, the task is not complete yet.
- A file read alone is not proof of success. Require all three before finalizing: (1) valid command syntax was actually sent, (2) the run completed cleanly enough to expose a candidate/result, and (3) `/root/period.txt` was freshly checked after that run.
- Treat self-contradictory or numerically broken search output as invalid and do not use it to choose the next candidate. Examples: non-finite score/power (`NaN`, `inf`, `-inf`), impossible fitted durations, a reported best period that disagrees with listed top peaks, or summary fields that contradict each other.
- If a tool or search output raises a specific warning about ambiguity (for example possible multiples or harmonics), resolve that warning with a direct comparison before finalizing; do not downgrade it to an optional note.
- Do not count unrelated inspection as validation. Example: viewing a few file rows or the file endpoint does not test whether `P` or `2P` is the better period.
- If a later refinement, coarse-speedup, or downsampled run is invalid, internally inconsistent, killed, or unfinished, keep the last earlier validated candidate as the current best result. Replace an earlier strong candidate only when the newer run is numerically sane and clearly better supported.
- Base the final explanation only on quantities you actually observed in stdout/stderr, saved summaries, plots you explicitly generated, or values you computed and printed. Do not state transit depth, duration, phase behavior, or confirmation-test results unless those outputs were produced in the run you inspected.
- When multiple candidate periods conflict, keep the justification tied to the documented comparison you actually ran rather than replacing one unsupported narrative with another.
- If execution evidence is ambiguous, prefer one short clean rerun with reduced or truncated-safe output over reasoning from partial logs.
- The final response itself must follow the task's exact required completion format with no extra prose unless the task explicitly allows it.

## Tips

- scipy.signal for periodogram/BLS
- astropy for lightcurve analysis
- Watch for periods matching stellar rotation (false positives)


- Inspect the data before locking in detrending: estimate the dominant variability timescale and choose filter/window lengths that remove stellar activity without erasing short transit signals.
- Sigma clipping can remove real transit dips; compare results with and without clipping, or use mild clipping, before locking in preprocessing.
- For transiting exoplanets, do not accept the strongest generic periodogram peak without transit checks.
- Report only diagnostics you actually observed (for example best period, SDE/SNR/FAP, top peaks); do not infer or invent metrics.
- After finding a candidate period, phase-fold the lightcurve and confirm repeated transit-like dips before finalizing the answer.
- Re-run the search with at least two reasonable detrending setups when possible, and check nearby harmonic/alias candidates explicitly (P, P/2, 2P, adjacent strong peaks); prefer periods that remain stable and give the clearest repeated transit-like dip.
- Use Lomb-Scargle mainly to characterize stellar rotation/variability; confirm transit periods with a transit-sensitive search plus phase-folded inspection.
- If `transitleastsquares` or another specialized package has import/API issues or is unavailable, fall back to a simpler BLS-style search with available libraries instead of prolonged debugging.

- If you inspect a package and discover the real callable is different from your assumption, rewrite the script from that verified signature; do not keep layering guessed fixes onto the old code path.
- Do not end after launching a script; inspect `/root/period.txt` directly before considering the task complete.
- For a concise workflow on inspection, gap handling, and parameter selection, see [references/inspection-and-validation.md](references/inspection-and-validation.md).
- For concrete implementation patterns and fallback order, read [references/implementation-patterns.md](references/implementation-patterns.md).

- Also inspect for large observation gaps; do not apply one continuous smoother across a major discontinuity when segmented detrending is feasible.
- When using flattening, try one or two nearby window lengths if feasible; prefer a candidate period that stays stable across those reasonable preprocessing choices.
- Preferred fallback sequence when the first attempt fails: verified `astropy.timeseries.BoxLeastSquares` run first, then use Lomb-Scargle only for variability/alias diagnostics, and only use specialized transit packages if you confirm the installed API quickly.
- If a search run is noisy or output is truncated, modify the script to print or save only final candidate summaries instead of inferring the answer from partial progress logs.
- A practical first-pass detrending choice for strong rotational variability is `LightCurve.flatten(...)` or an equivalent smoothing/median-filter trend removal, then run the transit search on the flattened flux.
- For compact examples of independent confirmation when TLS is unavailable or too expensive, see [references/independent-confirmation-patterns.md](references/independent-confirmation-patterns.md).
- For a compact pattern on flattening-window choice and TLS-to-BLS refinement, see [references/transit-refinement-patterns.md](references/transit-refinement-patterns.md).
- For concrete rules on duration-boundary failures, convergence across detrending choices, and cheap fallback transit checks, see [references/candidate-robustness-checks.md](references/candidate-robustness-checks.md).

- DO NOT treat `cat /root/period.txt` as evidence that the analysis found that same value. Right: verify which completed run produced the file and that the reported candidate period matches the file contents. Wrong: read an unexplained file value and then claim the logs supported it.
- When outputs conflict, prefer the candidate with explicit observed support from a completed run plus one validation check; never invent a fresh period that was not shown by the analysis.
- Final write step: normalize array-like outputs to a Python scalar before formatting, e.g. `best_period = float(np.asarray(best_period).item())`; then write `f'{best_period:.5f}'`.


