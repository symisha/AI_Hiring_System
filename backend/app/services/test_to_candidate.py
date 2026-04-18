from fastapi import APIRouter
from typing import List
from app.database.db_connection import supabase
router = APIRouter()


@router.get("/get-job-test/{job_id}")
def get_job_test(job_id: str):
    # Pull only the test column
    response = supabase.table("jobs").select("test").eq("id", job_id).single().execute()
    
    if not response.data or not response.data['test_content']:
        return {"error": "No test found for this job"}
    
    # Hide the answers (test_input and expected_output) before sending to candidate
    full_test = response.data['test_content']
    safe_test = [
        {
            "id": q['id'],
            "text": q['question_text'],
            "func": q['function_name']
        } for q in full_test
    ]
    
    return {"questions": safe_test}