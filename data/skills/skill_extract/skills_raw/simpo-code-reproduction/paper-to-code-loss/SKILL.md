---
name: paper-to-code-loss
description: "Implement and verify pairwise preference losses from research papers in ML repos, with environment setup and reproducible tests."
---

# Paper-to-Code Loss Implementation

A reusable workflow for implementing a paper-defined pairwise preference loss (e.g., SimPO/DPO-style objectives) into an existing codebase, setting up a compatible environment, and validating with provided unit tests and fixed tensors.

## When to Use

Activate this skill when you need to:
- implement or fix a loss function defined in a research paper
- map math equations to code variables (e.g., chosen/rejected log-probs, margins)
- set up a deterministic environment to run unit tests and save exact outputs
- produce reproducibility info (Python version and package list)

## Core Workflow

1. Inspect the codebase
- Locate the target function and its call site (e.g., Trainer.loss or a dedicated simpo_loss method).
- Read config classes/modules to discover hyperparameters (e.g., beta, gamma_beta_ratio, loss_type, label_smoothing).
- Inspect how inputs are produced (e.g., get_batch_logps) and whether log-probs are already length-normalized averages.
- Read the unit test to understand required outputs (file path, key names, shapes, dtypes) and any non-editable constraints.

2. Extract the loss from the paper
- Identify the canonical objective and map paper symbols to code variables:
  - average log-probabilities (per-token mean) vs summed log-probabilities
  - scaling factor beta
  - target margin gamma or a ratio that implies gamma = beta × gamma_beta_ratio
  - loss form: sigmoid (logistic) or hinge; whether label smoothing applies
- Write down a minimal variable mapping before coding:
  - avg_chosen_logps ← average log p(y_w | x)
  - avg_rejected_logps ← average log p(y_l | x)
  - chosen_rewards = beta × avg_chosen_logps
  - rejected_rewards = beta × avg_rejected_logps
  - gamma = beta × gamma_beta_ratio (if ratio is defined as gamma/beta). If the config already provides gamma directly, do not re-scale.
  - logits = chosen_rewards − rejected_rewards − gamma

3. Implement the loss
- Sigmoid loss (with optional label smoothing):
  - base: losses = −log σ(logits)
  - label smoothing ε in [0, 0.5]: losses = −[(1−ε) log σ(logits) + ε log σ(−logits)]
- Hinge loss variant:
  - losses = relu(1 − logits)
- Return per-example losses and detached rewards for metrics. Preserve shapes and devices.

4. Environment setup (reproducible and minimal)
- Read environment metadata (e.g., environment.yml) to discover required Python version.
- Create a clean environment that matches the repo’s Python version (e.g., with uv or venv) and install only the minimal deps required by the unit test (e.g., torch, transformers, trl, accelerate, datasets, numpy, any minor utils like rich) to reduce install time and conflicts.
- Example (adjust paths/versions to your project):
  - uv python install <py_version>
  - uv venv --python <py_version> /opt/env
  - /opt/env/bin/python -m pip install -U pip setuptools wheel
  - /opt/env/bin/python -m pip install "torch==<ver>" --index-url https://download.pytorch.org/whl/cpu
  - /opt/env/bin/python -m pip install "transformers==<ver>" "trl==<ver>" "accelerate==<ver>" "datasets==<ver>" "numpy==<ver>"

5. Run and verify unit tests
- Ensure the project root is on PYTHONPATH when running the test.
- Run the test using the environment’s Python.
- Verify the output file exists, has the right key name, shape, and dtype.
- Save reproducibility info: `python -VV` and `pip freeze` to a text file.

6. Minimal validation checks
- Sanity test: if avg_chosen_logps > avg_rejected_logps by a margin, losses should decrease; increasing gamma should increase losses.
- Confirm no double length normalization:
  - If the code already uses average log-probs, do not divide by lengths again.
- Confirm margin scaling:
  - If the config provides a ratio, compute gamma = beta × ratio.
  - If the config provides gamma directly, use it as-is.

## Implementation Template (Pairwise Margin Objective)

- Inputs: avg log-probs (1D tensors of shape [batch]), scalars beta, gamma or gamma_beta_ratio, loss_type in {"sigmoid", "hinge"}, label_smoothing epsilon.
- Pseudocode:

- Determine gamma:
  - if gamma_beta_ratio is provided and gamma is not:
    gamma = beta * gamma_beta_ratio

- Compute rewards:
  - chosen_rewards = beta * avg_chosen_logps
  - rejected_rewards = beta * avg_rejected_logps

- Compute logits:
  - logits = chosen_rewards - rejected_rewards - gamma

- Compute loss:
  - if loss_type == "sigmoid":
    - if label_smoothing == 0:
      losses = -log_sigmoid(logits)
    - else:
      losses = -(1-ε) * log_sigmoid(logits) - ε * log_sigmoid(-logits)
  - elif loss_type == "hinge":
    losses = relu(1 - logits)
  - else: raise error

- Return losses, chosen_rewards.detach(), rejected_rewards.detach()

## Verification

- Shape check: losses.shape == chosen_rewards.shape == rejected_rewards.shape == (batch,)
- Numeric sanity:
  - logits near large positive values → losses near 0 for sigmoid
  - logits near large negative values → losses large for sigmoid
  - hinge loss returns 0 when logits ≥ 1
- Output artifact:
  - Confirm npz file contains key exactly as required by the unit test (e.g., 'losses').
  - Ensure dtype is float and shape matches expectations.
- Reproducibility:
  - Write Python version and `pip freeze` to the required file; ensure repeatable installs by pinning versions in tests when possible.

## Common Pitfalls

- Wrong margin scaling:
  - Mistake: using gamma_beta_ratio as gamma directly without multiplying by beta when the ratio is defined as gamma/beta.
  - Fix: compute gamma = beta × gamma_beta_ratio unless gamma is provided directly.

- Double length normalization:
  - Mistake: re-dividing by sequence length when log-probs are already averages.
  - Fix: confirm data provenance; if average_log_prob=True in upstream code, do not divide again.

- Misapplied label smoothing:
  - Mistake: applying smoothing to hinge loss.
  - Fix: only apply label smoothing to sigmoid loss.

- Environment mismatch:
  - Mistake: using a Python or package version that changes trainer APIs (e.g., missing expected functions/imports).
  - Fix: match Python and core library versions required by the repo; install a minimal set needed for the unit test. Prefer aligning versions over patching imports.

- Ignoring PYTHONPATH
  - Mistake: running tests without ensuring the project root/module path is importable.
  - Fix: run tests with the project root on PYTHONPATH or install the package in editable mode if appropriate.

- Modifying unit tests
  - Mistake: editing the test harness to fit your output or API.
  - Fix: adapt your implementation to the test requirements; only change project code as intended by the task.

## Optional Script Usage

- scripts/pairwise_margin_loss.py
  - Reusable utilities to compute pairwise logits and losses (sigmoid/hinge) with label smoothing for quick experimentation or validation outside the training loop.

- scripts/log_env.py
  - Convenience tool to write `python -VV` and `pip freeze` to a file for reproducibility.
