---
name: court-form-filling
description: "Fill PDF forms with case information for legal filing, handling dates, addresses, and structured text fields."
---

# Court Form Filling

## When to Use

- Fill PDF forms with case/similar information
- Handle legal documents requiring specific field mapping
- Process dates in standard formats (YYYY-MM-DD)
- Extract and format personal information (names, addresses, phone numbers)

## Workflow

0. Before any substantive work, identify and follow any task-specific execution protocol exactly (for example, required tool/action syntax, wrapper format, helper invocation style, JSON/schema shape, response format, or exact completion token); if specified, use it for the entire run and final handoff.

1. Determine whether the PDF contains native fillable/AcroForm fields before choosing a method; if it does, prefer structured field extraction/filling over visual overlay or manual annotation approaches.
2. Read the blank PDF form to understand field structure.
3. Extract or inspect the complete form field list/schema first and use it as the source of truth for field IDs/names, control types, pages, rectangles, and export values when available; review relevant rendered pages or page images alongside that metadata so each target field is tied to the visible question/section before mapping values. Treat full field metadata plus page renderings as the default identification method. If any dump, preview, render, OCR, or command output is blank, partial, truncated, contradictory, or unclear, switch to another inspection method and do not map from incomplete schema visibility, field IDs alone, or guessed names.
4. If the task or skill folder provides PDF/form-processing scripts, use those prescribed scripts first to confirm fillability, export field metadata, and drive the fill workflow; inspect any helper script or mapping-file schema and match its exact expected structure before generating JSON or other transform input, preserving all required metadata keys (for example page/field identifiers), not just field names and values.
5. Parse case description to extract key information.
6. Build a complete traceable mapping for every datum you intend to fill: form evidence -> confirmed PDF field name/ID -> control type -> case fact -> value. Search the full extracted inventory for each target, inspect the specific metadata entry or visible form evidence for every field you intend to fill, use layout only to confirm semantics rather than invent targets, and do not proceed on partial field identification, partial dumps, or guessed IDs.
6. For checkboxes, radio buttons, yes/no controls, selects, and conditional sections, confirm the exact question semantics and valid export values before setting anything; distinguish the main answer control from any follow-up explanation field, do not answer a different question than the one shown on the form, and fill only the fields for the branch actually selected.
7. If a target field is ambiguous, unconfirmed, unsupported, or merely optional, leave it blank until resolved rather than guessing
8. Prefer creating a dedicated intermediate field-values mapping file (for example, JSON) before the final fill step; use it as a reviewable, reproducible artifact. Write it using a method that avoids shell-quoting corruption, then open and inspect the actual key-value contents, confirm it parses and preserves the required schema, verify every populated entry matches the approved mapping, includes every required metadata field, and contains only intended confirmed fields before using it.
8a. Keep the mapping minimal: include only confirmed required/supported fields from the case description, and omit or leave blank optional, court-filled, signature, or otherwise unsupported fields unless the case description explicitly supports them and the form evidence confirms the target field.
9. Fill the PDF form with the verified mapping while preserving the original AcroForm/form metadata; first establish one end-to-end method that produces a readable filled PDF with intact form structure, and if the method removes fields, breaks form structure, makes the output unreadable, or repeatedly produces library/object-manipulation errors, stop retrying small variations and switch to a clearly different approach.
9a. Compare the fill tool's reported updates with your intended mapping; if any required or high-risk field is missing from the confirmation output, treat the fill as incomplete and re-inspect before proceeding.
10. Save the filled form to the requested output path and keep that exact path consistent in commands and final reporting.
11. Re-open the saved PDF and verify the filled output itself: preferably render the completed document to page images and confirm both populated fields and intentionally blank areas, then extract/read back fields as needed to verify every populated required/high-risk field was actually written correctly against the full intended mapping. Do not treat file existence, file size, command success, or a small sample as verification.
12. When one verification method returns empty, unreadable, contradictory, truncated, or partial results, do not finalize; use a different inspection method, and for PDFs with native form fields prefer programmatic read-back of saved field values as an additional verification step rather than relying only on OCR, console output, or spot checks.
13. Keep intermediate field maps, generated JSON, extracted metadata, screenshots, and other verification artifacts until this output check passes.
14. After any post-fill change to mappings, transformed values, checkbox/radio selections, or helper inputs, rerun verification on the updated output before claiming completion.

15. Before the final response, check whether the task specifies an exact completion token, final response string, or output protocol; if so, emit that required text exactly and do not replace it with a narrative summary.

## Important Notes

- Use date format: xxxx-xx-xx (e.g., 2026-01-19)
- Only fill fields mentioned in case description
- Leave court-filled and optional fields empty
- Default to leaving court-filled, venue/caption, signature, and any other unspecified or unsupported fields blank unless the case description explicitly supports them and the form evidence confirms the target field

- Verify output PDF is readable before finishing

- Do not infer or invent field names, page IDs, checkbox identifiers, or field meanings from partial dumps, naming patterns, expected labels, or layout alone; verify against the full field list, metadata, or visible form evidence before filling
- Treat checkbox/radio fields and court/venue or conditional-caption fields as high-risk; fill them only when the form evidence and case facts clearly support the selection
- Do not add legal classifications, dates, narratives, or explanatory text not supported by the case description
- If mapping evidence is incomplete or uncertain, fill only confirmed fields and leave uncertain fields empty
- Do not treat file existence, file size, script success, or a small spot-check as proof the form was filled correctly; verification must check the filled PDF itself and all populated required/high-risk fields
- If rendering, field extraction, OCR, or another verification method returns empty, unreadable, contradictory, or partial output, treat verification as failed and use another inspection method
- If filling removes `/AcroForm`, causes unreadable-object errors, or makes field enumeration disappear, discard that method and switch to a different approach
- Do not delete field maps, extracted metadata, screenshots, or other intermediate evidence until verification is complete, unless cleanup was explicitly requested
- Follow any task-specific action/response protocol exactly if one is provided
- Treat an empty image read, blank preview, missing OCR text, failed post-fill field extraction, or other unusable verification output as no evidence; verify with another method before summarizing field contents or claiming success
- For checkbox/radio questions with negation, thresholds, counts, prior-filing history, or similar nuanced wording, verify the exact question text and which option corresponds to the case facts before selecting any value

- If the field list, helper-script input schema, or verification output is truncated, incomplete, contradictory, blank, or unusable, stop and retrieve a complete view or use another inspection method before filling or concluding success
- For fillable PDFs, treat exported field metadata as the source of truth for field IDs, locations, control types, and available export values before writing any values
- When field names are abstract or non-semantic, combine extracted field metadata (IDs/types/pages/rectangles) with layout-preserved rendered text to identify the actual question before assigning a value
- Do not start a value map or fill run until you can point, for each intended field, to evidence tying the PDF field name/ID to the visible prompt or control; for repeated names, checkboxes, radios, and later-page fields, inspect the actual target entries rather than extrapolating from a sample
- When using a helper fill script, inspect a real sample record/schema first, keep its format consistent, and verify every required key is present exactly as expected; do not switch formats midstream or batch-fill guessed IDs
- For each checkbox/radio field you plan to set, read that field's actual export/checked value from the extracted metadata and use that exact value; do not assume a shared checked state across fields
- For yes/no or conditional sections, never fill both the trigger answer and the opposite-branch explanation field; leave non-selected branch fields blank
- If the fill step confirms only a subset of the values you attempted to write, assume partial completion rather than success; reconcile the intended mapping with confirmed output field-by-field before finishing
- Repeated errors such as missing `/AcroForm`, invalid PDF object types, disappearing form fields, or broken object references mean the current fill method is unsound; stop low-level patching and change methods instead of continuing minor variations
- Do not describe pages as looking correct, legible, or filled unless the inspection output itself contains readable evidence supporting that claim
- Task-specific protocol compliance is mandatory: do not switch to a different tool syntax, response format, or completion phrase than the task requires


## Common Patterns

- PDF form field detection and filling
- Regular expression for extracting structured data
- Address parsing (street, city, state, zip)
- Phone number formatting

## Tips

- Check if fields use standard naming conventions
- Verify PDF field types (text, date, checkbox)
- Keep personal information exactly as provided in description
- Test with simple form first to understand field structure

- Build a brief fact -> field mapping list before filling: form evidence -> field meaning -> case fact -> value
- Search the full extracted field inventory for each intended target; field names can be misleading or non-semantic
- Inspect a sample field record before creating any JSON or transform input, and mirror the helper script's schema exactly
- After generating any mapping JSON or field-values file, open it and verify the actual key-value pairs before running the final fill step
- For AcroForm PDFs, prefer a fill pattern that preserves the source form dictionary rather than starting from a fresh writer that drops it
- For library-based fills, preserve the original `/AcroForm` before updating fields; if the method raises `/AcroForm`-related errors or field enumeration disappears, stop and switch methods instead of patching forward blindly
- Use a completion checklist for verification: parties, all provided contact details, addresses, dates, amounts, narrative/reason fields, signatures/dates, and every checkbox/radio you set

- After filling, check every item you set in the output PDF, especially names, dates, addresses, amounts, court/venue fields, long text boxes, and checkbox/radio selections

- When the form is fillable, start by exporting field metadata before building the mapping; use that field structure as the primary source of truth
- Treat the extracted field inventory plus rendered page images as the most reliable pairing for interpreting cryptic, long, or nested field names
- When the field inventory is large, search it systematically by case facts and likely concepts (for example party names/roles, dates, amounts, checkbox groups, and filing location fields) to narrow candidates before mapping
- If field IDs are unclear, use page order plus field coordinates/rectangles to map them to the rendered form
- Use an intermediate `field_values` JSON or equivalent mapping file as an auditable checkpoint before running the final fill
- After each fill pass on a native-form PDF, read the saved field values back programmatically and also prefer visual verification by rendering the saved PDF pages
- Before finalizing, make sure your completion message also matches any environment-required token or termination format exactly