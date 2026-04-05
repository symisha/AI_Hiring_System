from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from app.database.db_connection import supabase_url, supabase_key

security = HTTPBearer(auto_error=True)
supabase = create_client(supabase_url, supabase_key)

async def auth_middleware(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = (credentials.credentials or "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        user_response = supabase.auth.get_user(token)
        user = getattr(user_response, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )

def get_current_user_id(user=Depends(auth_middleware)) -> str:
    return user.id