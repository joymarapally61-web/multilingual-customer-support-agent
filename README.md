# Multilingual Customer Support AI Agent

A starter web app for customer support in Telugu, Hindi and English, powered by Gemini.

## Included
- Responsive chat UI with language selection.
- Server-side Gemini API call; the API key is never sent to the browser.
- Conversation context held in the browser for the current session.
- Browser speech recognition input and optional speech-synthesis output.
- Configurable JSON knowledge base.
- Basic per-process request throttling and security response headers.
- Dockerfile and Render blueprint for deployment.
- Starter API tests.

## Run locally
1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set your Gemini API key.
5. Run `uvicorn backend.main:app --reload`.
6. Open http://127.0.0.1:8000.

Never commit `.env`. Configure `ALLOWED_ORIGINS` as a comma-separated list only if the frontend is hosted on a different origin.

## Run tests
Install dev dependencies with `pip install -r requirements-dev.txt`, then run `pytest`.

## Deploy on Render
1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint** and select this repository.
3. Render reads `render.yaml` and builds the Docker image.
4. Add your Gemini API key as the secret environment variable `GEMINI_API_KEY`.
5. Deploy and open the generated service URL. Check `/health`.

Do not paste your API key into source code, GitHub files, browser JavaScript, screenshots or chat messages. Enter it only in the hosting provider's secret environment-variable settings.

## Important limitations — not production-ready yet
- Browser speech recognition and voices vary by browser/device. This is not Gemini Live streaming audio.
- Order lookup, refund requests, ticket creation and human handoff are not connected. Do not claim these actions work.
- There is no customer login, verified identity, database, tenant isolation or admin dashboard yet.
- The in-memory rate limit is per process and is not a substitute for a shared production rate limiter.
- Before production, implement authentication, server-side authorization, tenant-scoped data access, real business APIs, persistent ticketing, audit logs, privacy/retention controls, monitoring and security testing.
- Replace the sample knowledge base with the business's approved policies. The model must not be treated as the source of truth for order or payment state.

## Environment variables
- `GEMINI_API_KEY` — required server-side secret.
- `GEMINI_MODEL` — optional model override (default: `gemini-2.5-flash`).
- `ALLOWED_ORIGINS` — optional comma-separated frontend origins.
- `CHAT_RATE_LIMIT_PER_MINUTE` — optional per-IP in-memory limit (default 20).
