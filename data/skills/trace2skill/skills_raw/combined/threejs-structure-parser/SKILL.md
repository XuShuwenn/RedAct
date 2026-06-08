---
name: threejs-structure-parser
description: "Parse Three.js object.js file to extract mesh hierarchy, part structure, and export individual part meshes as OBJ files."
---

# Three.js Structure Parser

## When to Use

- Parse Three.js scene definitions
- Extract part-level mesh structure
- Export individual meshes to OBJ format

## Input

- `/root/data/object.js`: Three.js file with `createScene()` function

### Mandatory parsing discipline

- Treat `/root/data/object.js` as the authoritative source for hierarchy, part names, and mesh counts.
- Read the full relevant `createScene()` / scene-construction code, or continue reading/searching until you can verify the complete scene-building logic, before naming parts, estimating counts, or designing export logic.
- Derive hierarchy only from `THREE.Group` / `THREE.Mesh` relationships actually observed in the source; do **not** infer structure from comments, imports, headers, partial snippets, or truncated output.


## Input

## Execution Guardrails

- Read enough of `/root/data/object.js` to see the real `createScene()` hierarchy and relevant helper definitions before naming parts or summarizing structure. If an initial read is truncated, continue reading or parse the full file.
- Base extraction on observed source code or safe runtime traversal only. Do **not** guess structure from a partial snippet or recreate a presumed equivalent scene from memory.
- When feasible, prefer evaluating/importing the provided scene and traversing the constructed Three.js scene graph to derive parts, meshes, and nested groups; use raw source parsing mainly to locate `createScene()` and understand helper construction.
- Do not describe the model, part names, or mesh counts until a full read/parse of the relevant scene-construction code or an equivalent verified runtime traversal provides direct evidence.
- Write files only in task-authorized locations. Do not create helper scripts, temp files, or exports outside permitted directories.
- Use `/root/data/object.js` directly for static parsing or runtime traversal; do **not** recreate, replace, or hand-author a substitute `createScene()` from memory, guesses, or partial evidence.
- Follow any task- or environment-specific execution protocol exactly. If the task mandates a tool-call schema, response format, observation loop, allowed tool set, or exact completion token/string, use that contract verbatim from start to finish.
- Before designing export logic, inspect any existing helper scripts or task-provided utilities that already traverse/export the scene, and reuse their conventions when they fit the requested output.
- If helper code is necessary, run it inline when possible or write it only under a task-authorized writable location such as `/root/output/`; never stage scripts or temp files in `/root/` or other unauthorized paths.
- Before committing to a runtime/export pipeline, do a minimal environment check for required modules and helpers (for example `three`, `OBJExporter`, or any geometry-combination utility you plan to use), and check the scene file's module/dependency setup (for example `package.json`, ESM vs CommonJS expectations, and required imports) so you choose an implementation that matches verified availability.
- If you generate a helper script, immediately inspect the saved file and run a syntax check before executing it; fix any quoting/template corruption before relying on the script.
- Treat truncated reads of `/root/data/object.js`, partial command output, incomplete logs, or cut-off directory listings as incomplete evidence. Continue reading or rerun narrower checks until the scene logic, filenames, and results are unambiguous.
- Do not name parts, assign counts, branch on presumed scene-specific labels, or describe hierarchy until the relevant scene-construction code or runtime graph directly supports those claims.

## Output Structure

```
/root/output/
├── part_meshes/
│   ├── <part_name_1>/
│   │   ├── <mesh_name1>.obj
│   │   └── ...
│   └── ...
└── links/
    ├── <part_name_1>.obj
    └── ...
```

**Path rule:** write mesh OBJs directly under `part_meshes/<part_name>/` and part-level combined files under `links/<part_name>.obj`.

Requirements for completion:
- Create both `/root/output/part_meshes/` and `/root/output/links/`.
- Under `part_meshes/`, create a directory for each extracted part and place that part's mesh OBJ files inside it.
- Choose the output directory from the resolved part name, not from each nested child group name.
- Flatten nested subgroup meshes into the owning part directory: write `part_meshes/<part_name>/<mesh_name>.obj`, not `part_meshes/<part_name>/<subgroup>/<mesh_name>.obj`.
- Do **not** create top-level folders like `/root/output/part_meshes/<nested_group_name>/` for subgroups that belong inside a parent part.
- Do **not** add extra subgroup folders under `part_meshes/` unless the task explicitly requests nested output.
- Preserve part-based top-level folders: meshes from nested subgroups should still be written under their parent part directory when the requested schema is flat per part.
- Under `links/`, create one part-level `.obj` file per extracted part, including parts defined by nested `THREE.Group` nodes.
- Each `links/<part_name>.obj` must represent the whole part/group, not a single representative child mesh.
- Before saving, map each discovered part to exactly two artifact patterns: `part_meshes/<part_name>/<mesh>.obj` and `links/<part_name>.obj`.
- Do not claim completion from a partial or truncated directory listing; use targeted checks to confirm exact filenames, per-part file counts, and the presence of each required `links/<part_name>.obj`.
- Do not report success unless the filesystem shows the expected directories and files for all extracted parts.

## Approach

1. Read and inspect the full relevant contents of `object.js`, including `createScene()` and related helper code, before naming parts or describing hierarchy
   - If any file read or search output is truncated or only shows imports/comments/helpers, continue with narrower reads/searches until the hierarchy-construction logic you rely on is actually visible.
   - Do not state scene type, part names, mesh counts, or likely structure until that inspection or an equivalent verified runtime traversal has produced direct evidence.
2. Confirm the runtime/export path before scripting: verify the needed Three.js runtime pieces and exporter/helper modules are present if you plan to evaluate the scene, export OBJ, or combine geometry
3. Prefer constructing/evaluating the provided scene and traversing the resulting object graph when feasible; otherwise parse the verified source without inferring from imports, comments, or partial snippets
4. Enumerate all actual `THREE.Mesh` objects and all `THREE.Group` nodes created in the verified scene
   - Treat every meaningful `THREE.Group` encountered during recursive traversal as a candidate part output unless the task explicitly limits the extraction level.
5. Record each mesh and its ancestor group path; traverse groups recursively rather than checking only top-level children
   - Include meshes found at any depth under a part, including meshes attached directly to deeper groups as well as meshes inside nested subgroups; do not rely on a fixed `children`/`grandchildren` depth.
   - When feasible, instantiate the scene and traverse the resulting object graph; treat named `THREE.Group` nodes as the primary part boundaries when present, and assign each mesh to its nearest named ancestor group unless the task specifies a different partitioning rule.
6. Derive confirmed part names from the discovered hierarchy and map each mesh to its requested part output
   - Treat nested named groups as separate part boundaries so meshes owned by a nested named group are exported with that nested part instead of also being double-counted under the parent.
   - Before exporting, make a concrete inventory of confirmed parts, groups, and meshes from source inspection or safe runtime traversal, and reuse that same grouping inventory for both `part_meshes/` and `links/` outputs.
   - Drive exports from the discovered traversal inventory itself; do not hard-code expected group names, prefixes, or scene-specific labels unless they are directly confirmed in the source.
7. Export individual meshes as OBJ under `/root/output/part_meshes/<part_name>/`, calling `updateMatrixWorld(true)` first and cloning/applying each mesh's `matrixWorld` so standalone exports preserve assembled-scene placement and orientation
8. Create one part-level link OBJ per extracted part under `/root/output/links/` by exporting/combining the whole part/group in world space, not just a representative child mesh
9. If helper code is needed, first confirm the module-loading setup required to execute `object.js` correctly, then keep any script in an allowed location; prefer one reproducible load → traverse → export workflow when feasible instead of separate ad hoc steps
   - Prefer runtime traversal of the built scene or direct source parsing over handwritten reconstruction.
   - If combining meshes for a part-level OBJ, use a valid utility or traversal-based export path; do not rely on unsupported APIs such as `BufferGeometry.merge(...)`.
10. Before finalizing, verify the export command or script actually finished and build a complete inventory of discovered parts and meshes from full source inspection or runtime traversal
11. Verify the exported outputs against that inventory by direct filesystem inspection: confirm `/root/output/part_meshes/` and `/root/output/links/` both exist, every discovered part has its directory and `links/<part_name>.obj`, nested-group meshes were written under their parent part directory, no unauthorized extra subgroup directories were created under `part_meshes/`, and every discovered mesh/part is represented by the files actually written without omissions or unintended duplication
12. If any read, listing, export log, or verification output is truncated or ambiguous, rerun narrower checks for specific directories, filenames, counts, or exit status until every claimed artifact is directly observed; otherwise report the missing or unverified artifacts instead of claiming completion
13. Report part names, counts, and hierarchy details only when they were directly confirmed from source inspection, runtime traversal, or checked filesystem results, and if the task specifies an exact completion token or final-response format, output it exactly

## Three.js Components

- Mesh objects: Mesh with geometry + material
- Groups: THREE.Group containing multiple meshes
- Geometry types: Box, Sphere, Cylinder, etc.

## Tips

- Use Node.js to parse JavaScript
- Extract mesh names and parent groups
- Export OBJ with proper formatting
- Maintain hierarchy relationships


- Extract parts generically from observed `THREE.Group` / `THREE.Mesh` relationships; do not hardcode scene-specific labels unless they are directly present in the source.
- Do not stop at root children: nested `THREE.Group` nodes may also define meaningful parts and must be considered during traversal.
- Prefer importing/evaluating the provided scene file and traversing the resulting object graph when feasible.
- If a part is a group of meshes, export by traversing child meshes and writing them individually or by using a valid geometry-combination utility; do not call nonexistent methods like `BufferGeometry.merge(...)`.
- Do not implement `links/<part_name>.obj` by exporting only the first mesh you encounter; export the entire part/group object.
- Before claiming success, build a complete inventory of discovered groups/meshes and verify exports semantically, not just by file existence or script logs.
- If file reads, command output, or listings are truncated, rerun with narrower checks or structured summaries instead of assuming traversal completed.
- Report counts, filenames, and hierarchy details only when they were directly confirmed from source inspection or filesystem output.

- If an initial file read shows only imports, helpers, or a truncated snippet, continue reading or evaluate/traverse the scene before naming parts; partial headers are not evidence of hierarchy.
- Prefer runtime scene-graph traversal when possible: instantiate `createScene()`, call `updateMatrixWorld(true)`, and inspect named groups instead of relying only on static parsing.
- Separate evidence gathering from conclusions: first collect confirmed groups/meshes, then derive part names and counts from that inventory.
- A reliable default for part assignment is to use named `THREE.Group` nodes as part units and assign each mesh to its nearest named ancestor group unless the source shows a different explicit rule.
- Validate outputs in layers: confirm both top-level output trees exist, then inspect representative `links/<part>.obj` files and representative mesh OBJ files inside `part_meshes/<part>/`, and confirm counts from the filesystem itself (`find`, `ls -R`) rather than relying only on console success output or script logs.
