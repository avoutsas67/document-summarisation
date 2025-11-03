# %%
from pypdf import PdfReader, PdfWriter
from pathlib import Path

pdf_path = Path("RESTAPI/tehdas2-04.pdf")

pdf = PdfReader(pdf_path)

# %%
print(pdf.metadata)
print(f"Number of pages: {len(pdf.pages)}")

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
        part_suffix = f"P{part_num + 1:02d}"  # P01, P02, etc.
        output_filename = f"{pdf_path.stem}-{part_suffix}.pdf"
        output_path = output_folder / output_filename
        
        # Write the part to file
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        pages_in_part = end_page - start_page
        print(f"Created {output_filename} with {pages_in_part} pages (pages {start_page + 1}-{end_page})")
    
    print(f"\nAll parts saved in: {output_folder}")
    return output_folder

# %%
# Example usage:
# Split the current PDF into 30-page parts
split_pdf_to_parts(pdf_path, 30)

# %%
