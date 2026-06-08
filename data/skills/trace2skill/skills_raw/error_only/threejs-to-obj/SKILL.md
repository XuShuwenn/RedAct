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

## Inspect the Source First

- Read `/root/data/object.js` fully, or inspect all sections relevant to geometry construction, transforms, hierarchy, and faces/index data before deciding how to export.
- Do **not** infer object hierarchy, mesh types, or transform complexity from an initial snippet.
- If the file is long or an initial read is truncated, continue reading/searching systematically for geometry definitions, vertex arrays, face/index construction, and rotation/position/scale transforms before writing the exporter.

## Output

- `/root/output/object.obj`: Exported 3D object


## Execution Constraints

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
- If you need a helper script, place it only in an allowed directory, not in ad hoc top-level or input-data paths.
- Do not assume relative imports like `./data/object.js` unless they are correct from the helper script's actual location; use the provided absolute path when possible.
- Verify how the source can run under Node before writing the converter: check module format, exported entry points, and any browser-only assumptions.
- After writing a script, reopen/read it to confirm imports, file paths, rotation logic, and output path before executing it.
- Prefer exporting the existing scene or mesh hierarchy after applying the required rotation; avoid manual geometry merging unless the task explicitly requires it.
- For `THREE.InstancedMesh`, combine each instance matrix with the source object's own transform before reparenting/exporting; do not use `getMatrixAt()` alone as the final world transform.
- Verify representative world-space vertex/object positions after conversion when expanding instanced or nested objects.
- Validate the transform semantically, not just syntactically: confirm the export applies the required mapping (commonly `(x, y, z) -> (x, z, -y)`) to positions and corresponding normals if normals are written.
- Do not claim "all original positions preserved" or full scene coverage based only on successful OBJ output, file existence, or a partial source read.
- If the environment specifies an exact completion signal, output that exact string; a natural-language summary alone may not be sufficient.

