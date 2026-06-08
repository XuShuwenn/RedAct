# Quantum State Expectation Values Task

Given a quantum state represented as a Bloch sphere coordinate (theta, phi), compute the expectation values of the three Pauli matrices (sigma_x, sigma_y, sigma_z) using the `qutip` Python library.

The input is given in `/root/input.txt` with format:
```
theta phi
```
where theta and phi are in degrees (0-180 for theta, 0-360 for phi).

Write results to `/root/output.txt` with format:
```
Sigma X: +0.XXX
Sigma Y: +0.XXX
Sigma Z: +0.XXX
```

Use qutip.QubitStates to create the state and qutip.expect to compute expectation values. Round each value to 3 decimal places.