
import json
import uuid
from fastapi import Depends
from app.models.upload_job import JobCreate
from app.database.db_connection import supabase
from app.auth_middleware import auth_middleware
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()
@router.post("/upload-job")
async def upload_job(
    job_data: JobCreate, 
    user=Depends(auth_middleware)
):
    try:
        # Accessing the ID from the UserResponse object
        # Supabase UserResponse -> user attribute -> id attribute
        user_id = user.user.id 

        db_response = supabase.table("jobs").insert({
            "company_id": user_id, 
            "job_title": job_data.title,
            "short_description": job_data.short_description,
            "job_metadata": job_data.metadata,
            "status": "open",
            "job_description_url": None  
        }).execute()

        return {
            "message": "Job details saved successfully",
            "job_id": db_response.data[0].get("id") if db_response.data else None
        }

    except Exception as e:
        print(f"Database Insert Error: {str(e)}")
        return JSONResponse(
            {"message": "Failed to save job", "error": str(e)}, 
            status_code=500
        )