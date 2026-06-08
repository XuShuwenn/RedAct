# HTTP header/body structure for Suricata rules

Use this reference when a signature must combine HTTP method/path/header checks with request-body checks.

## Core rules

- Treat sticky buffers as scoped: a match meant for the body must be explicitly written in the request-body buffer context.
- Do not assume a rule is correct just because it parses after removing the body buffer; that often means the body requirement was dropped semantically.
- Repeated sticky-buffer errors usually mean the rule structure is invalid, not that it needs another small syntax tweak.

## Authoring pattern

1. Constrain the HTTP request metadata first (method, URI/path, headers).
2. Add body-specific matches in the request-body buffer context.
3. Re-run `suricata -T`.
4. Then test on traffic/PCAP to confirm the alert actually fires only when all required conditions are present.


Example buffer flow for this exfil pattern:
1. `http.method` + `content:"POST";`
2. `http.uri` with an exact-path matcher
3. `http.header` with the exact `X-TLM-Mode: exfil` match
4. `http.request_body` once
5. Body `content`/`pcre` for bounded `blob=` and bounded `sig=`

Avoid this invalid pattern:
- `http.request_body; content:"blob="; http.request_body; pcre:"/...sig.../";`

Use this valid pattern instead:
- `http.request_body; content:"blob="; pcre:"/...blob.../"; pcre:"/...sig.../";`

## Minimal working pattern

Use this shape when a signature must combine request metadata with body predicates:

```suricata
alert http any any -> any any (
  msg:"Custom Exfil";
  flow:to_server,established;
  content:"POST"; http.method;
  pcre:"#^/telemetry/v2/report$#"; http.uri;
  content:"X-TLM-Mode|3a 20|exfil"; http.header; nocase;
  http.request_body;
  pcre:"/(?:^|&)blob=[A-Za-z0-9+\\/]{80,}(?:&|$)/";
  pcre:"/(?:^|&)sig=[0-9A-Fa-f]{64}(?:&|$)/";
  sid:1000001;
)
```

Adapt operators as needed, but preserve the structure: header checks before the body switch, then keep both body predicates under the single `http.request_body` context.

### Minimal rebuild sequence

Use this when parser errors repeat:

1. Start from a minimal valid HTTP rule with `sid:1000001`.
2. Add the method check in the method buffer and confirm `suricata -T` passes.
3. Add the exact URI/path check in the URI buffer and confirm `suricata -T` passes.
4. Add the `X-TLM-Mode: exfil` header check in the header buffer and confirm `suricata -T` passes.
5. Switch to `http.request_body` once.
6. Add both body predicates under that one body-buffer context.
7. Re-run `suricata -T`, then test on PCAPs.

### Semantic safety check after parser fixes

If Suricata rejects your first draft, do **not** respond by stripping the body buffer and leaving `pcre` clauses bare.

Use this check after every rewrite:
- Header/method/path checks still target HTTP-specific buffers.
- `blob=` and `sig=` checks are still explicitly in the request-body buffer context.
- No body predicate was converted into an unscoped generic payload match just because that version parsed.
- Then rerun `suricata -T` and a positive-PCAP test.

A rule that parses but no longer scopes body predicates to the request body is a regression, not a fix.

If syntax is still unclear, consult a known-good local/example HTTP rule and mirror its buffer ordering before continuing.

## Guardrails

Wrong approach:
- Remove the body buffer reference so the rule validates, then leave `blob=`/`sig=` checks as generic content matches.

Right approach:
- Keep the body predicates explicitly scoped to the request body, and keep iterating until both syntax and behavior are validated.

- Common failure pattern: keep `http.header` active, then add body regexes or `/P`-style shortcuts; Suricata can reject this with a sticky-buffer-context error.
- Safer pattern: finish header checks, switch once to `http.request_body`, then place both body predicates there without reverting to generic payload matching.
- Wrong approach: delete `http.request_body` so the rule parses, then leave `blob=` / `sig=` as unconstrained payload matches.
- Right approach: keep the body predicates explicitly scoped to the request body, and keep iterating until both syntax and behavior are validated.
- If method/URI/header checks work but the known-positive sample still does not alert, suspect request-body regex scope/modifier semantics before weakening the rule.
- If the full rule still fails behaviorally, test the pieces separately: one temporary rule for method/URI, one for the header, and one for each body predicate or body regex. Recombine only after each piece matches in the expected buffer.
- Prefer simple `http.header` `content` checks for `X-TLM-Mode: exfil` when header normalization makes line-oriented PCREs brittle.
- Prefer `http.request_body` for request-body matching when available; avoid replacing body-scoped checks with unscoped payload matches just to satisfy the parser.

- If a rule parses but fails to alert, do not assume the next fix is another buffer rewrite. First confirm the packet is even eligible for the rule header: IP direction, port/protocol selection, and any `$HOME_NET` / `$EXTERNAL_NET` variable usage.
- Fast isolation order for a silent rule: (1) explicit `-S /root/local.rules` load check, (2) address/direction check against PCAP endpoints, (3) minimal method/URI match, (4) header match, (5) one body-buffer switch with bounded body predicates.
- In particular, if both endpoints in the capture are inside `HOME_NET`, a directional header such as `$HOME_NET any -> $EXTERNAL_NET any` can block alerts even when all HTTP content matches. Fix or account for rule eligibility before weakening content constraints.
- When parser fixes are failing repeatedly, do not keep issuing broad replacements against assumed text. Read back the full saved rule after each failed attempt and correct the specific sticky-buffer ordering or truncated clause that is actually present.
- A successful parse does not rescue an incomplete saved rule. If readback shows a line cut off at `pcre:` or another partial token, treat the file as invalid until the full intended rule text is visible and then rerun validation.

## Final check

Before finishing, confirm all of the following:
- POST method matched
- Exact path matched
- `X-TLM-Mode: exfil` matched in headers
- `blob=` with Base64 length threshold matched in body
- `sig=` with exactly 64 hex chars matched in body
