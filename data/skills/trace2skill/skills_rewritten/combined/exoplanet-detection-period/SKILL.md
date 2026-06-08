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
- Pre-flight protocol check before the first tool call: identify the exact required tool/action wrapper, allowed tool names, whether observations must be awaited between calls, the exact allowed writable directory, and the exact final completion string/token. Use that checklist literally for every tool call and for the final response.
- Before **every** tool call, do a brief compliance check: exact required wrapper/schema, allowed tool name, and a literal runnable command or complete code payload only; never substitute descriptive text such as "run the analysis" or "inspect the file" unless the environment explicitly defines it as executable.
- If you notice any drift from the required tool-call schema mid-run, correct course on the very next message; do not keep using the alternate format just because earlier calls returned observations.
- Use only explicitly available tools, and send literal executable commands or complete code payloads only; do **not** send narrative placeholders such as "inspect the file" or "run the analysis" as if they were commands.
- Before any file write, confirm that the destination path is inside an explicitly allowed writable directory from the task/environment instructions; do **not** assume `/root` is writable just because the input file is under `/root/data/`.
- If writable directories are restricted or ambiguous, do not create helper scripts or `/root/period.txt` in `/root` by default; place every generated file only in a directory the environment explicitly allows.
- Treat `/root/data/` as an input location, not automatic permission to write alongside it or elsewhere under `/root` unless the environment explicitly says so.
- Before the first write command, name the exact allowed output/script paths you will use and keep them consistent for the rest of the run.
- Wait for and inspect each tool observation before making claims about side effects or results; only say `/root/period.txt` was written or checked if the corresponding command actually ran successfully.
- Treat file paths as task-scoped constraints, not defaults from this skill. Use `/root/data/tess_lc.txt` and `/root/period.txt` only when the task/environment allows those paths; otherwise use the exact allowed absolute paths and keep helper outputs inside allowed directories.
- Do not let scientific progress override interface rules: a computed period is not a completed answer until both the required protocol and the required completion signal are satisfied.
- Do not continue with more tool calls after emitting the required completion signal.
- If the environment requires an exact completion token (for example `ACTION: TASK_COMPLETE`), the final response must be that exact token alone with no summary, explanation, or extra formatting unless the task explicitly allows extra prose.
- As soon as the deliverable is ready, stop tool use and emit the exact required completion signal/token verbatim.


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
   - If allowed writable directories are not explicit yet, pause and determine them from the task/environment instructions before creating helper scripts, plots, temp files, or the final output.
   - Only create scripts, temp files, summaries, and the final period file in confirmed-allowed locations.
   - If the task requires a different output path, tool-call schema, or exact completion token, treat that task-specific requirement as overriding this skill's defaults.

1. Filter data by quality flags and outliers
   - Prefer light cleaning first: keep quality-flag filtering, remove only clear non-finite points and obvious outliers, and avoid aggressive clipping that could erase shallow transit dips.
2. Remove stellar activity variability (rotational modulation, starspots)

   - Flatten long-timescale stellar variability with a gentle window/filter sized from the measured cadence, expected transit duration, and stellar-variability timescale so it suppresses rotation/starspot structure without erasing short transit dips.
   - If major time gaps are present, detrend segments separately or use a method that does not smooth across the gaps.
   - When a clearly large observational gap is present, split the filtered time series at that gap and detrend each segment separately before recombining for the transit search; do not let one smoothing window bridge the discontinuity.
3. Inspect the dataset enough to estimate cadence, time span, variability amplitude, and plausible transit timescales before locking detrending or search settings
   - Convert any detrending/flattening window specified in days or transit-timescale terms into the units the API actually expects (often number of cadences/samples) using the measured cadence; do not pass raw day values to sample-count parameters.
   - After the quick schema check, make sure the real analysis still loads the full filtered dataset from disk rather than operating only on the preview rows.
3a. Estimate any dominant stellar-variability/rotation timescale early (for example with a coarse Lomb-Scargle check) and use it to guide detrending and to avoid mistaking stellar modulation for a planet period.
   - If the file is large, use a quick script or summary statistics on the filtered data rather than relying on a tiny header sample.
   - Write down the dominant variability timescale you measured and use that specific value when choosing detrending windows or segmented detrending, rather than adjusting preprocessing blindly.
   - Explicitly compare any strong transit-search candidate to the measured variability timescale and its simple harmonics; down-rank candidates that track stellar variability unless the folded signal still shows narrow repeated transit-like dips.
4. Use a staged search: start with cheap diagnostics or coarse scans, then refine only promising periods
   - Preferred default: run one broad transit-sensitive search to locate the candidate region, then run a narrower higher-resolution search around the best candidate to reach the final 5-decimal value efficiently.
   - Treat the broad search as discovery and the narrow rerun as numeric refinement; do not rely on a single coarse global grid for the final reported precision.

4a. For transiting exoplanets, use a transit-sensitive search (BLS/TLS) for the final candidate; use Lomb-Scargle only for variability/alias diagnostics, not as the sole final picker.
   - If two completed lightweight runs converge closely on the same candidate and no task requirement remains unmet, treat that as sufficient support: perform the planned cheap validation, write `/root/period.txt`, and finish instead of escalating to package installation or optional method changes.
   - For `transitleastsquares`, read the candidate from the object returned by the search call (for example `results = model.power(...); candidate = results.period`); do **not** read period attributes from the TLS model object itself.
   - If TLS throws an API error once or the first real run is killed/stalls, stop broad TLS retries immediately: either rerun with an explicitly reduced workload or switch to verified `astropy.timeseries.BoxLeastSquares` for the primary result path.
   - If a lightweight available method already gives a stable candidate and the required validation checks pass, finalize from that result rather than escalating to optional package installation or unfamiliar tooling.
   - Only switch to an optional transit package if it is genuinely needed and you can verify the exact installed API immediately.

5. Validate candidate periods before finalizing: inspect other strong peaks, check harmonic/alias relationships, and phase-fold plausible candidates

   - Do not write `/root/period.txt` from the first top-scoring peak alone.
   - For transit-search results, re-test candidates whose fitted duration/depth is physically implausible or pinned to the search-grid boundary.
   - If sigma clipping or other outlier rejection was used, compare at least one conservative/no-clipping variant when feasible so real transit dips were not removed.
   - Before finalizing, check at least one competing peak or harmonic candidate (for example `P/2`, `2P`, or a nearby strong peak) and confirm the chosen period gives the clearest repeated transit-like dips when phase-folded.
   - When feasible, add one cheap eclipsing-binary guard such as odd/even event consistency before committing the final period.

   - If the search method explicitly warns that the true period may be a multiple, harmonic, or alias of the reported peak, treat the result as unresolved and run a targeted comparison of those specific alternatives before writing `/root/period.txt`.
   - Keep a short candidate ledger from observed outputs only: note each serious candidate period and which completed run produced it. Only choose among candidates that were explicitly printed, saved in a verified summary, or directly computed in the just-observed successful run.
   - Before using any run to choose the next candidate, sanity-check that its reported best period, top-peak list, score/power, and fitted duration are mutually consistent and finite.
   - Treat self-contradictory search output as invalid for decision-making: examples include `NaN`/`inf`/`-inf` power, impossible fitted durations, or a reported best period that disagrees with the listed top peaks.
   - If multiple runs disagree materially, do not introduce a new unsourced value as a compromise or guess. Perform one explicit tie-break comparison among the observed candidates and finalize only the winner of that documented comparison.
   - Match the verification action to the uncertainty: when testing whether a longer, shorter, or harmonic period is plausible, use phase-folds, local re-searches, or predicted-event checks at those candidate periods; do not use generic file inspection that cannot discriminate between them.
   - Examples of invalid verification for period ambiguity: printing a few file rows, checking only the file endpoint, or rereading `/root/period.txt` without a new discriminating analysis. Those actions do not tell `P` from `2P` and should not be used to clear an ambiguity warning.
   - If transit-specific tooling is unavailable, only use a fallback candidate after a direct coherence check shows repeated transit-like dips at that period in the folded light curve and after checking obvious aliases/harmonics.
6. If detrending or search settings materially affect the result, compare a small number of reasonable alternatives and prefer a period that remains consistent

   - Do not rely on a single hard-coded detrending window or search range when stellar variability is strong; test at least one nearby reasonable alternative or justify the bounds from the observed baseline/cadence.
   - Treat a candidate that shifts substantially across reasonable detrending choices as unvalidated; keep testing rather than finalizing immediately.
   - After trying a small set of reasonable detrending/search variants, stop expanding the search space: choose the candidate that is most stable across those checks and move to output.
   - Once a candidate is validated enough for the task, write `/root/period.txt` and finish; do not let optional extra validation block delivery.

   - If two lightweight or moderate runs (for example coarse+refined BLS, or BLS under two reasonable detrendings) agree on the same candidate within small drift, treat that as convergence: do a cheap final check, write `/root/period.txt`, and stop.
   - Do not escalate to a heavier method such as TLS after convergence unless the task specifically requires it or the existing candidate failed validation.
   - Repeated agreement from completed lightweight runs is enough evidence to finalize: if the same transit-like candidate recurs twice with similar value and passes one alias/phase-fold or competing-peak check, prefer immediate output over launching a new heavy search.
   - If a later optional refinement or confirmation run is killed, times out, or fails after an earlier completed run produced a validated candidate, immediately fall back to that earlier candidate or do one cheap local refinement around it and finish.
7. Identify the most plausible validated exoplanet orbital period.
   - For transit-like signals, treat a validated BLS-derived candidate from the detrended lightcurve as the default primary result unless stronger transit-specific evidence favors another period.
8. Round to 5 decimal places and write exactly one numeric value to `/root/period.txt` as soon as a defensible result is available.
   - If a candidate has already converged across your planned lightweight checks, you may do one short final precision pass or result-print step centered on that validated candidate to capture the exact scalar value for 5-decimal rounding.
   - Keep that precision step narrow and reporting-focused; do not reopen a broad exploratory search once the candidate period is already validated.
9. Re-open `/root/period.txt`, verify it exists and contains exactly one plausible numeric value, then finish instead of planning open-ended refinements.
   - Allow at most one short final validation after the first completed candidate is written, and only if it was part of the plan (for example one harmonic check or one narrow local refinement).
   - If that planned check agrees, fails, or is inconclusive, keep the existing earlier validated candidate unless the new run cleanly and clearly supersedes it.
   - Use an evidence chain before finalizing: validly formatted execution call -> observed completed run with candidate/result -> validly formatted file write succeeds -> validly formatted file read/check confirms exact contents.
   - When extracting the chosen period from search results, convert any NumPy/array-like single-value object to a plain Python float before rounding/formatting and writing the file.
   - Once this file check passes, do not launch refinement, comparison, cleanup, or inspection commands unless a specific unresolved issue still affects the chosen period.
   - The default final sequence is: verify `/root/period.txt` -> emit the exact required completion signal -> stop.


   - Apply a stopping rule: once a candidate has passed the planned lightweight checks, `/root/period.txt` is verified, and any required completion syntax is known, stop and finish immediately.
   - Do not reopen the search just because another refinement might move the fifth decimal place.
   - If two reasonable validation runs disagree modestly, prefer the candidate from the earlier fully completed, transit-validated, stable run rather than continuing ad hoc script churn.

## Output Format

Single value to `/root/period.txt`.


Only write `/root/period.txt` after the period-search run has visibly completed and the selected period has been checked against the search diagnostics.


## Output Format

## Execution Checklist

- Verify the input file exists and inspect a few rows before analysis.
- Inspect any header/comment lines first to confirm the true column meanings and ordering before parsing; use those observed labels to map time, flux, quality flag, and flux uncertainty instead of assuming the schema blindly.
- Also inspect the file endpoint or equivalent summary (for example `tail`, row count, min/max time) so the observation span is known before choosing detrending windows or period-search bounds.
- In the same early inspection phase, do one quick environment probe for any package you plan to rely on (`lightkurve`, `transitleastsquares`, etc.); only build the main pipeline around packages whose import succeeded and whose API you can verify quickly.
- Before designing the pipeline, obtain at least one compact full-file summary from disk (for example row count, count of usable `quality==0` rows, time span, cadence estimate, and major gaps); do not choose preprocessing/search settings from header rows alone.
- Record the observed time span and use it to justify the initial search range rather than relying on a canned default.
- Do not stop at a tiny header sample: also obtain full-file context with a lightweight command or script (for example row count, quality-flag distribution, time span, cadence, and major gaps) before locking preprocessing/search settings.
- If you create `/root/find_period.py` or any helper script, write actual executable Python code, not a prose plan or placeholder text.
- Use a strict artifact sequence for any generated script: write executable code -> read the saved file back once -> optionally syntax-check (`python3 -m py_compile ...`) -> only then execute it.
- Treat any generated script containing narrative sentences, TODO-style placeholders, or missing executable analysis steps as invalid; rewrite it before execution.
- Never run a scaffold that contains only comments, docstrings, imports, or high-level step labels. First implement the concrete analysis path that reads the real lightcurve, computes a candidate, and writes `/root/period.txt`.
- Execute the script with a literal command that names the exact saved path (for example `python3 /root/find_period.py`); never use placeholder text such as `python3 analysis script` or other non-executable descriptions.
- Run the exact script you created with its literal path, and do one quick path-consistency check so the created script path, invoked script path, input path, and output path all match the intended allowed absolute paths.

- Validate incrementally before committing to a full pipeline: confirm schema and row count, estimate baseline/cadence/flux scatter, inspect dominant low-frequency variability, and check for major time gaps before fixing preprocessing/search settings.
- If the input is too large to print fully, inspect a small sample to confirm schema, then run a script or shell pipeline that reads the full file directly from disk; do not base the final result on the sample alone.
- Do not describe the intended full-data analysis as if it already happened. After sample/schema inspection, execute a real full-dataset command or script and only then claim analysis results.
- Use quality-flag filtering and detrending before period search.
- Prefer BLS as the main detector for repeating transit dips; use Lomb-Scargle mainly as a supporting variability/alias diagnostic.
- Do not make the core detection step depend only on an unverified external package.
- If you try an unfamiliar transit-search library, first inspect the installed callable signature or a minimal confirmed example before wiring it into the full search; do not guess method names, positional arguments, or constructor kwargs.
- For unfamiliar transit-search packages, do the API check **before** writing the main pipeline around them: import the object, inspect its callable/signature/help, and confirm one minimal working call first.
- Do not write the full analysis script around an unfamiliar library before that inspection. First confirm the constructor signature, then the actual search method name, then one minimal successful call, and only then embed it in the end-to-end pipeline.
- If the first guessed API call fails, stop speculative patching immediately: inspect the real signature/result object, update the core search call, and do not edit plotting, summaries, or `/root/period.txt` extraction until that core call succeeds once.
- Do not spend multiple retries on import-name guesses or result-attribute guesses for an optional package. One failed guess is enough: inspect the installed symbols/call signature/result fields once, then either use that confirmed pattern or abandon the package.
- Spend at most one short API-inspection step and one minimal callable test on an unfamiliar optional package; if that does not yield a confirmed working call, abandon it and return to the verified fallback path.
- After one failed guessed call to an optional library, stop guessing. Use introspection results decisively to update the script to the observed API and run the end-to-end pipeline, or switch immediately to verified `astropy.timeseries.BoxLeastSquares`.
- Do not patch downstream extraction, plotting, or output code while the core search call is still failing. First obtain one successful search result, inspect its returned object/attributes, then wire result access and `/root/period.txt` writing.

- Confirm optional dependencies before making them part of the core search plan; otherwise start with standard available libraries (`numpy`, `scipy`, `astropy`) and use optional transit packages only after a quick import/API check.
- Do not treat ad hoc `pip install ...` attempts as the primary recovery path for missing optional packages. First run one concrete import/API verification; if the package is absent or unclear, switch immediately to the verified in-environment fallback (`astropy.timeseries.BoxLeastSquares`) and complete the task in the same run.

- If dependency checks disagree, treat the package state as unresolved. Run one definitive minimal verification (for example a direct `python -c` import and, if needed, a signature check) and then either use it or abandon it.
- Do not treat ad hoc package installation or a script that prints installation/setup instructions and exits as the default recovery path. Prefer a same-invocation completed workflow using verified available tools (prefer `astropy.timeseries.BoxLeastSquares`) rather than a branch that requires a second manual run.
- After any failed package attempt, return to an end-to-end path within one short retry: use the corrected confirmed call or immediately switch to a verified fallback (prefer `astropy.timeseries.BoxLeastSquares`) instead of continuing open-ended library exploration.
- Wait for the analysis/search to actually finish before trusting logs or output files.
- Treat a run as incomplete unless you see a final search summary, a specific reported candidate period/statistic, or a confirmed clean completion plus final result lines; progress bars, initialization lines, partial output, or an existing `/root/period.txt` do not prove the detection step finished.
- If using a heavy search (for example TLS), cap parallelism first to reduce kill/memory risk.
- Do not stop at script creation or launch; inspect the completed run output, confirm a specific candidate period was returned, then verify `/root/period.txt`.
- If command output is truncated, rerun with reduced verbosity or save the summary/result to an allowed file under `/root/` rather than inferring success from partial logs.
- Do not claim an import failure, candidate period, or validation result from partial stdout alone. Get the final lines, traceback, or a compact saved summary first, then decide.
- If needed, rerun the analysis so it emits only compact end-state diagnostics such as best period, score, duration, top competing peaks, and the effective search bounds/settings.
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
- Before trusting `/root/period.txt`, match it to the producing run: the selected numeric value must also appear in the observed stdout/stderr, a verified saved summary, or a directly inspected in-memory result from that same completed run.
- Do not finalize from `/root/period.txt` if its value does not match any explicitly observed candidate from the current analysis history; rerun or perform a targeted comparison instead.

- Before the final response, check the task instructions one last time and emit the exact required completion string/token with no extra prose if one is specified.
- Final protocol gate: verify both halves of task completion before stopping: (1) tool calls used the environment's required schema, and (2) the final response is the exact required completion token/string, with nothing appended if the environment requires an exact-only terminator.
- Do not end immediately after submitting `python ...` or another analysis command. Wait for the observation, confirm the run finished cleanly, then verify the output file and emit the exact completion signal.
- When extracting the final best period from `numpy`/`astropy` results, convert it to a plain scalar before rounding or formatting (for example `best_period = float(np.asarray(candidate).item())` for a single-value result); do not call `round(...)` on a NumPy array.
- After that file check, do not create extra verification/refinement scripts unless a specific unresolved issue blocks completion.
- If the deliverable is ready, stop tool use and emit the exact required completion string immediately.
- If the first method fails, is too heavy, or the run is incomplete, switch promptly to a lighter verified fallback (prefer `astropy.timeseries.BoxLeastSquares` / BLS over prolonged debugging of heavier or optional transit packages), re-run end-to-end, and re-check the output file before concluding.

- Distinguish timeout from resource kill before retrying: if the process is killed (for example exit code 137 or `Killed`), do not rerun unchanged with a longer timeout.
- After a kill from TLS before meaningful progress, make the next step concretely smaller: cap workers/threads, narrow the period range, reduce grid density, or switch directly to BLS. Do not spend multiple retries proving the same unconstrained TLS call still fails.

- Treat exit code `137`, `Killed`, or similar termination messages as resource-failure evidence, not as proof the search merely needs more time.
- If the same heavy workflow or package stack is killed twice, stop iterating on that stack for the current task. Immediately switch to a lighter confirmed path or make one clearly reduced-workload final retry.
- Treat missing common shell utilities as an environment-limitation signal: stop depending on extra system-inspection commands and switch to simpler self-contained Python/shell commands that directly produce the needed result.
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
- When a detrending API uses `window_length` or similar sample-based arguments, compute that value from the measured cadence and force any integer/odd-length requirements before running the full search.

- Prefer transit-specific searches (Box Least Squares / BLS, or TLS when available) for orbital period detection

- If TLS is available and its API is confirmed quickly, use it to locate the candidate period region, then refine the final numeric value with a denser BLS scan around that region before writing `/root/period.txt`.
- Use Lomb-Scargle primarily as a supporting diagnostic for stellar variability or cross-checking, not as the sole final period picker for transit signals

- Do not finalize a transit period from Lomb-Scargle alone; treat it only as a hint for variability, aliases, or candidate windows to confirm with a transit-sensitive search or clear phase-folded transit evidence.
- Prefer a coarse-to-fine workflow: Lomb-Scargle or downsampled/coarse BLS first, then narrow-range refinement
- If a heavy first-pass search is used, cap threads/workers before the run, get one tractable candidate region, then refine locally instead of starting with an all-core full-resolution sweep.
- Use the measured baseline, cadence, and dominant variability timescale to set practical search bounds and detrending windows instead of broad canned defaults.
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
- Treat timeouts, truncation, missing final summaries, method exceptions, or partial progress output as no result. Do not finalize from a file read alone after any of those states.
- If the final successful run is not fully observed, rerun in a lighter or shorter-summary form until you can see the candidate period and then verify `/root/period.txt` from that same run.
- Treat a submitted-but-unchecked command as no result. Finalize only from an observed completed run with a readable candidate period and a verified `/root/period.txt`.
- Treat invalid or unfinished search output as no result: examples include best power `-inf`, boundary-hit best periods exactly at the grid minimum/maximum, inconsistent summary fields, or missing final optimum reporting.

- Treat repeated API exceptions (`AttributeError`, unexpected kwargs, wrong result shape) as upstream failure. Stop editing summaries, plotting, or file-output extraction until one search call runs successfully and you have inspected the actual returned result object.
- Before finalizing, perform at least one sanity check: compare with a second method or detrending setting, inspect phase-folded behavior, or check obvious aliases/harmonics and stellar-rotation-like periods.
- Do not finalize the raw top BLS/TLS peak by itself. At minimum, compare it against one nearby competing peak or an obvious harmonic/alias candidate (`P`, `P/2`, `2P`), then inspect a phase-folded view or equivalent transit-shape check.
- Do not finalize from a single detrending+search configuration alone when a second reasonable check is feasible.
- If the measured stellar-variability period or its simple harmonics overlap the candidate, down-rank that period unless the folded signal still shows a clearly transit-like narrow dip.
- When a candidate period is found, check that predicted transit epochs recur at consistent times in the unfolded lightcurve; if an expected event is missing, verify whether it falls in a known data gap before rejecting the candidate.
- Make the event-consistency check concrete: list a few predicted transit times across the baseline and verify that multiple expected epochs coincide with actual dips in the filtered lightcurve; a missing event can be acceptable if it lands inside a previously identified observational gap.
- If a heavy method is killed or exceeds resources, do not just retry the same full-resolution search with minor runtime tweaks. Change strategy: cap threads/workers if appropriate, narrow the period range, reduce resolution safely, add a coarse first-pass scan, downsample only if transit sensitivity is still adequate, or switch to a lighter fallback.
- If a later exploratory run is invalid but an earlier valid run produced a strong candidate, fall back to the earlier valid candidate.
- Always have a fallback path that still writes the best available validated period estimate to `/root/period.txt` if the preferred search fails.

- For BLS/TLS-style searches, do not finalize from peak score alone; inspect the recovered duration (and depth when available) and treat implausibly broad events or boundary-hit durations as invalid until rechecked.
- If an earlier completed search produced a strong candidate and a later heavier run is killed, unavailable, or unfinished, keep the earlier validated candidate instead of blocking completion on the heavier method.
- Preserve evidence from successful earlier runs. If you have already observed a best period, score, duration, or folded-dip support from a completed lightweight run, treat those outputs as the current best result until a later run cleanly beats them.
- Give earlier coherent full-data results priority over later invalid acceleration, binning, or downsampling runs. Never replace a validated candidate with a contradictory new period taken from a run you already classified as partial, broken, or internally inconsistent.
- If a later exploratory or refinement run is invalid but an earlier run produced a valid candidate, fall back to the earlier valid candidate rather than continuing open-ended optimization.
- If candidate periods disagree strongly across runs or preprocessing choices, do not finalize by picking one ad hoc; resolve the conflict with a narrowed transit-aware search or by checking harmonics/aliases explicitly.
- Use a stopping rule: once one candidate remains best after the planned lightweight checks, write `/root/period.txt` and finish instead of launching optional extra searches.
- Define the decision rule before extra validation: for example, keep the candidate that is stable across the initial completed run plus one planned cross-check, or fall back to the earlier completed validated run if a later exploratory run conflicts or fails.
- If an earlier completed search and one refinement or alternate lightweight check agree closely on the same period, prefer completion over optional package debugging. Do not block delivery on upgrading to TLS or another specialized tool unless the task explicitly requires it.
- If multiple candidates appear, resolve them with one compact same-format comparison summary from the chosen validated method rather than mixing truncated runs, ad hoc dip inspections, and incompatible metrics.
- If a later comparison run is incomplete, truncated, or based on settings that did not take effect, do not let it reopen the decision. Revert to the last earlier validated candidate and finish.

- If two completed runs or a coarse-plus-refined search converge closely on the same candidate and no stronger contradiction appears, treat that as sufficient support to finalize.
- Treat late-stage exploratory scripts as high risk: they can introduce implementation errors and conflicting periods without improving the deliverable.
- If you already have a completed validated result, do not replace it based only on a later exploratory run unless that later run is itself clean, completed, and clearly stronger by the same validation criteria.
- Do not block completion on upgrading from an already-supported candidate to a preferred package or method.
- Re-opening an existing `/root/period.txt` is only a format check, not validation of the producing analysis.

- Finalization requires an observed chain: executed analysis command -> completion/result observation -> `/root/period.txt` checked -> exact required completion signal.
- Also verify provenance: the observed completion came from that command rather than stale output, and the checked `/root/period.txt` was produced by that same successful run.
- Do not stop after launching the analysis command. Completion requires all links in the chain to be visible in the transcript: valid command sent, run finished with an observed result, `/root/period.txt` freshly verified, then exact completion signal emitted.
- If any earlier `/root/period.txt` may exist, remove it before the decisive final run or otherwise prove the file was freshly written by that run before trusting its contents.
- A statement like "next I will run the script" does not satisfy this chain. Missing any link is a hard stop.
- After verifying `/root/period.txt`, emit the exact required completion token/string with no substitutions, paraphrase, or extra summary text when the environment requires an exact terminator.
- If any link in that chain is missing from the transcript, the task is not complete yet.
- A file read alone is not proof of success. Require all three before finalizing: (1) valid command syntax was actually sent, (2) the run completed cleanly enough to expose a candidate/result, and (3) `/root/period.txt` was freshly checked after that run.
- Treat self-contradictory or numerically broken search output as invalid and do not use it to choose the next candidate. Examples: non-finite score/power (`NaN`, `inf`, `-inf`), impossible fitted durations, a reported best period that disagrees with listed top peaks, or summary fields that contradict each other.
- If a tool or search output raises a specific warning about ambiguity (for example possible multiples or harmonics), resolve that warning with a direct comparison before finalizing; do not downgrade it to an optional note.
- The direct comparison must target the warned alternatives themselves and produce observable evidence for choosing one; unrelated inspection of raw rows, endpoints, or stale output files does not count as resolution.
- Do not count unrelated inspection as validation. Example: viewing a few file rows or the file endpoint does not test whether `P` or `2P` is the better period.
- If a later refinement, coarse-speedup, or downsampled run is invalid, internally inconsistent, killed, or unfinished, keep the last earlier validated candidate as the current best result. Replace an earlier strong candidate only when the newer run is numerically sane and clearly better supported.
- Base the final explanation only on quantities you actually observed in stdout/stderr, saved summaries, plots you explicitly generated, or values you computed and printed. Do not state transit depth, duration, phase behavior, or confirmation-test results unless those outputs were produced in the run you inspected.
- If you only reopened the output file, you may report only the file value and the checks you actually observed from the producing run. Do **not** add unprinted transit depth, duration, center phase, or phase-fold quality claims from memory or assumption.
- When candidates conflict, describe only the documented comparison you actually executed; do not resolve the conflict with unsupported astrophysical narrative.
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


