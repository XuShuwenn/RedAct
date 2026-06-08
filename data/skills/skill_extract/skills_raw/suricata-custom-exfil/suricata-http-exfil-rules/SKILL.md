---
name: suricata-http-exfil-rules
description: "Design and validate Suricata signatures for HTTP exfil patterns using method/URI/header/body conditions and offline PCAP testing with resource-aware run modes."
---

# Suricata HTTP Exfiltration Signature Development

Create precise Suricata rules for detecting custom exfiltration hidden in HTTP telemetry by combining method, path, header, and request-body constraints. Validate offline against provided PCAPs, including in constrained environments.

## When to Use

Activate this skill when you need to:
- Detect HTTP-based exfiltration patterns that require multiple simultaneous conditions.
- Match exact paths and custom headers while minimizing false positives.
- Validate rules offline against positive/negative PCAPs, especially in low-memory or resource-constrained environments.

## Core Workflow

1) Triage the traffic to define precise conditions
- Use protocol-aware tools to extract what matters:
  - Methods and URIs: `tshark -r <pcap> -Y http.request -T fields -e http.request.method -e http.request.uri`
  - Headers: `tshark -r <pcap> -Y http.request -T fields -e http.host -e http.user_agent -e http.accept -e http.request.full_uri`
  - Request body: `tshark -r <pcap> -Y http.request -T fields -e http.file_data`
- Compare positive vs negative captures. Identify the single differentiator(s): exact path, specific header value, parameter shape (length/charset) in the request body.

2) Draft the Suricata rule
- Scope the flow:
  - `flow:established,to_server;` to restrict to client-to-server HTTP requests.
- Method and URI:
  - `http.method; content:"POST";` (use `nocase;` only if requests in your environment vary in case)
  - Exact path: Prefer simple, robust constructs on `http.uri`:
    - `http.uri; content:"/your/exact/path"; startswith; endswith;`
    - Alternatively, PCRE anchored to entire path in the URI buffer:
      - `http.uri; pcre:"/^\/your\/exact\/path$/";`
- Header constraint:
  - Use `http.header` sticky buffer with a reliable content construct that survives normalization (Suricata normalizes header newlines to `\n`).
  - Example (case-insensitive): `http.header; content:"x-custom-mode|3a| exfil"; nocase;`
    - `|3a|` matches `:`. Include the space after `:` if your samples consistently include it.
- Request-body constraints:
  - Prefer Suricata 7 sticky buffer `http.request_body` for decoded/normalized body.
  - Apply multiple body patterns after setting the sticky buffer once (avoid repeating the sticky buffer for each pattern):
    - Base64-like parameter with minimum length:
      - Example: `pcre:"/(^|[&])blob=[A-Za-z0-9+\/]{80,}={0,2}/";`
      - Note: Normalization may convert `+` to space for URL-encoded bodies. If matching normalized bodies, make the pattern tolerant (e.g., allow `[ +]`), or test `http_client_body` (modifier) if raw body is required.
    - Hex digest with exact length:
      - Example: `pcre:"/(^|[&])sig=[0-9a-fA-F]{64}(?![0-9a-fA-F])/";`
  - Keep all request-body `pcre` and/or `content` checks grouped under a single `http.request_body;` sticky buffer to avoid duplicate-instance warnings.

Rule skeleton (adjust names, path, and lengths as needed):
alert http any any -> any any (msg:"Custom HTTP exfil"; flow:established,to_server; http.method; content:"POST"; http.uri; content:"/your/exact/path"; startswith; endswith; http.header; content:"x-custom-mode|3a| exfil"; nocase; http.request_body; pcre:"/(^|[&])blob=[A-Za-z0-9+\/]{MIN_B64_LEN,}={0,2}/"; pcre:"/(^|[&])sig=[0-9a-fA-F]{DIGEST_LEN}(?![0-9a-fA-F])/"; sid:<your-sid>; rev:1;)

3) Validate rule syntax
- Keep each rule on a single line; multi-line rules without proper handling fail to parse.
- Run: `suricata -T -c /path/to/suricata.yaml -S /path/to/local.rules`
  - Fix any parse errors before testing against PCAPs.

4) Offline test against PCAPs
- Recommended baseline command:
  - `suricata -c /path/to/suricata.yaml -S /path/to/local.rules -k none -r /path/to/positive.pcap -l /tmp/suri-pos --runmode single`
- Resource constraints (pool grow/memcap issues):
  - First try `--runmode single` to reduce threads and memory pressure.
  - If Suricata still fails to initialize, try explicit memcap adjustments (tune up or down based on error):
    - Lower preallocation for constrained environments: `--set stream.memcap=8mb --set stream.reassembly.memcap=16mb --set flow.memcap=8mb --set host.memcap=8mb`
    - If you see errors indicating insufficient memcap for flows/sessions, increase accordingly (e.g., 64mb or 128mb as environment permits).
- Repeat for negative PCAPs with a separate `-l` directory.

5) Verify alerts
- Examine `eve.json` for alert events and confirm the expected signature ID(s) triggered only on positives.
- Ensure a single transaction does not trigger duplicate alerts unless intended; if duplicates appear, review sticky buffer usage and pattern overlap.

## Verification Checklist
- Rule parses: `suricata -T` reports OK.
- Positive PCAP(s): at least one alert with the intended SID.
- Negative PCAP(s): zero alerts.
- Method/URI/Header/Body conditions are all required for a match.
- No duplicate-instance warnings for the same sticky buffer.
- URI exactness enforced (no trailing characters or query unless intended).

## Common Pitfalls and How to Avoid Them
- Sticky buffer misuse:
  - Problem: Mixing sticky buffers and modifiers incorrectly (e.g., treating `http_client_body` as sticky) or repeating the same sticky buffer multiple times causes errors/warnings.
  - Fix: Prefer `http.request_body` sticky buffer in Suricata 7+. Set it once, then apply multiple `content`/`pcre` checks. Use `http_client_body` only as a modifier paired with `content`/`pcre` if you specifically need raw body.
- Header matching fragility:
  - Problem: PCRE using `\r\n` fails (Suricata normalizes to `\n`) or case mismatch.
  - Fix: Use `http.header; content:"header-name|3a| value"; nocase;` and avoid explicit newline assumptions.
- URI buffer choice and anchoring:
  - Problem: Using unsupported keywords (e.g., `http.uri.path`) or over-anchored PCRE with double-escaped slashes that no longer match.
  - Fix: Verify available keywords: `suricata --list-keywords=all | grep http.`. For exact path, prefer `content; startswith; endswith;` or a single-escaped PCRE like `pcre:"/^\/path$/";`.
- Body normalization:
  - Problem: Expecting `+` in URL-encoded bodies; normalized `http.request_body` may convert `+` to space.
  - Fix: Either tolerate space in the regex or switch to raw body inspection with `http_client_body` modifier patterns.
- Modifier order:
  - Problem: `nocase` not applied because it appears far from `content`.
  - Fix: Place `nocase` immediately after its associated `content`.
- Multi-line rules:
  - Problem: Breaking rules across lines without proper handling leads to parse errors.
  - Fix: Keep as single line.
- Over-broad patterns:
  - Problem: Matching `blob`/`sig` anywhere increases false positives.
  - Fix: Use parameter boundaries `(^|[&])` and proper negative lookaheads `(?![0-9a-fA-F])` or terminal markers `(&|$)`.

## Optional Script Usage

Use `scripts/suri_offline_runner.py` to run Suricata offline on one or more PCAPs with resource-aware defaults and summarize alerts by SID.

Example:
- Positive test: `python3 scripts/suri_offline_runner.py --config /path/to/suricata.yaml --rules /path/to/local.rules --pcaps /path/to/positive.pcap --runmode-single --low-mem --outdir /tmp/suri-check`
- Negative test: `python3 scripts/suri_offline_runner.py --config /path/to/suricata.yaml --rules /path/to/local.rules --pcaps /path/to/negative.pcap --runmode-single --low-mem --outdir /tmp/suri-check`

Success criteria:
- Positive run prints alert counts including your expected SID.
- Negative run prints zero alerts for that SID.
