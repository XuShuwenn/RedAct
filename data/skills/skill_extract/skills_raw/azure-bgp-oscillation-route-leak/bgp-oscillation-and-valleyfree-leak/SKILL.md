---
name: bgp-oscillation-and-valleyfree-leak
description: "Detect BGP preference-cycle oscillations and valley-free route leaks, then assess which changes would resolve each issue."
---

# BGP Oscillation and Valley-Free Route Leak Analysis

A reusable workflow to analyze BGP topologies for:
- Preference-cycle oscillations (control-plane instability)
- Valley-free route leaks (policy violations)

It also guides evaluation of candidate solutions to determine whether they break oscillation cycles and/or stop route leaks.

## When to Use

Activate this skill when you need to:
- Inspect BGP preferences across ASes and detect cycles that cause oscillation
- Check export-policy compliance with the valley-free model using route event logs
- Evaluate whether proposed configuration or policy changes would fix oscillations and/or leaks
- Produce a structured JSON report with findings

## Core Workflow

1) Gather Inputs
- Load the provided JSON inputs (paths come from the task prompt). Typical files:
  - preferences.json: who prefers which neighbor for a given route or class of routes
  - local_pref.json (optional): weights or relationship tiers (customer > peer > provider)
  - relationships.json or topology.json: neighbor and relationship types (customer/peer/provider)
  - route.json: origin and propagation context for specific prefixes (optional)
  - route_events.json: observed advertisements including who advertised what to whom and, if available, relationship types and/or learned-from source
  - possible_solutions.json: free-text or structured candidate remediations

2) Build an Internal Model
- Construct a directed preference graph G where an edge A -> B indicates “A prefers B as next-hop for the route in question.” If multiple preferences exist per AS, include all relevant directed edges.
- Keep a mapping of AS relationship types per adjacency (customer/peer/provider). If not given per-edge, build from relationships.json (e.g., each AS lists its customers, providers, and peers).

3) Detect Oscillation (Preference Cycles)
- Oscillation arises when there is a directed cycle in G. Any simple cycle length ≥ 2 indicates a potential persistent selection loop.
- Algorithm (deterministic DFS):
  - For each AS u, do a DFS tracking a recursion stack. If you encounter an already-on-stack node v, you discovered a cycle. Reconstruct that cycle from the stack segment.
  - Optionally collect all distinct cycles; at minimum, record that oscillation_detected = true and the set of affected_ases.
- Success criterion: If no cycle exists, oscillation_detected = false. If cycles exist, list at least one representative cycle.

4) Detect Valley-Free Route Leaks
- Use the valley-free export rule:
  - To customers: may export routes learned from anywhere (self, customers, peers, providers)
  - To peers or providers (non-customers): may export only routes that are self-originated or learned from customers
  - Therefore, if a route learned from a peer or provider is exported to a peer or provider, that is a leak
- From route_events.json, for each advertisement event (the leaker AS exporting to a neighbor):
  - Determine learned_from_type (customer, peer, provider) and destination_type (customer, peer, provider). Use fields in the event if present; otherwise derive from relationships mapping relative to the leaker.
  - Flag a leak if destination_type in {peer, provider} and learned_from_type in {peer, provider}.
- Aggregate all leaks and set route_leak_detected accordingly.

5) Evaluate Candidate Solutions
- A solution resolves oscillation if it breaks every detected cycle by removing at least one edge in each cycle or removing the disputed path option. Common ways:
  - Change preference ordering/local_pref so a cycle edge is no longer selected (e.g., prefer customer > provider > peer or a specified deterministic order that eliminates mutual preference)
  - Enforce centralized routing intent that removes the contested path from consideration (effectively removing an edge)
  - Apply export policy that prevents a path from being imported/considered in one of the cycle vertices
  - Remove/disable the specific peering or route advertisement only if the task/environment allows it (do not assume you can disable provider-managed links if out of scope)
- A solution resolves route leaks if it ensures provider/peer-learned routes are not exported to non-customers. Common ways:
  - Export policy: block provider/peer-learned routes to peers/providers
  - Apply NO_EXPORT or equivalent communities/policies on provider-learned routes
  - Ingress filters on peer/provider sessions that reject paths containing disallowed upstream ASNs (prevents acceptance and subsequent re-export)
- Typically NOT sufficient to fix either issue:
  - Timer adjustments, route dampening, ECMP, max-prefix limits, RPKI origin validation (helps authenticity, not export policy), or restarts. These do not break preference cycles nor enforce valley-free export rules by themselves.
- Platform constraints: If the environment prohibits certain changes (e.g., disabling managed peering), mark such proposals as not applicable rather than effective fixes.

6) Produce the Output Report
- Follow the exact schema specified by the task prompt. A common shape:
  - oscillation_detected: boolean
  - oscillation_cycle: list of ASNs (one representative simple cycle)
  - affected_ases: list of ASNs involved in oscillation
  - route_leak_detected: boolean
  - route_leaks: list of objects { leaker_as, source_as, destination_as, source_type, destination_type }
  - solution_results: map from solution string → { oscillation_resolved: boolean, route_leak_resolved: boolean }
- Do not add extra top-level fields unless explicitly requested by the task.
- Ensure the directory exists before writing. Validate the JSON before saving.

## Verification

- Data completeness:
  - Confirm all required input files were read successfully (preferences, relationships, and route_events). If some are missing, state assumptions or degrade gracefully.
- Cycle detection sanity:
  - If oscillation_detected is true, each listed cycle must be a valid directed loop in the preference graph with ≥2 nodes.
  - Removing any one edge from a listed cycle should break that specific cycle.
- Leak detection sanity:
  - For every route leak reported, confirm the learned_from_type and destination_type combination violates valley-free export.
  - Deduplicate identical leak events in the output if the task expects unique entries.
- Solution mapping:
  - For oscillation: demonstrate which edge(s) the solution eliminates or which preference rule changes remove the cycle.
  - For leaks: point to the specific export/ingress policy that blocks provider/peer-learned-to-non-customer propagation.
- Output schema:
  - Keys, types, and structure exactly match the task’s required format. Avoid unrequested fields.

## Common Pitfalls

- Misclassifying solutions:
  - Timer changes, dampening, ECMP, restarts, and RPKI validation do not fix cycles or leaks by themselves.
  - Ingress filtering that rejects provider ASN on a peer session can stop leaks but does not inherently break a preference cycle unless it removes a cycle edge.
- Ignoring platform constraints or control-plane scope:
  - Do not claim success for actions that are not customer-controllable in the given environment.
- Skipping inputs:
  - Failing to use route_events.json or relationship data leads to missed leaks or false positives.
- Overfitting to a single AS pair:
  - Always run general cycle detection; handle multi-node cycles and multiple cycles.
- Output schema drift:
  - Adding or renaming fields not requested by the task causes scoring failures.

## Optional Script Usage

A helper script is included to deterministically detect preference cycles and valley-free export violations from generic JSON inputs. It does not hardcode any ASNs or environment details.

Example:
- Detect oscillations and leaks:
  - python scripts/bgp_analysis.py --preferences /path/to/preferences.json --route-events /path/to/route_events.json --relationships /path/to/relationships.json --out /path/to/oscillation_report.json
- Print results to stdout (no file):
  - python scripts/bgp_analysis.py --preferences prefs.json --route-events events.json

The script reports:
- oscillation_detected, oscillation_cycles (list), affected_ases
- route_leak_detected, route_leaks (list with leaker/source/destination/types)

Use these results and the evaluation rules above to score candidate solutions and assemble the final report in the task-specified format.
