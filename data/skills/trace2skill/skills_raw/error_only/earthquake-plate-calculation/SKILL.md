---
name: earthquake-plate-calculation
description: "Find the earthquake furthest from the Pacific plate boundary within the Pacific plate using GeoPandas and distance calculations."
---

# Earthquake Pacific Plate Distance Analysis

## When to Use

- Calculate distances between earthquake locations and plate boundaries
- Find maximum distance from a plate boundary within that plate
- Work with geospatial data using GeoPandas

## Input Files

- `/root/earthquakes_2024.json`: Earthquake data
- `/root/PB2002_boundaries.json`: Plate boundary data
- `/root/PB2002_plates.json`: Plate polygon data

## Output Format

JSON at `/root/answer.json`:
```json
{
  "id": "earthquake_id",
  "place": "location description",
  "time": "",
  "magnitude": ,
  "latitude": ,
  "longitude": ,
  "distance_km":
}
```


## Execution Protocol

## Execution Protocol

- Follow any task- or system-specified tool/action syntax exactly as written.
- Treat task-specific execution and completion instructions as higher priority than examples or habits from this skill.
- If the environment requires a specific completion string, output that exact string and nothing else after the answer file is created and verified.
- Do not add narrative summaries, extra JSON, or alternative tool-call formats when exact action/completion formatting is mandated.
## Key Steps

1. Load earthquake data with GeoPandas
2. Load plate polygons and explicitly confirm which feature is the Pacific plate (do not assume the code/name without inspection)
3. Filter earthquakes within the confirmed Pacific plate polygon
4. Load plate boundary lines and verify the selected boundary features correspond to the Pacific plate
5. Calculate each earthquake's minimum distance to the verified Pacific plate boundary using a geodesic-aware method suitable for Pacific-wide / antimeridian-spanning geometry; do not rely on a single planar CRS for all point-to-boundary distances unless you explicitly validate it against a geodesic check
6. Find the earthquake with the maximum validated distance
7. Round distance_km to 2 decimal places


## Validation

## Validation

- Confirm the earthquake selection is based on the Pacific plate geometry itself; do not replace `within`/spatial-join logic with longitude/latitude box heuristics.
- If the spatial filter returns zero or surprising results, debug CRS, geometry validity, dateline handling, and predicate choice before changing the problem definition.
- Treat truncated or cut-off script output as a failed/unknown run. Rerun with logs or check the exit status before trusting `/root/answer.json`.
- Verify both that the script completed normally and that `distance_km` is reported in kilometers and rounded to 2 decimals.

## Tips

- Use appropriate GeoPandas projection for distance calculations
- Verify units: result should be in kilometers

- Treat this as a global/ocean-basin geospatial problem: a single azimuthal or other local projection can distort point-to-line distances across the full Pacific extent.
- If you use any projected-distance shortcut, cross-check the winner and nearby top candidates with a geodesic calculation before finalizing the result.
- Validate the spatial logic, not just the output file: inspect a few top-distance candidates and confirm containment/distance behavior is sensible near the antimeridian and multipart boundaries.
- Do not rank candidates using sampled boundary vertices, midpoint approximations, or a preliminary geodesic screen and then exact-check only a few finalists.
- If the task asks for the furthest in-plate earthquake, compute the final exact distance metric for the full filtered earthquake set before taking the argmax.
- Use approximations only for debugging; never let an approximation determine the winner unless you still recompute the exact distance for all candidates.
- Keep recovery steps task-faithful: do not add fallback selection rules that broaden "within the Pacific plate" into approximate coordinate ranges.
- Before distance calculations, inspect and confirm: the Pacific plate feature, the count/sample of earthquakes inside it, and the boundary features used for the Pacific boundary.
- If an identifier lookup returns unrelated output, fix the query and re-check instead of proceeding with an assumed plate code.
- Do not rely on unchecked string matching alone (for example, guessing from `Code`, `PlateName`, `PlateA`, or `PlateB`). Inspect available columns and verify that the chosen polygon really is the Pacific plate and that the chosen boundary features collectively trace its boundary.
- Before trusting the final result, sanity-check the selection: confirm the number of matched plate polygons/boundary segments is plausible and that downstream distances are computed only against those validated features.


## Final Check

## Final Check

- Before finishing, verify `/root/answer.json` exists and matches the required JSON schema exactly.
- Re-read the current task instructions for any exact procedural requirements that govern completion (for example: required output path, exact completion string, or mandated interaction format).
- Do not assume the analysis is complete until both the result and the required completion procedure match the instructions exactly.