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
0a. Before any setup or installs, locate the real `simpo_loss` implementation site and read the full target function, nearby helper logic, config usage, and the complete unit test with additional targeted reads if any output is truncated.
0b. Do not start with environment recreation, broad dependency installation, or package upgrades while the exact missing code change or concrete test blocker is still unidentified.
1a. Before editing `simpo_loss`, inspect the surrounding `SimPOTrainer` code in `/root/SimPO/scripts/simpo_trainer.py`, relevant call sites/config such as `/root/SimPO/scripts/simpo_config.py`, and the full unit test in `/root/SimPO/unit_test/unit_test_1.py` so the implementation matches this repository's actual interface, tensor semantics, and expected outputs.
1a.i. Read the full current `simpo_loss` method body itself, not just search hits or truncated snippets, plus enough nearby helper logic to understand its inputs, returned values, class attributes, and any alternate branches before making any edit.
1a.ii. While inspecting, identify repository-specific fields, helpers, and branches that affect loss behavior (for example `get_batch_logps`, `get_batch_loss_metrics`, `beta`, `gamma_beta_ratio`, `loss_type`, `label_smoothing`, reward/logit conventions, return shapes, and detached metrics) and implement against those concrete expectations.
1a.iii. Determine from the repo/test whether inputs like `policy_chosen_logps` and `policy_rejected_logps` are raw sequence log-prob sums, already sequence-aggregated values, or length-normalized average log probabilities; if they are already averaged/normalized, do not divide by sequence length again when applying the SimPO formula.
1a.iv. If any file or PDF view is truncated, continue reading targeted ranges until you have the complete `simpo_loss` body, nearby helper/config logic, and the full unit test assertions before coding.
1b. Use the paper to confirm the loss formula, but validate assumptions against repository code; do not implement from partial snippets, summaries, or guessed normalization/scaling behavior.
1c. Explicitly map paper variables onto this repository's existing quantities before coding so you do not reapply normalization or mis-scale beta/gamma terms; if the paper uses a parameter not stored directly, derive it from existing config fields used by this codebase (for example, the effective `gamma` from `beta * gamma_beta_ratio` when applicable).
1d. Do not code from unreadable or partial paper extraction output. If the formula is not directly visible from a trustworthy paper excerpt, keep reading targeted paper/code/test sections until you can confirm the exact formula and map each term to local variables.
1d.i. A binary/open failure is not paper evidence. If `/root/SimPO/paper.pdf` is not yet readable as text, use a lightweight extraction/view method and confirm the specific SimPO objective text before claiming the implementation is paper-based.
1d.ii. If the paper remains inaccessible after reasonable targeted attempts, rely on repository code/tests for implementation details and explicitly use the paper only after obtaining readable formula content.
1e. Before editing `simpo_loss`, verify from the paper and local code/test together how `beta`, `gamma_beta_ratio`, `loss_type`, and `label_smoothing` are used, what tensors the function must return, and whether nearby reward/log-prob, reduction, or normalization branches affect the implementation.
1f. Do not edit until you have direct evidence from the repository: read the full current `simpo_loss` body from `def simpo_loss` through its final return, plus enough surrounding lines to see helper usage and all branches. A signature, docstring, grep hit, header-only view, or truncated snippet is not sufficient.
1g. Before coding, inspect the full `unit_test_1.py` and identify exactly how test tensors/artifacts are loaded and what outputs are asserted. If provided artifacts are relevant, inspect them using the same library/mechanism the test uses rather than guessing their format.
1h. Treat full inspection as a gate: before any package install, interpreter switch, or environment creation, finish reading the full current `simpo_loss` body, enough surrounding trainer/config code to identify its real inputs/outputs, and the complete `unit_test_1.py` assertions.
1i. When using shell/search tools, issue only executable commands and literal search patterns. Do not type intentions like `inspect local paper content` or vague grep patterns like `loss-related terms`; instead use concrete commands such as `ls`, `sed -n '1,240p' ...`, `grep -n "simpo_loss\|gamma_beta_ratio\|label_smoothing" ...`, or a small Python snippet that actually reads the target file/PDF.
2. Implement `simpo_loss` function in `SimPOTrainer` class
2a. Reopen the exact `simpo_loss` region in `/root/SimPO/scripts/simpo_trainer.py` and patch only that real function body; do not use blind/global replacement or edits based on task text, summaries, or guessed snippets.
2a.i. Before any edit, capture the exact existing lines you will replace from the live file. Do not use placeholder descriptions or guessed snippets as the edit target; anchor the change to verified source text from the actual `simpo_loss` body and nearby context.
2a.ii. Keep source edits tightly scoped to the requested implementation. Do not modify unrelated imports, fallback helpers, compatibility shims, tests, or other trainer logic just to work around environment issues unless a concrete traceback proves another minimal code change is strictly required.
2a.iii. If execution fails before reaching `simpo_loss`, prefer non-source fixes first: run from the correct repo root, set `PYTHONPATH`, use the matching interpreter, or install only the specific missing dependency shown by the traceback.
2b. Immediately after editing, re-read the modified function to confirm the change landed in the intended region, then run a lightweight file-level validation such as `python -m py_compile /root/SimPO/scripts/simpo_trainer.py` or an equivalent minimal import check before the full unit test.
2b.i. Verification is mandatory: read back the edited `simpo_loss` lines themselves and confirm the expected math and returns are present before doing environment work, installs, or full test execution.
2c. Do not assume the patch landed correctly from the edit command alone. Read back the full edited `simpo_loss` region (not just a header or short snippet) and confirm the intended final code is present before testing.
2d. Do not let investigation exceed the point of sufficiency: once you have (a) the full current `simpo_loss` body, (b) the relevant helper/config/test evidence for tensor semantics and expected outputs, and (c) the paper formula mapping, stop researching and edit `simpo_trainer.py` immediately.
2e. Prioritize the direct repository change: inspect local source/config/test files, patch `simpo_loss`, and attempt the provided unit test before any broad environment reconstruction. Do not spend the session creating new environments, installing environment managers, or installing large ML stacks unless a concrete traceback from the real test shows that a specific package/version is required.
3. Run unit test to verify implementation
3a. Treat observed execution of `python /root/SimPO/unit_test/unit_test_1.py` as mandatory evidence, not an intention. Do not conclude the task after editing or environment setup unless this script has actually been run and its result inspected.
4. Save loss to `/root/loss.npz` with key 'losses'
5. Follow the critical path: inspect code/test/paper context -> implement only the minimal change needed in `simpo_loss` -> run the provided unit test -> save `/root/loss.npz` with key `losses` -> write `/root/python_info.txt`.
6. Before finalizing, verify correctness against both the paper formula and the local trainer/test conventions, not just a passing test.

7. Use this execution order unless a concrete traceback forces otherwise: inspect full trainer/config/test and readable paper context -> implement only the minimal `simpo_loss` change -> run `python /root/SimPO/unit_test/unit_test_1.py` -> save `/root/loss.npz` with key `losses` -> write `/root/python_info.txt` -> verify both files.
8. If the unit test initially fails, capture the complete traceback before any install/upgrade, make only the smallest evidence-based environment or execution-context fix, then rerun the same real test immediately.
8a. Treat partial or truncated tracebacks as insufficient evidence. Re-run in a way that shows the exact exception or isolate the failing import first; do not install or upgrade packages until the concrete missing module, symbol, or version incompatibility is identified.
8b. Prefer the minimal execution fix order: verify `python`/`python3` availability, inspect repo dependency files and test imports, try the direct script, then fix repo-root / `PYTHONPATH` / working-directory issues before any package install or new environment.
8c. If the repository declares pinned or expected dependency versions, prefer those exact versions over broad unpinned installs; avoid upgrading core ML stacks speculatively.
8d. After each concrete environment or execution-context fix, rerun `python /root/SimPO/unit_test/unit_test_1.py` immediately before doing anything else.
8e. If an optional reference step fails (for example, importing an external trainer for comparison, using a helper inspection script, or reading nonlocal reference code), treat it as nonblocking. Fall back to local repository files (`simpo_trainer.py`, config, tests, paper) and keep progressing to the edit and real unit test.
9. Use a hard completion checklist before stopping: direct inspection completed, `simpo_loss` edited and read back, the provided unit test run successfully, `/root/loss.npz` saved with key `losses`, `/root/python_info.txt` updated after any package changes, and if the runtime requires a specific action schema or completion token, follow it exactly and finish with that exact completion signal.
10. Before the final response, perform a protocol check: if an exact completion string is required, emit exactly that string and nothing else. Do not substitute a narrative summary, and do not append extra text after the required token.

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
- Do not stop after patching: complete the test run and produce both `/root/loss.npz` and `/root/python_info.txt`.

- Before any package install, environment creation, or OS-level setup, confirm you have already read the full target function and full unit test and identified the smallest plausible `simpo_loss` change.
- Start with the task-critical path, not environment exploration: inspect the full `simpo_loss` body, inspect the full unit test, then attempt the direct required test command before broad setup checks.
- Anti-stall rule: if you have enough repository evidence to implement `simpo_loss`, switch from reading to editing. Do not continue gathering context once the missing step is simply to patch the function.
- Keep edits transparent in the trajectory: show the target function context before editing and read back the edited region after editing so the implementation can be audited.
- Treat environment debugging as traceback-first: capture the full failing error or a minimal reproducer before any install, and avoid introducing new version conflicts by changing several core ML packages at once.
- When imports fail, prefer repo-root execution-context fixes and repository-declared dependency versions; avoid broad unpinned installs that can create API drift.
- Treat optional reference imports/lookups and PDF utilities as nice-to-have only. If they fail or are unavailable, continue by reading local files directly and proceed with the minimal implementation/test loop.
- Do not perform broad environment rebuilds or package-stack installs before editing `simpo_loss` and attempting the real test once; use concrete test tracebacks to justify each environment change.
- Do not stop after launching a rerun. Wait for the real unit test result, inspect whether it passed or failed, and continue until you have either a verified passing run plus required deliverables or a concrete blocking error.
- Never mark the task complete from a code patch alone or from environment progress alone. Completion requires evidence that the designated unit test actually ran, plus verified creation of `/root/loss.npz` with key `losses` and `/root/python_info.txt`.
## Tips

- Read paper carefully for loss formula
- Don't modify unit_test.py
- Verify reproducibility

- Inspect the full target function body, nearby helpers, call sites, class attributes, and configurable loss branches before replacing the placeholder implementation.
- Do not assume quantities are already length-normalized, averaged, or otherwise transformed unless the repository code or test explicitly shows that.
- Translate the paper equation into the repository's score semantics before writing code; confirm whether values are already averaged, normalized, or margin-adjusted in surrounding code.
- Use `simpo_config.py` and `unit_test_1.py` to pin down which trainer attributes and defaults actually matter (`beta`, `gamma_beta_ratio`, `loss_type`, `label_smoothing`) before editing `simpo_loss`.
- Reuse existing trainer/config attributes to express paper hyperparameters; do not invent new constants or config keys when the same quantity can be derived from current fields.
- If a file view or PDF extraction is truncated, continue reading targeted ranges until the needed code or formula is fully visible.
- Safe edit pattern: view the current `simpo_loss` code, patch only the identified lines, then view that region again to verify the final code matches what you intended.
- If shell PDF tools are unavailable, use a lightweight Python PDF reader only for extracting the relevant objective text rather than adding heavy document-processing dependencies.
- If the test fails on imports, fix the specific missing or incompatible package or execution context from the traceback rather than reinstalling the whole ML stack.
- If you create `/root/python_info.txt` before the environment is final, rerun exactly `python -VV` and `python -m pip freeze` and rewrite the file after the passing test.
- Keep an explicit completion checklist and do not leave setup mode until each item is done: full target/test/paper inspected, `simpo_loss` implemented, unit test run successfully, `/root/loss.npz` saved with key `losses`, and `/root/python_info.txt` written.
- Treat `/root/loss.npz` and `/root/python_info.txt` as blocking deliverables; verify them at the end instead of assuming they were written.


## Execution Protocol and Scope Guardrails

## Execution Protocol and Scope Guardrails

- Follow the runtime's required action/tool schema exactly on every step. If the environment specifies a particular `Action:`/JSON format, tool-call syntax, or final completion token, use that exact format for every interaction and finish with the exact required completion signal.
- Use only the execution interface actually provided by the runtime/system for shell work. Do not invent alternate tool abstractions, editors, web fetchers, todo tools, or pseudo-tool syntaxes.
- Issue only executable shell commands. Do not send natural-language placeholders such as `extract paper text`, `inspect the file`, or `run the provided unit test`; instead send a real command like `sed -n '1,220p' ...`, `python ...`, `grep ...`, or `cd /root/SimPO && PYTHONPATH=/root/SimPO python /root/SimPO/unit_test/unit_test_1.py`.
- First identify the concrete repository task before any setup work: locate the real target file/function, read the provided unit test, and determine the minimal code change needed. Do not start by building environments, extracting requirements, or installing packages speculatively.
- Keep all changes project-scoped and minimally invasive. Do **not** modify global interpreter paths or system executables (for example `ln -sf /usr/bin/python3 /usr/bin/python`), and do **not** use system-wide package installation workarounds such as `pip install --break-system-packages` unless the task explicitly requires it.
- If `python` is unavailable, prefer using an existing compatible interpreter such as `python3` for inspection and the provided test path rather than changing `/usr/bin/python`.
- Prioritize the shortest path to proof of completion: inspect the needed code/test context, make the minimal `simpo_loss` edit, run the required direct unit test, write `/root/loss.npz`, write `/root/python_info.txt`, verify both files, then stop with the exact required completion signal if one exists.