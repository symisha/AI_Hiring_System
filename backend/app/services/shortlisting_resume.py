#extract all the rating from database
#check the deviation of the ratings
#that decides the threshold for shortlisting
# if the rating is above the threshold, then the resume is shortlisted
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.database.db_connection import supabase
from app.services.gmail_service import send_email
from app.auth_middleware import auth_middleware
from app.config.config import Settings
from app.services.interview_link import generate_interview_token, verify_interview_token

logger = logging.getLogger(__name__)
router = APIRouter()


def shortlist_resumes(job_id: str):
    """Return processed candidates with computed shortlist/reject sets using mean+1 std-dev threshold."""
    rows = (
        supabase.table("job_applications")
        .select("id,job_id,applicant_id,resume_score,status")
        .eq("job_id", job_id)
        .eq("status", "processed")
        .execute()
        .data
    ) or []

    applicant_ids = [row.get("applicant_id") for row in rows if row.get("applicant_id") is not None]
    applications_map = {}

    if applicant_ids:
        applications_rows = (
            supabase.table("applications")
            .select("id,name,email")
            .in_("id", applicant_ids)
            .execute()
            .data
        ) or []

        applications_map = {row.get("id"): row for row in applications_rows}

    for row in rows:
        row["applications"] = applications_map.get(row.get("applicant_id"), {})

    candidates = [row for row in rows if row.get("resume_score") is not None]
    scores = [float(row["resume_score"]) for row in candidates]

    if not scores:
        return {"threshold": None, "shortlisted": [], "rejected": []}

    mean_score = sum(scores) / len(scores)
    std_dev = (sum((x - mean_score) ** 2 for x in scores) / len(scores)) ** 0.5
    threshold = mean_score + std_dev

    shortlisted = [row for row in candidates if float(row["resume_score"]) >= threshold]
    rejected = [row for row in candidates if float(row["resume_score"]) < threshold]

    return {"threshold": threshold, "shortlisted": shortlisted, "rejected": rejected}


def _build_shortlist_email_html(candidate_name: str, job_id: str, interview_url: str) -> str:
    """Return an HTML email body for a shortlisted candidate."""
    return f"""\
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <h2 style="color: #2563eb;">Congratulations, {candidate_name}! 🎉</h2>
        <p>
            We are pleased to inform you that your resume has been <strong>shortlisted</strong>
            for the position (Job Ref: <code>{job_id}</code>).
        </p>
        <p>
            Our team was impressed with your qualifications, and we would like to
            move forward with the next steps in the hiring process.
        </p>
        <p>
            Please complete your AI interview within <strong>24 hours</strong> using this secure link:
        </p>
        <p>
            <a href="{interview_url}" style="background:#2563eb;color:#fff;padding:10px 16px;border-radius:6px;text-decoration:none;display:inline-block;">
                Start AI Interview
            </a>
        </p>
        <p>If the button does not work, copy this URL:<br/><code>{interview_url}</code></p>
        <p><strong>Note:</strong> This interview link expires automatically after 24 hours.</p>
        <br/>
        <p>Best regards,<br/><strong>AI Hiring System</strong></p>
    </div>
    """


def send_emails(shortlisted_resumes: list[dict], job_id: str = "N/A") -> dict:
    """
    Send shortlisting notification emails to all candidates via Gmail OAuth.

    Parameters
    ----------
    shortlisted_resumes : list[dict]
        Rows returned by `shortlist_resumes()`. Each row should contain
        nested `applications` dict with `name` and `email`.
    job_id : str
        Job reference id (used in the email body).

    Returns
    -------
    dict  –  {"sent": [...], "failed": [...]}
    """
    sent: list[str] = []
    failed: list[dict] = []

    for entry in shortlisted_resumes:
        # Support both flat and nested (joined) shapes
        applicant = entry.get("applications") or entry
        candidate_email = applicant.get("email")
        candidate_name = applicant.get("name", "Candidate")
        applicant_id = entry.get("applicant_id")

        if not candidate_email or not applicant_id:
            logger.warning(f"Skipping entry with missing email/applicant_id: {entry}")
            failed.append({"entry": entry, "reason": "missing email or applicant_id"})
            continue

        interview_token = generate_interview_token(
            {
                "purpose": "ai_interview",
                "job_id": str(job_id),
                "applicant_id": str(applicant_id),
                "email": candidate_email,
                "name": candidate_name,
            }
        )

        base_url = Settings.FRONTEND_INTERVIEW_URL.rstrip("/")
        interview_url = f"{base_url}?ivt={interview_token}"

        subject = "You've Been Shortlisted! – Next Steps"
        body_html = _build_shortlist_email_html(candidate_name, job_id, interview_url)

        try:
            send_email(to=candidate_email, subject=subject, body_html=body_html)
            sent.append(candidate_email)
            logger.info(f"✅ Email sent to {candidate_email}")
        except Exception as exc:
            logger.error(f"❌ Failed to send email to {candidate_email}: {exc}")
            failed.append({"email": candidate_email, "reason": str(exc)})

    logger.info(f"Email summary — sent: {len(sent)}, failed: {len(failed)}")
    return {"sent": sent, "failed": failed}


def shortlist_and_update_status(job_id: str, company_id: str) -> dict:
    """For an open/active job: shortlist processed candidates, send email, set statuses."""
    job = (
        supabase.table("jobs")
        .select("id")
        .eq("id", job_id)
        .eq("company_id", company_id)
        .in_("status", ["open", "active"])
        .limit(1)
        .execute()
        .data
    )

    if not job:
        return {"job_id": job_id, "threshold": None, "shortlisted": 0, "rejected": 0, "errors": ["job not found or not open/active"]}

    shortlisted_result = shortlist_resumes(job_id)
    threshold = shortlisted_result["threshold"]
    shortlisted_rows = shortlisted_result["shortlisted"]
    rejected_rows = shortlisted_result["rejected"]

    email_result = send_emails(shortlisted_rows, job_id=job_id) if shortlisted_rows else {"sent": [], "failed": []}

    errors = []
    updated_shortlisted = 0
    updated_rejected = 0

    for row in shortlisted_rows:
        try:
            (
                supabase.table("job_applications")
                .update({"status": "interview-stage"})
                .eq("id", row["id"])
                .execute()
            )
            updated_shortlisted += 1
        except Exception as exc:
            errors.append({"applicant_id": row.get("applicant_id"), "error": str(exc)})

    for row in rejected_rows:
        try:
            (
                supabase.table("job_applications")
                .update({"status": "rejected"})
                .eq("id", row["id"])
                .execute()
            )
            updated_rejected += 1
        except Exception as exc:
            errors.append({"applicant_id": row.get("applicant_id"), "error": str(exc)})

    return {
        "job_id": job_id,
        "threshold": threshold,
        "shortlisted": updated_shortlisted,
        "rejected": updated_rejected,
        "emails_sent": len(email_result.get("sent", [])),
        "email_failures": len(email_result.get("failed", [])),
        "errors": errors,
    }


@router.post("/shortlist/{job_id}")
def run_shortlisting_for_job(job_id: str, user=Depends(auth_middleware)):
    company_id = getattr(user, "id", None)
    if not company_id:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    result = shortlist_and_update_status(job_id=job_id, company_id=str(company_id))
    return result


@router.get("/interview-link/validate")
def validate_interview_link(token: str):
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


