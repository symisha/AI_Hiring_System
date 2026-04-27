from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
from app.auth_middleware import get_current_user         # Use the correct dependency for user
from fastapi import APIRouter, Depends                     # Import FastAPI class to create the web
from app.database.db_queries.dashboard_info import dashboard_info as get_dashboard_info
from app.database.db_queries.dashboard_info import submit_complaints_db
from app.database.db_queries.dashboard_info import search_applicants
from app.database.db_queries.dashboard_info import get_applicant_details 

router = APIRouter() 


@router.get("/dashboard-info")
def dashboard_endpoint(user=Depends(get_current_user)):
    return get_dashboard_info(user)


@router.post("/submit-complaint")
def submit_complaint_endpoint(subject: str, description: str, user=Depends(get_current_user)):
    return submit_complaints_db(subject, description)


@router.get("/job/{company_id}/search-applicants")
def search_applicants(company_id: str, query: str, user=Depends(get_current_user)):
    return search_applicants(company_id, query)
#probably a wrong logic here, need to check



@router.get("/job/{job_id}/get-applicants")
def get_applicants(job_id: str, user=Depends(get_current_user)):
    return get_applicant_details(job_id)