# Document Summarisation

A Python tool to convert PDF documents to Markdown format using Mistral OCR, extract table of contents, and generate summaries.

## Features

- **PDF to Markdown Conversion**: Uses Mistral's OCR API to accurately convert PDF documents to Markdown format
- **Table of Contents Extraction**: Automatically extracts headings and creates a structured table of contents
- **Document Summary Generation**: Uses Mistral AI to generate concise summaries of documents
- **Batch Processing**: Can process multiple PDF files efficiently
- **Preserves Structure**: Maintains document structure including headers, paragraphs, lists, and tables

## Requirements

- Python 3.7 or higher
- Mistral API key (get one from [Mistral's API key console](https://console.mistral.ai/api-keys))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/avoutsas67/document-summarisation.git
cd document-summarisation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your Mistral API key:
```bash
export MISTRAL_API_KEY='your-api-key-here'
```

## Usage

### Command Line

Basic usage:
```bash
python pdf_to_markdown.py <pdf_file>
```

Specify output directory:
```bash
python pdf_to_markdown.py document.pdf ./output
```

### Python API

```python
from pdf_to_markdown import PDFToMarkdownConverter

# Initialize converter
converter = PDFToMarkdownConverter(api_key="your-api-key")

# Process a PDF file
result = converter.process_pdf("document.pdf", output_dir="./output")

# Access results
print("Markdown content:", result['markdown'])
print("Table of contents:", result['toc'])
print("Summary:", result['summary'])
```

### Individual Operations

You can also use individual methods for specific tasks:

```python
from pdf_to_markdown import PDFToMarkdownConverter

converter = PDFToMarkdownConverter()

# Convert PDF to Markdown only
markdown = converter.convert_pdf_to_markdown("document.pdf")

# Extract TOC from existing markdown
toc = converter.extract_table_of_contents(markdown)

# Generate summary from markdown
summary = converter.generate_summary(markdown)
```

## Output Files

The tool generates three files:

1. **`<filename>.md`**: Full markdown conversion of the PDF
2. **`<filename>_toc.md`**: Extracted table of contents
3. **`<filename>_summary.md`**: AI-generated document summary

## Example Output

### Table of Contents
```
# Table of Contents

- Introduction
  - Background
  - Objectives
- Methodology
  - Data Collection
  - Analysis
- Results
- Conclusion
```

### Summary
```
# Document Summary

This document presents a comprehensive analysis of...
Key findings include...
The study concludes that...
```

## API Reference

### PDFToMarkdownConverter

#### `__init__(api_key: Optional[str] = None)`
Initialize the converter with Mistral API key.

#### `convert_pdf_to_markdown(pdf_path: str) -> str`
Convert a PDF file to Markdown format.

#### `extract_table_of_contents(markdown_content: str) -> List[Dict[str, str]]`
Extract table of contents from markdown content.

#### `generate_summary(markdown_content: str, max_tokens: int = 500) -> str`
Generate a summary of the document.

#### `process_pdf(pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, any]`
Complete processing pipeline: convert, extract TOC, and generate summary.

## Dependencies

- `mistralai` - Mistral AI Python client for OCR and chat completion
- `PyPDF2` - PDF file handling utilities

## Testing

Run the unit tests:

```bash
python -m unittest test_pdf_to_markdown.py -v
```

The tests use mocking to avoid requiring an actual Mistral API key during testing.

## Error Handling

The tool includes comprehensive error handling for:
- Missing API key
- File not found errors
- API connection issues
- Invalid PDF files

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.