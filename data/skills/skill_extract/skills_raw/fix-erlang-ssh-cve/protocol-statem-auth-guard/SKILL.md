---
name: protocol-statem-auth-guard
description: "Audit and fix protocol state machines so pre-auth messages cannot trigger privileged actions; add centralized authentication guards around message dispatch."
---

# Secure Authentication Guarding in Protocol State Machines

Harden stateful protocol servers (e.g., SSH-like, RPC, or any gen_statem-style FSM) by ensuring connection-level messages that can open channels, execute commands, or alter session state are only processed after successful authentication.

## When to Use

Activate this skill when:
- A protocol server processes connection/channel requests that might be reachable before authentication completes
- You observe a dispatch path like decode → classify → dispatch/internal-event → handler without a state guard
- A CVE or bug report mentions pre-auth request handling, command execution, or channel operations before auth

## Core Workflow

1. Map the Ingress Path
   - Identify where raw packets/messages are decoded into typed messages.
   - Find the mechanism that transforms decoded messages into internal events (macros, wrappers, or direct calls).
   - Locate the central handler that receives those internal events (e.g., a gen_statem handle_event clause for an event like {conn_msg, Msg}).

2. Identify the Gate
   - Determine the state(s) that indicate authentication completion (e.g., a "connected" state, an "authenticated" flag, or a macro that abstracts both connected and renegotiation states).
   - Confirm whether privileged messages (channel open, channel request/exec, subsystem/shell, data forwarding) are gated by this state before any side effects occur.

3. Choose the Policy for Pre-Auth Messages
   - Disconnect: Strongest defense; terminate on protocol violation with a standard reason code.
   - Postpone/Queue: Acceptable when protocol allows pipelining and you must preserve behavior; ensure no side effects are performed pre-auth and that queued events are safe to replay post-auth.
   - Drop/Ignore: Minimal intervention; use only if protocol spec allows silent ignore without disrupting clients.

4. Implement the Fix at the Choke Point
   - Prefer guarding the single central dispatch/handler for connection-level messages instead of scattering checks in the decoder or individual sub-handlers.
   - Add a guard that only allows processing when authenticated (or in authenticated renegotiation state), and add a complementary clause for the unauthenticated case.
   - Use existing macros/utilities for state checks to avoid missing special authenticated substates (e.g., renegotiation/ext-info).

   Example Erlang gen_statem pattern (abstracted):
   ```erlang
   %% Positive guard: only process when authenticated/connected
   handle_event(internal, {conn_msg, Msg}, StateName, Data) when CONNECTED(StateName) ->
       %% proceed with existing logic
       process_conn_msg(Msg, StateName, Data);

   %% Negative guard: reject or postpone before authentication
   handle_event(internal, {conn_msg, _Msg}, StateName, Data) when not CONNECTED(StateName) ->
       %% Choose one policy:
       %% (A) Disconnect with protocol error:
       {Shutdown, Data1} = send_disconnect(protocol_error_reason(), "Conn msg before auth", StateName, Data),
       {stop, Shutdown, Data1};
       %% (B) Or postpone (if pipelining supported):
       %% {keep_state_and_data, [postpone]};
   ```

   Notes:
   - CONNECTED(StateName) symbolizes an existing macro or helper that returns true only after auth (and during authenticated renegotiation if applicable). If a macro does not exist, implement a helper or guard against an explicit Data.authenticated flag.
   - Ensure this guarding clause is placed before any clause that would otherwise accept and process the event.

5. Preserve Legitimate Flows
   - Ensure authenticated renegotiation states are also allowed by the guard (e.g., via a macro that treats both connected and renegotiation as authenticated contexts).
   - Avoid moving or duplicating decoding logic; keep the fix in the central handler to prevent drift and missed cases.

6. Validate the Fix
   - Static checks:
     - Search for all handle_event clauses matching your internal event (e.g., {conn_msg, ...}) and confirm each is guarded or unreachable pre-auth.
     - Verify that no earlier code path performs side effects (spawn processes, open channels, exec commands) before the guard.
   - Behavioral checks:
     - Negative test: Perform minimal handshake short of authentication; send a privileged connection-level message; verify it’s rejected/disconnected or safely postponed with no side effects.
     - Positive test: Authenticate successfully; re-send the same message; verify normal operation.
   - Regression checks:
     - Test authenticated renegotiation (if supported) still allows the message.

## Verification Checklist

- Guard exists at the centralized handler for privileged connection-level messages.
- Unauthenticated path terminates (disconnect) or safely postpones without side effects.
- Clause ordering ensures unauthenticated cases don’t fall through to the authenticated handler.
- Macros/flags used for state checks cover connected and authenticated-renegotiation states.
- No operator precedence mistakes in guards (add parentheses around complex andalso/orelse expressions).
- Proper use of language terminators (e.g., periods vs semicolons) and no accidental partial replacements.
- Standard reason codes/messages are available and included via proper headers/imports.

## Common Pitfalls and How to Avoid Them

- Fixing at the wrong layer: Adding guards in the decoder for many message variants is brittle and easy to miss cases. Guard the central dispatch/handler instead.
- Side effects before guard: Ensure no process spawning, channel creation, or command execution occurs prior to the authentication gate.
- Ignoring renegotiation: A guard that only matches a single “connected” atom may break authenticated renegotiation states. Use an existing macro or helper that includes all authenticated contexts.
- Guard precedence bugs: In Erlang, andalso has higher precedence than orelse; parenthesize composite guards to avoid surprises.
- Clause order: The unauthenticated guard clause must be placed so it matches before any permissive clause.
- Postponing unsafe events: Only postpone if replaying the event post-auth is safe and intended by the protocol. Otherwise disconnect.
- Missing includes: If using disconnect reason codes or macros, confirm headers are included so compilation and behavior are correct.

## Optional Script Usage

Use the included audit script to flag potentially unguarded handlers in Erlang sources.

- What it does: Scans .erl files for gen_statem-like handle_event clauses that match target internal events (e.g., {conn_msg, ...}) and reports whether a guard referencing an authentication indicator (e.g., CONNECTED or authenticated) is present.
- How to run:
  - python scripts/statem_guard_audit.py --root path/to/src --events "{conn_msg" --require-guard CONNECTED authenticated
- Interpret results: Any reported unguarded clause that processes privileged messages requires review and likely a guard.

## Success Criteria

- Pre-auth privileged messages cannot trigger channels, execution, or stateful side effects.
- Authenticated sessions behave unchanged, including renegotiation if supported.
- The solution is centralized, minimal, and maintainable, avoiding duplicated checks across message variants.
