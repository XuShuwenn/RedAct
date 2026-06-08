---
name: reynolds-pipe-flow
description: "Compute the pipe-flow Reynolds number from density, dynamic viscosity, diameter, and velocity, and classify the flow regime with precise rounding and formatting."
---

# Reynolds Number for Pipe Flow

Compute Reynolds number for internal (pipe) flow and classify the flow regime using standard thresholds. Read scalar inputs from the task's input file, compute Re = ρ × v × D / μ, round to 1 decimal, classify, and write exactly two lines to the designated output file.

## When to Use

- The task provides fluid density (ρ), dynamic viscosity (μ), pipe diameter (D), and average flow velocity (v) and asks for the Reynolds number and flow regime.
- Input values are provided in a text file with labels, potentially using alternate label spellings (e.g., rho/ρ, mu/μ, diameter/D, velocity/v).

## Core Workflow

1. Ingest input values
   - Read the input file path specified by the task instructions.
   - Extract four scalars: density (ρ), dynamic viscosity (μ), diameter (D), velocity (v).
   - Accept common label variants: density (rho, ρ), viscosity (mu, μ, dynamic viscosity), diameter (D, diameter), velocity (v, flow velocity).
   - Parse numbers robustly, allowing integers, decimals, and scientific notation.

2. Validate inputs
   - Ensure all four parameters are present and parseable as floats.
   - Check μ > 0 to avoid division by zero and nonphysical values.
   - Check ρ > 0, D > 0, v ≥ 0. If any fail, stop and correct the extraction.
   - Confirm you are using dynamic viscosity μ (Pa·s), not kinematic viscosity ν (m²/s).

3. Compute Reynolds number
   - Use Re = ρ × v × D / μ with floating-point arithmetic.
   - Keep full precision for logic; do not prematurely round.

4. Classify the flow regime using the unrounded Re
   - Re < 2300 → laminar
   - 2300 ≤ Re < 4000 → transitional
   - Re ≥ 4000 → turbulent

5. Prepare outputs
   - Round Re to exactly 1 decimal place for display.
   - Format exactly two lines:
     - Reynolds number: {value with 1 decimal}
     - Flow regime: {laminar|transitional|turbulent}
   - Do not add extra commentary, units, or lines.

6. Write results
   - Write the two lines to the output file path specified by the task instructions.
   - Overwrite any existing file content.

## Verification

- Numerical sanity checks
  - Re must be nonnegative and dimensionless.
  - If μ is very small, expect a large Re; if v or D are small, expect a smaller Re.
- Boundary checks
  - If Re is near 2300 or 4000, classify based on the unrounded value, not the rounded display value.
  - Confirm the regime label matches the thresholds exactly.
- Rounding and formatting checks
  - Display Re with exactly one decimal using a dot as decimal separator.
  - Output should be exactly two lines with labels spelled and capitalized as specified and no trailing spaces.
- File write confirmation
  - Re-open the output file and confirm both lines exist and match the expected pattern.

## Common Pitfalls

- Using radius instead of diameter (D must be the full diameter; if given radius R, then D = 2R).
- Confusing dynamic viscosity μ (Pa·s) with kinematic viscosity ν (m²/s). Do not use ν in Re = ρ v D / μ.
- Dividing by zero or nonpositive μ; always validate μ > 0 before computing.
- Classifying with rounded Re instead of the unrounded value, causing boundary misclassification.
- Incorrect rounding (e.g., printing too many decimals or none). Always format to 1 decimal.
- Rigid parsing that fails on symbols (μ, ρ) or scientific notation. Use robust label matching and numeric parsing.
- Adding extra text or blank lines to the output file that violate the required format.

## Optional Script Usage

You can use scripts/compute_reynolds.py to parse common input formats, compute Re, classify the regime, and emit the two standardized output lines.

- Parse labeled file: python scripts/compute_reynolds.py --from-file INPUT.txt --write OUTPUT.txt
- Provide values directly: python scripts/compute_reynolds.py --rho 1000 --mu 0.001 --D 0.05 --v 1.2 --write OUTPUT.txt

The script:
- Accepts label variants (rho/ρ, mu/μ, D/diameter, v/velocity) and scientific notation.
- Validates positivity and μ > 0.
- Classifies using unrounded Re and prints Re with exactly one decimal.
