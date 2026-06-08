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

### Environment protocol is mandatory

- Before the first tool call, identify the exact tool/action schema required by the current environment and use it verbatim for every step; do **not** substitute another tool syntax, wrapper, or message format.
- Use only the tool names and argument schema explicitly available in the current environment. Do **not** invent or assume alternate tools from other environments.
- Treat protocol requirements as hard constraints equal in importance to the export task itself.
- If the task requires an exact completion token/string, end with that exact token and nothing else when the task is complete.


- Read enough of `/root/data/object.js` to see the real `createScene()` hierarchy and relevant helper definitions before naming parts or summarizing structure. If an initial read is truncated, continue reading or parse the full file.
- Base extraction on observed source code or safe runtime traversal only. Do **not** guess structure from a partial snippet or recreate a presumed equivalent scene from memory.
- When feasible, prefer evaluating/importing the provided scene and traversing the constructed Three.js scene graph to derive parts, meshes, and nested groups; use raw source parsing mainly to locate `createScene()` and understand helper construction.
- Do not describe the model, part names, or mesh counts until a full read/parse of the relevant scene-construction code or an equivalent verified runtime traversal provides direct evidence.
- Write files only in task-authorized locations. Do not create helper scripts, temp files, or exports outside permitted directories.
- Treat writable-path authorization conservatively: only create helper scripts, temp files, and outputs in directories the task explicitly authorizes. Do **not** assume `/root/` itself is writable just because `/root/data/` is readable.
- Before creating any helper artifact, confirm the destination path is explicitly allowed; if not clearly allowed, do not write there.
- If helper code is necessary, place it under a task-authorized writable directory such as `/root/output/`; do **not** write convenience scripts to locations like `/root/`.
- Use `/root/data/object.js` directly for static parsing or runtime traversal; do **not** recreate, replace, or hand-author a substitute `createScene()` from memory, guesses, or partial evidence.
- Follow any task- or environment-specific execution protocol exactly. If the task mandates a tool-call schema, response format, observation loop, allowed tool set, or exact completion token/string, use that contract verbatim from start to finish.
- Treat the environment/task interaction contract as a hard constraint, not a suggestion: before the first action, identify the exact allowed tool/action interface, required tool-call schema, observation loop, any todo/task-state requirements, and any exact final completion token/string, then follow that contract literally for every step.
- Read the task instructions and any referenced instruction source as authoritative requirements separate from `object.js`; do **not** infer the full deliverable only from the scene file when the task specifies an output schema, required checks, allowed tools, or a final completion string.
- Do **not** substitute alternate tool wrappers, XML-style tags, markdown pseudo-calls, unsupported tool names, or freeform prose actions when the environment requires a stricter schema.
- For every tool invocation, supply executable content only: shell tools must receive literal runnable commands, and file-write tools must receive the exact file contents to write.
- When invoking a shell-capable tool, provide concrete executable commands and arguments, not descriptive placeholders such as "inspect the file" or "run the export script".
- Prefer portable verification commands such as `find`, `ls -R`, `test`, `stat`, `head`, `grep`, and `wc -l`; if an optional utility like `tree` is unavailable, switch to those alternatives instead of skipping verification.
- If a planned verification command is unavailable or fails, switch to an equivalent concrete check and reduce confidence to match what was actually verified.
- If the environment requires an exact completion string, make the final message exactly that string and nothing else after it unless the instructions explicitly allow extra commentary.
- In the final response, claim only properties directly supported by source reads, runtime traversal, filesystem inspection, file-content inspection, or explicit counting commands.
- Before designing export logic, inspect any existing helper scripts or task-provided utilities that already traverse/export the scene, and reuse their conventions when they fit the requested output.
- If helper code is necessary, run it inline when possible or write it only under a task-authorized writable location such as `/root/output/`; never stage scripts or temp files in `/root/` or other unauthorized paths.
- When writing a helper script, config, or output file, write the literal intended file contents: real executable code or real data, not placeholders, TODOs, summaries, or prose descriptions of intended behavior.
- Immediately inspect the saved file contents directly and run a syntax check or execution test before relying on it.
- Before committing to a runtime/export pipeline, do a minimal environment check for required modules and helpers (for example `three`, `OBJExporter`, or any geometry-combination utility you plan to use), and check the scene file's module/dependency setup (for example `package.json`, ESM vs CommonJS expectations, and required imports) so you choose an implementation that matches verified availability.
- Before writing or executing any helper script, verify the target directory actually exists and is task-authorized, and prefer placing the script inside the project/working tree or another confirmed writable location that shares the needed dependency context.
- For Node-based helpers, choose an execution location where package resolution is verified to work for required imports such as `three`; do not assume unrelated temporary directories will resolve project dependencies.
- If you generate a helper script, immediately inspect the saved file and run a syntax check before executing it; fix any quoting/template corruption before relying on the script.
- For any helper script or generated exporter that is central to success, do not rely only on a description of what you intended to write. Re-open or print the saved file content and verify the key logic is actually present before execution; then syntax-check/run it and confirm the observed behavior matches the task requirements.
- Treat truncated reads of `/root/data/object.js`, partial command output, incomplete logs, or cut-off directory listings as incomplete evidence. Continue reading or rerun narrower checks until the scene logic, filenames, and results are unambiguous.
- Do not name parts, assign counts, branch on presumed scene-specific labels, or describe hierarchy until the relevant scene-construction code or runtime graph directly supports those claims.

## Output Structure

**Operational checklist before exporting:**
- Confirm any required action/response protocol from the task/environment and follow it exactly for every step.
- Use concrete executable shell commands for directory creation, inspection, counting, and previews.
- If you create a helper script, verify the saved file contains executable code before running it.

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
- Verify each required output tree explicitly. Do not infer that `part_meshes/` exists just because `links/` exists, or vice versa; run separate targeted checks when needed.
- Do **not** report directories, files, or counts that were not directly shown by the filesystem output you observed.
- Do not report success unless the filesystem shows the expected directories and files for all extracted parts.

## Approach

1. Read and inspect the full relevant contents of `object.js`, including `createScene()` and related helper code, before naming parts or describing hierarchy
   - Before this, read the full task instruction and any referenced files/prompts that define the requested deliverable, required tool protocol, and final response/completion token.
   - Evidence gate: if you have only seen headers, imports, helper functions, an initial fragment, or a truncated read, you do **not** yet have enough evidence to state concrete part names, hierarchy, counts, or scene-specific export logic. Continue reading/searching until the actual scene-building code is visible or confirm structure by verified runtime traversal first.
   - If the environment requires a strict action/observation format, keep every tool invocation and the final completion message in that exact format; procedural noncompliance is a task failure even if exports are correct.
   - If any file read or search output is truncated or only shows imports/comments/helpers, continue with narrower reads/searches until the hierarchy-construction logic you rely on is actually visible.
   - Do not state scene type, part names, mesh counts, or likely structure until that inspection or an equivalent verified runtime traversal has produced direct evidence.
2. Confirm the runtime/export path before scripting: verify the needed Three.js runtime pieces and exporter/helper modules are present if you plan to evaluate the scene, export OBJ, or combine geometry
   - Also verify the script location itself before execution: confirm the directory exists, is writable, and will run with the intended module-resolution context.
   - When checking the environment, use explicit shell commands such as `ls`, `find`, `cat`, `node -e`, or `grep` with concrete paths and arguments; avoid descriptive pseudo-commands.
   - If dependencies are installed relative to the working area, run the helper from that context rather than from unrelated temporary directories.
   - If you need to edit package, config, or script files, read the exact lines first, then apply a targeted change against the observed text.
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
   - After writing any helper script, inspect the saved file contents directly to confirm it contains executable code rather than notes, placeholders, or a truncated write.
   - If you write a helper script, the file contents must be actual Node.js/JavaScript source code, not a summary such as "created a Node.js export script...".
   - Self-check before execution: every shell invocation must be a concrete command with actual arguments/paths, and every generated script file must contain runnable code rather than narrative text.
   - After writing the script, immediately verify with a concrete check such as `sed -n '1,80p' <script>` or `node --check <script>` before executing it.
   - If an export step fails with an API/runtime error, do **not** summarize success until you have rerun the corrected workflow and verified the resulting files with explicit filesystem checks.
   - Prefer runtime traversal of the built scene or direct source parsing over handwritten reconstruction.
   - If combining meshes for a part-level OBJ, use a valid utility or traversal-based export path; do not rely on unsupported APIs such as `BufferGeometry.merge(...)`.
10. Before finalizing, verify the export command or script actually finished and build a complete inventory of discovered parts and meshes from full source inspection or runtime traversal
   - Treat a truncated log, failed command, ambiguous output, or unavailable utility as **non-evidence**. For batch exports, do not infer completion from a partial console log or the intention to implement a script; confirm the process exited successfully and, if needed, replace ambiguous output with valid concrete checks such as `find`, `ls`, targeted `test -f`, or exit-status inspection.
11. Verify the exported outputs against that inventory by direct filesystem inspection: confirm `/root/output/part_meshes/` and `/root/output/links/` both exist, every discovered part has its directory and `links/<part_name>.obj`, nested-group meshes were written under their parent part directory, no unauthorized extra subgroup directories were created under `part_meshes/`, and every discovered mesh/part is represented by the files actually written without omissions or unintended duplication
   - Do not stop after a top-level listing or one sample part folder. Run targeted per-part checks or structured summaries so no directory listing you rely on is truncated, inspect all discovered part directories, confirm every expected `links/<part_name>.obj`, and compare actual file counts against the traversal inventory before claiming completion.
   - Use non-truncated, targeted checks to support each claim, for example `find /root/output/part_meshes -maxdepth 2 -type f | sort`, `find /root/output/links -maxdepth 1 -type f | sort`, and representative `wc`/`head` checks on OBJ files.
   - Do **not** claim completion from partial listings, truncated console output, or script success messages alone.
12. If any read, listing, export log, or verification output is truncated or ambiguous, rerun narrower checks for specific directories, filenames, counts, or exit status until every claimed artifact is directly observed; otherwise report the missing or unverified artifacts instead of claiming completion
   - Before the final response, explicitly confirm both: (a) the primary export step exited cleanly or otherwise finished without ambiguity, and (b) filesystem checks match the claimed outputs. Never infer completion from a partial console log alone.
   - Never treat `head`, clipped recursive listings, or cut-off command output as full verification of all parts.
   - Prefer portable verification commands that return complete evidence, including explicit `wc -l` counts when reporting totals.
   - If command output is too long and becomes truncated, rerun narrower checks per part or directory, or use a short script to emit structured counts and filenames; never extrapolate totals from cut-off output.
   - Do **not** report exact file counts, exact filenames, or successful completion unless those details are supported by complete, non-truncated command output or targeted follow-up checks.
   - Keep the final report strictly tied to observed evidence: if logs only confirm some parts, some counts, or sample files, say exactly that and avoid inferring unobserved totals or success for the unseen remainder.
13. Before declaring success, confirm both sides of the evidence chain:
   - source evidence: the full relevant `createScene()` / helper construction logic was actually read or equivalently verified by runtime traversal
   - output evidence: the written files match that confirmed inventory of parts and meshes
   - Do **not** declare completion from sampled folders, partial reads, or file counts alone.
14. Before the final response, run a brief compliance check: required tool-call schema followed throughout the run, any helper scripts executed from verified locations, and the exact required completion string present with no accidental omission or paraphrase

15. Report part names, counts, and hierarchy details only when they were directly confirmed from source inspection, runtime traversal, or checked filesystem results, and if the task specifies an exact completion token or final-response format, output it exactly
16. Before each tool call, confirm the call uses the exact action protocol required by the environment and that the payload contains concrete executable content rather than a natural-language description of intent
17. After verification, summarize results at the same granularity as the evidence collected; if some checks were substituted, partial, or failed, state that limitation explicitly instead of implying full verification

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

- Before concluding anything about hierarchy, confirm you have actually read the relevant `createScene()` construction code or traversed the built scene; a filename, header comment, or first few lines are not enough.
- When reporting final totals, tie each number to observed evidence: a traversal inventory or explicit filesystem count command.


## Mandatory Final Checklist

- Confirm you fully inspected the relevant `object.js` / helper code or performed an equivalent verified runtime traversal; if any earlier read was truncated, finish reading before implementing.
- Confirm your tool usage and final response exactly match any task-specific action schema and completion token.
- Confirm the main export command completed cleanly, not just partially.
- Confirm `/root/output/part_meshes/` exists and contains per-part mesh OBJ files.
- Confirm `/root/output/links/` exists and contains one part-level OBJ per extracted part.
- Do not claim any hierarchy detail, count, filename, or output path that you did not directly observe.