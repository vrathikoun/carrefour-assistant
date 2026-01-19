from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Google Cloud / Vertex AI
    GOOGLE_APPLICATION_CREDENTIALS: str
    GCP_PROJECT_ID: str = "viphone-tuto"
    GCP_LOCATION: str = "europe-west1"

    # LLM
    LLM_MODEL: str = "gemini-pro"
    LLM_MAX_OUTPUT_TOKENS: int = 1024
    LLM_temperature: float = 0.2
    LLM_convert_system_message_to_human: bool = True
    LLM_verbose: bool = True
    LLM_callbacks: list = []
    
    # Langfuse (Observability)
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # App
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()