# Candidate Robustness Checks

## When to read this
Read this when BLS/TLS candidates change with detrending choices, when the best duration hits a search-grid edge, or when a preferred transit package is unavailable and you need a cheap confirmation step.

## 1) Duration-boundary warning
Treat these as model-failure signals, not as good detections:
- best duration equals the minimum tested duration
- best duration equals the maximum tested duration
- the same candidate keeps returning edge durations after minor retuning

Action:
- adjust detrending to remove residual low-frequency variability
- narrow durations to physically plausible transit values
- rerun and require the preferred candidate to move off the boundary before trusting it

## 2) Convergence rule across reasonable variants
Do not finalize from a single favorite run if nearby setups disagree.

Use at least two reasonable variants, for example:
- two detrending window lengths
- two nearby duration grids
- coarse search plus local refinement

Finalize only if the same candidate recurs with small drift. If the best period moves materially across variants, treat the solution as unresolved rather than choosing an average or the highest-power run.

## 3) Cheap fallback validation checks
If TLS or another heavy method fails, confirm a BLS candidate with one or more of:
- phase-fold the lightcurve and verify repeated transit-like dips at the candidate period
- compare odd vs even events for similar depth/timing
- count whether predicted transit times line up with multiple observed dips
- inspect obvious aliases/harmonics such as P, P/2, and 2P

A fallback candidate should be supported by more than one top-score statistic.
