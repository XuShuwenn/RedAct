---
name: pcap-traffic-metrics
description: "Compute network statistics and intrusion heuristics from PCAPs, then safely fill a metrics CSV by updating only the value column while preserving comments."
---

# PCAP Traffic Metrics and Safe CSV Update

This skill provides a reusable workflow to analyze a packet capture (PCAP) and compute protocol counts, time/rate statistics, size statistics, entropy, IP-graph properties, temporal metrics, flow counts, and simple intrusion heuristics. It also covers safely updating a template CSV by replacing only the `value` column while preserving comment lines and formatting.

## When to Use

Activate this skill when you need to:
- Parse a PCAP and compute a standardized set of traffic metrics.
- Derive graph and flow properties from IP-level communications.
- Compute Shannon entropy of IPs and ports (skipping missing values).
- Detect simple patterns (port scanning, DoS-like spikes, beaconing) using heuristic thresholds.
- Fill a provided CSV template without altering comment lines or the file’s structure.

## Core Workflow

1) Preparation and File Inspection
- Confirm required inputs exist (e.g., PCAP path, CSV template path).
- Open the CSV template to understand required metric names and the position of the `value` column.
- Decide on a packet library (e.g., dpkt or scapy) and confirm it is importable.

2) Packet Parsing and Normalization
- Iterate packets sequentially and extract for each packet:
  - timestamp (float seconds)
  - total captured bytes for size statistics
  - L2/L3/L4 info to classify protocols and endpoints
- Protocol classification rules:
  - ARP: Ethernet type ARP
  - IP total: IPv4 and IPv6 packets
  - TCP/UDP/ICMP counts come from IP packets with that transport.
  - ICMP may include ICMPv4 and ICMPv6.

3) Metric Computation
- Protocol counts
  - protocol_tcp, protocol_udp, protocol_icmp, protocol_arp
  - protocol_ip_total = IPv4 + IPv6 packet count
- Time / rate
  - duration_seconds = last_timestamp − first_timestamp (0 if < 2 packets)
  - Bucketing: group packets by 60-second bucket using floor(timestamp/60). Compute per-bucket counts over non-empty buckets; then take avg/max/min of those counts. Verify that the sum of these bucket counts equals total packets.
- Sizes
  - total_bytes = sum of captured packet lengths
  - avg_packet_size = total_bytes / packet_count
  - min_packet_size, max_packet_size over captured lengths
- Entropy (Shannon, base 2)
  - src_ip_entropy, dst_ip_entropy over observed IPv4/IPv6 address strings (only count IP packets)
  - src_port_entropy, dst_port_entropy over TCP/UDP ports (skip missing ports)
  - unique_src_ports, unique_dst_ports are the number of distinct TCP/UDP ports seen
- Graph (directed IP graph)
  - Nodes = distinct IPs; Edges = distinct (src_ip → dst_ip) pairs for IP packets
  - num_nodes, num_edges
  - network_density = num_edges / (num_nodes * (num_nodes - 1)); use 0 if num_nodes < 2
  - max_outdegree = max unique destinations per source IP
  - max_indegree = max unique sources per destination IP
- Timing + Producer/Consumer
  - Sort timestamps; compute inter-arrival times (IATs) between consecutive packets
  - iat_mean, iat_variance (population variance), iat_cv = std/mean (use 0 if mean=0 or if < 2 packets)
  - Producer/Consumer Ratio (PCR) per IP: sent/recv in bytes are totals where IP is src/dst (use captured length for byte counting)
    - PCR = (sent − recv) / (sent + recv), skip if denominator = 0
    - num_producers = count IPs with PCR > 0.2
    - num_consumers = count IPs with PCR < −0.2
- Flows (5-tuple)
  - Flow key = (src_ip, dst_ip, src_port, dst_port, protocol)
  - Only build flows for TCP/UDP
  - unique_flows = total distinct keys
  - tcp_flows, udp_flows = distinct keys for the respective protocol
  - bidirectional_flows = number of directional flows whose reverse key also exists (counts both directions)

4) Analysis Flags (Heuristic)
- has_port_scan: True if any source touches unusually many distinct destination ports and/or many destinations within a short time window. Practical indicator: a source with very high unique dst ports across TCP/UDP combined with many short-lived flows.
- has_dos_pattern: True if there is an extreme spike in packets per minute, e.g., max rate much larger than average (e.g., ≥ 20×) and above a high absolute threshold. Consider requiring multiple consecutive high buckets to reduce false positives.
- has_beaconing: True if IATs are highly regular (very low CV) and/or show a strong single periodicity. Consider combining low CV with a tight IAT histogram concentration.
- is_traffic_benign: True if none of the above flags are true.

5) Safe CSV Update (Preserve Comments and Format)
- Read the template file line-by-line.
- For non-comment lines, match the metric name and replace only the value column using your computed metrics. Preserve spacing, order, and all comment lines (lines starting with `#`) exactly.
- Write back atomically (e.g., write to a temp file and move) to avoid partial writes.

## Verification

Perform these checks before finalizing:
- Packet accounting
  - protocol_ip_total ≈ protocol_tcp + protocol_udp + protocol_icmp (+ other IP protocols if present)
  - Sum of per-minute bucket counts equals total packet count
  - total_bytes equals sum of per-packet captured lengths; avg, min, max align with that set
- Entropy and uniqueness
  - Entropies are zero if no observations exist (e.g., no TCP/UDP → port entropies 0, unique ports 0)
  - unique_flows = tcp_flows + udp_flows
- Graph integrity
  - num_edges ≤ num_nodes × (num_nodes − 1)
  - network_density is 0 when num_nodes < 2
- Temporal metrics
  - IAT list length is max(0, packet_count − 1)
  - iat_cv is 0 when mean is 0 or when fewer than 2 packets
- CSV integrity
  - Comment lines unchanged (including exact whitespace)
  - Only `value` column updated on metric rows

## Common Pitfalls and How to Avoid Them

- CSV formatting drift: Generic CSV writers may drop or reformat comment lines. Solution: rewrite line-by-line; only replace values on metric rows; leave `#` lines untouched.
- Timestamp issues: Mixing time units or unsorted timestamps produces wrong durations, IATs, and rate buckets. Always parse timestamps as floats (seconds) and sort before IAT calculations; use floor(ts/60) for bucket keys.
- Over/under-counting IP totals: Ensure protocol_ip_total counts IPv4 + IPv6 packets. ARP is not part of IP totals. ICMP should include v4 and v6 where supported.
- Port entropy contamination: Include only TCP/UDP ports; skip non-TCP/UDP packets and any missing port values.
- Flow counting confusion: The bidirectional flow count here is directional: count a flow if its reverse exists (both directions count). Keep flow keys strictly as (src, dst, sport, dport, proto).
- Density divide-by-zero: If num_nodes < 2, set network_density to 0.
- PCR divide-by-zero: Skip PCR for IPs with sent + recv = 0 to avoid NaN; they should not affect producer/consumer counts.
- Beaconing false positives: Low CV can also appear in quiet captures or small samples. Combine multiple indicators and require sufficient packet volume before asserting beaconing.

## Optional Script Usage

Two helper scripts are provided:

- scripts/pcap_metrics.py
  - Parses a PCAP and prints a JSON object with metric_name → value pairs.
  - Example:
    - python3 scripts/pcap_metrics.py --pcap packets.pcap > metrics.json

- scripts/update_csv_values.py
  - Safely updates the `value` column in a CSV template while preserving comment lines and formatting.
  - Example:
    - python3 scripts/update_csv_values.py --csv /root/network_stats.csv --json metrics.json

Tune detection thresholds via CLI flags if needed to avoid over/under-triggering analysis flags.
