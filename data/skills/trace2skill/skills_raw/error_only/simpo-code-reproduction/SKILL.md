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
1a. Before editing `simpo_loss`, inspect the surrounding `SimPOTrainer` code in `/root/SimPO/scripts/simpo_trainer.py`, relevant call sites/config such as `/root/SimPO/scripts/simpo_config.py`, and the full unit test in `/root/SimPO/unit_test/unit_test_1.py` so the implementation matches this repository's actual interface, tensor semantics, and expected outputs.
1b. Use the paper to confirm the loss formula, but validate assumptions against repository code; do not implement from partial snippets, summaries, or guessed normalization/scaling behavior.
2. Implement `simpo_loss` function in `SimPOTrainer` class
3. Run unit test to verify implementation
4. Save loss to `/root/loss.npz` with key 'losses'
5. Follow the critical path: inspect code/test/paper context -> implement only the minimal change needed in `simpo_loss` -> run the provided unit test -> save `/root/loss.npz` with key `losses` -> write `/root/python_info.txt`.
6. Before finalizing, verify correctness against both the paper formula and the local trainer/test conventions, not just a passing test.

## Requirements

- Environment setup for SimPO project
- Prefer the existing project environment and the smallest runnable setup that can execute the provided unit test; avoid broad or speculative dependency changes unless a concrete traceback shows they are necessary.
- Inspect test/import requirements before installing packages, and verify imports after each install step.
- Log Python version and packages to `/root/python_info.txt` using the exact commands `python -VV` and `python -m pip freeze`.
- If you install or upgrade any package after creating `/root/python_info.txt`, rerun both commands and rewrite the file so it reflects the final environment used for the passing test.

## Output

- `/root/loss.npz`: Loss matrix with key 'losses'
- `/root/python_info.txt`: Environment info


- Before finishing, verify both required files exist and that `/root/loss.npz` contains key `losses`.

## Unit Test

- Run `/root/SimPO/unit_test/unit_test_1.py`
- Fixed input tensors provided
- Output should match expected loss values


- Read the test file before coding to determine expected outputs, tensor semantics, and minimal dependencies.
- Run the script directly: `python /root/SimPO/unit_test/unit_test_1.py`.
- Treat a passing `unit_test_1.py` result as necessary but not sufficient; also confirm the implementation matches the paper and local trainer conventions for scaling, beta/gamma handling, normalization assumptions, and outputs.
- If the test or imports fail, capture the full traceback first and identify the exact missing module or incompatibility before changing packages or the environment.


## Workflow Guardrails

## Workflow Guardrails

- Read repository code and tests before inferring behavior from the paper; use the paper to confirm formulas, not to replace the repository's implementation contract.
- Run only the minimal commands needed to execute the provided unit test; avoid broad setup/reinstall detours unless clearly required.
- If environment issues block testing, resolve them from concrete evidence, then rerun the real unit test immediately.
- Do not stop after patching: complete the test run and produce both `/root/loss.npz` and `/root/python_info.txt`.
## Tips

- Read paper carefully for loss formula
- Don't modify unit_test.py
- Verify reproducibility


- Inspect the full target function body, nearby helpers, call sites, class attributes, and configurable loss branches before replacing the placeholder implementation.
- Do not assume quantities are already length-normalized, averaged, or otherwise transformed unless the repository code or test explicitly shows that.
- If a file view or PDF extraction is truncated, continue reading targeted ranges until the needed code or formula is fully visible.
- Keep an explicit completion checklist: implementation done, unit test run successfully, `/root/loss.npz` saved with key `losses`, and `/root/python_info.txt` written.
