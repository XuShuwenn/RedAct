---
name: syzkaller-ppdev-syzlang
description: "Write syzlang device descriptions for Linux parallel port driver (ppdev) including ioctl definitions and resource types."
---

# Syzkaller PPDEV Syzlang Support

## Runtime Protocol Overrides

- Follow the active environment/controller instructions exactly for tool invocation and final response format, even when they are not mentioned elsewhere in this skill.
- If the environment requires a specific tool-call schema, action syntax, or exact completion token/final line, use that exact format for every step and finish with exactly the required text.
- Treat protocol compliance as mandatory: a technically correct ppdev description still fails the task if the execution or completion format is wrong.
- For file creation or modification, write literal, inspectable file contents or exact text replacements grounded in the current file text; do **not** substitute placeholder descriptions such as "updated ioctl definition" or "created the constants file".

- Before the first tool/action step, identify the exact environment-required action/tool-call schema and any exact required completion token/string, then use that schema verbatim for every step.
- Do **not** invent alternate tool-call tags, wrappers, XML/markdown action blocks, pseudo-tools, or paraphrased completion messages when the environment specifies an exact protocol.
- If the environment requires waiting/polling for command results, keep doing so until you observe completion or an explicit blocking error; launching a command without later observing its result does **not** count as verification.
- Put a literal executable command string or exact file payload in each tool invocation. Do **not** send prose labels such as `inspect headers`, `write the constants file`, or `run verification` where a real command/content payload is required.
- If the environment requires an exact final completion string, emit that exact string as the final line and nothing else in place of it.


## When to Use

- Write syzlang device descriptions for ppdev
- Create syzkaller system call descriptions
- Define ioctl interfaces for /dev/parport*

## Required Files

1. `/opt/syzkaller/sys/linux/dev_ppdev.txt` - syzlang descriptions
2. `/opt/syzkaller/sys/linux/dev_ppdev.txt.const` - constant values

4c. Before introducing any flag set, enum-like domain, or named constant family, verify that the names are actually available in authoritative local userspace/UAPI headers, nearby syzkaller shared definitions, or another required public interface source. If they are not publicly exposed, model the field with the simplest validated numeric type or range instead of inventing symbolic flags or enums.
4d. Before declaring any helper struct or local replacement type, search shared files such as `sys.txt` and nearby `sys/linux/*.txt` for an existing reusable definition; reuse shared types such as `timeval` and built-ins such as `syz_open_dev` when available instead of creating duplicate structs, helper constants, or fake syscall constants.
4e. If the task still requires a specific ppdev/parport/IEEE1284 named constant that is absent from the local exported headers, consult an authoritative upstream Linux kernel header/source for that exact interface definition, copy only directly verified values, and record them in the same checklist used for local-header-derived items.## Workflow

1. Read the full authoritative headers before writing anything: inspect `linux/ppdev.h` and any needed related definitions from `linux/parport.h`.
2. Make a checklist of every ppdev ioctl, its ioctl number macro, argument type, and direction (`_IO`, `_IOR`, `_IOW`, `_IOWR`).
- Capture this checklist in a compact table before writing files: `ioctl name | _IO* macro kind | arg C type | planned syzlang arg model | const needed in .const`.
- Keep this checklist as the control document for the rest of the task: each declaration in `dev_ppdev.txt` and each constant in `.const` must map back to one checked header-derived row.
2a. Read enough of `linux/ppdev.h` and `linux/parport.h` to cover the complete relevant definitions before encoding anything; if a tool output is truncated, paged, or clipped, continue reading the remainder instead of extrapolating from the opening lines.
2c. Do not treat an opening chunk, summary, web snippet, or partial tool output as equivalent to header inspection. Continue reading until you have the full ioctl list, structs, and flag definitions from the authoritative local headers.
2d. Before writing any file, explicitly finish the header pass: if your reads of `linux/ppdev.h` or `linux/parport.h` only showed an opening segment, continue with additional reads until you have covered the remainder of each relevant file. Do not proceed based on a truncated first chunk plus memory or summaries.
2b. Mark which ioctls use size-sensitive argument types (especially any `timeval`-based commands), because their encoded constants may differ across `amd64` and `386`.
2e. Use the checklist to drive implementation order: (a) extract the ioctl inventory and `_IO*` directions from `linux/ppdev.h`, (b) inspect nearby `sys/linux/dev_*.txt` patterns for `syz_open_dev`, ioctl declaration style, pointer modeling, and per-arch `.const` syntax, then (c) encode ppdev with those repository-local idioms rather than inventing syntax from memory.

3. Treat kernel headers as the source of truth for ioctl names, numbers, flags, and structs; do **not** guess, hand-invent, or add interfaces not verified in headers.
4. Before creating either file, inspect a nearby syzkaller device description and its `.const` companion in `/opt/syzkaller/sys/linux/` to copy repository-local formatting exactly.
4a. Reuse nearby `sys/linux/dev_*.txt` and matching `.const` files as syntax/schema references for resource names, `syz_open_dev` specialization style, ioctl declaration shape, pointer payload modeling, `.const` layout, and supported per-arch override syntax; keep ppdev-specific names, numbers, and argument meanings derived from the headers.
4aa. Use this as a deliberate two-source check: derive the ppdev ABI surface from `linux/ppdev.h` / `linux/parport.h`, and derive repository-local syzlang syntax from nearby working `sys/linux/dev_*.txt` plus matching `.const` files. If syntax is uncertain, search for the exact in-tree construct you need and mirror that accepted pattern instead of improvising from memory.
4ab. Prefer ioctl-heavy character-device examples with both `.txt` and `.txt.const` companions (for example `dev_rtc`, `dev_i2c`, or `dev_loop`) when confirming current repository conventions for resources, opener specialization, ioctl declarations, pointer payloads, and per-arch constant layout.
4ac. For ioctls that pass integer-like values by address, model them as typed directional pointers (`ptr[in]`, `ptr[out]`, or validated mixed-direction forms) rather than bare scalars; confirm the exact shape against nearby accepted ioctl examples before finalizing ppdev declarations.
4b. While inspecting nearby files, also check whether common structs or helper types are already defined globally (for example in `sys.txt`) before declaring them locally; reuse shared definitions instead of duplicating standard types such as `timeval`.
4c. When a header-referenced value domain is not exposed as named userspace/UAPI constants, model it with the simplest validated numeric type or range instead of inventing unavailable symbolic flags or enums.

5. Only then write `dev_ppdev.txt` and `dev_ppdev.txt.const`.
6. Before writing, confirm the minimal modeled surface matches the headers: required includes, `fd_ppdev`, `syz_open_dev$ppdev("/dev/parport#", 0, 0)`, each ioctl name/number family, and each argument direction.
7. Prefer writing each target file in one shot (for example with a single-quoted heredoc or another atomic write method) instead of long chains of incremental appends.
7a. Every write must put the **actual final syzlang / `.const` source text** on disk. Do **not** write prose summaries, placeholders, status text, TODOs, or intent notes such as "created the syzlang description" or "generated constants" in place of real declarations/constants.
7b. Use concrete executable shell commands only. Do **not** replace commands with narrative labels such as `write the constants file`, `inspect headers`, or `run verification`.
7c. If you must patch an existing file, anchor the edit on exact surrounding text reread from disk first; if you cannot quote the real old/new content, stop and reread the file before editing.
7d. Immediately after each write or patch, reopen the affected file and verify the saved bytes are actual syzlang / `.const` syntax throughout, not narration, shell-escaping damage, or a partial fragment.
8. Prefer compiling a tiny C helper against the local headers to print ppdev/parport ioctl and flag values for `.const`; use that output to populate or cross-check constants instead of deriving encodings by hand.
9. As soon as both files are written, run `make descriptions` first to catch syntax/schema issues before the slower full build.
10. Immediately reopen both final files from `/opt/syzkaller/sys/linux/` and inspect the saved contents before any full build step; treat the on-disk files as authoritative over the intended payload.
10a. Inspect enough of each saved file to verify the complete implementation, not just the opening lines: use a full-file read or multiple reads that together cover the entire file.
10b. Do **not** claim counts, coverage, implemented structs, flag sets, or ioctl completion unless those exact items were confirmed in the final on-disk contents.
10c. File size checks, line counts, `grep` summaries, existence checks, or later build success do **not** substitute for reading the concrete saved text.
11. If writing directly into `/opt/syzkaller/sys/linux/` is awkward, stage the files in a writable location, verify them there, then copy them into the final paths and reread the final saved copies.
12. If readback shows truncation, malformed syntax, shell-quoting damage, wrong formatting, or a partial rewrite, fix that first and reread the saved files before continuing.
12a. Treat any visibly truncated tool output as **unverified** evidence. If a file-write command, `cat`/`sed` dump, or other shell result is cut off mid-command or mid-content, rerun a narrower readback/check until you can see the complete result.
12b. Base progress only on observed outcomes, not intended actions: do not conclude that a rewrite, copy, or verification step worked unless the output clearly shows the final saved content or an explicit success signal.
13. Keep a one-to-one mapping between the header-derived ppdev ioctl checklist and the syzlang ioctl declarations unless the task explicitly asks for extra variants; do **not** add alias/duplicate ioctl entries just to satisfy parser or unused-type complaints.
14. Do not claim coverage counts such as "all 23 ioctls" until you have extracted the complete ioctl list from the full untruncated headers and checked each entry off explicitly.

15. Treat any truncated write, placeholder payload, incomplete readback, empty inspection result, or contradictory check as a hard stop: resolve that exact issue from the saved files before continuing to constants generation, builds, or final reporting.



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
- Copy the opener/resource/ioctl declaration shape from the closest existing `sys/linux/dev_*.txt` example, then substitute only the ppdev-specific names, argument types, directions, and constants confirmed from headers.
- Prefer a single-quoted heredoc (`cat <<'EOF'`) or another write method that preserves `$` literally; do **not** introduce shell-quoting artifacts into the file content.
- After writing `dev_ppdev.txt`, immediately read back the exact `syz_open_dev$ppdev(...)` line and several ioctl declarations from disk before any build step. If the opener name, `$`, quotes, or parentheses differ from what you intended, rewrite the file first and only then continue.
- Do not claim full ioctl coverage, helper structs, or final ioctl counts from intent, command text, or partial previews. Read back enough of the saved file to visibly confirm those exact declarations before describing them as present.
- First derive the full ioctl list from `linux/ppdev.h`, then match the task scope exactly: include all 23 ioctls when full header coverage is requested, and exclude entries only when the task explicitly asks for a narrower set.
- Verify ioctl names, structs, and argument directions from the full untruncated contents of `linux/ppdev.h` and `linux/parport.h` before finalizing.
- Assign ioctl argument types only from the exact header definitions/macros. Do **not** upgrade an argument to flags, mode, phase, status, or another semantic domain based only on the ioctl name or nearby comments.
- Map syzlang argument handling directly from the ioctl macro kind in `linux/ppdev.h`: `_IO` means no argument, `_IOR` uses output-oriented pointer modeling, `_IOW` uses input-oriented pointer modeling, and `_IOWR` requires validated mixed-direction handling consistent with nearby syzkaller examples.
- When the header argument is an integer-like value passed via pointer, keep the payload modeled as a pointer to the corresponding integer width/category with the header-matching direction; do **not** collapse it to a raw scalar argument just because the logical value is numeric.
- Before adding any local struct used only to satisfy an ioctl argument, search `sys/linux/*.txt` for an existing shared definition and prefer that exact shared type when the layout matches the header.
- For each ioctl, keep read-style commands, write-style commands, and no-arg commands distinct based on the exact header macro usage and argument type rather than the ioctl name alone.
- Reuse existing syzkaller common type definitions when available; do not redeclare shared structs already provided elsewhere in `sys/linux/` unless the ppdev headers require a distinct layout.
- If `make descriptions` reports a syntax/schema issue, fix that exact declaration first and rerun `make descriptions` before attempting `make all`.

- After writing, verify the saved file contains literal syzlang syntax, not explanatory English. If read-back shows a summary sentence or other prose instead of actual declarations, the write failed and must be redone.



## dev_ppdev.txt.const

```
arches = amd64, 386
ioctl numbers and flag values
```


- Write the first line exactly as `arches = amd64, 386`.
- Treat that header as parser-critical project syntax: `arches = amd64, 386` must be the literal first line.
- Do **not** write `# arches = amd64, 386`, omit the header, or leave a placeholder stub expecting later steps to fix it.
- Before creating this file, inspect an existing `sys/linux/*.txt.const` example and copy its header/comment style exactly; do not rely on memory for `.const` file syntax.
- If parser output mentions a missing/invalid `arches` header or similar `.const` syntax problem, stop and compare the saved first lines against a nearby working `.txt.const` file before changing anything else.

- Do **not** prefix that line with `#` or any other comment marker.
- Populate constants from kernel headers or the syzkaller extraction/generation flow.
- Do **not** hand-compute ioctl numbers or flag values unless you verify them against a trustworthy extracted or build-produced result.
- Generate or validate constants in an architecture-aware way; do not copy amd64 values to 386 (or vice versa) by assumption.
- When one `.const` file covers multiple architectures, verify and use syzkaller's supported per-arch entry syntax from nearby `.const` files instead of forcing one shared value across both arches.
- Pay special attention to ioctls whose encoded size depends on argument layout; for ppdev, `PPGETTIME` and `PPSETTIME` require explicit per-arch validation because `struct timeval` size can differ between `amd64` and `386`.
- When a constant differs by architecture, encode explicit per-arch values in `.const` instead of copying one arch's number to the other.

- If any ioctl value depends on structure layout or encoded size bits, treat manual arithmetic as unsafe.
- For a multi-arch `.const` file, obtain or validate values for **each listed arch** from extraction, generated output, build products, or another direct evidence source; do **not** reuse values derived from one ABI for another by assumption.
- Prefer a small compiled helper/extractor that includes `linux/ppdev.h` and `linux/parport.h` and prints the needed ioctl and flag macros for each listed architecture.
- Treat a compiler-evaluated helper/probe as the default path for ppdev ioctl constants, especially for `_IOR`/`_IOW` commands and layout-sensitive entries; preserve the helper/extractor output long enough to compare the exact saved `.const` lines against it after writing.
- Treat copied, reformatted, or decimal-converted ioctl numbers as untrusted until they are checked back against direct helper/build/header-derived output; if a value had to be rewritten once, reread the final saved line and compare it again before continuing.
- Treat ABI-sensitive ioctl constants as mandatory per-arch checks: for commands backed by layout-sensitive structs, notably `PPGETTIME` and `PPSETTIME`, obtain `amd64` and `386` values separately and encode explicit per-arch overrides when they differ.
- If a first extraction attempt fails because ppdev ioctls are function-like macros, change the extraction method so the compiler/preprocessor evaluates the real header definitions; prefer a tiny C helper or another direct header-driven extraction path over hand-written `_IO*` reconstruction.
- If extraction/build-backed validation fails, debug that specific failure first and preserve the diagnostic; do **not** fall back to handwritten ioctl-encoding scripts, guessed completions, or visibly truncated numeric output.
- Evidence rule for multi-arch constants: include `386` only if you directly obtained or validated the ppdev constants for `386` from a successful extraction/build/helper run or another equally direct repository-backed source.
- A failed `gcc -m32`, missing multilib headers, or any other unsuccessful 386 helper/extraction attempt is affirmative evidence that `386` is still unvalidated; do **not** leave `386` in `arches = ...` or claim dual-arch coverage unless you later obtain direct successful 386 values by another method.
- If a `386` extraction attempt fails (for example due to missing multilib headers/toolchain), do **not** claim `386` coverage anyway; either resolve that blocker with another validated method or report that multi-arch validation remains incomplete.
- If a helper, generator, or compile attempt exposed a specific malformed constant or formatting bug, regenerate and then reopen the exact affected `.const` lines from disk before any build claim.
- If extraction, helper scripts, or ad hoc computations produce truncated, inconsistent, incomplete, or suspicious results, do not populate `.const` from them yet; rerun or use another trustworthy extraction path until every referenced constant is fully validated for each listed arch.
- Do **not** fill `.const` by hand from `_IOC` math, guessed struct sizes, or one-arch assumptions when `386` and `amd64` are both required.

- After writing the file, read back the first few lines and confirm the `arches = ...` header is present verbatim.
- Then inspect the full saved `.const` file, not just the header, to confirm no write truncation, cut-off numeric values, or partial constant list made it to disk.
- After any targeted edit to `.const`, reread the exact edited constant lines from disk and compare them against the validated source values before continuing.
- If a saved numeric value is shortened, partially overwritten, or otherwise differs from the validated helper/build output, stop and fix the write path; do **not** proceed with a known-corrupted `.const` file.
- After writing, verify the saved file contains literal `.const` syntax, not a description of intended contents.

- Include only constants actually referenced by `dev_ppdev.txt` plus any explicitly requested ppdev/IEEE1284 flag set; do not pad the file with guessed extras.
- Keep the `.const` file limited to values you can validate from headers, helper output, or trusted extraction/build-produced results; compare naming, ordering, and metadata conventions against nearby `.const` files, including whether `__NR_ioctl` is present.
- Include syscall-number constants only for real syscalls referenced by the description; do **not** add a `__NR_*` entry for the pseudo-call `syz_open_dev`.
- After `make descriptions`, reopen the saved `.const` file from disk and inspect enough of it to confirm the regenerated final file still contains the expected arch header and full ppdev constant set.

- If a helper/extractor initially emits malformed or partial `.const` lines (for example bad per-arch formatting, duplicated/truncated entries, or a previously failing macro such as `PPWSTATUS`), regenerate the file and then reopen the exact affected lines from disk before trusting any build result.
- A later passing tool run does **not** retroactively validate previously malformed constant lines; inspect the corrected saved `.const` text directly.
- Before adding any helper-related constant or local replacement type, verify it is truly required by nearby syzkaller examples and existing shared definitions; keep built-ins built-in and shared types shared.
- When generating constants, keep the extracted output organized per ioctl/flag name so you can compare it directly against the header-derived checklist before saving `.const`.




## Verification Commands

```bash
cd /opt/syzkaller
make descriptions
make all TARGETOS=linux TARGETARCH=amd64
```

Run these only after reading back the generated files and confirming they are complete.
Treat this as a staged gate: first use `make descriptions` to catch syntax/schema problems cheaply, then run `make all TARGETOS=linux TARGETARCH=amd64` only after the description step succeeds and the saved files were reread from disk.
Do not stop at build success: semantic verification against the full headers is still required.
Build success proves parse/build viability only. It does **not** prove that the requested ppdev surface was fully implemented, that the files contain real definitions instead of placeholder prose, or that every requested ioctl/constant is present.
- After builds pass, verify implementation claims from the saved files directly: if you claim a specific ioctl count, struct, opener, flag set, or arch entry, reread the exact on-disk lines that support that claim before responding.
- Never let `make descriptions` or `make all` substitute for end-of-file inspection of both generated files.
- Run `make descriptions` first and use its parser/type errors to drive the smallest syntax fix before attempting the full build.
- Treat `make descriptions` as the first required validation after both files are written and reread; use it as the fast gate for syntax, type, and `.const` integration before any broader build/debug cycle.
- If `make descriptions` fails on syzlang DSL syntax or declaration shape, immediately search `sys/linux/*.txt` for the same construct and copy the established in-tree form before trying novel rewrites from memory.
- Treat `make descriptions` as an early schema check, not final proof: after it passes, continue with the required build command and the header-to-syzlang audit rather than stopping at the first green validation step.
- Execute the required verification commands exactly as written; do **not** substitute `grep`, `syz-sysgen`, `make extract`, ad hoc scripts, or other partial proxies unless the task explicitly asks for them.
- If you try any extra validation command and it fails with usage text, invalid flags, timeout, unsupported-command behavior, empty result, or exit status != 0, treat that attempt as **no validation**; do not cite it as evidence the files are correct.
- Failed proxy checks do not become evidence via silence: if an extra parser/helper command prints nothing useful or only resets the shell/session, that is still **no validation**.
- Do not replace the required verification with unsupported alternatives such as ad hoc parser invocations unless the task explicitly asks for them and they complete with clear success evidence.
- If an earlier parser/build step reported an error and you later edit the files, do **not** claim verification succeeded until you rerun the required command and directly observe a clean completed result for that rerun.
- A truncated log, clipped tool output, or absence of an explicit success signal after rerunning still counts as unverified, not successful.
- Do **not** background `make all`, stop it early, or infer success from partial/truncated output. Wait for completion and confirm a clear success signal such as exit status 0.
- If the environment or tooling blocks the required commands, treat the task as unresolved until you either fix that issue or clearly report the exact blocking error.


- Run both commands to completion and do not claim success unless you directly observe clear completion for both commands, preferably explicit exit status `0` plus output consistent with completion.
- Do **not** infer success from partial output, dependency-download noise, silence, unrelated shell messages, piped/wrapper-truncated logs, or still-running output; if the result is ambiguous, rerun the exact command or a narrower targeted check with explicit status reporting until completion is observable.
- Prefer running verification with explicit status capture when output may be noisy or clipped, e.g. `make descriptions; echo EXIT:$?` and `make all TARGETOS=linux TARGETARCH=amd64; echo EXIT:$?`.
- If required build output is truncated, clipped, ends mid-stream, or only shows setup/download noise, treat it as **not run to completion**. Rerun the exact command with explicit status capture or a narrower tail/readback until you can directly observe success or failure.
- Do not translate startup logs, dependency-download noise, shell/job metadata, or a still-running/backgrounded job into success. If the command output has not yet shown completion, wait/poll and capture the final result before making any verification claim.
- A command counts as successful only if you directly observe completion plus a clear success signal such as `EXIT:0` or another equally explicit completed-success indication.
- Do **not** say a step `passed`, `succeeded`, or `looks good` while output is still partial, clipped, streaming, or missing an explicit completion signal; at that point the status is only `not yet verified`.
- If required verification currently fails, the task status is `unverified/failed`, not `completed successfully`, even if you suspect the error is unrelated. Report the exact blocking diagnostic and keep the final status aligned with the observed command results.
- Treat truncated, clipped, paged, still-streaming, malformed, mistyped, or otherwise ambiguous command/file output as **not yet verified**. If output is cut off or only shows setup/download noise, rerun with a narrower or more explicit check until you can directly observe the relevant result.
- If two validation checks disagree, stop and resolve the discrepancy from the saved files and direct commands before making any success claim.
- Before and after running builds, reopen `/opt/syzkaller/sys/linux/dev_ppdev.txt` and `/opt/syzkaller/sys/linux/dev_ppdev.txt.const` from their final paths and inspect the exact saved contents, including enough of each file to catch truncation rather than only spot-checking the top.
- Treat `make descriptions` and `make all` as necessary but not sufficient: after they pass, reconcile the final ioctl list against `linux/ppdev.h`, confirm argument directions match the header definitions, and ensure every constant referenced in `dev_ppdev.txt` is defined in `.const` for each listed arch.
- If either command fails, treat the task as unverified: quote the relevant diagnostic, make the smallest targeted fix, and rerun verification instead of guessing.
- On any failure or ambiguous result, first extract the exact parser/compiler/build diagnostic from the real output before editing files.
- Failure-handling sequence for `make descriptions` / `make all`: (1) rerun or narrow the command until you can see the exact diagnostic and an explicit completion signal, (2) quote or otherwise capture the concrete failing message/line, (3) inspect the exact referenced on-disk text, (4) make one smallest targeted fix, then (5) rerun the same verification command.
- When a diagnostic reports an unknown flag, type, resource, or identifier, first compare the exact referenced spelling in the error against the exact on-disk declaration/use sites and fix that concrete mismatch before trying structural changes such as reordering, renaming families, or remodeling arguments.
- Do **not** apply speculative fixes based on assumed parser rules when the observed error names a specific symbol; reconcile the named symbol directly, then rerun the failing step.
- When a diagnostic names an unknown flag, type, resource, or identifier, first compare the exact referenced spelling against the exact on-disk declaration before attempting broader fixes such as reordering, renaming families, or changing modeling strategy.
- Prefer direct identifier reconciliation over speculative edits: fix the concrete mismatch first, then rerun the relevant verification step.

- Treat direct file inspection as higher-priority evidence than a passing build. If readback, counts, or grep output suggests truncation, missing ioctls, malformed lines, or contradictory signals, stop and resolve that from the saved files before any success claim.
- On the first failure, stop and inspect the exact parser/compiler/build diagnostic before editing any file. Base each fix on an observed error, make the smallest targeted change, and rerun the relevant verification step instead of speculative trial-and-error rewrites.
- Do not treat build success, partial logs, or exit status alone as proof that the ppdev description is correct. After the commands pass, perform a semantic audit from the final on-disk files back to `linux/ppdev.h`.
- Treat final verification as a three-part check: (1) headers-to-syzlang audit, (2) saved-file readback from disk at the final paths, and (3) successful execution of the required repository build commands.
- Before declaring success, explicitly verify from the final saved files that every claimed ppdev ioctl came from `linux/ppdev.h`, that no extra unchecked interface was added, that the final ioctl count matches the header-derived checklist for the task scope, and that every constant referenced in `dev_ppdev.txt` is defined in `.const` for each listed arch.
- In the final audit, explicitly confirm the opener/resource pair is present, ioctl directions still match the `_IO*` forms from `linux/ppdev.h`, and every constant referenced in `dev_ppdev.txt` is defined in `.const` for each listed arch.
- During final constant audit, pay extra attention to ioctl constants whose encoded size depends on struct layout; confirm any such entries, especially `PPGETTIME` and `PPSETTIME`, have the correct per-arch values rather than assumed identical ones.
- During final audit, keep `.const` minimal and relevant: syscall constants should cover only actual syscalls used by the description.
- If `make descriptions` rewrites generated files, treat the post-generation on-disk contents as authoritative for final inspection; reread the full relevant ppdev sections rather than assuming the pre-build version survived unchanged.

- Base status claims only on evidence you directly observed from the final saved files and the required build commands; do **not** summarize what a write command was supposed to create.
- After each corrective edit made in response to a parser/build error, reread the affected file section and rerun the relevant verification step; do not chain speculative edits without confirming each one.
- In the final response, distinguish strictly between `completed successfully`, `failed with diagnostic`, and `did not finish / no confirming output observed`; never collapse the third case into success.

- Do not cite a write action itself, a narrated tool result such as "wrote file", or an indirect summary as evidence that a file now contains the intended definitions. The evidence must be the literal write payload or a direct reread of the final file contents from disk.
- If a write command's output is missing, indirect, or truncated, reopen the target file from disk before making any claim about what was saved.
- When using shell checks for counts or summaries, make the command self-validating and inspectable: prefer explicit commands such as `grep -c 'ioctl ' /opt/syzkaller/sys/linux/dev_ppdev.txt; echo EXIT:$?` or `sed -n '1,220p' /opt/syzkaller/sys/linux/dev_ppdev.txt` over narrative descriptions of what you intend to check.
- If a shell command returns empty output, an unexpected zero count, or a result inconsistent with prior observations, do not replace it with a different claim. First rerun an explicit readback/count command and identify whether the issue is the command pattern, file contents, or truncated output.



## Tips

- Check the complete `linux/ppdev.h` and relevant `linux/parport.h` definitions, not just the opening portion.
- Correct in/out arg directions.
- Match ioctl numbers from validated header-derived or build-produced constants, not manual reconstruction.
- Use kernel headers for the interface surface and nearby `sys/linux/*.txt` files for syzlang idioms; rely on both rather than either one alone.
- For `.const` generation, prefer a tiny compiled helper/extractor over manual `_IO`, `_IOR`, `_IOW`, or `_IOWR` macro expansion, especially for ABI- or struct-size-sensitive values.
- If symbolic names are unavailable in exported UAPI headers, encode the validated numeric type or range directly instead of inventing unsupported symbols.
- When a requested flag set or constant group is initially hard to find, keep tracing authoritative headers or generated constants until you either model it correctly or can state precisely what remains unresolved; do **not** silently widen the argument to a generic integer just to finish.
- Prefer an explicit unresolved note over a guessed or weakened ABI description when the header-backed representation is still unverified.
- If direct edits in `/opt/syzkaller/sys/linux/` are inconvenient, write under a writable directory, then copy into place and reread the final files from `/opt/syzkaller/sys/linux/` before building.

- Include **all ppdev ioctls from `linux/ppdev.h` (23 total)** when full coverage is requested, even commonly missed obsolete entries such as `PPWSTATUS`, `PPRFIFO`, `PPWFIFO`, `PPRECONTROL`, and `PPWECONTROL`.
- Derive ioctl argument types and directions from the exact header macros; do **not** infer semantics from ioctl names, comments, or memory.
- Keep related concepts distinct exactly as defined by headers (for example, phase vs mode vs flags vs status); do not substitute one domain for another without explicit header evidence.
- Do **not** hand-reconstruct ioctl encodings, flag values, widths, enums, or struct-sensitive ABI values if authoritative extraction or direct header validation is possible.
- If extraction or build tooling fails, investigate the specific error or missing macro handling rather than approximating values manually.
- Debug from observed diagnostics only: inspect the actual `make descriptions` or `make all` error output, then apply the minimal targeted change tied to that error.
- Cross-check representation choices against nearby syzkaller `sys/linux/*.txt` files when the headers define the interface but not the syzlang idiom.
- Before finishing, do a header-to-syzlang audit: verify `syz_open_dev` targets `/dev/parport#`, `fd_ppdev` is defined, `ppdev_frob_struct` is present, ioctl coverage matches the header-derived checklist, and constants match validated header values.

- Preserve the proven workflow order: authoritative headers first for interface truth, then nearby `sys/linux/dev_*.txt` and matching `.const` files for repository idioms and comparable ioctl pointer/input-output shapes, then programmatic constant extraction/validation, then file writes, then `make descriptions`, then full build.
- Preserve the split of responsibilities: headers define what ppdev exposes, while nearby syzkaller descriptions define how to encode those interfaces idiomatically.
- When exported symbolic constants are missing but the valid domain is still header-backed, prefer a bounded numeric range over omitting the ioctl or inventing unavailable symbolic names.
- For macro-heavy constants, either a tiny compiled helper or a preprocessor-backed extraction script is fine, as long as it evaluates the real local headers and you verify the final per-arch values before saving `.const`.



## Final Audit Before Responding

1. Re-open the saved `dev_ppdev.txt` and `dev_ppdev.txt.const` from disk.
2. Reconcile the ioctl checklist against `linux/ppdev.h`: names, count, argument type, and direction for every requested ioctl.
2a. Also reconcile that same checklist against the final on-disk `dev_ppdev.txt`: every checklist row should be represented once in syzlang or explicitly excluded by task scope, with no unchecklisted extras.
3. Confirm every constant referenced in `dev_ppdev.txt` is defined in `.const` for each listed arch, and that `.const` does not rely on unchecked arch assumptions.
3b. Confirm any modeled flag set or enum-like argument in `dev_ppdev.txt` uses only publicly available UAPI/shared syzkaller names. If the names are not actually exposed, replace that argument with the validated numeric representation before claiming completion.
3a. If any constant line was previously malformed, truncated, duplicated, or emitted with wrong per-arch formatting during this session, explicitly reopen and verify those exact lines in the final saved `.const` file before responding.
4. Confirm any claimed verification step has explicit observed success evidence; if not, rerun before answering.

5. Confirm the final on-disk files contain concrete syzlang / `.const` definitions throughout; no placeholder prose, status messages, TODOs, or narrative summaries may remain anywhere in either file.
6. Confirm your inspection covered the full saved files, not only selected snippets; if any observation was truncated or clipped, rerun that specific readback in a narrower form before responding.
7. Confirm every claimed verification command was actually run with the correct command/path, reached a clear completed result, and had directly observed success evidence where success is claimed.
8. Confirm any environment-mandated tool/action protocol and final completion token/string were followed exactly throughout the run.
8a. If the session required a specific action schema or exact terminator string, verify your own transcript matches it before responding; do not end with a natural-language summary when an exact completion token was required.
9. Do not state or imply success unless the reread saved files match your claims **and** the required build commands completed successfully with explicit observed evidence; otherwise answer with the exact unresolved failure state.
9a. Before stating coverage details such as ioctl counts, named structs, or flag groups, make sure those exact items were seen in the reopened final file contents; if the visible readback only shows a subset, describe only that confirmed subset or reread more of the file first.

10. Do not report completion from intent, partial snippets, counts, or silent commands. Report success only when the final saved files were reopened and inspected as concrete text, the checklist reconciles against both headers and final on-disk files, and the required verification commands produced explicit observed success evidence.
11. Sanity-check the final modeling against at least one nearby ioctl-heavy `sys/linux/*.txt` example so the opener style, resource usage, ioctl declaration form, mixed-direction pointer modeling, and any per-arch `.const` formatting still match repository-local conventions.
12. Perform a protocol audit before the final response: confirm the run used the required tool/action schema, no tool invocation contained placeholder prose instead of an executable command or literal file content, and the final line will be the exact environment-required completion token/string.
13. Confirm that any known-bad generated line from this session (especially malformed per-arch `.const` entries) was reread from the final saved file after the fix; do not rely on downstream build success as proof that the corrected text is now valid.
14. Report only outcomes supported by directly observed commands/file readback. If any earlier check was contradictory, empty, ambiguous, or still missing an explicit completion signal and you did not fully reconcile it, state that the task remains unresolved rather than converting that uncertainty into a success claim.