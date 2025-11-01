"""
PDF to Markdown Converter using Mistral OCR

This module converts PDF documents to Markdown format using Mistral's OCR API,
extracts the table of contents, and generates a document summary.
"""

import os
import sys
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from mistralai import Mistral


class PDFToMarkdownConverter:
    """
    Converts PDF documents to Markdown using Mistral OCR API.
    
    This class handles:
    - PDF to Markdown conversion using Mistral OCR
    - Table of contents extraction
    - Document summary generation
    """
    
    # Maximum characters from document to use for summary generation
    MAX_SUMMARY_CONTENT_LENGTH = 4000
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the converter with Mistral API key.
        
        Args:
            api_key: Mistral API key. If not provided, will use MISTRAL_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY must be provided or set as environment variable")
        
        self.client = Mistral(api_key=self.api_key)
    
    def _encode_pdf_to_base64(self, pdf_path: str) -> str:
        """
        Encode a PDF file to base64 string.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Base64 encoded string of the PDF
        """
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode("utf-8")
    
    def convert_pdf_to_markdown(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown format using Mistral OCR.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Markdown formatted string of the PDF content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Encode PDF to base64
        pdf_base64 = self._encode_pdf_to_base64(pdf_path)
        
        # Process with Mistral OCR
        ocr_response = self.client.ocr.process(
            model="pixtral-12b-2409",
            document={
                "type": "document_base64",
                "document_base64": pdf_base64
            }
        )
        
        # Combine all pages' markdown
        markdown_content = []
        for i, page in enumerate(ocr_response.pages, 1):
            markdown_content.append(f"<!-- Page {i} -->")
            markdown_content.append(page.markdown)
            markdown_content.append("")  # Empty line between pages
        
        return "\n".join(markdown_content)
    
    def extract_table_of_contents(self, markdown_content: str) -> List[Dict[str, str]]:
        """
        Extract table of contents from the markdown content.
        
        Looks for markdown headers (# ## ### etc.) to build the TOC.
        
        Args:
            markdown_content: Markdown formatted document content
            
        Returns:
            List of dictionaries containing TOC entries with 'level', 'title', and 'line' keys
        """
        toc = []
        lines = markdown_content.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith("#"):
                # Count the number of # to determine heading level
                level = 0
                for char in line:
                    if char == "#":
                        level += 1
                    else:
                        break
                
                # Extract title (remove # and whitespace)
                title = line.lstrip("#").strip()
                if title:  # Only add non-empty titles
                    toc.append({
                        "level": level,
                        "title": title,
                        "line": line_num
                    })
        
        return toc
    
    def generate_summary(self, markdown_content: str, max_tokens: int = 500) -> str:
        """
        Generate a summary of the document using Mistral AI.
        
        Args:
            markdown_content: Markdown formatted document content
            max_tokens: Maximum number of tokens for the summary
            
        Returns:
            Generated summary text
        """
        # Prepare the prompt for summarization
        # Limit content to avoid token limits
        content_preview = markdown_content[:self.MAX_SUMMARY_CONTENT_LENGTH]
        
        prompt = f"""Please provide a concise summary of the following document. 
Focus on the main topics, key points, and overall purpose of the document.

Document content:
{content_preview}

Please provide a summary:"""
        
        # Generate summary using Mistral chat
        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def process_pdf(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete processing pipeline: convert PDF to markdown, extract TOC, and generate summary.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Optional directory to save output files. If not provided, uses PDF directory.
            
        Returns:
            Dictionary containing 'markdown', 'toc', and 'summary' keys
        """
        print(f"Processing PDF: {pdf_path}")
        
        # Convert PDF to Markdown
        print("Converting PDF to Markdown...")
        markdown_content = self.convert_pdf_to_markdown(pdf_path)
        
        # Extract table of contents
        print("Extracting table of contents...")
        toc = self.extract_table_of_contents(markdown_content)
        
        # Generate summary
        print("Generating summary...")
        summary = self.generate_summary(markdown_content)
        
        # Prepare output directory
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path) or "."
        os.makedirs(output_dir, exist_ok=True)
        
        # Get base filename without extension
        base_filename = Path(pdf_path).stem
        
        # Save markdown content
        markdown_path = os.path.join(output_dir, f"{base_filename}.md")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Saved markdown to: {markdown_path}")
        
        # Save table of contents
        toc_path = os.path.join(output_dir, f"{base_filename}_toc.md")
        with open(toc_path, "w", encoding="utf-8") as f:
            f.write("# Table of Contents\n\n")
            for entry in toc:
                indent = "  " * (entry["level"] - 1)
                f.write(f"{indent}- {entry['title']}\n")
        print(f"Saved table of contents to: {toc_path}")
        
        # Save summary
        summary_path = os.path.join(output_dir, f"{base_filename}_summary.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("# Document Summary\n\n")
            f.write(summary)
        print(f"Saved summary to: {summary_path}")
        
        return {
            "markdown": markdown_content,
            "toc": toc,
            "summary": summary,
            "output_files": {
                "markdown": markdown_path,
                "toc": toc_path,
                "summary": summary_path
            }
        }


def main():
    """
    Command-line interface for the PDF to Markdown converter.
    """
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_markdown.py <pdf_file> [output_directory]")
        print("\nExample: python pdf_to_markdown.py document.pdf ./output")
        print("\nMake sure to set MISTRAL_API_KEY environment variable before running.")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        converter = PDFToMarkdownConverter()
        result = converter.process_pdf(pdf_path, output_dir)
        
        print("\n" + "="*50)
        print("Processing complete!")
        print("="*50)
        print(f"\nTable of Contents ({len(result['toc'])} entries):")
        for entry in result['toc'][:10]:  # Show first 10 entries
            indent = "  " * (entry['level'] - 1)
            print(f"{indent}- {entry['title']}")
        if len(result['toc']) > 10:
            print(f"  ... and {len(result['toc']) - 10} more entries")
        
        print(f"\nSummary preview:")
        print("-" * 50)
        summary_lines = result['summary'].split("\n")
        for line in summary_lines[:5]:  # Show first 5 lines
            print(line)
        if len(summary_lines) > 5:
            print("...")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
