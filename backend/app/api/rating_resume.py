from fastapi import APIRouter
from pydantic import BaseModel

# ✅ Create a router instance (not a FastAPI app)
router = APIRouter()

# Define request model
class TextRatingRequest(BaseModel):
    text: str

# Define response model
class TextRatingResponse(BaseModel):
    rating: float
    feedback: str

# Define your endpoint
@router.post("/rate-text", response_model=TextRatingResponse)
async def rate_text(data: TextRatingRequest):
    # Simple logic: if text is long, give higher score
    score = min(len(data.text) / 100, 10)
    return TextRatingResponse(rating=score, feedback="Looks good!")
# This file defines an API router for rating text, which can be included in the main FastAPI app.