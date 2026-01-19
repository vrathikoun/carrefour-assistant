from typing import TypedDict, List, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from app.config import get_settings
from app.schemas import PageContext
from app.llm import get_llm


settings = get_settings()

# --- 1. Définition de l'État du Graphe ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    context: PageContext
    suggestions: List[str]
    final_response: str

# --- 2. Initialisation du LLM ---
llm = get_llm()

# --- 3. Nodes (Les étapes du raisonnement) ---

def analyze_context_node(state: AgentState):
    """Analyse la page pour générer des Smart Pre-prompts (Proactive)."""
    context = state["context"]
    
    prompt = f"""Tu es l'assistant intelligent Carrefour.
    Analyse le contexte de la page suivante :
    Type: {context.page_type}
    Titre: {context.title}
    Produits: {len(context.products) if context.products else 0} visible(s)
    Promos: {context.promos}
    
    Génère 3 questions courtes et pertinentes que l'utilisateur pourrait poser.
    Réponds STRICTEMENT au format JSON:
    {{"suggestions": ["question1", "question2", "question3"]}}
    Exemple: Quel est le prix au kg ? | C'est du bio ? | Idée recette ?
    """
    
    msg = HumanMessage(content=prompt)
    response = llm.invoke([msg])
    try:
        data = json.loads(response.content)
        suggestions = data.get("suggestions", [])
    except Exception:
        suggestions = [s.strip() for s in response.content.split("|") if s.strip()]
    return {"suggestions": suggestions}

def chat_node(state: AgentState):
    """Répond à la question de l'utilisateur en utilisant le contexte."""
    context = state["context"]
    messages = state["messages"]
    
    # Injection du contexte dans le prompt système
    system_content = f"""Tu es l'assistant shopping Carrefour.
    CONTEXTE PAGE:
    Titre: {context.title}
    URL: {context.url}
    Type: {context.page_type}
    """
    
    if context.product:
        system_content += f"\nPRODUIT ACTUEL: {context.product}"
    if context.products:
        system_content += f"\nLISTE PRODUITS: {context.products}"
    if context.promos:
        system_content += f"\nPROMOS: {context.promos}"
    if context.bodyText:
        system_content += f"\nCONTENU TEXTE: {context.bodyText[:1000]}..."

    system_content += "\nRéponds de façon utile, concise et commerciale."

    messages_with_system = [SystemMessage(content=system_content)] + messages
    
    response = llm.invoke(messages_with_system)
    return {"final_response": response.content}

# --- 4. Construction du Graphe ---

workflow = StateGraph(AgentState)

workflow.add_node("proactive_analysis", analyze_context_node)
workflow.add_node("chatbot", chat_node)

def route_request(state: AgentState):
    if state.get("messages") and len(state["messages"]) > 0:
        return "chatbot"
    return "proactive_analysis"

workflow.set_conditional_entry_point(
    route_request,
    {
        "chatbot": "chatbot",
        "proactive_analysis": "proactive_analysis"
    }
)

workflow.add_edge("proactive_analysis", END)
workflow.add_edge("chatbot", END)

app_graph = workflow.compile()