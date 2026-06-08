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

## Task-Mode Gate

- First classify the user request: **analysis-only** (find/report paths, snippets, root cause, configuration behavior) or **patch-and-verify**.
- If the request is analysis-only, do **not** edit source files, create patch files, or start builds unless the user explicitly asks for that as a separate step.
- For analysis-only tasks, the deliverable is a report grounded in repository evidence: file paths, exact code snippets, and a step-by-step explanation of the vulnerable path.
- Do not switch from investigation to patching just because you think you found a likely fix; answer the requested deliverable first.
## When to Use

## Execution Protocol

- Before the first command, identify any required action wrapper, tool-call schema, and exact completion token; use that format verbatim on every step.
- Follow the task or environment's required tool/action syntax and response format exactly; do not improvise alternate tool-call formats.
- Do not substitute other tool syntaxes such as XML-style tags, ad hoc helper labels, or free-form shell blocks when a strict interface is specified.
- If a fixed completion string or final-output format is required, output that exact text and nothing else as the final response.
- Before finishing, re-check the required completion signal verbatim; do not add prose before or after an exact completion string.
- Treat harness/protocol requirements as mandatory success criteria alongside the code patch itself.

- Before the first tool call, determine the environment's exact required action wrapper/tool-call schema, wrapper order, and exact completion token; then use that syntax literally for the entire task.
- If the environment requires a strict format such as `Thought:` followed by `Action:` with JSON, use that exact structure on every tool invocation; do **not** emit XML-like tags, markdown shell blocks, pseudo-tool wrappers, unsupported helper labels, or prose-only shell descriptions.
- Every tool action must contain a concrete executable command or fully specified parameters; do **not** use placeholders such as `inspect relevant source file`, `generic source inspection command`, `...`, or fake pathspecs.
- Treat the required completion token as exact and case-sensitive. Immediately before the final response, compare it character-for-character; if an exact completion string is required, output that string alone and nothing else.
- Procedural format compliance is mandatory: a correct patch delivered with the wrong action schema or wrong completion string is still a failed task.

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
- Do **not** create placeholder `/root/patches/*.patch` files containing prose, TODO text, summaries of intended changes, or handwritten hunk text. Every patch artifact must be generated from the repository's real final diff and contain real unified diff headers/hunks.
- Never use placeholder edit targets such as `existing import block`, `class declaration`, `target snippet`, `...`, or descriptive prose in place of exact source text. Read the current file and edit against concrete lines actually present in the repository.
- Before any replacement, read the exact constructor, method body, validator, annotation block, or import block to be changed; do not edit from headers, search hits, assumed patterns, or truncated snippets alone.
- If an edit or patch application fails, stop and reread the full current region before retrying. Reconstruct the change from the repository's actual text, then inspect the affected file and `git -C /root/druid diff -- <file>` before making another change.
- After writing a patch file, inspect it in enough detail to confirm it is a concrete diff for the intended source files, including real `diff --git`, `---`, `+++`, and `@@` headers.


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

- A started Maven command is not evidence of success. Do not report "build succeeded" unless observed output later shows `BUILD SUCCESS` or you explicitly captured and observed exit code `0` after the command finished.
- If Maven output may truncate or outlive the visible output window, rerun the exact build with logging and an explicit status check, for example: `cd /root/druid && mvn ... > /tmp/druid-build.log 2>&1; echo EXIT:$?` and then inspect the log tail for `BUILD SUCCESS`/`BUILD FAILURE`.
- Treat output that shows only startup lines (`Scanning for projects...`, reactor order, module list) as **not built yet**; do not summarize the build as successful until you have inspected the ending lines or equivalent completion evidence.
- Do not infer success from warnings, generated artifacts, partial `tail` output, or intermediate module output alone.


## Verification

- Treat verification as observed evidence, not inference: do not conclude implementation, patch applicability, build success, or remediation success from file existence, grep hits, annotation strings, jar presence, partial logs, dependency introspection, or custom micro-repros alone.
- Build success is only a compile check, not fix confirmation. Do not claim the vulnerability is fixed unless you also inspect the final diff for every touched file and verify behavior against the concrete suspected path.
- Verification must include behaviorally meaningful evidence: observed rejection or neutralization of exploit-shaped sampler input and observed acceptance of representative legitimate input, or a clearly stated limitation if runtime verification was not achieved.
- For each changed file, the log must show evidence of the workflow: full relevant source read before editing, explicit edit command, and reread or `git -C /root/druid diff -- <file>` after editing.
- Treat truncated or partial command output as inconclusive. If a build or test log stops before the result summary, rerun with captured output and inspect the ending or print an explicit exit code before making any pass/fail claim.
- Before declaring the fix complete, run targeted searches for all validated sibling occurrences of the same security-sensitive pattern and inspect each intended site to confirm the change was actually applied.
- Completion checklist before the final completion token:
  - each changed source file has its final modified region or `git -C /root/druid diff -- <file>` inspected in the log
  - generated `/root/patches/*.patch` is shown and its contents are inspected
  - `git -C /root/druid apply --check /root/patches/<patch>.patch` succeeds visibly
  - build status is supported by `BUILD SUCCESS`, `BUILD FAILURE`, or an explicit exit code
- If exploit reproduction, fix validation, or build confirmation was not run or output is inconclusive, say so plainly; do not convert a plausible patch into a verified fix in the final report.

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

- Treat the most specific reported clue as the primary investigation anchor. For this issue, trace the empty-string key `""` through the real code paths first, including request parsing, map or JSON field handling, binding, validation, and the downstream JavaScript enforcement path actually reached from that input.
- Evidence gate before editing: do not choose a fix or modify code until the log shows the concrete acceptance path for the exploit input and the concrete enforcement or injection point that should block it.
- Do not settle on a root-cause theory from endpoint names, Jackson/library expectations, file names, grep hits, headers, imports, annotations, or partial snippets alone. First read the full relevant constructor, factory, validator, and method bodies that consume the request data and the security-sensitive config.
- If a read shows only headers, imports, class declarations, annotations, or another truncated fragment, treat the source evidence as insufficient. Continue reading until the exact acceptance point, binding logic, and enforcement path are visible in the log before editing.
- Before changing imports, annotations, constructor parameters, injected fields, shared deserialization, or validation logic, read the exact surrounding source lines first and base the edit on concrete text from the file; do not use placeholder matches like `...` or guessed structure.
- In your notes and final report, separate what is directly observed in source from hypothesis; do not implement or defend a hypothesis until repository evidence confirms it.
- If an investigation yields a concrete mechanism tied to one artifact, prefer a fix at that demonstrated boundary. Do not broaden the patch to sibling JavaScript-related classes, `ObjectMapper`, or other infrastructure layers merely because they look similar; expand scope only when repository evidence shows the same vulnerable pattern on a parallel path, and inspect each implementation body before changing it.

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

- Use only concrete executable commands in the shell log. Do **not** issue natural-language placeholders such as "search the source tree", "run the Maven build", or "inspect the file header" as if they were commands.
- Prefer auditable inspection commands that name the exact file and region, such as `grep -R -n`, `find`, `sed -n`, `awk`, `head`, `tail`, `cat`, and `git -C /root/druid diff -- <file>`.
- Do **not** use `git checkout -- <file>`, `git checkout <file>`, or other restore-from-index commands to inspect a modified file. These are destructive and can silently discard your patch. Use non-destructive reads or per-file diffs instead.
- If a file read shows only package/import lines, class declaration, or another truncated header view, read deeper until the operative constructor, method body, annotation handling, or binding logic is visible before editing.
