import uvicorn  # ASGI server used to run FastAPI apps (like "npm start" for Node)
from fastapi import FastAPI, Depends  # Main FastAPI class used to create the web application instance
from fastapi.middleware.cors import CORSMiddleware  # Middleware to handle CORS (Cross-Origin Resource Sharing)
from pydantic import BaseModel  # Used to define and validate data models (for requests/responses) with type checking
from app.config.config import Settings  # Import the Settings class to access environment variables

# Import routes (import nested routers directly to avoid circular/package import issues)
from app.routes import rating_resume, apply
from app.routes.dashboard_essentials.dashboard_info import router as dashboard_info_router
from app.routes.dashboard_essentials.profile_preview_router import router as profile_preview_router

# Database
from app.database.db_connection import supabase  # Supabase client instance

# Auth middleware
from app.auth_middleware import auth_middleware

# Create FastAPI app instance
app = FastAPI()

# Allowed origins for CORS
origins = [
    # "http://localhost:8000",  # Frontend URL
]

# Include your endpoints
app.include_router(rating_resume.router, prefix="/routes", tags=["rating"])
app.include_router(dashboard_info_router, prefix="/routes/dashboard_essentials", tags=["database"])
app.include_router(profile_preview_router, prefix="/routes/dashboard_essentials", tags=["database"])
app.include_router(apply.router, prefix="/routes", tags=["apply"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[Settings.FRONTEND_URL],  # List of allowed origins (frontend URLs)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root GET endpoint
@app.get("/")
async def read_root():
    return {"Hello": "World"}

# Root POST endpoint
@app.post("/")
async def create_item(item: dict):
    return {"item_received": item}

# Test endpoint to verify environment variable loading
@app.get("/whoami")
async def who_am_i(user=Depends(auth_middleware)):
    return user

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
