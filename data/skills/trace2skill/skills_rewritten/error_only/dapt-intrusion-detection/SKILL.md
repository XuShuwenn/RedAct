---
name: dapt-intrusion-detection
description: "Analyze network packet captures (PCAP) to compute traffic statistics, protocol counts, entropy, and detect intrusion patterns."
---

# Network Intrusion Detection

## When to Use

- Analyze PCAP files for network traffic statistics
- Compute protocol counts (TCP, UDP, ICMP, ARP)
- Calculate Shannon entropy for IPs and ports
- Detect port scans, DoS patterns, beaconing behavior


## When to Use

## Task-Instruction Priority

- Treat task/system execution instructions as higher priority than this skill.
- Follow the current task environment's required tool-call/action schema, response format, and completion token exactly for the entire run.
- Before finishing, perform a final compliance check: required output format, required files written, and exact completion signal emitted.

- Before the first action, identify any task-specific interaction contract (for example exact action/tool schema, wrappers, allowed tools, response format, and required completion token) and use that protocol verbatim for every step.
- Treat exact completion strings as mandatory. Do not substitute your preferred tool-call style, extra wrap-up text, or a natural-language ending when the environment requires a specific action protocol or completion token.
- If the environment prescribes an exact action/tool syntax (for example `Thought:` / `Action:` with a JSON object), copy that schema literally for every tool step. Do not switch to alternate tool-call tags, XML, markdown code fences, custom wrappers, or ad hoc formats.
- Do not treat procedural compliance as optional even if the analysis itself is correct; a wrong action format or wrong completion token is a task failure.

- At task start, inspect the required output artifact/template and any task-provided code/assets before implementing analysis logic.
- If helper modules or utilities are provided, prefer their tested functions over reimplementing packet parsing, entropy, graph, flow, timing, or detection logic unless the task requires custom implementation.
- Verify helper interfaces against reality before use: function signatures, expected input types, and returned key names/shapes are authoritative.
- Anchor computation and write-back to the exact required fields, row names, and schema in the destination artifact.
- For multi-metric tasks, prefer one reproducible workflow that parses the PCAP once, computes all required metrics/flags into a single results map, and writes the final artifact in one controlled pass.
- If a command or interpreter is unavailable, retry the same workflow with an available equivalent (for example, `python3` instead of `python`) before changing the analysis approach.
- If the task requires both file updates and a special completion signal, verify the artifact first, then end with the exact required signal.


## Preferred Workflow

## Preferred Workflow

- Compute all required metrics and flags into a single results mapping keyed by the destination template's exact metric or field names.
- Then perform a separate structured pass that fills only the intended value fields row-by-row or field-by-field, preserving all non-value content exactly as provided.
- For multi-metric tasks, prefer one rerunnable parse → compute → write pipeline so outputs, flags, and explanations stay tied to the same computed results.

## Key Metrics

### Protocol & Size Stats
- Packet counts by protocol
- Total bytes, avg/min/max packet size
- Packets per minute (avg/max/min across time buckets)

### Entropy Calculation
- Shannon entropy
- src_ip_entropy, dst_ip_entropy, src_port_entropy, dst_port_entropy

### Graph Metrics (directed IP graph)
- num_nodes: distinct IPs
- num_edges: unique (src→dst) pairs
- network_density
- max_outdegree/max_indegree

### Timing & PCR
- Inter-arrival times (iat_mean, iat_variance, iat_cv)
- Producer/Consumer Ratio per IP: (sent-recv)/(sent+recv)
- num_producers (PCR>0.2), num_consumers (PCR<-0.2)

### Flow Analysis
- 5-tuple flow key: (src_ip, dst_ip, src_port, dst_port, protocol)
- unique_flows, tcp_flows, udp_flows
- bidirectional_flows (flow and reverse both exist)

## Detection Flags
- is_traffic_benign: nothing clearly malicious
- has_port_scan: malicious port scanning
- has_dos_pattern: extreme traffic spike/flood
- has_beaconing: periodic communication (low IAT variance)

- Keep flag logic in the same units as the metric you computed. If you justify spikes with packets-per-minute, detect them from per-minute buckets; if you compute per-second thresholds, explain them in per-second terms. Do not mix units between code and explanation.
- Preserve event multiplicity for repetition-based flags. Do not deduplicate flows before checking repeated communications; use packet/flow occurrence counts over timestamped events, then assess periodicity on repeated src/dst(/port) communications.
- For `has_beaconing`, build counts and inter-arrival times from repeated timestamped communications (for example by src/dst or src/dst/port key over packets or non-deduplicated flow records), then test periodicity on those repeated events. Do not derive repetition counts from a deduplicated set.
- For `has_dos_pattern`, compute any spike threshold in the same bucket size you report (for example per-minute if you justify with packets-per-minute); keep the code, threshold, and explanation in the same units.
- Compute foundational metrics first, then derive boolean flags from those computed values using provided detector helpers or explicit threshold rules so the final flags and explanations match the actual metrics produced.


## Output Writing Safety

## Output Writing Safety

- If the task asks you to fill a provided CSV/template, preserve structural rows unchanged: headers, comment lines, blank lines, delimiter, and expected row order unless the task says otherwise.
- Only update data rows that correspond to computed metric names; do not rewrite headers or labels as if they were metrics.
- Do not perform exact-match full-file replacements unless you have read and verified the full current file contents.
- If only part of a file has been inspected, use a safer update method: edit only verified lines/fields or rewrite from structured data after confirming the expected schema.

## Tips

- Normalize packet timestamps to plain floats before sorting, differencing, or bucketing (for Scapy, use `float(pkt.time)`) to avoid `EDecimal`/type issues.
- Apply type normalization before any full analysis run, not only after a crash: convert timestamp-like values and other library numeric wrappers to native `float`/`int` before division, averaging, variance, or bucket-rate calculations.
- Safe pattern: `times = [float(pkt.time) for pkt in packets if hasattr(pkt, "time")]`; then compute deltas/rates only from `times`, not mixed raw library values.
- Sort packets by normalized timestamp for timing calculations.
- Skip missing values in entropy computation.
- Use scapy or pyshark for PCAP parsing.
- Inspect the task directory for provided analysis helpers (for example `pcap_utils.py`, utility modules, or starter scripts) and prefer adapting them over reimplementing packet parsing or metric logic from scratch when they satisfy the task.
- Before relying on helper modules/utilities, inspect their actual function signatures, expected argument types, return shapes, and output key names; adapt to the real interface instead of assuming packet/object formats or scalar returns.
- Check helper input contracts before composing utilities: confirm whether each helper expects packets, timestamps, counters, flows, or graph-derived state, then convert inputs explicitly before calling it.
- Use helper or library return keys exactly as defined (for example `packets_per_minute_avg`, `iat_mean`) and map those exact keys into the required output fields instead of inventing aliases.
- Create intermediate derived objects once (for example timestamps, flow tables, graph state), reuse them consistently, and when practical compute all requested metrics and flags in one reproducible script/run from that shared results set.

## Tips

## Validation Before Finalizing

- Re-open the produced output artifact and verify the full file; do not rely on a truncated preview or the first few lines.

- If the read output is truncated, only partially visible, or ends mid-row/mid-field, perform additional reads or targeted checks for the missing metrics/flags/rows before claiming completion.
- Do not state that rows or fields were written unless they are visible in tool output or confirmed by explicit targeted verification commands.
- After any edit, read back the completed artifact in full (or query every required row/field directly) and confirm the values written are exactly the values observed from computation.
- Confirm every required metric/flag/row from the task is present exactly once and populated, and that structural rows remain intact, including the original header row, comments, blank lines, and expected order.
- Validate completion against an explicit checklist of required metrics/flags/rows from the task; if output is truncated or partially visible, fetch the missing rows/fields or run targeted checks for each required field before declaring success.
- Check both execution evidence and the final artifact: review logs/stdout for successful completion of analysis steps, then confirm the written file actually reflects the computed values and required flags.
- Cross-check the completed artifact against your results map so every required metric/flag is populated exactly once, no expected field was omitted, and no near-match metric names were introduced.
- If helper functions or utilities were used, verify that final output keys/metric names match the helpers' actual return fields, types, and key names rather than assumed ones.
- If you changed one utility call or metric definition, rerun the full pipeline and re-check dependent fields before finalizing.
- Do not report or justify metrics, graph values, or flags unless you directly verified them in the completed artifact or in explicit tool output.
- Before finishing, also verify compliance with any task-specified interaction contract: required tool/action syntax, required response format, and exact completion token.
- Perform this protocol check separately from content validation: (1) required tool/action syntax was used on every step, and (2) the final response is exactly the mandated completion signal with no extra summary text if the environment requires a bare terminator.
- Use the task's requested deliverable as the boundary for final claims: mention only metrics/flags/labels that the task required and that you directly verified in the completed artifact or explicit tool output.

- Base the final narrative only on values directly observed in the completed output artifact, and ensure the narrative matches the actual computed values and detection logic used.


## Validation Before Finalizing

## Completion Discipline

- Once the required output artifact is complete and verified, stop. Do not delete, rewrite, or "clean up" helper scripts/files unless the task explicitly requires it.
- Prefer a stable handoff: produce the deliverable, verify it fully, and terminate with the mandated completion signal.

- Before emitting the completion signal, make one last pass: (1) required protocol followed exactly, (2) full artifact verified rather than partially previewed, and (3) final statements limited to verified outputs only.
- If the environment requires an exact completion token, emit that exact string and nothing else after verification. Do not append prose, summaries, interpretations, or extra analysis.
- Never perform post-success cleanup that could change the verified final workspace state. Stable handoff is preferred over removing files you created during the task.
