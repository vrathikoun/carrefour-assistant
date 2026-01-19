from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- App ---
    APP_ENV: str = "development"  # development | production
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # CORS
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # --- Google Cloud / Vertex AI ---
    # Optional because on Cloud Run / GCE you may rely on ADC without a file path.
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCP_PROJECT_ID: str = "viphone-tuto"
    GCP_LOCATION: str = "europe-west1"

    # --- LLM ---
    LLM_MODEL: str = "gemini-1.5-pro"
    LLM_MAX_OUTPUT_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.2
    LLM_CONVERT_SYSTEM_MESSAGE_TO_HUMAN: bool = True
    LLM_VERBOSE: bool = False
    ENABLE_LLM_SUGGESTIONS: bool = False


    # --- Langfuse (Observability) ---
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()