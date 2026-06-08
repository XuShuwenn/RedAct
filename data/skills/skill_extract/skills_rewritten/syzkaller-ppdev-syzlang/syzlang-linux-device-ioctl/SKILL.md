---
name: syzlang-linux-device-ioctl
description: "Author syzkaller syzlang support for Linux character devices: resources, openers, ioctl descriptions, and per-arch constants with verification."
---

Syzkaller Device Description Authoring (Linux ioctls)

This skill guides creating syzkaller syzlang support for a Linux device node that exposes ioctl operations. It covers harvesting interface definitions from headers, mapping ioctl directions, defining resources, struct and flag sets, and producing a matching constants file with architecture-specific values. It also includes standard verification steps and robust recovery checks.

When to Use

- Adding support for a new Linux device under /dev/* to syzkaller
- Modeling ioctl-based driver interfaces defined by kernel headers
- Creating the .txt (syzlang) and .txt.const (constants) files and validating with syzkaller’s build

Core Workflow

Phase 1: Inventory the Interface
- Locate the userspace-accessible headers that define the ioctl interface, structures, and flags (e.g., /usr/include/linux/<driver>.h and any dependent headers).
- Enumerate all ioctl commands that should be modeled; confirm the count against the header to avoid omissions.
- Identify any helper structs and known flag sets used by the ioctls.

Phase 2: Reuse Established Syzlang Patterns
- Inspect similar existing syzlang device descriptions in /opt/syzkaller/sys/linux to mirror structure and style:
  - include <linux/...>
  - resource fd_<dev>[fd]
  - syz_open_dev$<dev>("/dev/<path>#", ...) returning fd_<dev>
  - read/write syscalls if the device supports them (optional but common)
  - ioctl$NAME(...) entries for each ioctl
  - struct and flags definitions referenced by the ioctls
- Prefer using shared/common types already defined in syzkaller (e.g., timeval) rather than redefining them.

Phase 3: Map Ioctl Directions and Argument Types
- Determine argument direction from ioctl macro type (check header):
  - _IO or _IOC_NONE → usually no data payload; model a no-arg ioctl or a simple integer if explicitly required by header
  - _IOR or _IOC_READ → kernel writes to user → use ptr[out, TYPE]
  - _IOW or _IOC_WRITE → kernel reads from user → use ptr[in, TYPE]
  - _IOWR or _IOC_READ|_IOC_WRITE → both directions → use ptr[in, TYPE] if the buffer is both read and written, or follow existing device examples for combined direction handling
- Use flags[SET, BASETYPE] for bitmask arguments when the header provides named flags. If no exported names exist for a value family, use an integer type with an appropriate range instead.
- For helper structs:
  - Define syzlang struct fields with exact sizes and signedness from headers
  - Avoid redefining common types (search syzkaller tree first)

Phase 4: Author the Syzlang File (.txt)
- Add header includes for the interface and dependencies
- Define a device fd resource (resource fd_<dev>[fd])
- Provide a syz_open_dev opener that targets the correct path pattern (e.g., "/dev/<name>#") and returns the resource
- Add read/write entries if applicable
- Add ioctl entries for each command with correct direction and types; ensure names are distinctive and map to constants you will define in the .const file
- Define helper structs and flag sets used in ioctl entries

Phase 5: Create the Constants File (.txt.const)
- arches = amd64, 386 (or the subset required)
- Provide numeric values used by the .txt file:
  - All ioctl command numbers referenced
  - Flag values for any defined flag sets
  - Any other numeric constants needed by the syzlang file
- Where architecture affects ioctl numbers (e.g., due to sizeof differences), provide per-arch values. Use a helper program to extract the numbers by including the headers and printing macro expansions.

Phase 6: Verification
- Run: cd /opt/syzkaller; make descriptions
  - Fix syntax errors, missing constants, duplicate type definitions, or unused flag sets reported by the tool
- Confirm coverage:
  - Count defined ioctls vs. header count
  - Confirm opener path pattern is syntactically correct and returns the device resource
- Run: cd /opt/syzkaller; make all TARGETOS=linux TARGETARCH=amd64
  - This validates integration and generated outputs
- Spot-check chosen entries against headers to confirm direction and types

Verification Checklist
- Ioctl count in .txt matches intended coverage from headers
- Every ioctl used in .txt has a numeric mapping in .txt.const
- All flag sets defined are referenced by at least one ioctl entry
- No local redefinition of shared/common types present in syzkaller
- make descriptions succeeds without errors; then make all succeeds for the target architecture(s)

Common Pitfalls and Recoveries
- Wrong directions for ioctl arguments:
  - Always derive from _IO/_IOR/_IOW/_IOWR; verify via headers
- Missing architecture-specific values for ioctls whose size depends on types:
  - Compute on each required arch; cross-check host (64-bit) and 32-bit builds
- Using symbolic names not exported in userspace:
  - If macros are not present in userspace headers, use explicit integers or an int range in syzlang; define values in .txt.const only if known and stable
- Duplicating existing common types or structs:
  - Search existing syzlang files; reuse shared types like timeval instead of redefining them
- Defining flag sets but not referencing them:
  - Update ioctl entries to use flags[SET, BASETYPE] so the build doesn’t warn/fail on unused definitions
- Writing to restricted directories:
  - Write to a temporary location and move/copy into the target directory if direct writes fail
- Running full build before description validation:
  - Always run make descriptions first to isolate description issues

Optional Script Usage

Use the provided helper to extract ioctl and flag macro values from headers. This reduces manual mistakes and helps detect architecture differences.

- Typical workflow:
  - Identify header includes and macro names you need
  - Run the script for the host arch and optionally with -m32 to capture 32-bit values
  - Paste the outputs into the .txt.const file under the appropriate arch sections

Success Criteria
- The syzlang .txt file compiles and passes make descriptions
- The .txt.const file provides all required values for specified arches
- Full project build completes for at least one target arch
- The device resource, opener, ioctl entries, structs, and flags align with header definitions and shared syzkaller types
