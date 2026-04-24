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
async def auth_middleware(request: Request, call_next, credentials: HTTPAuthorizationCredentials = Depends(security)):
    print(f"DEBUG: Middleware received request for {request.url.path}") # <--- ADD THIS
    
    path = request.url.path
    
    # BROAD BYPASS CHECK
    # This catches /ws/interview, /ws/interview/, and even /interview/ws
    is_websocket = "ws/interview" in path or "/ws/" in path
    is_static = any(path.startswith(p) for p in ["/interview.html", "/static/", "/public/"])
    is_api_bypass = any(path.startswith(p) for p in ["/services/get-test", "/services/submit-test", "/services/interview-link/validate"])

    if is_websocket or is_static or is_api_bypass:
        print(f"DEBUG: ✅ Bypassing auth for {path}")
        return await call_next(request)

    # 2. THE RECRUITER CHECK: 403 status code prevents the browser popup
    if not credentials:
        raise HTTPException(status_code=403, detail="Recruiter login required")
    
    token = credentials.credentials
    try:
        # Assuming you have your supabase client imported
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid session")
    
    
def get_current_user_id(user=Depends(auth_middleware)) -> str:
    return user.id