import uvicorn  # ASGI server used to run FastAPI apps (like "npm start" for Node)
import asyncio
from urllib.parse import urlparse
from fastapi import FastAPI, Depends  # Main FastAPI class used to create the web application instance
from fastapi.middleware.cors import CORSMiddleware  # Middleware to handle CORS (Cross-Origin Resource Sharing)
from pydantic import BaseModel  # Used to define and validate data models (for requests/responses) with type checking
from app.config.config import Settings # Import the settingsclass to access environment variables


# Import routes (import nested routers directly to avoid circular/package import issues)
from app.routes import rating_resume, apply
from app.routes.dashboard_essentials.dashboard_info import router as dashboard_info_router
from app.routes.dashboard_essentials.profile_preview_router import router as profile_preview_router
from app.services.resume_extractor import router as resume_extractor_router
from app.services.shortlisting_resume import router as shortlisting_router
from app.api.interview_api import app1 as interview_ws_app
from app.routes.specific_job_routes import delRouter
from app.services.screening_scheduler import screening_scheduler_loop
from app.routes import interview_process_route
# Database
from app.database.db_connection import supabase  # Supabase client instance


#Import from services 
from app.services import job_description, save_test, submit_test


# Auth middleware

from starlette.middleware.base import BaseHTTPMiddleware

# Create FastAPI app instance
app = FastAPI()

def _origin(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return None


# Allowed origins for CORS
origins = [
    _origin(getattr(Settings, "FRONTEND_URL", None)),
    _origin(getattr(Settings, "FRONTEND_INTERVIEW_URL", None)),
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8081",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://ai-hiring-system-1trg.vercel.app",
    "http://localhost:3000",  
]
origins = [o for o in origins if o]

# Include your endpoints
app.include_router(rating_resume.router, prefix="/routes", tags=["rating"])
app.include_router(dashboard_info_router, prefix="/routes/dashboard_essentials", tags=["database"])
app.include_router(profile_preview_router, prefix="/routes/dashboard_essentials", tags=["database"])
app.include_router(apply.router, prefix="/routes", tags=["apply"])
app.include_router(delRouter, prefix="/routes", tags=["delete_job"])
app.include_router(resume_extractor_router, prefix="/services", tags=["resume_extractor"])
app.include_router(shortlisting_router, prefix="/services", tags=["shortlisting"])
app.include_router(dashboard_info_router, prefix="/routes/dashboard_essentials", tags=["complaints"])
app.include_router(job_description.router, prefix="/services", tags=["job_description"])
app.include_router(save_test.router, prefix="/services", tags=["save_test"])
app.include_router(submit_test.router, prefix="/services", tags=["submit_test"])
app.include_router(interview_process_route.router, prefix="/routes", tags=["make_test"])

app.mount("/ws", interview_ws_app)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#@app.on_event("startup")
#async def _start_screening_scheduler():
#    app.state.screening_scheduler_task = asyncio.create_task(screening_scheduler_loop())


@app.on_event("shutdown")
async def _stop_screening_scheduler():
    task = getattr(app.state, "screening_scheduler_task", None)
    if task:
        task.cancel()

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


#submit the form for resume uplooad ------------------------
from fastapi.responses import JSONResponse
from fastapi import Form, File, UploadFile
import uuid
BUCKET_NAME = "Resumes"


@app.post("/submit")

async def submit_form(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    resume: UploadFile = File(...),
    cover_letter: str = Form(""),
    job_id: str = Form(...)
    ):
    try:
        # Generate unique file name
        file_ext = resume.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        # Read file
        file_bytes = await resume.read()

        # Upload to Supabase
        supabase.storage.from_(BUCKET_NAME).upload(file_name, file_bytes)

        # Public URL
        file_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)

        # Insert into applicants table
        applicant_res = supabase.table("applicants").insert({
            "name": name,
            "email": email,
            "phone": phone,
            #"cover_letter": cover_letter,
            "resume_url": file_url
        }).execute()

        applicant_id = applicant_res.data[0]["id"]

        # Insert into job_applications table
        supabase.table("job_applications").insert({
            "job_id": job_id,
            "applicant_id": applicant_id
        }).execute()

        return {"message": "Application submitted!", "file": file_url}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

#Job description upload endpoint ------------------------
import json
"""   
@app.post("/upload-job")
async def upload_job(
    BUCKET_NAME: str = "Job Description",
    title: str = Form(...),
    description: str = Form(...),
    jd_file: UploadFile = File(...),
    user=Depends(auth_middleware)
):
    #print(get_current_user_id(user))
    try:
        # Check if file is JSON
        if jd_file.content_type != "application/json":
            return JSONResponse({"message": "Only JSON files are allowed"}, status_code=400)

        # Read file content
        file_bytes = await jd_file.read()

        # Optional: validate JSON content
        try:
            json.loads(file_bytes)
        except json.JSONDecodeError:
            return JSONResponse({"message": "Invalid JSON file"}, status_code=400)

        # Generate unique file name
        file_name = f"{uuid.uuid4()}.json"

        # Upload JSON to Supabase bucket
        #supabase.storage.from_(BUCKET_NAME).upload(file_name, file_bytes)

        # Get public URL
        #job_description_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)

        # Insert metadata + file URL into database
        # Some DB schemas do not have a `description` text column — store structured JD in `job_metadata` instead
        job_metadata = None
        try:
            job_metadata = json.loads(file_bytes)
        except Exception:
            job_metadata = {"raw": description}

        supabase.table("jobs").insert({
            "company_id": user.user.id,
            # some schemas use `job_title` instead of `title`
            "job_title": title,
            "job_description_url": job_description_url,
            "job_metadata": job_metadata,
            "status": "open"
        }).execute()

        return JSONResponse({
            "message": "Job description uploaded successfully",
            "job_description_url": job_description_url
        })

    except Exception as e:
        return JSONResponse({"message": "Error uploading JD", "error": str(e)}, status_code=500)
    


    #URL NOT BEING SAVED IN THE DATABASES YET...FIGURE OUT LATER  ------------------------



 """