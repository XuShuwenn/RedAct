---
name: dna-frame2-translation
description: "Analyze DNA sequences for type (DNA/RNA/Protein), calculate GC content, translate to proteins, and find longest ORF."
---

## Task Compliance

- Treat the task instructions as authoritative for input source, tool usage, output file location, required labels/templates, and completion format.
- If the task names a file as the source of the sequence, read that file first and analyze its contents rather than relying on duplicated sequence text elsewhere.
- If the environment requires a strict tool/action syntax, file-access order, or exact completion signal, follow that exact protocol.
- Do not claim a file was written unless you actually performed the write successfully through the available interface.
- Protocol-first rule: before any biological analysis, identify the environment's required interaction format, allowed tool names/interfaces, whether you must wait for each observation before continuing, and any exact completion string.
- If the environment specifies an exact tool/action invocation schema (for example `Action:` plus JSON), use that schema verbatim for every step; do not substitute prose, XML-style tags, pseudo-tools, or alternate wrappers.
- Use only tools and invocation methods explicitly available in the environment. Do not invent helper tools, alternate write mechanisms, or unsupported interfaces.
- For file-based tasks, do not attempt any write before the required source file has been read through the mandated interface; use read/inspect -> compute -> write unless the task explicitly requires a different order.
- If the task expects analysis from a specific input file path but only provides the raw sequence inline, first place that exact sequence into the required input file through an allowed interface, then treat that file as the single source of truth for all later analysis.
- For file-output tasks, after writing the result through the approved interface, read the written file back once and confirm the observed contents match the required labels, order, units, and values before declaring completion.
- After each action, wait for and inspect the returned observation/result before asserting that a file was read, a file was written, or a computation succeeded.
- Do not state computed GC%, translation, ORF results, or output-file creation unless those results were actually produced or confirmed through the permitted tool workflow visible in the trace.
- When the environment requires an exact completion signal, output that exact token/string and nothing else instead of a conversational ending.
- For nontrivial sequence jobs, prefer a short script that reads the designated input, normalizes the sequence once, computes all requested values from that same string, and then writes the final answer in the required format.


## Task Compliance

## Execution Protocol Checks

- Before any sequence analysis, re-check the environment instructions for allowed tool name(s), required action/message syntax, required file-read/write order, whether observations must be awaited after each action, output path requirements, and the exact completion signal.
- Treat execution-format requirements as mandatory gating checks, not style suggestions.
- If the task requires file output, perform the write only through the declared interface, verify success from the observation, then finish with the exact required completion message.
- Do not mix correct biological analysis with noncompliant tool usage; the task is not complete unless both the analysis and the execution protocol are correct.

- Treat protocol compliance as a hard gate: before the first tool call, identify the exact required action wrapper/message syntax, allowed tool names, whether each action must be followed by an observation, the required read/write order, and any exact completion string.
- If the environment prescribes a literal wrapper (for example `Action:` JSON, or `Thought:` then `Action:` JSON), use that wrapper verbatim for every tool call; do not improvise prose-only actions, XML-like tags, pseudo-tools, `Write(...)`, `tool_call`, or any undeclared interface.
- In action/observation environments, follow a strict one-step loop: send one compliant action, wait for its observation, then decide the next step. Do not combine multiple unobserved steps or claim success before the observation arrives.
- For file tasks, use only the approved interface for file operations and use the observed input file contents as the only source of truth; do not compute from duplicated prompt text when a task-designated file exists.
- Preferred ordered workflow for file-based tasks: inspect/read the designated input, normalize the sequence once, compute all requested metrics from that same sequence object in one run, validate final values and labels, write the exact requested output file, confirm the write through an observation, then emit the exact completion signal if one is required.
- Treat missing observations or tool errors as blocking: do not claim GC%, translation, ORF results, file creation, or task completion unless the visible trace already shows the compliant read and observable computation/write steps you relied on.
# DNA Sequence Analysis

## When to Use

- Analyze DNA/RNA sequences for composition
- Calculate GC content percentage
- Translate DNA sequences to protein sequences
- Find open reading frames (ORFs) in DNA

- Prefer a short script when the task combines sequence classification, GC calculation, translation, and ORF scanning; this reduces transcription errors and keeps all reported values consistent.
- Reliable combined-task workflow: normalize once, classify from the observed alphabet, compute `G/C/length` and GC% from that same normalized string, then perform DNA-specific frame translation and ORF scanning only if classification is DNA.
- Preserve the distinction between tasks: fixed-frame translation means translate every full codon in the requested frame, while longest-ORF analysis means compare only complete in-frame `ATG ... stop` segments.
- Keep all derived outputs tied to the same normalized sequence object in one workflow or script so classification, GC%, translation, and ORF results cannot drift apart.

- If the sequence is provided in or must be read from a file, verify the required input path first and use that file's contents as the single source of truth for all later calculations.
- For file-based tasks, read any exact output-template requirements before computing so labels, order, and units can be written correctly in one pass.

- At the start of a multi-part task, enumerate the exact required deliverables (for example: sequence type, GC%, frame-2 translation, longest ORF, output file path, required labels) before computing anything; use that checklist to drive both computation and final formatting.
- For filesystem-based tasks, inspect the relevant directories and identify the true input file, any required template, and the exact output path before computing.
- Proven workflow for file-based or graded multi-output tasks: read the designated input once, normalize one shared sequence, compute all requested metrics in one script/run from that same sequence object, treat that single computation output as the authoritative source for the final response or file, then write the complete labeled output in one pass.
- After a trusted script or terminal run returns sequence type, GC%, frame-2 translation, and ORF length, propagate those exact returned values into the final artifact; do not manually re-derive or "correct" one field unless you rerun the full computation from the normalized sequence.

## Key Calculations

### Required Pre-Analysis Validation
- Create one normalized sequence first: remove whitespace/newlines and uppercase it. Use that exact string for every later step.
- Before any translation or ORF work, verify and record: `length = len(seq)`, `g_count = seq.count('G')`, `c_count = seq.count('C')`, and `gc_percent = (g_count + c_count) / length * 100`.
- Do not mix counts, codons, or positions derived from different copies or segments of the sequence.
- If any downstream codon list or ORF positions imply a different sequence length than the validated `length`, recompute from the normalized sequence before answering.

- Use one reproducible pass (preferably a short script) to produce the normalized sequence and its core stats once: `seq`, `length`, `g_count`, `c_count`, and any frame codon lists. Reuse those exact values everywhere.
- Good default for multi-part tasks: one short script computes classification, GC%, frame-2 translation, and longest-ORF candidates from the same normalized `seq`, then a brief second check validates only the most convention-sensitive result before final output.
- If you discover a bug in translation, ORF logic, or classification, rerun the full analysis from the normalized input and regenerate the final response/output file; do not hand-patch only one reported field.
- If any later manual codon list, GC denominator, peptide length, position claim, or ORF span disagrees with the validated `length` or normalized sequence, discard the later result and recompute from `seq` before answering.


### Sequence Type Detection
- DNA: contains T (thymine)
- RNA: contains U (uracil) but no T
- Protein: contains letters beyond A, C, G, T, U
- Fast alphabet check: if all characters are in `{A,C,G,T}`, classify as DNA; if all are in `{A,C,G,U}` and no `T` appears, classify as RNA; if letters beyond the nucleotide alphabet are present, treat as Protein or invalid/mixed according to the observed characters.
- Do not label a sequence as Protein merely because it lacks both `T` and `U`; a sequence composed only of nucleotide letters (for example only `A/C/G`) is still nucleic acid and should be resolved with the DNA/RNA rules above.

- Classify from the normalized sequence before any GC, translation, or ORF work.
- If both `T` and `U` appear in the same sequence, treat it as invalid/mixed rather than forcing a DNA/RNA label.
- If the sequence contains characters outside the expected DNA/RNA/protein alphabets, do not force DNA translation/ORF rules without clarifying or noting the inconsistency.
- Only apply the DNA frame-2 translation and DNA ORF rules after confirming the input is DNA.
- Use sequence type as a gate for downstream analysis: do not run DNA frame-2 translation or DNA ORF scanning on RNA, protein, or mixed/invalid input unless the task explicitly instructs a conversion or override.
- Make the sequence-type decision before building codon lists so translation and ORF logic use the correct molecule assumptions.

### GC Content
- GC% = (G + C) / total_bases × 100
- Round to 1 decimal place
- Compute counts and denominator from the full normalized input sequence (uppercase, with whitespace removed).
- Verify counts from that same normalized sequence before reporting: compute `length = len(seq)` and count `G` and `C` directly.
- Prefer one reproducible counting step over manual inspection, e.g. `g = seq.count('G')`, `c = seq.count('C')`, `length = len(seq)`, then `gc_pct = (g + c) / length * 100`.
- Use the full validated nucleotide length as the denominator, and ensure any cited counts are consistent with the reported GC%.
- If you mention sequence length, report `len(seq)` from the normalized full sequence; do not reuse a guessed, hand-estimated, or partial length.
- Before any downstream analysis, sanity-check that `G + C <= length` and that codon grouping is based on that same validated sequence.

### Translation (Frame 2)
- Codons are read starting from position 2 (0-indexed)
- Start codon: ATG
- Stop codons: TAA, TAG, TGA (use * for stop)
- In this skill, `frame 2` means start offset `1` (the second nucleotide; position 2 in 1-based numbering).
- Convert the requested frame number to an explicit offset before translating: for frame 2, use offset `1` and iterate codons in steps of 3 from `seq[1:]`.
- Do NOT mix conventions in the same task. Use one normalized statement: `frame 2 = offset 1 = start at the second nucleotide`.
- Quick check: the first frame-2 codon must be `seq[1:4]`; if you start with `seq[2:5]`, you are using the wrong frame.
- Build the frame-2 codon list explicitly from `seq[1:]`, grouping successive triplets from that offset.
- Reliable implementation pattern: set `frame_seq = seq[1:]`, then iterate in 3-base steps over that frame sequence (or equivalently over indices `1, 4, 7, ...`) so the frame-2 offset stays unambiguous throughout analysis.
- Translate the entire remaining frame to the end; do not stop at the first stop codon unless the task explicitly asks for an ORF or peptide-until-stop.
- Do NOT answer a frame-translation request with only the first ORF. Continue translating all full codons in `seq[1:]`, writing `*` wherever an in-frame stop occurs.
- Distinguish the tasks explicitly: `translate frame 2` = translate every full codon from offset 1 to the end of `seq[1:]`; `find ORF` = start-to-stop analysis. Do not switch to ORF logic inside a frame-translation answer.
- Before reporting the peptide, confirm the explicit frame-2 codon list was built from the full normalized sequence `seq[1:]`, not from a truncated, miscopied, or separately reformatted substring.
- Quick check: for normalized `seq`, frame-2 peptide length must equal `len(seq[1:]) // 3`.
- Map each in-frame stop codon to `*` and ignore any trailing 1–2 bases that do not form a full codon.
- Cross-check that the final peptide length equals the number of full frame-2 codons and that no amino acids were inserted or omitted.
- If you write or reason about the codon list, the reported peptide must match it exactly codon-by-codon; do a final one-to-one pass to catch duplicated, skipped, or shifted amino acids.
- Do NOT report a peptide that differs from your own listed codons. Example: `... TGT(C) TCG(S) TAG(*) ...` must yield `...CS*...`, not `...CCS*...`.

- If translating by script, use a complete codon table before trusting the peptide; if any codon in the explicit frame-2 list is unmapped, fix the table or inspect that codon before finalizing output.

- Before finalizing a frame-2 translation, inspect the explicit frame-2 codon list and confirm the peptide matches it codon-by-codon; use this as the primary check for frame-offset mistakes.

### Longest ORF
- Scan all three reading frames codon-by-codon.
- Proven ORF workflow: complete the scan for frames 0, 1, and 2 before choosing a winner; do not assume the requested translation frame is also the longest-ORF frame.
- Build explicit codon lists for frame 0 (`seq[0:]`), frame 1 (`seq[1:]`), and frame 2 (`seq[2:]`) before searching for ORFs.
- Evaluate ORFs only from codon-aligned `ATG` starts within each frame's codon list; do not use nucleotide positions that are off that frame boundary.
- In each frame, consider only starts and stops that lie on that frame's codon boundaries.
- For each `ATG` start, find the first in-frame stop codon (`TAA`, `TAG`, or `TGA`) that closes it.
- Use a complete candidate-table workflow: in each frame, examine every in-frame `ATG`, pair it with its first later in-frame stop if present, record that complete start->stop segment, and compare all complete candidates across frames.
- Reject any ORF start/stop claim whose nucleotide index is not on the claimed frame boundary before comparing ORF lengths.
- Count as candidates only complete in-frame start->stop segments; exclude starts that run to sequence end without an in-frame stop.
- Compute ORF length in bp from start codon through stop codon inclusive.
- Compare all complete start→stop segments and report the maximum validated ORF length in bp.
- Enumerate candidates systematically: for each frame, list every in-frame `ATG`, extend each one to the first in-frame stop, keep only complete start→stop ORFs, then compare all candidate lengths.
- Ignore incomplete start-without-stop segments when choosing the longest ORF, but do not let their presence replace or invalidate separate complete ORFs found elsewhere.
- Do not report a longest ORF from a partial scan or a single observed candidate.
- If no complete ORF exists in any frame, say so explicitly.
- Use an explicit codon-by-codon scan for each frame before choosing the longest ORF; do not infer ORFs from raw substring matches that are off-frame.
- Record each candidate as `frame, start_codon_index, stop_codon_index, bp_length`, then compare only complete in-frame start→stop segments.
- Keep indexing consistent within one convention for the whole analysis; if giving positions, ensure the stated span matches the reported bp length exactly.

- Validate frame indexing explicitly: for frame offsets 0, 1, and 2, every codon start index considered in that frame must satisfy `index % 3 == offset`.
- Before reporting the longest ORF, re-extract the nucleotide segment from the claimed start through stop and confirm its codonization matches the reported ORF exactly (`ATG` at start, stop codon at end, all on the same frame).
- When reporting an ORF, verify the stated start codon, intervening codons, and stop codon are a single contiguous in-frame triplet sequence from the original normalized DNA.
- Sanity check every ORF claim with: `orf_bp = 3 × number_of_codons_including_start_and_stop`; if that does not match, the ORF is wrong.
- For longest ORF scanning within a frame, if multiple `ATG` codons appear before the next in-frame stop, evaluate all valid start→stop segments closed by that stop and keep the maximum length.

- For tasks that ask for sequence type, GC%, frame-2 translation, and longest ORF together, compute them in one pass from the same normalized sequence and keep the intermediate values together until final output.
- During longest-ORF analysis, track both the winning ORF length and the frame where it was found, even if the final output only requires the length; use the stored frame as a validation aid before answering.

## Output Format

```
Sequence type: {DNA|RNA|Protein}
GC content: XX.X%
Frame 2 translation: X...
Longest ORF length: N bp
```

- If the task requires writing to a file or using an exact template, preserve labels, line order, units, and rounding exactly as specified.
- Compute all requested values first, then write the final response/output file in one pass to avoid partial or inconsistent results.

- For graded or file-writing tasks, copy the required labels, line order, units, and rounding exactly from the spec before writing.
- If an input/output path is provided, read the source file before computing and write the final output only after all values have been validated against the normalized sequence.
- Generate the final response or file directly from the computed variables rather than hand-copying intermediate values.

- Before writing, compare the final output against the task's required deliverables checklist and confirm every requested field appears exactly once with the required label, order, units, and formatting.
- Build the final answer directly from validated computed variables, then emit or write the exact requested labeled summary once without paraphrasing, reordering labels, or omitting required lines.
- If a destination path is specified, write the completed labeled results directly to that exact path rather than leaving the answer only in the chat.
- If any core computation changes after validation, rewrite the entire final response/output file from the recomputed variables so every reported field comes from the same corrected run.
- After writing a required output file, read it back or otherwise confirm its contents through the approved interface before declaring completion.
## Final Checks

- Normalize the sequence once before any counting or frame analysis.
- Recompute the frame-2 codon list before writing the answer.
- If reporting a translation, ensure it matches the codon list exactly, one amino acid per full codon, with `*` for stop codons.
- If reporting an ORF length, confirm: start codon present, stop codon present, same frame, and length = number_of_codons × 3 bp.
- Ensure any position-, count-, or length-based claim matches the source sequence exactly before output.

- Prefer a small validation script for nontrivial inputs: normalize the sequence, classify type, compute GC%, translate frame 2, and scan ORFs from the same sequence object to reduce manual transcription errors.
- For multi-part tasks, prefer one short script that emits or verifies the same checkpoints from one run: normalized sequence, `len(seq)`, `G`, `C`, frame-2 codons/peptide from `seq[1:]`, and complete ORF candidates from frames `0/1/2`.
- In that validation pass, confirm sequence type before translation/ORF work: DNA if `T` is present and `U` is absent, RNA if `U` is present and `T` is absent, invalid if both appear, and Protein only if non-nucleotide letters are present.
- For sequence type, check characters explicitly: if `T` is present and `U` is absent, classify as DNA; if `U` is present and `T` is absent, classify as RNA; if letters beyond the nucleotide alphabet are present, classify as Protein.
- Confirm the reported nucleotide length matches the fully normalized sequence exactly before computing GC%, codons, or ORF positions.
- Recalculate GC% from the validated `G`, `C`, and total length values if there is any mismatch.
- For translation tasks, compare the final peptide against the explicit frame-2 codon list one last time, character by character if needed.
- If reporting a translation, ensure its peptide length equals `len(seq[1:]) // 3`.
- If a translation looks suspicious, verify every codon in the analyzed frame has a valid mapping before reporting the peptide.
- For ORF tasks, verify every reported ORF claim is backed by the frame scan and that start, stop, frame, and bp length are mutually consistent.
- Re-scan the source sequence from the normalized string and confirm every reported start/stop position lands on the claimed frame boundary.
- If citing an ORF as longest, ensure all three frames were checked and that the winning ORF came from an explicit candidate list.
- Before finalizing longest ORF, match the reported ORF length to an explicit codon list for that ORF; if you cannot write the codons in order, do not report it.
- Do not finalize from prose reasoning alone; perform one explicit codon-boundary validation pass for any reported translation or ORF result.

- Confirm you used the task-designated input source; if a file path was specified, re-read that file rather than trusting prompt duplication.
- Before final output, verify one shared source of truth: reported GC%, frame-2 peptide, and longest ORF must all trace back to the same normalized sequence and validated length.
- Before writing the final answer, do one full-sequence verification pass from the normalized input: recompute `len(seq)`, `g = seq.count('G')`, `c = seq.count('C')`, `gc_pct`, the complete frame-2 codon list from `seq[1:]`, and the ORF candidates from the same sequence object.
- If the task asks for both frame translation and longest ORF, keep them separate in the final check: translation = all full codons in frame 2 with `*` for any in-frame stops; ORF = start-to-stop segments only.
- After writing any intermediate codon parsing, compare it directly to the final reported peptide with a one-to-one codon->amino-acid pass; if the codons imply `...C S *...`, do not output `...C C S *...`.
- Before reporting ORF positions, re-derive them from the normalized sequence using one indexing convention end-to-end and confirm `bp_length = stop_nt_inclusive - start_nt + 1 = 3 * codon_count`.
- If reporting the longest ORF, verify the winning candidate by re-extracting its exact nucleotide span from the normalized sequence and confirming `ATG ... stop` on one contiguous frame boundary before output.
- If using a script, compute all requested values from the same normalized sequence variable and write the final output only after those values have been validated; do not mix script-derived values with hand-corrected counts unless you rerun the full check from the normalized input.
- If using a script for translation or ORFs, read back the exact reported peptide and ORF length from that run before finalizing; do not re-derive them manually from memory.
- For file tasks, use a two-stage workflow: verify/read the required input first, compute and validate all results, then write the exact requested output path and format in one pass.
- Confirm the execution method, required labels/templates, output file contents, and final completion message exactly match any task-specific protocol before finishing.

- Before the first tool call, confirm the required execution protocol: exact tool/action syntax, allowed tool names, required read/write order, output path, and exact completion signal.
- Ensure the visible workflow is evidence-first and in order: input read/inspection -> computation/validation -> output write. Do not skip directly to final biological results.
- Before any write or final answer, verify that every file read/write or computation you rely on was confirmed by an actual observation/result from the approved interface.
- If the visible trajectory does not yet show the required read/compute/write steps, do not assert final biological results; perform the missing compliant actions first.
- If the task requires a literal completion marker, send exactly that marker with no added explanation.

- Evidence-before-results check: before asserting sequence type, GC%, translation, ORF length, file creation, or task completion, confirm the visible trajectory contains the compliant input read plus the computation/validation and write steps you relied on.
- Final consistency check for combined tasks: confirm sequence type, GC%, frame-2 peptide, and longest-ORF result all came from the same normalized input string and the same validated run or script output before writing.
- If a script/tool run already returned the required fields, read back those exact values from the observation and use them directly in the final answer or output file.
- Do one pre-write completeness check: verify that each requested deliverable identified at the start of the task has a computed value and is present in the final response/file.
- Do one targeted re-check of frame-2 translation immediately before finalizing: confirm the codons come from `seq[1:]`, the peptide length is `len(seq[1:]) // 3`, and the reported amino-acid string matches those codons exactly.
- Before finalizing longest ORF, confirm the winning candidate came from an explicit per-frame scan, and retain the winning frame internally so the reported length can be checked against the correct frame-specific codon scan before output.
- If you wrote an output file, reopen that exact path and confirm the visible contents match the requested structure, line order, labels, units, and computed values before finishing; do not rely on a successful write call alone.
- Before claiming success, confirm each tool invocation used the declared interface/tool name, each required read/compute/write step was followed by its observation before continuing, and the final message is the exact required completion marker when one is specified.
- Do NOT substitute conversational text like `Done`, `Finished`, or a prose summary for a required literal completion token.
## Tips

- Use string methods to count G and C
- Handle mixed case input (uppercase it)

- For translation and ORF tasks, write out codons for each relevant frame first, then derive the peptide or ORF length from that codon list.
- Keep translation and ORF analysis separate: translation reports the whole requested frame, while longest ORF uses start→stop logic.
- Reuse the same codonization primitives for both tasks, but keep outputs distinct: frame-2 translation covers all full codons in offset `1`, while ORF scanning checks all three frames for complete start→stop segments only.
- Before finalizing, verify the reported frame-2 peptide and longest ORF are both supported by an explicit frame scan.

- In code, represent reading frames as offsets `0`, `1`, and `2`; for frame 2 translation, iterate codons from offset `1` explicitly.
