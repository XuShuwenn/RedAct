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
- Write files only in task-authorized locations. Do not create helper scripts, temp files, or exports outside permitted directories.

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
- Do **not** add extra subgroup folders under `part_meshes/` unless the task explicitly requests nested output.
- Preserve part-based top-level folders: meshes from nested subgroups should still be written under their parent part directory when the requested schema is flat per part.
- Under `links/`, create one part-level `.obj` file per extracted part, including parts defined by nested `THREE.Group` nodes.
- Each `links/<part_name>.obj` must represent the whole part/group, not a single representative child mesh.
- Do not report success unless the filesystem shows the expected directories and files for all extracted parts.

## Approach

1. Read and inspect the full relevant contents of `object.js`, including `createScene()` and related helper code, before naming parts or describing hierarchy
2. Parse the verified scene structure; do not infer hierarchy from imports, comments, or partial snippets
3. Enumerate all primitive-defined `THREE.Mesh` objects and all `THREE.Group` nodes actually created
4. Record each mesh and its parent group path; traverse groups recursively rather than checking only top-level children
5. Derive confirmed part names from the discovered hierarchy and map each mesh to its requested part output
6. Export individual meshes as OBJ under `/root/output/part_meshes/<part_name>/`
7. Create one part-level link OBJ per extracted part under `/root/output/links/`
8. If helper code is needed, keep it in an allowed output location
9. Before finalizing, verify the exported outputs against the parsed source structure: confirm both output trees exist, expected part directories were created, and discovered meshes/parts are represented by the files actually written

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
