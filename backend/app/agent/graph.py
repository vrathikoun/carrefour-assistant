from typing import TypedDict, List, Annotated
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.schemas import PageContext
from app.llm import get_llm
from app.extractors import compact_context, extract_json_object
from app.suggestions import suggestions_rule_based

# --- 1) State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    context: PageContext
    suggestions: List[str]
    final_response: str
    _suggestions_source: str

# --- 2) LLM ---
llm = get_llm()

# --- 3) Nodes ---
def analyze_context_node(state: AgentState):
    context = state["context"]

    system = SystemMessage(content="Return STRICT valid JSON only. No extra text.")
    user_prompt = f"""
You generate proactive suggestions for a Carrefour in-page assistant.

Rules:
- Use product names from the context whenever possible.
- Avoid generic templates like "compare top 3" or "cheapest per kg" unless it truly matches the page.
- Produce 3 suggestions with different intents:
  1) Budget/value
  2) Health/composition (or allergy/diet)
  3) Usage/recipe or practical choice

Return STRICT JSON only:
{{"suggestions": ["...", "...", "..."]}}

PAGE CONTEXT:
{compact_context(context)}
""".strip()

    response = llm.invoke([system, HumanMessage(content=user_prompt)])

    try:
        data = extract_json_object(response.content)
        suggestions = data.get("suggestions", [])
        if not isinstance(suggestions, list) or not all(isinstance(s, str) for s in suggestions):
            raise ValueError("Invalid suggestions format")

        suggestions = [s.strip() for s in suggestions if s.strip()][:3]
        if not suggestions:
            raise ValueError("Empty suggestions")

        # watermark debug (optional)
        suggestions = [f"🤖 {s}" for s in suggestions]

        return {"suggestions": suggestions, "_suggestions_source": "llm"}

    except Exception as e:
        import traceback
        print("[suggestions] LLM failed -> fallback rules")
        print("[suggestions] raw model output:", repr(response.content))
        traceback.print_exc()
        return {"suggestions": suggestions_rule_based(context), "_suggestions_source": "llm_fallback"}


def chat_node(state: AgentState):
    """Answer user question using compact in-page context."""
    context = state["context"]
    messages = state["messages"]

    system_content = (
    "Tu es l'assistant shopping Carrefour.\n"
    "Tu as accès à un CONTEXTE extrait de la page carrefour.fr.\n\n"
    "Règles:\n"
    "1) Pour tout ce qui est PRIX / DISPONIBILITÉ / PROMOS / PRODUITS VISIBLES: "
    "utilise STRICTEMENT le contexte. Si l'info n'y est pas, dis-le.\n"
    "2) Pour des IDÉES DE RECETTES / USAGES / CONSEILS CUISINE: "
    "tu peux utiliser des connaissances générales (sans inventer de prix ou de promos Carrefour).\n"
    "3) Pour recommander des PRODUITS SIMILAIRES: "
    "utilise en priorité la section 'Produits recommandés / similaires' si présente dans le contexte. "
    "Sinon, propose des critères de substitution et demande à l'utilisateur d'ouvrir/scroll la section recommandée.\n"
    "4) Sois concis, structuré (bullet points), et utile.\n\n"
    f"{compact_context(context)}\n"
)


    messages_with_system = [SystemMessage(content=system_content)] + messages
    response = llm.invoke(messages_with_system)

    return {"final_response": response.content}


# --- 4) Routing ---
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
        "proactive_analysis": "proactive_analysis",
    },
)

workflow.add_edge("proactive_analysis", END)
workflow.add_edge("chatbot", END)

app_graph = workflow.compile()
