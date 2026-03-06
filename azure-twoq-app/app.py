import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

app = FastAPI()

class Question(BaseModel):
    question: str

# Create Azure client properly
client = AzureOpenAI(
api_key=os.getenv("AZURE_OPENAI_KEY"),
api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.post("/ask")
def ask_ai(payload: Question):
    try:
        response = client.responses.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            input=payload.question
        )
        #messages=[
        #{"role": "system", "content": "You are a helpful assistant."},
        #{"role": "user", "content": payload.question}
        #],
        #temperature=0.3
        #)

        return {"answer": response.output_text}

    except Exception as e:
        return {"error": str(e)}