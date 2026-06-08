---
name: fillable-pdf-form-filling
description: "Fill structured, fillable PDFs (e.g., court/government forms) by extracting fields, mapping user data, handling checkboxes/dates/amounts, and verifying the result."
---

# Fillable PDF Form Filling

A reliable workflow to fill government/court forms (and similar AcroForm PDFs) using field extraction, visual mapping, cautious value formatting, and image-based verification.

## When to Use

Activate this skill when you must:
- fill a provided blank, fillable PDF using case/task details
- choose correct yes/no or multi-option checkboxes
- format dates and numeric amounts consistently
- leave court/clerk or optional fields empty on request

## Core Workflow

1) Detect and inspect form fields
- Check fillability:
  - python3 scripts/check_fillable_fields.py <input.pdf>
- Extract field metadata to JSON:
  - python3 scripts/extract_form_field_info.py <input.pdf> <field_info.json>
- Convert pages to images for visual mapping:
  - python3 scripts/convert_pdf_to_images.py <input.pdf> <images_dir>

2) Map user data to exact field_ids
- Read field_info.json. Identify candidate fields by page, type, and field_id substrings (e.g., Name, Address, City, State, Zip, Phone, Email, Amount, Date, Reason, Checkbox).
- Use page images to confirm which field aligns with each printed label.
- Optional: Run the annotator (scripts/annotate_pdf_fields.py) to overlay field boxes and labels on images for precise mapping.
- Build a field_values.json list with entries:
  - {"field_id": "<exact id from field_info.json>", "value": "<string value>"}
- Only include fields the instructions require; omit court/clerk-only or optional fields if told to leave them blank.

3) Normalize values before filling
- Dates: Use ISO format YYYY-MM-DD. Choose the fields that correspond to the requested labels (e.g., a date range typically uses two distinct date fields). Do not populate unrelated date boxes.
- Amounts: Use plain numerals, preferably fixed 2 decimals (e.g., 1500.00). Avoid currency symbols and thousands separators unless the specific PDF field clearly expects them.
- Checkboxes (and binary choices): Most two-option groups are left-to-right (Yes/No); confirm via image context. For AcroForm checkboxes, values are usually "/1" (left/first) and "/2" (right/second). Set exactly one value in a binary group. When unsure, annotate and verify visually, then adjust.
- Text areas: Keep explanations concise and factual; match the printed prompt near the field.

4) Validate your mapping (recommended)
- Ensure every field_id in field_values.json exists in field_info.json.
- Heuristically check that date-like and amount-like fields follow the normalization rules.
- Command:
  - python3 scripts/validate_field_values.py <field_info.json> <field_values.json>

5) Fill the PDF
- python3 scripts/fill_fillable_fields.py <input.pdf> <field_values.json> <output.pdf>

6) Verify the filled output
- Convert the filled PDF to images:
  - python3 scripts/convert_pdf_to_images.py <output.pdf> <filled_images_dir>
- Visually confirm:
  - Correct fields are populated
  - Only necessary fields are filled
  - Checkboxes align with the printed labels
  - Dates and amounts are properly formatted
  - Court/clerk-only fields remain empty
- If anything is off (e.g., the wrong checkbox in a pair), adjust field_values.json and refill.

## Verification Checklist

Before filling:
- Field metadata extracted (field_info.json present) and pages converted to images.
- Mappings use only field_ids that exist in field_info.json.
- Dates planned in YYYY-MM-DD per instructions.
- Numeric amounts prepared without currency symbols/commas unless confirmed.

After filling:
- Visual check on the filled images for:
  - Correct parties and contacts in the right sections
  - Correct amount and reason fields
  - Correct date fields (single date vs. date range as labeled)
  - Correct checkbox selection (Yes/No and multi-option lines)
  - Court/clerk fields left blank if instructed

## Common Pitfalls (and How to Avoid Them)

- Misinterpreting binary questions (e.g., "Have you filed more than N?" vs. "first time suing"): read the printed prompt near the checkboxes; pick the option that matches the literal question.
- Guessing field_ids: never. Always copy exact field_id strings from field_info.json.
- Wrong checkbox index: many two-option groups use "/1" and "/2"; confirm which side is which via the page image (left typically "/1"). Verify after filling.
- Filling the wrong date boxes: forms often include multiple date fields (single date, "from", and "through"). Match fields to the printed labels on the page, not just by name.
- Formatting amounts with "$" or commas: use plain numbers with two decimals unless the form specifically renders a currency mask.
- Filling court/clerk-only fields (case number, trial date, clerk signature): leave them empty unless the instructions explicitly direct you to fill them.
- Skipping output verification: always render the filled PDF to images for a final visual audit.
- Environment issues: use python3 for scripts; ensure output directories exist before conversion.

## Success Criteria

- The output PDF is created and visually shows correct, necessary entries only.
- Dates are in YYYY-MM-DD and placed in the correct fields.
- Amounts are numeric and properly formatted.
- Checkboxes match the intended answers and appear next to the correct printed labels.
- Court/clerk fields remain blank if required.

## Optional Script Usage

1) Annotate fields on page images to aid mapping
- python3 scripts/annotate_pdf_fields.py --field-info <field_info.json> --images-dir <images_dir> --out-dir <annotated_dir> [--types checkbox,text]
- Produces annotated images per page drawing boxes and labels over form fields.

2) Validate field_values against field_info
- python3 scripts/validate_field_values.py <field_info.json> <field_values.json>
- Warns on unknown field_ids and common formatting issues for dates and amounts; checks checkbox values are plausible.
