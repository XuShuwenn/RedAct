---
name: court-pdf-form-filling
description: "Fill court/government PDF forms by extracting fields, mapping provided facts to required inputs, correctly handling checkboxes/radios, and verifying results."
---

# Court/Government PDF Form Filling

Reusable workflow for completing fillable court or government PDF forms using user-provided case facts. Emphasizes accurate field mapping, correct checkbox/radio handling, date normalization, and strong verification. Applicable to multi-page forms with a mix of text fields, checkboxes, radios, and text areas.

## When to Use

Activate this skill when:
- The user asks you to complete a court/government PDF form from a provided blank PDF and case facts.
- The form includes fillable fields and requires precise selections (checkbox/radio) and formatted dates.
- You must fill only specified/required fields and leave court-only, optional, or unspecified fields blank.

## Core Workflow

1. Gather Requirements
   - Extract all facts from the prompt (parties, addresses, contact info, amounts, dates, venue basis, declarations, etc.).
   - Note constraints (e.g., required date format like yyyy-mm-dd; explicit instruction to leave court-filled/optional fields blank; required output path).
   - Identify any missing information. If critical, ask for clarification rather than guessing.

2. Inspect the PDF
   - Confirm the PDF is a fillable form (has AcroForm fields).
   - Extract field metadata (name, field type, current value, widget page index, checkbox/radio available states).
   - Optionally convert pages to images (or open a preview) to understand visual layout and correlate similar field names with physical positions.

3. Plan the Mapping
   - Create a field-value mapping plan before filling.
   - Decide exactly which fields to fill based on the prompt and form labels.
   - Explicitly list which fields must remain blank (court use, optional, or not mentioned by user).
   - Normalize dates to the required format (e.g., yyyy-mm-dd) and keep a consistent phone/address format per instructions.
   - For multi-part dates (e.g., separate month/day/year vs. a single date field), map accordingly; don’t assume format—inspect the fields.
   - For checkboxes/radios, determine the correct "On" state key for the intended selection by inspecting the field’s appearance states.

4. Create a Reproducible Values File
   - Save the planned mapping to a JSON file (keys: field names; values: strings for text fields, the correct "On" state for checkboxes/radios, or booleans that your filler script can translate to On/Off states).

5. Fill the Form
   - Use a robust library/script to populate the form fields from your mapping, preserving the form structure.
   - Ensure checkbox/radio widgets set both the value (V) and appearance state (AS) to the correct On/Off key.
   - Write the completed file to the requested output path.

6. Verification
   - Programmatic verification:
     - Re-read the filled PDF fields and confirm each mapped field contains the intended value.
     - Validate date formats (e.g., regex ^\d{4}-\d{2}-\d{2}$ when required).
     - Confirm that court-only/unspecified fields remain empty.
   - Visual verification:
     - Convert the filled PDF pages to images or open a preview to spot-check key pages.
     - Confirm checkboxes/radios appear selected as intended and free of unintended marks.
   - Confirm the output file exists and is readable.

7. Deliver
   - Provide the output path and a concise summary of what was filled.
   - Offer to adjust if any field mapping needs revision.

## Verification Checklist

- Output file exists at the requested path.
- All required fields populated; no court-only or unspecified fields were filled.
- Checkbox/radio selections match the intended options (On states verified from the form).
- Dates match the required format throughout the form.
- Visual spot-check on relevant pages shows text is legible and in the correct sections.

## Common Pitfalls and How to Avoid Them

- Filling court-use header fields (e.g., case number, court clerk entries):
  - Avoid: Only fill fields explicitly requested or required by the form instructions.
- Incorrect checkbox/radio selection due to assuming "Yes" is the On value:
  - Inspect the field’s appearance states and use the exact On key (e.g., a custom label like "1", "On", or a named state). Never assume "Yes" universally.
- Wrong date format or inconsistent date representation:
  - Normalize dates to the required format (e.g., yyyy-mm-dd) before filling. Verify via regex after filling.
- Mapping to the wrong field when names are similar:
  - Use both field metadata and page layout (via images) to disambiguate; confirm page numbers and positions.
- Overfilling or inferring new information:
  - Leave optional/not-mentioned fields blank. Do not guess missing details; ask for clarification if essential.
- Not updating widget appearance after setting value:
  - For checkboxes/radios, set both V and AS entries to the chosen On/Off value so the visual state matches the logical state.

## Optional Script Usage

This repository includes a generic helper script that can:
- List fields with types and checkbox/radio On/Off states.
- Fill a PDF using a JSON mapping.

Examples:

- List fields to JSON:
  - python3 scripts/pdf_form_utils.py list --pdf path/to/blank.pdf --out fields.json

- Fill form from JSON mapping:
  - python3 scripts/pdf_form_utils.py fill --pdf-in path/to/blank.pdf --values field_values.json --pdf-out path/to/filled.pdf

- Verify filled values:
  - python3 scripts/pdf_form_utils.py verify --pdf path/to/filled.pdf --expect field_values.json --require-date-format "^\d{4}-\d{2}-\d{2}$"

## Notes

- If the form includes multi-line narrative fields, keep the text concise to avoid overflow; prefer factual summaries.
- If the form splits a single concept across multiple fields (e.g., address lines), preserve order and avoid truncation.
- If the PDF has no fillable fields, plan for overlay rendering (out-of-scope for this helper) or inform the user that the form is not fillable.
