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

Read `/root/input.txt` first and confirm it contains exactly two whitespace-separated numbers in the order `theta phi`.

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

## Tips

- Read `/root/input.txt` before computing; do not assume different delimiters, units, or angle order.
- Prefer one short standalone Python script that performs: read input -> convert degrees to radians -> build state -> compute expectations -> write output -> verify output.
- Construct the qubit with `qt.basis(2, 0)` and `qt.basis(2, 1)` and use `qt.expect`; do not rely on `qt.QubitStates([theta, phi])`.
- Treat output formatting as part of correctness: labels must be exactly `Sigma X`, `Sigma Y`, `Sigma Z`, with signed 3-decimal values such as `Sigma X: +0.000`.
- If `qt.expect` returns tiny imaginary parts from numerics, write the real parts after confirming the imaginary component is negligible.
- Verify QuTiP symbols in the installed environment before relying on helper names from examples.
- Sanity-check results against Bloch-sphere geometry for pure states: `(sin(theta)cos(phi), sin(theta)sin(phi), cos(theta))` after converting to radians; for example, `theta=90°`, `phi=0°` should be approximately `(1, 0, 0)`.
