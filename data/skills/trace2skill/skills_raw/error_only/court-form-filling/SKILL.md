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

1. Read the blank PDF form to understand field structure
2. Extract or inspect the complete form field list/schema, visible labels, and relevant rendered pages before mapping any values; if inspection is partial, truncated, or unclear, inspect further instead of guessing
3. If using a provided helper script or mapping file, inspect its usage/schema first and match its exact expected structure before generating JSON or other transform input
4. Parse case description to extract key information
5. Build a traceable field-to-data mapping using only confirmed PDF field names/IDs present in the extracted metadata or observed form layout
6. For checkboxes, radio buttons, yes/no controls, selects, and conditional sections, confirm the exact question semantics and valid export values before setting anything; distinguish answer controls from follow-up explanation fields
7. If a target field is ambiguous, unconfirmed, unsupported, or merely optional, leave it blank until resolved rather than guessing
8. If you generate a field-value mapping file, validate that it parses and preserves the required schema before using it
9. Fill the PDF form with the verified mapping while preserving the original AcroForm/form metadata; if a method removes fields, breaks form structure, or makes the output unreadable, stop and switch approaches
10. Save the filled form to the output path
11. Re-open, render, or extract fields from the saved PDF and verify that every populated required/high-risk field was actually written correctly in the verified output

## Important Notes

- Use date format: xxxx-xx-xx (e.g., 2026-01-19)
- Only fill fields mentioned in case description
- Leave court-filled and optional fields empty
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
- After filling, check every item you set in the output PDF, especially names, dates, addresses, amounts, court/venue fields, long text boxes, and checkbox/radio selections