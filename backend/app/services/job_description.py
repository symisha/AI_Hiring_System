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
    

@router.put("/update-job/{job_id}")
async def update_job(
    job_id: str, 
    job_data: JobCreate, 
    user=Depends(auth_middleware)
):
    try:
        user_id = user.user.id

        # 1. Update the record where the ID matches AND the user owns it
        # This prevents one company from updating another company's job
        db_response = supabase.table("jobs").update({
            "job_title": job_data.title,
            "short_description": job_data.short_description,
            "job_metadata": job_data.metadata,
            "status": "open" 
        }).eq("id", job_id).eq("company_id", user_id).execute()

        # 2. Check if anything was actually updated
        if not db_response.data:
            return JSONResponse(
                {"message": "Job not found or you don't have permission to edit it"}, 
                status_code=404
            )

        return {
            "message": "Job updated successfully",
            "data": db_response.data[0]
        }

    except Exception as e:
        print(f"Update Error: {str(e)}")
        return JSONResponse(
            {"message": "Failed to update job", "error": str(e)}, 
            status_code=500
        )