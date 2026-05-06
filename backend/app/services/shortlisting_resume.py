import logging
from fastapi import APIRouter, Depends, HTTPException
from app.database.db_connection import supabase
from app.services.gmail_service import send_email
from app.auth_middleware import get_current_user
from app.config.config import Settings
from app.services.interview_link import generate_interview_token, verify_interview_token
from app.models.appstage import AppStatus

logger = logging.getLogger(__name__)
router = APIRouter()

# --- CONFIGURABLE THRESHOLDS ---
RESUME_THRESHOLD = 70.0
ASSESSMENT_THRESHOLD = 80.0

# --- HELPER: CORE LOGIC ---

def _process_shortlisting(job_id: str, current_status: str, score_column: str):
    """Fetches candidates and splits them based on fixed thresholds."""
    rows = (
        supabase.table("job_applications")
        .select(f"id, job_id, applicant_id, {score_column}, status")
        .eq("job_id", job_id)
        .eq("status", current_status)
        .execute()
        .data
    ) or []

    if not rows:
        return {"threshold": None, "shortlisted": [], "rejected": []}

    # Map applicant details
    applicant_ids = [r.get("applicant_id") for r in rows if r.get("applicant_id")]
    apps_map = {}
    if applicant_ids:
        app_data = (supabase.table("applications").select("id, name, email").in_("id", applicant_ids).execute().data) or []
        apps_map = {r["id"]: r for r in app_data}

    for row in rows:
        row["applications"] = apps_map.get(row.get("applicant_id"), {})

    # Determine threshold based on which stage we are in
    threshold = RESUME_THRESHOLD if score_column == "resume_score" else ASSESSMENT_THRESHOLD

    candidates = [row for row in rows if row.get(score_column) is not None]
    shortlisted = [r for r in candidates if float(r[score_column]) >= threshold]
    rejected = [r for r in candidates if float(r[score_column]) < threshold]

    return {"threshold": threshold, "shortlisted": shortlisted, "rejected": rejected}

# --- EMAIL TEMPLATE BUILDERS ---

def _build_test_email(name, job_id, url):
    return f"""
    <p>Good news, {name}!</p>
    <p>Your resume has been <strong>shortlisted</strong> for the position (Job Ref: {job_id}).</p>
    <p>To move forward in the hiring process, we invite you to complete a short AI-generated test.</p>
    <p>Please take the test within the next <strong>24 hours</strong> using the secure link below:</p>
    <p><a href="{url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Start Your Test</a></p>
    <p>If the button does not work, copy this URL:</p>
    <p style="word-break: break-all; color: #007bff;">{url}</p>
    <p><strong>Note:</strong> This test link expires automatically after 24 hours.</p>
    """

def _build_interview_email(name, job_id, url):
    return f"""
    <p>Congratulations, {name}!</p>
    <p>You have successfully passed the assessment for the position (Job Ref: {job_id}).</p>
    <p>The final step in our process is an AI-powered video interview.</p>
    <p>Please complete this interview within the next <strong>24 hours</strong> using the secure link below:</p>
    <p><a href="{url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Start Your Interview</a></p>
    <p>If the button does not work, copy this URL:</p>
    <p style="word-break: break-all; color: #28a745;">{url}</p>
    <p><strong>Note:</strong> This interview link expires automatically after 24 hours.</p>
    """
# --- EXPORTED FLOW FUNCTIONS (Scheduler looks for these) ---
def run_resume_to_assessment_flow(job_id: str):
    """Stage 1: RESUME_GRADED -> ASSESSMENT_PENDING"""
    data = _process_shortlisting(job_id, AppStatus.RESUME_GRADED.value, "resume_score")
    
    # Iterate through each shortlisted candidate
    for entry in data["shortlisted"]:
        # All logic using 'entry' MUST be indented here
        try:
            # 1. Update status first to prevent double-processing
            supabase.table("job_applications").update({
                "status": AppStatus.ASSESSMENT_PENDING.value
            }).eq("id", entry["id"]).execute()

            # 2. Prepare the email
            token = generate_interview_token({
                "purpose": "ai_test", 
                "job_id": job_id, 
                "applicant_id": entry["applicant_id"], 
                "email": entry["applications"].get("email"),
                "name": entry["applications"].get("name")
            })
            print(f"Token generated: {token[:10]}...") # TRACE 3
            
            # Use your specific localhost URL format
            url = f"{Settings.FRONTEND_URL.rstrip('/')}/assessment?ivt={token}"
            send_email(
                to=entry["applications"].get("email"), 
                subject="Next Step: Assessment Test", 
                body_html=_build_test_email(entry["applications"].get("name"), job_id, url)
            )
            logger.info(f"Sent assessment invite to {entry['id']}")
            
        except Exception as e:
            logger.error(f"Failed to process entry {entry.get('id')}: {e}")

    # Process rejected candidates
    for entry in data["rejected"]:
        supabase.table("job_applications").update({
            "status": AppStatus.REJECTED.value
        }).eq("id", entry["id"]).execute()
    
    return data

def run_assessment_to_interview_flow(job_id: str):
    """Stage 2: ASSESSMENT_GRADED -> INTERVIEW_SCHEDULED"""
    data = _process_shortlisting(job_id, AppStatus.ASSESSMENT_GRADED.value, "assessment_score")
    
    for entry in data["shortlisted"]:
        token = generate_interview_token({"purpose": "ai_interview", "job_id": job_id, "applicant_id": entry["applicant_id"], "email": entry["applications"].get("email")})
        url = f"{Settings.FRONTEND_INTERVIEW_URL.rstrip('/')}?ivt={token}"
        send_email(to=entry["applications"].get("email"), subject="Next Step: Interview", body_html=_build_interview_email(entry["applications"].get("name"), job_id, url))
        supabase.table("job_applications").update({"status": AppStatus.INTERVIEW_SCHEDULED.value}).eq("id", entry["id"]).execute()

    for entry in data["rejected"]:
        supabase.table("job_applications").update({"status": AppStatus.REJECTED.value}).eq("id", entry["id"]).execute()
        
    return data


@router.post("/shortlist/{job_id}")
def run_shortlisting_for_job(job_id: str, user=Depends(get_current_user)):
    """
    Manually triggers the shortlisting process for both Resume -> Test 
    and Test -> Interview for a specific job.
    """
    company_id = getattr(user, "id", None)
    if not company_id:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    # 1. Run Stage 1 (Resume Graded -> Assessment Pending)
    stage_one_results = run_resume_to_assessment_flow(job_id)

    # 2. Run Stage 2 (Assessment Graded -> Interview Pending)
    stage_two_results = run_assessment_to_interview_flow(job_id)

    return {
        "job_id": job_id,
        "resume_to_test": {
            "shortlisted": len(stage_one_results.get("shortlisted", [])),
            "rejected": len(stage_one_results.get("rejected", []))
        },
        "test_to_interview": {
            "shortlisted": len(stage_two_results.get("shortlisted", [])),
            "rejected": len(stage_two_results.get("rejected", []))
        }
    }


@router.get("/interview-link/validate")
def validate_interview_link(token: str):
    """Validates the JWT token for either test or interview."""
    payload = verify_interview_token(token)
    return {
        "valid": True,
        "purpose": payload.get("purpose"),
        "job_id": payload.get("job_id"),
        "applicant_id": payload.get("applicant_id"),
        "email": payload.get("email"),
        "name": payload.get("name"),
        "exp": payload.get("exp"),
    }