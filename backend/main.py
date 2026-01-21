import os
import uvicorn
from app.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", settings.PORT))  # Cloud Run provides PORT=8080
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",          # MUST be 0.0.0.0 on Cloud Run
        port=port,
        reload=False,            # reload must be False in containers
        log_level="info",
    )