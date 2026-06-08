---
name: lean4-induction-sequence-bounds
description: "Finalize Lean4 proofs for recursive sequences and inequality bounds by proving a closed form or a stronger inductive invariant, while respecting strict file-prefix and build constraints."
---

# Lean4 Induction for Recursive Sequence Bounds

Use this skill to complete Lean4 proofs that establish bounds on recursively-defined sequences. It focuses on two robust strategies—closed-form identification and stronger inductive invariants—and on safely editing within template constraints while compiling with no warnings.

## When to Use

Activate this skill when:
- You must finish a Lean4 proof in a provided template with a strict "do not edit" prefix.
- The goal is an inequality on a recursively-defined sequence over natural numbers.
- Only project-local tactics are available (e.g., custom `Induction`, `Numbers`, `Addarith`, `Extra`).

## Core Workflow

1. Inspect and Respect Constraints
- Read the target file and identify the exact "do not change" prefix (including leading blank lines). Do not alter it.
- Confirm that only the specified file may be changed and warnings count as errors.

2. Discover Available Tools
- Rely on imported modules already present in the file. Do not add imports unless explicitly allowed.
- Skim local tactic files mentioned in imports to learn what is available (e.g., induction helpers, arithmetic solvers, positivity tools). Do not assume external tactics exist.

3. Choose a Robust Proof Strategy
- Strategy A (Closed Form): Prove an exact identity for the sequence by induction, then derive the bound from a sign/monotonicity argument.
  - Inductive step template:
    - Unfold the recurrence with `simp`/`dsimp` on the sequence definition.
    - Rewrite using the induction hypothesis.
    - Finish with basic algebraic simplification provided by the project tactics.
  - After obtaining the identity, rewrite the goal and conclude using nonnegativity/positivity lemmas and a lightweight arithmetic tactic.

- Strategy B (Stronger Invariant): Prove a stronger inequality that leaves "slack" sufficient for the next increment.
  - Inductive step template:
    - Unfold the recurrence with `simp [recurrence]`.
    - Use the induction hypothesis to bound the previous term.
    - Show the increment fits within the remaining slack. Reduce this to a basic identity or inequality on the increment (e.g., a relationship between consecutive terms of a geometric progression).

4. Implement Carefully
- Base Case:
  - `simp`/`dsimp` the definition at 0.
  - Close with a simple numeric step (`numbers` or a project-provided arithmetic tactic).
- Step Case:
  - `simp [recurrence, IH]` to unfold and use the hypothesis.
  - Keep expressions in a shape that your arithmetic tactic can consume; avoid unnecessary rewrites that complicate denominators or exponents too early.
  - Use positivity/nonnegativity lemmas to justify inequality steps on reciprocal or power terms.

5. Type and Algebra Hygiene
- Ensure all numeric terms live in the intended type (e.g., `ℚ` or `ℝ`). If coercions are implicit, keep term shapes consistent.
- When dealing with powers and reciprocals:
  - Use natural exponents for recursive steps.
  - Prefer identities that match the IH’s form to minimize rewriting.

6. Finalize and Verify
- Remove any exploratory lemmas or unused `have` statements to avoid warnings.
- Ensure there are no `sorry` or placeholder tactics.
- Verify in the project environment (e.g., `lake env lean <file>`) and confirm that warnings are absent. If warnings are treated as errors, the build must be clean.
- Double-check that the protected prefix is byte-for-byte unchanged and that only the allowed file was modified.

## Verification

Before finalizing:
- Run the file check in the project environment (e.g., `lake env lean path/to/file.lean`).
- Confirm:
  - No warnings or lints remain.
  - No `sorry`/`admit`/placeholders.
  - The proof uses only tactics available from the existing imports.
  - The file prefix is unmodified (compare first N lines with the original).

Success criteria:
- The target theorem is fully proven.
- The file compiles with no warnings (treated as errors).
- The exact required prefix remains unchanged.

## Common Pitfalls and How to Avoid Them

- Pitfall: Modifying the protected prefix or other files.
  - Avoidance: Work only below the allowed line; verify a diff or compare the first N lines byte-for-byte.

- Pitfall: Using tactics not provided by the project imports.
  - Avoidance: Rely on tactics explicitly imported by the file; if a tactic fails mysteriously, switch to simpler rewrites and basic arithmetic.

- Pitfall: Over-aggressive rewriting that changes term shape too early.
  - Avoidance: Align terms to match the induction hypothesis first; rewrite only what’s needed so the arithmetic tactic can finish.

- Pitfall: Type mismatches (e.g., mixing naturals with rationals).
  - Avoidance: Keep sequences and constants in the same type throughout; add explicit types if necessary.

- Pitfall: Leaving unused facts or helper lemmas that produce warnings.
  - Avoidance: Remove unused `have` statements or name them with `_` if you truly need them transiently.

- Pitfall: Forgetting to justify positivity for divisions or powers in inequality steps.
  - Avoidance: Establish nonnegativity/positivity with dedicated lemmas/tactics before applying linear arithmetic.

## Optional Script Usage

The included script can help validate that your file prefix remains unchanged.
- Create a snapshot of the original prefix if needed.
- Run the script to compare the target file against the reference file for the first N lines.
- Integrate into a pre-commit hook to prevent accidental edits to protected regions.
