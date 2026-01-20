# carrefour-assistant
Chrome extension assistant analyzing user webpage in view to propose a better navigation and shopping experience
# Carrefour AI Assistant - Chrome Extension

This project is an intelligent agent for the Carrefour.fr website, designed to help users do their grocery shopping, find recipes, and manage their cart.

## Architecture

The project is divided into two main parts:

1. **Extension Chrome (`/extension`)** : User interface injected into the browser.
2. **Backend API (`/backend`)** : FastAPI using LangChain and Google Vertex AI (Gemini)

## Technical Stack

- **LLM** : Google Gemini Pro (via Vertex AI)
- **Orchestration** : LangChain
- **Observability** : Langfuse (Tracing & Monitoring)
- **Backend** : Python / FastAPI
- **Frontend** : Javascript (Chrome Extension Manifest V3)

## Configuration

### Prerequisites

1. A Google Cloud Platform project with Vertex AI enabled.
2. A Langfuse account (Cloud or Self-hosted).

### Backend installation

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure the file `.env` :
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

## Developpement

Launch the server: uvicorn app.main:app --reload