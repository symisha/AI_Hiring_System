from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Any
from app.services.testMakingProcess import AITestProcessor
from app.services.judge0 import Judge0PublicService
from app.auth_middleware import get_current_user


router = APIRouter()


#improper naming , should be test 

class testRequest(BaseModel):
    role: str  # Only role remains

@router.post("/generate-test/{job_id}")
def generate_test(
    job_id: str, 
    num_questions: int = Query(default=3, ge=1), 
    data: testRequest = None,
    user=Depends(get_current_user)
):
    ai = AITestProcessor()
    judge = Judge0PublicService()

    # Pass the ID from URL and count from Query
    # The 'role' is passed from the body for extra AI context
    questions = ai.generate_technical_test(
        job_id=job_id,
        num_questions=num_questions,
        role=data.role if data else "Technical Role"
    )

    return {
        "status": "success",
        "questions": questions
    }


class SubmissionRequest(BaseModel):
    candidate_code: str
    function_name: str
    test_input: str
    expected_output: Any

@router.post("/test-submission-to-judge0")
def test_submission(data: SubmissionRequest, user=Depends(get_current_user)):
    judge = Judge0PublicService()
    
    # This calls the polling logic we built
    result = judge.run_automated_test(
        candidate_code=data.candidate_code,
        question_meta={
            "function_name": data.function_name,
            "test_input": data.test_input,
            "expected_output": data.expected_output
        }
    )
    
    return result