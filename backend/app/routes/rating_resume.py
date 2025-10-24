from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from app.config import config

router = APIRouter()

load_dotenv()  # Load environment variables from .env file
# Initialize OpenAI client (make sure OPENAI_API_KEY is in your .env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request and response models
class TextRatingRequest(BaseModel):
    text: str
    instruction: str = "Rate the skills from 0 to 1 upto a 3 decimal place."

class TextRatingResponse(BaseModel):
    rating: float
    feedback: str

@router.post("/rate-text", response_model=TextRatingResponse)
async def rate_text(data: TextRatingRequest):
    """
    Sends text + instruction to OpenAI API and returns a rating + feedback.
    """
    # Create a prompt to send
    prompt = f"""
    {data.instruction}
    Text: {data.text}
    Respond with a JSON object like this:
    {{
        "rating": <number between 0 and 10>,
        "feedback": "<your feedback>"
    }}
    """

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # fast + cheap model
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract text from response
        reply = response.choices[0].message.content.strip()

        # Try to parse the JSON reply
        import json
        parsed = json.loads(reply)

        rating = float(parsed.get("rating", 0))
        feedback = parsed.get("feedback", "No feedback given.")

        return TextRatingResponse(rating=rating, feedback=feedback)

    except Exception as e:
        # Fallback error response
        return TextRatingResponse(
            rating=0.0,
            feedback=f"Error while rating text: {str(e)}"
        )


#rating still has to be saved in the database 
# this is just the API call to get the rating from openAI