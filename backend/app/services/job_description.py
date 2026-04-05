
import json
import uuid
import time
import hmac
import hashlib
import base64
from fastapi import Depends
from app.models.upload_job import JobCreate
from app.database.db_connection import supabase
from app.auth_middleware import auth_middleware
from app.config.config import Settings
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


def _make_apply_token(job_id: str, ttl_seconds: int = 60 * 60 * 24 * 30):
    expires = int(time.time()) + ttl_seconds
    payload = f"{job_id}:{expires}"
    sig = hmac.new(Settings.SUPABASE_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token_raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(token_raw.encode()).decode()


@router.post("/upload-job")
async def upload_job(
    job_data: JobCreate, 
    user=Depends(auth_middleware)
):
    try:
        user_id = user.id 

        db_response = supabase.table("jobs").insert({
            "company_id": user_id, 
            "job_title": job_data.title,
            "short_description": job_data.short_description,
            "job_metadata": job_data.metadata,
            "status": "open",
            "job_description_url": None  
        }).execute()

        created_job = db_response.data[0] if db_response.data else {}
        job_id = created_job.get("id")
        apply_token = None
        apply_link = None

        if job_id:
            apply_token = _make_apply_token(str(job_id))
            frontend = Settings.FRONTEND_URL.rstrip("/")
            apply_link = f"{frontend}/apply?token={apply_token}"
            # Persist token if the column exists; ignore silently if not yet added
            try:
                supabase.table("jobs").update({"apply_token": apply_token}).eq("id", job_id).execute()
            except Exception as token_err:
                print(f"[upload-job] apply_token column not available, skipping: {token_err}")

        return {
            "message": "Job details saved successfully",
            "job_id": job_id,
            "apply_token": apply_token,
            "apply_link": apply_link,
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
        user_id = user.id

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