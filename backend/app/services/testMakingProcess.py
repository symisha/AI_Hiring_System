import os
import json
import langchain_google_genai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class AITestProcessor:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-3-flash-preview")
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_KEY")
        )

    def fetch_job_context(self, job_id):
        # Queries the 'jobs' table for the specific ID from the URL
        response = self.supabase.table("jobs").select("job_metadata, job_title").eq("id", job_id).single().execute()
        
        if not response.data:
            return "General Technical Role"

        raw_metadata = response.data.get("job_metadata")
        job_title = response.data.get("job_title")

        # Handle stringified JSON in the metadata column
        metadata = json.loads(raw_metadata) if isinstance(raw_metadata, str) else raw_metadata
        
        skills = metadata.get("Key Skills", "")
        res_data = metadata.get("Key Responsibilities", [])
        responsibilities = ", ".join(res_data) if isinstance(res_data, list) else str(res_data)
        
        return f"Role: {job_title}. Skills: {skills}. Responsibilities: {responsibilities}"

    def generate_technical_test(self, job_id, num_questions=3, **kwargs):
        # 1. Fetch data from Supabase using the URL ID
        job_context = self.fetch_job_context(job_id)
        role = kwargs.get("role", "Technical Candidate")

        # 2. Your existing prompt (unchanged)
        prompt = f"""
        You are a Senior Technical Lead at a high-growth tech firm. 
        Your goal is to generate {num_questions} coding challenges for the role: {role}. 
        
       ### CONTEXT:
{job_context}

### CORE TASK:
Create challenges that are programmatically gradable via STDOUT comparison.

### RIGID CONSTRAINTS:
1. **Difficulty Scaling:** {num_questions} questions ranging from Easy to Hard based on JD seniority.
2. **Standard Libs Only:** No `numpy`, `pandas`, or external imports. Standard Python 3.x only.
3. **Deterministic Output:** - Floating points MUST be rounded to 2 decimals.
   - Boolean values MUST be "True" or "False" strings.
   - Lists/Sets MUST be returned in sorted order.
4. **No Ambiguity:** Provide a clear "Constraints" section within the `question_text` (e.g., "Input list size: 0 to 10^4").
5. **No System Access:** No `open()`, `import os`, or `requests`.

### JSON SCHEMA:
Return a JSON list of objects:
{{
  "id": integer,
  "difficulty": "Easy|Medium|Hard",
  "question_text": "Detailed problem statement + constraints + edge case behavior.",
  "function_name": "snake_case_name",
  "test_input": "Python literal (e.g., '[1, 2, 3]' or '\"string\"')",
  "expected_output": "The exact stringified result of the function."
}}

### EVALUATION CRITERIA:
The `test_input` must be an edge case that tests the candidate's attention to detail.
"""

        response = self.model.generate_content(prompt)
        
        # 3. Robust JSON cleaning
        # Handles cases where the AI might include markdown triple backticks
        content = response.text.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("\n", 1)[0].strip()
        if content.startswith("json"):
            content = content[4:].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback if the AI output is messy
            return {"error": "Failed to parse AI output as JSON", "raw": response.text}

