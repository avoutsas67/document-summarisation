# %%
from pypdf import PdfReader

pdf_path = "tehdas2-04.pdf"

pdf = PdfReader(pdf_path)

print(pdf.metadata)
print(f"Number of pages: {len(pdf.pages)}")

# %%
for page_num, page in enumerate(pdf.pages):
    text = page.extract_text()
    print(f"\n--- Page {page_num + 1} ---\n")
    text = pdf.pages[page_num].extract_text()

    # Print the size of the extracted text and a preview
    print(f"Extracted text length: {len(text)} characters")
    # Print the number of words in the extracted text
    word_count = len(text.split())
    print(f"Number of words: {word_count}")
    # Print the number of paragraphs in the extracted text
    paragraph_count = len(text.split('\n \n '))
    print(f"Number of paragraphs: {paragraph_count}")

# %%
