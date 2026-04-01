from app.database.db_queries.specific_job_db import delete_job_db
from app.database.db_connection import supabase
from fastapi import APIRouter, Depends
from app.auth_middleware import auth_middleware
from uuid import UUID

delRouter = APIRouter()

@delRouter.delete("/delete-job/{job_id}")
def delete_job_route(job_id: UUID, user=Depends(auth_middleware)): 
    # Call the delete_job_db function directly since service layer is not needed
    result = delete_job_db(job_id)
    return result

@delRouter.post("/generate-apply-link/{job_id}")
def generate_apply_link(job_id: str, user=Depends(auth_middleware)):
    try:
        # Generate apply token (use job_id as token)
        apply_token = job_id
        
        # Update job with apply_token
        response = supabase.table("jobs").update({
            "apply_token": apply_token
        }).eq("id", job_id).execute()
        
        if not response.data:
            return {"error": "Job not found or you don't have permission to edit it"}, 404
        
        return {
            "message": "Apply token generated",
            "apply_token": apply_token,
            "apply_link": f"{apply_token}"
        }
    except Exception as e:
        print(f"Error generating apply link: {str(e)}")
        return {"error": str(e)}, 500