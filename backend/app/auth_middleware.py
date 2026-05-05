from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from app.database.db_connection import supabase_url, supabase_key
from fastapi import Request # Add this import at the top

security = HTTPBearer(auto_error=False)
supabase = create_client(supabase_url, supabase_key)
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

bypass_paths = [
    # --- Assessment Flow ---
    "/services/get-test",
    "/services/submit-test",
    
    # --- Interview Flow (Candidates) ---
    "/interview.html",                     # The static page
    "/services/interview-link/validate",   # Token verification endpoint
    "/ws/interview",                       # THE CRITICAL FIX: WebSocket connection
    "/routes/apply/form",
    # --- Optional: Asset folders (if your HTML needs JS/CSS) ---
    "/static/",                            
    "/public/"
]
from fastapi import Request, HTTPException, status
from supabase import create_client
import os

# Ensure these match your actual config import
from app.database.db_connection import supabase_url, supabase_key

supabase = create_client(supabase_url, supabase_key)

async def auth_middleware(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing or invalid token"
        )

    token = auth_header.split(" ")[1].strip()

    try:
        # Get the user from Supabase
        user_response = supabase.auth.get_user(token)
        user = getattr(user_response, "user", None)
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # VERY IMPORTANT: 
        # Return just the user.id if your DB queries expect a string, 
        # or return the whole user object. 
        # Based on your previous code, let's return the whole object.
        return user

    except Exception as e:
        print(f"Auth Error: {e}") # This will show in your terminal
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
    
def get_current_user_id(user=Depends(auth_middleware)) -> str:
    return user.id