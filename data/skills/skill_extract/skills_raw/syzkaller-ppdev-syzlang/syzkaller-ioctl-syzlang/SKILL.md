---
name: syzkaller-ioctl-syzlang
description: "Model Linux character devices in syzkaller: create syzlang files with ioctl ops, compute constants (with arch overrides), and verify via sysgen/build."
---

# Syzkaller Device Modeling for Linux IOCTL Interfaces

Build complete syzlang support for a Linux character device: define resources and openers, describe ioctls with correct directions and types, compute and record constants (including arch-specific overrides), and validate with syzkaller's generator and build pipeline.

## When to Use

Activate this skill when you need to:
- add a new `/dev/...` device to syzkaller
- describe a set of Linux ioctls from kernel headers
- compute ioctl numbers and flag values for one or more architectures
- verify syzlang syntax and integration with syzkaller

## Core Workflow

1. Inventory the interface from headers
- Locate and read the UAPI headers (typically under `/usr/include/linux/` and related includes) defining the device’s ioctls, flags, and structs.
- Identify the ioctl macro used and its direction and payload:
  - _IO(type, nr) → no argument
  - _IOR(type, nr, T) → out (kernel writes to user), arg is ptr[out, T]
  - _IOW(type, nr, T) → in (user writes to kernel), arg is ptr[in, T]
  - _IOWR(type, nr, T) → inout, arg is ptr[in, T] but content may be mutated (use ptr[in, T] or ptr[inout, T] depending on syzlang support)
- List non-obsolete ioctls you intend to model. Exclude entries explicitly marked obsolete/deprecated to reduce noise.

2. Map kernel types to syzlang types
- Scalars:
  - unsigned char/char → int8
  - int/unsigned int → int32
  - long-sized fields vary by arch; use syzkaller predefined types when available or model via struct with arch-specific constants.
- Common structs:
  - If the struct already exists in `sys/linux/sys.txt` (e.g., timeval), reuse it by name; do not redefine.
  - Otherwise, define a minimal struct in your dev file with explicit field types.
- Flags:
  - Create named flag sets for bitmasks, then reference them via `flags[set_name, base_type]` (both arguments required).

3. Author the device description (dev_*.txt)
- Start with includes for the UAPI headers used by constants in your `.const` file:
  - `include <linux/<header>.h>` lines at the top.
- Define a resource for file descriptors and an opener:
  - `resource fd_<dev>[fd]`
  - Use a `syz_open_dev$<dev>` with a device path pattern such as `/dev/<name>#`, id intptr, and flags `flags[open_flags]`.
- Add read/write if the device supports them:
  - `read$<dev>(fd fd_<dev>, buf ptr[out, array[int8]], count len[buf])`
  - `write$<dev>(fd fd_<dev>, buf ptr[in, array[int8]], count len[buf])`
- For each ioctl, follow the macro’s direction for the argument pointer and match the base type:
  - Example patterns (names and types are illustrative):
    - `ioctl$FOO(fd fd_<dev>, cmd const[FOO])`          // _IO
    - `ioctl$BAR(fd fd_<dev>, cmd const[BAR], arg ptr[out, int8])` // _IOR unsigned char
    - `ioctl$BAZ(fd fd_<dev>, cmd const[BAZ], arg ptr[in, int32])` // _IOW int
    - `ioctl$QUX(fd fd_<dev>, cmd const[QUX], arg ptr[in, timeval])` // time struct
    - `ioctl$FLG(fd fd_<dev>, cmd const[FLG], arg ptr[in, flags[my_flags, int32]])`
- Define any helper structs and flag sets used by your ioctls after the ops:
  - `my_struct { field1 int8; field2 int8 }`
  - `my_flags = MY_FLAG_A, MY_FLAG_B`

4. Compute constants and create the .const file
- Create a constants file `/opt/syzkaller/sys/linux/dev_<dev>.txt.const` with:
  - First non-comment line: `arches = amd64, 386` (or the arches you need)
  - Only constants referenced by your dev file: ioctl numbers, flag values, etc.
  - Use decimal values. For arch-specific differences, provide overrides using `arch:value` suffixes, e.g., `NAME = <amd64_value>, 386:<i386_value>`.
- Compute ioctl numbers using the Linux `_IOC` encoding. For types whose size varies by arch (e.g., structs with longs like timeval), compute two sizes and encode per-arch numbers accordingly.
- Prefer programmatic computation (C or Python) to avoid mistakes. You can use the included helper script (see Optional Script Usage) to calculate values.

5. Verify
- Run syzkaller’s generator for syntax and constant validation:
  - `cd /opt/syzkaller && make descriptions`
- Build for a target arch to ensure integration:
  - `cd /opt/syzkaller && make all TARGETOS=linux TARGETARCH=amd64`
- Success criteria:
  - No syzlang parsing errors.
  - No unresolved or unused constants (unless intentionally included for future use).
  - Build completes for the targeted architecture(s).

## Verification Checklist
- dev file includes match header usage for constants in `.const`.
- Every `const[NAME]` referenced in dev file has a value in `.const`.
- Every flag set used appears in `.const` with consistent naming.
- Each `flags[set, base]` includes the base type (e.g., `int32`).
- Directions match ioctl macros: `_IOR` → ptr[out], `_IOW` → ptr[in], `_IO` → no arg.
- Arch-specific ioctl numbers provided for size-varying payloads.
- `arches = ...` header present as a non-comment, first line in `.const` (after optional banner comment).

## Common Pitfalls and How to Avoid Them
- Wrong arg direction: `_IOR` is out (ptr[out]), `_IOW` is in (ptr[in]); `_IOWR` is inout.
- Missing base type in `flags[...]`: syzlang requires both the flag set name and base integer type.
- Arch-specific sizes ignored: structs containing long-sized fields (e.g., timeval) cause different ioctl numbers across arches; add per-arch overrides with `386:<value>`.
- Constants mismatch: names in `.const` and dev file must align exactly; unused constants may trigger warnings.
- Commented or malformed arches header: `arches = ...` must not be commented and must appear in the constants file header.
- Redefining common types: reuse standard types (like `timeval`) already defined by syzkaller rather than redefining them.
- Including obsolete ioctls: model only those intended for userspace; kernel headers may carry obsolete entries.

## Optional Script Usage

Use `scripts/ioc_calc.py` to compute ioctl numbers programmatically.

Example usage (generic, not device-specific):
- Compute two ioctls for both amd64 and 386 where the second uses a struct with different sizes by arch.

1) Compute values:
- `python3 scripts/ioc_calc.py --type-char p --def FOO:_IO:0x80 --def BAR:_IOR:0x81:1`
- `python3 scripts/ioc_calc.py --type-char p --def BAZ:_IOW:0x82:16:8`  # 16 on amd64, 8 on 386

2) Add to `.const`:
- For equal values across arches: `FOO = <value>`
- For arch-specific: `BAZ = <amd64_value>, 386:<i386_value>`

## Templates

- Opener:
  - `syz_open_dev$<dev>(dev ptr[in, string["/dev/<name>#"]], id intptr, flags flags[open_flags]) fd_<dev>`
- No-arg ioctl:
  - `ioctl$NAME(fd fd_<dev>, cmd const[NAME])`
- In-arg ioctl:
  - `ioctl$NAME(fd fd_<dev>, cmd const[NAME], arg ptr[in, <type>])`
- Out-arg ioctl:
  - `ioctl$NAME(fd fd_<dev>, cmd const[NAME], arg ptr[out, <type>])`
- Flags:
  - `ioctl$NAME(fd fd_<dev>, cmd const[NAME], arg ptr[in, flags[my_flags, int32]])`
- Struct:
  - `my_struct { field1 int8; field2 int8 }`

By following this workflow and checks, you can reliably add new Linux device interfaces to syzkaller with correctly directed ioctls, accurate constants, and build-verified descriptions.
