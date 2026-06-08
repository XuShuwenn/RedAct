---
name: simpo-code-reproduction
description: "Implement SimPO loss function for language model alignment based on paper specifications and generate loss matrix."
---

# SimPO Loss Implementation

## When to Use

- Implement SimPO loss for model alignment
- Reproduce code from NLP papers
- Generate loss matrices for evaluation

## Input

- Paper: `/root/SimPO/paper.pdf`
- Template: `/root/SimPO/scripts/simpo_trainer.py`

## Task

1. Read SimPO paper to understand loss formula
0. Before any repository work, extract and follow the runtime's exact interaction/tool protocol from the active instructions: allowed tool names, required action syntax/schema, waiting rules, and any exact completion token. Use only that allowed format throughout; do not invent alternate tool calls or unsupported action schemas.
0.i. Treat protocol compliance as a blocking precondition: before the first command, confirm the exact allowed tool name(s), action schema, waiting/observation rules, whether free-form assistant text is allowed between actions, and any exact final completion token from the runtime instructions, then use only that interface and format for the rest of the task.
0.ii. Never mix in habitual tool syntaxes from other runtimes. If the runtime requires a specific `Thought`/`Action` wrapper or JSON-under-`Action:` pattern, use that exact pattern on every tool step; do not switch to XML-style tags, ad hoc tool names, markdown pseudo-tools, or prose pretending to be an action.
0.iii. If any repository read is truncated before showing the full `def simpo_loss` body or the full unit test assertions, immediately continue with targeted range reads or literal grep/sed commands until the missing lines are visible; do not switch to paper-only reasoning or environment setup first.
0.iv. Minimality gate: do not begin package installation, interpreter changes, or environment creation until you have identified the exact `simpo_loss` edit and have attempted the provided direct unit test once from the existing environment or the minimal repo-root/PYTHONPATH context.
0a. Before any setup or installs, locate the real `simpo_loss` implementation site and read the full target function, nearby helper logic, config usage, and the complete unit test with additional targeted reads if any output is truncated.
0b. Do not start with environment recreation, broad dependency installation, or package upgrades while the exact missing code change or concrete test blocker is still unidentified.
1a. Before editing `simpo_loss`, inspect the surrounding `SimPOTrainer` code in `/root/SimPO/scripts/simpo_trainer.py`, relevant call sites/config such as `/root/SimPO/scripts/simpo_config.py`, and the full unit test in `/root/SimPO/unit_test/unit_test_1.py` so the implementation matches this repository's actual interface, tensor semantics, and expected outputs.
1a.v. Inspect the concrete consumer path for `simpo_loss` (for example `get_batch_loss_metrics` and the immediate call site) to confirm how the returned loss/reward tensors are used, reduced, detached, and named before implementing or changing return values.
1a.i. Read the full current `simpo_loss` method body itself, not just search hits or truncated snippets, plus enough nearby helper logic to understand its inputs, returned values, class attributes, and any alternate branches before making any edit.
1a.ii. While inspecting, identify repository-specific fields, helpers, and branches that affect loss behavior (for example `get_batch_logps`, `get_batch_loss_metrics`, `beta`, `gamma_beta_ratio`, `loss_type`, `label_smoothing`, reward/logit conventions, return shapes, and detached metrics) and implement against those concrete expectations.
1a.ii.a. Inspect how `SimPOTrainer` initializes and stores the values used by `simpo_loss`, and read from trainer instance attributes that are actually assigned on the runtime object used by the test path; do not assume a config object or inherited field is available unless local code shows it is.
1a.ii.b. If this repository or an installed dependency has a nearby analogous preference-loss method (for example `cpo_loss`, DPO-style loss, or another trainer helper), inspect it only after reading the local trainer/config/test files and use it only as a structural template for score-gap construction, scaling or margin placement, return tuple shape, detached reward metrics, and tensor-handling conventions. Keep this repository's concrete `simpo_loss` inputs, config fields, call sites, outputs, and the paper objective authoritative.
1a.iii. Determine from the repo/test whether inputs like `policy_chosen_logps` and `policy_rejected_logps` are raw sequence log-prob sums, already sequence-aggregated values, or length-normalized average log probabilities; if they are already averaged/normalized, do not divide by sequence length again when applying the SimPO formula.
1a.iv. If any file or PDF view is truncated, continue reading targeted ranges until you have the complete `simpo_loss` body, nearby helper/config logic, and the full unit test assertions before coding.
1b. Use the paper to confirm the loss formula, but validate assumptions against repository code; do not implement from partial snippets, summaries, or guessed normalization/scaling behavior.
1c. Explicitly map paper variables onto this repository's existing quantities before coding so you do not reapply normalization or mis-scale beta/gamma terms; if the paper uses a parameter not stored directly, derive it from existing config fields used by this codebase (for example, the effective `gamma` from `beta * gamma_beta_ratio` when applicable).
1c.i. Reconstruct the intended objective by triangulating all three sources together: the paper's SimPO formula, the trainer's current call/return conventions, and repository config fields such as `gamma_beta_ratio`, `beta`, `loss_type`, and `label_smoothing`. Prefer this repo-specific mapping over a paper-only rewrite.
1d. Do not code from unreadable or partial paper extraction output. If the formula is not directly visible from a trustworthy paper excerpt, keep reading targeted paper/code/test sections until you can confirm the exact formula and map each term to local variables.
1d.i. A binary/open failure is not paper evidence. If `/root/SimPO/paper.pdf` is not yet readable as text, use a lightweight extraction/view method and confirm the specific SimPO objective text before claiming the implementation is paper-based.
1d.iii. If readable paper text still cannot be obtained after targeted extraction attempts, stop claiming the implementation is confirmed from the paper; implement from repository code/tests and describe the paper as unverified rather than guessed.
1d.ii. If the paper remains inaccessible after reasonable targeted attempts, rely on repository code/tests for implementation details and explicitly use the paper only after obtaining readable formula content.
1e. Before editing `simpo_loss`, verify from the paper and local code/test together how `beta`, `gamma_beta_ratio`, `loss_type`, and `label_smoothing` are used, what tensors the function must return, and whether nearby reward/log-prob, reduction, or normalization branches affect the implementation.
1f. Do not edit until you have direct evidence from the repository: read the full current `simpo_loss` body from `def simpo_loss` through its final return, plus enough surrounding lines to see helper usage and all branches. A signature, docstring, grep hit, header-only view, or truncated snippet is not sufficient.
1g. Before coding, inspect the full `unit_test_1.py` and identify exactly how test tensors/artifacts are loaded and what outputs are asserted. If provided artifacts are relevant, inspect them using the same library/mechanism the test uses rather than guessing their format.
1g.i. If the test uses `torch.load`, NumPy, or another loader for fixtures/artifacts, inspect those files with that same mechanism in a working interpreter before relying on them. Do not infer tensor contents from filenames or proceed after a failed load attempt.
1h. Treat full inspection as a gate: before any package install, interpreter switch, or environment creation, finish reading the full current `simpo_loss` body, enough surrounding trainer/config code to identify its real inputs/outputs, and the complete `unit_test_1.py` assertions.
1h.i. Pre-edit gate checklist: confirm you have visibly read (a) `def simpo_loss` through its final return, (b) nearby helper/config lines that define the tensors/attributes it uses, and (c) the full unit test assertions. If any one of these is still unread or truncated, do not edit yet.
1h.ii. Before any setup step, be able to state from direct local evidence the exact file/function to edit, the expected returned tensors/metrics, and what the unit test asserts.
1h.iii. Define a hard sufficiency threshold for action: once you have the full `simpo_loss` body, the relevant helper/config/test evidence for tensor semantics and expected returns, and a readable paper-to-repo variable mapping, stop investigating and edit `simpo_trainer.py` in the same work cycle.
1h.iv. Do not continue into dependency setup, upstream-library comparison, or extra paper extraction after crossing that threshold unless the immediate next step is blocked by a concrete traceback from the real required test.
1i. When using shell/search tools, issue only executable commands and literal search patterns. Do not type intentions like `inspect local paper content` or vague grep patterns like `loss-related terms`; instead use concrete commands such as `ls`, `sed -n '1,240p' ...`, `grep -n "simpo_loss\|gamma_beta_ratio\|label_smoothing" ...`, or a small Python snippet that actually reads the target file/PDF.
1i.i. Before sending any shell/search action, translate the intent into a command another engineer could paste and run unchanged. If the command contains prose instead of an executable program and literal arguments, rewrite it before executing.
1i.ii. For search, use exact symbols, filenames, or repository terms already observed in local files/tests; avoid generic patterns like `loss-related`, `relevant code`, or other summary phrases that are not literal source text.
2. Implement `simpo_loss` function in `SimPOTrainer` class
2a. Reopen the exact `simpo_loss` region in `/root/SimPO/scripts/simpo_trainer.py` and patch only that real function body; do not use blind/global replacement or edits based on task text, summaries, or guessed snippets.
2a.i. Before any edit, capture the exact existing lines you will replace from the live file. Do not use placeholder descriptions or guessed snippets as the edit target; anchor the change to verified source text from the actual `simpo_loss` body and nearby context.
2a.i.a. Make the edit auditable in the trajectory: show the real pre-edit `simpo_loss` lines, apply the concrete replacement against that verified text, then read back the edited region so the exact implementation is visible rather than described abstractly as a placeholder swap.
2a.i.b. Never target an edit with conceptual placeholders such as `existing placeholder return block`, `loss stub`, or a guessed summary. Use exact text read from the live file as the replacement anchor, and if the view was truncated, read additional ranges until the full target block is visible.
2a.ii. Keep source edits tightly scoped to the requested implementation. Do not modify unrelated imports, fallback helpers, compatibility shims, tests, or other trainer logic just to work around environment issues unless a concrete traceback proves another minimal code change is strictly required.
2a.iii. If execution fails before reaching `simpo_loss`, prefer non-source fixes first: run from the correct repo root, set `PYTHONPATH`, use the matching interpreter, or install only the specific missing dependency shown by the traceback.
2b. Immediately after editing, re-read the modified function to confirm the change landed in the intended region, then run a lightweight file-level validation such as `python -m py_compile /root/SimPO/scripts/simpo_trainer.py` or an equivalent minimal import check before the full unit test.
2b.i. Verification is mandatory: read back the edited `simpo_loss` lines themselves and confirm the expected math and returns are present before doing environment work, installs, or full test execution.
2c. Do not assume the patch landed correctly from the edit command alone. Read back the full edited `simpo_loss` region (not just a header or short snippet) and confirm the intended final code is present before testing.
2c.i. Verify with direct evidence before moving on: the trajectory should show the edited math/returns in the read-back of `simpo_loss`, not merely a successful edit command or a view of the method signature/docstring.
2c.ii. After reading back the edited region, run the designated unit test next. Do not pivot into broad environment recreation, dependency sweeps, package logging, or unrelated setup unless that test or a minimal import needed for it produces a concrete traceback.
2d. Do not let investigation exceed the point of sufficiency: once you have (a) the full current `simpo_loss` body, (b) the relevant helper/config/test evidence for tensor semantics and expected outputs, and (c) the paper formula mapping, stop researching and edit `simpo_trainer.py` immediately.
2e. Prioritize the direct repository change: inspect local source/config/test files, patch `simpo_loss`, and attempt the provided unit test before any broad environment reconstruction. Do not spend the session creating new environments, installing environment managers, or installing large ML stacks unless a concrete traceback from the real test shows that a specific package/version is required.
2f. If you have already read the full local function, relevant config/helpers, and the complete test, the next step is to edit `/root/SimPO/scripts/simpo_trainer.py` directly. Do not detour into environment-manager setup, interpreter replacement, virtualenv creation, large dependency installs, or external reference comparisons before making that minimal local patch.
2g. Treat optional comparison/reference inspections as nonblocking. If paper extraction, an external import, a parent-trainer lookup, a helper script, or other auxiliary check fails, immediately fall back to the local repository files already identified (`simpo_trainer.py`, `simpo_config.py`, `unit_test_1.py`, paper) and continue to the edit plus real unit-test run.
2h. If the direct test path is blocked by concrete, repeated dependency/import failures that cannot be resolved with repo-root execution, `PYTHONPATH`, or one-package fixes, use a clean minimal environment as a fallback for only the required test path. Install only the packages needed for `unit_test_1.py`, prefer repository-pinned versions where available, and skip optional/incompatible extras that are not required by the test.
3. Run unit test to verify implementation
3a. Treat observed execution of `python /root/SimPO/unit_test/unit_test_1.py` as mandatory evidence, not an intention. Do not conclude the task after editing or environment setup unless this script has actually been run and its result inspected.
3b. If the first run fails with `ModuleNotFoundError: No module named 'scripts'` or a similar repo-local import error, treat it as an execution-context issue first: rerun from the repo root with the repo root on `PYTHONPATH`, e.g. `cd /root/SimPO && PYTHONPATH=/root/SimPO python /root/SimPO/unit_test/unit_test_1.py`, then inspect the new result before installing anything.
3c. Do not stop after proposing a rerun command. Execute it, wait for the full traceback or pass result, and continue until there is explicit validation or a new concrete blocker.
3d. A custom script, manual loss calculation, import-only check, or self-written verification summary does not substitute for the required repository test.
4. Save loss to `/root/loss.npz` with key 'losses'
5. Follow the critical path: inspect code/test/paper context -> implement only the minimal change needed in `simpo_loss` -> run the provided unit test -> save `/root/loss.npz` with key `losses` -> write `/root/python_info.txt`.
6. Before finalizing, verify correctness against both the paper formula and the local trainer/test conventions, not just a passing test.

7. Use this execution order unless a concrete traceback forces otherwise: inspect full trainer/config/test and readable paper context -> implement only the minimal `simpo_loss` change -> run `python /root/SimPO/unit_test/unit_test_1.py` -> save `/root/loss.npz` with key `losses` -> write `/root/python_info.txt` -> verify both files.
8. If the unit test initially fails, capture the complete traceback before any install/upgrade, make only the smallest evidence-based environment or execution-context fix, then rerun the same real test immediately.
8a. Treat partial or truncated tracebacks as insufficient evidence. Re-run in a way that shows the exact exception or isolate the failing import first; do not install or upgrade packages until the concrete missing module, symbol, or version incompatibility is identified.
8a.i. If the traceback output is clipped, rerun with a command that preserves the full error text or reproduce the smallest failing import under the same interpreter before deciding on any dependency change.
8a.ii. On the first failed test run, stay in diagnosis mode: inspect the full traceback and the failing test/import lines, then choose the smallest fix supported by that evidence. Do not pivot to creating a new environment, installing environment managers, or broad dependency sets until a specific blocker has been confirmed.
8a.iii. Do not change multiple interdependent ML packages in one step. Make one evidence-backed fix at a time, prefer repository-declared/pinned versions, and rerun the real unit test immediately after each change to detect newly introduced conflicts.
8b. Prefer the minimal execution fix order: verify `python`/`python3` availability, inspect repo dependency files and test imports, try the direct script, then fix repo-root / `PYTHONPATH` / working-directory issues before any package install or new environment.
8b.i. If the direct test fails with a repo-local import error (for example missing `scripts`), immediately rerun the exact required script from the repository root with the repo on `PYTHONPATH`, e.g. `cd /root/SimPO && PYTHONPATH=/root/SimPO python /root/SimPO/unit_test/unit_test_1.py`; do not patch imports or restructure the repo to work around module-path issues.
8b.ii. If repository metadata such as `environment.yml`, `requirements.txt`, or `pyproject.toml` declares a specific Python version or constrained dependency set and the active interpreter clearly differs, treat matching that declared runtime as the next minimal fix after repo-root/`PYTHONPATH` checks, before broader debugging or speculative package changes.
8b.iii. If import errors persist after the path/runtime checks, inspect the full traceback and install only the exact missing package or transitive dependency named there, then rerun the same direct unit test immediately.
8b.iv. Use the same interpreter consistently for installs, test runs, `/root/loss.npz`, and `/root/python_info.txt`.
8c. If the repository declares pinned or expected dependency versions, prefer those exact versions over broad unpinned installs; avoid upgrading core ML stacks speculatively.
8c.i. Before installing or upgrading any dependency, inspect both the repository dependency files and the actual import sites that are currently failing so you can match the expected API layout/version.
8c.ii. If `environment.yml` or similar metadata exists, use the full declared specification as the source of truth; do not base environment recreation on only one subsection such as a `pip:` block unless the rest is confirmed irrelevant.
8c.iii. Avoid broad replacement installs of core ML packages with latest versions. If manual installation is unavoidable, choose the minimal compatible version set justified by the repository files and traceback evidence.
8c.iv. If a package imports but the traceback shows missing symbols or API drift, inspect the repository's expected version and install that compatible version explicitly rather than assuming the newest release matches this codebase.
8d. After each concrete environment or execution-context fix, rerun `python /root/SimPO/unit_test/unit_test_1.py` immediately before doing anything else.
8d.i. When creating a fallback environment, keep dependency scope minimal: start from the unit test imports and traceback, install the smallest compatible set, and avoid insisting on full project or optional dependency parity if the required direct script can run without it.
8e. If an optional reference step fails (for example, importing an external trainer for comparison, using a helper inspection script, or reading nonlocal reference code), treat it as nonblocking. Fall back to local repository files (`simpo_trainer.py`, config, tests, paper) and keep progressing to the edit and real unit test.
8f. Do not start long-running or background setup jobs that you will not immediately monitor to completion. Finish the foreground edit -> traceback-guided fix -> rerun loop; do not leave the task suspended in installs or environment creation.
8g. After any setup command that creates or changes a prerequisite (for example `python -m venv`, package install, interpreter selection, working-directory change, or `PYTHONPATH` adjustment), verify that step succeeded before issuing any dependent command. If it failed, stop using that path/environment immediately and choose a different evidence-based fix.
9. Use a hard completion checklist before stopping: direct inspection completed, `simpo_loss` edited and read back, the provided unit test run successfully, `/root/loss.npz` saved with key `losses`, `/root/python_info.txt` updated after any package changes, and if the runtime requires a specific action schema or completion token, follow it exactly and finish with that exact completion signal.
9a. Final-response gate: if a required completion string exists, do not write a summary, explanation, or status line. Output exactly that required string and nothing else.
9b. Evidence gate: do not mark the task complete unless you have directly re-opened the edited `simpo_loss` code from disk after the patch and confirmed the intended math/return logic is actually present.
10. Before the final response, perform a protocol check: if an exact completion string is required, emit exactly that string and nothing else. Do not substitute a narrative summary, and do not append extra text after the required token.
10a. Final-step guard: immediately before replying, re-check the active instructions for an exact completion marker. If one exists, the final message must be exactly that marker with no summary, no code fence, no bullet, and no trailing text.
10b. If the runtime also required a specific action syntax during execution, verify the trajectory used only that syntax before finalizing; protocol compliance is part of task completion, not an optional formatting detail.

- Environment setup for SimPO project
- Prefer the existing project environment and the smallest runnable setup that can execute the provided unit test; avoid broad or speculative dependency changes unless a concrete traceback shows they are necessary.
- Check repository environment metadata first (for example `environment.yml`, `requirements.txt`, `pyproject.toml`, or similar). If it declares a specific Python version or core package set and the current runtime differs, prefer matching that before speculative debugging.
- Before installing anything, establish a usable interpreter/package path: confirm whether `python` or `python3` exists, verify `-m pip` works for that same interpreter, and use one working interpreter consistently for installs, test runs, and `python_info.txt`.
- Before treating failures as code bugs, verify the execution context for the test and prefer import-path fixes such as running with the repo root on `PYTHONPATH` when repo-local modules like `scripts.*` are not found.
- Do not create a fresh environment or install large dependency sets preemptively. First attempt the minimal repo/unit-test path, then fix only the specific missing import, execution-context issue, or version incompatibility shown by an actual traceback.
- Inspect test/import requirements and repository dependency/config files before installing packages, and prefer pinned or repository-expected versions over latest-package installs.
- Do not upgrade/install broad core stacks speculatively (for example `torch`, `transformers`, `trl`, `accelerate`, `datasets`) unless a concrete traceback shows they are required and the chosen versions match repository expectations.
- After each install step, immediately verify the previously missing import or rerun the target unit test to confirm progress before installing anything else.
- If the current interpreter truly cannot run the needed imports or is externally managed, create a clean compatible environment only for the required test path, then install just the minimal dependencies indicated by concrete tracebacks.
- Log Python version and packages to `/root/python_info.txt` using the exact commands `python -VV` and `python -m pip freeze`.
- If you install or upgrade any package after creating `/root/python_info.txt`, rerun both commands and rewrite the file so it reflects the final environment used for the passing test.
- Do not treat implementation as complete until the real script `python /root/SimPO/unit_test/unit_test_1.py` has run successfully in the final environment.## Requirements

- Environment setup for SimPO project
- Prefer the existing project environment and the smallest runnable setup that can execute the provided unit test; avoid broad or speculative dependency changes unless a concrete traceback shows they are necessary.
- Inspect test/import requirements before installing packages, and verify imports after each install step.
- Log Python version and packages to `/root/python_info.txt` using the exact commands `python -VV` and `python -m pip freeze`.
- If you install or upgrade any package after creating `/root/python_info.txt`, rerun both commands and rewrite the file so it reflects the final environment used for the passing test.

1j. Use the unit test, fixture tensors/artifacts, and `simpo_config.py` to bound the implementation before coding: identify the exact `simpo_loss` inputs, asserted outputs, and trainer parameters the test actually exercises so you can make the smallest correct change.

## Output

- `/root/loss.npz`: Loss matrix with key 'losses'
- `/root/python_info.txt`: Environment info


- Before finishing, verify both required files exist and that `/root/loss.npz` contains key `losses`.

- Final checklist before ending: the provided unit test passes, `/root/loss.npz` exists and contains key `losses`, `/root/python_info.txt` reflects the final environment actually used for the passing run, and any explicitly required completion token/protocol has been emitted exactly.

- Run `/root/SimPO/unit_test/unit_test_1.py`
- Fixed input tensors provided
- Output should match expected loss values
- Read the full test file before coding to determine expected outputs, tensor semantics, and minimal dependencies.
- Before any environment changes, finish reading the full test file and the full target function context so you know which imports and behaviors are actually required.
- First try: `python /root/SimPO/unit_test/unit_test_1.py`.
- If direct execution fails with a repository import error such as missing `scripts`, rerun without editing tests from an import-safe context with the repo root on `PYTHONPATH`, for example `cd /root/SimPO && PYTHONPATH=/root/SimPO python /root/SimPO/unit_test/unit_test_1.py`.
- After fixing that import-path issue, rerun the same direct script immediately and continue from the new result; do not stop after proposing the fix.
- Do not substitute `pytest`, import-only checks, or manual loss computation for the required direct script execution.
- If a test/import failure occurs, capture or rerun it in a way that preserves the full traceback before installing or upgrading anything, then fix only the concrete blocker and rerun the same direct unit test immediately.
- After any environment change, rerun the provided script immediately to confirm the blocker is cleared.
- Treat a passing `unit_test_1.py` result as necessary but not sufficient; also confirm the implementation matches the paper and local trainer conventions for scaling, beta/gamma handling, normalization assumptions, and outputs.
- If the test still cannot run, keep the task incomplete rather than fabricating `/root/loss.npz` from an alternate code path.## Unit Test

- Run `/root/SimPO/unit_test/unit_test_1.py`
- Fixed input tensors provided
- Output should match expected loss values


- Read the test file before coding to determine expected outputs, tensor semantics, and minimal dependencies.
- Run the script directly: `python /root/SimPO/unit_test/unit_test_1.py`.
- Treat a passing `unit_test_1.py` result as necessary but not sufficient; also confirm the implementation matches the paper and local trainer conventions for scaling, beta/gamma handling, normalization assumptions, and outputs.
- If the test or imports fail, capture the full traceback first and identify the exact missing module or incompatibility before changing packages or the environment.


- Read repository code and tests before inferring behavior from the paper; use the paper to confirm formulas, not to replace the repository's implementation contract.
- Treat readable evidence as a gate: before editing, inspect the full `simpo_loss` body, nearby helpers, call sites, config usage, and the complete unit test so assumptions about averaging, normalization, beta/gamma, loss branches, detached metrics, and return values come from local code evidence.
- Constrain the implementation with nearby helpers, concrete trainer attributes, and supported branches before coding; preserve local conventions for outputs and returned values rather than only the bare paper equation.
- Do not write or replace the core SimPO math from personal deduction when the source formula is still unverified; if paper access is incomplete, keep investigating targeted paper/code/test sections rather than guessing.
- Keep source edits tightly scoped to `simpo_loss`; do not patch unrelated trainer/import compatibility code or fallback helpers unless the traceback proves another repository file must change for this task.
- After every code edit, read back the affected function or surrounding lines to confirm the replacement landed correctly before executing the test.
- Run only the minimal commands needed to execute the provided unit test; prefer the existing interpreter/environment, and do not create a new environment or install broad dependency sets unless a concrete traceback shows the exact missing requirement.
- When a test fails before reaching `simpo_loss`, fix module resolution or runtime context first, then rerun the real unit test before changing the implementation further.
- If environment issues block testing, capture the full traceback first, fix only the specific missing module, symbol, version incompatibility, or execution context it identifies, verify the affected import if needed, then rerun `python /root/SimPO/unit_test/unit_test_1.py` immediately.
- Do not let environment setup or optional PDF/reference-code investigation block the core path: once the local interface is clear enough, make the minimal `simpo_loss` edit and attempt the real unit test as early as possible.
- Do not treat dependency installation, import success, a code patch, or even a passing `unit_test_1.py` run as sufficient by itself. Finish only after re-checking `simpo_loss` against paper details and local trainer/config/test semantics, creating `/root/loss.npz` with key `losses`, writing `/root/python_info.txt` with the exact required commands, verifying both required files, and obeying any required runtime completion protocol literally.## Workflow Guardrails

## Workflow Guardrails

- Read repository code and tests before inferring behavior from the paper; use the paper to confirm formulas, not to replace the repository's implementation contract.
- Run only the minimal commands needed to execute the provided unit test; avoid broad setup/reinstall detours unless clearly required.
- If environment issues block testing, resolve them from concrete evidence, then rerun the real unit test immediately.
- When package incompatibility is the concrete blocker, prefer matching the repository's expected Python/library versions over broad latest-version installs; use version changes only when justified by the traceback or repo metadata.
- Do not stop after patching: complete the test run and produce both `/root/loss.npz` and `/root/python_info.txt`.

- Before any package install, environment creation, or OS-level setup, confirm you have already read the full target function and full unit test and identified the smallest plausible `simpo_loss` change.
- Start with the task-critical path, not environment exploration: inspect the full `simpo_loss` body, inspect the full unit test, then attempt the direct required test command before broad setup checks.
- Do not spend early steps on generic machine probing such as GPU checks, memory inspection, conda discovery, or package inventory unless a concrete traceback later makes one of those facts necessary to unblock the required direct test.
- Treat truncated reads as incomplete evidence. If a file view cuts off the target function, helper logic, config, or assertions, continue reading targeted ranges until the full relevant code is visible before editing.
- If you cannot point to the exact live `simpo_loss` lines that need replacement, you are not ready for installs or broader debugging; continue targeted file inspection first.
- Before reading environment metadata or attempting installs, name the concrete target in your own working state: the exact file/function to edit and the exact test/script to run. If you cannot name both yet, keep inspecting repository files instead of doing setup.
- When early execution fails, prefer the lightest next step that preserves forward progress on the repository task: repo-root execution, `PYTHONPATH`, or an alternate existing interpreter. Only install a package after the failing import/module is explicitly identified from the traceback.
- Anti-stall rule: if you have enough repository evidence to implement `simpo_loss`, switch from reading to editing. Do not continue gathering context once the missing step is simply to patch the function.
- Escalation rule: once the function/test interface is clear, the only justified reason not to edit `simpo_loss` next is a concrete blocker from the active runtime or a real traceback from the required unit test. Missing PDF tools, unavailable optional utilities, or failed comparison lookups are not blockers.
- Treat `no code edit yet` as a warning state. If you have already read `simpo_trainer.py`, `simpo_config.py`, and `unit_test_1.py`, the next steps should be patch -> read back -> run the direct unit test, not more setup churn.
- Keep edits transparent in the trajectory: show the target function context before editing and read back the edited region after editing so the implementation can be audited.
- Scope edits strictly to the requested implementation unless a concrete traceback proves another minimal repository change is unavoidable. Do not add broad compatibility shims, import rewrites, or fallback helpers to `simpo_trainer.py` just because the environment differs; first solve execution-context issues outside the source file and rerun the real test.
- Evidence gate before patching: if you cannot show the full current `simpo_loss` body, nearby helper/config context, the complete unit test assertions, and when relevant how fixture files are actually loaded, you are not ready to edit yet.
- Evidence standard: base conclusions on direct command output from file reads, tracebacks, and the required unit test result. Do not treat agent-written summaries, reports, or checklists as proof that the repository path succeeded.
- Treat environment debugging as traceback-first: capture the full failing error or a minimal reproducer before any install, and avoid introducing new version conflicts by changing several core ML packages at once.
- When dependency metadata exists, inspect the complete environment declaration rather than extracting only a convenient subsection. Partial dependency reconstruction is a last resort and must still be validated against current import sites and pinned expectations.
- If a library symbol is imported from a specific module path in repository code, verify that the intended package version actually provides that symbol before installing or upgrading that library.
- If `python` is missing, prefer an existing compatible interpreter such as `python3` for inspection and the required script path; do not spend time changing system executables or creating a new environment until a concrete traceback shows the existing interpreters cannot run the minimal task path.
- When imports fail, prefer repo-root execution-context fixes and repository-declared dependency versions; avoid broad unpinned installs that can create API drift.
- Treat optional reference imports/lookups and PDF utilities as nice-to-have only. If they fail or are unavailable, continue by reading local files directly and proceed with the minimal implementation/test loop.
- Do not perform broad environment rebuilds or package-stack installs before editing `simpo_loss` and attempting the real test once; use concrete test tracebacks to justify each environment change.
- Do not stop after launching a rerun. Wait for the real unit test result, inspect whether it passed or failed, and continue until you have either a verified passing run plus required deliverables or a concrete blocking error.
- A rerun command is not evidence by itself. Observe the returned output from that specific rerun, then either proceed to deliverables on success or debug from the explicit failure shown.
- Anti-stall sequence after editing: read back `simpo_loss` -> run `python /root/SimPO/unit_test/unit_test_1.py` (or the same script from an import-safe repo-root context if needed) -> inspect the actual result -> only then make the smallest traceback-based environment fix if required.
- Never mark the task complete from a code patch alone or from environment progress alone. Completion requires evidence that the designated unit test actually ran, plus verified creation of `/root/loss.npz` with key `losses` and `/root/python_info.txt`.

- Do not let a failed optional paper/PDF extraction derail the task. If local source and the unit test already expose the needed interface and expected behavior, continue to the minimal `simpo_loss` edit and use the paper only as a targeted confirmation step.
- If repeated setup attempts are not advancing the code task, explicitly switch back to source inspection/editing instead of trying broader provisioning.
- Anti-drift rule: after a focused `simpo_loss` edit, spend the next steps on validation of that edit (`read back -> lightweight check -> direct unit test`). Do not pivot into long environment reconstruction unless the real test has produced a concrete traceback that requires it.
- Treat repeated bullets in this skill as one consolidated rule set, not separate tasks to re-execute. Follow the critical path/checklist once, avoid redundant rereads after you already have full function/test/paper evidence, and move directly from sufficient inspection to the minimal edit and real test run.
- When verifying `/root/loss.npz` or any other output, use the same interpreter/environment that produced the passing test run. Do not treat failures from a different interpreter missing `numpy` or other packages as evidence that the artifact itself is bad.
## Tips

- Read paper carefully for loss formula
- Don't modify unit_test.py
- Verify reproducibility

- Inspect the full target function body, nearby helpers, call sites, class attributes, and configurable loss branches before replacing the placeholder implementation.
- Do not assume quantities are already length-normalized, averaged, or otherwise transformed unless the repository code or test explicitly shows that.
- Translate the paper equation into the repository's score semantics before writing code; confirm whether values are already averaged, normalized, or margin-adjusted in surrounding code.
- Use `simpo_config.py` and `unit_test_1.py` to pin down which trainer attributes and defaults actually matter (`beta`, `gamma_beta_ratio`, `loss_type`, `label_smoothing`) before editing `simpo_loss`.
- Read local trainer/config/test files first, then extract only the specific SimPO objective details needed from the paper; do not replace the repository contract with a paper-only implementation.
- If you find a nearby implemented preference-loss method in this repo or its installed trainer dependencies, use it as a template for function structure, return shapes, and detached metrics so `simpo_loss` matches local conventions instead of only the paper equation.
- If `ModuleNotFoundError` shows a repo-local package such as `scripts`, first rerun with the repo root on `PYTHONPATH` rather than editing imports or installing unrelated packages.
- Reuse existing trainer/config attributes to express paper hyperparameters; do not invent new constants or config keys when the same quantity can be derived from current fields.
- If a file view or PDF extraction is truncated, continue reading targeted ranges until the needed code or formula is fully visible.
- Safe edit pattern: view the current `simpo_loss` code, patch only the identified lines, then view that region again to verify the final code matches what you intended.
- If shell PDF tools are unavailable, use a lightweight Python PDF reader only for extracting the relevant objective text rather than adding heavy document-processing dependencies.
- If the default Python environment is constrained, prefer a local virtual environment over system-level workarounds, and keep it minimal to the direct `unit_test_1.py` path.
- If repository dependency pins include an obvious platform-specific or optional blocker (for example a package like `flash-attn` for a CPU-only/unit-test task), skip or relax only that blocker when the traceback and repo imports show it is unnecessary for the required test.
- If the test fails on imports, fix the specific missing or incompatible package or execution context from the traceback rather than reinstalling the whole ML stack.
- Common low-cost recovery pattern: fix repo import resolution first (`cd /root/SimPO && PYTHONPATH=/root/SimPO ...`), then satisfy only the exact missing transitive package named by the traceback if one remains.
- If repo metadata points to a specific Python version, prefer that compatible interpreter first; then add only the exact missing package exposed by the next traceback and rerun the real unit test immediately.
- If an import error indicates package API drift (for example a `trl` symbol mismatch), prefer installing the repository-compatible version of that package before changing the `simpo_loss` implementation again.
- If you create `/root/python_info.txt` before the environment is final, rerun exactly `python -VV` and `python -m pip freeze` and rewrite the file after the passing test.
- Keep an explicit completion checklist and do not leave setup mode until each item is done: full target/test/paper inspected, `simpo_loss` implemented, unit test run successfully, `/root/loss.npz` saved with key `losses`, and `/root/python_info.txt` written.
- Treat `/root/loss.npz` and `/root/python_info.txt` as blocking deliverables; verify them at the end instead of assuming they were written.


## Execution Protocol and Scope Guardrails

- Hard rule: if the runtime specifies a single allowed tool/action format, use that exact format for every tool interaction from start to finish. Do not switch to alternate tool syntaxes mid-run or use any tool/interface not explicitly allowed by the runtime instructions.
- Before the final response, perform a literal protocol audit: confirm both (a) every prior tool call used the required schema and (b) the final turn matches the exact required completion token/string with no extra prose before or after it.
- Before using any shell pipeline or helper utility in a command, prefer simple broadly available commands first and avoid assuming optional tools/utilities exist. If a command fails because a utility is missing, simplify the command and continue toward the required inspection or test rather than detouring into broad setup.
- Do not pivot from an unread or unverified code change into environment setup. First read the exact target body, make the minimal edit, and read back the edited region; only then debug execution blockers shown by the real unit test.
- Do not create a new interpreter, venv, or large dependency stack while the only evidence is a repository path/import issue or a truncated third-party traceback. Fix repo-root execution context and obtain the full concrete error first.
- Hard stop rules:
  1. Do not edit `simpo_loss` until you have read the full current function body and the full unit test.
  2. Do not send non-shell placeholder text as a command.
  3. Do not use any tool/interface not explicitly allowed by the runtime instructions.
  4. Do not stop after patching; the task is incomplete until the real unit test has been run, required files verified, and the exact required completion token emitted if one exists.

## Execution Protocol and Scope Guardrails

- Follow the runtime's required action/tool schema exactly on every step. If the environment specifies a particular `Action:`/JSON format, tool-call syntax, or final completion token, use that exact format for every interaction and finish with the exact required completion signal.
- Use only the execution interface actually provided by the runtime/system for shell work. Do not invent alternate tool abstractions, editors, web fetchers, todo tools, or pseudo-tool syntaxes.
- Issue only executable shell commands. Do not send natural-language placeholders such as `extract paper text`, `inspect the file`, or `run the provided unit test`; instead send a real command like `sed -n '1,220p' ...`, `python ...`, `grep ...`, or `cd /root/SimPO && PYTHONPATH=/root/SimPO python /root/SimPO/unit_test/unit_test_1.py`.
- First identify the concrete repository task before any setup work: locate the real target file/function, read the provided unit test, and determine the minimal code change needed. Do not start by building environments, extracting requirements, or installing packages speculatively.
- Keep all changes project-scoped and minimally invasive. Do **not** modify global interpreter paths or system executables (for example `ln -sf /usr/bin/python3 /usr/bin/python`), and do **not** use system-wide package installation workarounds such as `pip install --break-system-packages` unless the task explicitly requires it.
- If `python` is unavailable, prefer using an existing compatible interpreter such as `python3` for inspection and the provided test path rather than changing `/usr/bin/python`.
- Prioritize the shortest path to proof of completion: inspect the needed code/test context, make the minimal `simpo_loss` edit, run the required direct unit test, write `/root/loss.npz`, write `/root/python_info.txt`, verify both files, then stop with the exact required completion signal if one exists.