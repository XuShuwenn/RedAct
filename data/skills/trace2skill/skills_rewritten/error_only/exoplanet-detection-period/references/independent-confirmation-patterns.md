# Independent Confirmation Patterns

## When to read this
Read this when a transit candidate depends strongly on preprocessing, when TLS or another preferred validator fails, or when the top BLS solution is close to other strong peaks.

## Minimum independent confirmation
Do at least one of these before finalizing:
- Phase-fold the lightcurve at the candidate period and confirm repeated transit-like dips line up coherently
- Compare the candidate against other nearby strong peaks, not just P/2 and 2P
- Re-run with a second reasonable detrending setup and check that the same candidate remains competitive
- Check odd-even event consistency when the candidate could be a doubled/halved eclipsing-like solution

## Insufficient by itself
These checks help but do not count as full independent confirmation on their own:
- checking only P/2 and 2P
- choosing the detrending window that maximizes BLS power
- accepting a solution whose best duration is pinned to the search-grid minimum or maximum without re-running

## Boundary-hit rule
If the reported best duration equals the smallest or largest searched duration:
1. treat the peak as suspicious
2. widen or shift the duration grid to physically plausible values
3. re-run and confirm the period remains stable
