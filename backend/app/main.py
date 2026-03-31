import uvicorn  # ASGI server used to run FastAPI apps (like "npm start" for Node)
from fastapi import FastAPI, Depends  # Main FastAPI class used to create the web application instance
from fastapi.middleware.cors import CORSMiddleware  # Middleware to handle CORS (Cross-Origin Resource Sharing)
from pydantic import BaseModel  # Used to define and validate data models (for requests/responses) with type checking
from app.config.config import Settings # Import the settingsclass to access environment variables

# Import routes (import nested routers directly to avoid circular/package import issues)
from app.routes import rating_resume, apply
from app.routes.dashboard_essentials.dashboard_info import router as dashboard_info_router
from app.routes.dashboard_essentials.profile_preview_router import router as profile_preview_router
from app.services.resume_extractor import router as resume_extractor_router
from app.routes.specific_job_routes import delRouter
# Database
from app.database.db_connection import supabase  # Supabase client instance


#Import from services 
from app.services import job_description

# Auth middleware
from app.auth_middleware import auth_middleware, get_current_user_id

# Create FastAPI app instance
app = FastAPI()

# Allowed origins for CORS
origins = [
    # "http://localhost:8000",  # Frontend URL
]

# Include your endpoints
app.include_router(rating_resume.router, prefix="/routes", tags=["rating"])
app.include_router(dashboard_info_router, prefix="/routes/dashboard_essentials", tags=["database"])
app.include_router(profile_preview_router, prefix="/routes/dashboard_essentials", tags=["database"])
app.include_router(apply.router, prefix="/routes", tags=["apply"])
app.include_router(delRouter, prefix="/routes", tags=["delete_job"])
app.include_router(resume_extractor_router, prefix="/services", tags=["resume_extractor"])
app.include_router(dashboard_info_router, prefix="/routes/dashboard_essentials", tags=["complaints"])
app.include_router(job_description.router, prefix="/services", tags=["job_description"])


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[Settings.FRONTEND_URL],  # List of allowed origins (frontend URLs)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root GET endpoint
@app.get("/")
async def read_root():
    return {"Hello": "World"}

# Root POST endpoint
@app.post("/")
async def create_item(item: dict):
    return {"item_received": item}

# Test endpoint to verify environment variable loading
@app.get("/whoami")
async def who_am_i(user=Depends(auth_middleware)):
    return user

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



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