# --- simplified ATS pipeline: uploads-only, no DB, individual outputs ---

from groq import Groq
import base64, os, io
from pathlib import Path
#import pymupdf
from PIL import Image
import json
from datetime import datetime, timedelta
import secrets, string
import uuid, hmac, hashlib
import fitz
import re
import requests
import traceback
from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
from fastapi import APIRouter, Depends, HTTPException                     # Import FastAPI class to create the web
from app.auth_middleware import auth_middleware         # Import the authentication middleware to protect routes
from app.config.config import Settings
from app.models.appstage import AppStatus


def fit_score(text, applicant_id: str):
    match = re.search(r'"overall_fit_score"\s*:\s*"(\d{1,3})"', text)
    fit = int(match.group(1)) if match else None
    supabase.table("job_applications").update({"resume_score": fit}).eq("applicant_id", applicant_id).execute()
    return fit
    #put it in supabase
    


# Usage
  # '' = root of bucket
# ------------------------
# Example usage
# ------------------------



# ------------------------- CONFIG -------------------------
# Prefer env vars; falls back to your literal for convenience
#GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
#client = Groq(api_key=GROQ_API_KEY)
  # individual extracted resume JSON files
EVALS_DIR = "evaluations"                # individual evaluation JSON files



#os.makedirs(JD_IMG_DIR, exist_ok=True)
#os.makedirs(RESUME_IMG_DIR, exist_ok=True)
#os.makedirs(RESUMES_JSON_DIR, exist_ok=True)
#os.makedirs(EVALS_DIR, exist_ok=True)


model_id = "llama-3.3-70b-versatile"
API_key = Settings.LLAMA_API_KEY
DEBUG_PIPELINE = True


def debug_log(message: str):
    if DEBUG_PIPELINE:
        print(f"[resume_extractor] {message}")




def extract_resume_sections(path):
    doc = fitz.open(path)

    # 1. Combine text from all pages
    full_text = "\n".join(page.get_text() for page in doc)

    # --- TEXT NORMALIZATION STEP (Fixes large vertical gaps) ---
    
    # Normalize bullet weirdness
    full_text = re.sub(r'•\s*\n\s*', '• ', full_text)

    # Collapse sequences of 3 or more newlines into a standard paragraph break (\n\n).
    full_text = re.sub(r'\n\n\n+', '\n\n', full_text)

    # Strip excessive leading/trailing whitespace from each line and re-join.
    full_text = "\n".join([line.strip() for line in full_text.splitlines()])
    
    # After stripping, re-collapse any empty lines that were created solely from whitespace
    full_text = re.sub(r'\n\n\n+', '\n\n', full_text)
    
    # --- END Normalization ---

    # Map different heading variants to canonical names
    heading_map = {
        "work experience": "Experience",
        "experience": "Experience",
        "professional experience": "Experience",

        "education": "Education",
        "academics": "Education",

        "projects": "Projects", # NOTE: Ensure this key is lowercase in your actual code if your resume headings are lowercase
        
        "technologies & languages": "Technologies & Languages",
        "technologies and languages": "Technologies & Languages",

        "skills": "Skills",
        "technical skills": "Skills",
        "skill set": "Skills",

        "certification": "Certifications",
        "certifications": "Certifications",
        "courses": "Certifications",

        "extra-curricular": "Extra-curricular",
        "extra curricular": "Extra-curricular",
        "activities": "Extra-curricular"
    }

    sections = {}
    current_section = None

    for raw_line in full_text.splitlines():
        line = raw_line.strip()
        
        if not line:
            # preserve single blank lines in current section
            if current_section and sections[current_section] and not sections[current_section].endswith("\n"):
                sections[current_section] += "\n"
            continue

        # Clean potential heading line:
        candidate = re.sub(r'^[•\-\u2022]*\s*', '', line)
        candidate_clean = candidate.strip(" .:\t").lower()

        if candidate_clean in heading_map:
            # We hit a heading line
            current_section = heading_map[candidate_clean]
            sections.setdefault(current_section, "")
            continue

        # Otherwise, it's content for the current section
        if current_section:
            if sections[current_section]:
                sections[current_section] += "\n" + raw_line
            else:
                sections[current_section] = raw_line
        else:
            # Before the first heading (e.g. name/contact) – you can store or ignore
            pass

    # --- FILE WRITING BLOCK (Ensures consistent spacing) ---
    with open("output.txt", "w", encoding="utf-8") as f:
        for k, v in sections.items():
            
            # 1. Write the Section Title
            f.write(f"{k}:\n")
            
            # 2. Write the Section Content (cleaned)
            # v.rstrip() removes any extra newlines/spaces from the end of the content.
            f.write(v.rstrip())
            
            # 3. Add the consistent separation (two newlines = one blank line)
            f.write("\n\n")

    return sections

def compare_cv_with_jd(
    jd_text: str,
    resume_text: str,
    model: str = "llama-3.3-70b-versatile",
    api_key: str = API_key,
) -> str:
    from groq import Groq

    client = Groq(api_key=api_key)

    system_prompt = """
You are a strict resume-to-job-description (JD) evaluator designed to simulate an ATS + human recruiter hybrid. Your task is to compare a candidate’s CV against a given Job Description and produce a structured JSON assessment.

You must be strict, evidence-based, and follow all rules below.

---

========================
1. EDUCATION MATCH RULES
========================
- Compare candidate education against JD requirements.
- Hierarchy of degrees:
  PhD > Masters > Bachelors > Diploma > High School
- Higher education may provide advantage ONLY if relevant to the job domain.
- Do NOT overvalue education for practical engineering roles unless explicitly required.
- Extract:
  - Degree
  - Major/Field
  - University
  - Graduation Year
  - CGPA (if available)

Match output:
- yes → fully meets requirement
- partial → related but below requirement
- no → does not meet requirement

---

========================
2. SKILLS MATCH RULES
========================
- Match all technical skills, tools, frameworks, languages, and methodologies from JD.
- IMPORTANT RULE:
  If a skill appears in PROJECTS or EXPERIENCES, it MUST be considered valid even if not listed in Skills section.
- Do NOT penalize poor resume formatting or missing skill lists.

Skill inference allowed:
- Deep learning project → may imply TensorFlow / PyTorch
- Web project → may imply HTML/CSS/JS/React depending on context
- Data project → may imply Python, Pandas, SQL, etc.

Skill categories:
- Required (from JD)
- Candidate (ALL extracted from CV + projects + experience)
- Matched (intersection)
- Gap (ONLY those NOT found anywhere in CV, projects, or experience)

---

========================
3. PROJECTS ANALYSIS
========================
For each project:
- Extract tools, technologies, frameworks, and methods used
- Evaluate relevance to JD:
  - high → directly matches JD skills/domain
  - medium → partially relevant
  - low → weak or unrelated

Projects are strong evidence of capability and must be weighted accordingly.

---

========================
4. EXPERIENCE MATCHING RULES (VERY IMPORTANT)
========================

Experience hierarchy (strength order):
1. Full-time relevant experience (strongest)
2. Part-time / contract work
3. Internship (weakest professional experience)
4. Academic projects (supporting evidence only)

IMPORTANT RULES:
- Internship experience MUST NOT be treated as equivalent to full-time experience.
- 2+ years relevant full-time experience outweighs multiple internships.
- Prefer recent experience over older experience.

Seniority expectations based on JD:
- Entry-level: internships + projects acceptable
- Mid-level: 1–3 years relevant full-time experience expected
- Senior-level: 3+ years strong full-time experience required; internships have minimal impact

Compute:
- duration_years for each role
- total relevant years of experience (weighted)

---

========================
5. RELEVANCE PRIORITY ORDER
========================
When evaluating relevance:
1. Direct JD match (exact skills/domain)
2. Strong inferred match (same stack/domain)
3. Partial match
4. No match

---

========================
6. WEIGHTED SCORING MODEL (0–100)
========================

Final score must be computed using:

- Skills match: 40%
- Experience relevance: 35%
- Projects evidence: 15%
- Education match: 10%

Adjust weights slightly depending on JD seniority:
- Entry-level → increase projects weight
- Senior-level → increase experience weight

SCORING RULES:
- Do NOT inflate score due to education alone
- Do NOT over-credit internships for senior roles
- Strong practical experience outweighs credentials
- Score must reflect real hiring decision logic

---

========================
7. EXPERIENCE WEIGHTING RULE (EXPLICIT)
========================
- Full-time relevant experience = 100% weight
- Internship relevant experience = 40–60% weight
- Academic projects = 20–40% weight

---

========================
8. SKILL VALIDATION RULE
========================
- Skills found in projects or experience are VALID even if missing in skills list.
- Only mark as GAP if skill is not found anywhere in CV.

---

========================
9. OUTPUT REQUIREMENT
========================
[IMPORTANT] You MUST return ONLY valid JSON. No explanations, no extra text.

---

OUTPUT FORMAT:

{
  "education": {
    "required": "<from JD>",
    "candidate": "<from CV>",
    "match": "<yes/no/partial>",
    "notes": "<optional explanation>"
  },
  "skills": {
    "required": ["<JD skills>"],
    "candidate": ["<all extracted skills from CV + projects + experience>"],
    "match": ["<matched skills>"],
    "gap": ["<missing skills not found anywhere>"]
  },
  "projects": [
    {
      "title": "<project title>",
      "tools_methods": ["<tools, frameworks, methods>"],
      "relevance_to_JD": "<high/medium/low>"
    }
  ],
  "experience": [
    {
      "title": "<role>",
      "domain_relevance": "<relevant/not relevant/insufficient evidence>",
      "start_date": "<month year>",
      "end_date": "<month year or Present>",
      "duration_years": "<numeric>"
    }
  ],
  "strengths": ["<key strengths>"],
  "weaknesses": ["<key gaps>"],
  "overall_fit_score": "<0-100>"
}

---

FINAL RULES:
- Be strict but fair.
- Prioritize real-world applicable experience over certificates or education.
- Internship ≠ full-time experience.
- Skills must be inferred from ALL sections, not just skill list.
- Output must be deterministic, structured, and recruiter-like.

"""

    user_prompt = f"""
### Job Description:
{jd_text}

### Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=1500,
    )

    # This should now be a pure JSON string
    return response.choices[0].message.content


def _json_to_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _build_jd_text(job: dict) -> str:
    return (
        f"Job Title: {job.get('job_title', '')}\n\n"
        f"Short Description:\n{job.get('short_description', '')}\n\n"
        f"Job Metadata:\n{_json_to_text(job.get('job_metadata'))}"
    )


def _build_application_profile_text(meta: dict) -> str:
    parent_data = meta.get("applications", {}) 
    application = parent_data.get("metadata", {})
    return (
        f"Name: {application.get('name', '')}\n"
        f"Email: {application.get('email', '')}\n"
        f"Phone: {application.get('phone', '')}\n"
        f"City: {application.get('city', '')}\n"
        f"LinkedIn: {application.get('linkedin', '')}\n"
        f"Portfolio: {application.get('portfolio', '')}\n\n"
        f"Education:\n"
        f"- Degree: {application.get('degree', '')}\n"
        f"- Major: {application.get('major', '')}\n"
        f"- University: {application.get('university', '')}\n"
        f"- Graduation Year: {application.get('grad_year', '')}\n"
        f"- CGPA: {application.get('cgpa', '')}\n\n"
        f"Experiences:\n{_json_to_text(application.get('experiences'))}\n\n"
        f"Skills:\n{_json_to_text(application.get('skills'))}\n\n"
        f"Projects:\n{_json_to_text(application.get('projects'))}\n"
    )


def _extract_overall_fit_score(comparison_json_text: str):
    try:
        parsed = json.loads(comparison_json_text)
        raw_score = parsed.get("overall_fit_score")
        if raw_score is None:
            return None
        score = int(float(str(raw_score)))
        return max(0, min(100, score))
    except Exception:
        match = re.search(r'"overall_fit_score"\s*:\s*"?(\d{1,3})"?', comparison_json_text)
        if not match:
            return None
        score = int(match.group(1))
        return max(0, min(100, score))


def _upsert_resume_score(job_id: str, applicant_id: str, score: int, resume_evaluation, status: str):
    debug_log(f"Upserting score/evaluation. job_id={job_id}, applicant_id={applicant_id}, score={score}, status={status}")
    existing = (
        supabase.table("job_applications")
        .select("id")
        .eq("job_id", job_id)
        .eq("applicant_id", applicant_id)
        .limit(1)
        .execute()
    )

    debug_log(f"job_applications existing rows: {len(existing.data) if existing and existing.data else 0}")

    if existing.data:
        (
            supabase.table("job_applications")
            .update(
                {
                    "resume_score": score,
                    "resume_evaluation": resume_evaluation,
                    "status": status, # neeed to change 
                }
            )
            .eq("job_id", job_id)
            .eq("applicant_id", applicant_id)
            .execute()
        )
        debug_log("Updated existing job_applications row")
    else:
        (
            supabase.table("job_applications")
            .insert(
                {
                    "job_id": job_id,
                    "applicant_id": applicant_id,
                    #name should be here according to current scenario, but lets detele it later from the database job_applications 
                    #"name" : "candidate",
                    "status": status,
                    "resume_score": score,
                    "resume_evaluation": resume_evaluation,
                }
            )
            .execute()
        )
        debug_log("Inserted new job_applications row")

# ------------------------- MAIN ---------------------F----

router = APIRouter()


def screen_new_applications_for_job(job_id: str, company_id: str):
    debug_log("============================================================")
    debug_log(f"screen_new_applications_for_job called with job_id={job_id}, company_id={company_id}")

    job_response = (
        supabase.table("jobs")
        .select("id,company_id,status,job_title,job_metadata,short_description")
        .eq("id", job_id)
        .eq("company_id", str(company_id))
        .in_("status", ["open", "active"])
        .limit(1)
        .execute()
    )

    if not job_response.data:
        debug_log("No open/active job found for this company; collecting diagnostics")

        by_id = (
            supabase.table("jobs")
            .select("id,company_id,status")
            .eq("id", job_id)
            .limit(1)
            .execute()
            .data
        ) or []

        if not by_id:
            reason = "Job id does not exist"
            debug_log(reason)
        else:
            row = by_id[0]
            row_company = str(row.get("company_id"))
            row_status = str(row.get("status"))
            if row_company != str(company_id):
                reason = f"Job belongs to a different company (job.company_id={row_company}, token.user_id={company_id})"
                debug_log(reason)
            elif row_status not in {"open", "active"}:
                reason = f"Job status is '{row_status}', expected open/active"
                debug_log(reason)
            else:
                reason = "Job exists but query did not return it (unexpected filter issue)"
                debug_log(reason)

        return {
            "job_id": job_id,
            "total_applications": 0,
            "new_applications": 0,
            "processed": 0,
            "failed": 0,
            "results": [],
            "errors": [reason],
        }

    job = job_response.data[0]
    jd_text = _build_jd_text(job)


    pending_response = (
        supabase.table("job_applications")
        # 1. Select columns from job_applications
        # 2. Use 'applications(...)' to join and get columns from the parent table
        .select("""
            applicant_id, 
            resume_evaluation, 
            applications!applicant_id (
                metadata
            )
        """)
        .eq("job_id", job_id)
        .eq("status", AppStatus.RESUME_RECEIVED.value)
        .execute()
    )
    print("Pending applications response:", pending_response)
    pending_applications = pending_response.data or []

    debug_log(f"New candidates found to process: {len(pending_applications)}")

    os.makedirs(EVALS_DIR, exist_ok=True)

    processed_results = []
    failed_results = []

    for application in pending_applications:
        # 1. Get the ID directly from job_applications
        applicant_id = str(application.get("applicant_id"))
        
        # 2. Extract the metadata from the joined 'applications' table
        # This matches the 'applications!applicant_id' structure above
        joined_data = application.get("applications", {})
        metadata = joined_data.get("metadata", {})

        if not metadata:
            debug_log(f"Warning: No metadata found for applicant {applicant_id}")
            continue

        try:
            # 3. Pass the metadata dictionary to your formatter
            resume_text = _build_application_profile_text(metadata)
            comparison_json = compare_cv_with_jd(
                jd_text=jd_text,
                resume_text=resume_text,
                model=model_id,
                api_key=API_key,
            )

            score = _extract_overall_fit_score(comparison_json)
            if score is None:
                score = 0

            try:
                parsed_evaluation = json.loads(comparison_json)
            except Exception:
                parsed_evaluation = {"raw": comparison_json}

            parsed_evaluation["overall_fit_score"] = score

            _upsert_resume_score(
                job_id=job_id,
                applicant_id=applicant_id,
                score=score,
                resume_evaluation=parsed_evaluation,
                status=AppStatus.RESUME_GRADED.value
            )

            comparison_file = os.path.join(EVALS_DIR, f"{job_id}_{applicant_id}_comparison.json")
            with open(comparison_file, "w", encoding="utf-8") as file:
                file.write(json.dumps(parsed_evaluation, ensure_ascii=False, indent=2))

            processed_results.append(
                {
                    "applicant_id": applicant_id,
                    "resume_score": score,
                    "comparison_file": comparison_file,
                }
            )
            debug_log(f"Applicant processed successfully: {applicant_id}")
        except Exception as error:
            error_message = str(error)
            debug_log(f"Error processing applicant_id={applicant_id}: {error_message}")
            debug_log(traceback.format_exc())
            failed_results.append({"applicant_id": applicant_id, "error": error_message})

    debug_log(
        f"Screening complete. total={len(pending_applications)}, new={len(pending_applications)}, processed={len(processed_results)}, failed={len(failed_results)}"
    )

    return {
        "job_id": job_id,
        "total_applications": len(pending_applications),
        "new_applications": len(pending_applications), # dont need this if we process at a single time 
        "processed": len(processed_results),
        "failed": len(failed_results),
        "results": processed_results,
        "errors": failed_results,
    }


@router.post("/process-job/{job_id}")
def process_job_from_database(job_id: str, user=Depends(auth_middleware)):
    user_id = getattr(user, "id", None) if user is not None else None
    debug_log(f"process_job_from_database called with user_id={user_id}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    return screen_new_applications_for_job(job_id=job_id, company_id=str(user_id))