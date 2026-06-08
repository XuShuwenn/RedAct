---
name: threejs-to-obj
description: "Convert Three.js 3D object to OBJ format with Blender Z-up coordinate system (-90° X rotation)."
---

# Three.js to OBJ Conversion

## When to Use

- Export Three.js scenes to OBJ format
- Convert to Blender-compatible 3D files
- Apply coordinate system transformations

## Input

- `/root/data/object.js`: Three.js file with well-built 3D object


- Treat `/root/data` as read-only unless the task explicitly allows edits; place helper scripts, temporary files, and all outputs outside the input directory when possible.



## Inspect the Source First

- Treat initial reads as provisional only. If the visible content is truncated, incomplete, or ends mid-structure, continue reading/searching until you have enough evidence for geometry construction, hierarchy, transforms, and any export-affecting code paths.
- Do not design the export pipeline, write the converter, or claim support for hierarchy/instancing/transform cases until you have inspected enough of `/root/data/object.js` to see the relevant scene structure.
- Do **not** claim you understand or exported the full scene from a snippet; stop and inspect more before designing the exporter if you have not seen the relevant geometry-bearing portions of the file.

## Inspect the Source First

- Read `/root/data/object.js` fully, or inspect all sections relevant to geometry construction, transforms, hierarchy, and faces/index data before deciding how to export.
- Do **not** infer object hierarchy, mesh types, or transform complexity from an initial snippet.
- If the file is long or an initial read is truncated, continue reading/searching systematically for geometry definitions, vertex arrays, face/index construction, and rotation/position/scale transforms before writing the exporter.

## Output

- `/root/output/object.obj`: Exported 3D object


## Execution Constraints

- Before changing the environment or writing integration code, inspect existing project/runtime configuration (for example `package.json`, module type, existing `three` dependency/layout, and nearby helper scripts) and reuse it when possible.
- For nontrivial scenes or runtime-built geometry, prefer a small dedicated export script over manual reconstruction or ad hoc shell transformations.
- Do a lightweight preflight before execution: confirm the expected runtime/module format and whether required dependencies and actual `three` / examples paths are already available before inventing setup steps or guessing imports.

## Execution Constraints

- Follow the invoking task/runtime protocol exactly. If a specific tool/action syntax, wrapper, or exact completion marker is required, use that exact format instead of any default style.
- Read and write only within paths explicitly allowed by the task. This applies to final outputs, helper scripts, and temporary/intermediate artifacts.
- Prefer task-provided absolute paths over inferred relative paths for inputs, outputs, and imports; for this skill, write directly to `/root/output/object.obj` unless the task explicitly permits alternatives.
- Minimize filesystem changes. Write only the requested deliverable unless the task explicitly authorizes additional files.
- Do not create `package.json`, install packages, or otherwise modify the environment unless a concrete missing dependency or runtime error shows it is necessary.

## Key Requirements

1. Keep all original 3D positions
2. Apply -90 degree X rotation (Blender Z-up space)
3. Export in OBJ format


4. Apply the coordinate conversion exactly once
5. Validate transform preservation before claiming success, especially for scene-graph rewrites
6. Validate the exported geometry semantically, not just by file existence or line counts


7. For hierarchical scenes, preserve final placement by exporting each mesh with its effective transform applied exactly once, whether via a single export-root rotation or by baking world-space transforms into cloned geometry
8. When a baked transform has a negative determinant (mirrored scale), correct face winding and normals so surfaces do not export inside-out

9. If the scene uses constructs OBJ cannot represent directly (especially `THREE.InstancedMesh`), expand them into explicit meshes/geometry before writing OBJ

Preferred default for complex scenes: update world matrices, traverse meshes, clone geometry, bake each mesh's effective world transform exactly once into the clone, then apply the one-time Blender `-90°` X conversion in that same export path.



## Coordinate Transform

Blender Z-up: Apply rotation matrix
```
x' = x
y' = z
z' = -y  (or similar based on rotation)
```


**Important:** choose one transform path only:
- **Geometry-space:** rotate vertex positions/normals before writing OBJ
- **Object/world-space:** keep geometry unchanged and export using the object's effective transform once

Do **not** do both. Wrong: rotating `geometry` and also setting a root/object rotation of `-90°` around X. Apply the Blender Z-up conversion in one place only.


## OBJ Format

```
v x y z           # vertices
vn nx ny nz       # normals
f v1/vt1/vn1 ...  # faces
```


## Validation

- If command output or file previews are abbreviated, read back enough of the generated OBJ and any relevant script sections to support your claims.
- Cross-check success claims against observable evidence: verify that execution actually occurred and that outputs contain the expected data before claiming export success.
- For every nontrivial claim you plan to report (for example transform baking, instance expansion, hierarchy preservation, mirrored-scale correction, or normals handling), perform a matching check; otherwise do not claim it.
- Base the final report only on properties directly supported by inspected source, inspected generated files, and concrete command output from this run. Separate "implemented," "verified," and "assumed"; only present verified details as confirmed.
- Confirm compliance with task protocol before declaring success: required tool syntax was followed, all file operations stayed within authorized paths, and any exact completion marker is emitted exactly as specified.

## Validation

Before declaring success, verify task-critical properties, not just file existence:

- Confirm the OBJ covers the geometry-bearing parts found in `/root/data/object.js`.
- Spot-check representative source vertex/transform values and confirm the exported coordinates match the required `-90°` X rotation.
- Confirm the conversion is implemented exactly once, not in both geometry data and object/root transforms.
- If normals are written, rotate/check them consistently with the vertex transform.
- If faces or indices are emitted, confirm their indexing/counts are consistent with the parsed geometry.
- Use file counts or presence of `v`/`f` lines only as sanity checks; they are not sufficient evidence of correctness by themselves.
- Report conservatively: claim only what you actually verified from the source and output.

## Tips

- Parse Three.js geometry objects
- Apply transformation matrix
- Write OBJ with proper indices
- Handle both vertices and faces


- Prefer zero-setup execution and direct conversion to `/root/output/object.obj`; avoid extra artifacts unless explicitly allowed.
- Prefer inline execution or ephemeral commands when possible so the only persisted artifact is `/root/output/object.obj`.
- If execution appears to require environment setup, first try a no-install path that uses already-available tooling or a standalone helper script. Only add setup steps when a concrete runtime error proves they are necessary and the task permits them.
- If you need a helper script, place it only in an allowed directory, not in ad hoc top-level or input-data paths.
- When direct one-liners would be brittle, prefer a small dedicated conversion script in an allowed writable location so loading, transform baking, and OBJ serialization are reproducible and auditable.
- Do not assume relative imports like `./data/object.js` unless they are correct from the helper script's actual location; use the provided absolute path when possible.
- Before writing a converter, inspect how the source runs: check module format, exported entry points, browser-only assumptions, and nearby config such as `package.json` for module type and whether `three` is already available.
- Match the script to the detected runtime first; avoid guessing CommonJS vs ESM imports or package layout.
- Before importing Three.js helper/exporter modules (for example `OBJExporter`), inspect the installed package layout and import from the actual available path instead of assuming package-root exports.
- After writing a script, reopen/read it to confirm imports, file paths, rotation logic, and output path before executing it.
- Never write placeholder prose such as "add dependencies" or "write exporter here" into task-critical files. Write actual executable content only.
- When writing a helper script via shell, use a method that makes the content recoverable in the transcript (for example a heredoc in the command) or immediately read the file back through the allowed interface before execution.
- Never assume a script write succeeded from intent alone: inspect the saved file contents and confirm it contains runnable code, not placeholder prose or truncated text, before running it or describing what it does.
- If a file-write output is truncated, abbreviated, or otherwise not fully visible, treat the write as unverified and read the file back before execution.
- Prefer exporting the existing scene or mesh hierarchy after applying the required rotation; avoid manual geometry merging unless the task explicitly requires it.
- When the source is executable scene code, obtain the scene/mesh by running that code and export the resulting hierarchy rather than re-deriving vertices/faces by hand.
- Preferred default for executable scene code: run the source, obtain the resulting scene/mesh hierarchy, call `scene.updateMatrixWorld(true)`, then bake each mesh's effective world transform into cloned geometry before writing OBJ.
- If the repository or nearby files already include a working export/helper script, inspect and adapt that pattern before building a new exporter from scratch.

- Before writing a custom exporter, check whether the environment already has the needed runtime pieces (for example `three`, `OBJExporter`, or geometry utilities) and prefer those proven components over re-implementing OBJ serialization from scratch.
- When the source is module-driven scene code, prefer reusing an existing helper-script pattern for module loading and output writing (for example `pathToFileURL`-based loading) instead of inventing a new execution path.
- Before implementation, confirm the intended OBJ exporter/helper actually exists in the environment and inspect its callable interface plus any object-type limitations.
- If the exporter does not support a scene construct used by the source (for example `THREE.InstancedMesh`), normalize that construct into supported ordinary meshes before export rather than dropping it or guessing support.
- Reliable default workflow for flat OBJ export: inspect runtime setup first, apply the one-time Blender `-90°` X conversion in the chosen export path, call `scene.updateMatrixWorld(true)`, traverse meshes, clone each geometry, bake each mesh's `matrixWorld` into the clone, then serialize faces from the transformed clone.
- Inspect the exporter implementation or documentation before assuming it handles the source scene's object types; if it does not support a runtime construct directly, replace unsupported constructs with equivalent standard `Mesh` nodes before export instead of dropping them.
- For `THREE.InstancedMesh`, expand each instance into standalone exported geometry or ordinary `THREE.Mesh` objects by combining the object's `matrixWorld` with each `getMatrixAt()` result; do not treat the instance matrix alone as the final transform.
- If a mesh or subtree has mirrored/negative scale, detect the negative determinant and flip face winding (and normals, if written) after baking transforms.
- Keep the axis conversion explicit in the chosen export pipeline, and verify representative coordinates after export.
- For `THREE.InstancedMesh`, combine each instance matrix with the source object's own transform before reparenting/exporting; do not use `getMatrixAt()` alone as the final world transform.
- Verify representative world-space vertex/object positions after conversion when expanding instanced or nested objects.
- Validate the transform semantically, not just syntactically: confirm the export applies the required mapping (commonly `(x, y, z) -> (x, z, -y)`) to positions and corresponding normals if normals are written.
- Do not claim "all original positions preserved" or full scene coverage based only on successful OBJ output, file existence, or a partial source read.
- If the environment specifies an exact completion signal, output that exact string; a natural-language summary alone may not be sufficient.

- If you create a conversion script, make it auditable: either include the exact code in the work log or immediately reopen the saved file and inspect the critical parts (imports, input/output paths, axis conversion, transform application, OBJ writing) before running it.
- Do not treat `ls`, file existence, or the presence of `v`/`f` lines as proof that the export is correct; those are only sanity checks unless you also verify the required axis/transform behavior.

- Prefer the baked-world-transform workflow for grouped, nested, or procedural scenes because it preserves authored placement in flat OBJ output without relying on parent transforms at import time.
- Before choosing `OBJExporter` or another built-in exporter, inspect whether it supports all scene object types you found; if not, replace unsupported constructs with equivalent standard meshes or serialize them yourself rather than dropping them.
- For `THREE.InstancedMesh`, expand each instance into standalone exported geometry or ordinary `THREE.Mesh` objects by combining the object's `matrixWorld` with each `getMatrixAt()` result; do not treat the instance matrix alone as the final transform.
- When validating an instancing rewrite, check for evidence of the expanded instances in the OBJ (for example expected object/group names, counts, or representative transformed coordinates), not just overall geometry presence.
- Preserve a simple evidence trail: identify one representative source-space position or vertex, state the expected Blender-mapped value, then read back the OBJ to confirm the exported coordinates follow that mapping.

