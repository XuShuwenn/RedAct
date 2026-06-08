# Incremental rebuild for parser/load failures

Use this reference when Suricata reports repeated parser, sticky-buffer, or HTTP keyword errors, or when load status is ambiguous.

## Rebuild trigger

Stop freeform editing and restart from a minimal known-good rule when you see any of these patterns:
- the same sticky-buffer error repeats after a rewrite
- unknown/invalid HTTP keyword usage
- you are no longer sure what exact text is currently saved in `/root/local.rules`
- runtime output includes engine/init failures, so you cannot tell whether the current rule actually loaded

## Required reset sequence

1. Re-open `/root/local.rules` and copy the exact current saved rule text.
2. Replace only the target rule with a minimal valid HTTP rule using `sid:1000001`.
3. Run `suricata -T -S /root/local.rules -c /root/suricata.yaml`.
4. Add exactly one layer, then rerun `suricata -T` after each layer:
   - method
   - exact URI/path
   - header
   - single `http.request_body` switch
   - bounded `blob=` body predicate
   - bounded `sig=` body predicate
5. Only after clean load status, test PCAP behavior.

## Minimal rebuild skeleton

```suricata
alert http any any -> any any (
  msg:"Custom Exfil";
  flow:to_server,established;
  content:"POST"; http.method;
  content:"/telemetry/v2/report"; http.uri; isdataat:!1,relative;
  content:"X-TLM-Mode|3a 20|exfil"; http.header; nocase;
  http.request_body;
  pcre:"/(?:^|&)blob=[A-Za-z0-9+\\/]{80,}(?:&|$)/";
  pcre:"/(?:^|&)sig=[0-9A-Fa-f]{64}(?:&|$)/";
  sid:1000001;
)
```

## Interpretation guardrails

- Do not treat "no parse errors" as established unless the output also lacks engine/init failure for that same run.
- Do not move on to PCAP behavior until the saved final rule has a clearly successful load check.
- If you edit the rule after any successful test, the previous validation is stale; rerun load and behavior checks on the newly saved text.
