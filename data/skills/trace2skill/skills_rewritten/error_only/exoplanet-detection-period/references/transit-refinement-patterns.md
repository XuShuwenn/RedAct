# Transit Refinement Patterns

## When to read this
Read this when stellar variability is much stronger than the transit signal, or when TLS/BLS both seem useful and you need a concise discovery-then-refinement workflow.

## Activity-dominated light curves
If low-frequency modulation is large compared with the transit depth:
- remove obvious outliers first
- flatten/detrend before the transit search
- choose a detrending window comfortably longer than the expected transit duration so box-shaped dips survive
- if the first window choice is uncertain, compare one or two nearby windows and keep periods that remain stable

Examples of acceptable flattening approaches:
- `lightkurve.LightCurve(...).remove_outliers(...).flatten(window_length=..., polyorder=...)`
- median-filter or similar low-frequency trend removal using available scientific Python tools

## TLS then BLS refinement
Use this pattern when TLS is available and its API is verified quickly:
1. Run TLS to identify the strongest candidate period neighborhood
2. Build a narrower, denser BLS grid around that candidate
3. Recompute with BLS and take the refined best period
4. Validate with phase folding and basic alias/harmonic checks before writing the answer

Why this works:
- TLS is often effective for discovery
- BLS on a manually dense local grid gives better numeric refinement for the final 5-decimal output

## Stability check
Before finalizing, compare the candidate period across:
- at least two reasonable detrending windows or flattening settings, when practical
- nearby harmonic/alias alternatives such as `P`, `P/2`, and `2P`

Prefer the period that is both transit-like when phase-folded and stable under those small preprocessing changes.
