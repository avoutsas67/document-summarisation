"""
Example usage of the PDF to Markdown converter.

This script demonstrates how to use the PDFToMarkdownConverter class
to convert PDFs, extract table of contents, and generate summaries.
"""

from pdf_to_markdown import PDFToMarkdownConverter
import os


def example_basic_usage():
    """
    Basic example: Process a single PDF file.
    """
    print("Example 1: Basic Usage")
    print("=" * 50)
    
    # Initialize converter (will use MISTRAL_API_KEY from environment)
    converter = PDFToMarkdownConverter()
    
    # Process a PDF file
    pdf_path = "sample.pdf"  # Replace with your PDF file path
    
    if not os.path.exists(pdf_path):
        print(f"Note: {pdf_path} not found. This is just an example.")
        print("Replace 'sample.pdf' with an actual PDF file path to test.")
        return
    
    result = converter.process_pdf(pdf_path, output_dir="./output")
    
    print("\nProcessing complete!")
    print(f"Found {len(result['toc'])} table of contents entries")
    print(f"\nFirst 3 TOC entries:")
    for entry in result['toc'][:3]:
        print(f"  Level {entry['level']}: {entry['title']}")


def example_individual_operations():
    """
    Example: Use individual methods for specific tasks.
    """
    print("\nExample 2: Individual Operations")
    print("=" * 50)
    
    converter = PDFToMarkdownConverter()
    
    pdf_path = "sample.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Note: {pdf_path} not found. This is just an example.")
        return
    
    # Step 1: Convert to markdown
    print("Step 1: Converting PDF to Markdown...")
    markdown = converter.convert_pdf_to_markdown(pdf_path)
    print(f"Generated {len(markdown)} characters of markdown")
    
    # Step 2: Extract TOC
    print("\nStep 2: Extracting table of contents...")
    toc = converter.extract_table_of_contents(markdown)
    print(f"Found {len(toc)} headings")
    
    # Step 3: Generate summary
    print("\nStep 3: Generating summary...")
    summary = converter.generate_summary(markdown)
    print(f"Summary: {summary[:100]}...")


def example_with_custom_api_key():
    """
    Example: Initialize with a custom API key.
    """
    print("\nExample 3: Custom API Key")
    print("=" * 50)
    
    # You can pass the API key directly instead of using environment variable
    api_key = os.environ.get("MISTRAL_API_KEY", "your-api-key-here")
    converter = PDFToMarkdownConverter(api_key=api_key)
    
    print("Converter initialized with custom API key")


def main():
    """
    Run all examples.
    """
    print("PDF to Markdown Converter - Examples")
    print("=" * 50)
    print()
    
    # Check for API key
    if not os.environ.get("MISTRAL_API_KEY"):
        print("WARNING: MISTRAL_API_KEY environment variable not set!")
        print("Set it with: export MISTRAL_API_KEY='your-api-key'")
        print()
    
    # Run examples
    example_with_custom_api_key()
    print()
    example_basic_usage()
    print()
    example_individual_operations()
    
    print("\n" + "=" * 50)
    print("Examples complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
