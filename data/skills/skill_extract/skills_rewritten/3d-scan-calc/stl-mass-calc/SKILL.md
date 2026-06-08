---
name: stl-mass-calc
description: "Compute the mass of a 3D part by parsing a binary STL that stores Material ID in the 2-byte attribute field, isolating the largest connected component, mapping density from a reference, and performing correct unit conversions."
---

# STL Mass Calculation from Material-ID-Encoded Binary STL

This skill computes the mass of a 3D printed/scanned part from a binary STL where each triangle's 2-byte "Attribute Byte Count" stores a Material ID. It:
- parses the binary STL,
- identifies connected components and selects the largest,
- extracts the predominant Material ID for that component,
- looks up density from a reference table,
- computes mass with correct unit conversions,
- writes a JSON report with the mass and material ID.

## When to Use

Use this skill when you need to compute the mass of a part from a binary STL that encodes Material ID in the per-triangle attribute bytes and a separate table maps Material IDs to densities.

## Inputs and Assumptions

- Binary STL with per-triangle 2-byte attribute field storing Material ID (little-endian unsigned short).
- A density reference file (e.g., Markdown table) mapping Material ID to density values and units.
- STL coordinates are in a single unit system (e.g., mm, cm, m). Default assumption: millimeters.
- Density units are typically g/cm^3 or kg/m^3. Default expectation: g/cm^3.

## Core Workflow

1. Parse the Binary STL
   - Read 80-byte header, then 4-byte little-endian uint for triangle count.
   - For each triangle, read normal (3 floats), vertices (9 floats), and the 2-byte attribute field.
   - Interpret the 2-byte attribute field as Material ID (little-endian unsigned short).

2. Build Connectivity and Find the Largest Component
   - Deduplicate vertices using coordinate quantization to a tolerance (e.g., 1e-5 of STL unit) to get stable vertex IDs.
   - Represent each triangle by its three vertex IDs.
   - Build a mapping from vertex ID to incident triangles, then perform a BFS/DFS over triangle adjacency (sharing at least one vertex) to cluster triangles into connected components.
   - For each component, compute volume and track its triangles' material IDs.
   - Select the component with the largest absolute volume.

3. Determine the Component's Material ID
   - Compute the mode (most frequent) Material ID across triangles in the largest component.
   - If there are multiple IDs with similar frequency, log a warning and pick the majority; if extremely mixed, verify whether the part is truly single-material or if preprocessing is needed.

4. Volume Calculation
   - For each triangle (a, b, c), compute signed tetrahedral volume with origin: V_tri = dot(a, cross(b, c)) / 6.
   - Sum over triangles in the component and take absolute value for component volume.
   - If the mesh is open (non-watertight), volume may be unreliable. Check boundary edges and warn if many are unpaired.

5. Density Lookup
   - Parse the density reference to map Material ID to density and units.
   - Accept common Markdown table formats and tolerate extra columns or spacing.
   - If the density unit is missing, require an override flag or default to g/cm^3 only if this is consistent with expected results.

6. Unit Conversion and Mass Calculation
   - Convert volume from STL units to units consistent with the density:
     - If STL units = mm and density = g/cm^3: volume_cm3 = volume_mm3 / 1000.
     - If STL units = cm and density = g/cm^3: volume_cm3 = volume_cm3.
     - If STL units = m and density = kg/m^3: volume_m3 = volume_m3.
     - If density = kg/m^3 and you want grams: mass_g = (volume_m3 * density_kg_m3) * 1000.
   - Compute mass = Volume × Density, output mass in grams by default.

7. Output
   - Write JSON with fields:
     - main_part_mass: numeric mass in grams (float)
     - material_id: integer Material ID

## Verification

Perform these checks to ensure correctness and avoid common failure modes:
- Geometry checks:
  - Largest component dominance: confirm its volume is significantly larger than the next largest (e.g., ratio > 10×). If not, re-examine connectivity tolerance.
  - Boundary edges: compute count of edges that belong to exactly one triangle. A high number suggests a leaky mesh; volume may be underestimated.
- Density and units checks:
  - Confirm density unit (g/cm^3 or kg/m^3) from the reference. If ambiguous, require an explicit flag.
  - Sanity range: compare mass to a rough bound from the component's bounding box volume × density; your result should be reasonably below this bound.
  - 10^3 factor trap: if your result seems plausible but differs from a rough expectation by exactly ~1000×, revisit conversions between mm^3↔cm^3 and g↔kg.
- Consistency checks:
  - Material ID consistency within the largest component: if the top Material ID accounts for <80% of triangles, flag a potential multi-material region.
  - Recompute volume with a tighter/looser vertex tolerance; the result should not change markedly for a clean mesh.

## Common Pitfalls and How to Avoid Them

- Unit mismatch leading to 1000× error:
  - Always reconcile STL length units with density volume units. Common case: STL in mm, density in g/cm^3 → divide volume by 1000 to convert mm^3 to cm^3.
  - If density is kg/m^3 and you report grams, multiply by 1000 at the end.
- Ignoring the attribute bytes:
  - The 2-byte attribute field is repurposed as Material ID. Do not assume it's unused; parse it as little-endian unsigned short for each triangle.
- Choosing the largest component by triangle count instead of volume:
  - Use computed volume, not triangle counts. Meshes with finer tessellation can have more triangles despite smaller size.
- Using triangle normals for orientation:
  - Normals can be unreliable. Use the signed tetrahedral volume method and take absolute value per component.
- Over- or under-merging components due to floating point noise:
  - Deduplicate vertices with a quantization tolerance. If components fragment, increase tolerance slightly; if dissimilar parts merge, decrease tolerance.
- Assuming watertightness:
  - If boundary edges are present, volume may be inaccurate. Consider repairing, or treat the result as an estimate with a caveat.

## Success Criteria

- Output JSON includes the keys "main_part_mass" (grams) and "material_id" (integer).
- Largest connected component is used.
- Material ID is derived from triangle attribute bytes (mode of the largest component's triangles).
- Unit conversions reflect STL units and density units consistently.
- Numerical result is within expected accuracy (e.g., within sub-percent when mesh is watertight).

## Optional Script Usage

A helper script is provided to run the full workflow.

Example usage:
- Compute mass assuming STL units are millimeters and density table uses g/cm^3:
  - python3 scripts/stl_mass_calc.py --stl /path/to/model.stl --density-table /path/to/material_density_table.md --out /path/to/mass_report.json
- If your density table uses kg/m^3 and your STL is in meters:
  - python3 scripts/stl_mass_calc.py --stl /path/to/model.stl --density-table /path/to/density.md --density-units kg/m3 --stl-units m --out /path/to/mass_report.json

The script prints a short summary and writes the final JSON report.
