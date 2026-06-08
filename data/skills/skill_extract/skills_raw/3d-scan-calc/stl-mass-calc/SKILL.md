---
name: stl-mass-calc
description: "Compute the mass of the largest connected component in a binary STL where the 2-byte attribute field stores a material ID, using a Markdown density table."
---

# STL Mass Calculation from Material ID

Determine the mass of a 3D part from a binary STL by isolating the largest connected component, extracting its Material ID from the 2-byte attribute field of each triangle, looking up density from a Markdown table, and computing mass = volume × density.

## When to Use

Use this skill when you have:
- A binary STL where the 2-byte Attribute Byte Count is repurposed to encode a Material ID.
- A Markdown table mapping material IDs to densities (e.g., g/cm³).
- A need to filter scanning debris by selecting the largest connected mesh component and compute its mass.

## Core Principles

- Parse the STL deterministically (binary, little-endian). The 2-byte attribute after each triangle encodes Material ID.
- Identify connected components by triangle adjacency via shared vertices (with tolerance to account for duplicate vertex coordinates).
- Compute enclosed volume robustly via signed tetrahedra and use the absolute value for mass.
- Trust the units of the volume produced by your analyzer. Do not add conversions unless you computed volume from raw coordinates and know the coordinate units.
- Perform density lookup from the provided table, not from memory, and keep full precision until the final rounding step.

## Core Workflow

1) Parse Binary STL
- Structure per triangle: 12 floats (normal + 3 vertices, 48 bytes) followed by a 2-byte unsigned integer attribute (Material ID). All fields are little-endian.
- Read triangles sequentially. Store for each triangle:
  - Its 3 vertices (float triplets)
  - The Material ID (uint16)

2) Build Connected Components
- Two triangles are considered adjacent if they share any vertex index.
- Create a vertex index by spatial hashing of coordinates with a small tolerance (e.g., a grid based on 1e-6 of the model size) to collapse duplicate float vertices.
- For component labeling:
  - Build a mapping from vertex index → list of triangle indices.
  - BFS/DFS from each unvisited triangle; neighbors are all triangles touching any of its vertices.
  - Record the set of triangles per component.

3) Volume Calculation
- For each triangle with vertices a, b, c (3D vectors), accumulate signed volume using: V += dot(a, cross(b, c)) / 6.
- The component volume is the absolute value of the sum over its triangles. Use double precision and avoid early rounding.
- Select the largest component by volume (not triangle count) to robustly filter debris.

4) Component Material ID
- Compute the mode (most frequent) Material ID across triangles in the largest component.
- If multiple IDs are present, report the distribution; default to the majority ID and note the assumption.

5) Density Lookup (Markdown table)
- Parse the Markdown to map material_id → density (numeric).
- Be tolerant to formatting: capture integer IDs and floating-point densities from pipe-delimited rows. Ignore header/separator lines.
- Confirm the units (e.g., g/cm³) from the table or task context.

6) Units and Mass Computation
- If using a trusted mesh tool that reports volume with units, use those units directly without additional conversion.
- If you computed volume from STL coordinates, choose a unit assumption, then convert to match the density’s units:
  - If coordinates are millimeters (common for STL), convert mm³ to cm³ by dividing by 1000.
  - If coordinates are centimeters, use volume as-is for g/cm³.
  - Document the assumption and justify it (e.g., by bounding box magnitude).
- Mass = volume_in_density_units × density. Keep full precision internally; round only in the final output.

7) Output
- Write JSON with keys:
  - main_part_mass: numeric mass (rounded at the end to the required precision)
  - material_id: integer Material ID used for density lookup

## Verification

- Connectivity sanity:
  - Number of components ≥ 1 and the largest has much higher volume than others (debris). If not, review tolerance or adjacency criterion.
- Volume sanity:
  - Non-zero, positive volume for the main component; absolute of signed sum.
  - Bounding box scale consistent with your unit assumption (e.g., mm-scale parts typically have dimensions in the tens to hundreds).
- Material-database integrity:
  - The selected material ID exists in the density table.
  - Parsed density is numeric and in expected units.
- Unit consistency:
  - If you did not compute the volume yourself, do not apply extra conversions. If you did, explicitly convert to match the density’s unit system.
- Output validation:
  - JSON parses successfully and contains both required keys.
  - Maintain sufficient precision to meet accuracy requirements; avoid early rounding.

## Common Pitfalls

- Misinterpreting the attribute field:
  - The 2-byte attribute is a uint16 Material ID here, not color or unused. Read as little-endian unsigned short per triangle.
- Unit confusion:
  - Double-applying unit conversions (e.g., dividing by 1000 when your analyzer already returned cm³) produces a 1000× error.
  - Failing to convert mm³ to cm³ when computing volume from raw mm coordinates.
- Over-fragmented components:
  - Using exact float comparison for vertices splits a single part into many components. Use spatial hashing with tolerance for vertex deduplication.
- Rounding too early:
  - Rounding the volume or density before multiplying can push you outside tight accuracy thresholds. Round only the final mass.
- Hardcoding densities:
  - Values drift from the provided table or change across tasks. Always parse or reference the given table.

## Optional Script Usage

A helper script is provided to parse the STL, isolate the largest component, extract its Material ID, parse a Markdown density table, and output the mass JSON.

Example:
- Compute mass, assuming the volume you compute is already in cm³ (default):
  python3 scripts/stl_mass_tool.py --stl path/to/model.stl --density-table materials.md --out mass_report.json

- If you know the STL coordinates are millimeters and you computed volume from coordinates:
  python3 scripts/stl_mass_tool.py --stl path/to/model.stl --density-table materials.md --out mass_report.json --assume-units mm

The script prints basic diagnostics and writes the requested JSON.
