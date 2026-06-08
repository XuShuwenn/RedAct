---
name: reynolds-pipe-flow
description: "Compute the Reynolds number for internal pipe flow and classify the regime with robust parsing, validation, and correct threshold logic."
---

# Reynolds Number for Pipe Flow

Reusable workflow for calculating the pipe-flow Reynolds number (Re = ρ × v × D / μ) and classifying the flow regime (laminar, transitional, turbulent). Designed for tasks that provide fluid density (ρ), dynamic viscosity (μ), pipe diameter (D), and average flow velocity (v) via text input and require a formatted output.

## When to Use

Activate this skill when you need to:
- compute the pipe-flow Reynolds number from fluid and pipe parameters
- classify the regime using standard thresholds
- parse inputs that may contain varied key names (e.g., rho/ρ, mu/μ, diameter/D, velocity/v)
- produce a two-line, human-readable result with rounded Re

## Core Workflow

1. Parse inputs
   - Accept any of the following keys for each variable:
     - Density: rho, ρ, density
     - Dynamic viscosity: mu, μ, viscosity, dynamic_viscosity
     - Diameter: D, d, diameter
     - Velocity: v, u, velocity
   - Extract the first numeric value from each line and ignore units if present.
   - Allow input via command-line arguments or an input file. If both are present, command-line values override file values.

2. Validate values
   - μ must be > 0 (division by zero is invalid).
   - D must be > 0.
   - v ≥ 0.
   - ρ > 0.
   - If any check fails, stop and report a clear error.

3. Compute
   - Use Re = ρ × v × D / μ with full precision (do not round yet).

4. Classify flow regime using the unrounded Re
   - Re < 2300 → laminar
   - 2300 ≤ Re < 4000 → transitional
   - Re ≥ 4000 → turbulent

5. Format output
   - Round Reynolds number to 1 decimal place for display only.
   - Output exactly two lines when required:
     - "Reynolds number: {Re_rounded}"
     - "Flow regime: {laminar|transitional|turbulent}"

6. Write results
   - Write to the required output path or print to stdout if a path is not specified.

## Verification

- Dimensional sanity check: Ensure inputs are in consistent SI units (ρ in kg/m^3, μ in Pa·s, D in m, v in m/s). Re is dimensionless.
- Boundary tests: Verify regime logic on values near 2300 and 4000 using the unrounded Re.
- Rounding check: Confirm that only the displayed value is rounded; classification must use the unrounded Re.
- Numerical stability: Confirm μ is strictly positive to avoid division by zero. Ensure D > 0.
- Output conformity: Ensure two lines, correct labels, and a newline terminator if the task requires strict formatting.

## Common Pitfalls

- Using rounded Re for classification. Always classify from the unrounded value and round only for display.
- Misreading μ as kinematic viscosity (ν). The formula requires dynamic viscosity (Pa·s). If ν is provided instead, you must convert (ν = μ/ρ) before using Re = ρ v D / μ.
- Confusing diameter with radius or using D in the wrong units (e.g., mm instead of m). Convert units before computing.
- Incorrect thresholds (e.g., making 2300 or 4000 exclusive/inclusive incorrectly). Use the exact inequalities above.
- Failing to handle Unicode symbols (ρ, μ). Map common aliases and symbols to the required variables.
- Not guarding against μ ≤ 0, which leads to invalid results or exceptions.

## Optional Script Usage

A helper script is provided for robust parsing, computation, and output formatting.

- Compute from command line:
  - python scripts/reynolds_pipe.py --rho RHO --mu MU --D DIAM --v VEL

- Read from an input file (keys may include rho/ρ, mu/μ, D/diameter, v/velocity):
  - python scripts/reynolds_pipe.py --in input.txt

- Write to an output file in the two-line format:
  - python scripts/reynolds_pipe.py --in input.txt --out output.txt

Command-line arguments override values read from the input file.
