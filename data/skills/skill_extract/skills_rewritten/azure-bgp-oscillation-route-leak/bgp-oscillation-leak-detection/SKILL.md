---
name: bgp-oscillation-leak-detection
description: "Detect BGP preference-cycle oscillations and valley-free routing leaks in hub-and-spoke/cloud WAN topologies and evaluate which solution proposals would resolve them."
---

# BGP Oscillation and Route Leak Detection with Solution Evaluation

Reusable workflow for analyzing BGP behavior in cloud/managed WAN or hub-and-spoke topologies. It detects:
- Preference-cycle oscillations (mutual or longer cycles in routing preferences)
- Valley-free routing violations (e.g., exporting provider-learned routes to peers/providers)

It also evaluates candidate mitigation proposals and flags which fixes break oscillations and/or stop leaks.

## When to Use

Use this skill when:
- You are given routing preferences, relationships, and route event data for a WAN or multi-hub topology
- You must detect BGP oscillations and/or route leaks
- You must determine which proposed solutions will resolve the detected issues

Typical inputs include JSON files like: preferences, local preference weights, relationships, route advertisements/events, and possible solutions.

## Core Workflow

1. Load Inputs
   - Collect available JSON inputs from the specified input directory (filenames commonly include: preferences.json, local_pref.json, relationships.json, route.json, route_events.json, possible_solutions.json). Some may be optional.
   - Handle missing files gracefully; proceed with what is available.

2. Normalize Routing Preferences
   - Unify ASN/node identifiers (e.g., cast numeric strings to integers when possible; otherwise keep as normalized strings).
   - Normalize the preferences into a directed graph where an edge A→B indicates A prefers routing via B.
   - Accept flexible input shapes (e.g., dict with lists, list of {from,to} objects). Deduplicate edges.

3. Detect Oscillation (Preference-Cycle)
   - Run directed cycle detection on the preference graph (DFS or similar). Detect both 2-node cycles and longer cycles.
   - If a cycle is found, record one cycle path and the set of affected nodes.

4. Detect Valley-Free Route Leaks
   - If route_events contain per-advertisement metadata with source_type/destination_type (e.g., customer, provider, peer), flag violations:
     - Exporting provider/upstream-learned routes to peers or providers is a leak.
     - Exporting peer-learned routes to providers is also a leak.
   - If source/destination types are not directly provided, infer from a relationships mapping when available (e.g., customer/provider/peer between AS pairs).
   - Record each detected leak with leaker, source, destination, and the inferred relationship types used for the decision.

5. Evaluate Proposed Solutions
   - For each solution description, classify by keywords:
     - Resolves both oscillation and leak:
       - Deterministic forwarding/policy intent (e.g., "routing intent", "policy intent"), or static/UDR override mechanisms.
     - Resolves leak only:
       - Export controls that prevent leaking upstream-learned routes (e.g., "no-export", "export policy", "ingress filter", "AS-PATH filter", "RPKI origin validation").
       - Heuristic: If the leak involves the same hubs/nodes as the oscillation cycle and the solution explicitly blocks cross-hub re-advertisement, it may also break the cycle.
     - Resolves oscillation only:
       - Preference changes that break the cycle (e.g., "update routing preference", "local-pref/weight changes", "preference hierarchy", "stop preferring via X").
     - Ineffective or prohibited (do not count as fixes):
       - Timers/dampening/max-prefix, restarts, waiting, disabling connectivity/peering.
   - Output per-solution booleans: oscillation_resolved and route_leak_resolved.

6. Save the Report
   - Produce a JSON report with these fields:
     - oscillation_detected: boolean
     - oscillillation_cycle: array of nodes (one representative cycle path or empty)
     - affected_ases: array of unique nodes from detected cycles
     - route_leak_detected: boolean
     - route_leaks: list of {leaker_as, source_as, destination_as, source_type, destination_type}
     - solution_results: map of solution string → {oscillation_resolved: bool, route_leak_resolved: bool}
   - Ensure the output directory exists and the report is valid JSON.

## Verification

- Input Handling
  - Verify all expected inputs are attempted to be read and missing files are tolerated.
  - Normalize ASN/node identifiers consistently (e.g., int conversion where possible).
- Oscillation Detection
  - Confirm cycle detection flags 2-node cycles as well as longer cycles.
  - If oscillation_detected is true, ensure oscillation_cycle is non-empty and affected_ases contains the nodes in the cycle.
- Leak Detection
  - Verify that leak classification uses valley-free rules (provider/upstream-learned routes should not be exported to peers/providers).
  - Ensure each leak record includes leaker_as, source_as, destination_as, source_type, destination_type (inferred if necessary).
- Solution Evaluation
  - Confirm solution classification is keyword-based, case-insensitive, and not dependent on exact phrasing.
  - Check that prohibited/operational-only actions are not counted as fixes.
  - If a solution blocks cross-hub advertisements implicated in the cycle, reflect its impact on oscillation only if it truly breaks the cycle (e.g., it prevents the cycle-forming advertisement).
- Output
  - Validate the final JSON schema and required fields are present even if empty.
  - Confirm the output file is written and parseable.

## Common Pitfalls

- Brittle Parsing of Preferences
  - Assuming a single data shape for preferences leads to missed cycles. Normalize diverse formats (dicts, lists of edges, nested structures).
- Ignoring 2-Node Cycles
  - Many oscillations arise from mutual preferences; ensure cycle detection handles length-2 cycles.
- Type Mismatches
  - Comparing string ASNs to integers causes missed detections. Normalize identifiers consistently.
- Valley-Free Rule Misapplication
  - Blocking a leak does not automatically fix oscillation unless it prevents the specific cross-advertisements forming the preference cycle.
- Overvaluing Operational Tweaks
  - Timer changes, dampening, restarts, or waiting do not break structural preference cycles or export policies; do not mark them as resolved.
- Prohibited Actions
  - Disabling core peering or managed links is not an acceptable fix: do not count as resolved.
- Output Shape Errors
  - Forgetting to create the output directory or omitting required fields leads to grading failures.

## Optional Script Usage

A helper script is provided to implement the above workflow generically.

Example usage:
- Analyze inputs in an input directory and write a report:
  - python scripts/bgp_analysis.py --input-dir /path/to/data --output-file /path/to/output/oscillation_report.json

The script:
- Reads available JSON inputs
- Normalizes preference data
- Detects cycles and valley-free leaks
- Classifies solutions using robust keyword matching
- Writes a standards-compliant report
