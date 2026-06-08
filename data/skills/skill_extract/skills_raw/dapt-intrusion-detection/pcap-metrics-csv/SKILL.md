---
name: pcap-metrics-csv
description: "Compute network metrics and intrusion flags from a PCAP and populate a metric,value CSV while preserving comments."
---

# PCAP Metrics and CSV Population

A reusable workflow to extract core traffic statistics, graph features, timing metrics, flow counts, and intrusion flags from a PCAP, then fill a `metric,value` CSV template. Comment lines in the CSV must remain unchanged.

## When to Use

Use this skill when you need to:
- parse a PCAP and compute protocol counts, timing/rate, size stats, entropy, graph metrics, IAT stats, producer/consumer counts, flow metrics, and simple intrusion flags
- populate an existing CSV template where only the `value` column should be filled, and lines beginning with `#` must be preserved

## Core Workflow

Prefer the pcap-analysis helper utilities when available. If unavailable, follow the fallback algorithmic notes inline.

1) Load and split
- Load all packets once.
- Split by protocol layers for reuse: TCP, UDP, ICMP, ARP, and IP-containing packets.

2) Protocol counts
- protocol_tcp: count packets with TCP layer
- protocol_udp: count packets with UDP layer
- protocol_icmp: count packets with ICMP layer
- protocol_arp: count packets with ARP layer
- protocol_ip_total: count packets with an IP layer

3) Timestamps and duration
- Extract float timestamps from packets and sort.
- duration_seconds = last_ts − first_ts (0 if fewer than 2 timestamps).

4) Packets per minute (PPM)
- Bucket timestamps into contiguous 60s windows using the minimum timestamp as origin.
- Compute packets_per_minute_avg/max/min across the buckets actually observed. If no timestamps, all zero.

5) Sizes
- lengths = len(pkt) for each packet.
- total_bytes = sum(lengths)
- avg_packet_size = total_bytes / count
- min_packet_size, max_packet_size over lengths (0 for empty input)

6) Entropy (Shannon)
- Build frequency counters:
  - IPs: src and dst from IP packets only
  - Ports: src/dst from TCP and UDP only
- Shannon entropy H = −Σ p(x) log2 p(x) over observed values; if no values, return 0.
- Report src_ip_entropy, dst_ip_entropy, src_port_entropy, dst_port_entropy.
- unique_src_ports, unique_dst_ports = number of distinct observed ports.

7) Directed IP graph
- Nodes: distinct IPs seen as src or dst.
- Edges: unique (src_ip → dst_ip) pairs from IP packets.
- num_nodes, num_edges
- network_density = num_edges / (num_nodes × (num_nodes − 1)) if num_nodes ≥ 2 else 0
- max_outdegree: max count of distinct destinations per source
- max_indegree: max count of distinct sources per destination

8) Inter-arrival times (IAT)
- From sorted timestamps, IATs = differences between consecutive timestamps.
- iat_mean = mean(IATs) or 0
- iat_variance = population variance of IATs or 0
- iat_cv = std(IATs) / mean(IATs); use 0 if mean = 0

9) Producer/Consumer counts (PCR)
- For each IP (consider all nodes in the IP graph):
  - bytes_sent: sum of lengths where IP is src
  - bytes_recv: sum where IP is dst
  - PCR = (sent − recv) / (sent + recv); skip if denominator = 0
- num_producers: PCR > 0.2
- num_consumers: PCR < −0.2

10) Flows (5-tuple)
- Flow key = (src_ip, dst_ip, src_port, dst_port, protocol) for TCP and UDP only.
- unique_flows: number of distinct keys
- tcp_flows, udp_flows: counts restricted by protocol
- bidirectional_flows: number of flow pairs where reverse key exists, divided by 2

11) Intrusion flags (prefer helper thresholds)
- has_port_scan: use the provided helper if available, passing TCP packets. Avoid ad-hoc thresholds.
- has_dos_pattern: use helper with PPM avg and max
- has_beaconing: use helper with iat_cv
- is_traffic_benign = not (has_port_scan or has_dos_pattern or has_beaconing)
- Output flags as lowercase strings: "true" or "false".

12) Populate the CSV
- Read the existing CSV as raw lines.
- Preserve the header as-is.
- Preserve any line starting with '#', unchanged.
- For data lines: if the metric exists in your results mapping, replace the value after the first comma with your computed result; otherwise keep the line unchanged.
- Write the file back, ensuring a trailing newline.

## Preferred Helper Functions (if available)

- load_packets(pcap_path) -> list of packets
- split_by_protocol(packets) -> dict with keys: 'tcp','udp','icmp','arp','ip'
- packet_timestamps(packets) -> sorted list of float timestamps
- packets_per_minute_stats(timestamps) -> {'packets_per_minute_avg','packets_per_minute_max','packets_per_minute_min'}
- port_counters(tcp_packets, udp_packets) -> (src_port_counter, dst_port_counter)
- ip_counters(ip_packets) -> (src_ip_counter, dst_ip_counter)
- shannon_entropy(counter) -> float
- graph_metrics(ip_packets) -> {'num_nodes','num_edges','network_density','max_indegree','max_outdegree','_graph_state': (..., ..., all_nodes)}
- iat_stats(timestamps) -> {'iat_mean','iat_variance','iat_cv'}
- producer_consumer_counts(ip_packets, all_nodes) -> {'num_producers','num_consumers'}
- flow_metrics(tcp_packets, udp_packets) -> {'unique_flows','bidirectional_flows','tcp_flows','udp_flows'}
- detect_port_scan(tcp_packets) -> bool
- detect_dos_pattern(ppm_avg, ppm_max) -> bool
- detect_beaconing(iat_cv) -> bool

Notes:
- packets_per_minute_stats and iat_stats expect timestamps, not packet objects.
- For producer_consumer_counts, pass the all_nodes set returned by graph_metrics (often at g['_graph_state'][2]).
- flow_metrics expects TCP and UDP packet lists, not all packets.

## Verification Checklist

Cross-check before writing final results:
- Protocol sanity: protocol_tcp + protocol_udp + protocol_icmp ≤ protocol_ip_total
- ARP + IP-containing packets ≤ total packet count
- Duration ≥ 0; if no timestamps, duration = 0 and PPM stats = 0
- Size bounds: 0 ≤ min_packet_size ≤ avg_packet_size ≤ max_packet_size
- Entropy bounds: 0 ≤ entropy; entropy ≤ log2(unique_values) when applicable
- Graph bounds: 0 ≤ num_edges ≤ num_nodes × (num_nodes − 1); density in [0,1]
- Flow bounds: tcp_flows + udp_flows ≥ max(tcp_flows, udp_flows); bidirectional_flows ≤ unique_flows / 2
- IAT: iat_cv = 0 if iat_mean = 0
- PCR: counts only from IPs with sent+recv > 0
- CSV: header intact, comment lines unchanged, only value column updated, booleans lowercase

## Common Pitfalls and How to Avoid Them

- Wrong input types to helpers
  - Symptom: KeyError/wrong keys or nonsense results.
  - Fix: Pass timestamps to packets_per_minute_stats and iat_stats; pass TCP/UDP lists to flow_metrics; pass all_nodes to producer_consumer_counts.

- Reinventing detection thresholds
  - Symptom: Flags differ from expected behavior.
  - Fix: Use detect_port_scan, detect_dos_pattern, detect_beaconing from helpers instead of custom logic.

- Double-counting bidirectional flows
  - Symptom: bidirectional_flows too large.
  - Fix: Count pairs in both directions and divide by 2.

- Damaging CSV comments/header
  - Symptom: Added trailing commas to comment lines or altered header.
  - Fix: Treat lines starting with '#' and the header line as immutable; update only metric rows.

- Division by zero and empty data
  - Symptom: Exceptions or NaNs.
  - Fix: Guard duration, IAT, PCR, and density with explicit zero handling.

- Unsorted timestamps
  - Symptom: Negative IATs or wrong duration.
  - Fix: Always sort timestamps before duration/IAT calculations.

## Optional Script Usage

A small helper is provided to safely update a `metric,value` CSV with computed results while preserving comments and formatting.

Example usage:
- Produce a JSON file (or JSON on stdin) mapping metric -> value
- Run: python scripts/update_csv_values.py --csv /path/to/network_stats.csv --json /path/to/results.json
- Or: cat results.json | python scripts/update_csv_values.py --csv /path/to/network_stats.csv

Success criteria:
- All required metrics present in the CSV have values
- No comment/header corruption
- Flags are lowercase "true"/"false"
- Numerical invariants pass the Verification Checklist
