import os
import uvicorn
from config import settings

if __name__ == "__main__":
    port = int(os.environ["PORT"]) 
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
