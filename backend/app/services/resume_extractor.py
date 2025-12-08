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
from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
from fastapi import APIRouter, Depends                     # Import FastAPI class to create the web


def get_jd_from_supabase(bucket: str, filename: str):
    data = supabase.storage.from_(bucket).download(filename)
    return data.decode("utf-8")  # JSON text





# Local directory to save files
LOCAL_DIR = "uploads"
os.makedirs(LOCAL_DIR, exist_ok=True)
def download_all_files(bucket_name: str, folder_prefix: str = ""):
    LOCAL_UPLOADS_DIR = "uploads"
    os.makedirs(LOCAL_UPLOADS_DIR, exist_ok=True)
    """
    Download all files from a Supabase bucket/folder into LOCAL_UPLOADS_DIR
    """
    files = supabase.storage.from_(bucket_name).list(path=folder_prefix)
    
    if not files:
        print(f"No files found in bucket/folder '{folder_prefix}'.")
        return

    for file in files:
        remote_path = file['name']  # e.g., "resume1.pdf"
        local_path = os.path.join(LOCAL_UPLOADS_DIR, os.path.basename(remote_path))

        try:
            file_data = supabase.storage.from_(bucket_name).download(remote_path)
            with open(local_path, "wb") as f:
                f.write(file_data)
            print(f"Downloaded {remote_path} -> {local_path}")
        except Exception as e:
            print(f"Error downloading {remote_path}: {e}")

# Usage
  # '' = root of bucket
# ------------------------
# Example usage
# ------------------------



# ------------------------- CONFIG -------------------------
# Prefer env vars; falls back to your literal for convenience
#GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
#client = Groq(api_key=GROQ_API_KEY)

#MODEL = "gemma3:4b"            # Ollama local model for comparison
#JD_JSON_FILE = get_jd_from_supabase(                  )#JD_PDF= "jd_extraction.json"
UPLOADS_DIR = "uploads"        # resumes (PDFs) are read only from here
RESUMES_JSON_DIR = "extracted_resumes"   # individual extracted resume JSON files
EVALS_DIR = "evaluations"                # individual evaluation JSON files



#os.makedirs(JD_IMG_DIR, exist_ok=True)
#os.makedirs(RESUME_IMG_DIR, exist_ok=True)
#os.makedirs(RESUMES_JSON_DIR, exist_ok=True)
#os.makedirs(EVALS_DIR, exist_ok=True)


model_id = "llama-3.1-8b-instant"
API_key = "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"

def save_json_result(result_text, filename) -> bool:
    if result_text:
        try:
            parsed = json.loads(result_text)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved JSON to: {filename}")
            return True
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON, saving raw text to {filename}.txt ({e})")
            with open(f"{filename}.txt", "w", encoding="utf-8") as f:
                f.write(result_text)
            return False
    else:
        print("⚠️ No result to save")
        return False

def load_jd_file(file_path):
    file_path = Path(file_path).resolve()
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f), str(file_path)

def load_all_resume_files(directory):
    resume_files = {}
    dir_path = Path(directory).resolve()
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")
    for json_file in dir_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                resume_data = json.load(f)
                resume_name = json_file.stem
                resume_files[resume_name] = {"data": resume_data, "path": str(json_file)}
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    return resume_files


def get_resume_files_from_uploads(uploads_dir=UPLOADS_DIR):
    resumes = []
    p = Path(uploads_dir)
    if not p.exists():
        print(f"⚠️ Uploads directory '{uploads_dir}' not found!")
        return []
    for pdf in p.glob("*.pdf"):
        resumes.append({"candidate_id": pdf.stem, "resume_filepath": str(pdf), "resume_filename": pdf.name})
    return resumes


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
def extract_years_experience(text):
    pattern = r'(\d{4})[–\-—\.]{1,3}(\d{4})'
    
    match = re.search(pattern, text)
    
    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        
        # Calculate the duration
        duration = end_year - start_year
        return duration
    else:
        # Return 0 if no matching year range is found
        return 0

def extract_jd_section(JD_txt, JD):

    doc = fitz.open(JD)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    with open(JD_txt, "w") as f:
        f.write(full_text)


def extract_years_experience(text):
    pattern = r'(\d{4})[–\-—\.]{1,3}(\d{4})'
    
    match = re.search(pattern, text)
    
    if match:
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        
        # Calculate the duration
        duration = end_year - start_year
        return duration
    else:
        # Return 0 if no matching year range is found
        return 0


def compare_cv_with_jd(
    jd_text: str,
    resume_text: str,
    model: str = "llama-3.1-8b-instant",
    api_key: str = API_key,
) -> str:
    from groq import Groq

    client = Groq(api_key=api_key)

    system_prompt = """
You are an extremely strict and literal resume analyst. Your job is to compare a CV (resume) with a Job Description (JD) for ANY type of role and produce a realistic, conservative assessment.

CRITICAL RULES:
- Do NOT assume the candidate has a skill, tool, certification, or experience unless it is explicitly mentioned in the CV.
- Do NOT infer competence based on degree alone (e.g., business degree ≠ business analytics, CS degree ≠ strong programming).
- If the CV does not clearly demonstrate a requirement listed in the JD, treat it as a missing or weak match.
- Be conservative with your similarity score. If something is unclear or implied but not explicit, count it as missing.

Your output must include:

1. **Overall Relevance**
   - Briefly describe in plain language how relevant the CV is to the JD based ONLY on explicit evidence.

2. **Education Match**
   - Evaluate whether the candidate’s listed education meets the JD’s stated education requirements.
   - Do NOT assume additional coursework, concentrations, or specializations unless explicitly listed.

3. **Years of Experience Match**
   - Assess the JD’s required years of experience against the CV’s relevant experience, counting only what can be calculated from explicit start–end dates or clearly stated durations.
   - [IMPORTANT] For any entry listed as “<Month Year> – Present,” treat “Present” as the current year (2025).
   - Example: Aug 2024 – Present → calculate as 2024–2025.
   - If the timeline is unclear, label it as “insufficient evidence.”
   - [IMPORTANT] Any experience that is not clearly relevant to the JD’s domain or responsibilities must be marked as not relevant and excluded from the total experience calculation.

4. **Strengths / Matches**
   - List concrete strengths that clearly match the JD.
   - Each bullet must reference explicit CV evidence such as:
     - job responsibilities
     - tools or technologies
     - skills
     - achievements
     - certifications
     - domain experience
     - projects

5. **Gaps / Missing Requirements**
   - List all job requirements from the JD that are missing, weakly supported, or not clearly demonstrated in the CV.
   - Include missing:
     - skills
     - tools/software
     - responsibilities
     - certifications/licenses
     - domain/industry experience
     - soft skills explicitly required by the JD
   - Be strict and literal—assume nothing.

6. **Fit Assessment**
   - Classify the candidate strictly as one of:
     - "strong fit"
     - "moderate fit"
     - "weak fit"
     - "not a fit"
   - Base the assessment ONLY on explicit JD requirements and explicit CV evidence.

7. **Similarity Score (0–100%)**
   - First, explain your scoring logic in one concise sentence (e.g., “Score is based on percentage of core requirements explicitly matched.”)
   - Then give a numeric similarity score.
   - Use these strict scoring bands:
     - **80–100%** → Very close match; most core requirements clearly present.
     - **60–79%** → Reasonable match; some major gaps exist.
     - **40–59%** → Weak match; several core requirements missing.
     - **0–39%** → Very limited relevance.

IMPORTANT:
- ALWAYS err on the side of being strict, not generous.
- If the CV does not explicitly state a requirement, treat it as missing.
- Do NOT infer transferable skills unless explicitly described.

====================================================================
============================= OUTPUT ===============================
====================================================================

OUTPUT FORMAT (CRITICAL — FOLLOW EXACTLY):

You MUST output ONLY a single JSON object.

- The output MUST be valid JSON.
- The output MUST NOT include any explanation, commentary, markdown, or code fences (NO ```json).
- The output MUST contain ONLY the JSON object and NOTHING else.
- The JSON MUST contain these EXACT keys (do not rename, remove, or add keys):

{
  "Overall Relevance": "",
  "Education Match": "",
  "Years of Experience Match": "",
  "Strengths / Matches": [],
  "Gaps / Missing Requirements": [],
  "Fit Assessment": "",
  "Similarity Score": 0
}

RULES FOR EACH FIELD:
- "Overall Relevance": string summarizing relevance.
- "Education Match": string describing education alignment.
- "Years of Experience Match": string explaining years relevance.
- "Strengths / Matches": array of strings.
- "Gaps / Missing Requirements": array of strings.
- "Fit Assessment": must be one of:
    - "strong fit"
    - "moderate fit"
    - "weak fit"
    - "not a fit"
- "Similarity Score": integer from 0 to 100.

DO NOT output anything except the JSON object.

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

# ------------------------- MAIN -------------------------

router = APIRouter()


@router.get("/process-uploads")
def process_uploads_endpoint():
    logs = []   # store all messages for response

    def log(msg):
        print(msg)       # still prints to console
        logs.append(msg) # also store for API response

    download_all_files("Resumes", "")
    log("Downloaded all files from bucket 'Resumes'")

    JD_txt = get_jd_from_supabase("Job Description", "0de15667-02f8-40ce-9887-9eeafefd9abb.json")

    UPLOADS_DIR = "uploads"
    RESUMES_JSON_DIR = "extracted_resumes"
    EVALS_DIR = "evaluations"

    log("=" * 60)
    log("PROCESSING JD + RESUMES FROM 'uploads/'")
    log("=" * 60)

    # ----- PROCESS RESUMES -----
    resume_entries = get_resume_files_from_uploads(UPLOADS_DIR)
    log(f"Found {len(resume_entries)} PDF(s) in '{UPLOADS_DIR}'")

    processed = 0
    errors = []

    for i, resume_info in enumerate(resume_entries, start=1):
        resume_path = resume_info["resume_filepath"]
        resume_name = resume_info["candidate_id"]

        log(f"PROCESSING RESUME {i}/{len(resume_entries)}: {resume_path}")

        if not os.path.exists(resume_path):
            msg = f"⚠️ File not found, skipping: {resume_path}"
            log(msg)
            errors.append(msg)
            continue

        try:
            # Extract Resume
            sections = extract_resume_sections(resume_path)

            with open("output.txt", "w") as f:
                for k, v in sections.items():
                    f.write(f"{k}:\n{v}\n\n")

            with open("output.txt", "r") as f:
                resume_text = f.read()

            jd_bytes = supabase.storage.from_("Job Description").download("0de15667-02f8-40ce-9887-9eeafefd9abb.json")
            jd_text = jd_bytes.decode("utf-8")

            log("Comparing resume with JD...")

            comparison_result = compare_cv_with_jd(
                jd_text, resume_text, model_id, api_key=API_key
            )

            result_path = os.path.join(
                RESUMES_JSON_DIR, f"{resume_name}_comparison.json"
            )

            with open(result_path, "w", encoding="utf-8") as f:
                f.write(comparison_result)

            log(f"✅ Comparison result saved to: {result_path}")
            processed += 1

        except Exception as e:
            err = f"Error processing resume {resume_path}: {e}"
            log(err)
            errors.append(err)

    # ----- RETURN EVERYTHING -----
    return {
        "status": "completed",
        "total_files_found": len(resume_entries),
        "successfully_processed": processed,
        "errors": errors,
        "logs": logs
    }
