import os
import traceback
from pathlib import Path
import requests
import json

from app.database.db_connection import supabase

evaluating_prompt = """### ROLE & GOAL
You are an expert Data Scientist and Machine Learning Engineer acting as a fair and thorough interview grader.
Your goal is to evaluate a candidate's interview responses and produce a structured JSON score report.

### CRITICAL PRE-PROCESSING RULE — READ FIRST
- Each question-answer pair in the interview has a `status` field.
- **You MUST ONLY evaluate questions where `status` is `"valid"`.**
- If `status` is `"discarded"`, `"unknown"`, or anything other than `"valid"`, **SKIP that question entirely.** Do not score it, do not include it in the `details` array, and do not count it toward the `overall_score`.
- Ignore and exclude all introductory, background, and personal-history questions regardless of status.

### EVALUATION RULES (apply to each `valid` technical question)

**1. Answer Order Verification**
- If the candidate answers out of the order the interviewer asked → apply a **–2 penalty** to that question's score.
- The score can never go below **1** due to this penalty.
- If the order is correct → no penalty.

**2. Scoring Scale (1–10)**
Award partial credit if the candidate captures the correct core idea, even if depth is limited.
- **8–10:** Strong understanding, correct concepts, good clarity, mostly complete.
- **5–7:** Correct core idea but lacks depth, examples, or full coverage.
- **3–4:** Basic or partial understanding with at least one correct core idea.
- **1–2:** Mostly incorrect or very unclear.

**3. Conceptual Completeness**
An answer is considered complete if:
- The candidate clearly explains the full conceptual process.
- Key steps and important terminology are present.
- The reasoning is logically correct.

Do NOT penalize for the absence of:
- Mathematical equations or formal derivations.
- Code or detailed proofs.
> Only **concepts and key terminology** matter.

**4. Identify What Is Lacking**
For every evaluated question, describe in the `lacking` field:
- Missing steps in the conceptual explanation.
- Unsupported or vague claims.
- Misunderstandings or factual inaccuracies.
- Lack of clarity or incomplete reasoning.
- If the answer is complete, write `"None"` in the `lacking` field.

**5. Penalize Factual Errors**
- For any clearly incorrect technical statement, apply negative marking to the score.

**6. Evaluate ONLY the Candidate's Actual Words**
- Do NOT infer knowledge the candidate did not demonstrate.
- Do NOT fill in gaps on their behalf.
- Do NOT assume a more sophisticated meaning than what was literally stated.

**7. Repeated Answer**
- If an answer is highly similar to a previous answer in the same interview, mark it as `"repeated"`.
- Set `score = 0`.
- In `lacking`, write: `"Answer is repeated from a previous question; no new content provided."`

**8. Misaligned Answer**
- If the candidate answers a different question than the one asked, mark it as `"misaligned"`.
- Apply zero or partial points.
- In `lacking`, write: `"Answer is misaligned; candidate did not answer the current question."`
- Also apply the **–2 order penalty** if applicable.

### REWARD THE FOLLOWING
- Clarity and logical flow.
- Use of correct and specific terminology.
- Well-structured reasoning.

### FINAL SCORE CALCULATION
- **`overall_score`** = the **sum** of `score` values from all evaluated (valid, technical) questions.
- Do NOT include background/intro questions or skipped (non-valid) questions in the sum.

### STRICT OUTPUT FORMAT
- Respond with ONLY a single, valid JSON object. No markdown, no code fences, no explanations.
- The `details` array must contain exactly one entry per evaluated `valid` technical question.
- `overall_score` MUST be the arithmetic sum of all scores in `details`.

{
  "overall_score": <sum of all scores>,
  "details": [
    {
      "question": "<question text>",
      "answer": "<candidate's answer>",
      "score": <score 1-10>,
      "lacking": "<what the candidate is missing, or 'None'>"
    }
  ]
}

"""

api_key = "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"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def list_directory_contents(directory_path):
    """Return a list of file and folder names in the given directory."""
    try:
        return os.listdir(directory_path)
    except Exception as e:
        print(f"Error reading directory '{directory_path}': {e}")
        return []


def evaluate_interview(conversation):
    """Evaluate the entire interview conversation using Groq API."""
    # Format the conversation — include status so the model can filter by it
    formatted_conversation = ""
    for i, qa in enumerate(conversation, 1):
        question = qa.get("question", "")
        answer = qa.get("answer", "")
        status = qa.get("status", "unknown")
        if question and answer:
            formatted_conversation += (
                f"Question {i}: {question}\n"
                f"Answer {i}: {answer}\n"
                f"Status {i}: {status}\n\n"
            )

    user_prompt = (
        f"Here is the complete interview conversation:\n\n{formatted_conversation}"
        "Evaluate ONLY the questions where status is 'valid'. "
        "Skip all other questions. Return ONLY the JSON object."
    )

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": evaluating_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "max_tokens": 2048
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return "Evaluation could not be completed due to an error."


# ======================== API-CALLABLE FUNCTIONS ========================

def evaluate_interview_file(interview_filename: str) -> dict | None:
    """
    Load a specific interview JSON file, evaluate it with Groq, and return the evaluation dict.
    Returns None if the file is missing, empty, or evaluation fails.
    """
    if not os.path.exists(interview_filename):
        print(f"❌ Interview file not found: {interview_filename}")
        return None

    try:
        with open(interview_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read interview file {interview_filename}: {e}")
        return None

    raw_convos = data.get("conversations", [])
    conversation = []
    for c in raw_convos:
        q = c.get("ai_question")
        a = c.get("user_answer")
        s = c.get("status", "unknown")
        if q and a:
            conversation.append({"question": q, "answer": a, "status": s})

    if not conversation:
        print(f"⚠️ No conversation data in {interview_filename}")
        return None

    print(f"📊 Evaluating {len(conversation)} QA pairs from {interview_filename}...")
    evaluation_text = evaluate_interview(conversation)

    # Parse JSON result from LLM
    try:
        # Strip markdown fences if present
        cleaned = evaluation_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()
        evaluation_json = json.loads(cleaned)
        print(f"✅ Evaluation parsed — overall_score: {evaluation_json.get('overall_score')}")
        return evaluation_json
    except json.JSONDecodeError:
        print(f"⚠️ Evaluation result is not valid JSON, storing raw text")
        return {"raw_text": evaluation_text}


def save_evaluation_to_file(interview_filename: str, evaluation_data: dict) -> None:
    """
    Save the evaluation result to the interview_result/ directory as a JSON file.
    The output filename mirrors the interview filename.
    """
    try:
        os.makedirs("interview_result", exist_ok=True)
        base_name = os.path.basename(interview_filename)  # e.g. interview_<id>_<ts>.json
        result_name = base_name.replace("interview_", "result_", 1)
        result_path = os.path.join("interview_result", result_name)
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(evaluation_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Evaluation saved to file: {result_path}")
    except Exception as e:
        print(f"⚠️ Could not save evaluation file: {e}")
        traceback.print_exc()


def save_evaluation_to_db(candidate_id: str, job_id: str, evaluation_data: dict) -> bool:
    """
    Save the evaluation result to the job_applications table.
    Writes interview_data (full JSON) and interview_score (overall_score integer).
    Matches on applicant_id (candidate_id) + job_id.
    Returns True on success.
    """
    try:
        overall_score = evaluation_data.get("overall_score", None)

        payload = {
            "interview_data": evaluation_data,
        }

        # Write overall_score to interview_score if it exists and is numeric
        if overall_score is not None:
            try:
                payload["interview_score"] = int(overall_score)
            except (ValueError, TypeError):
                print(f"⚠️ overall_score '{overall_score}' is not numeric — skipping interview_score update")

        # Update the matching job application record
        result = (
            supabase.table("job_applications")
            .update(payload)
            .eq("applicant_id", str(candidate_id))
            .eq("job_id", str(job_id))
            .execute()
        )

        if result.data:
            print(f"✅ Evaluation saved to DB — applicant_id={candidate_id}, job_id={job_id}, score={overall_score}")
            return True
        else:
            print(f"⚠️ DB update returned no rows — applicant_id={candidate_id}, job_id={job_id}")
            print("   (Row may not exist yet; evaluation data was not saved)")
            return False

    except Exception as e:
        print(f"❌ Failed to save evaluation to DB: {e}")
        traceback.print_exc()
        return False


def evaluate_and_save_interview(interview_filename: str, candidate_id: str, job_id: str) -> bool:
    """
    Full pipeline: load transcript → evaluate with LLM → save to DB.
    Designed to be called as a background task from the /stop endpoint.
    Returns True if the full pipeline succeeded.
    """
    print(f"🔄 Starting evaluation pipeline for {interview_filename}")
    print(f"   candidate_id={candidate_id}, job_id={job_id}")

    evaluation = evaluate_interview_file(interview_filename)
    if not evaluation:
        print("❌ Evaluation pipeline aborted — no evaluation produced")
        return False

    # Always save to file regardless of DB outcome
    save_evaluation_to_file(interview_filename, evaluation)

    saved = save_evaluation_to_db(candidate_id, job_id, evaluation)
    if saved:
        print("✅ Evaluation pipeline complete")
    else:
        print("⚠️ Evaluation produced but DB save failed")
    return saved


if __name__ == "__main__":
    interview_path = "interviews"
    evaluations_path = "evaluations"  # ✅ Create separate folder for evaluations
    
    # ✅ Create evaluations directory if it doesn't exist
    os.makedirs(evaluations_path, exist_ok=True)
    
    contents = list_directory_contents(interview_path)
    print(f"Contents of {interview_path}:")
    
    for item in contents:
        print(item)
        item_path = os.path.join(interview_path, item)
        
        if os.path.exists(item_path):
            with open(item_path, "r") as f:
                data = json.load(f)

            # 1) get list from "conversations"
            raw_convos = data.get("conversations", [])

            # 2) map ai_question/user_answer/status -> question/answer/status
            conversation = []
            for c in raw_convos:
                q = c.get("ai_question")
                a = c.get("user_answer")
                s = c.get("status", "unknown")
                if q and a:
                    conversation.append({"question": q, "answer": a, "status": s})

            # 3) now check if we have anything to evaluate
            if conversation:
                print(f"\nEvaluating full interview in '{item}'...")
                evaluation_text = evaluate_interview(conversation)
                print("\nInterview Evaluation:")
                print(evaluation_text)
                print("\n" + "-"*50 + "\n")
                
                # ✅ Save evaluation to JSON file
                evaluation_filename = item.replace(".json", "_evaluation.json")
                evaluation_file_path = os.path.join(evaluations_path, evaluation_filename)
                
                # ✅ Try to parse as JSON, if fails save as text
                try:
                    # Try parsing the evaluation as JSON
                    evaluation_json = json.loads(evaluation_text)
                    evaluation_data = {
                        "interview_file": item,
                        "session_id": data.get("session_id"),
                        "language": data.get("language"),
                        "evaluated_at": data.get("started_at"),
                        "evaluation": evaluation_json
                    }
                except json.JSONDecodeError:
                    # If not valid JSON, save as text
                    evaluation_data = {
                        "interview_file": item,
                        "session_id": data.get("session_id"),
                        "language": data.get("language"),
                        "evaluated_at": data.get("started_at"),
                        "evaluation": {
                            "raw_text": evaluation_text
                        }
                    }
                
                # ✅ Write to file
                with open(evaluation_file_path, "w", encoding="utf-8") as eval_file:
                    json.dump(evaluation_data, eval_file, ensure_ascii=False, indent=2)
                
                print(f"✅ Evaluation saved to: {evaluation_file_path}")
                
            else:
                print(f"No conversation data found in '{item}'")
        else:
            print(f"JSON file '{item_path}' not found.")

