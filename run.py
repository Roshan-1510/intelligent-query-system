import os
import uvicorn
from config import settings

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000)) 
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # <-- Disable reload in production
        log_level=settings.log_level.lower()
    )
