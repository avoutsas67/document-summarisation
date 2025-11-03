"""
MistralOCRpdf2md - A clean class-based implementation for PDF to Markdown conversion using Mistral OCR
"""
import base64
import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict

import requests
from pypdf import PdfReader, PdfWriter
from dotenv import load_dotenv


class MistralOCRpdf2md:
    """
    Convert PDF documents to Markdown using Mistral OCR API.
    Handles large PDFs by splitting them into manageable parts.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: str = "mistral-document-ai-2505",
        pages_per_part: int = 30
    ):
        """
        Initialize the MistralOCRpdf2md converter.
        
        Args:
            api_key: Azure API key (defaults to environment variable)
            endpoint: Azure endpoint URL (defaults to environment variable)
            model: Model name to use for OCR
            pages_per_part: Number of pages per split part (default: 30)
        """
        load_dotenv()
        
        self.api_key = api_key or self._get_api_key()
        self.endpoint = endpoint or self._get_endpoint()
        self.model = model
        self.pages_per_part = pages_per_part
        self.images_dir = "images"
        
    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        key = os.getenv("AZ_DEV_DAP_AI_001_AIS_KEY", "")
        if not key:
            raise ValueError("API key not found in environment variables")
        return key
    
    def _get_endpoint(self) -> str:
        """Get endpoint URL from environment variables."""
        base_url = os.getenv("AZ_DEV_DAP_AI_001_AIS_URL", "")
        if not base_url:
            raise ValueError("Endpoint URL not found in environment variables")
        return f"{base_url}/providers/mistral/azure/ocr"
    
    def split_pdf(self, pdf_path: Path) -> Tuple[Path, List[Dict]]:
        """
        Split a PDF into multiple parts.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (output_folder, list of part metadata)
        """
        pdf_reader = PdfReader(pdf_path)
        output_folder = pdf_path.parent / pdf_path.stem
        output_folder.mkdir(exist_ok=True)
        
        total_pages = len(pdf_reader.pages)
        total_parts = (total_pages + self.pages_per_part - 1) // self.pages_per_part
        
        print(f"Splitting {total_pages} pages into {total_parts} parts...")
        
        pdf_parts = []
        for part_num in range(total_parts):
            part_info = self._create_pdf_part(
                pdf_reader, pdf_path, output_folder, part_num, total_pages
            )
            pdf_parts.append(part_info)
        
        print(f"All parts saved in: {output_folder}")
        return output_folder, pdf_parts
    
    def _create_pdf_part(
        self,
        pdf_reader: PdfReader,
        pdf_path: Path,
        output_folder: Path,
        part_num: int,
        total_pages: int
    ) -> Dict:
        """
        Create a single PDF part.
        
        Returns:
            Dictionary with part metadata
        """
        start_page = part_num * self.pages_per_part
        end_page = min(start_page + self.pages_per_part, total_pages)
        
        pdf_writer = PdfWriter()
        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        output_filename = f"{pdf_path.stem}-P{part_num}.pdf"
        output_path = output_folder / output_filename
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        pages_count = end_page - start_page
        print(f"Created {output_filename} with {pages_count} pages (pages {start_page + 1}-{end_page})")
        
        return {
            'id': part_num,
            'filename': output_filename,
            'pages': (start_page, end_page)
        }
    
    def _encode_pdf(self, pdf_path: Path) -> str:
        """Encode PDF file to base64."""
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    
    def _call_ocr_api(self, pdf_base64: str) -> Dict:
        """
        Call the Mistral OCR API.
        
        Args:
            pdf_base64: Base64 encoded PDF content
            
        Returns:
            API response as dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{pdf_base64}"
            },
            "include_image_base64": True
        }
        
        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    
    def _save_image(self, img_data: Dict, part_num: int, images_path: Path) -> None:
        """Save an image from the OCR result to disk."""
        img_filename_parts = img_data["id"].split("-")
        img_filename = f"{img_filename_parts[0]}-{part_num}.{img_filename_parts[1]}"
        img_path = images_path / img_filename
        
        img_bytes = base64.b64decode(img_data["image_base64"].split(",")[1])
        with open(img_path, "wb") as img_file:
            img_file.write(img_bytes)
    
    def _extract_markdown(
        self,
        ocr_result: Dict,
        part_num: int,
        page_offset: int,
        images_path: Path
    ) -> str:
        """
        Extract markdown content from OCR result and save images.
        
        Args:
            ocr_result: API response
            part_num: Current part number
            page_offset: Page number offset for this part
            images_path: Path to save images
            
        Returns:
            Extracted markdown text
        """
        markdown_content = ""
        
        for page in ocr_result.get("pages", []):
            # Save images from this page
            for img in page.get("images", []):
                self._save_image(img, part_num, images_path)
            
            # Extract markdown and add page footer
            page_footer = f"\n\nPage {page['index'] + page_offset + 1}\n\n---\n\n"
            markdown_content += page.get("markdown", "") + page_footer
        
        # Fix image references for this part
        markdown_content = markdown_content.replace('img-', f'img-{part_num}.')
        markdown_content = markdown_content.replace('(img-', f'({self.images_dir}/img-')
        
        return markdown_content
    
    def convert_pdf_part(
        self,
        pdf_path: Path,
        page_offset: int = 0,
        part_num: int = 0
    ) -> str:
        """
        Convert a single PDF (or part) to Markdown.
        
        Args:
            pdf_path: Path to the PDF file
            page_offset: Starting page number for this part
            part_num: Part number identifier
            
        Returns:
            Extracted markdown text
        """
        # Prepare paths
        images_path = pdf_path.parent / self.images_dir
        images_path.mkdir(parents=True, exist_ok=True)
        
        # Encode and process
        pdf_base64 = self._encode_pdf(pdf_path)
        ocr_result = self._call_ocr_api(pdf_base64)
        markdown_text = self._extract_markdown(
            ocr_result, part_num, page_offset, images_path
        )
        
        return markdown_text
    
    def convert_pdf(self, pdf_path: Path) -> str:
        """
        Convert a complete PDF to Markdown, handling splitting if needed.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Path to the generated markdown file
        """
        # Split PDF into parts
        output_folder, pdf_parts = self.split_pdf(pdf_path)
        
        # Process each part
        full_markdown = ""
        for part_info in pdf_parts:
            try:
                part_path = output_folder / part_info['filename']
                page_offset = part_info['pages'][0]
                part_num = part_info['id']
                
                print(f"Processing: {part_path}")
                markdown_text = self.convert_pdf_part(part_path, page_offset, part_num)
                full_markdown += markdown_text
                print(f"✓ OCR completed successfully for part: {part_info['filename']}")
                
            except requests.exceptions.HTTPError as e:
                print(f"API Error: {e}")
                print(f"Response: {e.response.text}")
                raise
            except Exception as e:
                print(f"Error processing {part_info['filename']}: {e}")
                raise
        
        # Fix image paths to include folder name
        full_markdown = full_markdown.replace(
            f'({self.images_dir}',
            f'({output_folder.stem}/{self.images_dir}'
        )
        
        # Save final markdown file
        md_path = pdf_path.parent / f"{pdf_path.stem}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_markdown)
        
        print(f"\n✓ Markdown saved to: {md_path}")
        return str(md_path)


def main():
    """Example usage of MistralOCRpdf2md."""
    # Initialize converter
    converter = MistralOCRpdf2md(pages_per_part=30)
    
    # Convert PDF
    pdf_path = Path("tehdas2-04.pdf")
    
    try:
        md_path = converter.convert_pdf(pdf_path)
        print(f"\nConversion completed! Markdown file: {md_path}")
    except FileNotFoundError:
        print(f"Error: PDF file '{pdf_path}' not found")
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
