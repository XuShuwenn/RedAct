---
name: protocol-preauth-guard
description: "Identify and fix pre-authentication message handling that allows side effects in stateful protocol servers."
---

# Pre-Authentication Guarding for Stateful Protocol Handlers

A reusable workflow to locate and fix vulnerabilities where a server processes side-effecting protocol messages before a session is authenticated. Applicable to SSH-like connection layers, RPC frameworks, or any transport with a handshake/authentication phase followed by a stateful message phase.

## When to Use

Activate this skill when:
- A report indicates unauthenticated remote actions (e.g., command execution, channel opening, subsystem start) via crafted protocol messages.
- You are auditing a state-machine-based server and need to ensure side-effecting messages are only processed after authentication.
- You must add or verify message gating across connection phases (pre-auth, post-auth, rekey/renegotiation).

## Core Workflow

1) Map the protocol flow and states
- Identify phases: transport handshake, authentication in progress, fully connected/authenticated, and any renegotiation states.
- Locate where decoded protocol messages enter the application (message codec) and where they are dispatched (main handler/event loop).
- Inventory message types and classify which are:
  - Safe pre-auth (e.g., handshake, negotiation, service selection as per spec)
  - Require authentication (side-effecting: open channels/sessions, execute actions, start subsystems, data that triggers processing)

2) Trace the unsafe path
- For each message type that can cause side effects, trace from decode → dispatch → handler → side effect.
- Confirm whether an authentication/connected-state check exists before side effects occur.
- Prefer to enforce gating at the earliest common entry point for those messages (e.g., a connection-level message handler), not deep inside the executor, to prevent partial processing or queuing.

3) Choose the guard strategy
- Introduce a state predicate that clearly reflects “allowed to process side-effect messages”. Typical predicates:
  - authenticated == true
  - state in {connected, rekeying_after_auth}
- Maintain an allowlist of pre-auth messages that must continue to work (handshake, negotiation steps). Avoid global blocks that break compliant clients.
- Consider renegotiation: if the session was authenticated and is temporarily negotiating keys, side-effect messages may be acceptable per spec; gate on “previously authenticated” rather than strictly “currently connected”.

4) Implement the guard
- At the entry of connection-level message handling, add a conditional:
  - If message requires authentication AND session is not yet authenticated → reject early (disconnect/close with a protocol-appropriate error and no further processing).
  - Else → proceed with normal handling.
- Ensure consistent error/disconnect paths and logging, reusing existing helpers and reason codes defined by the project.
- Keep changes minimal and in the idiomatic style of the codebase (pattern matching, guards/macros, or explicit conditionals as used elsewhere).

5) Preserve normal behavior
- Do not block pre-auth messages mandated by the protocol (e.g., negotiation, service requests permitted pre-auth). Use an explicit allowlist for pre-auth traffic.
- Ensure post-auth flows, including rekey/renegotiation, remain functional when already authenticated.

6) Expand coverage of message variants
- Side-effecting message families often include multiple variants (e.g., open, request, data, extended-data). Make sure the guard covers all entry points and variants that reach side-effecting logic.

7) Verify
- Static review: audit the handlers to confirm every side-effecting path is gated.
- Behavioral checks:
  - Pre-auth: send a disallowed message → expect early rejection/disconnect with appropriate reason.
  - Post-auth: send the same message → expect normal behavior.
  - Post-auth rekey (if applicable): ensure messages still work when allowed by the protocol/spec.
- Build/lint/compile to catch syntax or guard placement issues.

## Verification

Use a combination of static and behavioral verification:

- Static guard audit
  - Search for handler clauses or functions that process side-effecting messages.
  - Within a small window around the handler entry, check for an authentication/connected-state guard.
  - Confirm all variants are covered.

- Behavioral reasoning/tests (no secrets or environment needed)
  - Pre-auth test sequence: connect, do only handshake steps, then send a side-effecting message.
    - Expected: immediate reject/disconnect; no side effects.
  - Post-auth test sequence: connect, authenticate, then send the same message.
    - Expected: normal processing.
  - Post-auth rekey (if supported): trigger rekey, then send message.
    - Expected: continue to work when authenticated session is undergoing rekey, in line with protocol rules.

- Code-level checks
  - Guard expression uses the project’s canonical state variable or macro.
  - Disconnect/error paths reuse standardized helpers and constants.
  - No partial processing occurs before the guard returns.
  - Changes compile and match stylistic patterns found elsewhere in the same module.

## Common Pitfalls

- Overblocking and breaking handshake
  - Blocking all pre-auth messages will break protocol compliance. Use an allowlist for pre-auth messages and a denylist (or requires-auth list) for side-effecting messages.

- Underblocking by missing variants
  - Only guarding one message type (e.g., a single request) while leaving related open/data/extended variants unguarded keeps the bypass viable. Cover all entry points that reach side effects.

- Guard placed too late
  - Adding checks after the message is already forwarded/queued can still allow side effects. Guard at the earliest common dispatch point.

- Ignoring renegotiation
  - Rekey/renegotiation may occur after authentication. Disallowing all side-effect messages during these phases can break valid clients. Gate on “already authenticated” rather than “strictly connected” when appropriate.

- Style/syntax inconsistencies
  - Introducing non-idiomatic guards (wrong macro usage, unmatched terminators, missing includes) can cause build failures or subtle bugs. Mirror existing patterns in the module.

- Wrong disconnect reason or error path
  - Use the project’s standard error/disconnect helpers and reason codes to stay consistent and aid diagnostics.

## Success Criteria

- All side-effecting connection-level messages are rejected before authentication completes.
- Legitimate pre-auth messages continue to function per protocol.
- Post-auth behavior is unchanged for compliant clients, including during permitted renegotiation.
- The patch is minimal, idiomatic, compiles cleanly, and centralizes gating at an early entry point.

## Optional Script Usage

Use the helper script to audit handlers for missing pre-auth guards.

- Typical usage examples:
  - Identify handlers (by regex) that process side-effecting messages and check for a nearby guard (by regex):
    - python scripts/guard_audit.py --root path/to/src --handler-pattern "channel_.*request|open.*channel" --guard-pattern "auth|connected|state.*authenticated" --window-back 20 --window-forward 5
  - Exit with non-zero status in CI if any unguarded handlers are found:
    - python scripts/guard_audit.py --root path/to/src --handler-pattern "exec|shell|subsystem" --guard-pattern "authenticated|connected" --ci

Adjust the patterns to match the project’s naming. This script is language-agnostic and operates on regex matches and proximity.
