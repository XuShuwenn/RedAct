---
name: qubit-bloch-expectations
description: "Compute Pauli expectation values for a qubit given Bloch-sphere angles using QuTiP, with analytic cross-checks and strict output formatting."
---

# Qubit Expectation Values from Bloch Angles

Compute expectation values of the Pauli matrices (σx, σy, σz) for a single-qubit pure state specified by Bloch-sphere angles (theta, phi). Uses QuTiP operators for the primary result and verifies against the closed-form Bloch-vector expressions.

## When to Use

Activate this skill when the task is to:
- compute ⟨σx⟩, ⟨σy⟩, ⟨σz⟩ for a qubit state described by Bloch angles
- use QuTiP to build the state and evaluate expectations
- produce results rounded and formatted with explicit sign (e.g., +0.123)

## Core Workflow

1. Parse inputs
   - Expect two angles: theta and phi, provided in degrees unless stated otherwise.
   - Convert to floats; trim whitespace and validate parse.
   - Convert to radians: th = radians(theta_deg), ph = radians(phi_deg).

2. Construct the qubit state |ψ⟩ from Bloch angles
   - Use the standard parameterization for a pure qubit:
     |ψ⟩ = cos(th/2) |0⟩ + e^{i·ph} sin(th/2) |1⟩
   - With QuTiP, construct:
     ket = cos(th/2) * basis(2, 0) + np.exp(1j * ph) * sin(th/2) * basis(2, 1)
   - This is intrinsically normalized (cos² + sin² = 1). Optionally verify norm ≈ 1.

3. Define Pauli operators and compute expectations
   - Use QuTiP: sx = sigmax(), sy = sigmay(), sz = sigmaz().
   - Compute expectations with expect: vals = expect([sx, sy, sz], ket).
   - Coerce tiny imaginary parts to real (numerical noise), e.g., float(np.real_if_close(v)).

4. Format output
   - Round each value to 3 decimals and include explicit sign.
   - Example line format: "Sigma X: +0.123" (same for Y and Z, in that order).
   - Follow the exact ordering and spelling requested by the task.

5. Write results
   - Write lines in the required order to the specified output target.
   - Do not add extra lines or spaces. Ensure newline termination per line if specified.

## Verification

Perform these checks before finalizing:
- Analytic cross-check against Bloch-vector components:
  - bx = sin(th) · cos(ph)
  - by = sin(th) · sin(ph)
  - bz = cos(th)
  - Compare QuTiP results to (bx, by, bz) with a small tolerance (e.g., 1e-9 absolute before rounding).
- Normalization: (ket.dag() * ket).full()[0,0] ≈ 1 to within tolerance.
- Range and type:
  - Each expectation should be real within numerical tolerance and within [-1, 1].
- Formatting: After rounding to 3 decimals, ensure sign is explicit ("+" for non-negative, "-" for negative) and exactly three digits after the decimal point.

## Common Pitfalls

- Degrees vs radians: Trigonometric functions in NumPy expect radians. Always convert degrees to radians before use.
- Missing complex phase: Do not omit the e^{i·phi} factor on the |1⟩ amplitude.
- Pauli-Y sign/convention: Use QuTiP’s built-in sigmay() to avoid sign errors; do not handcraft σy unless you are certain of the convention.
- Nonexistent convenience constructors: If a convenience API for qubit-from-Bloch is unavailable, build the state explicitly with basis(2,0) and basis(2,1) as shown.
- Ignoring numerical noise: Small imaginary parts may appear due to floating-point error. Use np.real_if_close before formatting.
- Incorrect rounding/formatting: Ensure exactly three decimals and an explicit sign in the output. Avoid locale-dependent formatting.
- Wrong output order or labels: Keep the exact order and labels required (X, then Y, then Z).

## Success Criteria

- The output contains exactly three lines for σx, σy, σz, each with an explicit sign and three decimals.
- QuTiP-based expectations match analytic Bloch-vector values within tolerance.
- The constructed state is normalized, and all expectation values are real within numerical tolerance and in [-1, 1].

## Optional Script Usage

You can use the provided helper script to compute and verify expectations.

- Basic usage (angles in degrees):
  - python scripts/qubit_expectations.py --theta-deg 90 --phi-deg 0
- Read from stdin (a single line: "theta phi"):
  - echo "90 0" | python scripts/qubit_expectations.py --stdin
- Write to a file:
  - python scripts/qubit_expectations.py --theta-deg 45 --phi-deg 30 --output result.txt
- Enable analytic verification and set tolerance:
  - python scripts/qubit_expectations.py --theta-deg 60 --phi-deg 120 --verify --tol 1e-9
