# run.py - Entrypoint to start the FastAPI server

import uvicorn
from config import settings

if __name__ == "__main__":
    # Explicitly set port to 8000
    uvicorn.run(
        "main:app",  # main.py must contain `app = FastAPI()`
        host=settings.host,
        port=8000,
        reload=True if settings.debug else False,
        log_level=settings.log_level.lower()
    )
