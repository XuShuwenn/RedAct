---
name: paper-loss-implementation
description: "Implement a paper-defined pairwise preference loss in an ML repo, wire it to config, run the provided unit test deterministically, and log the Python environment for reproducibility."
---

# Implementing Paper-Defined Pairwise Loss with Reproducible Test Execution

This skill guides you to implement a pairwise preference loss described in a paper (e.g., SimPO-style objectives) inside an existing trainer class, integrate configuration parameters correctly, and run a fixed-input unit test to generate deterministic outputs while logging the exact Python environment.

## When to Use

Use this skill when:
- A repository includes a trainer with a missing or stubbed loss method whose definition is specified in an accompanying paper.
- A unit test with fixed tensors is provided to validate the loss implementation and save outputs for evaluation.
- The task requires logging Python version and installed packages for reproducibility.

## Core Workflow

1. Locate and Understand the Code Paths
- Identify the trainer file and the target loss function (e.g., `simpo_loss`).
- Read the configuration module to find relevant hyperparameters (names may include beta, margin ratio, loss type, and label smoothing).
- Inspect the unit test to understand input shapes, expected return values, and the output file/key it generates. Do not modify the unit test.

2. Extract the Objective from the Paper
- Establish the pairwise comparison between preferred (chosen) and non-preferred (rejected) responses using model scores (often log probabilities).
- Define reward scaling and margin:
  - chosen_rewards = beta × chosen_logps
  - rejected_rewards = beta × rejected_logps
  - margin term gamma = beta × gamma_ratio (gamma_ratio comes from config)
  - logits = (chosen_rewards − rejected_rewards) − gamma
- Implement loss variants:
  - Sigmoid-style objective with optional label smoothing:
    - Base loss per example: L = −log(sigmoid(logits))
    - With label smoothing s in [0, 1]:
      L = (1 − s) × [−log(sigmoid(logits))] + s × [−log(sigmoid(−logits))]
  - Hinge-style objective:
    - L = max(1 − logits, 0)
- Return per-example losses, chosen_rewards, and rejected_rewards as tensors.

3. Implement the Loss Function
- Use the repo's tensor library (e.g., PyTorch) and stable primitives:
  - For sigmoid-based: use `logsigmoid` and its negative form, or stable softplus equivalents.
  - Keep the implementation vectorized; avoid per-sample Python loops.
- Ensure the function reads configuration from the trainer (beta, gamma_ratio, loss_type, label_smoothing) rather than hardcoding values.
- Validate tensor shapes: chosen and rejected inputs should align; output tensors must match the batch dimension.
- Do not perform reductions to a single scalar unless the trainer explicitly requires it; unit tests often expect per-example losses.

4. Environment Setup and Test Execution
- Check the repo’s environment specification (e.g., environment.yml or requirements.txt).
- Verify the current Python version and, if needed, create a compatible virtual environment.
- Install the listed dependencies.
- Ensure the project directory is discoverable by Python (e.g., set PYTHONPATH to include the repo root) when running tests.
- Execute the provided unit test from the repository context so it can find imports and write outputs. Do not alter test files.

5. Reproducibility Logging
- After running the unit test, log environment details to the requested file using exactly:
  - `python -VV`
  - `python -m pip freeze`
- Write both outputs to the designated info file in a deterministic manner.

## Verification

- Shape and Type Checks:
  - losses: one value per input example (same batch dimension as inputs)
  - chosen_rewards and rejected_rewards: same shape as inputs
- Configuration Wiring:
  - Confirm beta scales rewards
  - Confirm gamma = beta × gamma_ratio is subtracted from the pairwise difference
  - Confirm loss_type switches behavior (sigmoid vs hinge)
  - Confirm label_smoothing blends the two sigmoid terms when > 0
- Numerical Sanity:
  - Hinge losses are non-negative
  - Sigmoid losses are positive and increase as logits decrease
- Determinism:
  - Unit test uses fixed tensors; re-running yields identical outputs
  - Output file contains the expected key (e.g., `losses`) with the correct shape
- Environment Log:
  - The Python version and full package list are recorded via `python -VV` and `python -m pip freeze`

## Common Pitfalls

- Misusing input scores:
  - Using probabilities instead of log probabilities when the trainer provides log probabilities
  - Mixing batch dimensions or broadcasting incorrectly between chosen and rejected inputs
- Margin and Scaling Errors:
  - Omitting beta scaling on rewards
  - Applying gamma_ratio without scaling by beta
  - Reversing the sign in logits (should be chosen − rejected − gamma)
- Loss Variant Mistakes:
  - Returning a scalar mean instead of per-example values when the unit test expects a vector
  - Ignoring label_smoothing when the config sets it
  - Not erroring on unknown `loss_type`
- Test and Environment Issues:
  - Modifying unit test files
  - Running the test without adding the repo to Python’s import path
  - Mismatched Python version vs environment specification
  - Forgetting to log environment details using the exact commands

## Success Criteria

- The trainer’s loss function compiles and returns (losses, chosen_rewards, rejected_rewards) tensors with correct shapes.
- The provided unit test runs and generates the expected output file containing a `losses` entry.
- Re-running the test yields identical results due to fixed inputs.
- The environment information file contains the outputs of `python -VV` and `python -m pip freeze`.

## Optional Script Usage

The helper script below provides a standalone, dependency-light implementation of the pairwise margin logits and losses (sigmoid with optional label smoothing, hinge). It can be used to validate formulas and shapes outside the repo before coding the trainer method.

- Use it to sanity-check logits and loss behavior for sample inputs.
- Do not rely on it during final unit test execution; the repository’s trainer must implement the loss.
