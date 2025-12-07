from fastapi import Header, HTTPException
from typing import Optional
from ..database.supabase_client import supabase


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validates the 'Authorization: Bearer <token>' header using supabase
    """
    # Check header exists
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Check the format
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format. Use 'Bearer <token>'.")
    
    # Extract token
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing.")
    
    try:
        result = supabase.auth.get_user(token)
        user = None
        
        if hasattr(result, "user") and result.user:
            user = result.user
        elif isinstance(result, dict) and result.get("user"):
            user = result["user"]
            
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user
    
    except Exception:
        raise HTTPException(
            status_code=401, detail="Invalid or expired token."
        )