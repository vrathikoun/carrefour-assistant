from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Google Cloud / Vertex AI
    GOOGLE_APPLICATION_CREDENTIALS: str
    GCP_PROJECT_ID: str = "carrefour-genai-project"
    GCP_LOCATION: str = "europe-west1"
    
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