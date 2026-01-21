# Backend – AI Assistant API

This folder contains the **FastAPI backend** responsible for:
- receiving page context from the extension
- generating proactive suggestions
- answering user questions using an AI agent
- enforcing strict context grounding

---

## Core Design Principles

- **Stateless API** (Cloud Run friendly)
- **Context-bounded reasoning** (anti-hallucination)
- **Deterministic fallbacks**
- **LLM observability**

---

## Project Structure

~~~
backend/
├── app/
│   ├── app.py            # FastAPI routes (API layer)
│   ├── agent/
│   │   └── graph.py      # LangGraph agent definition (reasoning & routing)
│   ├── llm.py            # LLM instantiation (Vertex AI / Gemini)
│   ├── extractors.py     # Context compaction & robust JSON parsing
│   ├── suggestions.py   # Rule-based proactive suggestions
│   ├── schemas.py       # Pydantic data models
│   └── config.py        # Environment-based configuration
├── main.py               # Uvicorn entrypoint
├── requirements.txt      # Python dependencies
└── README.md             # Backend documentation
~~~

---

## Agent Architecture (LangGraph)

The AI agent is implemented as a **state graph**, not a linear chain.

### Agent States

```python
AgentState = {
  messages: conversation history,
  context: page context,
  suggestions: proactive prompts,
  final_response: assistant answer
}
```

### Routing Logic

- If no user message → proactive_analysis
- If user message exists → chatbot

This clean separation allows independent evolution of proactive and reactive behaviors.

### Anti-Hallucination Strategy

- Page context injected into system prompt
- Explicit instruction to not infer missing information
- No external browsing
- No persistent memory

This ensures responses remain grounded in visible data only.

### Observability

Langfuse is used to trace:

- LLM calls
- latency per node
- token usage
- errors and fallbacks

### Running locally

```bash
cd backend
python main_local.py
```
