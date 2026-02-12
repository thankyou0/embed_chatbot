import uvicorn
import logging
from app.core.config import settings

if __name__ == "__main__":
    # Disable uvicorn access logs from terminal
    logging.getLogger("uvicorn.access").disabled = True
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_config=None,  # Use our custom logging setup
    )

