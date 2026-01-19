from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler

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
    # Proactivité "in-context" rapide: rules-based
    suggestions = suggestions_rule_based(request.context)
    return SuggestionsResponse(suggestions=suggestions)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
    )

    inputs = {
        "context": request.context,
        "messages": [HumanMessage(content=request.message)] if request.message else [],
        "suggestions": [],
        "final_response": "",
    }

    try:
        result = await app_graph.ainvoke(inputs, config={"callbacks": [langfuse_handler]})
        return ChatResponse(
            response=result.get("final_response", ""),
            suggestions=result.get("suggestions", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))