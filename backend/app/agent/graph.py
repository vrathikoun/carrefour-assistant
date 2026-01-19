from typing import TypedDict, List, Annotated
import operator
import json

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.schemas import PageContext
from app.llm import get_llm
from app.extractors import compact_context
from app.suggestions import suggestions_rule_based

# --- 1) State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    context: PageContext
    suggestions: List[str]
    final_response: str

# --- 2) LLM ---
llm = get_llm()

# --- 3) Nodes ---
def analyze_context_node(state: AgentState):
    """
    Optional LLM suggestions.
    NOTE: In case of parsing errors, fallback to rule-based suggestions (fast & robust).
    """
    context = state["context"]

    system = SystemMessage(
        content="You MUST output STRICT valid JSON only. No extra text."
    )

    user_prompt = f"""
Generate 3 short, helpful suggested user questions for a Carrefour shopping assistant.
Return STRICT JSON:
{{"suggestions": ["...", "...", "..."]}}

PAGE CONTEXT (compact):
{compact_context(context)}
""".strip()

    response = llm.invoke([system, HumanMessage(content=user_prompt)])

    try:
        data = json.loads(response.content)
        suggestions = data.get("suggestions", [])
        if not isinstance(suggestions, list) or not all(isinstance(s, str) for s in suggestions):
            raise ValueError("Invalid suggestions format")
        # small cleanup
        suggestions = [s.strip() for s in suggestions if s.strip()][:3]
        if not suggestions:
            raise ValueError("Empty suggestions")
        return {"suggestions": suggestions}
    except Exception:
        # robust fallback
        return {"suggestions": suggestions_rule_based(context)}


def chat_node(state: AgentState):
    """Answer user question using compact in-page context."""
    context = state["context"]
    messages = state["messages"]

    system_content = (
        "Tu es l'assistant shopping Carrefour.\n"
        "Règle: utilise UNIQUEMENT le contexte fourni. "
        "Si l'information n'est pas dans le contexte, dis-le clairement.\n\n"
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
