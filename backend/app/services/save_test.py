from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List
from app.database.db_connection import supabase
from app.services.interview_link import verify_interview_token

router = APIRouter()

# 1. Define the Schema for a single Question
class Question(BaseModel):
    id: int
    difficulty: str
    question_text: str
    function_name: str
    test_input: str
    expected_output: Any

# 2. Define the Request Body for saving to a specific Job
class SaveTestRequest(BaseModel):
    job_id: str
    questions: List[Question]



@router.post("/save-test-to-job")
def save_test_to_job(data: SaveTestRequest):
    """
    Saves the generated test directly into the 'test' column 
    of the 'jobs' table for a specific job_id.
    """
    try:
        # Convert list of Pydantic objects to a list of dictionaries
        # Using .model_dump() (Pydantic v2) or .dict() (Pydantic v1)
        questions_json = [q.model_dump() for q in data.questions]
        
        # We update the 'test' column in the 'jobs' table
        # Since you use Supabase, it handles the JSONB serialization automatically
        response = supabase.table("jobs").update({
            "test": questions_json 
        }).eq("id", data.job_id).execute()
        
        # Check if the update actually found a row
        if not response.data:
            raise HTTPException(status_code=404, detail="Job ID not found")
        
        return {
            "status": "success", 
            "message": f"Test successfully linked to job {data.job_id}",
            "data": response.data[0]
        }

    except Exception as e:
        # Detailed error for debugging
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    


@router.get("/get-test/{token}")
def get_test(token: str):
    """Retrieves the test using the token for identification."""
    payload = verify_interview_token(token)
    job_id = payload.get("job_id")
    
    try:
        response = supabase.table("jobs").select("test").eq("id", job_id).single().execute()
        if not response.data or not response.data.get("test"):
            raise HTTPException(status_code=404, detail="No test found")
        
        sanitized_test = [
            {
                "id": q["id"],
                "difficulty": q.get("difficulty"),
                "question_text": q.get("question_text"),
                "function_name": q.get("function_name")
            } for q in response.data["test"]
        ]
        return {"job_id": job_id, "questions": sanitized_test, "applicant_name": payload.get("name")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))