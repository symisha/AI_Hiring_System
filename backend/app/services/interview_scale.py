
import os

from groq import Groq
from app.database.db_connection import supabase
from dotenv import load_dotenv
from app.services.skill_graph import build_skill_map, build_interview_flow

load_dotenv()

# ── Fetch job details ─────────────────────────────────────────────────────────
def fetch_job_details(job_id):
    response = supabase.table("jobs").select(
        "id, job_title, job_metadata,seniority"
    ).eq("id", job_id).execute()
    if response.data:
        print(f"Response from Supabase: {response.data}")
        return response.data[0]
    return None


# ── Prompt — edit freely ──────────────────────────────────────────────────────
INTERVIEW_SYSTEM_PROMPT = """\
You are a senior technical interviewer conducting a real job interview.

Job Title  : {job_title}
Seniority  : {seniority}

You have been given a skill graph that defines what matters for this role.
Use it as your strict question bank — do not ask about anything outside it.

SKILL GRAPH:
{skill_graph}

(Skills with higher scores are more important — weight your questions accordingly.)

═══════════════════════════════════════════════
INTERVIEW STRUCTURE — FOLLOW STRICTLY
═══════════════════════════════════════════════

STAGE 1 — Background (max 3 questions)
Ask about past experience and real projects tied directly to the skills in the graph.
  - Ask what they have built or worked on that involves these skills
  - Ask about tools they used, scale they worked at, and problems they solved
  - Do NOT ask "tell me about yourself" or any generic opener
  - Do NOT go deeper than 1 follow-up per background answer

STAGE 2 — Core + Applied Skills (7–8 questions total)
Draw questions from CORE and APPLIED skills in the graph.
  - Prioritize higher-scored skills — they must be covered
  - Lower-scored skills should each get at least one question
  - Questions must be conceptual AND practical — not definitions
    BAD:  "What is overfitting?"
    GOOD: "You're training a model and validation loss starts rising while training loss drops —
           walk me through what you'd investigate and how you'd fix it."
  - Each question should touch a different skill — do not drill into one area
  - Build naturally from previous answers — reference what the candidate said
  - Increase depth progressively but stay broad — cover the graph, not one corner of it

STAGE 3 — Behavioral (woven in, not a separate block)
Do not ask behavioral questions as a standalone block.
Weave them in naturally where they fit — e.g., after a technical answer that hints at
a challenge, pivot with a light behavioral angle before moving to the next skill.

═══════════════════════════════════════════════
CONVERSATION RULES — CRITICAL
═══════════════════════════════════════════════

1. Ask ONE question at a time. Never stack two questions.

2. After every candidate response, do exactly one of:
   - Follow up naturally if the answer was vague or opened something worth probing
     ("You mentioned X — how did that actually work in practice?")
   - Acknowledge briefly and transition if the answer was solid
     ("That makes sense, especially around X. Let me shift to something related...")

3. Always reference what the candidate said. Never ask in a vacuum.

4. Never repeat a topic already covered.

5. Never hint, tutor, or explain concepts to the candidate.

6. Do not number questions or name stages out loud.

7. When all questions are done, close professionally and thank the candidate.
   Do not reveal scores, evaluations, or what stage you were in.

═══════════════════════════════════════════════
STRICT JSON OUTPUT + STATUS RULES (REQUIRED)
═══════════════════════════════════════════════

You MUST respond with ONLY a single valid JSON object on EVERY turn.
- No markdown, no code fences, no extra text.

Your JSON object MUST contain these keys exactly:
    - "ai_question": your next question for the candidate (ONE question only)
    - "user_answer": the candidate's most recent utterance
    - "status": must be EXACTLY either "valid" or "discarded" (no other values)

Status selection rules:
- Use "valid" ONLY when the candidate's most recent utterance actually answers your immediately previous question.
- Use "discarded" when the candidate's most recent utterance does NOT answer your immediately previous question.
- If you are unsure, choose "discarded" and re-ask the same question.

═══════════════════════════════════════════════
INTERRUPTION + REPEAT RULES (MARK PREVIOUS Q INVALID)
═══════════════════════════════════════════════

If the candidate does NOT answer your last question because they:
    - interrupt / change topic,
    - ask their own question instead of answering,
    - ask for clarification (e.g., "what do you mean by...?"),
    - ask you to repeat (e.g., "repeat please", "say that again", "I didn't hear"),
then you MUST:
    1) Set "status" to "discarded" (this marks the previous question invalid in the log).
    2) Set "ai_question" to the SAME last unanswered question again (repeat it verbatim for repeat-requests).
    3) For clarification requests, you may add ONE short clarifying sentence, then re-ask the same question (still one question total).
    4) Do NOT advance to a new skill/topic.
    5) Do NOT count this as a completed question. Wait until you get a real answer marked "valid".

Only set "status" to "valid" when the candidate actually answers the question you asked.

═══════════════════════════════════════════════
COVERAGE TRACKER (internal — never say this aloud)
═══════════════════════════════════════════════
Before closing, mentally verify:
  ✓ At least 1 question touched each CORE skill
  ✓ At least 1 question touched each APPLIED skill
  ✓ Behavioral angles were woven in at least once
  ✓ Total questions asked: 10–11 max

═══════════════════════════════════════════════
TONE
═══════════════════════════════════════════════
Professional but conversational. Focused, not interrogative.
Feel like a senior engineer having a real technical conversation.

Greet the candidate briefly, explain the format in one sentence, then ask your first question.
"""


# ── Normalize job_metadata for LLM ───────────────────────────────────────────
def format_job_metadata(job):
    m = job.get("job_metadata", {})

    def clean_list(items):
        if isinstance(items, str):
            return items.strip()
        return "\n".join(f"- {i.strip()}" for i in items if i)

    return (
        "Key Skills:\n"
        + clean_list(m.get('Key Skills', '').split('\n')) + "\n\n"
        "Responsibilities:\n"
        + clean_list(m.get('Key Responsibilities', [])) + "\n\n"
        "Required Qualifications:\n"
        + clean_list(m.get('Required Qualifications', [])) + "\n\n"
        "Preferred Qualifications:\n"
        + clean_list(m.get('Preferred Qualifications', [])) + "\n"
    )

# ── Format interview flow for LLM ─────────────────────────────────────────────
def format_interview_flow(interview_flow):
    lines = []
    for stage in ["core", "applied", "behavioral", "background"]:
        if interview_flow.get(stage):
            lines.append(f"{stage.upper()}:")
            for s in interview_flow[stage]:
                lines.append(f"  - {s['skill']} (score: {s['score']})")
    return "\n".join(lines)

def build_prompt(job: dict) -> str:
    # Build the skill map and interview flow
    skill_map = build_skill_map(job["id"] if "id" in job else job.get("job_id"))
    interview_flow = build_interview_flow(skill_map) if skill_map else {}
    skill_graph_str = format_interview_flow(interview_flow)
    return INTERVIEW_SYSTEM_PROMPT.format(
        job_title=job.get("job_title", "N/A"),
        seniority=job.get("seniority", "N/A"),
        skill_graph=skill_graph_str,
    )


# ── Closing detector ──────────────────────────────────────────────────────────
CLOSING_PHRASES = [
    "thank you for your time",
    "that concludes",
    "best of luck",
    "we will be in touch",
    "we'll be in touch",
    "that's all the questions",
    "the interview is now complete",
    "good luck with",
]

def interview_ended(text: str) -> bool:
    return any(phrase in text.lower() for phrase in CLOSING_PHRASES)




# ── Groq API integration ─────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

def groq_stream_chat(messages, temperature=1, max_completion_tokens=1024, top_p=1, stop=None):
    client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else Groq()
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        top_p=top_p,
        stream=True,
        stop=stop
    )
    return completion




def interview_loop(job_id: str):
    # 1. Fetch job
    job = fetch_job_details(job_id)
    if not job:
        print("Job not found.")
        return

    # 2. Build system prompt (now includes skill graph)
    system_prompt = build_prompt(job)

    # 3. Conversation history for Groq
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Begin the interview now."}
    ]

    # 4. Get opening message (streamed)
    print("\nInterviewer: ", end="", flush=True)
    opening_stream = groq_stream_chat(messages)
    opening_text = ""
    for chunk in opening_stream:
        content = chunk.choices[0].delta.content or ""
        opening_text += content
        print(content, end="", flush=True)
    print("\n")
    messages.append({"role": "assistant", "content": opening_text})

    # 5. Conversation loop
    while True:
        try:
            candidate_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInterview ended.")
            break

        if not candidate_input:
            continue
        if candidate_input.lower() in ["exit", "quit"]:
            print("You have exited the interview.")
            break

        messages.append({"role": "user", "content": candidate_input})
        print("\nInterviewer: ", end="", flush=True)
        reply_text = ""
        reply_stream = groq_stream_chat(messages)
        for chunk in reply_stream:
            content = chunk.choices[0].delta.content or ""
            reply_text += content
            print(content, end="", flush=True)
        print("\n")
        messages.append({"role": "assistant", "content": reply_text})

        if interview_ended(reply_text):
            print("=" * 50)
            print("Interview Complete")
            print("=" * 50)
            break


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    job_id = "66132a84-d4bb-4aae-a879-129e7283fbde"
    interview_loop(job_id)
