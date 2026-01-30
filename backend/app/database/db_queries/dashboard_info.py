from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
from app.auth_middleware import auth_middleware         # Import the authentication middleware to protect routes

class DashboardContext:
    user_email = None
    user_id = None

#for DASHBOARD INFO
def set_user_info(user):
    DashboardContext.user_email = user.user.user_metadata["email"]
    DashboardContext.user_id = user.user.id

def get_total_job_postings():
    try:
        response = (
            supabase.table("jobs")
            .select("*")            # get all columns
            .eq("company_id", DashboardContext.user_id)   # filter by user_id
            .execute()
        )
        jobs = response.data
        total_jobs = len(jobs) if jobs else 0

        return {
            "id" : DashboardContext.user_id,
            "email": DashboardContext.user_email,
            "total_job_postings": total_jobs,
            "jobs": jobs,
            "job_title": [job['title'] for job in jobs] if jobs else []
        }

    except Exception as e:
        print("Error in get_total_job_postings:", e)
        return {"error": str(e)}


def dashboard_info(user):
    set_user_info(user)
    return get_total_job_postings()
    

    
#Help ticket submission

def submit_complaints_db(subject: str, description: str):
    try:
        supabase.table("complaints").insert({
            "company_id": DashboardContext.user_id,
            "subject": subject,
            "description": description
        }).execute()

        return {"message": "Help ticket submitted successfully."}

    except Exception as e:
        print("Error in submit_complaints_db:", e)
        return {"error": str(e)}
    

 #search bar 

from fastapi import APIRouter, Query

router = APIRouter()


def search_applicants(
    company_id: str,
    q: str = Query(..., min_length=1)
):
    response = (
        supabase.table("applicants")
        .select("""
            id,
            name,
            email,
            phone,
            resume_url,
            experience
        """)
        .eq("company_id", company_id)
        .or_(
            f"name.ilike.%{q}%,email.ilike.%{q}%"
        )
        .limit(10)
        .execute()
    )

    return response.data
