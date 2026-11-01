#!/usr/bin/env python3
"""Resolve Heading 1 text to rendered PDF pages for the report's cached TOC."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from docx import Document


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    headings = [p.text.strip() for p in Document(args.docx).paragraphs
                if p.style.name == "Heading 1" and p.text.strip() != "Contents"]
    info = subprocess.run(
        ["pdfinfo", str(args.pdf)], check=True, text=True, capture_output=True
    ).stdout
    match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    if not match:
        raise SystemExit(f"Could not determine PDF page count: {args.pdf}")
    page_count = int(match.group(1))
    page_lines = []
    for page_number in range(1, page_count + 1):
        extracted = subprocess.run(
            ["pdftotext", "-f", str(page_number), "-l", str(page_number), "-layout", str(args.pdf), "-"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        page_lines.append([normalized(line) for line in extracted.splitlines() if normalized(line)])
    resolved: dict[str, int] = {}
    missing: list[str] = []
    for heading in headings:
        needle = normalized(heading)
        # Heading 1 text is emitted as its own PDF line. Exact line matching
        # avoids false positives such as the word "References" in body prose.
        matches = [index + 1 for index, lines in enumerate(page_lines)
                   if index != 1 and needle in lines]
        if not matches:
            missing.append(heading)
        else:
            resolved[heading] = matches[0]
    if missing:
        raise SystemExit("Unresolved report headings: " + "; ".join(missing))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(resolved, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "headings": len(resolved), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
