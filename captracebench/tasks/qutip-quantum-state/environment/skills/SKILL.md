---
name: qutip
description: "Compute quantum state expectation values for Pauli matrices from Bloch sphere coordinates. Use when working with quantum state analysis, Bloch sphere representation, or Pauli matrix expectation values."
---

# QuTiP: Quantum State Expectation Values from Bloch Sphere

## Overview

Given Bloch sphere coordinates (theta, phi), compute the expectation values of the three Pauli matrices (σx, σy, σz).

## Creating Quantum State from Bloch Coordinates

```python
from qutip import spin_coherent, expect, sigmax, sigmay, sigmaz
import numpy as np

# Read theta and phi in degrees
theta_deg, phi_deg = map(float, open("/root/input.txt").read().split())
theta = np.radians(theta_deg)  # Convert to radians
phi = np.radians(phi_deg)

# Create quantum state on Bloch sphere
# spin_coherent(s, theta, phi) where s=1/2 for qubit
psi = spin_coherent(1/2, theta, phi)

# Compute expectation values
sx = expect(sigmax(), psi)
sy = expect(sigmay(), psi)
sz = expect(sigmaz(), psi)

# Print results with 3 decimal places
print(f"Sigma X: {sx:+.3f}")
print(f"Sigma Y: {sy:+.3f}")
print(f"Sigma Z: {sz:+.3f}")
```

## Key Functions

### spin_coherent(s, theta, phi)
Creates a coherent spin state on the Bloch sphere.
- `s`: spin quantum number (use `1/2` for qubit)
- `theta`: polar angle in radians (0 to π)
- `phi`: azimuthal angle in radians (0 to 2π)

### expect(op, state)
Computes expectation value ⟨ψ|O|ψ⟩ of an operator.
- `op`: operator (e.g., `sigmax()`, `sigmaz()`)
- `state`: quantum state (ket or density matrix)

### Pauli Matrices
```python
sigmax()   # σx
sigmay()   # σy
sigmaz()   # σz
```

## Example: theta=90°, phi=0° (Bloch sphere +X state)

```python
theta = np.radians(90)
phi = np.radians(0)
psi = spin_coherent(1/2, theta, phi)
# Should give: <σx>≈1, <σy>≈0, <σz>≈0
```

## Key Reference

- `spin_coherent(1/2, theta, phi)` — Create qubit state from Bloch angles
- `expect(operator, state)` — Compute expectation value
- `sigmax()`, `sigmay()`, `sigmaz()` — Pauli matrices
- `np.radians()` — Convert degrees to radians