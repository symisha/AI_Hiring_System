from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from app.config.config import Settings
from app.database.db_connection import supabase
from app.auth_middleware import get_current_user
from app.models.appstage import AppStatus
from app.services.cnic_embedding import extract_cnic_embedding
import time
import hmac
import hashlib
import base64
import uuid
from uuid import UUID

router = APIRouter()

SECRET = Settings.SUPABASE_KEY or "change-me"
CNIC_BUCKET_NAME = getattr(Settings, "SUPABASE_CNIC_BUCKET", None) or "Resumes"
CNIC_PREFIX = "cnic"


def _make_token(job_id: str, ttl_seconds: int = 60 * 60 * 24 * 30):
    expires = int(time.time()) + ttl_seconds
    payload = f"{job_id}:{expires}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token_raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(token_raw.encode()).decode()


def _verify_token(token: str):
    # Stable public link format: token is the job UUID itself.
    try:
        UUID(str(token))
        return str(token)
    except Exception:
        pass

    # Backward-compatible format: signed/expiring token.
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
def generate_apply_link(job_id: str, user=Depends(get_current_user)):
    """Generate a tokenized apply link for a job (protected route for HR users)."""
    # Verify job exists
    try:
        res = supabase.table("jobs").select("*").eq("id", job_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")

    token = job_id
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
        res = supabase.table("jobs").select("*").eq("id", job_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Job not found")
        if res.data.get("status") != "open":
            raise HTTPException(status_code=410, detail="This job is no longer accepting applications")
        return res.data
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")


@router.post("/apply/form")
def submit_form_application(
    token: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    city: str = Form(None),
    linkedin: str = Form(None),
    portfolio: str = Form(None),
    cnic_image: UploadFile = File(...),
    degree: str = Form(None),
    major: str = Form(None),
    university: str = Form(None),
    grad_year: str = Form(None),
    cgpa: str = Form(None),
    experiences: str = Form(None),
    skills: str = Form(None),
    projects: str = Form(None),
    metadata: str = Form(None)
):
    print(f"Received application for token {token} | name: {name} | email: {email}")
    """Accept candidate structured form application (no resume file required)."""
    import json as _json

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

    try:
        experiences_data = _json.loads(experiences) if experiences else []
    except Exception:
        experiences_data = []
    try:
        skills_data = _json.loads(skills) if skills else []
    except Exception:
        skills_data = []
    try:
        projects_data = _json.loads(projects) if projects else []
    except Exception:
        projects_data = []

    print(f"Processing application for job {job_id}")

    if not cnic_image or not getattr(cnic_image, "filename", None):
        raise HTTPException(status_code=400, detail="CNIC image is required")
    if cnic_image.content_type and not str(cnic_image.content_type).startswith("image/"):
        raise HTTPException(status_code=400, detail="CNIC must be an image file")

    file_ext = (cnic_image.filename.split(".")[-1] if "." in cnic_image.filename else "").lower()
    if file_ext not in {"png", "jpg", "jpeg", "webp"}:
        raise HTTPException(status_code=400, detail="Supported CNIC image types: png, jpg, jpeg, webp")

    cnic_storage_path = f"{CNIC_PREFIX}/{job_id}/{uuid.uuid4()}.{file_ext}"
    try:
        file_bytes = cnic_image.file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to read CNIC image")

    try:
        cnic_embedding = extract_cnic_embedding(file_bytes, file_ext)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract CNIC embedding: {str(e)}")

    try:
        supabase.storage.from_(CNIC_BUCKET_NAME).upload(cnic_storage_path, file_bytes)
        cnic_image_url = supabase.storage.from_(CNIC_BUCKET_NAME).get_public_url(cnic_storage_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload CNIC image: {str(e)}")

    candidate_metadata = {
        "name": name,
        "email": email,
        "phone": phone,
        "city": city,
        "linkedin": linkedin,
        "portfolio": portfolio,
        "cnic_image_url": cnic_image_url,
        "cnic_embedding": cnic_embedding,
        "degree": degree,
        "major": major,
        "university": university,
        "grad_year": grad_year,
        "cgpa": cgpa,
        "experiences": experiences_data,
        "skills": skills_data,
        "projects": projects_data,
        "applied_on": int(time.time()),
        "status": "new"
    }
    record_for_applications = {
        "job_id": job_id,
        "name": name,
        "email": email,
        "phone": phone,
        "city": city,
        "cnic_image_url": cnic_image_url,
        "cnic_embedding": cnic_embedding,
        "metadata": candidate_metadata,
    }
    print(f"Candidate metadata for {name}: {candidate_metadata}")

    try:
        response = (
            supabase.table("applications")
            .insert(record_for_applications)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to insert into applications table")
        print(f"New application received: {response.data[0]['id']} for job {job_id}")

        # Optional: if the applications table has a dedicated `cnic_image_url` column,
        # persist the URL there as well (ignore errors if the column doesn't exist).
        try:
            supabase.table("applications").update({"cnic_image_url": cnic_image_url}).eq(
                "id", response.data[0]["id"]
            ).execute()
        except Exception:
            pass

        job_app_response = (
            supabase.table("job_applications")
            .insert({
                "job_id": job_id,
                "applicant_id": response.data[0]["id"],
                "status": AppStatus.RESUME_RECEIVED.value,
            })
            .execute()
        )
        print(f"Created job_applications record for application {response.data[0]['id']}: {job_app_response.data}")
        if not job_app_response.data:
            raise HTTPException(status_code=500, detail="Failed to insert into job_applications table")

        return {
            "status": "success",
            "message": "Record created in applications and job_applications tables.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving application: {str(e)}")


