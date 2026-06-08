---
name: fix-druid-loophole-cve
description: "Patch Apache Druid JavaScript injection vulnerability (CVE-like) that allows arbitrary code execution via empty key bypass."
---

# Apache Druid CVE Patch

## When to Use

- Patch Apache Druid 0.20.0 JavaScript injection vulnerability
- Fix authentication bypass allowing arbitrary code execution
- Rebuild Druid with Maven after patching


## When to Use

## Execution Protocol

- Follow the task or environment's required tool/action syntax and response format exactly; do not improvise alternate tool-call formats.
- If a fixed completion string or final-output format is required, output that exact text and nothing else.
- Treat harness/protocol requirements as mandatory success criteria alongside the code patch itself.

## Vulnerability

Empty key `""` bypasses JavaScript security to allow:
```javascript
java.lang.Runtime.getRuntime().exec('malicious_command')
```

Endpoint: `POST /druid/indexer/v1/sampler`

## Patch Location

Write patches to `/root/patches/`
Apply to git repo at `/root/druid/`


- Make every code change auditable in the shell log: use explicit edit commands, then inspect the modified file or `git -C /root/druid diff -- <file>`; `git status` alone is not enough.
- Generate `/root/patches/*.patch` only after source edits are finalized and any rebuild/verification steps are complete.
- Create the patch from actual repository diffs after applying edits; do not hand-write synthetic hunk text.
- After generating a patch file, inspect its contents, not just its existence, to confirm it matches the final intended fix and contains proper per-file diff headers.
- If you make further code changes after creating a patch, regenerate the patch from the final tree before finishing.

## Build Command

```bash
cd /root/druid && mvn clean package -DskipTests -Dcheckstyle.skip=true -Dpmd.skip=true \
  -Dforbiddenapis.skip=true -Dspotbugs.skip=true -Danimal.sniffer.skip=true \
  -Denforcer.skip=true -Djacoco.skip=true -Ddependency-check.skip=true \
  -pl '!web-console' -pl indexing-service -am
```

- Run the build exactly from `/root/druid`; use `cd /root/druid && ...` in one command so the log proves the correct working directory.
- Use this build command exactly as specified when the task requires a rebuild.
- If shell history expansion affects `!`, quote or escape it without changing semantics; do **not** drop `-pl '!web-console'` or replace the command with a simpler approximation.
- Do **not** claim the rebuild succeeded unless the observed output shows `BUILD SUCCESS` or an explicit zero exit code.
- If output is truncated, ambiguous, or only shows startup lines like `Scanning for projects...` or `Reactor Build Order`, treat build status as unverified and rerun or inspect the tail/log before summarizing the result.


## Verification

## Verification

- Do not claim the vulnerability is reproduced, fixed, or the build passed unless observable output shows the final result.
- Do not stop at a successful Maven build.
- Before declaring success, verify both:
  - exploit-shaped sampler input on `POST /druid/indexer/v1/sampler` is rejected or neutralized
  - representative legitimate sampler/filter input still works
- If you changed shared parsing, mapping, or helper code, perform an explicit regression sanity check on ordinary requests.
- Verify the generated patch file is applicable against `/root/druid/` before finishing (for example, `git -C /root/druid apply --check /root/patches/<patch>.patch`).
- In the final report, clearly distinguish directly observed results from anything not fully verified.

## Fix Strategy

- Validate/empty-string keys in JavaScript filter config
- Ensure security settings cannot be bypassed
- Block Runtime.exec calls in JavaScript functions


- Trace the reported sampler payload through the actual request-handling, deserialization, validation, and enforcement path before editing code.
- Inspect relevant constructor bodies, JSON annotations/configuration, and the code that consumes JavaScript filter config; do **not** assume a deserialization bypass without evidence.
- Prefer the narrowest fix at the validated vulnerability boundary; for this issue, prioritize sampler request / transformSpec filter handling before changing other JavaScript classes.
- If considering rejecting empty keys, scope that check to the vulnerable JavaScript configuration path rather than all deserialization.
- Do not broaden changes to aggregators, post-aggregators, extractionFns, parseSpecs, constructors, or global parser/ObjectMapper behavior unless repo evidence shows the same bypass path there.
- If you cannot identify where the empty-string key is accepted and where JavaScript enablement should have blocked it, keep investigating before modifying files.

## Tips

- Check transformSpec filter validation
- Add proper security checks for JavaScript execution
- Skip web-console to avoid OOM


- After each text replacement, inspect the exact modified region (imports, constructor, method body, validator, or call site), not just the file header or first few lines.
- Avoid broad blind replacements across Java files; read enough surrounding code before and after each edit.
- Do not rely on truncated source reads, annotations alone, compiled artifacts alone, or partial command output to conclude the root cause or that the vulnerability is fixed.
- In final reporting, mention only commands actually run and outcomes actually observed; quote the observed evidence when reporting results.
