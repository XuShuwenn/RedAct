---
name: lean4-induction-closed-form
description: "Finalize Lean4 proofs for recursively defined sequences by proving a closed form via induction and then deriving bounds, while respecting fixed-file-prefix and import constraints."
---

# Lean4: Closed-Form Induction for Recursive Sequences (with Bounds)

A reusable workflow to complete Lean4 proofs for recursively defined sequences by:
1) proving a closed-form formula by induction using only allowed imports/tactics, and
2) deriving the required inequality/bound from basic nonnegativity facts.

This skill emphasizes robust rewrites (powers and division), positivity proofs, and file-discipline checks under strict prefix constraints.

## When to Use

Activate this skill when:
- A sequence is defined recursively (e.g., S (n+1) = S n + term n), and you need to prove a global bound or monotonic property.
- You are not allowed to modify the imports or the file prefix (exact header/lines must stay identical).
- Division, powers, and simple rational arithmetic appear, and heavy tactics (e.g., `field_simp`) may not be available.

## Core Workflow

1) Inspect the constraints
- Do not change any lines before the specified start line. Keep all imports unchanged.
- Only edit within the permitted region.

2) Strengthen the claim to a closed form
- Prove a stronger equality by induction (simple_induction or standard induction) that expresses the partial sum in a closed form.
- Pattern:
  - Introduce a local lemma: `have h : ∀ k, S k = C - T k := by ...` or `have h (k) : S k = C - T k := by ...`.
  - Use `simple_induction` if available in the project; otherwise use `induction k with
    | zero => ...
    | succ k ih => ...`.

3) Base case
- Open the definition using `simp [S]` or `dsimp [S]` (as defined in the file).
- Close numeric equalities using the available numeric tactic (often `numbers` or `norm_num` via the project’s wrapper).

4) Inductive step (robust fraction/power rewrites)
- Start from recursion and rewrite with the IH:
  - `rw [S, IH]` (or `simp [S, IH]` if appropriate).
- Convert the new term to match the closed-form decrement. Typical tools:
  - `pow_succ`: rewrites `b^(k+1)` to `b^k * b`.
  - Division rearrangements: `div_mul_eq_div_div`, `div_div`, or `by have hpow : ... := ...; rw [← hpow]`.
- A robust approach to avoid unavailable field tactics:
  - Show an identity that connects consecutive decrement terms, e.g., prove a local lemma of the shape
    `(2 : ℚ) / 2^(k+1) = 1 / 2^k`, using:
    - `rw [pow_succ]` to expand `2^(k+1)` into `2^k * 2`.
    - `rw [div_mul_eq_div_div]` then evaluate `(2 : ℚ) / 2 = 1` using `numbers`.
  - After aligning terms via such a lemma, use basic additive rewrites (e.g., `sub_add`, `add_comm`, `add_assoc`) to reach the next closed-form statement.
  - Avoid relying on `ring` for fractions; it may not handle division. Prefer concrete rewrites and small arithmetic facts.

5) Conclude the target inequality
- After `rw [h]` (the closed-form), derive the bound using nonnegativity facts:
  - Prove `0 ≤ decrement_term` via:
    - `one_div_nonneg.mpr` together with `pow_nonneg` (e.g., `pow_nonneg` on a nonnegative base), or
    - `positivity` tactic if available.
  - Apply a simple inequality lemma such as `sub_le_self` with a nonnegative term, or use the project’s arithmetic tactic (e.g., `addarith` or `linarith`) to finish.

6) Verify
- Ensure the file type-checks without warnings (treat warnings as errors if required).
- Confirm the prefix/header remains unchanged.

## Verification Checklist

- File prefix and imports are unchanged before the allowed edit line.
- Base case closes with `simp/dsimp [S]` and a numeric tactic (`numbers`/`norm_num`).
- Inductive step uses:
  - `pow_succ` for powers,
  - a small division lemma like `div_mul_eq_div_div` to relate successive terms,
  - basic rewrites (`sub_add`, associativity/commutativity) instead of heavy tactics.
- Final inequality uses a nonnegativity proof (`one_div_nonneg` + `pow_nonneg`, or `positivity`) and a simple inequality lemma (`sub_le_self` or arithmetic tactic) to conclude.
- No extra imports introduced and no unrecognized tactics used.

## Common Pitfalls and How to Avoid Them

- Unavailable tactics (e.g., `field_simp`):
  - Replace with explicit rewrites using `pow_succ` and division lemmas.
  - Avoid cancellation requiring nonzero denominators unless strictly necessary.

- Misusing numeric tactics:
  - Do not write `numbers [S]`. Instead, first open definitions with `simp [S]` (or `dsimp [S]`), then apply `numbers`.

- Mixing term/tactic modes or bad indentation:
  - Ensure tactics follow `by` in tactic mode with proper indentation.
  - Avoid placing `simp` where Lean expects a term; structure the proof as a coherent tactic block.

- Overreliance on `ring` for rationals with division:
  - `ring` does not handle division well. Prefer elementary rewrites and small lemmas.

- Breaking the prefix constraint:
  - Never alter lines before the specified start. Keep imports exactly as given.

## Minimal Patterns (Lean snippets)

- Closed-form lemma skeleton:
  - `have h (k : ℕ) : S k = C - T k := by
      simple_induction k with k IH
      · simp [S]; numbers
      · simp [S, IH]
        -- use pow_succ, division lemmas, and small rewrites to finish
    `

- Nonnegativity to bound:
  - `have hnonneg : (0 : ℚ) ≤ T n := by
      -- one_div_nonneg.mpr (pow_nonneg ...) or positivity
    `
  - Then either `apply sub_le_self; exact hnonneg` or use an arithmetic tactic to finish.

## Success Criteria

- The proof compiles with no warnings.
- The prefix and imports remain unchanged.
- The final goal is solved via the closed-form lemma and a clean inequality step based on nonnegativity.

## Optional Script Usage

Use the helper script to:
- Compare the first N lines of the modified Lean file with a baseline file (e.g., an untouched copy) to ensure the prefix is unchanged.
- Optionally scan for disallowed tactics (e.g., `field_simp`) to prevent late failures under restricted environments.
