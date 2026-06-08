---
name: jackson-inject-bypass-fix
description: "Harden Jackson @JacksonInject usage so JSON input cannot override injected values (e.g., security configs) and ship a verified build."
---

# Jackson Injectable Override Hardening

This skill distills a robust workflow to fix vulnerabilities where JSON input can override dependency-injected values in Java code using Jackson `@JacksonInject`. It is especially applicable to security-critical configs (e.g., enabling scripting), where an attacker may craft payloads (including empty-string property names) to bypass intended injection.

Use this when you need to:
- Prevent JSON payloads from providing values for `@JacksonInject` parameters
- Fix CVE-like issues involving empty JSON keys or injection bypass
- Patch and rebuild a multi-module Maven project and verify the fix

## Core Workflow

1) Reconnaissance: locate vulnerable injection points
- Search for `@JacksonInject` on constructors, factory methods, or fields of classes that gate security-sensitive behavior.
  - Also search for the specific sensitive types (e.g., scripting config types) used only via injection.
- Identify custom Jackson configuration in the codebase:
  - Custom `AnnotationIntrospector`, `InjectableValues`, or `ObjectMapper` wiring that affect injection.
- Inventory all modules where these occur so you don't miss less obvious call sites.

2) Choose a primary hardening strategy (prefer precise over invasive)
- Preferred local fix (simple, low-risk): annotate each susceptible injection site with
  - `@JacksonInject(useInput = com.fasterxml.jackson.annotation.OptBoolean.FALSE)`
  - This instructs Jackson to never take a value from JSON for that injection point.
- Centralized alternative (when many sites or annotation edit is impractical):
  - Override your custom `AnnotationIntrospector` method returning a `JacksonInject.Value` with `useInput=false` for any member annotated with `@JacksonInject`. Ensure this introspector is the primary one on the `ObjectMapper`.
- Defense-in-depth (optional but recommended):
  - Add `Objects.requireNonNull(config, "<Config> must not be null")` (or similar) in constructors for injected configs. This guards against deserialization trickery that results in nulls.
  - Keep existing runtime checks (e.g., `config.isEnabled()`) in the actual execution path.

3) Avoid brittle or over-broad changes
- Do not change constructor signatures or add ad-hoc trap parameters; it breaks serialization compatibility.
- Avoid relying solely on `@JsonIgnoreProperties` tweaks; it may block valid requests or still miss the inject-bypass path.
- Global request filters or parser hacks (rejecting empty keys) can be used as an extra layer but are not a substitute for fixing injection semantics.

4) Apply consistently across all affected modules
- Patch every occurrence of the vulnerable injection pattern.
- Ensure you import `com.fasterxml.jackson.annotation.OptBoolean` where needed.
- If using the centralized introspector approach, verify it is actually active for all server-side mappers.

5) Build and package
- Use a module-aware Maven build with dependencies resolved (e.g., build the target module with `-am`).
- If the project includes large submodules (like web UI) that are unnecessary, exclude them to reduce resource issues.
- Disable nonessential checks for patched builds as appropriate per project policy (e.g., skip tests or static checks) when the environment requires it.

6) Verify the fix
- Confirm compiled classes include the hardened annotations/logic by listing JAR entries and/or decompiling.
- Smoke-test by ensuring crafted JSON attempting to set injectable values (including empty-field names) no longer takes effect.
- Validate that legitimate requests still deserialize and function as expected.

## Implementation Snippets

A) Local annotation hardening
- Before:
  - `@JacksonInject SomeConfig config`
- After:
  - `@JacksonInject(useInput = com.fasterxml.jackson.annotation.OptBoolean.FALSE) SomeConfig config`
- Ensure the import exists:
  - `import com.fasterxml.jackson.annotation.OptBoolean;`

B) Centralized introspector hardening (alternative)
- In your custom `AnnotationIntrospector`:
  - If a member has `@JacksonInject`, return a `JacksonInject.Value` whose id matches your injection key and whose `useInput` is disabled.
  - Keep `findInjectableValueId` logic consistent with your DI setup (e.g., Guice keys).

C) Defense-in-depth
- Inside constructors receiving injected configs:
  - `this.config = Objects.requireNonNull(config, "Config must not be null");`

## Verification Checklist

- Code
  - All security-sensitive `@JacksonInject` parameters now have `useInput = OptBoolean.FALSE` (or are enforced centrally via the introspector).
  - Null checks added where beneficial.
  - No constructor API changes that could break JSON compatibility.
- Build
  - Project compiles with patched code; artifacts are produced for all affected modules.
- Runtime
  - Malicious JSON attempts to set injected values are rejected or ignored; behavior reflects injected defaults.
  - Normal, valid JSON requests still deserialize properly.

## Common Pitfalls and Recovery

- Missed occurrences
  - Pitfall: Only patching obvious classes (e.g., filters) and neglecting auxiliary ones (e.g., routing strategies, worker selection, parse specs).
  - Recovery: Use a repo-wide search (see optional script) and re-check all modules.

- Missing imports / compile errors
  - Pitfall: Adding `useInput = OptBoolean.FALSE` without importing `OptBoolean`.
  - Recovery: Add `import com.fasterxml.jackson.annotation.OptBoolean;` or use fully qualified name in the annotation.

- Overreliance on `@JsonIgnoreProperties`
  - Pitfall: Assuming setting ignoreUnknown will fix injection bypass. It may cause unintended rejections or miss the actual injection path.
  - Recovery: Use `useInput = OptBoolean.FALSE` or the introspector approach; treat ignore policies only as supplementary.

- Overly invasive global parsing changes
  - Pitfall: Rewriting global JSON factories or adding request filters that reject valid payloads.
  - Recovery: Prefer precise injection hardening; apply global guards only as additional layers after verifying they don't break normal traffic.

- Breaking serialization compatibility
  - Pitfall: Changing constructor parameter lists to add trap parameters.
  - Recovery: Keep constructors stable; use annotations and introspector logic instead.

## Optional Script Usage

Use the helper script to scan a repository for `@JacksonInject` sites and flag any that lack `useInput = OptBoolean.FALSE`.

1) Run:
- `python3 scripts/check_jackson_inject_use_input.py --root <repo-root>`

2) Review output:
- It lists files and line numbers where `@JacksonInject` appears without the hardening attribute, helping ensure full coverage.

3) After patching:
- Re-run the script to confirm no remaining unprotected sites.

## Success Criteria

- All injection points for sensitive configs are immune to JSON override.
- Build artifacts compile and contain the patched classes.
- Security tests that previously bypassed injection fail (i.e., the exploit is blocked), while legitimate requests still succeed.
