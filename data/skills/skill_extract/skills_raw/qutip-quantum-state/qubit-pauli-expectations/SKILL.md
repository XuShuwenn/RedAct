---
name: qubit-pauli-expectations
description: "Compute σx, σy, σz expectation values for a single-qubit state given Bloch angles (theta, phi) using QuTiP, with robust angle handling and exact output formatting."
---

# Single-Qubit Pauli Expectations from Bloch Angles (QuTiP)

This skill computes expectation values of the Pauli matrices (σx, σy, σz) for a pure qubit state specified by Bloch sphere angles (theta, phi). It prefers QuTiP APIs and includes a deterministic fallback construction and analytic verification.

## When to Use

Activate this skill when you need to:
- compute ⟨σx⟩, ⟨σy⟩, ⟨σz⟩ from Bloch angles (theta, phi)
- use QuTiP to construct the state and calculate expectations
- produce fixed-format output with signed, rounded values

## Core Workflow

1. Parse input
   - Read two numbers: `theta` and `phi` in degrees.
   - Convert to radians: `theta_rad = theta_deg * π/180`, `phi_rad = phi_deg * π/180`.

2. Construct the qubit state (|ψ⟩)
   - Preferred (QuTiP, widely available): `psi = qutip.spin_coherent(1/2, theta_rad, phi_rad)`.
   - If the above is unavailable or unsuitable, build explicitly:
     - |ψ⟩ = cos(theta/2)|0⟩ + e^(i·phi) sin(theta/2)|1⟩ using QuTiP basis vectors.

3. Compute expectations with QuTiP
   - Use `qutip.expect` with `qutip.sigmax()`, `qutip.sigmay()`, `qutip.sigmaz()`.
   - Extract real parts and cast to Python floats to avoid tiny imaginary residues.

4. Format results
   - Round to 3 decimals and include a leading sign: `f"{value:+.3f}"`.
   - Write exactly three lines in this order:
     - `Sigma X: <value>`
     - `Sigma Y: <value>`
     - `Sigma Z: <value>`

5. Final checks
   - Ensure |ψ⟩ is normalized (norm ≈ 1 within tolerance).
   - Each expectation must lie within [-1, 1] up to small numerical error; clamp near-zero values within tolerance to 0 for clean formatting.

## Verification

Perform at least one of the following independent checks:
- Analytic Bloch formula: For a Bloch vector (theta, phi), the expectations satisfy
  - ⟨σx⟩ = sin(theta)·cos(phi)
  - ⟨σy⟩ = sin(theta)·sin(phi)
  - ⟨σz⟩ = cos(theta)
  Compare your QuTiP results to this analytic result with a tight tolerance (e.g., 1e-9) before rounding.
- Sanity cases (for quick spot checks):
  - theta = 0 → ⟨σz⟩ ≈ +1 and ⟨σx⟩ ≈ ⟨σy⟩ ≈ 0
  - theta = π → ⟨σz⟩ ≈ −1 and ⟨σx⟩ ≈ ⟨σy⟩ ≈ 0
  - theta = π/2, phi = 0 → ⟨σx⟩ ≈ +1, others ≈ 0
  - theta = π/2, phi = π/2 → ⟨σy⟩ ≈ +1, others ≈ 0

Success criteria:
- Output has exactly three lines in the order X, Y, Z with signed 3-decimal numbers.
- Numerical values agree with analytic Bloch predictions within tolerance before rounding.
- No extra text or lines beyond the required output.

## Common Pitfalls

- Degrees vs. radians: Forgetting to convert input degrees to radians before calling trigonometric functions or QuTiP APIs.
- API availability differences: Some QuTiP builds may not provide a `QubitStates` helper. Use `spin_coherent(1/2, theta, phi)` or explicit basis construction as a robust alternative.
- Tiny imaginary parts: `expect` may return complex numbers with negligible imaginary components due to numerical noise. Take `np.real` before formatting.
- Incorrect angle conventions: Ensure theta is polar angle from +z and phi is azimuthal angle around z. The chosen `spin_coherent` and the analytic formulas above share this convention.
- Formatting errors: Missing leading sign, wrong decimal precision, or wrong line order will cause format mismatches.
- Silent norm drift: If you manually construct the state, confirm normalization; otherwise expectations may drift outside [-1, 1].

## Optional Script Usage

A helper script is provided to parse inputs, construct the state, compute expectations with QuTiP when available, and write the required output.

Example:
- From explicit angles: `python scripts/qubit_expectations.py --theta-deg 90 --phi-deg 0 --output output.txt`
- From a file containing: `theta phi` on one line: `python scripts/qubit_expectations.py --input input.txt --output output.txt`

The script:
- Converts degrees to radians
- Prefers `qutip.spin_coherent(1/2, theta, phi)`; falls back to explicit state construction if needed
- Uses `qutip.expect` for σx/σy/σz if QuTiP is present; otherwise verified analytic values are used (only as a last resort)
- Writes exactly:
  - `Sigma X: +0.XXX`
  - `Sigma Y: +0.XXX`
  - `Sigma Z: +0.XXX`
