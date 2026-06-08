---
name: syzkaller-ppdev-syzlang
description: "Write syzlang device descriptions for Linux parallel port driver (ppdev) including ioctl definitions and resource types."
---

# Syzkaller PPDEV Syzlang Support

## When to Use

- Write syzlang device descriptions for ppdev
- Create syzkaller system call descriptions
- Define ioctl interfaces for /dev/parport*

## Required Files

1. `/opt/syzkaller/sys/linux/dev_ppdev.txt` - syzlang descriptions
2. `/opt/syzkaller/sys/linux/dev_ppdev.txt.const` - constant values

## Workflow

1. Read the full authoritative headers before writing anything: inspect `linux/ppdev.h` and any needed related definitions from `linux/parport.h`.
2. Make a checklist of every ppdev ioctl, its ioctl number macro, argument type, and direction (`_IO`, `_IOR`, `_IOW`, `_IOWR`).
3. Treat kernel headers as the source of truth for ioctl names, numbers, flags, and structs; do **not** guess, hand-invent, or add interfaces not verified in headers.
4. Before creating either file, inspect a nearby syzkaller device description and its `.const` companion in `/opt/syzkaller/sys/linux/` to copy repository-local formatting exactly.
5. Only then write `dev_ppdev.txt` and `dev_ppdev.txt.const`.


## dev_ppdev.txt Content

```
include <linux/ppdev.h>
include <linux/parport.h>
resource fd_ppdev[fd]
syz_open_dev/dev/parport# -> fd_ppdev
ioctl ppdev_ioc... (23 total)
ppdev_frob_struct { mask, val }
IEEE1284 mode flags + ppdev flags
```

- Use a normal syzlang specialization name for the opener, e.g. `syz_open_dev$ppdev("/dev/parport#", 0, 0) fd_ppdev`.
- Prefer a single-quoted heredoc (`cat <<'EOF'`) or another write method that preserves `$` literally; do **not** introduce shell-quoting artifacts into the file content.
- After writing `dev_ppdev.txt`, read back the exact opener and ioctl declarations from disk to confirm shell quoting did not corrupt identifiers.
- Implement ioctl descriptions for all 23 ppdev ioctls from `linux/ppdev.h` when the task requests the full header set; do not omit entries because they are labeled obsolete unless explicitly told to exclude them.
- Verify ioctl names, structs, and argument directions from the full untruncated contents of `linux/ppdev.h` and `linux/parport.h` before finalizing.


## dev_ppdev.txt.const

```
arches = amd64, 386
ioctl numbers and flag values
```


- Write the first line exactly as `arches = amd64, 386`.
- Do **not** prefix that line with `#` or any other comment marker.
- Populate constants from kernel headers or the syzkaller extraction/generation flow.
- Do **not** hand-compute ioctl numbers or flag values unless you verify them against a trustworthy extracted or build-produced result.
- Generate or validate constants in an architecture-aware way; do not copy amd64 values to 386 (or vice versa) by assumption.
- If any ioctl value depends on structure layout or encoded size bits, treat manual arithmetic as unsafe.
- After writing the file, read back the first few lines and confirm the `arches = ...` header is present verbatim.


## Verification Commands

```bash
cd /opt/syzkaller
make descriptions
make all TARGETOS=linux TARGETARCH=amd64
```

Run these only after reading back the generated files and confirming they are complete.

- Run both commands to completion and do not claim success unless you observe clear success signals for both commands, such as successful output and/or exit status 0.
- Do **not** infer success from partial output, silence, unrelated shell messages, or still-running/truncated output; rerun a targeted check if the result is ambiguous.
- Before and after running builds, reopen `/opt/syzkaller/sys/linux/dev_ppdev.txt` and `/opt/syzkaller/sys/linux/dev_ppdev.txt.const` from their final paths and inspect the exact saved contents.
- Treat `make descriptions` and `make all` as necessary but not sufficient: after they pass, reconcile the final ioctl list against `linux/ppdev.h`, confirm argument directions match the header definitions, and ensure every constant referenced in `dev_ppdev.txt` is defined in `.const` for each listed arch.
- If either command fails, treat the task as unverified: quote the relevant diagnostic, make the smallest targeted fix, and rerun verification instead of guessing.


## Tips

- Check linux/ppdev.h for ioctl definitions
- Correct in/out arg directions
- Match ioctl numbers from kernel headers


- Include **all ppdev ioctls from `linux/ppdev.h` (23 total)** when full coverage is requested, even commonly missed obsolete entries such as `PPWSTATUS`, `PPRFIFO`, `PPWFIFO`, `PPRECONTROL`, and `PPWECONTROL`.
- Derive ioctl argument types and directions from the exact header macros; do **not** infer semantics from ioctl names, comments, or memory.
- Keep related concepts distinct exactly as defined by headers (for example, phase vs mode vs flags vs status); do not substitute one domain for another without explicit header evidence.
- Do **not** hand-reconstruct ioctl encodings, flag values, widths, enums, or struct-sensitive ABI values if authoritative extraction or direct header validation is possible.
- If extraction or build tooling fails, investigate the specific error or missing macro handling rather than approximating values manually.
- Debug from observed diagnostics only: inspect the actual `make descriptions` or `make all` error output, then apply the minimal targeted change tied to that error.
- Cross-check representation choices against nearby syzkaller `sys/linux/*.txt` files when the headers define the interface but not the syzlang idiom.
- Before finishing, do a header-to-syzlang audit: verify `syz_open_dev` targets `/dev/parport#`, `fd_ppdev` is defined, `ppdev_frob_struct` is present, ioctl coverage matches the header-derived checklist, and constants match validated header values.

