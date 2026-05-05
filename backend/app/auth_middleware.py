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
