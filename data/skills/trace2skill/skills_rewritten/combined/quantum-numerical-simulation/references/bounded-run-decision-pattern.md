# Bounded Run Decision Pattern

## When to read this
Read this before launching a long production run in a constrained environment, or when you have already checked a running job several times without new evidence.

## Core rule
Turn monitoring into a bounded decision loop:
1. Define the next required evidence before the run starts.
2. Wait/check only long enough to learn whether that evidence appears.
3. If repeated checks show no new evidence, make one validated plan change instead of continuing to poll.

## What counts as evidence
Use concrete artifacts or checkpoints, for example:
- reduced-case CSV written and non-empty
- `case 1` finished
- a new flushed in-script checkpoint such as `steadystate done`
- target CSV file created and growing/completed
- explicit traceback/error showing what failed

CPU time, process existence, or "still running" alone are **not** sufficient progress signals.

## Restart rule
Restart a heavy run only when at least one of these is true:
- you observed a real failure (traceback, error exit, invalid model, wrong dims)
- the same stage has stalled repeatedly with no artifact/checkpoint progress
- a materially changed on-disk script/configuration has already passed a quick faithful validation

Do **not** kill and relaunch just because a different solver or option seems promising.

## Restricted-shell monitoring
If utilities like `ps`/`pgrep` are unavailable, use tools you have already confirmed exist:
- inspect logs/files directly
- use `ls` for artifact presence/size
- use short Python commands to check file existence, size, or parse progress logs

## End-state rule
Do not spend the session in indefinite observation. After several checks with no new evidence, choose exactly one next action:
- keep waiting because progress evidence is present
- pivot to one validated new plan
- report the blocking stage with evidence if completion is not achievable in the environment