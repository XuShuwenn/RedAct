---
name: suricata-custom-exfil
description: "Write Suricata signatures to detect custom HTTP telemetry exfiltration patterns in network traffic."
---

# Suricata Custom Exfiltration Detection

## When to Use

- Write Suricata IDS rules for custom exfil patterns
- Analyze PCAP files for suspicious traffic
- Avoid false positives in detection


## Execution Protocol

## Execution Protocol

- Follow any task/runtime instructions exactly when they specify tool invocation format, response schema, or final completion requirements.
- If the task requires a specific tool/action schema or wrapper, use that exact format for every tool interaction.
- Do not claim `/root/local.rules` was updated unless you performed an explicit write action.
- If the task requires an exact final completion string or output format, emit it verbatim and nothing else.

## Exfil Pattern (ALL conditions must be true)

1. HTTP POST request
2. Request path exactly: `/telemetry/v2/report` (match the whole HTTP URI/path exactly, not as a substring)
3. Header: `X-TLM-Mode: exfil`
4. Body contains `blob=` with Base64 value ≥ 80 chars
5. Body contains `sig=` with exactly 64 hex characters


Do not ship a partial rule. A rule that omits the exact path check, the required header, or either body predicate is incorrect even if it matches a sample PCAP.

Before finalizing a rule, map each condition to a detection primitive that enforces the stated scope and boundaries, not just a substring seen in sample traffic.

**Interpret exactness literally:**
- Path must be exactly `/telemetry/v2/report`, not a longer URI containing that substring.
- `blob=` must capture one parameter value whose Base64 text is at least 80 chars; bound it with `&`, whitespace, end of body, or equivalent parameter separators.
- `sig=` must be one parameter value of exactly 64 hex chars; reject longer hex strings by bounding the value with `&`, whitespace, end of body, or equivalent separators.


## Input Files

- `/root/pcaps/`: PCAP files for testing
- `/root/suricata.yaml`: Suricata config
- `/root/local.rules`: Rules file to update

- Preserve existing `/root/local.rules` content unless the task explicitly says to replace it.
- Unless the task explicitly says otherwise, modify only `/root/local.rules`.

**Scope constraint:** Do **not** edit `/root/suricata.yaml` as a workaround for testing or validation.

## Evidence Gathering

- Inspect the HTTP request directly before writing the rule; do not infer headers, path, or body fields from summaries or truncated output.
- If a packet summary does not visibly show `POST`, `/telemetry/v2/report`, `X-TLM-Mode`, `blob=`, and `sig=`, run a more targeted command and verify those fields from actual output.
- Prefer commands that expose application data, e.g. `tcpdump -A -s 0 -r <pcap>` with an appropriate filter, or `tshark -r <pcap> -Y http -V`.
- Base the rule on observed traffic only. Do not state that a pcap contains specific headers, paths, or body parameters unless the command output actually shows it.


## Required Workflow

1. Inspect `/root/local.rules` before editing.
2. Inspect available files in `/root/pcaps/` to understand what traffic is provided for validation.
3. Draft the full rule first, then write it to `/root/local.rules` with an explicit file modification command; do not overwrite the file with partial or placeholder content.
4. Re-open `/root/local.rules` and confirm the rule text is present.
5. Run `suricata -T -S /root/local.rules -c /root/suricata.yaml` to catch syntax and sticky-buffer errors.
6. If PCAPs are provided, verify behavior on them: the rule should alert on intended positive traffic and stay quiet on negative traffic.
7. Do not claim success until the write and at least one decisive verification step have actually occurred; if runtime validation is blocked, state that explicitly.

## Output

Update `/root/local.rules` with a single Suricata rule using `sid:1000001`.

Target outcome:
- Alert only when all 5 conditions match
- Keep changes limited to the rule file
- The rule logic itself must explicitly encode all 5 listed conditions; do not infer missing constraints from sample traffic or partial tests
- If runtime validation is incomplete, say so explicitly rather than claiming the alert was observed

Hard requirements:
- Make an explicit file write to `/root/local.rules`; do not just describe the intended change.
- Preserve the required SID exactly: `1000001`.
- After writing, read `/root/local.rules` back and confirm the expected rule text is present while preserving existing rules.
- Before declaring success, run `suricata -T -c /root/suricata.yaml -S /root/local.rules`.
- If PCAP testing is part of the task, also verify behavior on sample PCAPs: confirm the rule alerts on a positive capture and stays quiet on a negative/non-matching capture.

Do not stop at parse success. Final completion requires evidence that the rule both loads and alerts on matching traffic when feasible. If direct runtime testing is blocked, state that explicitly and keep the rule/task incomplete rather than claiming success from reasoning alone.

Do not claim success if all verification attempts failed. Report the rule plus the exact validation evidence obtained, or explicitly state that runtime validation was blocked.


## Suricata Rule Format

```suricata
alert tcp any any -> any any (msg:"Custom Exfil"; ...; sid:1000001;)
```

Use HTTP sticky buffers carefully: declare a given sticky buffer once, then place all related `content`/`pcre` checks under it until switching buffers. Do **not** repeat `http.request_body;` before each body condition; Suricata can reject this as a duplicate sticky-buffer instance.

Use exact field/value matching for required HTTP elements. Do **not** replace a required header/value pair with a broad substring check.

For HTTP header matching with `http.header` + `content`, treat header names as case-insensitive: add `nocase` or use a pattern robust to capitalization.

When a rule must enforce both an HTTP header condition and request-body conditions, treat buffer selection as a design constraint, not a cosmetic modifier choice. Read [HTTP header/body structure for Suricata rules](references/http-buffer-structure.md) before writing or revising such a rule.


- Constrain matches to the correct HTTP buffers (`http.method`, `http.uri`, header buffer, `http.request_body`).
- Scope checks to HTTP app-layer buffers; do not satisfy the 5 conditions with generic payload matching when HTTP sticky buffers are available.
- Match the header as a value match, not as separate loose tokens. For this task, prefer `content:"X-TLM-Mode|3a 20|exfil"; http_header; nocase;` (or an equivalent case-safe exact-value form) over separate `x-tlm-mode` and `exfil` contents.
- For exact path requirements, do **not** rely on `content:"/telemetry/v2/report"` alone; that permits superstrings such as `/telemetry/v2/report/extra` or query variants.
- Encode exactness in the rule itself, typically with a URI-anchored `pcre` that matches the entire path value.
- Constrain parameter boundaries in the body. For example, `sig=` should require exactly 64 hex chars followed by `&` or end of body, not just any 64-char prefix.
- Prefer body patterns anchored to parameter boundaries such as `(?:^|&)blob=...(?:&|$)` and `(?:^|&)sig=...(?:&|$)` within the request body.
- Build incrementally: start with a minimal valid rule, confirm it parses with `suricata -T`, then add method/path, header, and finally body constraints.
- Do not add dummy `content`, `pkt_data`, or filler keywords just to silence parser errors; rebuild from a minimal valid rule and add one buffer change at a time.



## Tips

- Use PCRE for bounded pattern matching when exact lengths or delimiters matter.
- Check HTTP fields with valid Suricata HTTP buffers/modifiers only.
- Treat `suricata -T` as syntax/parser/load validation only; it does not prove the rule detects the target traffic.
- Use the supplied pcaps/config to verify the rule instead of relying only on the textual pattern.
- After every rule edit, run `suricata -T -S /root/local.rules -c /root/suricata.yaml` before deeper testing.
- Put the path/header checks in their appropriate HTTP buffers, then switch to `http.request_body` once for all body checks (`blob=` and `sig=`).
- If using `pcre` in a sticky buffer, keep it in the current buffer context instead of re-declaring the same buffer.
- Base conclusions only on directly observed packet or command output. If inspection output is truncated, incomplete, or errors, use a different extraction method before asserting header values, body contents, or lengths.
- Match headers against observed parsed traffic; header names may be normalized to lowercase. Prefer `nocase` for header-name/value checks unless exact case is required.
- If a positive sample does not alert, inspect the actual HTTP request and align `content`/`pcre` checks with what Suricata exposes in the intended buffer.
- Treat truncated Suricata test output as unresolved, not as a pass.
- Validate edge cases, not just one positive/negative sample: test a longer URI such as `/telemetry/v2/reporting`, a short `blob`, a `sig` with 63/65 chars, and values followed by extra valid characters.
- Verify the rule text enforces each stated condition directly; sample PCAP hits are only a supplement.
- Verify results conservatively: state only what the observed test output directly shows.
- If you did not inspect both positive and negative outcomes explicitly, do not claim exact alert counts or absence of alerts.
- Treat any edit after a successful test as unverified; rerun validation on the final saved rule before claiming success.
- Before finishing, audit: POST, exact path, exact header/value, `blob=` Base64 length threshold, `sig=` exact 64-hex boundary, and `sid:1000001`.
- Avoid false positives with specific patterns, but never drop one of the 5 required conditions.
- Validate the final `/root/local.rules` content before declaring success.
