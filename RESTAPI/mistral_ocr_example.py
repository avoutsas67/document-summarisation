"""
Azure AI Foundry Mistral Document AI (Mistral OCR) Example
This script demonstrates how to use Mistral OCR to extract text from a PDF file
"""

import base64
import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

AZ_DEV_DAP_AI_001_AIS_URL=os.getenv("AZ_DEV_DAP_AI_001_AIS_URL", "")
if AZ_DEV_DAP_AI_001_AIS_URL:
     AZ_MISTRAL_DOC_AI_2505_ENDPOINT=AZ_DEV_DAP_AI_001_AIS_URL + "/providers/mistral/azure/ocr"

AZ_DEV_DAP_AI_001_AIS_KEY =os.getenv("AZ_DEV_DAP_AI_001_AIS_KEY", "")
if AZ_DEV_DAP_AI_001_AIS_KEY:
    AZ_MISTRAL_DOC_AI_2505_KEY=AZ_DEV_DAP_AI_001_AIS_KEY
    
AZ_MISTRAL_DOC_AI_2505_NAME=os.getenv("AZ_MISTRAL_DOC_AI_2505_NAME", "mistral-document-ai-2505")


api_key = AZ_DEV_DAP_AI_001_AIS_KEY
model = AZ_MISTRAL_DOC_AI_2505_NAME
endpoint = AZ_MISTRAL_DOC_AI_2505_ENDPOINT

# %%
class MistralOCR:
    """
    A client for interacting with Azure AI Foundry Mistral OCR API
    """
    
    def __init__(self, endpoint: str, api_key: str):
        """
        Initialize the Mistral OCR client
        
        Args:
            endpoint: Azure AI Foundry endpoint URL (e.g., https://your-endpoint.eastus2.models.ai.azure.com)
            api_key: Your Azure API key
        """
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.model = "mistral-ocr-2503"
        self.ocr_url = f"{self.endpoint}/v1/ocr"
    
    def encode_pdf_to_base64(self, pdf_path: str) -> str:
        """
        Read a PDF file and encode it to base64
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Base64 encoded string of the PDF
        """
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                base64_encoded = base64.b64encode(pdf_bytes).decode('utf-8')
                return base64_encoded
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            raise Exception(f"Error encoding PDF: {str(e)}")
    
    def perform_ocr(self, pdf_path: str, include_images: bool = True) -> dict:
        """
        Perform OCR on a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            include_images: Whether to include extracted images in the response
            
        Returns:
            Dictionary containing the OCR results
        """
        # Encode the PDF to base64
        print(f"Encoding PDF: {pdf_path}")
        base64_pdf = self.encode_pdf_to_base64(pdf_path)
        
        # Create the request payload
        payload = {
            "model": self.model,
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}"
            },
            "include_image_base64": include_images
        }
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Make the API request
        print("Sending request to Mistral OCR...")
        try:
            response = requests.post(
                self.ocr_url,
                headers=headers,
                json=payload,
                timeout=120  # 2 minute timeout for large documents
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse and return the response
            result = response.json()
            print("OCR completed successfully!")
            return result
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise
    
    def save_results(self, ocr_result: dict, output_path: str):
        """
        Save OCR results to a file
        
        Args:
            ocr_result: The OCR result dictionary
            output_path: Path where to save the results
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_result, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")
    
    def extract_text_only(self, ocr_result: dict) -> str:
        """
        Extract only the text content from OCR results
        
        Args:
            ocr_result: The OCR result dictionary
            
        Returns:
            Extracted text as a string
        """
        try:
            # The response contains content in markdown format
            if 'choices' in ocr_result and len(ocr_result['choices']) > 0:
                content = ocr_result['choices'][0].get('message', {}).get('content', '')
                return content
            return ""
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""


def main():
    """
    Main function demonstrating the usage of Mistral OCR
    """
    # Configuration - Replace with your actual values
    AZURE_ENDPOINT = os.getenv("AZURE_OCR_ENDPOINT", "https://your-endpoint.eastus2.models.ai.azure.com")
    AZURE_API_KEY = os.getenv("AZURE_OCR_API_KEY", "your-api-key-here")
    
    # Input PDF file path
    PDF_PATH = "sample_document.pdf"  # Replace with your PDF file path
    
    # Output paths
    OUTPUT_JSON = "ocr_results.json"
    OUTPUT_TEXT = "extracted_text.md"
    
    # Initialize the OCR client
    print("Initializing Mistral OCR client...")
    ocr_client = MistralOCR(endpoint=AZURE_ENDPOINT, api_key=AZURE_API_KEY)
    
    # Check if PDF exists
    if not Path(PDF_PATH).exists():
        print(f"Error: PDF file not found at {PDF_PATH}")
        print("Please provide a valid PDF file path.")
        return
    
    try:
        # Perform OCR
        ocr_result = ocr_client.perform_ocr(
            pdf_path=PDF_PATH,
            include_images=True  # Set to False if you don't need images
        )
        
        # Save the full JSON response
        ocr_client.save_results(ocr_result, OUTPUT_JSON)
        
        # Extract and save text only
        extracted_text = ocr_client.extract_text_only(ocr_result)
        if extracted_text:
            with open(OUTPUT_TEXT, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"Extracted text saved to: {OUTPUT_TEXT}")
            
            # Print first 500 characters as a preview
            print("\n" + "="*50)
            print("TEXT PREVIEW (first 500 characters):")
            print("="*50)
            print(extracted_text[:500])
            if len(extracted_text) > 500:
                print("...")
        else:
            print("No text content found in OCR results")
        
        # Display usage statistics if available
        if 'usage' in ocr_result:
            print("\n" + "="*50)
            print("USAGE STATISTICS:")
            print("="*50)
            usage = ocr_result['usage']
            print(f"Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"Total tokens: {usage.get('total_tokens', 'N/A')}")
            
    except Exception as e:
        print(f"\nError during OCR processing: {e}")
        return


if __name__ == "__main__":
    main()
