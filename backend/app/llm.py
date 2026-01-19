from langchain_google_vertexai import ChatVertexAI
from app.config import get_settings

settings = get_settings()

def get_llm(temperature: float | None = None):
    return ChatVertexAI(
        model_name=settings.LLM_MODEL,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_output_tokens=settings.LLM_MAX_TOKENS,
        project=settings.GCP_PROJECT_ID,
        location=settings.GCP_LOCATION,
    )