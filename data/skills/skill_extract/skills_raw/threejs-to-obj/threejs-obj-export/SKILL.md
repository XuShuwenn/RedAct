---
name: threejs-obj-export
description: "Export Three.js scenes to Blender-ready OBJ by baking world transforms, expanding instanced meshes, and applying a -90° X rotation to convert to Z-up."
---

# Three.js to OBJ (Blender Z-up) Export

Reusable workflow to export a Three.js scene/object to Wavefront OBJ that imports cleanly into Blender's Z-up coordinate system. It bakes all world transforms into geometry and expands InstancedMesh objects so the OBJ contains actual mesh data for every visible instance.

## When to Use

Use this skill when you need to:
- Convert a Three.js scene or object into a single OBJ file for DCC tools (Blender, etc.)
- Preserve exact world-space positions and orientations
- Handle InstancedMesh by expanding instances into real meshes
- Convert from Three.js Y-up to Blender Z-up by applying a -90° rotation around X

## Core Workflow

1. Inspect how the scene/object is exported.
   - Identify a factory function that returns the root Object3D (e.g., `createScene`, `buildScene`) or a directly exported `scene`.
   - Confirm the code uses ES modules or run the exporter script with an `.mjs` extension or a project configured with `"type": "module"`.

2. Load the scene and update transforms.
   - Import the scene module and obtain the root Object3D.
   - Call `root.updateMatrixWorld(true)` to ensure `matrixWorld` values are current.

3. Expand InstancedMesh objects.
   - For each `InstancedMesh`, iterate its instances and create a separate mesh per instance.
   - Compute the combined transform as: `combined = rootInstance.matrixWorld * instanceMatrix`.

4. Bake transforms into geometry.
   - For each (expanded) mesh, clone its BufferGeometry and apply the mesh's world matrix.
   - Apply a -90° rotation around X to convert to Blender Z-up: `R_x(-π/2) * worldMatrix`.
   - Avoid relying on parent/group transforms—they are not represented in OBJ and will be lost if not baked.

5. Export with OBJExporter.
   - Build a new export root that contains only meshes with identity transforms and already-baked geometry.
   - Use `OBJExporter().parse(exportRoot)` to obtain the OBJ string and write it to disk.

6. Save and verify.
   - Ensure the output directory exists.
   - Verify the OBJ has non-zero counts of vertices (`v`) and faces (`f`), and that object names (`o`) are present.
   - Optionally import into Blender to confirm Z-up orientation.

## Verification

- Structural checks:
  - File exists and is non-empty.
  - `v` (vertices) and `f` (faces) counts are greater than zero.
  - `o` (object) lines appear if you expect multiple sub-meshes.
- Coordinate conversion sanity:
  - After applying -90° X rotation, the former Y-up axis should map to Z-up in Blender. If your model had a clear up direction, confirm it appears upright in Blender.
- Instance expansion:
  - If the source used InstancedMesh, ensure the expected number of instances appear as actual geometry (counts or object names).

## Common Pitfalls and How to Avoid Them

1. InstancedMesh not expanded → Missing geometry in OBJ
   - OBJ has no instancing. Always expand `InstancedMesh` into individual meshes before export.

2. Not calling `updateMatrixWorld(true)` → Stale transforms baked into geometry
   - Always update matrices before reading `matrixWorld`.

3. Relying on scene/group transforms → Incorrect positions in OBJ
   - OBJ has no parent transforms. Bake world transforms into geometry for every mesh.

4. Double-applying Z-up rotation → Wrong orientation
   - Apply -90° X rotation exactly once during baking. Avoid both wrapping the scene and re-applying per mesh.

5. Merging all geometries indiscriminately → Lost object names/material groups
   - Keep meshes separate unless a specific merge-by-material is intended. This preserves object names and grouping.

6. Module system mismatch (ESM vs CJS) → Import errors
   - Use `.mjs` for the exporter or set `"type": "module"` in `package.json`. Import `OBJExporter` from `three/examples/jsm/exporters/OBJExporter.js`.

7. Ignoring normals after negative scale or complex transforms → Shading artifacts
   - After baking transforms, compute vertex normals if they are missing or obviously incorrect.

## Success Criteria

- OBJ imports into Blender upright in Z-up orientation.
- All expected scene parts are present with correct positions and scales.
- Instanced geometry appears as real meshes (no missing components).
- Reasonable counts of `v` and `f` lines; meshes carry meaningful object names.

## Optional Script Usage

This repository provides a generic exporter you can reuse:

- Inputs:
  - `--entry <path>`: Path to the ES module that exposes the scene/object.
  - `--factory <name>` (optional): Exported function to call that returns an Object3D.
    - If omitted, the script tries common names like `createScene`, `buildScene`, etc., or uses an exported `scene`/default.
  - `--out <path>`: Destination OBJ file path.
  - `--no-z-up` (optional): Skip the -90° X rotation if you do not want Z-up conversion.

Example:
- `node scripts/export_three_to_obj.mjs --entry ./data/object.js --factory createScene --out ./output/object.obj`

To verify the output quickly:
- `python3 scripts/obj_stats.py ./output/object.obj`
- Review counts for vertices, normals, faces, and objects.
