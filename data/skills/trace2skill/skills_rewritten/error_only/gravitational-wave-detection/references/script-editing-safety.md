# Script Editing Safety

Use this when you are iteratively patching a Python search script or recovering from a suspicious overwrite.

## Core rules

1. Prefer narrow edits to full-file rewrites.
2. After every write, reopen the file and inspect enough of it to confirm the full program is present.
3. Run a quick syntax/import smoke test before any expensive execution.
4. If the file appears truncated, malformed, or unexpectedly short, stop and restore the last known-good version before making more changes.
5. Do not stack optimization refactors on top of an unverified edit.

## Recovery checklist

- Compare the current file against the last version that successfully imported or ran.
- Restore the last known-good script if the new one is incomplete.
- Reapply only the minimal needed patch.
- Reinspect the saved file.
- Run a bounded foreground test before resuming long or batched execution.

## Do / Do not

- Do inspect the actual saved file, not just the command you intended to write.
- Do treat a truncated preview or malformed file as a blocker.
- Do verify that the executable script path is the one you just inspected.
- Do not continue from a file that contains only partial code, stub comments, or cut-off definitions.
- Do not launch multiprocessing/background jobs from a script that has not passed a fresh syntax/import smoke test.
