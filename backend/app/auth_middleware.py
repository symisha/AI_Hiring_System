from fastapi import Request, HTTPException, status
from supabase import create_client
from app.database.db_connection import supabase_url, supabase_key

supabase = create_client(supabase_url, supabase_key)

# The "Public" whitelist - these NEVER check for tokens
bypass_paths = [
    "/docs",                               # Allow API documentation
    "/openapi.json",                       # Required for docs
    "/static/",
    "/public/"  
    "/interview.html",
    "/services/interview-link/validate",
    "/ws/interview",  # WebSocket handshake
    "/services/get-test",
    "/services/submit-test",
<<<<<<< Updated upstream
    
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
=======
    "/favicon.ico",
    "/",
    "/routes/apply/form",
]

async def auth_middleware(request: Request, call_next):
    path = request.url.path
    
    # 1. Check bypass list
    # Matches exact paths or prefixes like /static/
    if any(path == p or path.startswith(("/static/", "/public/")) for p in bypass_paths):
        return await call_next(request)

    # 2. Extract Bearer Token manually (since we are in middleware)
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # If it's a GET request to a route not in bypass, it's likely a recruiter page
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing or invalid bearer token"
        )

    token = auth_header.split(" ")[1].strip()

    # 3. Your original Supabase validation logic
    try:
        user_response = supabase.auth.get_user(token)
        user = getattr(user_response, "user", None)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Store user in state so get_current_user_id can still find it
        request.state.user = user
        return await call_next(request)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )

# Dependency to get current user from request.state
from fastapi import Request
def get_current_user(request: Request):
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=403, detail="User not authenticated")
    return user
>>>>>>> Stashed changes
