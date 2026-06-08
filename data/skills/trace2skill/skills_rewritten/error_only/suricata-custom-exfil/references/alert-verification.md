# Alert verification and evidence thresholds

Use this reference when validating PCAP behavior or deciding whether alert results are strong enough to support a success claim.

## Rule

Claim a detection result only from explicit evidence:
- visible SID `1000001` in console/log output, or
- a directly inspected alert artifact such as `fast.log` or `eve.json` showing the alert, or
- an explicit zero-alert result from an inspected artifact/log for the negative case.

Not sufficient by itself:
- Suricata startup/shutdown lines
- packet counters
- clean process exit
- empty `jq`/grep output when the underlying file was not shown to exist and contain records
- truncated console output
- failed commands or missing output directories

## Safe validation pattern

1. Run the PCAP test.
2. Inspect the actual alert artifact or parsed alert output.
3. Confirm whether SID `1000001` appears for the positive PCAP.
4. Confirm whether SID `1000001` is absent for the negative PCAP.
5. If either check is ambiguous, rerun with simpler commands and inspect the files directly.

## Reporting discipline

- Say "rule parses/loads" only for `suricata -T` success.
- Say "alert observed" only when an alert record is explicitly visible.
- Say "negative case stayed quiet" only when the negative-case alert output/log was explicitly checked.
- If logs were not created, output was truncated, or the command failed, report validation as incomplete or blocked.

## Common mistake

Wrong:
- "Suricata ran successfully on both pcaps, so the rule was verified."

Right:
- "`suricata -T` passed, but I did not observe any SID `1000001` alert record for the positive pcap, so runtime detection remains unverified."
