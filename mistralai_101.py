# %%
import os
from mistralai import Mistral
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
azure_endpoint = AZ_MISTRAL_DOC_AI_2505_ENDPOINT

print(f"Using model: {model}")
print(f"Using Azure endpoint: {azure_endpoint}")

# %%

client = Mistral(
    api_key=api_key,
    server_url=azure_endpoint,
)
# %%
ocr_response = client.ocr.process(
    model=model,
    document={
        "type": "document_url",
        "document_url": "https://arxiv.org/pdf/2201.04234"
    }
)
# %%
client.ocr.process()