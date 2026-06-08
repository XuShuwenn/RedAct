---
name: azure-bgp-oscillation-route-leak
description: "Detect BGP route oscillation and route leaks in Azure Virtual WAN topology, and evaluate which solutions can fix them."
---

# Azure BGP Route Leak Detection

## When to Use

- Analyze BGP routing configurations in Azure Virtual WAN
- Detect route oscillation and valley-free routing violations
- Evaluate which solutions resolve BGP routing issues

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
- Validate that all required inputs are present, readable, and fully loaded before analysis. If a file is missing, renamed, truncated, or partially read, resolve that first and re-read the full content before using it.
- Inspect each JSON file's actual schema before writing detection logic. Normalize once into simple internal forms and use those forms consistently.
- `preferences.json` may use ASN string keys with nested objects such as `{ "65002": {"prefer_via": 65003} }`; normalize this to a plain map like `65002 -> 65003` before cycle detection.
- Convert ASN identifiers to one type consistently (prefer integers in memory) so comparisons and output are stable.
- Treat only the provided input files as the evidence base. Do not assume AS roles, hub/provider/peer/customer relationships, Azure-owned ASNs, WAN ASN values, or leak paths unless they are directly supported by the inputs.
- Treat `possible_solutions.json` as authoritative: do not score, name, number, or infer any solution unless it appears in the fully loaded file.


## Required Analysis Workflow

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
- Do not add extra top-level fields such as `summary` or `explanation` unless explicitly requested.
- In `solution_results`, each solution value must contain only `oscillation_resolved` and `route_leak_resolved`.
- Keep `route_leaks` entries to the requested structure such as `leaker_as`, `source_as`, and `destination_as`; do not add narrative fields such as `description` unless requested.
- If no supported oscillation cycle is found, use `"oscillation_detected": false` and an empty `oscillation_cycle`.
- If no supported leak instance is established from the inputs, use `"route_leak_detected": false` and an empty `route_leaks` array.
- Populate output fields only from observable input data and directly derivable routing rules; do not infer unsupported topology details or remediation effects.
- After writing `/app/output/oscillation_report.json`, read it back or parse it to confirm the file is complete, valid JSON, contains all required top-level keys, and includes a `solution_results` entry for every candidate in `possible_solutions.json`.

## Tips

- Detect oscillation from the actual preference graph between hubs/ASes; report a cycle only if the preferences form a directed loop.
- Detect a route leak only from actual advertisement paths and relationship data that show a valley-free violation, especially hub-to-hub re-advertisement via Virtual WAN.
- Mark `oscillation_resolved` true only if the solution removes at least one edge or preference needed for the demonstrated loop.
- Mark `route_leak_resolved` true only if the solution prevents the specific prohibited advertisement path evidenced in the inputs.
- Evaluate each proposed solution from its network effect on the given topology and preferences, not by keyword or substring matching on the solution name/text.
- If evidence is insufficient to prove a specific leak, AS relationship, or solution outcome, stay conservative rather than filling gaps with assumptions.
- Verify `solution_results` covers every solution from `possible_solutions.json`; no omissions, duplicates, or guesses from incomplete solution text.
- Before finalizing, cross-check that every reported oscillation or leak claim is traceable to the observed preference graph or route propagation path in the input files.