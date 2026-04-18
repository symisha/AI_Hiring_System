from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from app.database.db_connection import supabase
from app.services.judge0 import Judge0PublicService

router = APIRouter()

class Solution(BaseModel):
    question_id: int
    code: str

class TestSubmission(BaseModel):
    # We use applicant_id to link the final result
    applicant_id: str 
    solutions: List[Solution]

@router.post("/submit-test/{job_id}")
def submit_test(job_id: str, submission: TestSubmission):
    # 1. Fetch the "Answer Key" from the JOBS table (where the AI saved them)
    job_data = supabase.table("jobs").select("test").eq("id", job_id).single().execute()
    
    if not job_data.data or not job_data.data.get('test'):
        raise HTTPException(status_code=404, detail="No test found for this job.")
    
    answer_key = job_data.data['test']
    judge = Judge0PublicService() 
    
    results_log = []
    points_earned = 0

    # 2. Iterate and Grade using Judge0
    for sol in submission.solutions:
        meta = next((q for q in answer_key if q['id'] == sol.question_id), None)
        
        if meta:
            report = judge.run_automated_test(
                candidate_code=sol.code,
                question_meta=meta
            )
            
            if report['success']:
                points_earned += 1
            
            results_log.append({
                "question_id": sol.question_id,
                "passed": report['success'],
                "actual": report['actual'],
                "error": report.get('error_details')
            })

   # --- 3. Save the attempt to the 'test' table ---
    final_score = f"{points_earned}/{len(answer_key)}"
    
    # We map the solutions to a list of dicts so Supabase stores them as JSONB
    formatted_solutions = [
        {"question_id": sol.question_id, "code": sol.code} 
        for sol in submission.solutions
    ]

    test_insert_response = supabase.table("test").insert({
        "solution": formatted_solutions, # This saves the actual code!
        "score": final_score,
        "logs": results_log
    }).execute()

    if not test_insert_response.data:
        raise HTTPException(status_code=500, detail="Failed to save results to test table.")

    # Capture the UUID to link it in the next step
    generated_test_uuid = test_insert_response.data[0]['uuid']


    # --- 4. Update the hub (job_applications) ---
    # We find the row that matches both the applicant and the specific job
    supabase.table("job_applications").update({
        "test_ID": generated_test_uuid
    }).eq("applicant_id", submission.applicant_id).eq("job_id", job_id).execute()

    return {
        "message": "Test processed and linked to application", 
        "score": final_score,
        "test_ID": generated_test_uuid
    }