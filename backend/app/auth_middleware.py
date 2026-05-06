from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from supabase import create_client
from app.database.db_connection import supabase_url, supabase_key

# Initialize Supabase
supabase = create_client(supabase_url, supabase_key)

# Public routes (no auth required)
BYPASS_PATHS = {
    "/docs",
    "/openapi.json",
    "/interview.html",
    "/services/interview-link/validate",
    "/ws/interview",
    "/services/get-test",
    "/services/submit-test",
    "/favicon.ico",
    "/",
    "/routes/apply/form",
    "/ws/verify-cnic",
    "/ws/stop",}

BYPASS_PREFIXES = ("/static/", "/public/")


# 🔐 Middleware (ONLY for validating + attaching user)
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Skip public routes
    if path in BYPASS_PATHS or path.startswith(BYPASS_PREFIXES):
        return await call_next(request)

    # Get Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(status_code=401, content={"detail": "No Authorization header"})

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(status_code=401, content={"detail":
"Invalid auth header format"})

        token = parts[1]

        # Validate token with Supabase
        response = supabase.auth.get_user(token)

        if not response.user:
            return JSONResponse(status_code=401, content={"detail":
"User not found"})

        # Attach user to request
        request.state.user = response.user

        return await call_next(request)

    except Exception as e:
        print(f"Auth Middleware Error: {str(e)}")
        return JSONResponse(status_code=401, content={"detail":
"Invalid or expired token"})


# 👇 Dependency (USED IN ROUTES)
def get_current_user(request: Request):
    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in request"
        )

    return user