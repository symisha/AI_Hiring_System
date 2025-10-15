from fastapi import APIRouter, Request



# takes input from the resume_form on the frontend 
# and sends it to the backend to be stored in a NoSQL DB

router = APIRouter()

@router.post("/api/resume")
async def receive_dynamic_resume(request: Request):
    data = await request.json()  # Parse full JSON body
    print("📥 Received resume data:", data)

    # You can store this as-is in a NoSQL DB (like MongoDB or Firestore)
    # or keep it as a JSON field in PostgreSQL.

    return {"message": "Resume data received", "received_fields": list(data.keys())}