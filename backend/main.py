import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .prompt import SYSTEM_PROMPT

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
KB_PATH = ROOT / "knowledge_base" / "faqs.json"

app = FastAPI(title="Multilingual Customer Support Agent")
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    language: str = Field(default="auto", pattern="^(auto|en|te|hi)$")
    history: list[dict[str, str]] = Field(default_factory=list, max_length=30)


def load_knowledge_base() -> str:
    try:
        return json.dumps(json.loads(KB_PATH.read_text(encoding="utf-8")), ensure_ascii=False)
    except (OSError, json.JSONDecodeError):
        return "{}"


@app.get("/")
def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/chat")
def chat(payload: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Server is missing GEMINI_API_KEY.")
    try:
        client = genai.Client(api_key=api_key)
        language_hint = {
            "auto": "Detect the customer's language.",
            "en": "Reply in English.",
            "te": "Reply in Telugu.",
            "hi": "Reply in Hindi.",
        }[payload.language]
        contents = []
        for item in payload.history[-20:]:
            role = item.get("role")
            text = item.get("text", "")
            if role in ("user", "model") and isinstance(text, str):
                contents.append(types.Content(role=role, parts=[types.Part(text=text[:4000])]))
        contents.append(types.Content(role="user", parts=[types.Part(text=payload.message)]))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT + "\n" + load_knowledge_base()
                + "\n" + language_hint,
                temperature=0.3,
            ),
        )
        return {"reply": response.text or "I couldn't prepare a response. Please try again."}
    except Exception as exc:
        # Avoid returning provider internals or secrets to the browser.
        raise HTTPException(status_code=502, detail="The AI service is temporarily unavailable.") from exc
