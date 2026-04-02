from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.config.config import Settings
from app.database.db_connection import supabase
from app.auth_middleware import auth_middleware
import time
import hmac
import hashlib
import base64

router = APIRouter()

SECRET = Settings.SUPABASE_KEY or "change-me"


def _make_token(job_id: str, ttl_seconds: int = 60 * 60 * 24 * 30):
    expires = int(time.time()) + ttl_seconds
    payload = f"{job_id}:{expires}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token_raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(token_raw.encode()).decode()


def _verify_token(token: str):
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        parts = decoded.split(":")
        if len(parts) < 3:
            return None
        job_id = parts[0]
        expires = int(parts[1])
        sig = parts[2]
        payload = f"{job_id}:{expires}"
        expected = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        if int(time.time()) > expires:
            return None
        return job_id
    except Exception:
        return None


@router.post("/job/{job_id}/generate-link")
def generate_apply_link(job_id: str, user=Depends(auth_middleware)):
    """Generate a tokenized apply link for a job (protected route for HR users)."""
    # Verify job exists
    try:
        res = supabase.table("jobs").select("*").eq("id", job_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")

    token = _make_token(job_id)
    frontend = Settings.FRONTEND_URL.rstrip("/")
    link = f"{frontend}/apply?token={token}"
    return {"apply_link": link}


@router.get("/apply")
def get_job_for_apply(token: str):
    """Public endpoint to return basic job info for a given token."""
    job_id = _verify_token(token)
    if not job_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    try:
        # Not all schemas include a `description` column. Prefer returning structured `job_metadata` and `job_description_url`.
        res = supabase.table("jobs").select("id,title,job_metadata,job_description_url,location,posted_on,status").eq("id", job_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Job not found")
        if res.data.get("status") != "open":
            raise HTTPException(status_code=410, detail="This job is no longer accepting applications")
        return res.data
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")


@router.post("/apply")
def submit_application(
    token: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    cover_letter: str = Form(None),
    resume: UploadFile = File(...),
):
    """Accept candidate application + resume upload for the job identified by token."""
    job_id = _verify_token(token)
    if not job_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    try:
        job_res = supabase.table("jobs").select("id,status").eq("id", job_id).single().execute()
        if not job_res.data:
            raise HTTPException(status_code=404, detail="Job not found")
        if job_res.data.get("status") != "open":
            raise HTTPException(status_code=410, detail="This job is no longer accepting applications")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")

    # Upload resume to Supabase storage (bucket: resumes)
    try:
        bucket = "resumes"
        # create a path like jobid/timestamp_filename
        timestamp = int(time.time())
        filename = resume.filename or f"resume_{timestamp}.pdf"
        path = f"{job_id}/{timestamp}_{filename}"

        content = resume.file.read()
        upload = supabase.storage.from_(bucket).upload(path, content)
        # upload returns a dict; check for error key in some client versions
        # create public URL
        public_url = supabase.storage.from_(bucket).get_public_url(path).get("publicURL")

        # Insert application record into `applications` table
        record = {
            "job_id": job_id,
            "name": name,
            "email": email,
            "phone": phone,
            "cover_letter": cover_letter,
            "resume_path": path,
            "resume_url": public_url,
            "applied_on": int(time.time()),
            "status": "new",
        }

        supabase.table("applications").insert(record).execute()

        return {"status": "success", "message": "Application submitted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving application: {str(e)}")
