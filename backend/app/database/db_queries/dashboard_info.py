from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
from app.auth_middleware import auth_middleware         # Import the authentication middleware to protect routes

class DashboardContext:
    user_email = None
    user_id = None

#for DASHBOARD INFO
def set_user_info(user):
    # supabase.auth.get_user may return different shapes depending on client
    # Try several common shapes: object with .user, dict with ['data']['user'],
    # or a direct user dict/object.
    try:
        if hasattr(user, "user"):
            u = user.user
        elif isinstance(user, dict) and user.get("data") and isinstance(user.get("data"), dict) and user.get("data").get("user"):
            u = user.get("data").get("user")
        elif isinstance(user, dict) and user.get("user"):
            u = user.get("user")
        else:
            u = user

        # extract email
        if isinstance(u, dict):
            DashboardContext.user_email = (u.get("user_metadata") or {}).get("email")
            DashboardContext.user_id = u.get("id")
        else:
            DashboardContext.user_email = getattr(u, "user_metadata", {}).get("email") if getattr(u, "user_metadata", None) else None
            DashboardContext.user_id = getattr(u, "id", None)
    except Exception as e:
        print("Error parsing user info in set_user_info:", e)
        DashboardContext.user_email = None
        DashboardContext.user_id = None

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
            # Some job records use 'title' while older code referenced 'job_title'
            "job_title": [job.get('job_title') or job.get('title') for job in jobs] if jobs else []
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




#applicants details

def get_applicant_details(job_id: str):
    try:
        response = (
            supabase.table("job_applications")
            .select("*")            # get all columns
            .eq("job_id", job_id)  
            .execute()
        )
        applicants = response.data
        total_applicants = len(applicants) if applicants else 0

        return {
            "total_applicants": total_applicants, 
            "applicants": applicants
        }      
    except Exception as e:
        print("Error in get_applicant_details:", e)
        return {"error": str(e)}


