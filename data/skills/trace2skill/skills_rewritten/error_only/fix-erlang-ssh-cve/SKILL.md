---
name: fix-erlang-ssh-cve
description: "Investigate and fix Erlang/OTP SSH server vulnerability allowing arbitrary command execution via crafted SSH protocol messages."
---

# Erlang/OTP SSH Server CVE Fix

## When to Use

- Fix Erlang/OTP SSH server remote code execution vulnerability
- Investigate which SSH message type causes the attack
- Patch source code to block unauthorized commands

## Input

- Source code at `/app/workspace/otp_src_27.3.2/`
- Affected version: Erlang/OTP SSH server


## Input

## Execution Protocol

- Follow any task-specific tool/action protocol exactly. If the environment specifies a required action schema, wrapper, allowed tool names, JSON format, or exact completion token, use that exact format throughout.
- Do not substitute alternate tool syntax, pseudo-calls, narration-only stand-ins, unsupported parameters, or different completion phrasing.
- Make only executable, verifiable actions with real commands, real file paths, real search patterns, and concrete edit targets taken from text you have already read.
- Before the first tool use and before the final response, re-check the required protocol and completion signal; if an exact completion token is required, emit it verbatim as the last line.
## Vulnerability

Crafted SSH protocol messages allow:
- Arbitrary system command execution
- No authentication required

## Fix Requirements

1. Investigate which SSH message causes the attack
2. Fix the bug in source code
3. Server should maintain normal SSH behavior
4. Block unauthorized message types


5. Produce an actual source-code patch in the provided Erlang files; do not stop at analysis or a written report
6. Verify the full exploit path from unauthenticated input to command execution before patching
7. Keep the fix as narrow as the demonstrated vulnerable message/state combination while preserving normal authenticated SSH behavior
8. Inspect edited Erlang control flow for syntax, clause ordering, fallback behavior, and return-shape consistency before finishing
9. Do not claim a fix was applied unless you performed an explicit write/edit to a source file in `/app/workspace/otp_src_27.3.2` and verified the modified region by reading it back
10. If the task or system instructions require an exact completion token or action line, treat it as mandatory output correctness and emit it exactly as the last line


## Approach

- Trace the exploit path end-to-end before editing: identify the incoming SSH message type, follow decode/dispatch through the current connection state, queueing if any, and confirm exactly where unauthenticated handling reaches the sensitive operation
- Read the exact dispatch and handler branches you plan to modify before naming the vulnerable message or exploit mechanism; treat exploit chains as hypotheses until you inspect the downstream handler that performs the sensitive action
- Confirm the exact message and state combination that reaches command execution before choosing a fix
- If a file read is truncated or incomplete, continue reading until the full relevant function body, clauses, and called functions are visible
- Treat header-only, comment-only, grep-only, tiny-fragment, or otherwise truncated reads as incomplete evidence; continue with targeted reads until the full relevant function body, neighboring clauses, and call path are visible before concluding anything
- Search the source with concrete code tokens, not English descriptions: use observed module names, function names, macros, atoms, records, message constants, strings such as `"exec"`, and exact clause heads as your grep/query patterns
- If earlier reads used abbreviated paths, offsets, searches, or truncated output, re-read the final target region contiguously from the verified file path before editing so full clause boundaries and surrounding code are visible
- Patch the minimal validated guard point in source code, typically by rejecting or deferring unauthorized message types until the connection is in the correct authenticated/connected state
- Prefer the narrowest evidence-backed enforcement point over broad repetitive blocking across many message types, and avoid unnecessary state-machine refactors when a local handler fix is sufficient
- Keep the result implementation-focused: investigation is intermediate work, not the deliverable
- No need to build or start server

- First, obey any task-specific execution/interface requirements exactly (for example mandated action formats, allowed tool names, JSON schemas, or exact completion tokens); do not substitute a different workflow
- Keep diagnosis claims provisional until you have read the full relevant handler/control-flow region and confirmed the unauthenticated path in code
- Do not state that pre-auth command execution is confirmed unless you have direct code evidence for each link: unauthenticated message admission, state handling/gating, downstream dispatch, and the sensitive operation
- If any key read is truncated, surrounding clauses are missing, or a search returns ambiguous/no results, explicitly treat the exploit path as unconfirmed and continue reading/searching before naming the root cause
- Do not commit to a root cause from search hits, isolated `ssh_connection:handle_msg/...` clauses, partial snippets, or dangerous sink handlers alone; read the full relevant decode/dispatch or state-machine branch and the downstream server-side handler that performs the sensitive action before naming the vulnerable message/state pair
- Trace from unauthenticated parser/state-machine entry through receive/decode, any event wrapping such as `{conn_msg, Msg}`, queueing/deferred handling, dispatch, fallback, and into the exact privileged handler you plan to patch; do not treat packet decoding, internal wrapping, or postponement as proof of an auth bypass
- Inspect the earliest shared connection/FSM dispatch boundary that admits the validated message path before patching individual `exec`/`shell`/subsystem or other leaf handlers; check both `ssh_connection_handler.erl` and `ssh_connection.erl`, plus any state-specific forwarding code, to prove whether pre-auth states delegate into generic privileged message handling
- If your investigation produces conflicting conclusions, stop and resolve them by reading the specific dispatch, deferred-queue, fallback, channel-setup, and later handler code that distinguishes those cases before editing
- For channel-related hypotheses such as `SSH_MSG_CHANNEL_REQUEST` / `"exec"`, also verify prerequisites: whether unauthenticated code can create or reference the needed channel, how channel open and channel lookup/cache behave before authentication, and whether the request is rejected earlier for missing state
- Before any structural edit to an Erlang handler or multi-clause function, read the entire target function/clause body plus enough surrounding clauses to see boundaries, guards, helper usage, fallthrough/default behavior, and module context; if output is truncated, continue reading until the whole region is visible
- Make edits only against exact, observed source text from the verified file; use real surrounding lines as anchors and never use paraphrases, placeholders, or guessed code summaries as edit targets
- After each edit, immediately read back the entire modified function or clause group plus adjacent clauses in full, not just a snippet, to verify inserted text, clause boundaries, separators, terminators, guards, helper placement, and fallback behavior in context
- If any edit leaves the file malformed, incomplete, or structurally suspect, stop and repair immediately: re-read the full affected function/clause group, restore valid Erlang structure, and do not proceed until the code is coherent again
- Do not replace a critical clause from a partial glimpse such as only a function head, `case`, or a few body lines; use precise observed edit anchors from the verified file path only after the exact existing text and boundaries are known
- Patch only the validated message/state combination unless additional message types or a broader dispatcher path were separately traced end-to-end and shown to require changes while preserving normal SSH behavior
- When evidence shows a common pre-auth dispatch layer admits the exploit path and fans out to multiple downstream handlers, prefer the earliest validated shared dispatcher/state guard over scattered sink-level checks; otherwise keep the later narrower guard
- Reuse existing OTP authentication/connection-state predicates, macros, and nearby helpers instead of inventing parallel auth tracking, and verify the exact pre-auth versus post-auth state variants and transitions involved rather than relying on broad state names
- Do not claim an unauthenticated dispatch path is vulnerable until you have identified the concrete field, predicate, state variant, or helper in code that represents authentication/connection status on that path, and shown how the offending message reaches the patched code before or despite that check
- Do not declare the vulnerability confirmed from grep hits, truncated reads, or a generic handler clause alone; only conclude the root cause after you have read the full relevant dispatch/state-check/handler chain in code and can point to the exact unauthenticated path
- If a message is valid later in the session but unsafe before authentication, use postponement only when code shows the state machine actually drains that postponed message after the intended authenticated/connected transition; otherwise reject it at the validated guard point before any side-effecting handler runs
- When rejecting an unauthorized channel-style request, preserve existing protocol reply semantics: send the normal failure response only when the request expects a reply, otherwise reject/ignore without inventing a new response path
- Once the vulnerable guard point is confirmed, make an actual `.erl` source edit in the repository and then read back the modified region before describing the patch as applied
- Do not describe a fix as applied until the repository shows an actual source edit: make the `.erl` change, read back the full modified region, and confirm a concrete `git diff` hunk exists in the intended file
- Separate reasoning from verification: do not say the fix is verified, validated, or confirmed by execution unless you have actual build, test, compile, or syntax-check output. If no execution check was performed, say so explicitly and limit claims to static inspection, readback, and diff review

## Tips

- Look at SSH message type handling in Erlang/OTP source
- Check for missing authentication checks
- Use git diff to verify changes


- Do not infer the vulnerability from isolated `ssh_connection:handle_msg/...` clauses alone; verify how the surrounding state-machine code actually delivers those messages before authentication
- Treat finding an `"exec"` or similar dangerous handler as a lead, not proof of exploitability; verify earlier channel, state, and authentication requirements first
- Distinguish reception/decoding or deferred handling of SSH messages from later authenticated processing; postponed or queued messages are not rejected and are not themselves proof of a vulnerability
- Prefer targeted guards on the evidenced message type or prerequisite state transition over broad protocol gating; when multiple downstream handlers share the same unsafe pre-auth entry path, a dispatcher-level connected/authenticated-state check is often the narrowest correct fix
- After identifying the bug, immediately edit the relevant `.erl` file; do not finish with only a vulnerability explanation
- Before broadening a fix from one message type to many or patching a broad dispatcher, inspect accepted states, transition behavior, unmatched-message fallthrough, and later handling so normal SSH flows still work after the change
- Before finishing, confirm there is a concrete diff in the source tree

- Verify the forwarding path from state-specific handling into shared connection-message dispatch in `ssh_connection_handler.erl` / `ssh_connection.erl` before editing leaf request handlers
- If connection-protocol messages are wrapped, queued, or forwarded as a common work-item type before auth, inspect that admission point first; it is often the narrowest safe fix location
- If you suspect an unauthenticated channel-request exploit, inspect both the request handler and the code that establishes/looks up channels before auth; prove that the request can reach the dangerous branch with the required channel context
- Avoid introducing new helper functions or moving clauses unless necessary for the narrow fix; if you do, read back the full enclosing function and adjacent declarations after editing to confirm valid Erlang structure
- Do not assume similarly named states are equivalent for security decisions; read the concrete state values/tuples and confirm which ones occur before authentication versus after authentication or rekey

- After each nontrivial `.erl` edit, reopen the complete affected function/clause group using surrounding real source context, not just a diff hunk or short snippet
- Before broadening a fix from one handler or message type to adjacent ones, prove from the actual pre-auth dispatch/state path that each added path is reachable and part of the demonstrated exploit
- If a task mandates an exact completion signal, do a final pre-send check that the required token appears exactly as instructed, typically as the last line
## Final Check

- Confirm the patch blocks the identified unauthorized message path, not a guessed broader class of messages
- Confirm the complete modified region was read back in full after the final edit
- Confirm modified Erlang functions have valid clause grouping, guards, return shapes, fallback behavior, and terminators after the edit
- Use `git diff` plus a surrounding code read to ensure the patch is coherent, narrowly scoped, and preserves normal SSH behavior outside the validated exploit path

- Confirm every action/tool emission followed any required task/system syntax exactly, including mandated schema, allowed tool names, and any exact final completion token
- Confirm the work log shows at least one successful concrete write operation to the intended `.erl` file; planned changes, searches, or prose descriptions do not count
- Confirm every edit was anchored to exact source text read from the verified file path immediately before patching; no placeholder strings, guessed anchors, paraphrased blocks, grep-only evidence, or truncated snippets were used as the basis for the edit
- Confirm the exact edited handler/function body was opened before the edit and the full modified function/clause group was read back again after the last edit; if output was truncated, continue until the whole region is visible
- Confirm you identified the concrete pre-auth state/dispatch/auth-status path that reaches the patched code and inspected the downstream side-effecting handler or shared privileged dispatch branch before choosing the guard point
- If any edit ever broke code structure during patching, confirm you repaired it and then re-read the full repaired function or clause group before finalizing
- Confirm `git diff` shows the intended hunk in the intended file, and do not claim stronger verification than you actually performed: report concrete compile/test/syntax output if run; otherwise explicitly rely on full source readback plus diff review and keep claims narrower

## Final Check

## Final Check

- Confirm the patch blocks the identified unauthorized message path, not a guessed broader class of messages
- Confirm the chosen guard point lies on the real unauthenticated dispatch path, runs before any side-effecting handler is invoked, and that any existing authentication flag/state reused by the patch is set on normal successful login flow
- Confirm the named vulnerability root cause is backed by a verified end-to-end reachability trace from unauthenticated input through decode/dispatch/state handling, including any queueing or deferred handling, to the sensitive operation
- Confirm the chosen fix point is the earliest shared dispatch/state gate actually reached by the exploit when evidence shows multiple downstream handlers fan out from that path; if you instead patched later, verify that narrower guard is required and sufficient
- Confirm every modified message type or path was individually evidenced; avoid or revert speculative edits to adjacent handlers, broad protocol ranges, or generic pre-auth behavior that were not part of the demonstrated exploit path
- Confirm the final behavior for the unauthorized message is terminal for that pre-auth input unless postponement was explicitly validated from code: it must not be accidentally preserved, rerouted through fallback behavior, or replayed into the sensitive handler after authentication
- If you used postponement/deferal, confirm the message type is valid after the intended authenticated/connected transition, the postponed path is actually drained, and the return shape matches neighboring clauses
- Confirm the fix uses an existing source of truth for authentication/connection state and established local guard conventions where available, while still permitting legitimate post-authentication or transitional handling visible in adjacent code
- Confirm unauthorized requests now fail with protocol-consistent behavior while authenticated or otherwise valid connected-session handling remains on the original path
- Confirm at least one Erlang source file in `/app/workspace/otp_src_27.3.2` was actually modified and `git diff` shows the intended concrete patch hunk in the intended file path; if there is no diff, the task is not complete
- Re-read the full edited function or clause group, including neighboring clauses, helper placement, delimiters, clause ordering, fallback/default branches, and surrounding module context; if output is truncated, continue until the whole modified region is visible
- Verify clause order, variable binding, matching, guard structure, separators, `end`/terminator placement, helper-function placement, disconnect reason construction, return tuple shape, and surrounding fallthrough/fallback behavior are intact after the edit
- Re-read your investigation notes for contradictions; if you have both "already gated by authenticated/connected state" and "unauthenticated path reaches command execution," do not finalize until one is disproven from code
- Confirm every tool/action used matched any explicitly required execution protocol, and if the task specifies an exact completion token or final-output format, emit it verbatim as the last line