# %%
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

AZ_DEV_DAP_AI_001_AIS_URL=os.getenv("AZ_DEV_DAP_AI_001_AIS_URL", "")
if AZ_DEV_DAP_AI_001_AIS_URL:
    AZ_DEV_DAP_AI_001_AIS_ENDPOINT=AZ_DEV_DAP_AI_001_AIS_URL + "/models"
    AZ_MISTRAL_SMALL_2503_ENDPOINT=AZ_DEV_DAP_AI_001_AIS_URL + "/openai/v1/"
    AZ_MISTRAL_MEDIUM_2505_ENDPOINT=AZ_DEV_DAP_AI_001_AIS_URL + "/openai/v1/"
    AZ_MISTRAL_DOC_AI_2505_ENDPOINT=AZ_DEV_DAP_AI_001_AIS_URL + "/providers/mistral/azure/ocr"

AZ_DEV_DAP_AI_001_AIS_KEY =os.getenv("AZ_DEV_DAP_AI_001_AIS_KEY", "")
if AZ_DEV_DAP_AI_001_AIS_KEY:
    AZ_MISTRAL_SMALL_2503_KEY=AZ_DEV_DAP_AI_001_AIS_KEY
    AZ_MISTRAL_DOC_AI_2505_KEY=AZ_DEV_DAP_AI_001_AIS_KEY
    AZ_MISTRAL_MEDIUM_2505_KEY=AZ_DEV_DAP_AI_001_AIS_KEY

AZ_MISTRAL_DOC_AI_2505_NAME=os.getenv("AZ_MISTRAL_DOC_AI_2505_NAME", "mistral-document-ai-2505")
AZ_MISTRAL_SMALL_2503_NAME=os.getenv("AZ_MISTRAL_SMALL_2503_NAME", "mistral-small-2503")
AZ_MISTRAL_MEDIUM_2505_NAME=os.getenv("AZ_MISTRAL_MEDIUM_2505_NAME", "mistral-medium-2505")

for key, value in os.environ.items():
    if key.startswith("AZ"):
        print(f"{key}={value}")

# %%
model_name = AZ_MISTRAL_MEDIUM_2505_NAME
endpoint = AZ_MISTRAL_MEDIUM_2505_ENDPOINT
api_key = AZ_MISTRAL_MEDIUM_2505_KEY
deployment_name = model_name

client = OpenAI(
    base_url=f"{endpoint}",
    api_key=api_key
)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

print(completion.choices[0].message)

