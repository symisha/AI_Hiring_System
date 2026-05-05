import json
import traceback
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.db_connection import supabase
from app.services.judge0 import Judge0PublicService
from app.services.interview_link import verify_interview_token
from app.models.appstage import AppStatus

router = APIRouter()

class Solution(BaseModel):
    question_id: int
    code: str

class TestSubmission(BaseModel):
    token: str
    solutions: List[Solution]

@router.post("/submit-test")
async def submit_test(submission: TestSubmission):
    print(f"DEBUG: Received submission with token: {submission.token[:10]}...") # ADD THIS

    try:
        # 1. Decode the token to get the specific Application UUID
        payload = verify_interview_token(submission.token)
        
        # We use the ID from the token as the Primary Key for job_applications
        target_app_id = payload.get("applicant_id") 
        
        if not target_app_id:
            raise HTTPException(status_code=400, detail="Invalid token: Missing Application ID")

        # 2. Update Status to 'taken' for this specific row ONLY
        supabase.table("job_applications").update({
            "status": AppStatus.ASSESSMENT_TAKEN.value
        }).eq("applicant_id", target_app_id).execute()

        # 3. Retrieve Job ID to find the correct test questions
        app_data = supabase.table("job_applications").select("job_id").eq("applicant_id", target_app_id).single().execute()
        if not app_data.data:
            raise HTTPException(status_code=404, detail="Application record not found")
        
        current_job_id = app_data.data['job_id']

        # 4. Fetch the 'Answer Key'
        job_resp = supabase.table("jobs").select("test").eq("id", current_job_id).single().execute()
        answer_key = job_resp.data.get("test", [])
        
        # 5. Grading via Judge0
        judge = Judge0PublicService()
        results_log = []
        passed_count = 0

        for sol in submission.solutions:
            q_meta = next((q for q in answer_key if q['id'] == sol.question_id), None)
            if q_meta:
                report = judge.run_automated_test(sol.code, q_meta)
                if report.get("success"):
                    passed_count += 1
                
                results_log.append({
                    "question_id": sol.question_id,
                    "passed": report.get("success"),
                    "status": report.get("status"),
                    "error": report.get("error_details")
                })

        # 6. Calculate normalized score (Percentage)
        total_q = len(answer_key)
        final_percentage = round((passed_count / total_q) * 100, 2) if total_q > 0 else 0

        # 7. Insert detailed results into 'test' table
        # test_owner points to the unique job_application id
        supabase.table("test").insert({
            "solution": [s.model_dump() for s in submission.solutions],
            "score": f"{passed_count}/{total_q}",
            "logs": results_log,
            "test_owner": target_app_id
        }).execute()

        # 8. Finalize the main application record
        # This only affects the specific row where id matches
        supabase.table("job_applications").update({
            "status": AppStatus.ASSESSMENT_GRADED.value,
            "assessment_score": final_percentage
        }).eq("applicant_id", target_app_id).execute()

        return {
            "status": "success", 
            "percentage": final_percentage,
            "score": f"{passed_count}/{total_q}"
        }

    except Exception:
        print(f"!!! SYSTEM ERROR !!!\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal processing error")