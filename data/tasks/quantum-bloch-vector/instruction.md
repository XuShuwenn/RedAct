# Bloch Sphere Vector Task

Given a quantum state as Bloch angles (theta, phi) in `/root/input.txt`, calculate the Bloch vector components (rx, ry, rz).

theta and phi are in degrees (0-180 for theta, 0-360 for phi).

Bloch vector components:
- rx = sin(theta) * cos(phi)
- ry = sin(theta) * sin(phi)
- rz = cos(theta)

Write to `/root/output.txt`:
```
rx: +0.XXX
ry: +0.XXX
rz: +0.XXX
```

Round to 3 decimal places.