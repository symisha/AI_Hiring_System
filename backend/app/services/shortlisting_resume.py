#extract all the rating from database
#check the deviation of the ratings
#that decides the threshold for shortlisting
# if the rating is above the threshold, then the resume is shortlisted
import logging
from app.database.db_connection import supabase
from app.services.gmail_service import send_email

logger = logging.getLogger(__name__)


def shortlist_resumes(job_id: str):
    """Return applicants whose resume_score is above (mean + 1 std-dev)."""
    #get all the ratings for the job_id
    ratings = supabase.table("job_applications").select("resume_score").eq("job_id", job_id).execute().data
    scores = [r["resume_score"] for r in ratings if r["resume_score"] is not None]
    
    if not scores:
        return []
    
    #calculate the mean and standard deviation
    mean_score = sum(scores) / len(scores)
    std_dev = (sum((x - mean_score) ** 2 for x in scores) / len(scores)) ** 0.5
    
    #set the threshold as mean + 1 standard deviation
    threshold = mean_score + std_dev
    
    #get all the resumes that have a score above the threshold
    shortlisted = (
        supabase.table("job_applications")
        .select("*, applicants(name, email)")   # join applicant details
        .eq("job_id", job_id)
        .gte("resume_score", threshold)
        .execute()
        .data
    )
    
    return shortlisted


def _build_shortlist_email_html(candidate_name: str, job_id: str) -> str:
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
            You will receive further details regarding the upcoming interview
            round shortly. Please keep an eye on your inbox.
        </p>
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
        nested `applicants` dict with `name` and `email`.
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
        applicant = entry.get("applicants") or entry
        candidate_email = applicant.get("email")
        candidate_name = applicant.get("name", "Candidate")

        if not candidate_email:
            logger.warning(f"Skipping entry with no email: {entry}")
            failed.append({"entry": entry, "reason": "missing email"})
            continue

        subject = "You've Been Shortlisted! – Next Steps"
        body_html = _build_shortlist_email_html(candidate_name, job_id)

        try:
            send_email(to=candidate_email, subject=subject, body_html=body_html)
            sent.append(candidate_email)
            logger.info(f"✅ Email sent to {candidate_email}")
        except Exception as exc:
            logger.error(f"❌ Failed to send email to {candidate_email}: {exc}")
            failed.append({"email": candidate_email, "reason": str(exc)})

    logger.info(f"Email summary — sent: {len(sent)}, failed: {len(failed)}")
    return {"sent": sent, "failed": failed}


