# Fallback Branch Verification

Use this when a primary TTS path failed and you changed code or commands to use a fallback.

## Goal

Prove the new branch is actually the one being executed before spending another long run.

## Minimal verification pattern

1. Read back the exact script or command that will run.
2. Confirm the primary failing engine call is removed, guarded, or disabled.
3. Add one visible marker for the selected branch if needed (for example, print the engine name).
4. Run one tiny fallback-only synthesis sample.
5. Inspect logs or stderr and confirm they no longer mention the old failing engine, API, or traceback site.
6. Only then rerun the larger pipeline.

## Treat these as proof the switch did NOT take effect

- same engine name appears in logs
- same traceback file and line recur
- same failing API call or CLI is still invoked
- the supposed fallback run never prints or logs its branch marker

If any of those happen, stop. Fix the executed path or control flow first instead of retrying the full job.

## Practical rule

A claimed fallback is not real until a tiny direct sample shows different execution evidence and produces a readable artifact through the fallback path.
