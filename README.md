# Flask LLM Demo

A small Flask app that uses an OpenAI-compatible chat model for both chat and search. The project includes a simple browser UI, health/config endpoints, and a lightweight test suite.

## What It Does

- answers questions through `POST /chat`
- returns LLM-generated search-style results through `GET /search`
- exposes `/health`, `/stats`, and `/config-check`
- supports OpenAI-compatible providers, including OpenRouter

This project is now LLM-only:

- no local knowledge base
- no embeddings
- no FAISS index
- no ingestion pipeline

## Project Structure

```text
flask_rag/
├── app/
│   ├── services/
│   │   ├── assistant.py
│   │   ├── diagnostics.py
│   │   └── llm.py
│   ├── static/
│   │   ├── app.css
│   │   └── app.js
│   ├── templates/
│   │   └── index.html
│   ├── config.py
│   ├── routes.py
│   ├── run.py
│   ├── serve.py
│   ├── wsgi.py
│   └── __init__.py
├── tests/
│   └── test_app.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

Install dependencies:

```powershell
cd f:\Python_learning\flask_rag
.\venv\Scripts\pip.exe install -r requirements.txt
```

Create `.env` from `.env.example` and set your provider values.

Example:

```env
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=5000
LOG_LEVEL=INFO

OPENAI_API_KEY=your_provider_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_CHAT_MODEL=openai/gpt-4o
OPENROUTER_SITE_URL=http://localhost:5000
OPENROUTER_APP_NAME=flask_rag
```

## Run

Development:

```powershell
.\venv\Scripts\python.exe app\run.py
```

Production-style local serving:

```powershell
.\venv\Scripts\python.exe app\serve.py
```

## Endpoints

- `/` UI
- `/health` health check
- `/stats` runtime mode and feature status
- `/config-check` safe runtime config visibility
- `/search?q=Dubai` LLM-backed search response
- `/chat` LLM-backed chat response

## Example Requests

Chat:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/chat -ContentType 'application/json' -Body '{"message":"What is Dubai?"}'
```

Search:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:5000/search?q=15*15"
```

## Tests

```powershell
cd f:\Python_learning\flask_rag
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

## Notes

- wrong or unclear input is instructed to return `"I don't know."`
- simple math can be answered directly by the model
- citations are currently disabled because there is no retrieval layer
