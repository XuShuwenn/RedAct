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

## Guardrails

Wrong approach:
- Remove the body buffer reference so the rule validates, then leave `blob=`/`sig=` checks as generic content matches.

Right approach:
- Keep the body predicates explicitly scoped to the request body, and keep iterating until both syntax and behavior are validated.

## Final check

Before finishing, confirm all of the following:
- POST method matched
- Exact path matched
- `X-TLM-Mode: exfil` matched in headers
- `blob=` with Base64 length threshold matched in body
- `sig=` with exactly 64 hex chars matched in body
