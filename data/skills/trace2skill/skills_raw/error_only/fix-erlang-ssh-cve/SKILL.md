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


## Approach

- Trace the exploit path end-to-end before editing: identify the incoming SSH message type, follow decode/dispatch through the current connection state, queueing if any, and confirm exactly where unauthenticated handling reaches the sensitive operation
- Read the exact dispatch and handler branches you plan to modify before naming the vulnerable message or exploit mechanism; treat exploit chains as hypotheses until you inspect the downstream handler that performs the sensitive action
- Confirm the exact message and state combination that reaches command execution before choosing a fix
- If a file read is truncated or incomplete, continue reading until the full relevant function body, clauses, and called functions are visible
- Patch the minimal validated guard point in source code, typically by rejecting or deferring unauthorized message types until the connection is in the correct authenticated/connected state
- Prefer the narrowest evidence-backed enforcement point over broad repetitive blocking across many message types, and avoid unnecessary state-machine refactors when a local handler fix is sufficient
- Keep the result implementation-focused: investigation is intermediate work, not the deliverable
- No need to build or start server

## Tips

- Look at SSH message type handling in Erlang/OTP source
- Check for missing authentication checks
- Use git diff to verify changes


- Do not infer the vulnerability from isolated `ssh_connection:handle_msg/...` clauses alone; verify how the surrounding state-machine code actually delivers those messages before authentication
- Treat finding an `"exec"` or similar dangerous handler as a lead, not proof of exploitability; verify earlier channel, state, and authentication requirements first
- Distinguish reception/decoding or deferred handling of SSH messages from later authenticated processing; postponed or queued messages are not rejected and are not themselves proof of a vulnerability
- Prefer targeted guards on the evidenced message type or prerequisite state transition over broad protocol gating
- After identifying the bug, immediately edit the relevant `.erl` file; do not finish with only a vulnerability explanation
- Before broadening a fix from one message type to many or patching a broad dispatcher, inspect accepted states, transition behavior, unmatched-message fallthrough, and later handling so normal SSH flows still work after the change
- Before finishing, confirm there is a concrete diff in the source tree



## Final Check

## Final Check

- Confirm the patch blocks the identified unauthorized message path, not a guessed broader class of messages
- Confirm the complete modified region was read back in full after the final edit
- Confirm modified Erlang functions have valid clause grouping, guards, return shapes, fallback behavior, and terminators after the edit
- Use `git diff` plus a surrounding code read to ensure the patch is coherent, narrowly scoped, and preserves normal SSH behavior outside the validated exploit path