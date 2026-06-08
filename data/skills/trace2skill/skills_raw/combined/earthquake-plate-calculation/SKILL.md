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
   - If the earthquake file is GeoJSON-like feature data and field access is unclear, parse feature properties/coordinates explicitly and normalize it into a GeoDataFrame with Point geometry early so containment, reprojection, and distance calculations stay in one consistent workflow.
2. Inspect the earthquake, plate, and boundary schemas first (geometry types, column/property names, CRS, feature counts, and a few sample values) before writing filters or output extraction logic
3. Load plate polygons, inspect available identifier/name columns, and explicitly confirm the authoritative Pacific plate identifier/code from the data itself; prefer a stable shared code field only if inspection shows it is correct, and keep visible evidence of the exact matching row(s) used
4. If antimeridian handling is needed, normalize Pacific-spanning geometries consistently across points, polygons, and boundaries before spatial filtering or distance work
5. Use the confirmed Pacific plate polygon only for containment: filter earthquakes within that polygon before any ranking or distance calculation
6. Load plate boundary lines separately, inspect boundary identifier/side fields, and select only the verified Pacific-boundary segments using the same confirmed Pacific identifier (for example rows where `PlateA` or `PlateB` matches the verified Pacific code); verify the selected features plausibly trace that same plate boundary, then combine them into one validated geometry before nearest-distance calculations
7. Calculate each in-plate earthquake's minimum distance to the verified Pacific plate boundary lines, not the polygon exterior as a shortcut. Keep containment/topology checks in EPSG:4326, then reproject both the filtered earthquakes and verified boundary geometry to a meter-based CRS for the main full-set distance pass; never measure directly in EPSG:4326 degrees
8. Because this is a Pacific-wide / antimeridian-spanning problem, geodesically validate the winner and nearby top candidates before finalizing, and do not let sampled vertices, midpoint shortcuts, or other approximations determine the winner
9. Compute the final exact distance metric for the full filtered in-plate set, then take the argmax of the validated distances
10. Round `distance_km` to 2 decimal places
11. Prefer a small reproducible script for the full workflow (load, inspect columns, isolate Pacific polygon/boundaries, filter earthquakes, compute distances, write `/root/answer.json`) instead of ad hoc interactive steps when the analysis has multiple geospatial transforms


## Validation

- Do a quick preflight check on the source files: confirm they load as expected, inspect key columns/properties, and verify geometry types/CRS before relying on field names, joins, or identifier guesses.
- Validate from logged evidence, not assumption: keep a visible check of the Pacific plate row/identifier, the number of earthquakes selected inside it, and the count/sample of boundary features before trusting the final argmax.
- Do not mix identifiers across layers: the polygon selection and boundary selection must both be traceable to the same verified Pacific plate identifier.
- Preserve the two-step geometry logic: use the Pacific plate polygon for in-plate membership, then use the verified Pacific plate boundary lines for edge distance. Do not substitute polygon distance for boundary distance.
- If boundary data uses adjacent-plate fields such as `PlateA`/`PlateB`, prefer deriving the Pacific boundary from those verified side identifiers instead of hand-picking segments by name alone.
- If antimeridian normalization or longitude shifting is used, confirm it is applied consistently to all relevant layers before `within` checks or distance calculations.
- Before computing distances, confirm the active CRS for the distance step is meter-based rather than EPSG:4326 degree units, apply it consistently to both earthquakes and boundary geometries, and convert to kilometers only after measurement.
- Preserve the order of operations: containment filter first, boundary restriction second, exact full-set distance computation third, argmax last.
- If a script's stdout/stderr is truncated, cut off, or missing an expected end marker, treat the run as incomplete: rerun with logging/redirection or check the exit status before trusting any output file.
- Artifact existence alone is insufficient. Verify the process exited successfully and that `/root/answer.json` was produced by a completed run.
- After writing `/root/answer.json`, read it back and verify the actual serialized fields/schema, that `distance_km` is numeric kilometers rounded to 2 decimals, and that the script completed normally.
- If task instructions mandate a specific action/tool schema or exact completion token, treat compliance as part of validation exactly as you check the answer schema.

## Validation

- Confirm the earthquake selection is based on the Pacific plate geometry itself; do not replace `within`/spatial-join logic with longitude/latitude box heuristics.
- If the spatial filter returns zero or surprising results, debug CRS, geometry validity, dateline handling, and predicate choice before changing the problem definition.
- Treat truncated or cut-off script output as a failed/unknown run. Rerun with logs or check the exit status before trusting `/root/answer.json`.
- Verify both that the script completed normally and that `distance_km` is reported in kilometers and rounded to 2 decimals.

## Tips

- Inspect source schemas before filtering so field names and Pacific identifiers come from the data, not guesses.
- Keep all geometries in one consistent GeoPandas workflow; converting event-style earthquake JSON into a GeoDataFrame early makes filtering, reprojection, and distance checks less error-prone.
- Good default workflow: inspect columns and sample values -> confirm the Pacific plate feature and identifier -> filter earthquakes by Pacific polygon membership -> derive matching Pacific boundary segments with that same identifier -> union the verified boundary geometry -> reproject to a metric CRS for bulk distance computation -> convert meters to kilometers -> geodesically sanity-check the chosen maximum-distance event.
- Use the polygon layer for in-plate membership and the boundary-line layer for point-to-boundary distance.
- If you use GeoPandas/Shapely `.distance(...)`, first reproject both earthquakes and boundary geometry to a metric CRS suitable for bulk measurement (for example `EPSG:4087`); never measure in `EPSG:4326` degrees.
- Treat this as a global/ocean-basin geospatial problem: if you use a projected-distance workflow, still geodesically validate the final winner and nearby top candidates before trusting the ranking.
- Prefer dataset-backed identifiers over guessed string matches, and when distances are measured against many Pacific boundary segments, union them first so every earthquake is compared to the same validated boundary geometry.
- Do not add fallback branches that replace Pacific-plate containment with longitude/latitude ranges or other loose geographic proxies.
- For multi-step GIS tasks across several files, prefer a short reproducible script (for example `/root/solve_earthquake.py`) that loads data, validates Pacific identifiers/features, computes the full result, and writes `/root/answer.json`.
- Verify units explicitly: projected distances may be in meters, so round to 2 decimals only after conversion to kilometers.
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

- Perform a procedural check as well as a data check: confirm your tool/action format matched the task instructions throughout the run.
- Confirm separately before finishing: (1) `/root/answer.json` exists, can be read back, and matches the required schema, and (2) the exact required final completion action/token has been emitted in the exact instructed format with no extra narrative if the task forbids it.
- Do not stop after a prose summary or file readback when the environment requires an explicit completion signal.

## Final Check

- Before finishing, verify `/root/answer.json` exists and matches the required JSON schema exactly.
- Re-read the current task instructions for any exact procedural requirements that govern completion (for example: required output path, exact completion string, or mandated interaction format).
- Do not assume the analysis is complete until both the result and the required completion procedure match the instructions exactly.