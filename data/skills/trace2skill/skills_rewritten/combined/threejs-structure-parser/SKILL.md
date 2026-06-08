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

**Protocol preflight before any substantive action:**
- Read the full task instruction and any referenced instruction source before designing the export workflow from `object.js`.
- Identify the exact required action/tool wrapper and field schema, any required observation loop, any required todo/task-state workflow, the allowed tool name(s), any path requirements such as absolute-path-only commands, and any exact required completion token/string for the current environment.
- Use that exact interface exclusively for the entire run; do **not** switch to XML-style tags, markdown pseudo-calls, invented tool names, alternate wrappers, or freeform narrative actions.
- If only one tool (for example `bash`) is explicitly established, assume only that tool is available and perform reads, writes, edits, listings, and execution through it unless the environment explicitly adds more tools.
- Treat protocol drift as a hard failure: if a planned call does not exactly match the required schema, correct it before continuing.
- If the environment requires a todo/task tracker, create a real multi-step plan before substantive work and keep it updated through source inspection, export approach selection, export execution, verification, and finalization.
- Plan concrete executable verification checks in advance (`find`, `ls`, `test`, `wc -l`, targeted `head`) and do not rely on placeholder commands, optional missing tools, or truncated listings.
- If the environment requires an exact completion signal, reserve the final message for that exact string only unless the instructions explicitly allow extra text.


- Before the first tool call, identify the exact tool/action schema required by the current environment and use it verbatim for every step; do **not** substitute another tool syntax, wrapper, or message format.
- Use only the tool names and argument schema explicitly available in the current environment. Do **not** invent or assume alternate tools from other environments.
- Treat protocol requirements as hard constraints equal in importance to the export task itself.
- If the task requires an exact completion token/string, end with that exact token and nothing else when the task is complete.


- Read enough of `/root/data/object.js` to see the real `createScene()` hierarchy and relevant helper definitions before naming parts or summarizing structure. If an initial read is truncated, continue reading or parse the full file.
- Base extraction on observed source code or safe runtime traversal only. Do **not** guess structure from a partial snippet or recreate a presumed equivalent scene from memory.
- When feasible, prefer evaluating/importing the provided scene and traversing the constructed Three.js scene graph to derive parts, meshes, and nested groups; use raw source parsing mainly to locate `createScene()` and understand helper construction.
- Do not describe the model, part names, or mesh counts until a full read/parse of the relevant scene-construction code or an equivalent verified runtime traversal provides direct evidence.
- Write files only in task-authorized locations. Do not create helper scripts, temp files, or exports outside permitted directories.

- When the task or environment requires absolute paths, use concrete authorized absolute paths in tool calls, shell commands, and script invocations; do not use relative paths, placeholders, or implied locations.
- Hard rule: never create helper files in convenient but unauthorized locations such as `/root/extract_meshes.js`; use only explicitly permitted output/work directories.
- If a needed path is not explicitly known, resolve it first from observed filesystem evidence before proceeding.

- Treat writable-path authorization conservatively: only create helper scripts, temp files, and outputs in directories the task explicitly authorizes. Do **not** assume `/root/` itself is writable just because `/root/data/` is readable.
- Before creating any helper artifact, confirm the destination path is explicitly allowed; if not clearly allowed, do not write there.

- If you need a helper script and only `/root/output/` is clearly writable, place it there rather than in `/root/` or guessed convenience locations.

- If helper code is necessary, place it under a task-authorized writable directory such as `/root/output/`; do **not** write convenience scripts to locations like `/root/`.
- Use `/root/data/object.js` directly for static parsing or runtime traversal; do **not** recreate, replace, or hand-author a substitute `createScene()` from memory, guesses, or partial evidence.
- Follow any task- or environment-specific execution protocol exactly. If the task mandates a tool-call schema, response format, observation loop, allowed tool set, or exact completion token/string, use that contract verbatim from start to finish.
- Treat the environment/task interaction contract as a hard constraint, not a suggestion: before the first action, identify the exact allowed tool/action interface, required tool-call schema, observation loop, any todo/task-state requirements, and any exact final completion token/string, then follow that contract literally for every step.
- Read the task instructions and any referenced instruction source as authoritative requirements separate from `object.js`; do **not** infer the full deliverable only from the scene file when the task specifies an output schema, required checks, allowed tools, or a final completion string.
- Do **not** substitute alternate tool wrappers, XML-style tags, markdown pseudo-calls, unsupported tool names, or freeform prose actions when the environment requires a stricter schema.
- For every tool invocation, supply executable content only: shell tools must receive literal runnable commands, and file-write tools must receive the exact file contents to write.

- Shell payloads must be copy-pastable terminal commands with exact binaries, paths, and arguments. Never send intent text or placeholders like `check modules`, `create output folders`, `run export script`, or `count generated OBJ files` as if they were commands.
- Bad shell payloads: `inspect project files`, `run extraction script`, `inspect the output directory structure`.
- Good shell payloads: `mkdir -p /root/output/part_meshes /root/output/links`, `find /root/data -maxdepth 2 -type f | sort`, `node /root/output/extract_meshes.js`, `find /root/output -maxdepth 3 -type f | sort`.
- Bad file-write payloads: summaries such as `created a script that loads the scene...` or placeholder replacements like `existing package content` -> `updated package content`.
- Good file-write payloads: the full literal script/code or the exact observed text replacement.
- If you need to modify an existing file, first read the exact relevant lines, then edit against the observed text; do not use placeholder anchors such as `existing import block` or `existing config`.

- When invoking a shell-capable tool, provide concrete executable commands and arguments, not descriptive placeholders such as "inspect the file" or "run the export script".
- Prefer portable verification commands such as `find`, `ls -R`, `test`, `stat`, `head`, `grep`, and `wc -l`; if an optional utility like `tree` is unavailable, switch to those alternatives instead of skipping verification.
- If a planned verification command is unavailable or fails, switch to an equivalent concrete check and reduce confidence to match what was actually verified.
- If the environment requires an exact completion string, make the final message exactly that string and nothing else after it unless the instructions explicitly allow extra commentary.
- In the final response, claim only properties directly supported by source reads, runtime traversal, filesystem inspection, file-content inspection, or explicit counting commands.
- Before designing export logic, inspect any existing helper scripts or task-provided utilities that already traverse/export the scene, and reuse their conventions when they fit the requested output.
- If helper code is necessary, run it inline when possible or write it only under a task-authorized writable location such as `/root/output/`; never stage scripts or temp files in `/root/` or other unauthorized paths.
- When writing a helper script, config, or output file, write the literal intended file contents: real executable code or real data, not placeholders, TODOs, summaries, or prose descriptions of intended behavior.

- A file-creation step is not evidence of implementation unless the saved content itself contains the needed code/data. After writing or editing, immediately reopen or print the file, confirm the key logic is present, and run a syntax check or execution test before relying on it.
- Do **not** delete a generated helper/export script before final verification and task completion; keep it in an authorized location until outputs are fully checked.

- Immediately inspect the saved file contents directly and run a syntax check or execution test before relying on it.
- Before committing to a runtime/export pipeline, do a minimal environment check for required modules and helpers (for example `three`, `OBJExporter`, or any geometry-combination utility you plan to use), and check the scene file's module/dependency setup (for example `package.json`, ESM vs CommonJS expectations, and required imports) so you choose an implementation that matches verified availability.
- Before writing or executing any helper script, verify the target directory actually exists and is task-authorized, and prefer placing the script inside the project/working tree or another confirmed writable location that shares the needed dependency context.
- For Node-based helpers, choose an execution location where package resolution is verified to work for required imports such as `three`; do not assume unrelated temporary directories will resolve project dependencies.
- If you generate a helper script, immediately inspect the saved file and run a syntax check before executing it; fix any quoting/template corruption before relying on the script.
- For any helper script or generated exporter that is central to success, do not rely only on a description of what you intended to write. Re-open or print the saved file content and verify the key logic is actually present before execution; then syntax-check/run it and confirm the observed behavior matches the task requirements.
- Treat truncated reads of `/root/data/object.js`, partial command output, incomplete logs, or cut-off directory listings as incomplete evidence. Continue reading or rerun narrower checks until the scene logic, filenames, and results are unambiguous.
- Do not name parts, assign counts, branch on presumed scene-specific labels, or describe hierarchy until the relevant scene-construction code or runtime graph directly supports those claims.

- Before designing a new exporter/parsing workflow, inspect any existing skill docs, task-provided utilities, or exporter scripts in the workspace and reuse/adapt them when they match the requested output.
- Validate both the runtime environment and the input file shape before coding: inspect dependency/module setup (for example `package.json`, installed `three`, exporter helpers, ESM vs CommonJS) and inspect `/root/data/object.js` so the implementation matches the verified scene/module format.


## Output Structure

**Operational checklist before exporting:**

- Inspect any existing helper/export scripts before designing a new exporter so you can reuse a verified mechanism when it fits the task.
- Verify `three` and any export/combine helpers you will use are actually available before scripting.
- Run a minimal runtime import check for the libraries/exporters you plan to use before investing in a larger script.
- Prefer one traversal-based exporter script that produces both `part_meshes/` and `links/` from the same confirmed grouping inventory.
- After execution, verify completion from the filesystem, not from script logs alone.

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

- If any listing is clipped by `head`, console limits, or long output truncation, rerun narrower checks per directory/part until every claimed artifact is directly shown.
- Treat partial samples as partial evidence only; do not upgrade them into a full-success claim.
- Minimum verification before claiming completion: inspect both top-level trees, enumerate all part directories, enumerate all `links/*.obj` files, and compare those results against the confirmed traversal/source inventory.
- Do **not** extrapolate from one sample part folder to all other parts.
- Verification must go beyond folder existence: inspect complete non-truncated file listings for all discovered parts, and inspect representative OBJ contents (for example with `head`/`wc`) before claiming success.

- Verify each required output tree explicitly. Do not infer that `part_meshes/` exists just because `links/` exists, or vice versa; run separate targeted checks when needed.
- Do **not** report directories, files, or counts that were not directly shown by the filesystem output you observed.
- Do not report success unless the filesystem shows the expected directories and files for all extracted parts.

## Approach

1. Read and inspect the full relevant contents of `object.js`, including `createScene()` and related helper code, before naming parts or describing hierarchy

   - Also inspect any local skill docs, task-provided helper scripts, or existing exporter utilities before implementing so you can reuse established traversal, loading, and OBJ-writing patterns instead of inventing a fresh pipeline.
   - Protocol gate before any action: identify the exact allowed tool names, invocation wrapper, and final completion string from the environment instructions before doing implementation work.
   - Minimum evidence rule: seeing only the file header, imports, helper declarations, comments, `head`, or an initial short snippet is **not** enough to claim you understand the scene. Continue reading/searching until the actual scene-construction logic is visible, or verify the structure by runtime traversal.
   - Anti-premature-conclusion check: if the visible content is only early lines or helper code, treat scene identity, part names, hierarchy, and mesh counts as unknown until further evidence is collected.

   - Before this, read the full task instruction and any referenced files/prompts that define the requested deliverable, required tool protocol, and final response/completion token.
   - Evidence gate: if you have only seen headers, imports, helper functions, an initial fragment, or a truncated read, you do **not** yet have enough evidence to state concrete part names, hierarchy, counts, or scene-specific export logic. Continue reading/searching until the actual scene-building code is visible or confirm structure by verified runtime traversal first.
   - If the environment requires a strict action/observation format, keep every tool invocation and the final completion message in that exact format; procedural noncompliance is a task failure even if exports are correct.
   - If any file read or search output is truncated or only shows imports/comments/helpers, continue with narrower reads/searches until the hierarchy-construction logic you rely on is actually visible.
   - Do not state scene type, part names, mesh counts, or likely structure until that inspection or an equivalent verified runtime traversal has produced direct evidence.
2. Confirm the runtime/export path before scripting: verify the needed Three.js runtime pieces and exporter/helper modules are present if you plan to evaluate the scene, export OBJ, or combine geometry
   - First check whether the workspace already contains a task-specific exporter, traversal utility, or prior skill asset you can adapt; prefer extending a verified existing pattern over rebuilding the workflow from scratch when it already matches the task.
   - Proven preflight sequence: inspect `package.json` or equivalent project metadata, verify Node.js and the `three` package, then confirm any exporter/utilities you plan to use (for example `OBJExporter` or geometry-combination helpers) actually exist before writing the exporter script.
   - Match the helper script's module style to the verified project/runtime setup before execution. If the exporter uses `import` syntax, confirm the environment is configured for ESM; if the project is CommonJS, use a compatible loading approach instead of assuming imports will run.
   - Before writing or executing a helper script, verify the exact script directory exists and is task-authorized; do not assume locations like `/root/tmp` or `/tmp` are valid.
   - For Node helpers, prefer an execution location inside the verified project/working tree where dependency resolution for packages such as `three` is confirmed to work.
   - Start with a minimal smoke test before writing a full exporter: verify the exact imports you need load successfully in the intended runtime/module mode.
   - Let verified module availability determine the implementation; do not start coding against unconfirmed helpers or APIs.

   - Also verify the script location itself before execution: confirm the directory exists, is writable, and will run with the intended module-resolution context.
   - When checking the environment, use explicit shell commands such as `ls`, `find`, `cat`, `node -e`, or `grep` with concrete paths and arguments; avoid descriptive pseudo-commands.
   - If dependencies are installed relative to the working area, run the helper from that context rather than from unrelated temporary directories.
   - If you need to edit package, config, or script files, read the exact lines first, then apply a targeted change against the observed text.
3. Prefer constructing/evaluating the provided scene and traversing the resulting object graph when feasible; otherwise parse the verified source without inferring from imports, comments, or partial snippets
4. Enumerate all actual `THREE.Mesh` objects and all `THREE.Group` nodes created in the verified scene
   - Treat every meaningful `THREE.Group` encountered during recursive traversal as a candidate part output unless the task explicitly limits the extraction level.
5. Record each mesh and its ancestor group path; traverse groups recursively rather than checking only top-level children

   - Success pattern to preserve: use named parent `THREE.Group` nodes as the default logical part boundaries when the scene hierarchy supports it.

   - Include meshes found at any depth under a part, including meshes attached directly to deeper groups as well as meshes inside nested subgroups; do not rely on a fixed `children`/`grandchildren` depth.
   - When feasible, instantiate the scene and traverse the resulting object graph; treat named `THREE.Group` nodes as the primary part boundaries when present, and assign each mesh to its nearest named ancestor group unless the task specifies a different partitioning rule.
6. Derive confirmed part names from the discovered hierarchy and map each mesh to its requested part output

   - Favor semantically named `THREE.Group` nodes discovered in the source/runtime traversal as the default part boundaries when they provide useful part-level organization.
   - Keep one authoritative inventory of `{part_name -> meshes[]}` derived from that hierarchy, and drive both granular mesh exports and part-level `links/<part_name>.obj` exports from the same inventory so the two output trees stay consistent.

   - Treat nested named groups as separate part boundaries so meshes owned by a nested named group are exported with that nested part instead of also being double-counted under the parent.
   - Before exporting, make a concrete inventory of confirmed parts, groups, and meshes from source inspection or safe runtime traversal, and reuse that same grouping inventory for both `part_meshes/` and `links/` outputs.
   - Drive exports from the discovered traversal inventory itself; do not hard-code expected group names, prefixes, or scene-specific labels unless they are directly confirmed in the source.
7. Export individual meshes as OBJ under `/root/output/part_meshes/<part_name>/`, calling `updateMatrixWorld(true)` first and cloning/applying each mesh's `matrixWorld` so standalone exports preserve assembled-scene placement and orientation
   - Successful default: bake world transforms into exported geometry before writing OBJ so nested meshes keep their correct final placement in standalone files.

8. Create one part-level link OBJ per extracted part under `/root/output/links/` by exporting/combining the whole part/group in world space, not just a representative child mesh
   - Treat mesh-level exports and part-level exports as two separate flows: export each individual mesh into `part_meshes/<part_name>/`, then separately export/combine the whole confirmed part/group into `links/<part_name>.obj`.

9. If helper code is needed, first confirm the module-loading setup required to execute `object.js` correctly, then keep any script in an allowed location; prefer one reproducible load → traverse → export workflow when feasible instead of separate ad hoc steps

   - If the environment requires a todo/task-state tool, record the substantive workflow there rather than a single generic item; keep it aligned with the real phases completed and remaining.
   - Preferred successful pattern: write one dedicated exporter that loads/builds the scene once, traverses recursively, groups meshes by confirmed part, writes per-mesh OBJs under `part_meshes/`, and writes one whole-part OBJ under `links/`.
   - Reject placeholder writes immediately: if the saved helper file is not executable source code that actually loads, traverses, and exports the scene, replace it before proceeding.
   - If an export step fails with an API/runtime error, reopen the saved script after fixing it, confirm the intended replacement actually exists, then rerun the workflow end-to-end before making any success claim.

   - After writing any helper script, inspect the saved file contents directly to confirm it contains executable code rather than notes, placeholders, or a truncated write.
   - If you write a helper script, the file contents must be actual Node.js/JavaScript source code, not a summary such as "created a Node.js export script...".
   - Self-check before execution: every shell invocation must be a concrete command with actual arguments/paths, and every generated script file must contain runnable code rather than narrative text.
   - After writing the script, immediately verify with a concrete check such as `sed -n '1,80p' <script>` or `node --check <script>` before executing it.
   - If an export step fails with an API/runtime error, do **not** summarize success until you have rerun the corrected workflow and verified the resulting files with explicit filesystem checks.
   - Prefer runtime traversal of the built scene or direct source parsing over handwritten reconstruction.
   - If combining meshes for a part-level OBJ, use a valid utility or traversal-based export path; do not rely on unsupported APIs such as `BufferGeometry.merge(...)`.
10. Before finalizing, verify the export command or script actually finished and build a complete inventory of discovered parts and meshes from full source inspection or runtime traversal
   - Treat a missing required completion token, unsupported tool syntax, placeholder file contents, or an unread-back helper script as unresolved failure states; fix them before continuing.
   - Preserve and compare both sides of verification: (1) the traversal/exporter discovery output listing the parts/groups/meshes it found, and (2) direct filesystem checks of the OBJ files written for those same parts.
   - A streaming export log, sampled listing, partial count output, or truncated stdout/stderr is not completion evidence by itself. If output is clipped or ends mid-run, first confirm the command exit status and then run separate targeted filesystem checks for `/root/output/part_meshes/` and `/root/output/links/`.
   - Do not report exact totals unless they come from complete commands such as targeted `find ... | sort`, `wc -l`, or structured per-part checks whose full output was observed.

   - Treat a truncated log, failed command, ambiguous output, or unavailable utility as **non-evidence**. For batch exports, do not infer completion from a partial console log or the intention to implement a script; confirm the process exited successfully and, if needed, replace ambiguous output with valid concrete checks such as `find`, `ls`, targeted `test -f`, or exit-status inspection.
11. Verify the exported outputs against that inventory by direct filesystem inspection: confirm `/root/output/part_meshes/` and `/root/output/links/` both exist, every discovered part has its directory and `links/<part_name>.obj`, nested-group meshes were written under their parent part directory, no unauthorized extra subgroup directories were created under `part_meshes/`, and every discovered mesh/part is represented by the files actually written without omissions or unintended duplication

   - Minimum completion check: compare the discovered traversal inventory against filesystem results, not just against script logs. Verify every confirmed part has both artifact types and that observed file counts are consistent with the inventory.
   - Minimum required evidence before claiming success: verify `/root/output/part_meshes/` with a targeted listing/count and verify `/root/output/links/` with a separate targeted listing/count; do not infer one from the other or from a truncated combined listing.
   - Also inspect at least a representative sample of written OBJ contents so verification covers file existence and non-empty exported data, not just path names.
   - Do not stop at a successful script/process exit code; always run direct filesystem checks to confirm the expected output tree and artifacts actually exist.
   - If you are using a todo/task tracker, do not mark the export task complete, remove it, or emit any required completion token until this verification is finished with non-truncated evidence for all claimed parts/files.

   - Do not stop after a top-level listing or one sample part folder. Run targeted per-part checks or structured summaries so no directory listing you rely on is truncated, inspect all discovered part directories, confirm every expected `links/<part_name>.obj`, and compare actual file counts against the traversal inventory before claiming completion.
   - Use non-truncated, targeted checks to support each claim, for example `find /root/output/part_meshes -maxdepth 2 -type f | sort`, `find /root/output/links -maxdepth 1 -type f | sort`, and representative `wc`/`head` checks on OBJ files.
   - Do **not** claim completion from partial listings, truncated console output, or script success messages alone.
12. If any read, listing, export log, or verification output is truncated or ambiguous, rerun narrower checks for specific directories, filenames, counts, or exit status until every claimed artifact is directly observed; otherwise report the missing or unverified artifacts instead of claiming completion
   - Before the final response, explicitly confirm both: (a) the primary export step exited cleanly or otherwise finished without ambiguity, and (b) filesystem checks match the claimed outputs. Never infer completion from a partial console log alone.

   - If a verification command fails or is unavailable (for example `tree: command not found`), treat that step as failed evidence, replace it with an equivalent concrete check, and reduce final claims to only what the substitute checks directly proved.
   - Do not claim file-format details such as normals, faces, or complete OBJ structure unless you directly inspected those records in the written files.

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

   - Final gate: if any earlier step used the wrong action syntax, wrote a helper outside an explicitly allowed directory, or verified only a sample of the outputs, do **not** declare success yet; correct the issue and re-verify first.
   - If the environment mandates a specific wrapper or exact completion token, preserve that syntax literally on every step and make the final message exactly that token/string when required.


15. Report part names, counts, and hierarchy details only when they were directly confirmed from source inspection, runtime traversal, or checked filesystem results, and if the task specifies an exact completion token or final-response format, output it exactly
16. Before each tool call, confirm the call uses the exact action protocol required by the environment and that the payload contains concrete executable content rather than a natural-language description of intent
17. After verification, summarize results at the same granularity as the evidence collected; if some checks were substituted, partial, or failed, state that limitation explicitly instead of implying full verification

18. Before the final response, check every claimed part name, count, and output path against an observed source read, runtime traversal result, or explicit filesystem command; remove any claim that lacks a traceable observation.


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

- For complex exports, prefer one dedicated processing script that loads the scene, traverses it once, and writes all required outputs in one pass.
- Inspect `package.json` and the scene file's module format before scripting so the helper runs in a verified compatibility context.
- Use confirmed named hierarchy as the default semantic partitioning for exports: identify named subassemblies first, then export against that structure rather than inventing part boundaries later.
- Generate per-mesh files and part-level merged/group OBJ files from the same confirmed part inventory so validation can compare the two views consistently.
- After export, do quick structural validation with directory listings, OBJ counts, sample filenames, and at least one OBJ header/content check.



## Mandatory Final Checklist

- Confirm you fully inspected the relevant `object.js` / helper code or performed an equivalent verified runtime traversal; if any earlier read was truncated, finish reading before implementing.
- Confirm your tool usage and final response exactly match any task-specific action schema and completion token.

- Confirm you read the explicit task instruction itself, not just `/root/data/object.js`, before choosing the export plan or declaring completion.
- Confirm every prior action used only the required environment protocol; no mixed tool syntaxes, substitute wrappers, or unsupported tool names were used.
- Confirm every prior tool call used executable content: shell calls were literal commands and file-write calls contained the actual saved code/data.
- If a todo/task-state mechanism was required, confirm it tracked the full job, not just setup, and that all major steps were explicitly completed before finalization.
- If you edited any existing file, confirm the change was anchored to exact text you read first.
- Confirm any generated script/config file was written only to an explicitly authorized path, reopened after writing, and contained actual code/data rather than a summary sentence.
- If the task requires an exact completion string, output exactly that string and nothing else.
- Confirm no success claim relies on truncated file reads, clipped logs, partial listings, or sampled output.

- Confirm the main export command completed cleanly, not just partially.

- Confirm the runtime/module configuration used for any helper script matched the script syntax actually executed.
- Confirm the exporter/traversal reported the discovered parts/groups you expected, then separately confirm matching OBJ artifacts exist on disk.
- Confirm `/root/output/part_meshes/` and `/root/output/links/` were verified independently from observed filesystem output; never infer one from the other.
- Confirm verification covered all extracted parts and all `links/*.obj` outputs, not just one sample directory.
- Confirm any exact totals mentioned come from explicit non-truncated counting commands or a complete structured inventory you directly observed.
- Confirm no cleanup/removal of helper scripts occurred before verification and any required final protocol completion.

- Confirm `/root/output/part_meshes/` exists and contains per-part mesh OBJ files.
- Confirm `/root/output/links/` exists and contains one part-level OBJ per extracted part.

- Confirm representative filenames and counts with direct filesystem evidence, not only exporter log messages.
- Confirm at least one representative mesh OBJ and one representative part-level OBJ contain plausible OBJ text before declaring success.

- Do not claim any hierarchy detail, count, filename, or output path that you did not directly observe.

- Confirm you checked for existing local exporter guidance/scripts first and reused compatible patterns rather than inventing an unnecessary new pipeline.
- Confirm final verification is based on non-truncated evidence for all required outputs, not sample listings or clipped command output.
- If any verification step failed and had to be replaced, confirm the final report was narrowed to the scope of the replacement checks.
- Confirm filesystem verification included the expected `/root/output` structure, not just script logs or assumed success.
