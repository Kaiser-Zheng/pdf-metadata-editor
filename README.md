# PDF Metadata Editor

A simple CLI tool to add or update metadata in PDF files. Supports batch processing with glob patterns.

## Installation

```bash
uv sync
```

## Configuration

1. Copy the template config file:
   ```bash
   cp metadata.json.template metadata.json
   ```

2. Edit `metadata.json` with your desired metadata values.

### Config Options

| Field    | Description                                      |
|----------|--------------------------------------------------|
| Title    | Document title (`auto` = use filename)           |
| Author   | Author name                                      |
| Subject  | Document subject (`auto` = use filename)         |
| Creator  | Application that created the original document  |
| Producer | Application that converted it to PDF            |
| Keywords | Comma-separated keywords for search             |

## Usage

```bash
# Single file
uv run pdf_metadata_editor.py -i document.pdf

# Batch process all PDFs in current directory
uv run pdf_metadata_editor.py -i "*.pdf" -o ./processed/

# Multiple files with custom config
uv run pdf_metadata_editor.py -i doc1.pdf doc2.pdf -c custom.json

# Recursive glob
uv run pdf_metadata_editor.py -i "**/*.pdf" -o ./output/
```

### Options

| Option              | Description                              |
|---------------------|------------------------------------------|
| `-i, --input FILE`  | Input PDF file(s) or glob pattern(s)     |
| `-o, --output DIR`  | Output directory for processed PDFs      |
| `-c, --config FILE` | Config file (default: `metadata.json`)   |
| `-h, --help`        | Show help message                        |

