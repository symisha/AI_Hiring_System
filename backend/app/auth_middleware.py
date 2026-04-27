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
    
    # --- Optional: Asset folders (if your HTML needs JS/CSS) ---
    "/static/",                            
    "/public/"
]


async def auth_middleware(request: Request, call_next):
    print(f"DEBUG: Middleware received request for {request.url.path}")
    path = request.url.path

    # BROAD BYPASS CHECK
    is_websocket = "ws/interview" in path or "/ws/" in path
    is_static = any(path.startswith(p) for p in ["/interview.html", "/static/", "/public/"])
    is_api_bypass = any(path.startswith(p) for p in ["/services/get-test", "/services/submit-test", "/services/interview-link/validate"])

    if is_websocket or is_static or is_api_bypass:
        print(f"DEBUG: ✅ Bypassing auth for {path}")
        return await call_next(request)

    # Extract Authorization header manually
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=403, detail="Recruiter login required")

    token = auth_header.split(" ", 1)[1]
    try:
        user_response = supabase.auth.get_user(token)
        request.state.user = user_response.user
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid session")

    return await call_next(request)
    
    

# Dependency to get current user from request.state
from fastapi import Request
def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=403, detail="User not authenticated")
    return user