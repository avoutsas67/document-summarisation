# Azure AI Foundry Mistral OCR - Python Example

This example demonstrates how to use Azure AI Foundry's Mistral Document AI (Mistral OCR) to extract text and structure from PDF documents using Python.

## Features

- ✅ Load PDF files from local drive
- ✅ Convert PDF to base64 encoding
- ✅ Perform OCR using Mistral OCR API
- ✅ Extract text in Markdown format
- ✅ Support for images extraction
- ✅ Save results as JSON and text files

## Prerequisites

1. **Azure Subscription**: You need an active Azure subscription
2. **Azure AI Foundry Project**: Create a project in one of these regions:
   - East US
   - West US3
   - South Central US
   - West US
   - North Central US
   - East US 2
   - Sweden Central

3. **Mistral OCR Deployment**: Deploy the Mistral OCR model in Azure AI Foundry

## Setup Instructions

### 1. Deploy Mistral OCR in Azure AI Foundry

1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Create or select a project
3. Navigate to the Model Catalog
4. Search for "Mistral OCR" or "mistral-ocr-2503"
5. Click **Deploy** and select **Pay-as-you-go**
6. Complete the deployment (takes less than 1 minute)
7. Copy your **Endpoint URL** and **API Key** from the deployment page

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install requests
```

### 3. Configure Your Credentials

You can configure credentials in two ways:

**Option 1: Environment Variables (Recommended)**

```bash
export AZURE_OCR_ENDPOINT="https://your-endpoint.eastus2.models.ai.azure.com"
export AZURE_OCR_API_KEY="your-api-key-here"
```

**Option 2: Edit the Script**

Edit `mistral_ocr_example.py` and replace the placeholder values:

```python
AZURE_ENDPOINT = "https://your-endpoint.eastus2.models.ai.azure.com"
AZURE_API_KEY = "your-api-key-here"
```

## Usage

### Basic Usage

```bash
python mistral_ocr_example.py
```

Make sure you have a PDF file named `sample_document.pdf` in the same directory, or update the `PDF_PATH` variable in the script.

### Using as a Library

```python
from mistral_ocr_example import MistralOCR

# Initialize client
ocr_client = MistralOCR(
    endpoint="https://your-endpoint.eastus2.models.ai.azure.com",
    api_key="your-api-key"
)

# Perform OCR
result = ocr_client.perform_ocr("document.pdf")

# Extract text only
text = ocr_client.extract_text_only(result)
print(text)

# Save results
ocr_client.save_results(result, "output.json")
```

### Advanced Example

```python
# Process multiple PDFs
import glob
from mistral_ocr_example import MistralOCR

ocr_client = MistralOCR(endpoint=ENDPOINT, api_key=API_KEY)

for pdf_file in glob.glob("*.pdf"):
    print(f"Processing: {pdf_file}")
    result = ocr_client.perform_ocr(pdf_file, include_images=False)
    
    output_name = pdf_file.replace(".pdf", "_ocr.json")
    ocr_client.save_results(result, output_name)
```

## API Response Format

The OCR API returns results in this structure:

```json
{
  "id": "ocr-xxxxx",
  "object": "ocr.completion",
  "created": 1234567890,
  "model": "mistral-ocr-2503",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "# Document Title\n\nExtracted text in Markdown format..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 5678,
    "total_tokens": 6912
  }
}
```

## Supported Features

### Document Types
- ✅ PDF files (up to 1,000 pages, 50MB max)
- ✅ Scanned documents
- ✅ Complex layouts (tables, equations, figures)
- ✅ Multilingual documents (99+ languages)

### Output Format
- Markdown format with preserved structure
- Tables extracted as Markdown tables
- Mathematical equations in LaTeX format
- Embedded images (when `include_image_base64=True`)

### Performance
- Processes thousands of pages per minute
- Lightweight and fast inference
- Enterprise-grade security with network isolation

## Limitations

- Maximum file size: 50MB
- Maximum pages: 1,000 pages per document
- Requires base64 encoding (no direct URL support in Azure deployment)
- Pay-as-you-go pricing based on token usage

## Pricing

Pricing is based on token usage:
- Prompt tokens (input)
- Completion tokens (output)

Check the Azure AI Foundry portal for current pricing details.

## Troubleshooting

### Common Issues

**Issue: Getting `null` or empty responses**
- Ensure PDF is properly base64 encoded
- Check that file size is under 50MB
- Verify the PDF is not corrupted
- Try with a simple single-page PDF first

**Issue: Authentication errors**
- Verify your API key is correct
- Check that the endpoint URL includes the full path
- Ensure your Azure subscription is active

**Issue: Timeout errors**
- Increase the timeout value for large documents
- Try processing smaller documents first
- Check your network connection

**Issue: Rate limiting**
- The API has rate limits based on your deployment tier
- Implement retry logic with exponential backoff
- Consider batch processing with delays

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Mistral OCR Model Card](https://ai.azure.com/catalog/models/mistral-ocr-2503)
- [Image-to-Text Models Guide](https://learn.microsoft.com/azure/ai-foundry/how-to/use-image-models)

## License

This example code is provided as-is for demonstration purposes.

## Contributing

Feel free to submit issues and enhancement requests!
