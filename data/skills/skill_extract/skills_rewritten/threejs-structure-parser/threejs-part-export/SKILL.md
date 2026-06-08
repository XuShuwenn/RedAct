---
name: threejs-part-export
description: "Parse a Three.js scene to identify part-level groups and export both per-part (links) OBJs and per-mesh OBJs with world transforms applied."
---

# Three.js Part-Level Mesh Export

Export part-level groups and individual meshes from a Three.js scene as OBJ files. This workflow identifies parts as named THREE.Group containers (and assigns ungrouped meshes to a fallback part) and writes:
- one merged OBJ per part (links)
- one OBJ per individual mesh within each part (part_meshes)

Results have world transforms baked into geometry to preserve placement.

## When to Use

Use this skill when you need to:
- parse a Three.js file defining a scene via a function (e.g., createScene)
- discover the part hierarchy (named groups) and meshes
- export OBJ files per part and per mesh in an organized directory structure

## Core Workflow

1) Inspect the scene module
- Open the Three.js source to locate the function that constructs the scene (commonly createScene). Confirm it returns a THREE.Scene or an object containing one.
- Check how parts are labeled: named THREE.Group nodes typically indicate parts.

2) Verify environment and module setup
- Ensure Node.js can run ES modules. Prefer scripts with the .mjs extension.
- Ensure the project can import Three.js and the OBJ exporter:
  - Dependency: three
  - Import path: three/examples/jsm/exporters/OBJExporter.js
- If your scene source uses ES module syntax, set the package to ESM (e.g., package.json "type": "module") or adapt the loader to match the module type.

3) Define part identification rules
- A part is any named THREE.Group. All meshes beneath that group belong to the part.
- Meshes without a named-group ancestor are assigned to a fallback part (e.g., "root").
- Optionally exclude a purely container root group if it has no direct meshes and only contains other named groups.

4) Traverse, bake transforms, and export
- Load the scene and call scene.updateMatrixWorld(true) before traversal.
- For per-mesh export:
  - For each mesh, clone its geometry, apply mesh.matrixWorld to the clone, create a temporary mesh with identity transform, and export it alone.
- For per-part (link) export:
  - Collect all meshes in the part; create a temporary group and add baked clones (geometry with matrixWorld applied) for each; export the group as a single OBJ.
- Sanitize file and folder names. Provide stable fallbacks for unnamed nodes and deduplicate within a folder.
- Create output directories recursively.

5) Organize outputs
- links/<part_name>.obj → the merged/baked OBJ for each part
- part_meshes/<part_name>/<mesh_name>.obj → individual baked OBJs per mesh in that part

## Verification

Perform these checks after export:
- Structure:
  - The links folder contains one OBJ per identified part.
  - The part_meshes folder contains a subfolder per part with one OBJ per mesh.
- Content sanity:
  - OBJ files are non-empty and contain vertex lines (lines starting with "v ").
  - A mesh OBJ and its part OBJ share consistent relative placement (baked world coordinates).
- Cardinality:
  - Count of links equals count of named groups (plus optional fallback part if ungrouped meshes exist).
  - Spot-check that duplicate mesh names in the same part were deduplicated (e.g., suffixes) and not overwritten.
- Names and transforms:
  - Filenames are filesystem-safe (no illegal characters).
  - The scene graph was updated (matrixWorld applied) before baking.

## Common Pitfalls

- Module import errors:
  - Cause: Running ESM import in CommonJS context or vice versa.
  - Fix: Use .mjs for scripts and set package.json "type": "module" when needed, or adapt imports accordingly.

- Missing OBJ exporter:
  - Cause: Not importing from three/examples/jsm/exporters/OBJExporter.js.
  - Fix: Install three, import OBJExporter from the examples path.

- Unbaked transforms (misplaced meshes):
  - Cause: Exporting without applying matrixWorld to geometry.
  - Fix: scene.updateMatrixWorld(true) then geometry.clone().applyMatrix4(mesh.matrixWorld) for each exported mesh.

- Mutating original geometry:
  - Cause: Applying transforms directly to the original geometry.
  - Fix: Always clone geometry before applying transforms.

- Name collisions and invalid filenames:
  - Cause: Unnamed meshes/groups or repeated names.
  - Fix: Sanitize names and ensure uniqueness within a directory (suffix duplicates).

- Skipping nested parts or ungrouped meshes:
  - Cause: Assuming only top-level groups or ignoring meshes without named ancestors.
  - Fix: Traverse the full graph; bucket meshes by nearest named-group ancestor; assign others to a fallback part.

## Optional Script Usage

A generic Node.js ESM script is provided to load a scene module, identify parts, and export OBJs.

Example usage:
- node scripts/export_scene_parts.mjs \
  --input ./path/to/scene_module.mjs \
  --func createScene \
  --linksOut ./output/links \
  --meshesOut ./output/part_meshes \
  --includeRoot false

Arguments:
- --input: Path to the module that constructs the scene.
- --func: Name of the exported function that returns a Scene (default: createScene). If the default export is that function, you can still pass the name.
- --linksOut: Output directory for per-part OBJs.
- --meshesOut: Output directory for per-mesh OBJs.
- --includeRoot: Whether to treat the top-level container group as a part if named (true/false; default false).

Success criteria: After running, the links directory contains one OBJ per part; the part_meshes directory contains a subfolder per part with OBJ files for each mesh; files are non-empty and reflect world-space placement.
