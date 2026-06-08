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

0. Read the current task/system instructions for execution mechanics before any analysis step. If they require a specific tool/action schema, allowed tool names, or exact completion token, use that protocol verbatim for every invocation and for the final response; do not substitute other tool-call styles, aliases, or a prose completion.

1. Inspect the raw earthquake, plate, and boundary files first (top-level shape, feature paths, geometry types, property/column names, CRS, feature counts, and a few sample values) before writing parsing or filter logic.
   - For large GeoJSON/JSON inputs, inspect only a small sample first (for example, top-level keys, feature count, first 1-3 features, and property keys) instead of dumping the entire file; use that sample to choose the parsing approach.
2. If the earthquake file is GeoJSON-like feature data, parse feature properties/coordinates explicitly and normalize it into a GeoDataFrame with Point geometry early so containment, reprojection, and distance calculations stay in one consistent workflow.
3. Inspect the earthquake, plate, and boundary schemas first (geometry types, column/property names, CRS, feature counts, and a few sample values) before writing filters or output extraction logic.
   - Minimum inspect-first evidence: print the top-level JSON shape for earthquakes, list columns for plates/boundaries, and show 1-3 representative rows/features from all three files before writing parsing or boundary-selection code; record the actual observed columns/property paths used later.
   - Do not reference guessed fields like `plate1`/`plate2` or assume flat earthquake keys such as `longitude`/`latitude` until the inspected schema shows they exist.
   - If a GeoJSON file is too large or noisy to inspect comfortably in raw form, switch immediately to a short Python/GeoPandas inspection script that prints only the needed schema facts, sample rows, and confirmed identifiers; do not rely on partial manual scrolling for large feature collections.
4. Load plate polygons, inspect available identifier/name columns, and explicitly confirm the authoritative Pacific plate identifier/code from the data itself (for example, a validated row showing `PlateName = Pacific` and its matching stable code such as `Code = PA` if the dataset uses those fields). Keep visible evidence of the exact matching row(s) used before reusing that identifier downstream.
   - Prefer stable metadata fields such as `Code` and `PlateName` when inspection shows they identify the Pacific plate unambiguously; do not rely on feature order or implicit position in the file.
   - Prefer confirming the Pacific feature first (for example, by searching likely name/code columns and printing the matching row) before building the full containment-and-distance workflow.
   - Explicitly inspect the selected Pacific plate geometry type/layout (for example Polygon vs MultiPolygon) after load so downstream containment and antimeridian handling use the actual geometry structure, not an assumption.
5. Use the confirmed Pacific plate polygon only for containment: filter earthquakes within that polygon before any ranking or distance calculation
   - Use a predicate that matches the task's intended inclusion semantics after inspection (`within`, `covered_by`, or equivalent). If points that appear to lie on the plate edge are possible, do not silently exclude them just because `within` is strict; inspect a sample and choose the predicate deliberately.
6. Load plate boundary lines separately, inspect boundary identifier/side fields, and select only the verified Pacific-boundary segments using the same confirmed Pacific identifier (for example rows where `PlateA` or `PlateB` matches the verified Pacific code); verify the selected features plausibly trace that same plate boundary, then combine them into one validated geometry before nearest-distance calculations
   - Do not require a single boundary-name pattern such as one exact `Name` value; boundary labels may vary (`PA-AN`, `AU-PA`, `KE/PA`, etc.). Prefer verified side-membership fields over name-only matching when assembling the full Pacific boundary set.
7. Calculate each in-plate earthquake's minimum distance to the verified Pacific plate boundary lines, not the polygon exterior as a shortcut. Keep containment/topology checks in EPSG:4326, then reproject both the filtered earthquakes and verified boundary geometry to a meter-based CRS for the main full-set distance pass; never measure directly in EPSG:4326 degrees
8. Because this is a Pacific-wide / antimeridian-spanning problem, geodesically validate the winner and nearby top candidates before finalizing, and do not let sampled vertices, midpoint shortcuts, or other approximations determine the winner
9. Compute the final exact distance metric for the full filtered in-plate set, then take the argmax of the validated distances; do not shortlist candidates with approximations and only exact-check a few finalists.
9a. After selecting the argmax, read back that winning earthquake row from the same filtered dataset used for distance computation and map each required output field (`id`, `place`, `time`, `magnitude`, latitude, longitude) from observed source columns/properties before writing `/root/answer.json`; do not reconstruct winner metadata from guessed field names, stale earlier samples, or a different intermediate table.
10. Round `distance_km` to 2 decimal places after converting from meters to kilometers
11. Prefer a small reproducible script for the full workflow (load, inspect columns, isolate Pacific polygon/boundaries, filter earthquakes, compute distances, write `/root/answer.json`) instead of ad hoc interactive steps when the analysis has multiple geospatial transforms
   - Default to a single end-to-end script once the initial schema inspection is done; use ad hoc commands only for quick inspection or targeted validation, not as the primary analysis path.
12. If you create a script or JSON artifact, write the actual executable/data content, not comment-only scaffolding, pseudocode, or a prose description of intended logic. Immediately read the file back and confirm it contains runnable code/data matching the intended artifact type before executing or trusting it.
   - Do not use placeholder file-write actions such as "wrote the script" without visible contents. The decisive computation must be inspectable from the transcript via the write payload itself or an immediate readback.
   - If the write mechanism or transcript shows only a paraphrase like "created script to..." rather than visible source code/data, assume the artifact is not trustworthy yet; rewrite it using a safer method and read it back before proceeding.
13. Treat results as valid only if the logged command or script run is concrete and reproducible; if a command is malformed, non-executable, or merely descriptive, rerun with an explicit executable command before trusting any output.
14. Never use placeholder shell text as if it were a command. Write the exact executable command instead of descriptions like `inspect the earthquake JSON structure`, `run the analysis script`, or `list relevant JSON files`.
15. When creating a script, write full runnable code only: real imports, concrete data loading, actual geometry/filter/distance logic, and explicit output writing. Do not save TODOs, English placeholders, or comment-only scaffolding as if they were executable.
16. Keep the decisive workflow in this order unless inspected data proves a required adjustment: inspect schemas -> confirm Pacific polygon identifier -> filter earthquakes inside that polygon -> derive matching Pacific boundary segments with the same identifier -> reproject both filtered earthquakes and verified boundary geometry to a meter-based CRS -> compute exact distances for the full filtered set -> take the argmax -> write and read back `/root/answer.json`.


## Validation

- Do a quick preflight check on the source files: confirm they load as expected, inspect key columns/properties, and verify geometry types/CRS before relying on field names, joins, or identifier guesses.
- For large source files, a lightweight schema sample is enough for preflight: confirm top-level structure, geometry type(s), and representative property keys/values without trying to print the full dataset.
- Validate from logged evidence, not assumption: keep a visible check of the Pacific plate row/identifier (including both the human-readable name and the reused code when available), the number of earthquakes selected inside it, and the count/sample of boundary features before trusting the final argmax.
- Treat a failed or contradictory identifier lookup as a blocked prerequisite, not a minor warning. If a query meant to confirm the Pacific plate returns unrelated rows or ambiguous results, stop and inspect schema/sample rows until the Pacific polygon identifier and matching boundary-side identifier are explicitly verified from the data.
- Record the contradictory output itself and the follow-up inspection that resolves it before proceeding. Do not continue to filtering or distance calculations on the assumption that the intended Pacific identifier is "probably" correct.
- Do not mix identifiers across layers: the polygon selection and boundary selection must both be traceable to the same verified Pacific plate identifier.
- Preserve the two-step geometry logic: use the Pacific plate polygon for in-plate membership, then use the verified Pacific plate boundary lines for edge distance. Do not substitute polygon distance for boundary distance.
- If boundary data uses adjacent-plate fields such as `PlateA`/`PlateB`, prefer deriving the Pacific boundary from those verified side identifiers instead of hand-picking segments by name alone.
- If antimeridian normalization or longitude shifting is used, confirm it is applied consistently to all relevant layers before `within` checks or distance calculations.
- Before computing distances, confirm the active CRS for the distance step is meter-based rather than EPSG:4326 degree units, apply it consistently to both earthquakes and boundary geometry, and convert to kilometers only after measurement.
- A good default for bulk distance comparison is projecting both layers to `EPSG:4087`, then computing distances in meters and converting to kilometers for the final output.
- Preserve the order of operations: containment filter first, boundary restriction second, exact full-set distance computation third, argmax last.
- Explicitly verify that no outside-Pacific earthquakes are included in the ranked set; if ranking was done before containment filtering, discard that result and recompute on the in-plate subset only.
- Explicitly verify that the distance step used reprojected geometries in a metric CRS for the decisive computation; if the script measured in EPSG:4326 or degree units, treat the result as invalid and rerun.
- If a script's stdout/stderr is truncated, cut off, or missing an expected end marker, treat the run as incomplete: rerun with logging/redirection or check the exit status before trusting any output file.
- Artifact existence alone is insufficient. Verify the process exited successfully and that `/root/answer.json` was produced by a completed run.
- After writing `/root/answer.json`, read it back and verify the actual serialized fields/schema, that `distance_km` is numeric kilometers rounded to 2 decimals, and that the script completed normally.
- If task instructions mandate a specific action/tool schema or exact completion token, treat compliance as part of validation exactly as you check the answer schema.
- Validate procedural compliance explicitly against the current task instructions before finishing: correct tool/action format used throughout, required output path produced, and exact completion token ready.
- Add an explicit interface audit before finalizing: confirm every prior tool invocation used the permitted tool name(s) exactly and matched the required action/schema if one was mandated. If any call used an unsupported name, typo, or alternate format, treat the run as non-compliant.
- Validate transcript mechanics before finishing: confirm every tool invocation used the required schema, no unsupported tool names/aliases or malformed action payloads were used, and the final assistant message is exactly the required completion token/string with no extra prose when exclusivity is required.
- Before running the main script, verify that every referenced input field/column in the code was observed in the inspected schema output.
- If you created or edited a script, verify the on-disk file contains executable code by reading it back before treating the run as supported.
- If a created `.py` file reads back as narrative text, bullet points, or comments describing intended logic rather than executable Python, treat it as a failed artifact creation and rewrite it before running anything.
- Keep execution evidence traceable: every claimed observation should come from a concrete logged command or script run that another reader could repeat.
- Validate command concreteness, not just intent: if the log shows a description of what was supposedly done instead of the literal executable command, treat that evidence as missing and rerun with an explicit command.
- If you created a script for the main analysis, read back enough of the file to confirm it is real Python code rather than placeholders before executing it or citing its results.
- Prefer robust, minimal validation commands. For anything beyond a trivial expression, use a short `python3 - <<'PY'` block or a small temporary script rather than fragile `python -c` one-liners with compound statements.
- If a validation command errors, truncates, or produces unclear output, treat that check as not performed; rerun with a simpler command before relying on the result.
- A plausible result is not enough: if any explicit protocol requirement was violated, treat the task as incomplete and fix the procedure before finalizing.
- Before writing `/root/answer.json`, read back the selected winning earthquake row from the filtered in-plate dataset and confirm its output fields (`id`, `place`, time, magnitude, coordinates) come from that exact row rather than from guessed property names or a separately parsed source object.
- If you use a verified shared identifier such as the Pacific code to connect polygons and boundary segments, log the exact column names and matching value used in each layer so the relationship is auditable from the run output.
- Use this minimal evidence chain before trusting the winner: (1) show the exact Pacific polygon row/identifier from the plate file, (2) show the boundary-side filter built from that same identifier, (3) show the count of earthquakes contained in the Pacific polygon, and only then (4) compute and rank distances.
- If you use a script for the decisive run, prefer putting the schema inspection prints and identifier confirmation inside that same script so the logged run shows the data-backed assumptions and the final result together.

## Validation

- Confirm the earthquake selection is based on the Pacific plate geometry itself; do not replace `within`/spatial-join logic with longitude/latitude box heuristics.
- If the spatial filter returns zero or surprising results, debug CRS, geometry validity, dateline handling, and predicate choice before changing the problem definition.
- Treat truncated or cut-off script output as a failed/unknown run. Rerun with logs or check the exit status before trusting `/root/answer.json`.
- Verify both that the script completed normally and that `distance_km` is reported in kilometers and rounded to 2 decimals.

## Tips

- Inspect source schemas before filtering so field names and Pacific identifiers come from the data, not guesses; when available, confirm both the Pacific name field and the exact code/value you will reuse for boundary selection.
- When files are large, prefer sampling over full reads during inspection: print only the top-level structure and a few representative features/properties, then move to the scripted workflow.
- Keep all geometries in one consistent GeoPandas workflow; converting event-style earthquake JSON into a GeoDataFrame early makes filtering, reprojection, and distance checks less error-prone.
- Good default workflow: inspect schemas and sample values -> confirm the Pacific plate feature and shared identifier -> write one short reproducible script -> filter earthquakes by Pacific polygon membership -> derive matching Pacific boundary segments with that same identifier -> union the verified boundary geometry -> reproject to a metric CRS for bulk distance computation (for example `EPSG:4087`) -> convert meters to kilometers -> geodesically sanity-check the chosen maximum-distance event -> write and read back `/root/answer.json`.
- Preserve this proven sequence: containment filter first, then metric-CRS boundary distance computation, then write `/root/answer.json` and read it back for verification.
- When source GeoJSON layers are large, prefer a small script that prints targeted inspection output (columns, CRS, feature counts, Pacific match rows) and then continues into the full computation instead of trying to inspect the raw files manually.
- A reliable pattern is: confirm the Pacific plate feature exists and capture its identifier first, then reuse that verified identifier for polygon selection, boundary selection, and the final scripted distance analysis.
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

- Safe quick-check pattern: use `python3 - <<'PY'` blocks for anything beyond a trivial expression, then print the specific fact you need to verify. Avoid dense one-line constructs that are easy to truncate or misquote.
- If you already have the requested file and the checks pass, finalize immediately; additional ad hoc commands should be the exception, not the default.


## Final Check

- Perform a procedural check as well as a data check: confirm your tool/action format matched the task instructions throughout the run.
- Confirm separately before finishing: (1) `/root/answer.json` exists, can be read back, and matches the required schema, and (2) the exact required final completion action/token has been emitted in the exact instructed format with no extra narrative if the task forbids it.
- Do not stop after a prose summary or file readback when the environment requires an explicit completion signal.

- Final pre-completion checklist: (1) `/root/answer.json` exists and matches schema, (2) any created script used for the decisive computation was read back and contains actual runnable code, (3) every tool invocation used the exact required action syntax and permitted tool names, and (4) the exact required completion token will be emitted with no extra text.
- Do not end with a natural-language success message, recap, or result summary when an exact completion token is required; the required token is part of task correctness.

## Final Check

- Before finishing, verify `/root/answer.json` exists and matches the required JSON schema exactly.
- Re-read the current task instructions for any exact procedural requirements that govern completion (for example: required output path, exact completion string, or mandated interaction format).
- Do not assume the analysis is complete until both the result and the required completion procedure match the instructions exactly.