---
name: threejs-part-exporter
description: "Parse a Three.js scene, group meshes by nearest named THREE.Group, and export individual and merged part OBJ files."
---

# Three.js Part Mesh Exporter

Extract part-level structure from a Three.js scene by treating named THREE.Group nodes as parts, assign meshes to their nearest named parent, and export:
- individual meshes (with world transforms baked) into part-specific folders
- merged part meshes into a links directory

Use this skill when you need a reproducible workflow to inspect a Three.js scene, discover its parts, and save geometry to OBJ for downstream use.

## When to Use
- A project provides a createScene (or equivalent) function that builds a Three.js scene in Node.js.
- You need to organize meshes by logical parts (named groups) and export geometry to OBJ.
- You must bake hierarchical transforms so exported geometry matches world-space placement.

## Core Workflow

1) Prepare the environment
- Ensure Node.js supports ES modules (either set "type": "module" in package.json or use .mjs for scripts).
- Install three and ensure examples are available (OBJExporter):
  - Import path: three/examples/jsm/exporters/OBJExporter.js

2) Load the scene
- Dynamically import the scene module (e.g., ./data/object.js).
- Obtain a factory function (e.g., createScene) and build the root Object3D or Scene.
- Call updateWorldMatrix(true, true) on the root before traversal.

3) Identify parts and assign meshes
- Treat every named THREE.Group (excluding the root if it represents the whole model) as a part.
- For each mesh (THREE.Mesh or THREE.SkinnedMesh), find its nearest named ancestor group; assign the mesh to that part.
- This nearest-named-parent rule keeps nested structures correct without double-counting.

4) Export geometry
- For each part:
  - Individual meshes: bake the mesh's world transform into its geometry (apply matrixWorld to a cloned BufferGeometry), then export to OBJ as part_meshes/<part>/<mesh>.obj.
  - Link (merged) mesh: collect all descendant meshes of the part, bake each to world space, add to a temporary group, and export a single OBJ to links/<part>.obj.
- Sanitize file/folder names; handle unnamed/duplicate meshes by generating safe unique names.

5) Directory layout
- out/
  - part_meshes/
    - <part_name>/
      - <mesh_name>.obj
  - links/
    - <part_name>.obj

## Verification
- Inspect the output tree to confirm expected parts and meshes are present.
- Open a sample of exported OBJs in a viewer and confirm:
  - geometry appears in world-space positions (not clustered at the origin)
  - merged part OBJs visually match the corresponding scene subassembly
- Sanity checks:
  - the number of exported meshes roughly matches the count of meshes found during traversal
  - no unexpected overwrites (duplicate names should be disambiguated)

## Common Pitfalls (and Fixes)
- ES module errors (Cannot use import statement outside a module):
  - Add "type": "module" to package.json or use a .mjs script.
- Wrong OBJExporter import path:
  - Use three/examples/jsm/exporters/OBJExporter.js (not addons or non-jsm paths).
- Incorrect transforms (OBJs at origin or wrong scale):
  - Always updateWorldMatrix(true, true) before traversal and bake matrixWorld into geometry (BufferGeometry.applyMatrix4).
- Missing nested meshes:
  - Do not filter only for direct children; traverse all descendants and assign meshes by nearest named ancestor.
- Overwriting files or invalid filenames:
  - Sanitize names and disambiguate duplicates by appending counters.
- Exporting invisible or helper objects:
  - Optionally skip child.visible === false or non-Mesh nodes.

## Success Criteria
- Every named group (intended as a part) has a corresponding links/<part>.obj.
- Every mesh is exported once into the folder of its nearest named parent part under part_meshes/.
- Exported geometry reflects world-space placement from the original scene.

## Optional Script Usage
A generic Node.js script is provided (scripts/export_three_parts.mjs).

Example:
- Ensure dependencies: npm i three
- Ensure ESM: add "type": "module" to package.json or run the .mjs script directly.
- Run:
  node scripts/export_three_parts.mjs \
    --scene ./data/object.js \
    --fn createScene \
    --out ./output \
    --include-root=false

Arguments:
- --scene: path to the module exporting a scene factory function
- --fn: name of the exported factory function (default: createScene)
- --out: output directory (default: ./output)
- --include-root: export unassigned meshes under a root_unassigned part (default: false)
