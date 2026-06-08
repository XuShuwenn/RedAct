# Protocol and Path Discipline

Use this when the task/environment specifies a mandatory action format, exact completion token, or restricted filesystem.

## Required interaction contract

1. Re-read the task/system protocol before the first tool call.
2. If a specific action syntax is required, use it verbatim for every action.
3. Do not substitute unsupported wrappers, custom tags, pseudo-tool markup, or prose descriptions of intended commands.
4. If an exact completion string is required, treat it as the only valid final response.

## Path authorization checklist

1. List every file you expect to read or write:
   - source workbook
   - helper script, if any
   - temporary files, if any
   - final output workbook
2. Confirm each absolute path is explicitly allowed by the task/context.
3. If any destination is not clearly authorized, stop and report the blocker.
4. Do not move "nearby" in the filesystem just because it seems convenient.

## Auditable execution rule

For each decisive step, make the operation inspectable:
- show the exact command
- show the exact file path
- show the exact code written or edited
- show the exact validation output

Do not use placeholders like:
- "inspect workbook"
- "run python3 ..."
- "fix formula logic"
- "improve matching"

Instead, emit the concrete command or concrete edit.

## Finalization after late fixes

If you discover a bug after an apparent success:
1. treat earlier validation as obsolete
2. apply the concrete fix
3. rerun save/recalc/reopen validation on the latest workbook
4. confirm the final artifact path again
5. only then emit the exact completion token

## Quick self-check

- Did every tool call follow the mandated format?
- Did every write happen in an explicitly authorized path?
- Are all critical commands concrete rather than descriptive placeholders?
- Was the workbook revalidated after the last actual change?
- Is the final response exactly the required completion token, with no extra prose?