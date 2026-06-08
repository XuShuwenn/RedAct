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

- Before the first command, identify any required action wrapper, tool-call schema, and exact completion token; use that format verbatim on every step.
- Follow the task or environment's required tool/action syntax and response format exactly; do not improvise alternate tool-call formats.
- Do not substitute other tool syntaxes such as XML-style tags, ad hoc helper labels, or free-form shell blocks when a strict interface is specified.
- If a fixed completion string or final-output format is required, output that exact text and nothing else as the final response.
- Before finishing, re-check the required completion signal verbatim; do not add prose before or after an exact completion string.
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


- Use this order for patch delivery: edit source files in `/root/druid/` -> inspect the exact final diffs -> run required build/verification -> export `/root/patches/*.patch` from the final repository diff -> inspect patch contents -> `git -C /root/druid apply --check` the patch.
- Do not draft or hand-write speculative patch hunks before the source changes are finalized.


- Make every code change auditable in the shell log: use explicit edit commands, then inspect the modified file or `git -C /root/druid diff -- <file>`; `git status` alone is not enough.
- Generate `/root/patches/*.patch` only after source edits are finalized and any rebuild/verification steps are complete.
- Create the patch from actual repository diffs after applying edits; do not hand-write synthetic hunk text.
- After generating a patch file, inspect its contents, not just its existence, to confirm it matches the final intended fix and contains proper per-file diff headers.
- If you make further code changes after creating a patch, regenerate the patch from the final tree before finishing.

- For every file you claim to change, the shell log must show an explicit write/apply command followed by inspection of the modified region or `git -C /root/druid diff -- <file>`; never rely on `git status` alone as proof of the edit.
- Before creating `/root/patches/*.patch` or claiming implementation is done, confirm the intended source files appear in repo diff output such as `git -C /root/druid diff --name-only` or `git -C /root/druid diff --stat`, then inspect the relevant per-file diff.

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

- When summarizing build status, cite the observed terminal evidence (`BUILD SUCCESS`, `BUILD FAILURE`, or explicit exit code); otherwise report the build as unverified.
- Do not substitute indirect signs such as generated JARs, intermediate module output, warnings, partial reactor logs, or filtered output from `tail`/`head` as proof of final build status.
- If Maven output is long or truncated, redirect to a log and inspect the end of that log and/or print an explicit exit code before summarizing.
- After introducing a new security helper, interface, import, or annotation/injection change, run the required build promptly; use any compiler errors to finish integration cleanly, then rerun until the observed result is conclusive.
- If the exact command fails specifically because of reactor/project selection syntax, keep the same verification standard but fall back to a module-scoped build that still compiles the affected code and produces the needed artifact (for example, `cd /root/druid && mvn clean package ... -pl indexing-service -am`). State clearly that you used a fallback because the prescribed selector failed.


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

- Trace the reported sampler payload through the actual request-handling, Jackson deserialization, validation, and JavaScript enablement/enforcement path before editing code.
- Start with repository searches for the real control points (`javascript`, `JavaScriptConfig`, sampler/filter classes, `@JsonCreator`, `@JsonProperty`, `@JacksonInject`, and object-mapper wiring), then map the exploit from `POST /druid/indexer/v1/sampler` to the code that actually accepts the malformed input.
- Inspect relevant constructor bodies, JSON annotations/configuration, injected parameters, injectable-value handling, and the shared code that validates, compiles, or executes user-supplied JavaScript; do **not** assume either a sampler-local bug or a deserialization bypass without evidence.
- Search for every consumer of injected JavaScript security config (for example, `@JacksonInject` usages involving `JavaScriptConfig`) to determine whether the bypass is isolated or shared across parallel deserialization paths.
- Prefer the narrowest fix at the validated vulnerability boundary: start from sampler request / transformSpec filter handling, but patch the shared DI/deserialization or JavaScript enforcement point when repo evidence shows that is where security is actually bypassed.
- If repo evidence shows request JSON can override an injected security-sensitive value such as `JavaScriptConfig`, patch that constructor/deserialization boundary or shared Jackson enforcement point rather than relying only on downstream runtime checks.
- For sensitive injected security/config objects such as `JavaScriptConfig`, prefer Jackson injection that rejects client override (for example, `@JacksonInject(useInput = OptBoolean.FALSE)`) when supported.
- If the validated root cause is Jackson constructor/property binding in JavaScript-related classes, preserve existing constructors used by normal Java callers and add a separate JSON entry point or equivalent hardening when needed.
- When constructor binding for a security-relevant parameter is implicit or ambiguous, make it explicit at the validated vulnerable boundary; if you add a named `@JsonProperty` to an injected parameter, inspect any Jackson/Guice integration so legitimate injection still resolves.
- If a framework-supported annotation or binding change cleanly blocks user override of injected `JavaScriptConfig`, prefer that targeted deserialization fix over broader behavioral changes, but first confirm the repo's dependency version supports it.
- If repo evidence shows attacker-smuggled empty-key, unknown, or extra fields are the validated root cause, reject them at the affected security-sensitive DTO/class boundary rather than changing global parser/ObjectMapper behavior.
- Reuse existing JavaScript security gates where possible instead of inventing a separate enforcement model.
- After confirming one vulnerable JavaScript class or constructor pattern, audit true siblings for the same pattern and patch them consistently; do not expand to unrelated aggregators, post-aggregators, extractionFns, parseSpecs, constructors, or global parser/ObjectMapper behavior without evidence of the same path.
- If version-specific library behavior matters, inspect the locally installed dependency/classes to confirm semantics before choosing the patch.
- If you cannot identify where the empty-string key is accepted and where JavaScript enablement should have blocked it, keep investigating before modifying files.

## Tips

- Check transformSpec filter validation
- Add proper security checks for JavaScript execution
- Skip web-console to avoid OOM


- After each text replacement, inspect the exact modified region (imports, constructor, method body, validator, or call site), not just the file header or first few lines.
- Avoid broad blind replacements across Java files; read enough surrounding code before and after each edit.
- Do not rely on truncated source reads, annotations alone, compiled artifacts alone, or partial command output to conclude the root cause or that the vulnerability is fixed.
- In final reporting, mention only commands actually run and outcomes actually observed; quote the observed evidence when reporting results.

- If a source read shows only headers, annotations, or a truncated snippet, reread the exact constructor, validator, method body, or call site you are relying on until the acceptance point and enforcement logic are visible in the log.
- Use targeted searches such as `grep -R "@JacksonInject JavaScriptConfig" -n /root/druid` (or equivalent), plus searches for matching constructor/factory signatures, to enumerate sensitive consumers before deciding patch scope.
- When the issue looks like injected config overriding a server-supplied security object, grep for the exact annotation-and-type pair rather than only endpoint names.
- When framework behavior is central to the bug, inspect the exact local dependency version (for example with `javap` or source jars) instead of relying on memory about Jackson/Guice semantics.
- After patching one constructor or injected-config path, inspect all other occurrences of the same injected type to avoid leaving parallel deserialization entry points unpatched.
- If you use an annotation-based hardening fix, inspect the final source diff to confirm the import and annotation arguments are present at each intended constructor site.
- After each text replacement, inspect the exact modified region for every changed class, and before generating the final patch confirm the repo diff contains only the intended fix.
- If `git apply --check` on an intermediate handcrafted patch fails because context drifted, finish the source fix with direct edits, then regenerate the patch from the final repository diff before completing the task.
- Before exporting the final patch, remove temporary repro/debug files so `/root/patches/*.patch` contains only intentional source edits.
