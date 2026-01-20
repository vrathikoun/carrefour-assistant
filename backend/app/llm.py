import os
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings

settings = get_settings()

if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS

def get_llm(temperature: float | None = None) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE if temperature is None else temperature,
        max_output_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
        project=settings.GCP_PROJECT_ID,
        location=settings.GCP_LOCATION,
        convert_system_message_to_human=settings.LLM_CONVERT_SYSTEM_MESSAGE_TO_HUMAN,
        verbose=settings.LLM_VERBOSE,
    )
