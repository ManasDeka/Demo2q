from dotenv import load_dotenv
import os
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
api_key=os.getenv("AZURE_OPENAI_KEY"),
api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

resp = client.responses.create(
model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
input="Say hello in one short sentence."
)

print(resp.output_text)