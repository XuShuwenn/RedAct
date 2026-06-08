#!/usr/bin/env python3
"""Annotate PDF page images with form fields from field_info.json.

Usage:
  python3 scripts/annotate_pdf_fields.py --field-info /path/field_info.json \
      --images-dir /path/images --out-dir /path/annotated [--types checkbox,text]

Notes:
- Expects images created by convert_pdf_to_images.py with filenames like page_1.png, page_2.png, ...
- field_info.json is produced by extract_form_field_info.py and contains entries with keys:
  {"field_id": str, "page": int, "type": str, "rect": [left,bottom,right,top]}
- This script converts PDF coordinates to image coordinates and draws labeled boxes.
"""
import argparse
import json
import os
from PIL import Image, ImageDraw


def parse_args():
    p = argparse.ArgumentParser(description="Annotate page images with PDF form fields")
    p.add_argument("--field-info", required=True, help="Path to field_info.json")
    p.add_argument("--images-dir", required=True, help="Directory with page_*.png")
    p.add_argument("--out-dir", required=True, help="Directory to write annotated images")
    p.add_argument("--types", default=None, help="Comma-separated field types to include (e.g., 'checkbox,text')")
    return p.parse_args()


def short_label(field_id: str) -> str:
    parts = field_id.split('.')
    # Use last two parts to keep labels concise
    if len(parts) >= 2:
        return f"{parts[-2]}.{parts[-1]}"
    return parts[-1]


def annotate_page(img_path: str, fields: list, out_path: str):
    img = Image.open(img_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    for idx, d in enumerate(fields, 1):
        l, b, r, t = d.get("rect", [0, 0, 0, 0])
        # Convert PDF coords (origin bottom-left) to image coords (origin top-left)
        y1 = H - t
        y2 = H - b
        color = "red" if d.get("type") == "checkbox" else "blue"
        draw.rectangle([l, y1, r, y2], outline=color, width=2)
        label = f"{idx}:{short_label(d.get('field_id',''))}"
        draw.text((l, max(0, y1 - 12)), label, fill=color)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)


def main():
    args = parse_args()
    with open(args.field_info, "r") as f:
        info = json.load(f)

    allow_types = None
    if args.types:
        allow_types = {t.strip() for t in args.types.split(',') if t.strip()}

    # Group fields by page
    by_page = {}
    for d in info:
        if allow_types and d.get("type") not in allow_types:
            continue
        by_page.setdefault(d.get("page", 0), []).append(d)

    os.makedirs(args.out_dir, exist_ok=True)

    # Annotate each page image if present
    for page, fields in sorted(by_page.items()):
        img_path = os.path.join(args.images_dir, f"page_{page}.png")
        if not os.path.exists(img_path):
            # Skip pages without images
            continue
        out_path = os.path.join(args.out_dir, f"annotated_page_{page}.png")
        annotate_page(img_path, fields, out_path)
        print(f"Annotated: {out_path} ({len(fields)} fields)")


if __name__ == "__main__":
    main()
