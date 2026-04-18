from fastapi import APIRouter, HTTPException
# Import your processor class
from app.services.interview_process import AIInterviewProcessor 

router = APIRouter()
ai_processor = AIInterviewProcessor()

@router.post("/generate-test/{job_id}")
async def generate_test(job_id: str):
    """
    Step 1: Fetches job context from Supabase, 
    asks Gemini for questions, and returns them for review.
    """
    try:
        # 1. Generate the questions using your class logic
        questions = ai_processor.generate_technical_test(job_id=job_id)
        
        if "error" in questions:
            raise HTTPException(status_code=500, detail=questions["error"])
            
        return {
            "job_id": job_id,
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")