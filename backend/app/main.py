from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler
from app.schemas import ChatRequest, ChatResponse
from app.agent.graph import app_graph
from app.config import get_settings

app = FastAPI(title="Carrefour AI Assistant Backend")
settings = get_settings()

# Configuration CORS pour autoriser l'extension Chrome
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, remplacez par l'ID de l'extension: "chrome-extension://<ID>"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "service": "Carrefour AI Assistant"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Configuration Langfuse pour le tracing de cette requête
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST
    )
    
    try:
        # Construction du prompt système avec le contexte de la page
        context_str = f"L'utilisateur est sur la page : {request.context.title} ({request.context.url}).\n"
        # Préparation de l'input pour LangGraph
        inputs = {
            "context": request.context,
            "messages": [HumanMessage(content=request.message)] if request.message else [],
            "suggestions": [],
            "final_response": ""
        }
        
        # Invocation du graphe avec callback Langfuse
        result = await app_graph.ainvoke(inputs, config={"callbacks": [langfuse_handler]})
        
        return ChatResponse(
            response=result.get("final_response", ""),
            suggestions=result.get("suggestions", [])
        )
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))