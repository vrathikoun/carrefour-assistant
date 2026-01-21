import os
import uvicorn

from app.config import get_settings

settings = get_settings()


def main() -> None:
    """
    Run FastAPI locally with:
        python main.py

    Swagger:
        http://localhost:8000/docs
    """
    # In local dev, it's common to force reload=True.
    # In Cloud Run / Docker, reload MUST be False.
    reload = settings.RELOAD and (settings.APP_ENV.lower() != "production")

    uvicorn.run(
        "app.app:app",               # points to backend/app/app.py -> app = FastAPI(...)
        host=settings.HOST,
        port=settings.PORT,
        reload=reload,
        log_level="info",
        # Optional: if you're on Windows / some environments, this avoids reload issues.
        # reload_dirs=["."],
    )


if __name__ == "__main__":
    main()