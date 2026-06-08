---
name: qutip-quantum-state
description: "Compute Pauli matrix expectation values for quantum states represented as Bloch sphere coordinates using QuTiP."
---

# Quantum State Expectation Values

## When to Use

- Compute expectation values of observables
- Analyze quantum states on Bloch sphere
- Use QuTiP for quantum calculations

## Input Format

File `/root/input.txt`:
```
theta phi
```
- theta: 0-180 degrees
- phi: 0-360 degrees

Treat both angles as degrees from the input file, then convert to radians before any trigonometric or state-construction step.

Read `/root/input.txt` first and confirm it contains exactly two whitespace-separated numbers in the order `theta phi`.
Use those two parsed values as the only task parameters for the computation; do not reorder them or infer alternate parameterizations.

- Inspect the actual contents before coding anything else; build the smallest script around the observed two-number format rather than assuming extra structure.

## Calculations

Using QuTiP:
```python
import qutip as qt

# Create state from Bloch angles
state = qt.QubitStates([theta, phi])

# Compute expectation values
<sigma_x> = qt.expect(qt.sigmax(), state)
<sigma_y> = qt.expect(qt.sigmay(), state)
<sigma_z> = qt.expect(qt.sigmaz(), state)
```

## Output Format

To `/root/output.txt`:
```
Sigma X: +0.XXX
Sigma Y: +0.XXX
Sigma Z: +0.XXX
```

Round to 3 decimal places, always include the sign, and preserve the exact labels shown above, e.g. `{value:+.3f}`. If QuTiP returns a complex number with only negligible imaginary numerical noise, confirm the imaginary part is ~0 and write only the real part.

For example:
```python
with open('/root/output.txt', 'w') as f:
    f.write(f"Sigma X: {sigma_x:+.3f}\n")
    f.write(f"Sigma Y: {sigma_y:+.3f}\n")
    f.write(f"Sigma Z: {sigma_z:+.3f}\n")
```

After writing, read `/root/output.txt` back to confirm the labels, order, newline-separated lines, signs, rounding, and formatting are exact.
Execute the script before finishing, and rely on the generated `/root/output.txt` rather than assuming the code is correct.

Use a post-write exact-content check when possible: read the file back and confirm it matches the expected three newline-separated lines in the required order, with labels exactly `Sigma X`, `Sigma Y`, `Sigma Z` and values formatted via `{value:+.3f}`.
Also verify the script's computed values agree with what was written to `/root/output.txt`; do not treat console output or an in-memory value as sufficient.

## Tips

- Read `/root/input.txt` before computing; do not assume different delimiters, units, or angle order.
- Prefer one short standalone Python script that performs: read input -> convert degrees to radians -> build state -> compute expectations -> write output -> verify output.

- For this kind of small numeric task, prefer direct execution of one short Python script in the workspace rather than manual derivation or multi-step hand transcription.
- Use the values read from `/root/input.txt` as the single source of truth for the computation.
- Prefer QuTiP for the Pauli operators and expectation values; do not reimplement the Pauli matrices unless QuTiP is unavailable.
- Verify the installed QuTiP API before using convenience helpers. If a helper such as `qt.QubitStates` is unavailable or unclear, construct the pure state directly with supported primitives after converting to radians: `state = np.cos(theta/2) * qt.basis(2, 0) + np.exp(1j * phi) * np.sin(theta/2) * qt.basis(2, 1)`, then use `qt.expect`.
- Treat output formatting as part of correctness: labels must be exactly `Sigma X`, `Sigma Y`, `Sigma Z`, with signed 3-decimal values such as `Sigma X: +0.000`.
- If `qt.expect` returns tiny imaginary parts from numerics, write the real parts after confirming the imaginary component is negligible.
- Verify QuTiP symbols in the installed environment before relying on helper names from examples.
- Sanity-check results against Bloch-sphere geometry for pure states: `(sin(theta)cos(phi), sin(theta)sin(phi), cos(theta))` after converting to radians; for example, `theta=90°`, `phi=0°` should be approximately `(1, 0, 0)`.

- Prefer checking the written file itself rather than relying on terminal prints or intermediate variables when validating success.
- Avoid placeholder notation like `<sigma_x>` in code; assign real Python variable names such as `sigma_x`, `sigma_y`, `sigma_z` and format those values into the output file.
- Prefer direct expectation values of the Pauli operators with `qt.expect` over indirect conversions or manual Pauli-matrix arithmetic.
- Before finishing, sanity-check results against Bloch-sphere geometry for pure states: `(sin(theta)cos(phi), sin(theta)sin(phi), cos(theta))` after converting to radians.
- Probe the installed QuTiP environment before coding against remembered APIs; for example, confirm the version and available symbols, then choose a compatible implementation.
- Prefer supported QuTiP primitives for state construction and expectations; a direct superposition from `qt.basis(2, 0)` and `qt.basis(2, 1)` is the default safe choice.
- If a convenience helper from examples or memory is unavailable, replace it with equivalent core primitives instead of changing libraries.
- If QuTiP or its dependencies emit non-fatal warnings, continue only if the state construction, `qt.expect` calls, and output-file verification still succeed; do not change approach just because of a warning message.
- Run the script after writing it; do not stop at code generation. Confirm `/root/output.txt` exists and matches the required format exactly.
