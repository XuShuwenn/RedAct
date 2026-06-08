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

Round to 3 decimal places.

## Tips

- Use qt.QubitStates for Bloch coordinates
- Convert degrees to radians
- qt.expect for observable expectation values
