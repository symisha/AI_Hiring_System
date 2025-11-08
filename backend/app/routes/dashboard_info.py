from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
from app.auth_middleware import auth_middleware         # Import the authentication middleware to protect routes
from fastapi import APIRouter, Depends                     # Import FastAPI class to create the web
from app.database.db_queries import dashboard_info as get_dashboard_info


router = APIRouter() 
@router.get("/dashboard-info")
def dashboard_endpoint(user=Depends(auth_middleware)):
    return get_dashboard_info(user)