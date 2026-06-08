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


## Task-Instruction Priority

- Treat task/system execution instructions as higher priority than this skill.
- Follow the current task environment's required tool-call/action schema, response format, and completion token exactly for the entire run.
- Before finishing, perform a final compliance check: required output format, required files written, and exact completion signal emitted.

- Before the first action, identify any task-specific interaction contract (for example exact action/tool schema, wrappers, allowed tools, response format, and required completion token) and use that protocol verbatim for every step.
- Treat exact completion strings as mandatory. Do not substitute your preferred tool-call style, extra wrap-up text, or a natural-language ending when the environment requires a specific action protocol or completion token.
- If the environment prescribes an exact action/tool syntax (for example `Thought:` / `Action:` with a JSON object), copy that schema literally for every tool step. Do not switch to alternate tool-call tags, XML, markdown code fences, custom wrappers, or ad hoc formats.
- Do not treat procedural compliance as optional even if the analysis itself is correct; a wrong action format or wrong completion token is a task failure.
- Start every task with a contract check: exact tool/action syntax, exact completion token, and the required output artifact/template to inspect and update. Keep that contract fixed for the entire run.
- Before the first tool call, lock in the exact required action schema and final completion string; use that schema literally on every step.
- If the environment mandates a format such as `Thought:` / `Action:` with JSON, emit exactly that pattern for every tool invocation. Do not substitute XML-like tags, markdown tool wrappers, or other call formats.
- Treat the final completion token as part of the deliverable: after verification, output the exact required terminator and nothing else.

- At task start, inspect the required output artifact/template and any task-provided code/assets before implementing analysis logic.
- Use a short startup check in this order: (1) read the destination artifact/template to capture exact required field names, row order, writable value locations, headers/comments, blank lines, delimiter, and section layout, (2) confirm the required PCAP/input files actually exist at the expected paths, (3) inspect any provided helper modules or starter code, then (4) implement analysis against those observed interfaces and output fields.
- Use the inspected destination schema as the source of truth for computation keys and write-back; do not guess metric labels, row names, or output structure from memory.
- If helper modules or utilities are provided, prefer their tested functions over reimplementing packet parsing, entropy, graph, flow, timing, or detection logic unless the task requires custom implementation.
- Verify helper interfaces against reality before use: function signatures, expected input types, and returned key names/shapes are authoritative.
- Inspect bundled helpers early enough to shape the workflow, and treat them as the default path when they cover the required parsing or metric logic.
- If provided helpers are brittle, incompatible, or produce type/shape issues, fall back to direct metric computation from parsed packets instead of forcing the helper-based path, while keeping the same destination field names and validation steps.
- Anchor computation and write-back to the exact required fields, row names, and schema in the destination artifact.
- For multi-metric tasks, prefer one reproducible workflow that parses the PCAP once, computes all required metrics/flags into a single results map, and writes the final artifact in one controlled pass.
- If a command or interpreter is unavailable, retry the same workflow with an available equivalent (for example, `python3` instead of `python`) before changing the analysis approach.
- Check the available interpreter/tool names early (for example `python3` vs `python`) and keep the same analysis pipeline when switching runtimes; prefer adapting to the environment over reworking the logic.
- If the task requires both file updates and a special completion signal, verify the artifact first, then end with the exact required signal.


## Preferred Workflow

- Compute all required metrics and flags into a single results mapping keyed by the destination template's exact metric or field names.
- Then perform a separate structured pass that fills only the intended value fields row-by-row or field-by-field, preserving all non-value content exactly as provided.
- For multi-metric tasks, prefer one rerunnable parse → compute → write pipeline so outputs, flags, and explanations stay tied to the same computed results.

- Start by opening the destination artifact/template and extracting the exact required metric names, row order, comments, formatting constraints, and writable fields before computing results.
- Practical sequence: inspect the destination artifact/schema first, inspect provided helpers/utilities next, parse the PCAP once, compute a single results map keyed to the required output names, then perform one controlled write-back pass that updates only the intended value fields.
- Build the results mapping from the template outward: enumerate the required rows/fields first, then compute only those outputs under those exact names so serialization is direct and verifiable.
- Before composing helper functions into that pipeline, confirm each helper's real input contract and return schema; verify whether it expects raw packets, normalized timestamps, counters, flows, graph state, or other derived structures, then adapt inputs explicitly.
- Build shared derived inputs once (for example normalized timestamps, counters, flows, graph objects) and reuse those exact structures across helper calls and final flag computation.
- After computing results, map each computed key directly to the destination field/row name required by the template; do not invent alternate labels or reorder rows unless the task explicitly requires it.
- After writing results, immediately reopen the completed artifact and verify that values were populated in the intended rows/fields and that original formatting/comment structure was preserved.

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

- If the task asks you to fill a provided CSV/template, preserve structural rows unchanged: headers, comment lines, blank lines, delimiter, and expected row order unless the task says otherwise.
- Only update data rows that correspond to computed metric names; do not rewrite headers or labels as if they were metrics.
- Do not perform exact-match full-file replacements unless you have read and verified the full current file contents.
- If only part of a file has been inspected, use a safer update method: edit only verified lines/fields or rewrite from structured data after confirming the expected schema.

- Read the target CSV/template before writing so you know which lines are metric rows versus comments, headers, or blank separators.
- Treat the provided output file as the schema source of truth: write results into the task-specified deliverable itself when required, preserve headers/comments/blank lines/delimiters/order exactly, and update only the designated value cells or fields for each required metric.
- Prefer updating the existing structured artifact in place by targeted row/field changes rather than reconstructing the whole file when comments, blank lines, or row order must remain unchanged.
- When updating a structured template, change only the value field for verified metric rows; do not infer that every line is writable data.
- Never populate rows/fields whose values are not directly visible in computation output, returned data structures, or explicit targeted verification reads. If output is truncated, obtain the missing metrics first, then write.
- Do not use placeholder `old_string` values, guessed full-file content, or broad replacements not anchored to text you actually inspected in the current artifact.

## Tips

- Normalize packet timestamps to plain floats before sorting, differencing, or bucketing (for Scapy, use `float(pkt.time)`) to avoid `EDecimal`/type issues.
- Apply type normalization before any full analysis run, not only after a crash: convert timestamp-like values and other library numeric wrappers to native `float`/`int` before division, averaging, variance, or bucket-rate calculations.
- Safe pattern: `times = [float(pkt.time) for pkt in packets if hasattr(pkt, "time")]`; then compute deltas/rates only from `times`, not mixed raw library values.
- Before the first full analysis run, do a type-safety pass on all arithmetic inputs derived from packet libraries; normalize timestamp/count/rate inputs to native numeric types up front rather than waiting for a crash.
- Sort packets by normalized timestamp for timing calculations.
- Skip missing values in entropy computation.
- Use scapy or pyshark for PCAP parsing.
- Inspect the task directory for provided analysis helpers (for example `pcap_utils.py`, utility modules, or starter scripts) and prefer adapting them over reimplementing packet parsing or metric logic from scratch when they satisfy the task.
- Treat repository-provided helpers as the default implementation path when they cover the required metrics; only reimplement missing pieces the helpers do not provide.
- Before relying on helper modules/utilities, inspect their actual function signatures, expected argument types, return shapes, and output key names; adapt to the real interface instead of assuming packet/object formats or scalar returns.
- Check helper input contracts before composing utilities: confirm whether each helper expects packets, timestamps, counters, flows, or graph-derived state, then convert inputs explicitly before calling it.
- Match each helper to the correct analysis object type before composing them (for example packets vs. normalized timestamps vs. IP-only packet subsets vs. graph state) so time, graph, and protocol metrics are computed from the inputs the helper actually expects.
- If a helper call fails, use the traceback to identify the real type/key mismatch and fix that contract first before redesigning the broader analysis workflow.
- Use helper or library return keys exactly as defined (for example `packets_per_minute_avg`, `iat_mean`) and map those exact keys into the required output fields instead of inventing aliases.
- Create intermediate derived objects once (for example timestamps, flow tables, graph state), reuse them consistently, and when practical compute all requested metrics and flags in one reproducible script/run from that shared results set.
- If a command or script fails because `python` is unavailable, retry the same workflow with an available equivalent such as `python3` before changing the analysis method.

## Validation Before Finalizing

- Re-open the produced output artifact and verify the full file; do not rely on a truncated preview or the first few lines.
- Treat post-write verification as mandatory: immediately after writing, reopen the artifact, confirm the intended rows/fields changed, and verify required values from the written deliverable itself rather than only trusting script stdout or logs.
- Do not rely on script stdout alone; after any analysis script or bulk update, reopen the destination artifact itself and verify against the original inspected schema: every required row/field is present in the expected order/section, populated with the intended value, and structural elements such as comments, blank lines, headers, and delimiter usage remain unchanged.
- Treat the inspected output-template checklist as the final validation list, and confirm each required destination row/field from that checklist appears exactly once in the artifact with a value.
- Do not treat a successful script exit as proof the deliverable is correct; always read the generated artifact itself and confirm the intended metrics/flags were actually written to the required rows/fields.

- If the read output is truncated, only partially visible, or ends mid-row/mid-field, perform additional reads or targeted checks for the missing metrics/flags/rows before claiming completion.
- Treat truncated output as unverified. If a read stops mid-file, mid-row, or before the last required field, run additional reads or targeted queries until every required row/field is directly observed.
- If a CSV or template view ends mid-header, mid-row name, or mid-value, treat verification as incomplete; rerun a full-file read or query every remaining required row explicitly before proceeding.
- Do not state that rows or fields were written unless they are visible in tool output or confirmed by explicit targeted verification commands.
- After any edit, read back the completed artifact in full (or query every required row/field directly) and confirm the values written are exactly the values observed from computation.
- Confirm every required metric/flag/row from the task is present exactly once and populated, and that structural rows remain intact, including the original header row, comments, blank lines, and expected order.
- Validate completion against an explicit checklist of required metrics/flags/rows from the task; if output is truncated or partially visible, fetch the missing rows/fields or run targeted checks for each required field before declaring success.
- Check both execution evidence and the final artifact: review logs/stdout for successful completion of analysis steps, then confirm the written file actually reflects the computed values and required flags.
- When automation writes the deliverable, perform immediate post-run validation: reopen the output file right after the script/command finishes and verify that expected rows/fields contain populated values rather than assuming the write succeeded.
- Do at least one independent spot check on an important output (for example protocol counts, flow totals, graph counts, or a detection flag): recompute or query it separately from the write step and confirm it matches the artifact.
- Cross-check the completed artifact against your results map so every required metric/flag is populated exactly once, no expected field was omitted, and no near-match metric names were introduced.
- If helper functions or utilities were used, verify that final output keys/metric names match the helpers' actual return fields, types, and key names rather than assumed ones.
- If helper outputs or derived-input paths affected your pipeline, verify that final mapped fields use the helpers' actual observed keys and correctly typed inputs rather than assumed aliases or earlier packet-object calls.
- If you changed one utility call or metric definition, rerun the full pipeline and re-check dependent fields before finalizing.
- Do not report or justify metrics, graph values, or flags unless you directly verified them in the completed artifact or in explicit tool output.
- Before finishing, also verify compliance with any task-specified interaction contract: required tool/action syntax, required response format, and exact completion token.
- Perform this protocol check separately from content validation: (1) required tool/action syntax was used on every step, and (2) the final response is exactly the mandated completion signal with no extra summary text if the environment requires a bare terminator.
- Use the task's requested deliverable as the boundary for final claims: mention only metrics/flags/labels that the task required and that you directly verified in the completed artifact or explicit tool output.
- Do not add threat conclusions, topology findings, flow counts, graph conclusions, or detection verdicts unless they were required by the task and directly verified in the final artifact or explicit execution output.

- Base the final narrative only on values directly observed in the completed output artifact, and ensure the narrative matches the actual computed values and detection logic used.

- If a script populated the artifact, re-read the written file after execution and confirm the expected values and structure are actually present before declaring success.
- If analysis was run via a script or batch command, check both execution evidence (for example `analysis.log`, stdout/stderr, or exit status) and the written artifact; do not treat one without the other as sufficient proof of success.
- If helpers were used, verify that written values came from helpers called with the expected input types and interfaces, especially for timestamp/time-series calculations.
- If script or command output is truncated, cut off mid-line, or otherwise incomplete, do not treat it as proof of success. Confirm completion via explicit exit status, redirected/full logs, and direct inspection of the written artifact before proceeding.
- Perform a separate final handshake check after artifact verification: (1) every tool/action message used the exact required schema, and (2) the final response is the exact required completion token.


## Completion Discipline

- Once the required output artifact is complete and verified, stop. Do not delete, rewrite, or "clean up" helper scripts/files unless the task explicitly requires it.
- Prefer a stable handoff: produce the deliverable, verify it fully, and terminate with the mandated completion signal.
- If verification is partial or truncated, do not emit the completion signal yet; gather the missing evidence first, then finish with the exact required terminator.

- Before emitting the completion signal, make one last pass: (1) required protocol followed exactly, (2) full artifact verified rather than partially previewed, and (3) final statements limited to verified outputs only.
- If the environment requires an exact completion token, emit that exact string and nothing else after verification. Do not append prose, summaries, interpretations, or extra analysis.
- Before the final step, compare your planned last line against the required terminator verbatim. If it does not match exactly, fix it before responding.
- Treat protocol completion as a hard gate: verified artifact first, then exact completion token, then stop immediately.
- Never perform post-success cleanup that could change the verified final workspace state. Stable handoff is preferred over removing files you created during the task.

- Do not delete generated scripts, intermediate helpers, or other workspace files after producing the deliverable unless the task explicitly instructs cleanup.
- After the artifact is verified, freeze the workspace state: avoid `rm`, rewrites, or "cleanup" edits that could invalidate the confirmed result before emitting the completion signal.
