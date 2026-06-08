---
name: lean4-proof
description: "Complete Lean 4 mathematical proofs for sequences and convergence, ensuring type checking passes."
---

# Lean 4 Proof Completion

## When to Use

- Complete mathematical proofs in Lean 4
- Prove properties about sequences and series
- Ensure type-safe, warning-free proofs

## Input

- `/app/workspace/solution.lean`: Template with imports, definition, theorem

- Treat `/app/workspace/solution.lean` as the deliverable: make final edits there, not only in a scratch file.
- If you test ideas elsewhere, copy the working proof back into `solution.lean` and validate `solution.lean` itself before finishing.

## Problem

Given sequence S_n:
- S_0 = 1
- S_{n+1} = S_n + 1/2^{n+1}
- S_n = Σ_{i=0}^n 1/2^i

Prove: S_n ≤ 2 for all n ∈ ℕ

## Constraints

- Do NOT modify anything before line 15
- Do NOT change any other files
- Must type-check with no warnings
- Start proof from line 15

- Preserve the file prefix exactly when told not to modify earlier lines; edit only the permitted region starting from line 15.
- Edit only `/app/workspace/solution.lean`; do NOT create temporary `.lean` files, modify other files, or change project layout to make Lean build.
- If the proof becomes malformed or truncated, re-open the current theorem/proof region and replace the entire proof body in one coherent edit; do NOT keep patching small fragments.
- Treat obvious proof corruption as a reset condition: if the theorem body is truncated, duplicated, or parser-broken, print/re-read the whole theorem region with line numbers and reconstruct it from a clean full-body replacement.
- Do NOT use repeated short substring replacements inside a broken proof script; they are brittle and can corrupt the file.
- If `lean` reports parser/type errors inside `solution.lean`, fix those proof/script errors first; do NOT diagnose them as environment issues until the file itself parses.
- Do not stop with any remaining Lean errors such as unsolved goals, rewrite failures, `no goals to be solved`, leftover `sorry`, or a proof that exists only outside `solution.lean`.
- Before completion, run a check/build that confirms `/app/workspace/solution.lean` type-checks with no warnings.


## Constraints

## Required Workflow

- Before editing, inspect `/app/workspace/solution.lean` and identify the exact theorem statement and current proof text from line 15 onward.
- Preserve protected lines by editing only the permitted region after line 15; do not replace the whole file when a prefix-preservation constraint is in force.
- After opening `solution.lean`, inspect its imports and any referenced local tactic files/modules early; custom tactics or helper lemmas in the workspace may indicate the intended proof style.
- Before the first substantive edit, run one type-check on the unedited `solution.lean` to establish a baseline, then re-open the theorem region so you are debugging the exact current file text rather than a remembered draft.
- After every substantive edit, re-open the edited proof block in `solution.lean` before the next diagnosis or compile; do not reason from an assumed proof script.

- After any broad replacement or whole-body rewrite, immediately read back the exact edited theorem text from `solution.lean` before running Lean again; confirm concrete Lean code was written, not placeholders, truncation, or a partially replaced proof.
- Do NOT use vague replacement payloads such as "the completed proof", "proof here", or theorem-stub placeholders. Every write to `solution.lean` must insert explicit Lean source that you have inspected afterward.
- After any write, replacement, or relocation involving `/app/workspace/solution.lean`, immediately re-open that exact file and inspect the edited theorem region before any further diagnosis or validation. If the file contents differ from what you intended, fix the file first and only then continue.
- Read the recursive definition of the target sequence/function before choosing a proof plan; for statements over `ℕ` about a recursively defined object, default to induction on that same argument unless the theorem statement clearly forces another structure.
- Follow the environment's required action/tool protocol exactly. Do not improvise alternate tool-call syntaxes or completion signals; task-specific interface requirements are part of correctness.
- Treat any externally specified interaction schema as a hard constraint with highest priority. If the environment specifies a strict tool-call schema such as `Thought:` plus `Action:` with JSON, use that exact wrapper and field syntax for every tool invocation.
- Do NOT substitute XML-style tags, markdown code blocks, pseudo-Python calls, unsupported call names like `Read`/`Edit`/`Bash`, or free-form prose commands when a specific action format is required.
- Before the first tool call and again before the final response, re-check the required call/response format from the task instructions.
- If the environment requires an exact final string such as `ACTION: TASK_COMPLETE`, output that exact string and nothing else after all required checks pass.

- Establish a baseline by checking the unedited file once; after each substantive edit, re-open the changed proof block and check again.
- When Lean reports an error, read the exact source line and current goal/error message before changing tactics or strategy; do not debug by speculation.
- If `solution.lean` has parser errors or local type errors, fix those in the file first; do NOT treat them as project/build-layout issues and do NOT create, move, or touch other files.
- If two local proof edits in a row fail, stop patching fragments. Re-open the full theorem/proof from `solution.lean`, restore a coherent proof body, and replace the whole body in one edit before testing again.
- If repeated `rw`/`calc`/normalization attempts hit the same kind of failure, stop that proof path and switch to a structurally simpler one, usually direct induction or a stronger local statement aligned with the recurrence.

- If repeated checks return the same concrete arithmetic equalities about `/`, inverses, or powers, abandon that algebraic path quickly. Prefer an induction invariant whose successor step uses the recurrence and monotonicity/order facts you can already close, rather than a closed form that requires delicate denominator manipulation.
- When a rewrite such as `rw [ih]` fails, compare the displayed goal to the lemma or hypothesis literally. First reshape the goal (`simp`, `norm_num`, `change`, or a different induction variable/form) so the expressions match; do not keep trying nearby rewrites blindly.
- Build proofs in two phases: first establish the structural step (base case / inductive step / unfolding of the recursive definition), then solve the resulting concrete arithmetic or order subgoals with the simplest available lemmas or local tactics.
- When Lean exposes a simple subgoal, close that exact goal with the simplest available lemma or tactic instead of introducing stronger equalities or heavier algebra.
- If planning to use a tactic or lemma that is not obviously guaranteed by the existing imports, verify it first before building the proof around it. This includes algebraic or arithmetic tactics such as `ring`, `linarith`, `norm_num`, `positivity`, `field_simp`, or similar tools.

- Do NOT restructure the proof around a guessed tactic name or syntax. If Lean has not yet accepted that tactic in the current file, treat it as unavailable and use a verified simpler path instead.
- Verify planned tactics with a minimal check before committing the proof structure to them. If Lean reports `unknown tactic`, rejects the tactic shape, or `simp` does not apply to the actual goal, immediately rewrite the proof using already verified primitives; do NOT keep extending the same tactic-dependent path.
- If direct induction on the target inequality stalls, do not keep patching the same weak statement; switch to a stronger recurrence-compatible statement and prove that instead. For this sequence, a local closed form such as `S n = 2 - 1 / (2 : ℚ)^n` or a slack-term bound can make the final inequality immediate.
- Under file-prefix restrictions, keep helper lemmas, local inductions, and alternative proof attempts inside the allowed theorem body of `solution.lean` using `have`, `suffices`, or a local `let`; do not add top-level declarations above protected lines or move the proof into scratch files.

- When the task restricts edits to `solution.lean`, do all substantive proof work there. Do NOT iterate in `test.lean` or another scratch `.lean` file and assume you will copy back later; if you briefly verify an idea elsewhere, immediately transfer the working proof into `solution.lean` and re-check `solution.lean` itself before continuing.
- Type-check in the project environment first when imports or tactics may depend on local packages: prefer `lake env lean /app/workspace/solution.lean`; use `lake env lean -q /app/workspace/solution.lean` if a project-wide build fails for unrelated reasons, and use `lake build` as an additional full-project check when appropriate.

- Never treat partial, silent, or ambiguous output as a successful check. A verification step counts only if the command explicitly finishes without errors for `/app/workspace/solution.lean`; if output is truncated, empty, interrupted, or only shows partial build progress, rerun a concrete check command.
- Do NOT respond to Lean import/build/path errors by creating directories, moving files, renaming the deliverable, or changing project structure when the task says to edit only `solution.lean`. Keep the deliverable at `/app/workspace/solution.lean` and prefer direct checking of that file in the existing project environment.

- Treat task-specific interaction requirements as part of correctness: if the environment specifies an exact tool-call schema or exact completion string, follow it literally.
- Before the final response, verify all acceptance conditions in the final filesystem state: only the allowed file was edited, protected lines are unchanged, the completed proof is in `/app/workspace/solution.lean`, that exact file type-checks cleanly, any required tool-call schema was followed throughout, and the required completion token is emitted exactly when specified.

- As soon as the final required check succeeds and the file contents are confirmed, stop. Do not do optional cleanup, extra experiments, file deletions, or prose explanation after success when a strict completion signal is required.
- Immediately before finishing, re-open `/app/workspace/solution.lean` and confirm the file itself contains the full final proof body you intend to submit; do not rely on a proof written only in chat or memory.

- If the file view is truncated, incomplete, or ellipsized, re-read the relevant region or whole file until you have the full final artifact in view. Do NOT present or quote a proof script that was not the last fully observed file contents.
- If the current file is partial, malformed, or differs from your intended final proof, write the complete proof into `solution.lean`, then type-check that exact file again before responding.
- Never create scratch `.lean` files when the task restricts edits to `solution.lean`; use only non-modifying inspection commands outside the permitted file.
- When earlier lines are protected or an exact prefix is required, verify structure separately from type-checking: inspect the file contents/line numbers and confirm the untouched prefix, including blank lines or spacing, is unchanged and the proof starts in the allowed region.
## Tips

- Start with induction on `n` when it matches the recursive definition.
- If the inductive hypothesis is too weak for the successor step, switch quickly to a stronger recurrence-compatible statement instead of forcing more rewrites on `S n ≤ 2`. For this sequence, a local closed form such as `S n = 2 - 1 / (2 : ℚ)^n` is often the cleanest route; in some proofs, a slack-term inequality can work better.

- Do NOT default to the closed form if it leads to reciprocal-power or division identities that are not closing immediately. In that situation, pivot to a simpler inequality-based invariant whose base case and step can be checked with lightweight arithmetic already confirmed to work.
- Known: geometric series sum = 2 - 1/2^n.
- In arithmetic over `ℚ`, annotate key numerals and powers explicitly, for example `(2 : ℚ)^n` and `1 / (2 : ℚ)^n`, to avoid coercion and rewrite failures.
- Use `sorry` only temporarily; remove every `sorry` before finishing.
- Prefer `lake env lean /app/workspace/solution.lean` for validation; use `lake env lean -q /app/workspace/solution.lean` or `lake build` if needed.

- Let Lean's displayed goal shape drive each `rw`, `simp`, or tactic step: only rewrite when the target exactly matches the lemma or hypothesis form.

- In induction proofs, normalize successor/index syntax before rewriting: simplify forms like `S (k + 0)`, `S (Nat.succ k)`, or powers/divisions into the exact shape needed by the lemma/hypothesis, then apply `rw`.
- If two rewrite attempts fail on shape mismatch, stop repeating nearby rewrites; first run a simplification or goal-shaping step and re-check the displayed goal.
- If `rw`, `simp`, `calc`, or normalization attempts fail, inspect the exact current goal and the exact source line before changing tactics; do not speculate about equivalent algebraic forms without matching them to Lean's reported state.

- If the same rewrite, normalization, or tactic pattern fails twice on essentially the same arithmetic shape, stop that line of attack. First confirm the tactic or lemma is actually available in the current imports and types; then switch to a simpler invariant or prove a small helper equality whose two sides match Lean's normal form exactly.
- Before using a lemma or tactic, verify both scope and type compatibility from the current goal. Do NOT call tactics or rewrites speculatively when the goal still has the wrong type or shape.
- Prefer the proof shape that matches the recurrence. Start from the theorem goal when it stays simple, but if the recurrence does not support direct inequality induction cleanly, strengthen the claim to a closed form or sharper invariant inside the theorem and derive the bound from positivity/nonnegativity.
- When Lean shows a simple remaining goal, close that exact goal with the simplest arithmetic/order lemma or tactic rather than introducing heavier algebra.
- Avoid proof plans that depend on unverified tactics such as `field_simp` or `ring`; if they are unavailable, use simpler rewrites and lemmas already confirmed in the file context.
- After any failed sequence of edits, re-open the current file contents before making further changes.
- Final step: run `lake build`, `lean --check`, or a direct `lean /app/workspace/solution.lean` check after the last edit and finish only after an explicit clean success.

- For recursively defined sequence proofs, use the recursion in the exact successor shape needed by the induction step, such as `S (k + 1) = S k + ...`, instead of relying on brittle rewrites against the definition.
- Before using arithmetic automation such as `ring`, `norm_num`, or `linarith`, normalize expressions into a compatible form with targeted rewrites like `pow_succ`, `div_eq_mul_inv`, or `div_div`; do not expect automation to bridge mismatched forms on its own.
- For terms like `1 / (2 : ℚ)^(n+1)`, introduce a small helper rewrite if needed so denominator shifts are explicit before the main `calc` chain.
- After rewriting the sequence into a form like `2 - t`, prove `0 ≤ t` first and finish the upper bound with a simple order lemma rather than continuing to unfold the recursion.
- Match tactics to the goal shape: use `simp` and lightweight numeric closure for base cases, algebraic normalization for identities, and linear arithmetic only after the goal is in a compatible form.
- If the file imports custom arithmetic or induction tactic modules, prefer those verified local tools over inventing a heavier manual algebra proof.
- Once the goal is reduced to a numeric or ordered-field fact, use the lightest arithmetic finish that fits, such as `norm_num` after `simp` for rational base cases.
- After the proof type-checks, do a cleanup pass for warnings and re-run the final check so the submitted file is warning-free, not merely error-free.


## Finalization Checklist

## Finalization Checklist

- Re-read `/app/workspace/solution.lean` and confirm the theorem proof is complete with no truncated lines or leftover `sorry`.
- Type-check the actual edited `solution.lean` in its required path.
- Make sure the final Lean code in the file matches what you intend to submit.
- If the environment specifies an exact completion token or format, output it verbatim and do not replace it with a prose summary.