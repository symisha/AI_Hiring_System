import time
import hmac
import hashlib
import base64
from app.database.db_queries.specific_job_db import delete_job_db, update_job_db, close_job_db, activate_job_db, try_persist_apply_token
from app.database.db_connection import supabase
from fastapi import APIRouter, Depends, HTTPException
from app.auth_middleware import auth_middleware
from app.models.upload_job import JobCreate
from app.config.config import Settings
from uuid import UUID

delRouter = APIRouter()
SECRET = Settings.SUPABASE_KEY or "change-me"


def _make_apply_token(job_id: str, ttl_seconds: int = 60 * 60 * 24 * 30):
    expires = int(time.time()) + ttl_seconds
    payload = f"{job_id}:{expires}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token_raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(token_raw.encode()).decode()

@delRouter.put("/edit-job/{job_id}")
def edit_job_route(job_id: UUID, job_data: JobCreate, user=Depends(auth_middleware)):
    """Update an existing job"""
    result = update_job_db(job_id, job_data.title, job_data.short_description, job_data.metadata)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@delRouter.delete("/delete-job/{job_id}")
def delete_job_route(job_id: UUID, user=Depends(auth_middleware)): 
    # Call the delete_job_db function directly since service layer is not needed
    result = delete_job_db(job_id)
    return result


@delRouter.put("/close-job/{job_id}")
def close_job_route(job_id: UUID, user=Depends(auth_middleware)):
    result = close_job_db(job_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@delRouter.put("/toggle-job-status/{job_id}")
def toggle_job_status_route(job_id: UUID, user=Depends(auth_middleware)):
    try:
        existing = supabase.table("jobs").select("id,status").eq("id", job_id).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Job not found")

        current_status = existing.data.get("status")
        if current_status == "open":
            result = close_job_db(job_id)
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            return {"success": True, "status": "inactive", "apply_token": None}

        new_token = _make_apply_token(str(job_id))
        result = activate_job_db(job_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        # Best-effort: persist token; continue even if apply_token column doesn't exist yet
        try_persist_apply_token(job_id, new_token)
        return {"success": True, "status": "open", "apply_token": new_token}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error toggling job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle job status")

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
            raise HTTPException(status_code=404, detail="Job not found or you don't have permission to edit it")
        
        return {
            "message": "Apply token generated",
            "apply_token": apply_token,
            "apply_link": f"{apply_token}"
        }
    except Exception as e:
        print(f"Error generating apply link: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))