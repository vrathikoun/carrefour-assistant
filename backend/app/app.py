import os
from langfuse import Langfuse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from langfuse.langchain import CallbackHandler

from app.config import get_settings
from app.schemas import (
    ChatRequest,
    ChatResponse,
    SuggestionsRequest,
    SuggestionsResponse,
)
from app.suggestions import suggestions_rule_based
from app.agent.graph import app_graph

settings = get_settings()

langfuse_client = None
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_BASE_URL"] = settings.LANGFUSE_BASE_URL

langfuse_client = Langfuse()


app = FastAPI(title="Carrefour AI Assistant Backend")

# CORS: OK pour démo. En prod, restreindre à l'ID extension.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "Carrefour AI Assistant"}


@app.post("/suggestions", response_model=SuggestionsResponse)
async def suggestions_endpoint(request: SuggestionsRequest):
    if settings.ENABLE_LLM_SUGGESTIONS:
        try:
            result = await app_graph.ainvoke(
                {
                    "context": request.context,
                    "messages": [],
                    "suggestions": [],
                    "final_response": "",
                    "_suggestions_source": "unknown",
                },
                config={"callbacks": [CallbackHandler()]},
            )
            sugg = result.get("suggestions", []) or suggestions_rule_based(request.context)
            src = result.get("_suggestions_source", "unknown")
            return SuggestionsResponse(suggestions=sugg, source=src)
        except Exception as e:
            print("[suggestions] graph error -> rules fallback:", repr(e))
            return SuggestionsResponse(suggestions=suggestions_rule_based(request.context), source="rules")
    else:
        return SuggestionsResponse(suggestions=suggestions_rule_based(request.context), source="rules")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Langfuse tracing (safe: if it fails, we still answer)
    callbacks = []
    try:
        callbacks = [CallbackHandler()]  # uses default Langfuse client initialized above
    except Exception:
        callbacks = []

    inputs = {
        "context": request.context,
        "messages": [HumanMessage(content=request.message)] if request.message else [],
        "suggestions": [],
        "final_response": "",
    }

    try:
        result = await app_graph.ainvoke(inputs, config={"callbacks": callbacks})
        return ChatResponse(
            response=result.get("final_response", ""),
            suggestions=result.get("suggestions", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))