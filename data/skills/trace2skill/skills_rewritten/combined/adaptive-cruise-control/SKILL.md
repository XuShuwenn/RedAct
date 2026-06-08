---
name: adaptive-cruise-control
description: "Implement adaptive cruise control systems with PID controllers for vehicle speed and distance regulation."
---

# Adaptive Cruise Control

## When to Use

- Implement PID control loops for vehicle speed regulation
- Maintain safe following distance from lead vehicle
- Simulate vehicle dynamics with acceleration constraints

## Key Concepts

- **PID Controller**: output = Kp×error + Ki×∫error + Kd×d(error)/dt
- **Setpoint**: target speed (e.g., 30 m/s)
- **Error**: setpoint - measured_value
- **Anti-windup**: prevent integral term from exceeding bounds

- **Sensor data role**: treat provided sensor logs as exogenous inputs (for example timestamps, lead-vehicle behavior, and measured gap) unless the task explicitly defines them as the ego vehicle's reference trajectory
- **Acceptance criteria**: explicit metric thresholds, safety limits, artifact requirements, and required output formats are hard gates for completion, not documentation notes

## Workflow

1. Read vehicle parameters from YAML (mass, acceleration limits, etc.) and confirm the actual schema before using keys in code; do not assume sections such as `simulation` or fields such as `dt` exist unless verified.

   - If the task or environment specifies an exact action/tool-call syntax, allowed tool names, message structure, or exact completion token, treat that protocol as a hard requirement from the first step to the last. Use only the permitted format and emit the required completion string literally when the task is complete.
   - Before the first action, lock onto the required protocol in operational terms: allowed tool names, required action envelope, command style, and exact completion token. Reject habitual alternate wrappers or improvised tool names. A protocol mismatch is a blocking failure even if the technical solution is otherwise correct.
   - When execution is required, issue concrete shell/Python commands with explicit programs, paths, and arguments. Prefer commands that are directly runnable in the observed environment; if an interpreter/path/filename is wrong, correct it and rerun rather than replacing execution with prose.

   - If a required value is missing from the observed schema, re-open the config to confirm, then derive it only from the task/spec or use an explicit guarded default and document that choice in code; do not introduce unchecked dependencies on imagined paths.
 Preserve the task's required runtime interfaces, file roles, class/function signatures, and runtime loading paths instead of hard-coding values or collapsing files for convenience.
2. Read sensor data (time, ego_speed, lead_speed, distance) and inspect enough of the dataset to map regime changes, signal availability over time, row count, timestep behavior, missing-data patterns, and when lead-vehicle interaction first becomes valid/present; do not infer missing signals from only the first few rows.


   - Explicitly locate the first/last timestamps or row ranges where lead-vehicle measurements are valid, confirm how missing lead fields are represented (for example `NaN`/blank), and build a quick phase map (for example: initial cruise, first valid lead detection, follow engagement, any emergency event, lead disappearance/return to cruise) before implementing mode logic.
   - Before explaining behavior with scenario-specific causes or implementing follow/emergency logic, confirm those claims from the dataset with a file-aware check that reaches representative lead-interaction regions, not just opening rows. If you have not verified where lead signals become present/non-null and where follow conditions can occur, treat the diagnosis and implementation assumptions as unverified.
   - Preserve any initial no-lead interval in both controller behavior and outputs: stay in cruise-only behavior until lead interaction becomes valid, and keep follow/lead-specific output fields blank or otherwise task-specified during that interval rather than fabricating early follow activity.

   - If any inspection output is truncated, empty unexpectedly, or only shows an early prefix, treat the data interpretation as unverified. Re-run with a reliable full-file, CSV-aware check until you confirm row counts, where lead-vehicle signals first become non-null/present, and whether any columns are truly absent before designing controller or mode logic around that assumption.
3. Implement PID controller class with configurable gains, and keep controller behavior, ACC mode/safety logic, and simulation/evaluation orchestration separated so gains, mode conditions, and metrics can change without entangling plant updates.

   - Prefer a small staged pipeline when the task has multiple deliverables: keep reusable PID logic, ACC supervisory/mode decisions, simulation execution, tuning, and reporting/evaluation separable so each stage can be rerun and validated independently without changing required interfaces.

4. Implement ACC system with cruise/follow/emergency modes from the stated spec/config; in follow mode, make spacing/safety control the primary objective and use speed regulation only as a limiter/cap unless the task specifies a different control law. Handle mode transitions explicitly by resetting or reinitializing PID state as needed to avoid derivative kick or stale integral carryover.

   - Do not add lead-detection ranges, distance cutoffs, or other gating rules that suppress valid follow intervals unless the task explicitly requires them; poor spacing metrics should be fixed by correcting control/simulation behavior, not by redefining when the lead vehicle counts.
   - If braking or emergency response appears one or more steps late, inspect the exact update order around the transition window: sensor ingestion, filtering/smoothing, mode detection, PID/state reset, command computation, and plant update. Treat delay introduced by stale state, smoothing, or post-update detection as a structural bug to fix before retuning gains.
   - If follow-mode outputs disappear unexpectedly, spacing fields go blank, or the simulation reverts to `cruise` while lead interaction should still be active, treat that as a blocking logic/state bug. Inspect lead-presence gating, mode-transition conditions, output-column wiring, and spacing-state updates before any further gain tuning or final reporting.

5. Simulate closed-loop vehicle dynamics: propagate ego state from the previous simulated state and `accel_cmd`, while treating recorded data only as exogenous inputs unless the task explicitly specifies replay semantics. If follow behavior must respond to controller changes, initialize from the measured gap if needed and propagate compatible ego/lead motion dynamically (for example via positions/gap) instead of mixing logged per-step ego outcomes or incompatible sampled gaps into the simulated plant.

   - If logged ego speed or ego state is being replayed inside the controlled plant, treat that as a blocking model bug. Fix state propagation and output wiring so reported trajectories come from the simulated closed loop; do not fall back to measured ego outputs merely to make CSVs or plots look expected.

   - If you uncover this mismatch during debugging, do not preserve expected-looking traces by reverting outputs to recorded ego values. Keep the model internally consistent and let validation reflect the true closed-loop behavior while you repair the implementation.
   - Before any gain search or major rewrite, prove the simulation is trustworthy with concrete checks from current artifacts/code: compare propagated state against expected scenario semantics, inspect representative traces around follow/emergency transitions, and confirm spacing/position updates are internally consistent. If large mismatches remain, stop tuning and repair the model first instead of changing assumptions or control structure ad hoc.
6. After each file write or major edit, immediately reopen the file and confirm the concrete implementation/content is present, complete, untruncated, and syntactically/import-valid before building on it; treat malformed content, escaped newlines, partial writes, suspicious truncation, placeholder prose, or summary-style write/edit descriptions as blocking errors.

   - Keep changes auditable: after each claimed code, config, or tuning change, show the exact write/edit command and verify the resulting file or artifact directly.
   - Write the literal artifact content required by the file type: executable Python, valid YAML/JSON/CSV, or other structured output. Never use narrative placeholders such as "implemented...", "updated...", or summary text in place of the file's actual contents.
   - Before making a targeted edit, read the relevant section containing the exact code/text to change. If your view is truncated or only shows a file prefix, reopen the needed region first instead of inferring unseen content.
   - Verify actual implementation and artifact content, not intentions: inspect enough contiguous lines/functions/classes to confirm runnable logic is present, and reopen generated result/report files too. Do not rely on write summaries, tiny snippets, file existence, line counts, or grep hits alone; if a source file contains prose instead of code or a result file has blank/unpopulated expected fields, fix it before proceeding.

7. Tune PID parameters using measured simulation outcomes only after the closed-loop simulation is behaving plausibly, and verify that materially different gain sets produce different trajectories or metrics; if they do not, treat that as a blocking implementation bug. Inspect saved traces around cruise→follow transitions, emergency entry, and steady-state regions to distinguish tuning issues from state/update or command-arbitration bugs.

   - Keep tuning evidence-driven and reproducible: use a consistent metrics script or evaluation loop, record resulting metrics, save the best validated gains in a task-appropriate artifact, and have the final simulation/report path load that artifact rather than copying gains manually. If multiple retuning attempts leave metrics nearly unchanged, still far outside spec, or traces show physically implausible/unsafe behavior, stop tuning and debug structure instead—controller coupling, desired-gap/sign conventions, state propagation, mode transitions, safety overrides, and metric computation—before changing gains again.
   - If the evaluator or simulation is open-loop, replaying logged ego behavior, or otherwise insensitive to controller changes, treat all gains from that loop as invalid. Keep the evaluator and acceptance calculation fixed while tuning controller behavior; change evaluation code only for a confirmed bug or explicit task requirement, then rerun the full pipeline and treat earlier results as non-comparable.
   - Treat persistent impossible safety outputs (for example negative gap/min-distance, ego overtaking the lead in a scenario that should remain separated, or catastrophically bad spacing across many gain sets) as structural bugs, not tuning misses. Switch to targeted debugging of plant propagation, command arbitration, lead/ego position updates, and mode logic, then rerun validation from that repaired baseline.
   - If traces or metrics expose a likely structural defect, stop packaging or broad retuning and run a fix loop on that defect: inspect the full relevant code path, edit it, rerun the scenario that exposed the bug, and confirm the problematic metrics or trace segment changed in the expected direction before moving on.
   - If the simulation/evaluation loop is validated and manual retuning still stalls, run a small scripted parameter sweep over plausible gain ranges, compare the task metrics from each run, and refine around the best candidates instead of guessing gains one at a time.

8. Run the full required simulation/analysis pipeline and compute the task's stated metrics from complete artifacts, not partial console logs. For mixed driving regimes, map each metric to the operating regime and interval defined by the task (for example cruise-speed metrics during cruise-valid segments and spacing metrics during settled follow segments); if the spec instead requires whole-run evaluation, use that exactly.

   - Build a runnable evaluation loop early: get the simulator/export path and a separate metric-checking script or command working before extensive tuning so every controller change can be judged by fresh quantitative outputs.
   - After any substantive change to controller logic, simulation/state propagation, report generation, or metric code, invalidate earlier metric claims and rerun the full pipeline before trusting numbers.
   - If the run emits warnings, partial output, or truncated report reads, treat verification as incomplete until you inspect the full regenerated artifact or recompute the metrics directly from produced files.
   - Do not narrow steady-state windows, move evaluation start times, add alternate masks, or rely on self-selected filtered subsets just because current metrics look bad. Treat such changes as evaluator modifications that require explicit spec justification.
   - Keep diagnostic sub-window checks separate from acceptance reporting unless the specification explicitly defines them as acceptance criteria.
   - If outputs contain behavior that contradicts ACC intent or safety expectations, treat the affected conclusions as unverified until you inspect regenerated artifacts directly and resolve the contradiction.


   - Use exact executable shell/Python commands with concrete filenames and arguments; do not use natural-language tool calls such as "run the tuning script" or "analyze the output".
   - Keep diagnostic sub-window metrics separate from acceptance metrics. Do not narrow the evaluation window, add favorable masks, or substitute slices such as "stable-only," "follow-only," or "non-emergency" unless the specification explicitly defines that scope.
   - Keep the evaluation pipeline and metric definitions fixed while tuning controller behavior. Change the evaluator only for a confirmed bug or explicit task requirement, then rerun the complete pipeline from the updated baseline before trusting any numbers.
   - Do not infer pass/fail from sparse progress prints or truncated output; inspect the generated artifacts or recompute metrics directly from them, and rerun after any controller, simulation, or metric-code change.
9. Keep evaluation logic, metric definitions, scenario assumptions, mode conditions, and interaction/tool-call protocol aligned with the task; if data meaning is ambiguous, validate the interpretation before changing plant or sensor semantics. Do not change metric definitions, masks, windows, detection logic, or simulation semantics just to obtain passing numbers.

   - Do not stop based on an unsupported feasibility judgment. If you think a target may be impossible under the stated plant limits or scenario, support that claim with explicit calculations or full-run evidence tied to the spec; otherwise keep iterating or report the requirement as unmet and unproven.
   - Before making architecture or flow changes for poor behavior, inspect the full relevant control path in code and connect the suspected defect to observed traces/metrics. Do not diagnose resets, arbitration bugs, or mode-logic faults from a header skim or intuition alone.

10. Before finishing, inspect the final deliverables directly and verify every required metric, safety bound, filename, row count, column order, runtime wiring, file/output requirement, and exact completion/output protocol from the produced artifacts themselves; if anything is unmet or unverified, continue iterating or report it explicitly as unresolved.

   - Do a two-level final check: (a) structural checks such as expected file presence, row counts, headers, and first-row semantics, then (b) representative inspection around mapped phase transitions and safety-critical events before trusting aggregate metrics.
   - When you edit reporting/evaluation code, verify both layers: reopen the changed source to confirm the intended logic is fully present and untruncated, then regenerate and inspect the report/artifact to confirm the new fields or pass/fail outputs actually appear.
   - Reconcile contradictions before finalizing: if row counts, metric values, scenario interpretations, or validation outputs disagree across commands or runs, re-check the authoritative artifacts and rerun validation until one consistent latest result is established.
   - Do a final requirement-by-requirement checklist and mark each item PASS, FAIL, or UNVERIFIED from the latest full validated run only. Treat threshold violations, malformed or missing outputs, absent required columns, blank follow/safety fields when they should be populated, missing expected mode transitions, wrong row counts, or wrong completion/protocol output as blocking failures.


   - Perform an explicit requirement-by-requirement pass/fail checklist against the original task wording. Treat artifact mismatches such as wrong row counts, missing outputs, malformed files, blank follow/safety fields when they should be populated, or missing expected mode transitions as blocking failures just like failed numeric metrics.
   - Copy reported numbers only from the latest verified run/output. If a metric is not visible in current artifacts, mark it unverified instead of reusing earlier results.
11. If any required metric or safety check fails, treat the task as unfinished: keep iterating or state explicitly which requirement remains unmet; do not present the task as successful, complete, or "working" while known failures remain. Producing the requested files is not sufficient for completion, and you must not rationalize failed metrics as close enough, likely computed differently, or acceptable due to scenario difficulty. Emit any required completion token only when every required completion condition is satisfied.

   - A self-check that reports any FAIL, unmet threshold, missing artifact, or unverified metric is a blocking result. Use it to drive another debug/tune cycle; do not convert partial passes such as "3/5 targets achieved" into a completion claim.
   - Do not write summaries such as "successful," "acceptable," "ready," or "good enough" when the latest validation still contains any failed or unverified requirement.
   - Before any final response or completion signal, compare every required threshold and artifact against the latest verified run one by one. If any metric is failing, missing, out of bounds, supported only by prose, or otherwise unverified, do not mark the task complete and do not soften the result; report the unmet requirement explicitly unless the task defines a different failure-reporting protocol.
   - If the environment specifies an exact completion token or action string, verify it from the task instructions and emit that literal string exactly, with no paraphrase or extra trailing text when strict output is required.

## Modes

- **cruise**: No lead vehicle - maintain set speed
- **follow**: Lead vehicle detected - maintain safe distance
- **emergency**: TTC below threshold - apply braking

## Important Parameters

- Time headway, minimum gap, acceleration limits
- Speed rise time, overshoot, steady-state error targets

- Treat performance targets as hard pass/fail gates: rise time, overshoot, steady-state error, minimum distance, TTC, and related safety limits must be checked against stated thresholds before declaring completion.

## Tips

- Load PID gains from YAML or other task-specified artifacts at runtime rather than hard-coding them in controller logic
- Use discrete-time equations: error[t] - error[t-1] for derivative
- Clamp output to acceleration limits [-8.0, 3.0] m/s²

- Use simplified scenarios only for quick debugging; always close the loop with end-to-end validation on the actual task dataset, full simulation, and original success metrics
- Tune gains from measured results, not intuition alone; keep a best-known validated configuration and replace it only with gains that pass the current controller version's checks
- Do not assume config paths or nested fields exist unless you verified them; prefer validated keys or explicit guarded defaults
- Do not infer controller quality from partial console output; if output is truncated, inspect saved CSV/YAML/results files as the source of truth
- After editing Python sources, read them back or run a quick compile/import check before any tuning; truncated or malformed files invalidate all downstream debugging
- Do not replay controlled ego states from logs inside a closed-loop simulation unless the task explicitly requires replay semantics
- Treat recorded lead-vehicle behavior, timestamps, and measured gap as inputs; keep controlled ego states, logged outputs, and computed metrics consistent with the same simulation state
- If the dataset includes per-step `distance`, first verify whether it is an exogenous measured input, a replay/evaluation signal, or a state tied to a prior ego trajectory. Use it directly only when the task defines that semantics and it stays consistent with your simulation; otherwise initialize from it if needed and propagate compatible ego/lead states so controller changes can affect spacing metrics without mixing logged and simulated trajectories
- In closed-loop follow simulations, initialize lead position from the first observed gap when needed, update lead motion from lead-speed or other exogenous inputs, and compute simulated spacing from compatible states so follow metrics remain physically meaningful
- In follow mode, ensure the spacing controller can actually drive commanded acceleration; use speed control as a cap or more restrictive limiter only when the spec requires it. If command arbitration makes spacing metrics insensitive to gain changes, fix the control structure before further retuning
- Add simple supervisory logic around PID when required by the task: anti-windup/integral clamping under saturation, integral reset on mode changes, blocking positive acceleration when already too close, TTC-triggered emergency braking, and small deadbands near zero spacing error to reduce chatter
- When generating time-series CSV output, confirm whether each row should record pre-update or post-update state, ensure the first row matches the required initial-state semantics, and inspect headers/first rows to verify column order and timestep semantics
- Before accepting tuning results, run a sanity check with two very different gain sets; if rise time, steady-state error, or spacing metrics are unchanged, the evaluation loop is not properly coupled to the controller
- If safety metrics or spacing behavior stay nearly constant across retuning attempts, debug model/state-update logic first: check sign conventions, desired-gap formula, emergency triggers, distance/position initialization, mode transitions, and whether the distance loop is being structurally suppressed
- Inspect saved time-series outputs around mode transitions and steady-state segments before changing gains; use those traces to decide whether the issue is tuning, follow logic, or simulation coupling
- Do not rewrite plant/sensor semantics, cruise/follow definitions, evaluation windows, metric formulas, or lead-detection/gating rules to make results look better unless the task specification explicitly requires it
- Treat physically impossible outputs, contradictory row counts, malformed files, unsafe collisions, or mismatched timestamp/row semantics as bugs to fix, not acceptable artifacts
- If the task specifies an exact tool-call syntax, final response token, completion string, or output protocol, use it literally


- If the environment requires a strict tool/action protocol or literal completion token, use that format exactly on every step; do not improvise alternate tool-call syntaxes or free-form completion text
- When verifying implementation files, inspect enough of each file to confirm the expected code structure exists, not just that the file exists or has nonzero length
- If a sanity check with very different gains leaves metrics unchanged, stop tuning and repair the simulation/evaluation coupling before choosing final gains
- Do not claim metrics or final conclusions from truncated output; inspect saved artifacts or rerun until every cited result is fully visible
- Keep the evaluation yardstick fixed while debugging and tuning; improvements that appear only after self-chosen masks, windows, or evaluator changes are unproven until justified by the spec


- When optional lead-vehicle signals appear partway through the run, inspect enough rows with a CSV-aware/full-file view to identify when they first become valid and wire mode-entry logic to that observed availability rather than assuming they exist from t=0
- Before tuning, write down a simple phase map from the input data and use those checkpoints for trace inspection and debugging
- Keep runtime controller code, tuning artifacts, and final deliverable generation separate so production runs can reload validated parameters and reproduce reported results cleanly
- Ground every code change in observed file text: read the specific region you will modify, then edit that exact content rather than inferred logic from a truncated snippet
- Never replace concrete code/config/result writes with summaries of intended functionality; if a file should contain code, parameters, or metrics output, write the actual content and read it back
- During output validation, compare the first and last few exported rows against the update loop to catch timestamp/state alignment bugs, off-by-one logging, or shifted initial conditions that metric summaries may not reveal
- When follow mode begins after a period with no valid lead vehicle, initialize follow state from the first valid interaction sample and reset or seed PID state intentionally to avoid artificial transients at mode entry
- When unsafe behavior appears despite reasonable gains, inspect the exact samples around the onset: raw input distance/lead-speed changes, filtering/smoothing, mode-switch timing, PID resets, and when braking authority actually reaches the plant
- Use regime-aware diagnostics during tuning, but keep final pass/fail aligned to the task's stated metric windows and masks
- Treat tuning outputs, simulation logs, and metrics reports as evidence, not as files to hand-edit into a preferred answer; modify source config/code, rerun, and trust only the regenerated artifacts
- Before writing a report or final summary, copy each cited metric from the latest verified artifact or evaluator output and cross-check that pass/fail statements match those numbers exactly


## Validation and Spec Compliance

- Treat task-environment interaction requirements as hard constraints: use the exact required tool/action syntax, command style, message structure, allowed tool names, and final completion signal literally, with no alternate tool-call formats at any step.
- Treat the latest full validation run as the completion gate. If any required metric is out of bounds, unreported, only partially computed, or derived from a disconnected/open-loop evaluation when closed-loop performance is required, do not say the task is complete.
- Do not replace a failing overall metric with a narrower self-selected pass metric, altered window, changed mask, new detection threshold, or modified evaluator after the fact unless the task explicitly defines that method as the acceptance criterion.
- Validate generated artifacts for both integrity and semantics: file contents should be complete and concrete, key columns should be populated when expected, mode transitions should occur under the scenario conditions, and cited metrics should agree with the artifacts you reference.
- Do not cite metric values from truncated output, earlier runs, or memory. Reopen the latest full report/results or recompute from the latest artifacts, then quote only what is explicitly supported there.
- Compare each required metric against its threshold explicitly before any success claim. If even one required metric still fails in the latest verified run, continue iterating or report the task as incomplete with the remaining gaps.
- If you changed controller code, simulation code, report generation, or metric logic, invalidate earlier metric claims and rerun end-to-end before concluding anything.
- If repeated runs show impossible safety behavior or metrics that barely change across very different gains, stop tuning and debug the simulation/control structure before claiming progress.
- Do not trust conclusions drawn from failed or ambiguous data-inspection commands; re-inspect until dataset contents are confirmed before relying on claims such as "lead data is absent" or "follow mode never occurs."
- If the latest artifacts do not explicitly support a claimed metric value or success statement, report it as unverified or unmet rather than asserting completion.
- Before the last message, perform a final protocol check and ensure no required metric, safety item, artifact requirement, or protocol condition remains failed or unverified.

## Validation and Spec Compliance

- Preserve the task's metric definitions exactly. Do **not** redefine overshoot, steady-state error, evaluation windows, masks, thresholds, or success criteria unless the task explicitly instructs you to.
- Preserve required class/function signatures, file names, and input semantics unless the task explicitly allows changes.
- Only claim requirements are met when the current run's visible outputs or recomputed produced data explicitly show the required metrics; if output is partial, truncated, or missing a metric, report it as unverified.
- Check generated artifacts for integrity, not just existence: confirm files are complete, rows and columns match the spec, formatting is correct, and tails are not truncated.
- Verify that required scenarios and modes (`cruise`, `follow`, `emergency`) are actually exercised when applicable, and report the requested performance and safety metrics explicitly.
- If repeated runs show unchanged results, stop and inspect whether your edits were actually applied or whether the simulation/evaluation is disconnected from the controller.
- Do not explain away failed metrics; treat misses as evidence to change gains, mode logic, data handling, or simulation setup and then re-validate.
- Follow any task-specific execution or interaction protocol exactly, including required tool formats and exact completion tokens.