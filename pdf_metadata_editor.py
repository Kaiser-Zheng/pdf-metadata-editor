#!/usr/bin/env python3
"""
PDF Metadata Editor

Add metadata to PDF files using values from a JSON configuration file.
Supports batch processing with glob patterns.

Usage:
  uv run pdf_metadata_editor.py -i document.pdf
  uv run pdf_metadata_editor.py -i "*.pdf" -o ./processed/
  uv run pdf_metadata_editor.py -i file1.pdf file2.pdf -o ./output/ -c custom.json
"""

import argparse
import json
import sys
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import Any

from PyPDF2 import PdfReader, PdfWriter

METADATA_MAPPING: dict[str, str] = {
    "Title": "/Title",
    "Author": "/Author",
    "Subject": "/Subject",
    "Creator": "/Creator",
    "Producer": "/Producer",
    "Keywords": "/Keywords",
}


def load_config(path: Path) -> dict[str, Any] | None:
    """Load metadata configuration from JSON file."""
    try:
        result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return result
    except FileNotFoundError:
        print(f"Error: Config file '{path}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{path}': {e}")
    except Exception as e:
        print(f"Error reading config: {e}")
    return None


def resolve_metadata(config: dict[str, Any], pdf_name: str) -> dict[str, str]:
    """Resolve 'auto' values in metadata config using PDF filename."""
    resolved: dict[str, str] = {}
    for key, value in config.items():
        if key not in METADATA_MAPPING:
            print(f"  Warning: Unknown field '{key}' ignored")
            continue
        if str(value).lower() == "auto" and key in ("Title", "Subject"):
            resolved[key] = pdf_name
        else:
            resolved[key] = str(value)
    return resolved


def update_pdf_metadata(input_path: Path, output_path: Path, config: dict[str, Any]) -> bool:
    """Update PDF metadata and save to output file."""
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Start with existing metadata
        metadata: dict[str, Any] = dict(reader.metadata or {})

        # Resolve auto values and apply new metadata
        pdf_name = input_path.stem
        resolved = resolve_metadata(config, pdf_name)

        for key, value in resolved.items():
            pdf_key = METADATA_MAPPING[key]
            metadata[pdf_key] = value
            print(f"  {key}: {value}")

        # Timestamps
        now = datetime.now().strftime("D:%Y%m%d%H%M%S")
        metadata.setdefault("/CreationDate", now)
        metadata["/ModDate"] = now

        writer.add_metadata(metadata)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return True

    except FileNotFoundError:
        print("  Error: File not found")
    except Exception as e:
        print(f"  Error: {e}")
    return False


def expand_inputs(patterns: list[str]) -> list[Path]:
    """Expand glob patterns and validate PDF files."""
    files: list[Path] = []
    for pattern in patterns:
        matches = glob(pattern, recursive=True)
        if matches:
            files.extend(Path(m) for m in matches if m.lower().endswith(".pdf"))
        else:
            path = Path(pattern)
            if path.exists() and path.suffix.lower() == ".pdf":
                files.append(path)
    return sorted(set(files))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add metadata to PDF files using JSON configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run pdf_metadata_editor.py -i document.pdf
  uv run pdf_metadata_editor.py -i "*.pdf" -o ./processed/
  uv run pdf_metadata_editor.py -i doc1.pdf doc2.pdf -c custom.json
        """,
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        required=True,
        metavar="FILE",
        help="Input PDF file(s) or glob pattern(s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        help="Output directory for processed PDFs",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="metadata.json",
        metavar="FILE",
        help="Config file (default: metadata.json)",
    )

    args = parser.parse_args()

    # Load config
    config = load_config(Path(args.config))
    if config is None:
        sys.exit(1)

    if not config:
        print("Warning: Empty configuration file")

    # Expand input patterns
    input_patterns: list[str] = args.input
    pdf_files = expand_inputs(input_patterns)
    if not pdf_files:
        print("Error: No PDF files found matching input pattern(s)")
        sys.exit(1)

    # Determine output directory
    output_dir: Path | None = Path(args.output) if args.output else None

    print(f"Processing {len(pdf_files)} PDF(s)...\n")

    success = 0
    failed = 0
    for idx, pdf in enumerate(pdf_files, start=1):
        print(f"[{idx}/{len(pdf_files)}] {pdf.name}")

        if output_dir:
            out_path = output_dir / pdf.name
        else:
            out_path = pdf.with_stem(f"{pdf.stem}_updated")

        if update_pdf_metadata(pdf, out_path, config):
            print(f"  -> Saved: {out_path}\n")
            success += 1
        else:
            print("  -> Failed\n")
            failed += 1

    print(f"Done: {success} succeeded, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
