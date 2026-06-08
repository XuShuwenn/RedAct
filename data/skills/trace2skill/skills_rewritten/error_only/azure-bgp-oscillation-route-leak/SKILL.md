---
name: azure-bgp-oscillation-route-leak
description: "Detect BGP route oscillation and route leaks in Azure Virtual WAN topology, and evaluate which solutions can fix them."
---

# Azure BGP Route Leak Detection

## When to Use

- Analyze BGP routing configurations in Azure Virtual WAN
- Detect route oscillation and valley-free routing violations
- Evaluate which solutions resolve BGP routing issues


## Execution Discipline

## Execution Discipline

- Follow any task-specific interaction or tool/action contract exactly. If the environment requires a specific wrapper, literal action syntax, tool name, file-path restriction, or exact completion signal, use that exact format for every step.
- Before the first action, re-check the task prompt for execution constraints, allowed paths, sequencing rules, and termination requirements.
- Keep writes inside explicitly allowed locations; prefer direct commands or in-memory JSON processing over creating helper scripts, scratch files, or unnecessary intermediate artifacts.
- If the task specifies an exact completion token, emit that exact token and nothing else after all files are written and validated.

## Key Concepts

- **Oscillation**: Routing preference cycle causing unstable routes
- **Route leak**: Hub advertising routes to another hub via Virtual WAN (violates valley-free)
- **Valley-free routing**: Customer→Provider→Peer patterns, no Provider→Peer→Customer
- **AS path preferences**: local_pref determines routing priority


- Treat AS relationships and advertisement paths as **unknown unless explicit in the input files**. Do not assume a hub is a provider, peer, or customer, or that a route leak exists, without direct evidence from the loaded JSON.
- Treat provider/peer/customer roles as data-driven from `local_pref.json` or other explicit inputs, not as defaults implied by Azure Virtual WAN terminology.

## Input Files

- `/app/data/route.json`: Route advertised from vnet
- `/app/data/preferences.json`: Routing preferences between hubs
- `/app/data/local_pref.json`: Relationship type weights
- `/app/data/possible_solutions.json`: Solutions to evaluate


- Verify the actual filenames present in `/app/data` before reading them. If a listed filename differs from what is on disk, use the observed path and reconcile the mismatch before analysis.
- Treat the directory listing as the source of truth for filenames. Explicitly map each required logical input to an observed on-disk file before analysis, and use the observed path consistently.
- Treat any directory-listing mismatch as unresolved until you successfully open the on-disk file that supplies that required input. Do not say all inputs are loaded until each required dataset has been matched to an observed filename and read successfully.
- Do not silently normalize extensions or "fix" suspicious names such as `.jso` to `.json`; use the observed path or re-check it first.
- Do not create scripts, compute results, or draft the report while any required input path is still assumed rather than verified.
- Validate that all required inputs are present, readable, and fully loaded before analysis. If a file is missing, renamed, truncated, or partially read, resolve that first and re-read the full content before using it.
- Inspect each JSON file's actual schema before writing detection logic. Normalize once into simple internal forms and use those forms consistently.
- `preferences.json` may use ASN string keys with nested objects such as `{ "65002": {"prefer_via": 65003} }`; normalize this to a plain map like `65002 -> 65003` before cycle detection.
- After normalizing a schema, ensure all downstream logic uses the normalized representation consistently. For example, once preferences become `asn -> preferred_asn`, later cycle detection must not still access nested fields like `.get("prefer_via")` on those values.
- Convert ASN identifiers to one type consistently (prefer integers in memory) so comparisons and output are stable.
- Treat only the provided input files as the evidence base. Do not assume AS roles, hub/provider/peer/customer relationships, Azure-owned ASNs, WAN ASN values, or leak paths unless they are directly supported by the inputs.
- Treat `possible_solutions.json` as authoritative: do not score, name, number, or infer any solution unless it appears in the fully loaded file.

- After listing `/app/data`, build your read plan from the observed filenames only. If an expected file is misspelled, renamed, or differs from the prompt/skill, confirm which on-disk file supplies each required input and then use that verified path consistently.
- If any file read is truncated, incomplete, malformed, cut off mid-object/array/string, or shown only as partial command output, treat that as a hard stop: re-read until the full valid JSON content is available before analysis.
- Do not enumerate or evaluate candidate solutions until `possible_solutions.json` has been fully read, parsed successfully, and inspected end-to-end, including the complete list and full text of every solution.
- Record the exact set of loaded solution items first; later `solution_results` must map only to that confirmed set.
- Do not rely on delegated or opaque subagent judgments for oscillation detection, leak detection, or per-solution outcomes. Perform and verify the core reasoning directly from the loaded inputs.
- If complete recovery of a required input is not possible, stop analysis rather than fabricate a complete report from incomplete evidence.


## Required Analysis Workflow

11. Do not create auxiliary scripts or write intermediate files unless the task explicitly allows them; only write the required output file(s).
12. If any loaded input or produced report appears partial or malformed at any point, do not continue from it; re-read, regenerate, or rewrite it and validate the full contents first.
13. Make the derivation auditable before writing the report: parse and normalize the loaded inputs, identify the supported preference graph and any advertisement/relationship evidence, then determine oscillation, leak status, and per-solution outcomes from that evidence rather than jumping directly from raw file reads to a completed report.
14. Do not change detection logic, solution judgments, or final conclusions based on a truncated terminal view of the report. First retrieve or parse the complete saved JSON, then decide whether any correction is needed.

15. You may use delegation only for non-critical assistance; do not outsource the core determinations of oscillation detection, route leak detection, or per-solution outcomes unless the task explicitly requires it.
16. If any delegated tool or subagent provides analytical conclusions, treat them as untrusted until you verify the substantive claims directly against the loaded inputs before using them in the report.
17. Before final completion, read back `/app/output/oscillation_report.json`, parse or inspect the full contents, and confirm the on-disk artifact is complete, valid JSON matching the required schema rather than a placeholder, summary, or partial write.
18. Do not finalize from a write confirmation or assumption about what was written; finalization requires explicit post-write verification visible in the interaction log.
19. Before the final response, run a termination check: confirm the output file is fully written and validated, then emit the exact task-required completion signal in the exact required format with identical spelling, punctuation, and casing, and no extra text if specified.

## Required Analysis Workflow

1. Read all four input files completely before deciding anything.
2. Normalize the parsed JSON into stable internal structures before analysis.
3. Build preference, relationship, and advertisement relationships from the input data, not from assumptions about Azure topology.
4. Detect baseline issues from the provided evidence only:
   - determine whether a directed preference cycle creates oscillation
   - determine whether any advertised path violates valley-free routing
5. If the inputs do not show enough topology, relationship, or advertisement data to prove a specific route leak, set `route_leak_detected` to `false` and `route_leaks` to `[]` rather than guessing.
6. Evaluate every entry in `possible_solutions.json` separately by recomputing whether the demonstrated cycle and prohibited advertisement would still exist after applying that solution's stated effect.
7. Mark `oscillation_resolved` true only if the solution breaks the observed preference cycle, and mark `route_leak_resolved` true only if it prevents the specific prohibited advertisement path evidenced in the inputs.
8. Do not classify solutions by keyword matching, generic networking intuition, or unsupported assumptions.
9. Produce exactly one `solution_results` entry per input solution and no extra entries.
10. Only after completing the per-solution evaluation, write `/app/output/oscillation_report.json` and validate it.
## Output Format

JSON at `/app/output/oscillation_report.json`:
```json
{
  "oscillation_detected": true/false,
  "oscillation_cycle": [AS1, AS2],
  "affected_ases": [AS_numbers],
  "route_leak_detected": true/false,
  "route_leaks": [{"leaker_as": N, "source_as": M, "destination_as": K, ...}],
  "solution_results": {"solution_name": {"oscillation_resolved": bool, "route_leak_resolved": bool}}
}
```


- Match the schema exactly and save only the fields shown above.
- The bytes written to `/app/output/oscillation_report.json` must be the actual final report object, not a label, placeholder, TODO marker, summary sentence, or natural-language description of work performed.
- Reject any output file whose contents are non-JSON status text or self-descriptions of the analysis instead of the report object.
- If the task required evaluating N solutions from `possible_solutions.json`, the saved JSON must contain exactly N `solution_results` entries with matching solution names/keys.
- Do not add extra top-level fields such as `summary` or `explanation` unless explicitly requested.
- In `solution_results`, each solution value must contain only `oscillation_resolved` and `route_leak_resolved`.
- Keep `route_leaks` entries to the requested structure such as `leaker_as`, `source_as`, and `destination_as`; do not add narrative fields such as `description` unless requested.
- If no supported oscillation cycle is found, use `"oscillation_detected": false` and an empty `oscillation_cycle`.
- If no supported leak instance is established from the inputs, use `"route_leak_detected": false` and an empty `route_leaks` array.
- Populate output fields only from observable input data and directly derivable routing rules; do not infer unsupported topology details or remediation effects.
- Do not add solution tiers, rankings, recommendation names, prohibited-actions lists, or other remediation labels unless those exact items appear in the provided inputs or are explicitly requested.
- If a solution, label, or remediation text does not appear in `possible_solutions.json` or another loaded input, do not introduce it into the report or final response.
- After writing `/app/output/oscillation_report.json`, read back or parse the entire file to confirm it is complete (not truncated), valid JSON, contains all required top-level keys, contains no extra top-level fields, and includes exactly one `solution_results` entry for every candidate in `possible_solutions.json`.
- Do not treat a partial terminal display as sufficient verification; if the readback cuts off mid-file or mid-field, perform another full check before finishing.
- Verification means confirming the complete saved file, not a truncated screen view. If the displayed output is truncated, do not infer that the unseen remainder is correct; re-read or parse the artifact until the entire JSON is visible or fully validated.
- Do not declare completion while any required field, solution entry, or closing JSON structure remains unseen or unparsed in verification.
- During read-back validation, confirm the file content is the actual serialized report object, not a placeholder string or descriptive label.

- Before saving, compare the output object against the required schema and remove any unsupported or unrequested fields.
- Do not add top-level fields like `summary`, per-solution fields like `reason` or `explanation`, or narrative fields inside `route_leaks` unless explicitly requested.
- When source inputs use different field names for leak events, transform them into the required report keys such as `leaker_as`, `source_as`, and `destination_as` before saving.
- Validate that every `solution_results` entry has exactly this shape: `"solution_name": {"oscillation_resolved": bool, "route_leak_resolved": bool}`; do not add fields such as `status`, `reason`, `summary`, or `invalid`.
- Before finalizing, cross-check that the keys in `solution_results` match the exact set and count of solutions actually loaded from `possible_solutions.json`, with no omissions, duplicates, or extra inferred entries.
- If `possible_solutions.json` was re-read due to truncation or schema uncertainty, rebuild `solution_results` from the final confirmed file contents before saving.
- Write the report atomically as complete JSON; if the first write or read-back shows truncated, partial, or invalid JSON, rewrite `/app/output/oscillation_report.json` completely and re-validate before finishing.
- Return only the required artifact and any task-required completion signal.

## Tips

- Detect oscillation from the actual preference graph between hubs/ASes; report a cycle only if the preferences form a directed loop.
- Detect a route leak only from actual advertisement paths and relationship data that show a valley-free violation, especially hub-to-hub re-advertisement via Virtual WAN.
- Mark `oscillation_resolved` true only if the solution removes at least one edge or preference needed for the demonstrated loop.
- Mark `route_leak_resolved` true only if the solution prevents the specific prohibited advertisement path evidenced in the inputs.
- Evaluate each proposed solution from its network effect on the given topology and preferences, not by keyword or substring matching on the solution name/text.
- If evidence is insufficient to prove a specific leak, AS relationship, or solution outcome, stay conservative rather than filling gaps with assumptions.
- Verify `solution_results` covers every solution from `possible_solutions.json`; no omissions, duplicates, or guesses from incomplete solution text.
- Before finalizing, cross-check that every reported oscillation or leak claim is traceable to the observed preference graph or route propagation path in the input files.

- Treat completeness as a gate: do not start detection or solution scoring until every required file has been fully read and successfully parsed.
- A directed preference cycle is enough for oscillation detection, but it is not enough by itself for `route_leak_detected = true`.
- When `preferences.json` already gives direct next-hop preferences, check that graph first; a simple 2-node or longer directed cycle is enough to prove oscillation without simulating BGP dynamics.
- If a route record explicitly states relationship labels for where the route was learned and where it was advertised, use those labels directly to test valley-free export rules instead of inferring missing relationships from topology names.
- Normalize once, then keep all detection and evaluation logic operating on that normalized representation; do not pass raw nested preference objects into cycle logic.
- For each solution marked effective, be able to name the specific cycle edge it breaks or the specific prohibited advertisement it blocks from the observed inputs.
- If any file view is truncated, incomplete, or suspiciously partial, stop and re-read the full file before claiming complete topology facts or evaluating every solution.
- Keep the reasoning auditable from observed data; do not copy in unverified classifications from a subagent, summary, or truncated intermediate output.
- Before finishing, confirm both the saved output file and any task-specific final response or completion format are satisfied exactly.

- Use a simple evidence test before asserting `route_leak_detected = true`: you must be able to point to both the observed advertisement or re-advertisement path and the observed relationship labels or explicit policy rule that it violates.
- A partial screen view of `possible_solutions.json` is not enough to score every candidate; first recover the entire list and full text of each solution.
- Treat solution evaluation as evidence-constrained: a solution resolves oscillation only if its stated effect breaks the observed directed cycle, and resolves a leak only if its stated effect blocks the specific prohibited advertisement shown in the inputs.
- If you cannot point to that specific mechanism from the loaded inputs and the solution text, keep the result conservative rather than asserting that the solution works.
- Keep conclusions strictly bounded by the observed files and your direct computations from them. Do not introduce outside Azure rules, product limitations, rankings, or remediation claims unless they are explicitly present in the inputs or task instructions.
- Before writing the output file, sanity-check that the in-memory report is complete JSON with real values derived from the loaded inputs, not a placeholder string or unfinished template.