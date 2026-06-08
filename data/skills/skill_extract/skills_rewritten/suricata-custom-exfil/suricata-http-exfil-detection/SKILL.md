---
name: suricata-http-exfil-detection
description: "Design and validate Suricata HTTP signatures for structured exfil patterns, testing against pcaps while minimizing false positives."
---

# Suricata HTTP Pattern Detection and Offline Validation

Create robust Suricata signatures for structured HTTP exfiltration patterns and validate them offline against positive and negative traffic captures.

## When to Use

Use this skill when you need to:
- Detect custom application-layer (HTTP) exfiltration patterns with precise field constraints
- Minimize false positives by combining multiple HTTP conditions
- Validate rules offline against packet captures and troubleshoot non-firing or noisy signatures

## Core Workflow

1) Inspect the traffic (both positive and negative)
- Enumerate HTTP requests in each pcap to understand the target flow and the benign baseline.
  - Example tooling:
    - List requests: `tshark -r <pcap> -Y 'http.request' -T fields -e http.request.method -e http.request.uri`
    - Follow stream to view headers/body: `tshark -r <pcap> -z follow,tcp,ascii,<stream_id> -q`
- Identify exact method, URI path, distinguishing headers, and request-body fields. Note differences in negative samples to avoid false positives.

2) Choose HTTP-aware buffers and confirm keyword support
- Use protocol-aware buffers to constrain matches to the correct part of the HTTP transaction:
  - `http.method` for the request method
  - `http.uri` (or `http.request_line` if needed) for the request path/target
  - `http.header` for headers
  - `http.request_body` (or `http_client_body` on older versions) for the request body
- Verify supported keywords in your Suricata version before writing rules:
  - `suricata --list-keywords | grep -i http`
  - If `http.request_body` is not listed, use `http_client_body` instead.

3) Build the rule incrementally
- Start with stable constraints:
  - Flow direction: `flow:established,to_server;`
  - Method: `http.method; content:"POST";`
  - Path (exact): `http.uri;` with one of:
    - `content:"/exact/path"; startswith; endswith;` (enforces exact equality), or
    - Anchored PCRE under the URI buffer: `pcre:"/^\/exact\/path$/";`
- Header match (case-insensitive, tolerant to whitespace): under `http.header;` use either
  - Single content if the engine normalizes headers sufficiently: `content:"x-custom-header: value"; nocase;` or
  - A header PCRE that tolerates spacing and case: `pcre:"/\bx-custom-header\s*:\s*value\b/i";`
- Body conditions: under `http.request_body;` (or `http_client_body;`)
  - First ensure field presence via `content:"key=";`
  - Then use PCRE for structure/length checks, e.g.:
    - Base64-like minimum length: `pcre:"/key=[A-Za-z0-9+\/=]{80,}/";`
    - Fixed-length hex: `pcre:"/sig=[0-9a-fA-F]{64}(?:[&\s]|$)/";`
- Make checks order-insensitive: repeat the body buffer before each field’s content/PCRE so each requirement is evaluated independently anywhere in the body.

4) Combine into a single signature (template)
- Replace placeholders with your exact path, header, and field names. Use an organization-unique sid.

```
alert http any any -> any any (
    msg:"HTTP exfil pattern";
    flow:established,to_server;
    http.method; content:"POST";
    http.uri; content:"<exact-path>"; startswith; endswith;
    http.header; pcre:"/\b<Header-Name>\s*:\s*<Expected-Value>\b/i";
    http.request_body; content:"blob=";
    http.request_body; pcre:"/blob=[A-Za-z0-9+\/=]{80,}/";
    http.request_body; content:"sig=";
    http.request_body; pcre:"/sig=[0-9a-fA-F]{64}(?:[&\s]|$)/";
    sid:<your-sid>; rev:1;
)
```

Notes:
- If `startswith; endswith;` for the URI is not supported, use `pcre:"/^\\/your\\/path$/";` under the `http.uri` buffer instead.
- If `http.request_body` is unsupported, switch to `http_client_body` everywhere you reference the body.

## Verification

A) Static validation (syntax only)
- `suricata -T -c <suricata.yaml> -S <rules.file>`
- Fix any parse errors before running on pcaps.

B) Offline pcap test
- Use fresh output directories per run to avoid stale logs.
- Run with conservative settings if resource issues arise:
  - Prefer a single-process runmode, reduce streams/memory via `--set` overrides if needed.
  - Example pattern: `suricata -c <suricata.yaml> -S <rules.file> -r <pcap> -l <outdir> [--runmode single] [--set key=value ...]`
- Inspect EVE alerts (JSON lines):
  - `jq 'select(.event_type=="alert") | .alert.sid' <outdir>/eve.json`
  - Confirm alerts appear for positive pcaps and do not appear for negative pcaps.

C) Load-path sanity check
- If no alerts appear, verify the rules file being used matches the file you edited:
  - Run Suricata with `-S <rules.file>` explicitly during tests.
  - Confirm the config’s `rule-files` includes your file if not passing `-S`.

D) Field-by-field isolation tests
- If combined rule doesn’t fire, test partial rules:
  - Method+path only
  - Header only (under `http.header`)
  - Body fields individually (under the body buffer)
- Recombine after confirming each component matches independently.

## Common Pitfalls and How to Avoid Them

- Mixing buffers without re-selecting them:
  - Always re-state the buffer (`http.header;`, `http.request_body;`, etc.) before each `content`/`pcre` intended for that part. Do not rely on default payload buffers for HTTP.

- Assuming adjacency across headers or between header/body:
  - Avoid `distance/within` across different buffers. Use independent checks per buffer or a header PCRE that tolerates whitespace and punctuation.

- Overly strict or brittle path matching:
  - Substring matches can cause false positives; incorrect `bsize` can cause misses. Prefer `startswith; endswith;` under `http.uri` for exact equality or an anchored PCRE.

- Case and spacing in headers:
  - HTTP header names are case-insensitive and may contain varying whitespace. Use `nocase` or a tolerant PCRE under the header buffer.

- Order sensitivity in body checks:
  - Do not assume a fixed order for body fields. Ensure each field is validated independently under the body buffer.

- Unsupported HTTP keywords across versions:
  - If `http.request_body` is unavailable, switch to `http_client_body`. Confirm with `--list-keywords`.

- Rule not loaded or wrong rules file:
  - Confirm the exact rules file Suricata loads during testing (pass `-S <rules.file>`). Watch for BOM/encoding issues in edited files.

- Resource-related startup failures:
  - Use simpler runmodes and lower memory/stream caps via `--set`. Always write to fresh output directories to avoid confusion with previous runs.

## Success Criteria

- Rule validates in test mode with no errors.
- Positive pcap(s) produce alert(s) for the rule’s sid.
- Negative pcap(s) produce zero alerts.
- Alert details show the expected HTTP fields matched.

## Optional Script Usage

A helper script is provided to automate offline tests. It:
- Validates rules (`-T`)
- Runs Suricata offline on one or more pcaps
- Summarizes alert counts, optionally filtered by a target sid

Usage examples:
- Validate and test one pcap:
  - `python scripts/suri_offline_test.py --config suricata.yaml --rules local.rules --pcap sample.pcap --sid 1234567`
- Test multiple pcaps with conservative run settings:
  - `python scripts/suri_offline_test.py --config suricata.yaml --rules local.rules --pcap pos.pcap --pcap neg.pcap --sid 1234567 --runmode single --set stream.memcap=32mb`
