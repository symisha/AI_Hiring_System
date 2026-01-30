from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
from app.auth_middleware import auth_middleware         # Import the authentication middleware to protect routes
from fastapi import APIRouter, Depends                     # Import FastAPI class to create the web
from app.database.db_queries.dashboard_info import dashboard_info as get_dashboard_info
from app.database.db_queries.dashboard_info import submit_complaints_db
from app.database.db_queries.dashboard_info import search_applicants

router = APIRouter() 

@router.get("/dashboard-info")
def dashboard_endpoint(user=Depends(auth_middleware)):
    return get_dashboard_info(user)

@router.post("/submit-complaint")
def submit_complaint_endpoint(subject: str, description: str, user=Depends(auth_middleware)):
    
    return submit_complaints_db(subject, description)

@router.get("/job/{company_id}/search-applicants")
def search_applicants(company_id: str, query: str, user=Depends(auth_middleware)):
   return search_applicants(company_id, query)
#probably a wrong logic here, need to check