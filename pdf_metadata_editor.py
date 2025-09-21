#!/usr/bin/env python3
"""
PDF Metadata Editor

This script adds metadata to PDF files using values from a JSON configuration file.
Usage: python pdf_metadata_editor.py input.pdf [--output output.pdf] [--config metadata.json]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("Error: PyPDF2 library not found. Install it with: pip install PyPDF2")
    sys.exit(1)


def load_metadata_config(config_path: str | Path) -> Optional[Dict[str, Any]]:
    """Load metadata configuration from JSON file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            metadata: Dict[str, Any] = json.load(f)
        return metadata
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{config_path}': {e}")
        return None
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return None


def update_pdf_metadata(
    input_path: str | Path, output_path: str | Path, metadata_config: Dict[str, Any]
) -> bool:
    """Update PDF metadata and save to output file."""
    try:
        # Read the input PDF
        reader: PdfReader = PdfReader(input_path)
        writer: PdfWriter = PdfWriter()

        # Copy all pages to the writer
        for page in reader.pages:
            writer.add_page(page)

        # Get existing metadata (if any)
        existing_metadata: Dict[str, Any] = reader.metadata or {}

        # Prepare new metadata
        new_metadata: Dict[str, Union[str, Any]] = {}

        # Standard PDF metadata fields mapping
        metadata_mapping: Dict[str, str] = {
            "Title": "/Title",
            "Author": "/Author",
            "Subject": "/Subject",
            "Creator": "/Creator",
            "Producer": "/Producer",
            "Keywords": "/Keywords",
        }

        # Copy existing metadata first
        for key, value in existing_metadata.items():
            new_metadata[key] = value

        # Update with new metadata from config
        for config_key, config_value in metadata_config.items():
            if config_key in metadata_mapping:
                pdf_key: str = metadata_mapping[config_key]
                new_metadata[pdf_key] = str(config_value)
                print(f"Setting {config_key}: {config_value}")
            else:
                print(f"Warning: Unknown metadata field '{config_key}' ignored")

        # Add creation date if not present
        if "/CreationDate" not in new_metadata:
            new_metadata["/CreationDate"] = datetime.now().strftime("D:%Y%m%d%H%M%S")

        # Add modification date
        new_metadata["/ModDate"] = datetime.now().strftime("D:%Y%m%d%H%M%S")

        # Apply metadata to writer
        writer.add_metadata(new_metadata)

        # Write the output PDF
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        return True

    except FileNotFoundError:
        print(f"Error: Input PDF file '{input_path}' not found.")
        return False
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Add metadata to PDF files using JSON configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_metadata_editor.py document.pdf
  python pdf_metadata_editor.py document.pdf --output updated_document.pdf
  python pdf_metadata_editor.py document.pdf --config custom_metadata.json
        """,
    )

    parser.add_argument("input_pdf", help="Input PDF file path")
    parser.add_argument("--output", "-o", help="Output PDF file path (default: input_updated.pdf)")
    parser.add_argument(
        "--config",
        "-c",
        default="metadata.json",
        help="Metadata configuration JSON file (default: metadata.json)",
    )

    args: argparse.Namespace = parser.parse_args()

    # Validate input file
    input_path: Path = Path(args.input_pdf)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_pdf}' does not exist.")
        sys.exit(1)

    if not input_path.suffix.lower() == ".pdf":
        print(f"Error: Input file must be a PDF file.")
        sys.exit(1)

    # Determine output path
    output_path: Path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_stem(f"{input_path.stem}_updated")

    # Load metadata configuration
    print(f"Loading metadata configuration from '{args.config}'...")
    metadata_config: Optional[Dict[str, Any]] = load_metadata_config(args.config)
    if metadata_config is None:
        sys.exit(1)

    # Validate that we have some metadata to add
    if not metadata_config:
        print("Warning: No metadata found in configuration file.")

    print(f"Processing PDF: {input_path}")
    print(f"Output will be saved to: {output_path}")

    # Update PDF metadata
    if update_pdf_metadata(input_path, output_path, metadata_config):
        print(f"\nSuccess! Updated PDF saved as '{output_path}'")

        # Display what was updated
        try:
            reader: PdfReader = PdfReader(output_path)
            if reader.metadata:
                print("\nFinal PDF metadata:")
                for key, value in reader.metadata.items():
                    if key.startswith("/"):
                        clean_key: str = key[1:]  # Remove leading slash
                        print(f"  {clean_key}: {value}")
        except:
            pass
    else:
        print("Failed to update PDF metadata.")
        sys.exit(1)


if __name__ == "__main__":
    main()
