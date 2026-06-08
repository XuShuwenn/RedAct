---
name: 3d-scan-calc
description: "Analyze 3D mesh files to calculate geometric properties (volume, components) and extract attribute data from STL files."
---

# 3D Scan Calculation

## When to Use

- Calculate volume of complex or noisy 3D meshes
- Filter debris from scan data by isolating largest component
- Extract metadata (material IDs) stored in binary STL files

## Basic Workflow

1. Parse the STL file (binary format)
2. Identify connected components
   - Build components from mesh connectivity (shared vertices/edges between triangles), not from material IDs, colors, or other metadata labels
   - If asked for the main part, select the largest geometric connected component after connectivity analysis
3. Extract geometric properties (volume) and attributes
4. Compute derived values (mass = volume × density)


5. Before mass calculation, verify two prerequisites: (a) the exact material-ID-to-density row was explicitly retrieved, and (b) any unit conversion is supported by explicit evidence.
6. If either prerequisite is missing, stop short of a definitive mass claim and state what remains unverified.
7. Verify the full chain before final output: selected component -> material ID -> density lookup -> unit assumptions/conversion -> final arithmetic.

## Important Notes

- STL attribute bytes may store metadata (material ID, color)
- Volume units depend on STL coordinate system - verify before computing

- Do not assume STL units by convention alone. If units are not stated in metadata, task text, or accompanying documentation, report geometric results in file units (for example, volume in file-units^3) rather than silently converting.
- If density is given in a fixed unit system (for example `g/cm^3`), only convert mesh volume when the mesh length unit is supported by explicit evidence.
- If multiple unit interpretations remain plausible and would produce materially different masses, do not choose one arbitrarily; keep investigating or report the ambiguity.
- Filter out noise/debris by keeping largest connected component

- Do not treat material ID groups as connected components unless the task explicitly defines components that way.
- When a task provides an external material-density table or lookup file, treat that file as the source of truth: read/parse it directly, verify the exact material ID entry, and do not hard-code or infer mappings from partial previews.
- If a lookup table or sidecar-file read is truncated or partial, re-read or search for the exact material ID/key before using the value.

## Common Patterns

- Binary STL parsing (2-byte attribute at end of each triangle)
- Connected component analysis for noise filtering
- Volume calculation from mesh geometry


- For debris filtering: construct triangle/vertex adjacency, compute connected components, then keep the component with the greatest geometric extent (typically volume or triangle count as requested)
- For triangle-based volume, use simple helper functions for cross/dot products and signed-volume accumulation in pure Python instead of `numpy` unless external packages are explicitly required or already guaranteed.

## Tips

- Check coordinate system units before multiplying volume × density
- Material lookup tables may be needed for density values
- Test with sample file before processing full dataset


- Treat mass calculations as conditional: `mass = volume × density` only after units and density are both validated from provided inputs.
- For material tables, cite or extract the exact row used; do not infer unseen entries from partial output.
- A small bounding box or plausible size is not enough to prove units are mm vs cm; verify from metadata, documentation, or other explicit evidence.
- In final results, make numeric inputs traceable: state the material ID, confirmed density source/value, and whether unit evidence was established.

## Verification Checklist

- Confirm the material/attribute value came from the parsed mesh, not an assumption.
- Confirm the density or other reference value was explicitly read for that exact ID/key.
- Show or compute the arithmetic used for derived outputs, including any unit conversion.
- If the task specifies a required output schema, follow it exactly.