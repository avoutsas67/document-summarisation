"""
Quick Start Example for Mistral OCR
A minimal example to get started quickly
"""
# %%
import base64
import os
import requests
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from dotenv import load_dotenv

load_dotenv()

AZ_DEV_DAP_AI_001_AIS_URL=os.getenv("AZ_DEV_DAP_AI_001_AIS_URL", "")
if AZ_DEV_DAP_AI_001_AIS_URL:
     AZ_MISTRAL_DOC_AI_2505_ENDPOINT=AZ_DEV_DAP_AI_001_AIS_URL + "/providers/mistral/azure/ocr"

AZ_DEV_DAP_AI_001_AIS_KEY =os.getenv("AZ_DEV_DAP_AI_001_AIS_KEY", "")
if AZ_DEV_DAP_AI_001_AIS_KEY:
    AZ_MISTRAL_DOC_AI_2505_KEY=AZ_DEV_DAP_AI_001_AIS_KEY
    
AZ_MISTRAL_DOC_AI_2505_NAME=os.getenv("AZ_MISTRAL_DOC_AI_2505_NAME", "mistral-document-ai-2505")

# %%
def split_pdf_to_parts(pdf_path, pages_per_part=30):
    """
    Split a PDF into multiple parts with specified number of pages per part.
    
    Args:
        pdf_reader: PdfReader object
        pdf_path: Path object of the original PDF file
        pages_per_part: Number of pages per part (default: 30)
    """
    pdf_reader = PdfReader(pdf_path)
    metadata = pdf_reader.metadata
    pages = pdf_reader.pages
    
    pdf_parts = []
    # Create output folder based on PDF filename (without extension)
    output_folder = pdf_path.parent / pdf_path.stem
    output_folder.mkdir(exist_ok=True)
    
    total_pages = len(pdf_reader.pages)
    total_parts = (total_pages + pages_per_part - 1) // pages_per_part  # Ceiling division
    
    print(f"Splitting {total_pages} pages into {total_parts} parts...")
    
    for part_num in range(total_parts):
        # Calculate page range for this part
        start_page = part_num * pages_per_part
        end_page = min(start_page + pages_per_part, total_pages)
        
        # Create new PDF writer for this part
        pdf_writer = PdfWriter()
        
        # Add pages to this part
        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        # Generate output filename
        part_suffix = f"P{part_num}"  # P0, P1, etc.
        output_filename = f"{pdf_path.stem}-{part_suffix}.pdf"
        output_path = output_folder / output_filename
        
        # Write the part to file
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        pages_in_part = end_page - start_page
        pdf_part = { 'id': part_num, 'filename': output_filename, 'pages': (start_page, end_page) }
        pdf_parts.append(pdf_part)
        print(f"Created {output_filename} with {pages_in_part} pages (pages {start_page + 1}-{end_page})")
    
    print(f"\nAll parts saved in: {output_folder}")
    return output_folder, pdf_parts, pages, metadata

# %%

def pdf2md(pdf_path: str, endpoint: str, api_key: str, model: str = 'mistral-document-ai-2505', page_offset: int = 0, part: int=0) -> str:
    """
    Simplest possible example of using Mistral OCR
    
    Args:
        pdf_path: Path to your PDF file
        endpoint: Your Azure endpoint URL
        api_key: Your Azure API key
    """
    # Step 1: Read and encode PDF to base64
    with open(pdf_path, "rb") as pdf_file:
        pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    # Step 2: Prepare the request
    #url = f"{endpoint.rstrip('/')}/v1/ocr"
    url = endpoint
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "document": {
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{pdf_base64}"
        },
        "include_image_base64": True
    }
    
    # Step 3: Make the API call
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    result = response.json()
   
    # Step 4: Extract content
    md_images_dir = 'images'
    pdf_parent = Path(pdf_path).parent
    pdf_stem = Path(pdf_path).stem
    md_images_path = pdf_parent / md_images_dir
    md_images_path.mkdir(parents=True, exist_ok=True)
    extracted_text = ""
    for page in result.get("pages", []):
        for img in page.get("images", []):
            # Save image base64 to disk 
            # Create a directory for using the stem of the PDF file
            img_filename_parts =  img["id"].split("-") # Extract filename from id
            img_filename = f"{img_filename_parts[0]}-{part}.{img_filename_parts[1]}"
            img_path = md_images_path / img_filename
            img_data = base64.b64decode(img["image_base64"].split(",")[1])
            with open(img_path, "wb") as img_file:
                img_file.write(img_data)
        page_footer = f"\n\nPage {page['index'] + page_offset + 1} \n\n---\n\n"
        extracted_text += page.get("markdown", "") + page_footer
    # Save the result
    extracted_text = extracted_text.replace('img-', f'img-{part}.')
    extracted_text = extracted_text.replace('(img-', f'({md_images_dir}/img-')
    md_path = pdf_parent / f"{pdf_stem}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return extracted_text

# %%
if __name__ == "__main__":
    # Replace with your values
    api_key = AZ_DEV_DAP_AI_001_AIS_KEY
    model = AZ_MISTRAL_DOC_AI_2505_NAME
    endpoint = AZ_MISTRAL_DOC_AI_2505_ENDPOINT
    # Example usage:
    # Split the current PDF into 30-page parts
    for i in range (11):
        pdf_path = Path(f"tehdas2-{i+1:02d}.pdf")
        output_folder, pdf_parts, pages, metadata = split_pdf_to_parts(pdf_path, 30)
        md_content = ""
        md_images_dir = 'images'
        for part_id in range(len(pdf_parts)):
            try:
                part_filename = pdf_parts[part_id]['filename']
                part_offset = pdf_parts[part_id]['pages'][0]
                PDF_FILE = output_folder / part_filename
                print(f"Processing: {PDF_FILE}")
                extracted_text = pdf2md(PDF_FILE, endpoint=endpoint, api_key=api_key, model=model, page_offset=part_offset, part=part_id)
                md_content += extracted_text
                print("✓ OCR completed successfully for part:", part_filename) 

            except FileNotFoundError:
                print(f"Error: PDF file '{PDF_FILE}' not found")
            except requests.exceptions.HTTPError as e:
                print(f"API Error: {e}")
                print(f"Response: {e.response.text}")
            except Exception as e:
                print(f"Error: {e}")
        md_content = md_content.replace(f'({md_images_dir}',f'({output_folder.stem}/{md_images_dir}')
        md_path = output_folder.parent / f"{pdf_path.stem}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

# %%
for i in range(1, 11):
    print(f"Doc id:{i:02d}")
# %%
