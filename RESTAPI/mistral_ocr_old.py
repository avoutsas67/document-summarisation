# %%
import os
import csv
import json
import requests
import base64
import binascii
from urllib.parse import urlparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from mistralai import Mistral
import pymupdf #type: ignore

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PATH_DATA = Path("data")
PATH_PDF_PROCESSING = PATH_DATA / "pdf-processing"
PATH_EPAR_URL = (
    "/Users/achilleas.voutsas/Development/epar-pi/epar-pi-samples/epar-pi-samples.csv"
)
PATH_DUCKDB_EPAR = "ocr_data.duckdb"
HEADER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

environment = Environment(loader=FileSystemLoader("templates/"))
template_md = environment.get_template("ocr_data.md.j2")

with open(PATH_EPAR_URL) as f:
    reader = csv.reader(f)
    epar_pi_urls = list(reader)

url_epar = epar_pi_urls[0][1]
ocr_data = []


# %% [markdown]
# # Mistral OCR experiment converting PDF to markdown
#
# ## Check the size of a pdf file and download it
# %%
url = url_epar
try:
    response = requests.head(url, stream=True, headers={"User-Agent": HEADER_USER_AGENT})
    response.raise_for_status()  # Raise an exception for bad status codes
    if "Content-Length" in response.headers:
        file_size_bytes = int(response.headers["Content-Length"])
        print(f"File size: {file_size_bytes} bytes")
    else:
        print("Content-Length header not found.")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

# %% [markdown]
# ## Functions processing the PDF and storing results

# %%
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

def get_ocr_response_data(url: str) -> dict:
    """
    Processes a Mistral OCR request for a given document URL and returns the response data.

    Args:
        url (str): The URL of the document to be processed by the OCR service.

    Returns:
        dict: A dictionary containing the OCR response data, including the original document URL.
    """
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": url},
        include_image_base64=True,
    )
    data = ocr_response.model_dump()
    data["url"] = url
    return data

def set_process_folder(url: str, root:Path = PATH_PDF_PROCESSING) -> dict:
    process_folder: dict = {}
    url_parsed = urlparse(url)
    domain = url_parsed.netloc
    path_source = Path(url_parsed.path)
    stem = path_source.stem
    process_folder['stem'] = stem
    suffix = path_source.suffix
    process_folder['suffix'] = suffix
    path_parts = path_source.parent.parts
    if path_parts[0] == os.sep:
        path_parts = path_parts[1:]
    path_target:Path = Path(f"{root}/{domain}/{os.sep.join(path_parts)}") 
    path_target.mkdir(parents=True, exist_ok=True)
    process_folder['path'] = path_target
    return process_folder

def create_images(data: dict, process_folder: dict):
    for i, page in enumerate(data["pages"]):
        for img in page["images"]:
            img_base64 = img["image_base64"].split(",")
            base64_string = img_base64[1]
            filename = img["id"]
            path_image = process_folder['path'] / filename
            try:
                image = base64.b64decode(base64_string, validate=True)
                with open(path_image, "wb") as f:
                    f.write(image)
            except binascii.Error as e:
                print(e)

def process_pdf(url: str):
    process_folder = set_process_folder(url)
    try:
        path_target_json = process_folder['path'] / f"{process_folder['stem']}.json"  
        if not path_target_json.exists():
            data = get_ocr_response_data(url)
        create_images(data, process_folder)
        path_target_md = process_folder['path'] / f"{process_folder['stem']}.md"
        path_target_json.write_text(json.dumps(data))
        context = { "ocr_pages": data['pages'] }
        with open(path_target_md, mode="w", encoding="utf-8") as results:
            results.write(template_md.render(context))
    except Exception as e:
        print(f"An error occurred: {e}")
    return data

def download_pdf(url: str, output_path: Path):
    try:
        response = requests.get(url, headers={"User-Agent": HEADER_USER_AGENT})
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF to {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the PDF: {e}")

def read_pdf_metadata_and_toc(pdf_path: Path) -> dict:
    try:
        doc = pymupdf.open(pdf_path)
        page_count = doc.page_count
        metadata = doc.metadata
        toc = doc.get_toc()
        return {"metadata": metadata, "toc": toc}
    except Exception as e:
        print(f"An error occurred while reading the PDF metadata and TOC: {e}")
        return {}

def split_pdf_into_pages(pdf_path: Path, output_folder: Path):
    try:
        doc = pymupdf.open(pdf_path)
        page_count = doc.page_count
        output_folder.mkdir(parents=True, exist_ok=True)
        page_count = doc.page_count
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            pix.save(output_folder / f"page_{page_num + 1}.png")
            single_page_doc = pymupdf.open()
            single_page_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            output_path = output_folder / f"page_{page_num + 1}.pdf"
            single_page_doc.save(output_path)
            print(f"Saved {output_path}")
    except Exception as e:
        print(f"An error occurred while splitting the PDF: {e}")

# Example usage:
# metadata_and_toc = read_pdf_metadata_and_toc(Path("sample.pdf"))
# print(metadata_and_toc)
# split_pdf_into_pages(Path("sample.pdf"), Path("output_pages"))

# %%
data_epar = process_pdf(url_epar)
ocr_data.append(data_epar)
# %%
url_test = "https://arxiv.org/pdf/2201.04234"
data_test = process_pdf(url_test)
ocr_data.append(data_test)
# %%
# %%
process_folder = set_process_folder(url_epar)
path_target_json = process_folder['path'] / f"{process_folder['stem']}.json" 
path_target_json.exists()

# %%
path_target_md = process_folder['path'] / f"{process_folder['stem']}.md"
md_data = json.loads(path_target_json.read_text())

# %%
out = Path("output")
split_pdf_into_pages(Path('test.pdf'), out)

# %% [markdown]
# ## Upload PDF to Mistral and process it with OCR
# %%
path_nap = Path("SPC SCAN") 
path_nap_pdf = path_nap / "SPC SCAN.pdf"
path_nap_md = path_nap / "SPC SCAN.md"
assert path_nap_pdf.exists()

uploaded_pdf = client.files.upload(
    file={
        "file_name": "uploaded_file.pdf",
        "content": open(path_nap_pdf, "rb"),
    },
    purpose="ocr"
)  
signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

# %%
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": signed_url.url,
    }
)
data = ocr_response.model_dump()
print(data.keys())
# %%
context = { "ocr_pages": data['pages'] }
with open(path_nap_md, mode="w", encoding="utf-8") as results:
    results.write(template_md.render(context))
# %%
