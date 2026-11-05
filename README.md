# Multilingual Customer Support AI Agent

A starter web application for customer support in Telugu, Hindi and English, powered by Gemini.

## Architecture

- `frontend/`: responsive chat interface with language selection and browser speech input/output.
- `backend/`: FastAPI server; calls Gemini from the server so the API key is never exposed to the browser.
- `knowledge_base/`: business-specific FAQs and policies.
- `tests/`: basic API tests.

## Requirements

- Python 3.10+
- A Gemini API key from Google AI Studio

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
4. Start the server: `uvicorn backend.main:app --reload`
5. Open http://127.0.0.1:8000

Do not commit `.env`. The included order/refund/ticket functions are DEMO stubs and must be connected to authenticated business systems before real customer use.

## Important production work

- Replace demo data and policies with verified business data.
- Add customer authentication and verify order ownership server-side.
- Connect real order, refund and ticket APIs; require authorization for sensitive actions.
- Add rate limits, abuse protection, audit logs, retention controls and monitoring.
- Configure CORS for your actual frontend domain.
- Review privacy, consent and applicable Indian data-protection requirements.
- Browser Web Speech support and Telugu/Hindi voices vary by browser and device. This is browser speech, not Gemini Live audio.

## Environment

See `.env.example`. Never put the Gemini key in frontend JavaScript.
