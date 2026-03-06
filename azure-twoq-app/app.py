import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ⛔ On Render, .env is NOT auto-loaded. Keep load_dotenv() only for local dev.
# If you still want it for local runs, uncomment the two lines below.
# from dotenv import load_dotenv
# load_dotenv()  # Will only have effect locally where a .env file exists.

from openai import AzureOpenAI

app = FastAPI(title="TwoQ Backend", version="1.0.0")

# ----- Models -----
class Question(BaseModel):
    question: str

# ----- CORS -----
# During initial bring-up, allow all. Later, restrict to your frontend URL:
# allow_origins=["https://<your-frontend>.onrender.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # TODO: tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Utilities -----
def get_azure_client() -> AzureOpenAI:
    """
    Create a new Azure OpenAI client using environment variables.
    Fails fast with a helpful error if any variable is missing.
    """
    key = os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not key or not api_version or not endpoint:
        missing = []
        if not key: missing.append("AZURE_OPENAI_KEY (or AZURE_OPENAI_API_KEY)")
        if not api_version: missing.append("AZURE_OPENAI_API_VERSION")
        if not endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
        raise HTTPException(
            status_code=500,
            detail=f"Missing environment variables: {', '.join(missing)}"
        )
    return AzureOpenAI(api_key=key, api_version=api_version, azure_endpoint=endpoint)

def get_deployment_name() -> str:
    dep = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not dep:
        raise HTTPException(status_code=500, detail="Missing AZURE_OPENAI_DEPLOYMENT")
    return dep

# ----- Basic routes -----
@app.get("/")
def root():
    return {"status": "ok", "message": "TwoQ backend is running."}

@app.get("/healthz")
def healthz():
    return {"ok": True}

# ----- Main API -----
@app.post("/ask")
def ask_ai(payload: Question):
    try:
        client = get_azure_client()
        deployment = get_deployment_name()

        # Using the new Responses API on Azure OpenAI SDK
        resp = client.responses.create(
            model=deployment,
            input=payload.question,
            # If you prefer Chat format, switch to client.chat.completions.create(...)
            # and pass messages=[{"role":"user","content": payload.question}]
        )

        # The SDK may return text in different shapes; normalize to string
        answer_text = getattr(resp, "output_text", None)
        if not answer_text:
            # Fallback: try common shapes if output_text not present
            try:
                answer_text = resp.choices[0].message.content  # chat style
            except Exception:
                answer_text = str(resp)

        return {"answer": answer_text}

    except HTTPException:
        # re-raise helpful config errors from above
        raise
    except Exception as e:
        # Bubble up a concise error for your UI to show
        raise HTTPException(status_code=500, detail=f"AI call failed: {e}")