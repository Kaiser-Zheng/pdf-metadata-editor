# PDF Metadata Editor

A simple Python tool to add metadata to PDF files using JSON configuration.

## Quick Start

### Prerequisites

- Python 3.8+
- uv package manager

### Installation

Clone the repository:

```bash
git clone git@github.com:Kaiser-Zheng/pdf-metadata-editor.git
cd pdf-metadata-editor
```

Install dependencies with uv:

```bash
uv sync
```

### Usage

1. Create a `metadata.json` file with your desired metadata:
```json
{
    "Title": "My Document Title",
    "Author": "Your Name", 
    "Subject": "Document Description",
    "Creator": "Scanner App",
    "Keywords": "pdf, metadata, document"
}
```

2. Run the script:
```bash
# Basic usage - creates input_updated.pdf
uv run pdf_metadata_editor.py input.pdf

# Specify output file
uv run pdf_metadata_editor.py input.pdf --output updated.pdf

# Use custom metadata config
uv run pdf_metadata_editor.py input.pdf --config my_metadata.json
```

## Command Line Options

```
usage: pdf_metadata_editor.py [-h] [--output OUTPUT] [--config CONFIG] input_pdf

positional arguments:
  input_pdf             Input PDF file path

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output PDF file path (default: input_updated.pdf)
  --config CONFIG, -c CONFIG
                        Metadata configuration JSON file (default: metadata.json)
```

## JSON Configuration

The metadata JSON file supports these standard PDF fields:

| Field | Description | Example |
|-------|-------------|---------|
| `Title` | Document title | "Research Paper Analysis" |
| `Author` | Document author | "Kaiser Zheng" |
| `Subject` | Document subject/description | "Academic Research" |
| `Creator` | Application that created the document | "Scanner Pro" |
| `Producer` | Application that produced the PDF | "PDF Generator" |
| `Keywords` | Comma-separated keywords | "research, academic, analysis" |
