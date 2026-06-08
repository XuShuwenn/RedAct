---
name: jackson-deserialization-hardening
description: "Harden Java services that use Jackson against deserialization bypasses (e.g., empty JSON keys or injected-config overrides) and ship safe patches and builds."
---

# Jackson Deserialization Hardening for Security Bypasses

Secure workflow for fixing vulnerabilities where crafted JSON input bypasses security controls during Jackson deserialization, including patterns like empty-string object keys or request JSON overriding injected configuration. This skill helps choose a robust, centralized patch strategy, implement it compatibly with the project's Jackson version, and verify both exploit blocking and normal behavior.

## When to Use

Activate this skill when you see:
- A Java service using Jackson where crafted JSON can alter security-related behavior during parsing
- Attacks exploiting empty or unusual JSON keys (e.g., "") to evade checks
- Cases where server-provided configuration (e.g., via `@JacksonInject`) is overridden by request JSON values
- Vulnerabilities in nested request bodies (e.g., ingestion or transformation specs) that are deserialized before validation

## Core Workflow

1. Establish Context and Constraints
   - Confirm the exact code version and build modules that will ship the fix.
   - Identify the Jackson versions used (core/databind) to ensure API compatibility.
   - Decide which modules to build and whether to skip heavy components (e.g., web UI) to avoid resource issues.

2. Trace the Vulnerable Code Path
   - Locate the HTTP endpoint(s) and request model classes involved.
   - Identify sensitive components (filters, aggregators, extractors, parsers) that rely on security-related configuration.
   - Inspect the ObjectMapper setup (custom modules, InjectableValues provider, AnnotationIntrospector, JSON provider wiring).

3. Choose a Centralized Mitigation Locus
   - Prefer a fix that applies broadly rather than patching many call sites:
     - Parser-level rejection: Reject malformed input early (e.g., empty object keys) via a guarded `JsonFactory` or `JsonParser` wrapper used by the default `ObjectMapper`.
     - Injection-level hardening: Ensure `@JacksonInject` values cannot be supplied or overridden by input JSON by updating the project's `AnnotationIntrospector`/injectable handling.
   - Select the approach (or a combination) based on the exploit mechanics and available APIs in the project's Jackson version.

4. Implement the Fix Compatible with the Jackson Version
   - Parser-level rejection (example considerations):
     - Wrap or extend `JsonFactory` to return a `JsonParser` that checks field names and rejects empty strings.
     - Ensure all parser creation paths used by the app (`createParser` overloads) return the guarded parser.
     - Wire the guarded factory into the default `ObjectMapper` used by HTTP and internal deserialization (including copies/clones).
   - Injection-level hardening (example considerations):
     - Update the custom `AnnotationIntrospector` to ensure injected values are always taken from server configuration, not request JSON.
     - If constructor- or field-based injection is used, ensure the injected value is not also annotated as a JSON property that can be bound from input.
     - Add constructor-time validation so sensitive operations require a valid injected config and cannot be enabled by input alone.

5. Defense-in-Depth Safeguards
   - Add null/consistency checks in constructors of sensitive components; fail fast if the injected configuration disallows the behavior.
   - Avoid relying solely on post-deserialization validation when the bypass occurs during parsing; ensure early rejection or immutable injection.

6. Build and Package Patches
   - Commit changes and produce patch files via `git diff` into a patches directory for archival and deployment.
   - Build the minimal set of modules needed for deployment and tests, using skip flags where appropriate to reduce resource load.

7. Validate the Fix
   - Negative tests: Crafted payloads with empty object keys or injection-override attempts must be rejected (e.g., parse error, 4xx response).
   - Positive tests: Legitimate requests that conform to expected schemas must still succeed.
   - Static verification: Confirm all ObjectMapper instances used by HTTP ingest the guarded `JsonFactory` (parser-level) or that injectable values cannot be overridden by input (injection-level).
   - Artifact verification: Ensure patched classes are present in produced JARs.

## Verification Checklist

- Version & API Compatibility
  - The project's Jackson versions are identified, and no fix relies on APIs unavailable in that version.
- Central Wiring
  - The guarded `JsonFactory` or modified `AnnotationIntrospector` is used by the ObjectMapper that handles HTTP request deserialization.
- Behavior Under Attack
  - Inputs containing empty string JSON keys are rejected early (parser-level) OR cannot influence injected configuration (injection-level).
- Legitimate Behavior Preserved
  - Typical, valid requests still parse and execute as before.
- Build & Patch Artifacts
  - Patch files generated from `git diff` exist and reflect the changes.
  - Built artifacts contain the modified classes.

## Common Pitfalls and How to Avoid Them

- Using unsupported Jackson APIs
  - Pitfall: Relying on methods only present in newer Jackson versions.
  - Avoidance: Identify the exact Jackson versions from the build and implement wrappers/overrides compatible with those versions.

- Fix applied in the wrong place
  - Pitfall: Patching many scattered classes while missing other deserialization entry points.
  - Avoidance: Prefer centralized fixes (parser factory or annotation introspector) so all code paths are covered.

- Guard not wired globally
  - Pitfall: Creating a guarded `JsonFactory` but not using it for all ObjectMappers (including copies/clones or provider-bound mappers).
  - Avoidance: Update the default mapper configuration, ensure `copy()` preserves the factory, and verify providers use the guarded mapper.

- Breaking legitimate requests
  - Pitfall: Overly strict checks that reject valid input formats.
  - Avoidance: Specifically target malformed patterns (e.g., empty field names) and add regression tests for standard inputs.

- Injection still overridable
  - Pitfall: Sensitive configuration marked with both `@JacksonInject` and a JSON property, allowing input binding.
  - Avoidance: Ensure sensitive config is inject-only and add constructor-time validation.

- Debug code left behind
  - Pitfall: Temporary logs or print statements in hot paths.
  - Avoidance: Remove all debug scaffolding before building patches.

- Build instability
  - Pitfall: Building large UI modules or enabling heavy checks causing OOM/timeouts.
  - Avoidance: Build only required modules and skip non-essential checks when appropriate.

## Optional Script Usage

Use the helper script to quickly detect empty-string JSON keys in crafted payloads during verification:

- Detect empty keys in a file:
  - `python scripts/validate-empty-json-keys.py --file payload.json`
- Detect empty keys from stdin:
  - `cat payload.json | python scripts/validate-empty-json-keys.py`

Non-zero exit status indicates at least one empty key was found, with reported JSON pointer paths for triage.
