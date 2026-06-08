---
name: suricata-custom-exfil
description: "Write Suricata signatures to detect custom HTTP telemetry exfiltration patterns in network traffic."
---

# Suricata Custom Exfiltration Detection

## When to Use

- Write Suricata IDS rules for custom exfil patterns
- Analyze PCAP files for suspicious traffic
- Avoid false positives in detection


- Treat environment/interface requirements as task-critical: required tool-call syntax, wrapper schema, allowed tool names, and exact completion tokens are part of correctness, not presentation.
- Follow any task/runtime instructions exactly when they specify tool invocation format, response schema, or final completion requirements.
- Before the first tool call, identify any task- or runtime-mandated interaction rules (for example required wrapper/JSON schema, one-action-per-turn constraints, wait-for-observation requirements, or action-only completion signals) and follow that exact contract for the entire run.
- Do not improvise alternate tool-call markup or switch to a different tool-call format mid-task.
- Do not claim `/root/local.rules` was updated unless you performed an explicit write action.
- Mark `/root/local.rules` as updated only after an explicit write succeeded and a read-back shows the expected rule text.
- Keep `/root/local.rules` compliant throughout iteration. Do not replace the deliverable with debug rules that change hard requirements such as `sid:1000001`; if experiments are needed, use a scratch file or restore the compliant rule immediately.
- If the task requires an exact final completion string or output format, emit it verbatim as the last output and nothing else.
- Before the final response, perform a protocol check: confirm the required tool-call format was used throughout, confirm the required file write actually occurred, confirm required validations completed or were explicitly reported as blocked, and confirm whether the final turn must be only a specific completion token.
- If substantive rule work is complete but the required action/output format has not been satisfied, the task is not complete.## Execution Protocol

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

Observed alerts on sample PCAPs do not excuse a missing structural constraint in the rule. If the task says a field is exact, encode that exactness in the signature itself and treat PCAP hits as confirmation only.

**Interpret exactness literally:**
Translate every "exact" requirement into rule syntax with anchors or delimiters; sample PCAP hits are not enough if the saved rule still matches superstrings or partial parameter values.

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

- Do not edit `/root/suricata.yaml` to make traffic parse, ports match, or rules load unless the task explicitly authorizes config changes; if validation is blocked by environment/config issues outside `/root/local.rules`, report the blocker instead.

## Evidence Gathering

- Inspect the HTTP request directly before writing the rule; do not infer headers, path, or body fields from summaries or truncated output.
- If a packet summary does not visibly show `POST`, `/telemetry/v2/report`, `X-TLM-Mode`, `blob=`, and `sig=`, run a more targeted command and verify those fields from actual output.
- Prefer commands that expose application data, e.g. `tcpdump -A -s 0 -r <pcap>` with an appropriate filter, or `tshark -r <pcap> -Y http -V`.
- Base the rule on observed traffic only. Do not state that a pcap contains specific headers, paths, or body parameters unless the command output actually shows it.

- Evidence gate: before drafting the rule, obtain command output that explicitly shows `POST`, the exact URI/path, the `X-TLM-Mode` header line/value, and the relevant body parameters.
- Treat packet summaries, handshake-only lines, truncated output, failed extraction, or `head`/summary views as insufficient for header/body claims.
- If an inspection command is truncated, incomplete, ambiguous, or omits needed HTTP fields, do not revise the rule yet; rerun with a narrower filter or alternate command until the full method, URI, relevant headers, and body parameters are directly visible.
- Acceptable fallback pattern: isolate the relevant packet/stream, then use a verbose view such as `tcpdump -A -s 0 -r <pcap>` or `tshark -r <pcap> -Y 'http.request' -V`.
- Do not infer header casing, delimiter behavior, encoding details, parameter lengths, or positive/negative traffic characteristics from partial output; only claim what the visible evidence shows.
- When debugging a non-firing rule, ground each change in specific observed traffic details from the capture, not inferred normalizations or assumptions.
- When comparing positive vs. negative PCAPs, state only differences explicitly visible in the extracted request output.


0. Before debugging rule logic against live traffic, verify the validation command actually loads `/root/local.rules` (for example, use `suricata -T -S /root/local.rules -c /root/suricata.yaml` or another task-specified explicit rule-file flag). If a different runtime path/config does not include `/root/local.rules`, do **not** fix that by editing config; keep the deliverable scoped to `/root/local.rules` and report the limitation.
1. Inspect `/root/local.rules` before editing.
2. Inspect available files in `/root/pcaps/` to understand what traffic is provided for validation.
3. Draft the final rule, but validate structure incrementally: start from a smallest valid rule for the intended HTTP buffer strategy, then add method/path, header, and body predicates one layer at a time.
4. Write the completed rule to `/root/local.rules` with an explicit file modification command; preserve existing content unless the task explicitly authorizes replacement, and do not overwrite the file with partial or placeholder content.
   - The write must be observable in the transcript (for example via `cat >`, `tee`, `printf >`, `sed -i`, or another explicit file-modification command). Describing the intended rule text is not enough.
   - Keep the draft in working memory or a scratch command until the rule is complete; never replace `/root/local.rules` with truncated text, placeholders, or a half-built rule.
5. Re-open `/root/local.rules` and confirm the new rule text is present while prior content remains intact.
   - Treat this as a hard gate: if there is no observable write command and no read-back showing the saved rule, the task is not complete.
6. Run `suricata -T -S /root/local.rules -c /root/suricata.yaml` to catch syntax and sticky-buffer errors.
   - Treat parser/load validation and traffic-match validation as separate checkpoints. If `suricata -T` reports sticky-buffer, keyword, modifier, or other parser errors, fix that structure first before interpreting any alert/no-alert result from PCAP testing.
   - If parser errors persist, stop broad rewrites: reduce to a minimal valid HTTP rule that still uses the correct buffers, confirm it loads, then add exactly one missing constraint at a time (method/path -> header -> one body predicate -> the final body predicate), rerunning `suricata -T` after each change.
   - Before deeper testing, make the test harness reliable: create any needed output/log directories first, use the supplied config unless the task says otherwise, and confirm runtime options/paths are valid so a no-alert result reflects the rule rather than setup mistakes.
7. If PCAPs are provided, verify behavior on them with the provided config/inputs first: the rule should alert on intended positive traffic and stay quiet on negative traffic.
   - Do not skip PCAP inspection/testing when those artifacts are provided; if artifact-based validation cannot be completed, report it explicitly as blocked or incomplete.
   - Use direct, separate checks for positive and negative outcomes. Avoid compound commands whose branches are not clearly visible in the captured output.
   - Capture decisive output for both outcomes. If console output is noisy, truncated, or ambiguous, inspect Suricata alert artifacts directly (for example, `fast.log`, `eve.json`, or extracted alert IDs) before concluding whether the rule fired.
   - Treat PCAP hits as behavioral evidence only. Also verify from the saved final rule text that each of the 5 required conditions is explicitly encoded in the intended HTTP buffer with exact boundaries.
   - Do not change the rule after a failed test until you have re-inspected the underlying HTTP request with enough detail to justify the revision.
8. Make final success claims only from verification output that is explicitly visible and current in the transcript. If a decisive command's output is truncated, cut off, stale relative to later edits, or does not visibly show the result, rerun a narrower/clearer check immediately before finishing or report validation as incomplete.
9. If offline PCAP processing fails for environmental or threading reasons, retry Suricata with `--runmode single` before concluding runtime validation is blocked.
10. If the combined rule parses but does not alert, isolate the failing condition with temporary test signatures for method/URI, header, and body predicates, confirm each against the pcap, then recombine the final single rule in `/root/local.rules`.
11. After any debugging with temporary rules, remove them and rerun validation on the final saved `sid:1000001` rule before claiming success.
12. After the final edit, read back the complete rule line from `/root/local.rules` with a command that shows the full text, and if you made any post-validation rule edit, rerun validation on the saved final rule before claiming success.
13. Distinguish outcomes precisely: "rule written", "rule parses/loads", and "alert observed on PCAP" are different states and must not be collapsed into one claim.
14. Perform a final requirement audit before declaring completion: verify the saved rule still preserves existing rules, uses `sid:1000001`, encodes all 5 conditions directly (including exact path boundaries), and that the response/tool protocol matches any task-specific format requirements.## Required Workflow

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

Do not stop at parse success. Final completion requires evidence that the rule both loads and alerts on matching traffic when feasible.

If the positive PCAP produces no SID 1000001 alert, or the event output is empty/inconclusive, do not declare success; continue debugging the rule semantics, especially buffer scope and exact-match boundaries.

If direct runtime testing is blocked, say that explicitly and keep the task incomplete rather than claiming success from reasoning alone. Report only the validation evidence you actually observed.

Do not claim success if all verification attempts failed. Ground every completion claim in observable actions: explicit write to `/root/local.rules`, readback confirmation, and validation output.

Report only validation outcomes directly shown by command output or inspected alert logs. If evidence is missing, truncated, ambiguous, contradictory, or based on non-default workaround flags, state that clearly instead of claiming default-config success.

If the runtime or task specifies an exact completion string/final-answer format, output it verbatim at the end and do not append extra prose.


## Suricata Rule Format

```suricata
alert tcp any any -> any any (msg:"Custom Exfil"; ...; sid:1000001;)
```

Use HTTP sticky buffers carefully: declare a given sticky buffer once, then place all related `content`/`pcre` checks under it until switching buffers. Do **not** repeat `http.request_body;` before each body condition; Suricata can reject this as a duplicate sticky-buffer instance.

If parser errors mention the previous sticky buffer still being set, no matches for the previous buffer, or output like `duplicate instance for http_client_body`, stop and rebuild from a minimal valid rule instead of adding filler keywords or another body-buffer declaration.

Use exact field/value matching for required HTTP elements. Do **not** replace a required header/value pair with a broad substring check.

For HTTP header matching with `http.header` + `content`, treat header names as case-insensitive by default: add `nocase` (or use an equivalent case-robust form) even if the sample shows one capitalization. Base the header match on the representation actually observed in packet inspection or parsed output; if the capture shows normalized lowercase header names such as `x-tlm-mode: exfil`, make the rule tolerant of that form rather than assuming original capitalization.

When a rule must enforce both an HTTP header condition and request-body conditions, treat buffer selection as a design constraint, not a cosmetic modifier choice. Read [HTTP header/body structure for Suricata rules](references/http-buffer-structure.md) before writing or revising such a rule.

If you hit parse errors or are unsure about keyword ordering, stop and compare against a known-working Suricata HTTP rule pattern before adding more complexity. Do not keep guessing at `http.method`, `http.uri`, `http.header`, or `http.request_body` syntax through trial and error.

- Constrain matches to the correct HTTP buffers (`http.method`, `http.uri`, header buffer, `http.request_body`).
- Scope checks to HTTP app-layer buffers; do not satisfy the 5 conditions with generic payload matching when HTTP sticky buffers are available.
- Match the header as a value match, not as separate loose tokens. For this task, prefer a scoped content check equivalent to `content:"X-TLM-Mode|3a 20|exfil"; http_header; nocase;` over separate header-name and value substrings or a brittle newline-sensitive header PCRE.
- For exact path requirements, do **not** rely on `content:"/telemetry/v2/report"` alone; that permits superstrings such as `/telemetry/v2/report/extra` or query variants.
- Encode exactness in the rule itself, typically with a URI-anchored `pcre` that matches the entire path value.
- A proven exact-path alternative is: match `content:"/telemetry/v2/report"; http.uri;` then immediately enforce end-of-buffer with `isdataat:!1,relative;` so longer URIs like `/telemetry/v2/reporting` do not match.
- If you use exact-size helpers such as `bsize`, count the target string length explicitly from the observed value before saving the rule; do not estimate.
- Constrain parameter boundaries in the body. For example, `sig=` should require exactly 64 hex chars followed by `&`, whitespace, end of body, or another explicit parameter terminator, not just any 64-char prefix.
- Preferred body-value pattern shape: bind form parameters to `(?:^|&)name=value(?:&|$)` so length/format checks apply to the whole parameter value, not just a prefix.
- Likewise, keep `blob=` and `sig=` scoped to a single parameter value with both leading and trailing boundaries.
- Build incrementally: start with a minimal valid rule, confirm it parses with `suricata -T`, then add method, exact path, header, and finally switch once to `http.request_body` for both body predicates.
- For this task, a safe structure is: `http.method` for `POST` -> exact `http.uri` check -> `http.header` exact header/value check -> one `http.request_body` declaration followed by both bounded body predicates.
- Prefer `http.request_body` for body predicates in Suricata 7-style workflows; do not switch to generic payload matching or older body keywords just to get a parse.
- A bare `pcre` for `blob=` or `sig=` is not an acceptable substitute for request-body scoping. If a parser fix removes the body buffer selector, the rule is incomplete even if `suricata -T` passes.
- Do not add dummy `content`, `pkt_data`, whitespace matches, `bypass`, or similar filler keywords just to silence parser errors; those are not valid substitutes for correct buffer structure.
- Never "temporarily" drop the required header check or either body predicate just to get a passing test. A rule that parses without all 5 conditions is still incorrect.


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
- Validate edge cases, not just one positive/negative sample: test a longer URI such as `/telemetry/v2/reporting`, a short `blob`, a `sig` with 63/65 chars, values followed by extra valid characters, and bodies where `blob=` or `sig=` appear only as malformed parameters or loose substrings.
- Verify the rule text enforces each stated condition directly; sample PCAP hits are only a supplement.
- Specifically audit boundary-sensitive fields in the saved final rule: exact URI/path scope, exact `X-TLM-Mode: exfil` header match, `blob=` value bounded as one parameter with length >= 80, and `sig=` bounded to exactly 64 hex chars before a delimiter or end.
- Verify results conservatively: state only what the observed test output directly shows.
- If you did not inspect both positive and negative outcomes explicitly, do not claim exact alert counts or absence of alerts.
- Treat any edit after a successful test as unverified; rerun validation on the final saved rule before claiming success.
- Before finishing, audit: POST, exact path, exact header/value, `blob=` Base64 length threshold, `sig=` exact 64-hex boundary, and `sid:1000001`.
- Final self-check: confirm the URI check is anchored to the whole path, `blob=` is bounded by a parameter delimiter or end-of-body after the 80+ Base64 value, and `sig=` is bounded after exactly 64 hex chars.
- Build incrementally: start with a minimal valid rule, confirm it parses with `suricata -T`, then add method, exact path, header, and finally switch once to `http.request_body` for both body predicates.
- After each added condition or buffer switch, rerun `suricata -T`; if the same sticky-buffer error repeats, revert to the last known-good rule and rebuild.
- When a validation command writes logs or outputs to a directory, create that directory first.
- For Suricata PCAP tests, prefer consistent invocation with the supplied config so parser/runtime differences do not masquerade as rule failures.
- If a no-alert result appears after adding an exact-length or exact-boundary constraint, verify the counted length from the actual observed field before changing broader rule logic.
- If `suricata -r <pcap>` fails unexpectedly despite a valid rule, retry with `--runmode single` and report both attempts.
- Avoid false positives with specific patterns, but never drop one of the 5 required conditions.
- Validate the final `/root/local.rules` content before declaring success.
- If the environment specified a tool/action schema or exact completion token, verify compliance one last time before the final turn.## Tips

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
