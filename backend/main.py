import asyncio
import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .prompt import SYSTEM_PROMPT

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
KB_PATH = ROOT / "knowledge_base" / "faqs.json"
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

app = FastAPI(title="Multilingual Customer Support Agent", version="0.2.0")
allowed_origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "").split(",") if x.strip()]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")

# Lightweight per-process abuse guard for the starter app. Use a shared store (e.g. Redis)
# and trusted proxy configuration for multi-worker/production deployments.
_requests = defaultdict(deque)
RATE_LIMIT = int(os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "20"))


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    language: str = Field(default="auto", pattern="^(auto|en|te|hi)$")
    history: list[dict[str, str]] = Field(default_factory=list, max_length=20)


def load_knowledge_base() -> str:
    try:
        data = json.loads(KB_PATH.read_text(encoding="utf-8"))
        return json.dumps(data, ensure_ascii=False)
    except (OSError, json.JSONDecodeError):
        return "{}"


def check_rate_limit(request: Request) -> None:
    # Do not trust X-Forwarded-For unless the app is behind a configured trusted proxy.
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = _requests[ip]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many messages. Please wait a minute.")
    bucket.append(now)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "microphone=(self)"
    return response


@app.get("/")
def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


def generate_reply(payload: ChatRequest) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    language_hint = {
        "auto": "Detect the customer's latest language and mirror it.",
        "en": "Reply in English.",
        "te": "Reply in Telugu.",
        "hi": "Reply in Hindi.",
    }[payload.language]
    contents = []
    for item in payload.history[-20:]:
        role = item.get("role")
        text = item.get("text", "")
        if role in ("user", "model") and isinstance(text, str) and text.strip():
            contents.append(types.Content(role=role, parts=[types.Part(text=text[:2000])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=payload.message)]))
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT + "\n" + load_knowledge_base() + "\n" + language_hint,
            temperature=0.25,
            max_output_tokens=500,
        ),
    )
    return response.text or "I couldn't prepare a response. Please try again."


@app.post("/api/chat")
async def chat(payload: ChatRequest, request: Request):
    check_rate_limit(request)
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="The server administrator must configure the Gemini API key.")
    try:
        reply = await asyncio.to_thread(generate_reply, payload)
        return {"reply": reply}
    except Exception as exc:
        # Provider details and secrets are deliberately not sent to the browser.
        raise HTTPException(status_code=502, detail="The AI service is temporarily unavailable. Please try again.") from exc
