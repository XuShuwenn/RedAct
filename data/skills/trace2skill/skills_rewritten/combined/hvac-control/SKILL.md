---
name: hvac-control
description: "Implement PID temperature controller for HVAC system to maintain 22.0C with specific performance requirements."
---

# HVAC Temperature Controller

## When to Use

- Implement PID control loops for temperature regulation
- Calibrate thermal system parameters
- Tune controller gains for specific performance criteria

## Targets

- Steady-state error < 0.5°C
- Settling time < 120s
- Overshoot < 10%
- Control duration >= 150s
- Max temperature < 30°C
- Initial temperature ~ 18.0°C (±2°C noise)
- Heater power: 0-100%


- Treat task-specified metric definitions as fixed acceptance criteria.
- Do not loosen settling bands, add smoothing, redefine overshoot, or otherwise change pass/fail measurement logic just to make results pass.
- If performance misses a target, tune the controller, model, duration, or anti-windup behavior instead of changing the metric definition.
- Only change analysis/evaluation code when correcting a clear bug, and keep the corrected logic aligned with the original task specification.

- When evaluating settling or steady-state accuracy, use the band explicitly stated by the task requirements; do not silently tighten it beyond spec or loosen it for convenience.

## Workflow

1. **Calibration**: Run a fixed-power heater step test (commonly ~50% power) long enough to capture the thermal rise clearly; prefer 30+ seconds and enough samples for model fitting (dense logging such as ~20+ points minimum, more when feasible) → `calibration_log.json`

   - For slow thermal plants, extend the step test toward steady state when feasible so the asymptote is visible; one clean, well-observed step is usually enough to identify a usable first-order model.
   - Keep the staged identify-then-control sequence intact when parameters are not already known: collect excitation data first, fit the plant model from the saved calibration artifact second, compute initial gains from the fitted model third, then do closed-loop verification. Avoid starting with ad hoc gain guesses when the plant is not yet identified.
   - Immediately inspect `calibration_log.json` after writing it and confirm the actual schema/fields, timestamps or sample count, and heater/temperature entries before implementing downstream fitting code. Build estimation logic against the observed file structure, not assumptions.

2. **Parameter Estimation**: Fit thermal model (K, tau) → `estimated_params.json`

   - Prefer fitting the explicit first-order step-response model directly to the logged trajectory, e.g. `T(t) = T0 + K*u*(1 - exp(-t/tau))`, estimating `T0` if needed. Check for `scipy` first and prefer `scipy.optimize.curve_fit` or equivalent library fitting before writing custom estimation code; record fit quality such as `r_squared` or RMSE.

   - Decide the estimation approach only after the dependency check: if `scipy` is available, prefer direct first-order step-response fitting; otherwise use a simpler documented fallback. If repeated estimation tweaks barely change `K`/`tau`, stop refining the plant model and move effort to controller design.
   - Prefer the simplest low-order model that fits the calibration data well. If a first-order fit already explains the response, use it as the basis for initial tuning before adding model complexity.
   - Keep stages inspectable and reusable: calibration, estimation, tuning, control, and evaluation may live in separate scripts or one orchestrator, but they must write the listed stage artifacts so each phase can be checked and rerun independently.

3. **Gain Tuning**: Start from the identified first-order model and use a standard model-based rule (prefer IMC/lambda; PI is a strong default for first-order thermal plants) before doing manual retuning → `tuned_gains.json`

   - Preferred default for this skill: calibration step test → first-order fit → IMC-style **PI** tuning with a conservative/moderate `lambda` → closed-loop verification. Only add PID or extra model complexity when verified results show PI is insufficient.
   - Load `estimated_params.json` directly when computing initial gains so tuning is grounded in the persisted identified model rather than console output or memory.
   - Keep the initial design model-based: derive PI gains from the identified first-order model before any ad hoc gain sweep. If the initial IMC/PI design is stable with acceptable overshoot but too slow, reduce `lambda` stepwise before changing controller structure; `lambda ≈ 0.5 * tau` is a strong next candidate for this task family.
   - If the closed loop is stable but finishes below setpoint or shows persistent offset, estimate the heater power required to hold 22.0°C from the fitted model and compare it with the late-run average controller output. If the actual late-run output is materially below the estimated holding level, treat this as insufficient integral action or anti-windup behavior and strengthen that before sweeping other gains.
   - Use manual retuning only after verifying the closed-loop artifacts from that model-based starting point.

4. **Closed-loop Control**: Run to 22.0°C → `control_log.json` + `metrics.json`


   - Prefer implementing calibration, estimation, tuning, closed-loop execution, and metrics writing in one reproducible driver/entry point so each rerun regenerates a consistent artifact set, while keeping stages logically separable for targeted debugging.
   - Persist each phase as machine-readable artifacts and consume those artifacts in later phases: use saved `tuned_gains.json` for the control run and compute `metrics.json` from that same saved `control_log.json` so reported metrics match the executed trajectory.
   - Preserve protective logic from the first closed-loop run onward: keep heater saturation and anti-windup enabled during tuning and verification instead of adding them only at the end.
   - Compute evaluation metrics from the saved closed-loop trajectory using the task's exact definitions and any task/config-specified parameters rather than remembered defaults.
   - When validating the closed-loop run, check operational completeness as well as metric values: confirm the saved trajectory duration meets the task minimum and that the log has enough samples to support the reported metrics.


   - Plan the closed-loop run length up front so settling and duration targets are actually observable; 180s is a good default when allowed because it exceeds the minimum control-duration requirement.

   - When the written task uses steady-state error `< 0.5°C` and that same tolerance for settling, evaluate both against an explicit ±0.5°C band around the setpoint. Encode minimum runtime and any required consecutive in-band logic in the run/evaluation flow itself when applicable, rather than relying on informal post-run interpretation.
   - If measurement noise makes the trajectory hard to interpret, reduce noise sensitivity in the controller path (for example, light measurement filtering) and verify against the raw saved trajectory; do not widen settling bands or otherwise relax task-defined metrics.

   - Match the simulator's step semantics exactly. In discrete step-based simulators, a safe default is: apply current command → read resulting measurement from that step → compute next command. If loop timing/order is wrong, fix that before retuning gains.

   - When behavior looks unexpectedly sluggish, unstable, or one-step delayed, inspect the closed-loop update order in code and logs before changing gains. Verify actuation, plant update, measurement read, controller update, and logging all occur in the intended sequence.

   - Run in a way that exposes full closed-loop completion and final metrics. If stdout is truncated or tailed before metrics appear, rerun without truncation or inspect the generated JSON files directly before making any performance claim.
   - Do not describe overshoot, settling, steady-state error, or improvement/regression for a tuning change unless you inspected the corresponding `metrics.json` or raw `control_log.json` from that run.
   - Treat visibly cut-off output, startup-only text, mid-phase logs, or partial file prints as non-evidence. If output is incomplete or ends mid-message, do not diagnose root cause or retune yet; first confirm the run completed cleanly and directly read the saved artifacts or traceback from that same run.
   - If `cat`, logging, or a verification command shows only the beginning of `metrics.json` or any other required artifact, run another direct read/check before inferring unseen values.

   - Evidence gate for tuning: after each controller run, fully read the current run's `metrics.json` and, when a metric is surprising or borderline, spot-check the matching `control_log.json` before changing gains, filtering, anti-windup, or duration.
   - Do not quote numeric metric values, describe overshoot/settling improvement, or emit the completion token unless those values were fully observed in completed output or read directly from the saved artifacts produced by that same run.



5. **Verification & Finalization**: Confirm the control run finished end-to-end; inspect `estimated_params.json`, `tuned_gains.json`, `control_log.json`, and `metrics.json` directly; compare every item in **Targets** against observed values using the original task-specified metric definitions; if evaluation code appears inconsistent with the spec, change it only to restore exact alignment with the stated definitions, then rerun and cross-check settling time, overshoot, and steady-state error against the raw trajectory before trusting `metrics.json`; ensure `control_log.json` and `metrics.json` come from the same latest completed run; and only then report success or emit any exact runtime/task-specified completion token.

   - Treat evaluator edits as bug fixes only, never as tuning shortcuts. Any analysis-code change must be justified by a direct mismatch with the written task spec and must not relax the acceptance criterion after observing a failing run.

   - Red flag: if a target starts passing immediately after an evaluator edit and before a substantive controller/design change, assume metric drift until proven otherwise. Compare the edited evaluator against the written task definition and the same run's raw `control_log.json` before trusting the new score.
   - Never widen a settling band, add scoring-side smoothing, switch to alternate tolerance interpretations, or introduce persistence/moving-average logic just because a run failed or noise is inconvenient. Change the controller, filtering, anti-windup, or run design instead.
   - After any evaluator change, rerun the controller and verify that any improved reported metrics come from the same new `control_log.json`, not from re-scoring an old trajectory under a different rule.
   - Before any success claim, actually read the relevant final artifact contents from the current run. Do not infer metric values, gains, duration, sample counts, or implementation details from expectations, earlier runs, file existence, or partial stdout.
   - Do not declare success from an earlier good run while submitting a different final run. Verify that the exact latest run you intend to submit completed and that its `control_log.json` and `metrics.json` satisfy every requirement.
   - Final step discipline: once all required artifacts are verified and any mandated completion token/action is known, stop tool use and emit that exact token/string as the next and final step.
   - Do not add narrative summaries, extra inspections, cleanup, or destructive commands after verification unless the task explicitly requires them; preserve the validated final state unchanged.


If any required metric fails, do not present the task as complete. Continue tuning and rerun, or explicitly report the unmet requirement.

- Finalization gate: after the **last** controller/code/tuning change, run the full verification/evaluation step again and read the newly written `metrics.json` before any summary. Do not report final metric values from an earlier run if a later control run occurred.

- Hard fail-stop: if the latest verified `metrics.json` shows even one required target failing, do not use success language, do not emit any completion token, and do not present the task as complete. Either continue iterating or plainly report the remaining failing metric(s).
- Last-run rule: if you perform a final control run, you must also perform the matching evaluation step for that same run before summarizing. A control-only last step is never sufficient evidence for final metrics.

- Success gate: only claim completion or emit any task-specified completion token/string when the latest verified `metrics.json` shows every mandatory target passing and the required artifacts are complete. If even one required metric still fails, do **not** signal completion; continue iterating or report the remaining failure plainly.


If 2-3 retuning attempts produce the same failing pattern (especially settling time, oscillation, or noise-driven non-settling), stop sweeping one gain knob and change the design: add measurement filtering, strengthen anti-windup, or switch tuning/control structure. Once you have explicitly diagnosed a root cause such as noise-sensitive non-settling, do not spend additional runs on lambda-only or gain-scale-only retunes unless you also changed something that directly addresses that diagnosed cause.
0. **Protocol + plant/task pre-flight**: Before any tool use, extract any task-mandated action schema, command wrapper, turn-taking rule, allowed tools, and exact completion token/string. Use that interface verbatim for every step. Also read the simulator/model and configuration files before choosing identification or tuning logic; extract the governing thermal equation when available, plus timestep, ambient conditions, noise, safety limits, and setpoint so the controller matches the actual process assumptions.


   - Make the protocol lock concrete before the first action: write down the exact required wrapper/schema, exact allowed tool names, whether only one action is allowed per turn, and the exact final completion string in the form you will use. If a planned action does not fit that template exactly, do not send it.
   - Treat any tool not explicitly authorized by the environment as unavailable. If only `bash` is allowed, do all reading, writing, editing, and execution through `bash` rather than inventing helper-tool calls.
   - Reserve any exact completion string for the final response only after verification passes, and emit that exact string with no extra prose if the environment requires a token-only finish.
   - Inspect both the main simulator/harness implementation and any plant/config file before designing the experiment or controller workflow. Confirm the actual plant update equation, timestep, actuator clamp, logging fields, required outputs, and evaluator locations; then carry those discovered values consistently through calibration, tuning, simulation, and metrics generation instead of mixing in assumed defaults.
   - If source inspection shows a standard first-order thermal law, preserve that simplification: estimate the matching parameters (`K`, `tau`, and `T0` if needed) and start with a PI controller designed for that model before considering more complex controller structure.
   - Before coding, confirm the actual runnable interpreter and check whether required libraries such as `scipy` are available and necessary. Avoid optional packages like `sklearn` for simple first-order fitting unless they are confirmed installed and genuinely needed.

   - Treat the required interaction/tool protocol as a hard constraint, not a preference. Before the first action, lock the exact allowed tools, wrapper syntax, wait-for-observation rule, and required completion token/string; then use that interface verbatim for the whole task.
   - Use only concrete, executable commands/actions. For shell/Python/file actions, provide literal commands or code with explicit program names, paths, and arguments; do not use placeholders or narrative intent such as "run the workflow", "inspect the results", or "check metrics".
   - Before adding a nonstandard dependency, check that it is both available and necessary. Prefer stdlib plus already-mentioned packages such as `scipy`, and use a fallback or avoid the dependency when the task does not require it.
   - Ground every file edit in inspected text: read the target file first (or confirm it is absent), then patch against exact observed text/anchors. Do not perform blind edits or use vague placeholders like `...`, `existing logic`, or narrative replacement targets.

   - Never issue edits against invented placeholders such as `existing logic`, `controller section`, `previous tuning setting`, or `...`. If you cannot quote the exact observed anchor text, reread the file before patching.
   - After any create/overwrite step, read the saved file back and verify the contents match the intended implementation before relying on it.
   - If you create or overwrite a Python/controller script, immediately inspect the saved file contents and confirm it is executable source code, not a prose placeholder or plan. Run a quick syntax check or smallest safe execution check before deeper debugging so later failures are not caused by a malformed artifact.


Prefer one reproducible end-to-end entry point that performs calibration, parameter estimation, gain tuning, closed-loop control, metrics calculation, and all required JSON writes in sequence, while keeping phases logically separable for targeted reruns.

- Strong default: implement the full workflow in one reproducible script/entry point after inspecting the simulator and environment. Use separate functions/phases internally, but make one command regenerate all required artifacts from calibration through final metrics.
- Use separate phase reruns only for focused debugging; before any final claim, rerun the full pipeline so `estimated_params.json`, `tuned_gains.json`, `control_log.json`, and `metrics.json` all come from one consistent latest execution.
- When creating the entry-point script or any helper script, write literal executable source code only; never save narrative descriptions, TODO text, or summaries in `.py` files.
- Immediately after writing a script, read it back or otherwise inspect the saved file and run a fast validation such as `python -m py_compile <script>` before relying on it for controller/debugging conclusions.
- If the inspected file contents are prose, placeholders, or an incomplete stub instead of executable source code, stop and rewrite the file correctly before any run.


- Between every closed-loop run and every tuning change, read the saved JSON artifacts (`estimated_params.json`, `tuned_gains.json`, `control_log.json`, `metrics.json`) and base the next adjustment on those contents, not on truncated stdout or file existence alone.
- Use a grounded tuning loop: inspect verified metrics/raw trajectory, identify the dominant failure mode (slow rise, overshoot, oscillation, offset, saturation/windup), choose one targeted change tied to that failure mode, rerun, and re-verify. Avoid blind gain sweeps or repeated aggressiveness increases without new evidence.
- Use reruns to validate robustness, not to hunt for a lucky pass. If results vary materially across runs, report the variability and tune for consistent compliance under the original metric definitions instead of looping until one run passes.


- Robustness gate: if noise, fitted parameters, or closed-loop metrics vary materially across reruns, validate the candidate controller across several completed runs using the same fixed metric definitions and inspect each run's saved artifacts. Do not keep rerunning until one pass appears; only finalize when the implementation shows consistent compliance or when you can clearly report the remaining unstable metric.
- Preserve the staged pipeline unless the task explicitly requires otherwise: collect calibration data, fit the simplest adequate plant model, derive initial gains from that model, then validate on a full closed-loop run.
- Do not stop at theoretical gains. Always confirm performance with a completed closed-loop run and explicit saved metrics/artifacts from that run.



## Execution Discipline


- Before the first substantive action, restate internally the required tool/action format, exact allowed tool names, whether only one action is allowed per turn, and the exact completion token; then use only that protocol for the whole task.
- In strict action-schema environments, every tool use must be emitted exactly in the required wrapper/schema. Do not switch to alternate tool-call formats, invented tool names, XML/markdown wrappers, or prose descriptions in place of the mandated schema.
- Emit at most one tool action per assistant turn unless the environment explicitly allows batching. After each action, wait for the observation before sending the next one.
- Use exact executable tool inputs. Shell actions must be real commands, Python actions must contain complete code, and file writes must contain the literal script/data to save; do not use English descriptions, plans, or summaries as commands.
- If a command fails because the interpreter/tool name is wrong or unavailable, correct the command and rerun; do not continue as though the intended program executed.
- Before editing code, inspect the exact source region, anchor the change to text you actually observed, and verify the applied diff afterward. Avoid vague find/replace anchors or placeholder strings that are not present in the file.
- After writing a script, verify the artifact itself before blaming control logic: inspect the file and, for Python, prefer a fast check such as `python -m py_compile <script>` or equivalent before full execution.
- If any verification output is truncated, incomplete, or elided, perform another read/check before making pass/fail claims.
- Never claim a tuning improvement or quote exact metric values unless the corresponding run's `metrics.json` was fully observed or the values were recomputed from the saved `control_log.json` in a visible verification step.
- Treat verification and completion as separate steps: first confirm artifacts and metrics, then perform the environment's exact final completion action. If a single terminating string is required, emit exactly that string and nothing else.
- Once success criteria are verified, do not take any additional tool actions unless they are explicitly required for task completion.
- Treat post-verification cleanup as prohibited by default. Never delete or overwrite scripts or generated artifacts after validation unless the task explicitly asks for cleanup or replacement.

## Execution Discipline

- Follow any task- or environment-specific execution instructions exactly. If a strict tool/action schema, command wrapper, response format, or exact completion token is required, use it verbatim.
- Do not substitute alternate tool syntaxes, wrappers, or informal prose actions when a strict protocol is specified.
- After each action, wait for the observation/result before issuing the next action when the environment requires turn-by-turn interaction.
- Treat interface and completion requirements as part of task success. When the required output files are complete, stop and emit the exact mandated completion string if one is specified.
- Do not declare success or failure from partial/truncated stdout, file existence alone, or intermediate artifacts. First confirm the run completed, then inspect the generated JSON outputs.
- Preserve the original metric definitions from the task statement. Do not change settling bands, smoothing, overshoot calculation, or other pass/fail logic just to make results look acceptable unless explicitly authorized.
- Do not delete scripts, logs, or generated artifacts unless the task explicitly requests cleanup.
- If task/environment instructions conflict with this skill's generic guidance, obey the task/environment instructions.
## Model

First-order thermal system:
- K: system gain
- tau: time constant
- u: heater power (0-100%)

## Output Files

- `calibration_log.json`: Phase, heater power test, data array
- `estimated_params.json`: K, tau, r_squared, fitting_error
- `tuned_gains.json`: Kp, Ki, Kd, lambda
- `control_log.json`: Phase, setpoint, data array
- `metrics.json`: rise_time, overshoot, settling_time, steady_state_error, max_temp


- Treat these saved files as the authoritative handoff between phases: write them at each stage, then read them back before deciding the next action or making any final claim.
- Prefer generating `metrics.json` in the same end-to-end control script that writes `control_log.json`, so the reported metrics are computed directly from the saved trajectory of that exact run.
- Verify artifact completeness and coverage, not just existence: confirm required keys are present and that calibration/control logs span the intended runtime with plausible sample counts or timestamps consistent with simulator timestep and duration requirements before declaring success.
- Final verification pattern: read the latest saved artifacts directly, compare each metric to the stated thresholds one by one, and only then decide whether the task is complete.
- Treat artifact validation as part of success: verify the JSON files exist, are complete, internally consistent, and correspond to the same latest completed run before claiming the controller meets requirements.


- Before any final summary, read `estimated_params.json`, `tuned_gains.json`, `control_log.json`, and `metrics.json` directly. Do not rely on file existence, partial output, or expected code paths.
- Only state requirement pass/fail after inspecting `metrics.json` values; if output is incomplete or metrics are missing, report that verification is incomplete instead of assuming success.

- Verify artifact structure as well as control performance: confirm calibration/control logs cover the required duration and contain enough data points, not just that `metrics.json` looks acceptable.

- Check that log coverage matches the actual runtime configuration you inspected earlier (for example timestep × samples ≈ required duration) before treating the artifacts as complete.

- Compute `metrics.json` directly from the same saved closed-loop trajectory written to `control_log.json` so reported metrics and evidence stay consistent.
- If `metrics.json` passes but log duration, sample count, or required fields are missing/incomplete, treat the task as not yet complete and rerun/fix the pipeline.

## Tips

- Use scipy.optimize for curve fitting
- Ziegler-Nichols or model-based tuning for PID

- Default to model-first tuning: collect one clean open-loop step response, fit a first-order model, then compute initial gains from a standard IMC/model-based rule before hand-tuning.

- Prefer a clean excitation run before any closed-loop tuning guesses: one fixed-power step with enough duration and samples is usually sufficient to estimate a useful first-order thermal model for PI initialization.

- For first-order thermal plants, IMC-style PI tuning is often enough; if the response is stable but settling is too slow, reduce `lambda` stepwise and rerun verification while keeping overshoot acceptable.
- Prefer PI over PID when measurement noise is noticeable; add derivative only if it clearly improves verified metrics.

- Anti-windup for integral term; when clamping heater power to [0, 100], prefer back-calculation or equivalent integral correction so saturation does not cause slow recovery or overshoot.
- Clamp heater power to [0, 100]

- Include explicit heater saturation/safety handling, and add a hard over-temperature safeguard or power reduction near the max-temperature limit instead of relying on tuning alone to satisfy the safety bound.
- Add practical robustness by default when noise matters: use light controller-side measurement filtering if needed and document it, but do not widen acceptance bands or redefine the metrics unless the task explicitly authorizes that change.



- Treat all listed targets as mandatory pass/fail gates, not advisory goals.
- Base tuning changes on verified artifact contents, not partial console output or guessed failures.
- If a run appears truncated, verify completion and inspect artifacts before interpreting results.
- Freeze metric definitions early; tune the controller, not the scoring rule.
- Treat `metrics.json` as a summary, not proof: if results look unexpected or metric code changed, verify against raw `control_log.json` data.
- If noise makes settling behavior hard to interpret, first verify the task's metric definition and compare `metrics.json` against raw `control_log.json`. Reduce noise sensitivity with controller-side measurement filtering and document it; do not widen acceptance bands or redefine settling unless the task explicitly authorizes that change.

- If raw trajectory and evaluator disagree, inspect the metric code and simulator/config together before retuning; fix a true spec mismatch, but keep the task's original acceptance logic unchanged.

- If a proposed model-estimation fix barely changes fitted `K`/`tau` or closed-loop behavior, shift focus to controller design rather than repeating the same estimation idea.
- Before finishing, check whether the task requires a specific final-output token or action format.


- For simple HVAC thermal plants, a step-test → first-order fit → IMC PI workflow is a reliable default and usually better than ad hoc gain sweeping.

- When simulator/source inspection already confirms a first-order thermal process, use that known structure directly instead of inventing a higher-order model; spend effort on validated tuning, saturation handling, and anti-windup rather than unnecessary model complexity.
- A single aggressiveness adjustment after model-based tuning is often enough: if the verified response is stable but too slow, reduce `lambda` before trying broader controller redesign.

- Use a conservative `lambda` first to limit overshoot and oscillation, then retune from verified closed-loop results.
- In validation runs, clip heater output to `[0, 100]` and use saturation-aware anti-windup by preventing the integral term from accumulating further in the direction that would drive more saturation.
- If settling time fails under the stated definition, do not widen the settling band, add smoothing to the acceptance metric, or otherwise relax the evaluator to force a pass; improve the closed-loop response instead.
- When command output is truncated, prefer `metrics.json` plus spot-checks of `control_log.json` over narrative guesses about performance.
- Use `control_log.json` as the source of truth for debugging: confirm whether the trajectory actually enters and stays in the required band before concluding that tuning helped.
- If the identified first-order plant yields a stable IMC/PI design that is simply too slow, reduce the IMC closed-loop time constant (`lambda` or equivalent) before switching controller structure or sweeping gains blindly.
- If initial PI/PID tuning is fast enough but overshoot is the main failing metric, reduce aggressiveness before redesigning everything: lower `Kp`/`Ki`, limit or pause integration near the setpoint, and consider softer output limiting as temperature approaches the target.
- If a simple first-order fit already gives stable usable `K`/`tau`, do not overcomplicate the plant model; shift effort to controller design if repeated estimation tweaks barely change closed-loop behavior.
- If the task mandates an exact final token such as `ACTION: TASK_COMPLETE`, output that exact string and nothing else as the terminating action.


- Before the final response, do a last-pass checklist: latest control run completed, latest evaluation completed after that run, `metrics.json` was reread, and every required target passes on that latest evaluation.
- If you just changed gains, filtering, anti-windup, duration, or evaluation code, the previous metrics are stale; rerun evaluation and discard earlier metric claims.
- If parameter estimates or closed-loop metrics vary substantially across reruns, reduce estimator/controller sensitivity and check consistency across several runs; a single lucky pass is not sufficient evidence of task completion.
- Before changing metric code, first prove the existing evaluator is actually inconsistent with the written task definition by comparing it against the saved `control_log.json` trajectory from a completed run.


- Preserve a staged workflow even when using one entry-point script: write each intermediate JSON artifact so you can inspect calibration, estimation, tuning, and final evaluation separately.
- Before retuning from a surprising result, confirm the evaluator is using the task/config-specified metric parameters taken from the current task files, not hard-coded defaults.


