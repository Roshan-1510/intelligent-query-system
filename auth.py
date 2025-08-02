from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

# HTTP Bearer security scheme
security = HTTPBearer()

# Get API key from environment variable with fallback
def get_api_key() -> str:
    """Get API key from environment variable or use default"""
    api_key = os.environ.get("API_KEY", "7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9")
    if not api_key:
        raise ValueError("API_KEY environment variable is required")
    return api_key

async def verify_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify the API key from the Authorization header.
    
    Args:
        request: FastAPI request object
        credentials: HTTP authorization credentials
        
    Returns:
        The verified API key
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Check authentication scheme
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme. Bearer token required."
            )

        # Get expected API key
        expected_api_key = get_api_key()
        
        # Verify API key
        if credentials.credentials != expected_api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        return credentials.credentials
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )
