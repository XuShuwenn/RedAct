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


## Output Writing Safety

## Output Writing Safety

- If the task asks you to fill a provided CSV/template, preserve structural rows unchanged: headers, comment lines, blank lines, delimiter, and expected row order unless the task says otherwise.
- Only update data rows that correspond to computed metric names; do not rewrite headers or labels as if they were metrics.
- Do not perform exact-match full-file replacements unless you have read and verified the full current file contents.
- If only part of a file has been inspected, use a safer update method: edit only verified lines/fields or rewrite from structured data after confirming the expected schema.

## Tips

- Sort packets by timestamp for timing calculations
- Skip missing values in entropy computation
- Use scapy or pyshark for PCAP parsing

## Tips

## Validation Before Finalizing

- Re-open the produced output artifact and verify the full file; do not rely on a truncated preview or the first few lines.
- Confirm every required metric/flag/row from the task is present exactly once and populated, and that structural rows remain intact.
- If output is truncated or partially visible, fetch the missing rows/fields or run targeted checks before declaring success.
- Base the final narrative only on values directly observed in the completed output artifact, and ensure the narrative matches the actual computed values and detection logic used.
