from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.testMakingProcess import AIInterviewProcessor
from app.services.judge0 import Judge0PublicService


router = APIRouter()

class InterviewRequest(BaseModel):
    role: str  # Only role remains

@router.post("/generate-interview/{job_id}")
def generate_interview(
    job_id: str, 
    num_questions: int = Query(default=3, ge=1), 
    data: InterviewRequest = None
):
    ai = AIInterviewProcessor()
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
    expected_output: str

@router.post("/test-submission")
def test_submission(data: SubmissionRequest):
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