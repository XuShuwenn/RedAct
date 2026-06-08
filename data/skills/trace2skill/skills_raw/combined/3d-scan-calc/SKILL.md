---
name: 3d-scan-calc
description: "Analyze 3D mesh files to calculate geometric properties (volume, components) and extract attribute data from STL files."
---

# 3D Scan Calculation

## When to Use

- Calculate volume of complex or noisy 3D meshes
- Filter debris from scan data by isolating largest component
- Extract metadata (material IDs) stored in binary STL files


## Task-Protocol Overrides


- Treat task-specific execution rules as mandatory overrides to this skill: if the prompt requires a specific tool/action syntax, completion token, final message format, file path, or schema, follow that exact contract.
- Before the first tool call, check whether the task defines a required invocation format; if it does, use that format consistently for every tool interaction.
- Before the final response, re-check for any exact completion requirement (for example a literal token such as `ACTION: TASK_COMPLETE`) and output exactly what the task requires, with no extra prose if the task forbids it.
- Do not let otherwise-correct geometry or mass results fail on protocol noncompliance.
## Basic Workflow

1. Inspect the workspace for provided helper scripts/tools that already parse the mesh or compute the requested geometry; prefer validated task-provided or existing mesh-analysis utilities over reimplementing STL parsing or connectivity analysis from scratch.
   - If a helper already returns values like main-component volume, component selection, or material ID, use those results directly after sanity-checking them against the task requirements.
   - Preferred execution order for scan-derived mass tasks: discover helper/tool -> isolate largest geometric component -> read volume/material ID from that component -> retrieve exact density row -> compute mass only if units are explicitly supported.
   - Preferred successful pattern for multi-step tasks: use the helper/tool for largest-component geometry extraction, read the external lookup table early, then run one small script that performs lookup, arithmetic, and required file output end-to-end.
   - If using a helper such as a mesh analyzer, still verify that it preserved the task-relevant attribute/Material ID and that its "largest component" logic is geometric connectivity, not metadata grouping.
   - When running provided helpers or your own script, try the working interpreter directly; if `python` is unavailable, retry with `python3` before changing approach.
2. Parse the STL file (binary format) only if needed
   - Keep extraction staged: first obtain geometric measurements and raw identifiers from the mesh, then perform any external table lookup and final arithmetic as a separate step.
   - Preserve task-defined meanings of STL attribute bytes; if the prompt says they encode Material ID or similar metadata, extract and carry that field through to the lookup step.
   - For binary STL, explicitly read the 2-byte attribute field from each 50-byte triangle record when the task indicates it carries metadata; do not let a default parser silently drop it.
   - If metadata is triangle-level (for example, Material ID in attribute bytes), summarize or preserve it before/while isolating components so the selected main component can still be tied back to the correct ID(s).
3. Identify connected components
   - Prefer a mesh-analysis library/tool that can split the mesh into connected components and return the largest component directly; fall back to manual triangle/vertex adjacency only if no suitable tool is available.
   - DO NOT implement components as `material_id -> triangles` or pick the main part as the material with the largest summed volume; disconnected regions sharing one material must remain separate components.
   - Minimum acceptable pattern: build triangle/vertex adjacency from shared geometry, run connected-components traversal, measure each geometric component, then select the requested largest component.
   - For scanned meshes with debris, perform component isolation before extracting volume or attribute-driven physical properties.
   - Build components from mesh connectivity (shared vertices/edges between triangles), not from material IDs, colors, or other metadata labels
   - If asked for the main part, select the largest geometric connected component after connectivity analysis
4. Extract geometric properties (volume) and attributes
   - If any required lookup file/table output is truncated or does not visibly include the needed material ID/key, do a targeted re-read/search for that exact entry before using it.
   - If final quantities depend on an external reference file (for example, a material-density table), read/parse that reference early so the extracted material ID can be resolved immediately against the exact source row.
   - After isolating the requested geometric component, determine its material/attribute value from the triangles in that component rather than from whole-file assumptions.
   - If attribute values differ within the selected component, report the inconsistency and do not assume a single material ID unless the task provides a rule for resolving it.
   - If mesh units are not explicitly stated in the STL/task/supporting docs, keep geometric results in file units and treat mass as unverified rather than choosing a conversion.
5. Compute derived values (mass = volume × density)
   - Keep the dependency order explicit for multi-step tasks: `largest connected component -> geometric measurement(s) + material ID from that component -> exact reference-table row for that ID -> derived calculation`.
   - Before writing any derived physical quantity, explicitly compute and record the chain in order: component-selection result, extracted material ID, exact retrieved lookup row/value, unit evidence (or lack of it), conversion used, and final arithmetic.
6. Before mass calculation, verify two prerequisites: (a) the exact material-ID-to-density row was explicitly retrieved, and (b) any unit conversion is supported by explicit evidence.
7. If either prerequisite is missing, stop short of a definitive mass claim and state what remains unverified.
   - Do not write a definitive mass/result file field that depends on those missing prerequisites; leave the physical quantity unverified instead of choosing a conventional unit or guessed lookup value.
8. Verify the full chain before final output: selected component -> material ID -> density lookup -> unit assumptions/conversion -> final arithmetic.
9. If the task requires writing a result file or structured payload, validate the exact final artifact after writing: re-open/read it, confirm required fields and numeric values match your intended result, and fix any malformed serialization before finishing.
   - Write exactly the requested path and schema only; do not rename the file, omit required keys, or add extra keys/prose beyond the contract.
   - Before writing any artifact that includes mass or other unit-dependent physical quantities, confirm unit evidence is explicit in the task/files/docs. If units are still ambiguous and multiple conversions remain plausible, do not write a definitive physical value; write only the verified geometry in file units plus an explicit `unverified`/`ambiguous units` status if the schema allows, or stop and report the blocker.
10. If tooling or your own script produces multiple candidate results under different unit assumptions, do not pick one by convention; resolve the ambiguity from explicit evidence or report that no definitive physical quantity can be concluded.
11. Follow any task-specific execution/output protocol literally. If the task or system message requires a specific tool-call format, schema, file path, or exact completion token, use that exact format and end exactly as required; do not substitute your usual tool syntax or a free-form closing message.


## Important Notes

- STL attribute bytes may store metadata (material ID, color)
- Volume units depend on STL coordinate system - verify before computing

- Do not assume STL units by convention alone. If units are not stated in metadata, task text, or accompanying documentation, report geometric results in file units (for example, volume in file-units^3) rather than silently converting.
- If density is given in a fixed unit system (for example `g/cm^3`), only convert mesh volume when the mesh length unit is supported by explicit evidence.
- If multiple unit interpretations remain plausible and would produce materially different masses, do not choose one arbitrarily; keep investigating or report the ambiguity.
- If unit ambiguity remains unresolved, do **not** write a definitive mass to the final artifact/output file. Either continue investigating until the length unit is evidenced, or report volume in file units and explicitly mark mass as unverified.
- Do **not** justify a unit choice with bounding-box size, plausibility, scanning conventions, or "typical STL units" alone; those are not sufficient evidence for conversion to density-table units.
- Filter out noise/debris by keeping largest connected component

- Do not treat material ID groups as connected components unless the task explicitly defines components that way.
- When a task provides an external material-density table or lookup file, treat that file as the source of truth: read/parse it directly, verify the exact material ID entry, and do not hard-code or infer mappings from partial previews.
- If a lookup table or sidecar-file read is truncated or partial, re-read or search for the exact material ID/key before using the value.
- Do not use a density value unless the exact material ID row/key was explicitly retrieved from the source file in the current task context.
- DO NOT reconstruct or hard-code a material-density mapping from a partial preview, prior run, or hand-copied subset. Read the referenced source file directly, search/parse until the exact material ID entry is found, and keep the used row traceable in the final result.
- If you cannot retrieve that exact entry, report the lookup as unverified rather than guessing.
- Wrong: using a density for ID 42 when the visible table output only showed rows through ID 25.
- Right: re-read/search the file for `42`, then cite the exact retrieved row/value before computing mass.

- Treat write success as insufficient by itself when producing deliverables: verify the contents of the written file/payload, not just the tool's success message.

- Prefer parsing the provided lookup file directly in code over manually transcribing a density dictionary from terminal output, especially when the file is long or initially viewed only partially.
- Do not treat a plausible final number as sufficient. Before saving a derived numeric deliverable, ensure the log or script output shows the exact lookup row, the unit status, and the arithmetic that reproduces the written value.
- Once required geometry/attribute values have been extracted from the provided files or trusted helper output, stop exploratory digging unless a new check can produce explicit task-relevant evidence. Do not let inconclusive searches (file size, conventions, web info, internal skill code, plausibility arguments) change the numeric result.

- Binary STL parsing (2-byte attribute at end of each triangle)
- For binary STL tasks where the prompt assigns meaning to the 2-byte attribute field, parse and preserve it explicitly through component selection and later lookup steps instead of discarding it as unused.
- Connected component analysis for noise filtering
- Reliable implementation pattern: build triangle connectivity from shared vertices/edges, run connected-components traversal, keep the largest geometric component, then compute its measurements.
- Volume calculation from mesh geometry
- For closed meshes, compute volume by summing signed tetrahedral contributions from triangle vertices; use the absolute value only after summing the signed total.

- For debris filtering: construct triangle/vertex adjacency, compute connected components, then keep the component with the greatest geometric extent (typically volume or triangle count as requested)
- For triangle-based volume, use simple helper functions for cross/dot products and signed-volume accumulation in pure Python instead of `numpy`.
- Do not add or install external packages for basic STL parsing, connectivity, or volume math unless the task explicitly requires them and the environment already guarantees them.
- Prefer a short end-to-end scripted workflow for multi-step tasks: first try an existing helper/tool for mesh analysis, then isolate the largest component if needed -> extract attribute/material ID -> read exact density entry -> compute outputs -> write required result file in the exact requested schema -> read it back to verify.
- Keep that workflow reproducible and auditable: emit or retain the intermediate values used for the final result (selected component measurement, extracted material ID, matched lookup row/value, unit status, arithmetic) so the written artifact can be checked against the computation.
- If an existing mesh-analysis tool can supply largest-component measurements and preserved STL attribute metadata in one run, prefer that single-tool flow over mixing custom parsers and manual geometry code.
- Use manual STL parsing mainly when the task specifically requires byte-level extraction or when a mesh tool cannot expose the needed geometry/attributes.## Common Patterns

- Binary STL parsing (2-byte attribute at end of each triangle)
- Connected component analysis for noise filtering
- Volume calculation from mesh geometry


- For debris filtering: construct triangle/vertex adjacency, compute connected components, then keep the component with the greatest geometric extent (typically volume or triangle count as requested)
- For triangle-based volume, use simple helper functions for cross/dot products and signed-volume accumulation in pure Python instead of `numpy`.
- Do not add or install external packages for basic STL parsing, connectivity, or volume math unless the task explicitly requires them and the environment already guarantees them.
- Prefer a short end-to-end script for multi-step tasks: load mesh -> isolate largest component if needed -> extract attribute/material ID -> read exact density entry -> compute outputs -> write required result file.
- Use manual STL parsing mainly when the task specifically requires byte-level extraction or when a mesh tool cannot expose the needed geometry/attributes.

- Check coordinate system units before multiplying volume × density
- Material lookup tables may be needed for density values; when they are, read the table early and resolve the exact parsed material ID against the source row before computing derived quantities.
- Test with sample file before processing full dataset


- Treat mass calculations as conditional: `mass = volume × density` only after units and density are both validated from provided inputs.
- For material tables, cite or extract the exact row used; do not infer unseen entries from partial output.
- Prefer source-driven lookup code over manual dictionaries when a task provides a density table file. Parse the provided table file and select the row matching the mesh's material ID instead of embedding `{id: density}` values by hand.
- Preserve task-defined STL attribute bytes through the workflow; if they encode Material ID or similar metadata, extract them from the mesh/component you actually measured and carry that exact value into lookup/output.
- A small bounding box or plausible size is not enough to prove units are mm vs cm; verify from metadata, documentation, or other explicit evidence.
- In final results, make numeric inputs traceable: state the material ID, confirmed density source/value, and whether unit evidence was established.
- Before writing any mass output, record a compact calculation trace: largest-component selection result, parsed material ID, exact density-table entry, unit status (`confirmed unit` or `file units only`), and the arithmetic used.
- If any link in that chain is missing, do not emit a definitive mass; report volume and the missing verification instead.

- Prefer a single reproducible scripted workflow for multi-step tasks (mesh analysis -> lookup -> calculation -> file output) so results are easy to verify.
- If a tool can directly return largest-component measurements and preserved STL attribute metadata, prefer that over reimplementing mesh connectivity from scratch.
- When helper scripts or domain utilities are present, inspect their expected inputs/outputs first so your workflow matches the task's intended mesh parsing and component-analysis path.
- When running helper scripts, try the provided interpreter directly; if `python` is unavailable, retry with `python3` before changing approach.## Tips

- Check coordinate system units before multiplying volume × density
- Material lookup tables may be needed for density values
- Test with sample file before processing full dataset


- Treat mass calculations as conditional: `mass = volume × density` only after units and density are both validated from provided inputs.
- For material tables, cite or extract the exact row used; do not infer unseen entries from partial output.
- Prefer source-driven lookup code over manual dictionaries when a task provides a density table file. Parse the provided table file and select the row matching the mesh's material ID instead of embedding `{id: density}` values by hand.
- A small bounding box or plausible size is not enough to prove units are mm vs cm; verify from metadata, documentation, or other explicit evidence.
- In final results, make numeric inputs traceable: state the material ID, confirmed density source/value, and whether unit evidence was established.
- Before writing any mass output, record a compact calculation trace: largest-component selection result, parsed material ID, exact density-table entry, unit status (`confirmed unit` or `file units only`), and the arithmetic used.
- If any link in that chain is missing, do not emit a definitive mass; report volume and the missing verification instead.

- Prefer a single reproducible scripted workflow for multi-step tasks (mesh analysis -> lookup -> calculation -> file output) so results are easy to verify.
- If a tool can directly return largest-component measurements and preserved STL attribute metadata, prefer that over reimplementing mesh connectivity from scratch.
- When running helper scripts, try the provided interpreter directly; if `python` is unavailable, retry with `python3` before changing approach.

## Verification Checklist

- Confirm any requested connected-component step was implemented from geometric adjacency, not metadata grouping or label aggregation.
- If a lookup file was long or truncated, confirm the exact material-ID row/key was re-read or searched and is visible in the evidence used.
- Before giving a final mass, verify that both the exact unit evidence and the exact density-table row are present in the observed inputs. If either is missing, stop short of a definitive mass.
- Confirm any lookup table values came from a direct read/search of the referenced source file, not a manually reconstructed subset or hard-coded dictionary.
- If multiple unit interpretations produce different physical answers, do not finalize one without explicit evidence resolving the units.
- If reporting mass, explicitly state the evidence for mesh length units; otherwise report only file-unit geometry and note that mass remains unverified.
- Verify the final numeric result is reproducible from logged intermediate values, not just stated in the output artifact.
- Confirm the solution does not depend on avoidable third-party packages for basic geometry or parsing.
- Check whether the task provides a helper script or existing tool that should be used instead of custom parsing.
- If the task requires a file output or JSON report, write exactly the requested path and schema; do not add extra keys or prose.
- If you wrote an output file, read it back and confirm the serialization is well-formed and the values/keys exactly match the intended final answer.

## Verification Checklist

- Confirm the material/attribute value came from the parsed mesh, not an assumption.
- Confirm the density or other reference value was explicitly read for that exact ID/key.
- Show or compute the arithmetic used for derived outputs, including any unit conversion.
- If the task specifies a required output schema, follow it exactly.