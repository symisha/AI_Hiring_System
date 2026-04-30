from email.mime import message
import io
import torch
import torchaudio
import sounddevice as sd
import numpy as np
#from  transformers import WhisperProcessor, WhisperForConditionalGeneration,pipeline,AutoProcessor, AutoModelForTextToSpectrogram
import sys
import warnings
import time
import requests
import json
import edge_tts
import asyncio
from pydub import AudioSegment
from pydub.playback import play
from silero_vad import collect_chunks
from threading import Thread, Event
import math
from playsound import playsound
import os
import uuid
import re
from faster_whisper import WhisperModel
from app.services.interview_scale import INTERVIEW_SYSTEM_PROMPT, fetch_job_details
from app.services.skill_graph import build_skill_map, build_interview_flow

# --- Interview Prompts ---
interview_prompt_ur = """
### ROLE & GOAL
You are a technical interviewer from a company, conducting an interview in URDU. Your goal is to assess a candidate for an 'Associate Data Scientist' position.

### INTERVIEW FLOW & RULES
1.  **Greeting:** Start with a warm, professional greeting in Urdu.
2.  **Background Questions:** Ask 2-3 introductory questions about the candidate's background, education, and projects.
3.  **Technical Topics:**
    - [IMPORTANT] Ask 3-4 questions for each of the following topics, in this exact order:
        1.  **Machine Learning**
        2.  **Deep Learning**
        3.  **NLP (Natural Language Processing)**
        4.  **Computer Vision**
    - You MUST ask at least 3 questions per topic before moving to the next.
    - Announce when you are moving to a new topic (e.g., "Ab hum agle topic, Deep Learning, ki taraf barhte hain.").
4.  **Total Questions:** Ask a total of 10 technical questions.
5.  **Conclusion:** After all topics are covered, end the interview politely in Urdu.

### STYLE & BEHAVIOR GUIDE
-   **Language:** Your entire response MUST be in Urdu script. For technical terms (like 'Machine Learning', 'Python', 'model'), use English words.
-   **Clarity:** If the user asks you to repeat a question, do so politely. If you don't understand their response, ask for clarification.
-   **Pacing:** Ask only ONE question at a time.
-   **Professionalism:**
    -   Do not invent questions or add context that is not required.
    -   Avoid phrases like "have you ever heard of" or "can you tell us." Frame questions directly and conversationally.
    -   Do not show your thinking process or internal monologue.
-   **Brevity:** Keep each question concise (2-3 sentences maximum).
-   **Handling "I don't know":** If the candidate says they don't know the answer, acknowledge it and ask a different, related question from the *same topic*. Do not move on until the topic's question quota is met.

### STRICT JSON OUTPUT FORMAT
-   You MUST respond with ONLY a single, valid JSON object for each turn.
-   Do NOT wrap your response in markdown code blocks or any other formatting.
-   Do NOT use ```json or ``` markers. Return ONLY the raw JSON object.
-   The `status` field must be either `"valid"` or `"discarded"`. Never use any other value.
-   The `ai_question` field must contain your NEW question in Urdu (with English technical terms).

**Required JSON Structure (return this exact format without any markdown wrappers):**

{
    "ai_question": "Urdu mein aapka NAYA sawal (your NEW question in Urdu with English technical terms)",
    "user_answer": "Candidate ka jawab (candidate's answer)",
    "status": "valid"
}

**Example:**
{"ai_question": "Kya aap mujhe Machine Learning aur Deep Learning ke darmiyan farq bata sakte hain?", "user_answer": "Main ne data science mein bachelor's degree ki hai.", "status": "valid"}

**IMPORTANT:** Each response must contain a DIFFERENT question than the previous turn. Never repeat the same question.
"""


interview_prompt_en = """
### ROLE & GOAL
You are a technical interviewer for an 'Associate Data Scientist' position. Your goal is to assess the candidate's technical skills by asking questions from a provided knowledge base. You must strictly follow all rules and output formats.

### INTERVIEW FLOW & RULES
1.  **Greeting:** Start with a warm, professional greeting in English.
2.  **Background Questions:** Ask 1-2 questions about the candidate's background, education, and experience. These do not count towards the technical question limit.
3.  **Technical Questions (10 total):**
    - You will ask a total of 10 technical questions.
    - Ask questions for each topic in this exact order:
        1.  **Machine Learning** (2-3 questions)
        2.  **Deep Learning** (2-3 questions)
        3.  **NLP** (2-3 questions)
        4.  **Computer Vision** (2-3 questions)
    - You MUST ask 2-3 questions for a topic before moving to the next.
    - Announce topic transitions (e.g., "Great, let's move on to Deep Learning.").
4.  **Conclusion:** After all topics are covered, end the interview politely.

### BEHAVIOR & INTERACTION GUIDE
-   **Question Source:** ONLY ask questions found in the provided document context. Do paraphrase questions.
-   **Pacing:** Ask ONE question per utterance.
-   **Conversational Tone:** Keep the interaction natural and conversational. Ask follow-up questions if it feels natural, but stay on topic.
-   **Candidate Answers:**
    -   Do NOT correct the candidate's answers.
    -   If the candidate says they don't know, ask a different but related question from the *same topic*.
-   **Internal Thoughts:** Do not show your thinking process. Your output should only be the JSON object.
-   **Brevity:** Keep your questions brief (2-3 sentences max).

### ANSWER VALIDATION & STATUS RULES
Your primary task is to validate the candidate's answer based on the following rules and assign a `status`.

1.  **`valid` Status:**
    -   The answer directly addresses the **current** question.
    -   The answer is NOT a repetition of a previous answer in this session.
    -   *Background and goodbye questions are always `valid` but do not count as technical questions.*

2.  **`discarded` Status:**
    -   The answer is a repetition or highly similar to a previous answer in this interview.
    -   If you mark an answer as `discarded` for being repetitive, use this specific response text: "It seems your answer is similar to what you said before. Can you answer the current question specifically?". Do not generate a new question.
    -   The answer does not address the current question or is completely unrelated.
    -   [IMPORTANT] If you mark an answer as `discarded` for being unrelated, use this specific response text: "Your answer does not seem to be related to the question. Please answer the question I just asked.". Do not generate a new question.

### STRICT JSON OUTPUT FORMAT
-   You MUST respond with ONLY a single, valid JSON object for each turn.
-   Do NOT wrap your response in markdown code blocks or any other formatting.
-   Do NOT use ```json or ``` markers. Return ONLY the raw JSON object.
-   Do not include any commentary, explanations, or text outside of the JSON structure.
-   The `status` field must be either `"valid"` or `"discarded"`. Never use any other value.

**Required JSON Structure (return this exact format without any markdown wrappers):**

{
    "ai_question": "Your NEW question for the candidate to answer next.",
    "user_answer": "The candidate's transcribed answer to the PREVIOUS question.",
    "status": "valid"
}

**Example valid response:**
{"ai_question": "Could you tell me about your experience with Python?", "user_answer": "I have 3 years of experience with Python.", "status": "valid"}
"""


os.makedirs("conversation_logs", exist_ok=True)

def format_interview_flow(interview_flow):
    lines = []
    for stage in ["core", "applied", "behavioral", "background"]:
        if interview_flow.get(stage):
            lines.append(f"{stage.upper()}:")
            for skill in interview_flow[stage]:
                lines.append(f"  - {skill['skill']} (score: {skill['score']})")
    return "\n".join(lines)

def build_system_prompt(job_id):
    if not job_id:
        return None
    job = fetch_job_details(job_id)
    if not job:
        return None
    skill_map = build_skill_map(job_id)
    if skill_map is None:
        return None
    interview_flow = build_interview_flow(skill_map)
    skill_graph_str = format_interview_flow(interview_flow)
    return INTERVIEW_SYSTEM_PROMPT.format(
        job_title=job.get("job_title", "N/A"),
        seniority=job.get("seniority", "N/A"),
        skill_graph=skill_graph_str,
    )

# ======================== QUESTION COUNTER SYSTEM ========================
valid_question_count = 0
MAX_QUESTIONS = 10

def parse_llm_response_status(ai_response):
    """
    Parse LLM response to extract JSON status if present.
    Expected format: {"ai_question": "...", "user_answer": "...", "status": "valid/discarded"}
    Returns: status string or None if not found
    """
    try:
        # Try to find JSON in the response
        import re
        json_match = re.search(r'\{[^}]*"status"\s*:\s*"([^"]+)"[^}]*\}', ai_response)
        if json_match:
            status = json_match.group(1).lower()
            return status if status in ['valid', 'discarded'] else None
        return None
    except Exception as e:
        print(f"Error parsing LLM status: {e}")
        return None

def increment_counter_if_valid(ai_response):
    """
    Check if LLM response indicates a valid answer and increment counter.
    Returns: (incremented: bool, current_count: int, status: str)
    """
    global valid_question_count
    
    status = parse_llm_response_status(ai_response)
    
    if status == 'valid':
        valid_question_count += 1
        print(f"✅ Valid answer #{valid_question_count}/{MAX_QUESTIONS}")
        return True, valid_question_count, status
    elif status:
        print(f"⚠️ Answer marked as '{status}' - counter not incremented ({valid_question_count}/{MAX_QUESTIONS})")
        return False, valid_question_count, status
    else:
        # If no status found in response, assume it's conversational (not a Q&A yet)
        return False, valid_question_count, None

def get_question_count():
    """Get current valid question count"""
    return valid_question_count

def reset_question_count():
    """Reset counter (useful for new interviews)"""
    global valid_question_count
    valid_question_count = 0

def should_end_interview():
    """Check if interview should end based on question count"""
    return valid_question_count >= MAX_QUESTIONS

def generate_interview_end_message(language_choice):
    """Generate polite interview ending message based on language"""
    if language_choice == "2":  # Urdu
        return "شکریہ! آپ نے interview مکمل کر لیا ہے۔ آپ نے 10 سوالات کے جوابات دیے ہیں۔ براہ کرم اپنا جواب submit کریں۔ خدا حافظ!"
    else:  # English
        return "Thank you for completing the interview! You have successfully answered all 10 questions. Please submit your responses now. Goodbye and good luck!"

def save_status_to_json(question, answer, status, filename):
    """
    Save conversation with status tracking
    status: 'valid', 'unanswered', 'repeated', 'misaligned', or None
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"conversations": [], "valid_question_count": 0}
        
        data["conversations"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ai_question": question,
            "user_answer": answer,
            "status": status if status else "unknown",
            "valid_count_at_time": valid_question_count
        })
        
        # Update valid question count in file
        data["valid_question_count"] = valid_question_count
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error saving conversation with status: {e}")

# ======================== END COUNTER SYSTEM ========================

def start_new_interview(language):
    interview_ID = str(uuid.uuid4())
    filename = f"conversation_logs/conversation_{interview_ID}.json"
    data = {
        "interview_id": interview_ID,
        "language": language,
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "conversations": []
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

def save_conversation_to_json(question, answer, status, filename):
    """Save AI question and user answer to JSON file"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"conversations": []}
        
        data["conversations"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ai_question": question,
            "user_answer": answer,
            "status" : status if status else "None",
        })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error saving conversation: {e}")
        

def play_greeting(greeting_file):
    sound = AudioSegment.from_mp3(greeting_file)
    play(sound)

# ✅ Update transcribe_greeting function
def transcribe_greeting():
    greeting_audio = AudioSegment.from_mp3(greeting_file)
    greeting_audio = greeting_audio.set_frame_rate(SAMPLE_RATE).set_channels(1)
    greeting_array = np.array(greeting_audio.get_array_of_samples(), dtype=np.float32) / 32768.0
    
    # Detect language based on greeting file
    lang = "en" if "english" in greeting_file.lower() else "ur"
    return transcribe(greeting_array, language=lang)


# processor = WhisperProcessor.from_pretrained("openai/whisper-small",device="cpu")
# whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

vad_model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True,
    source='github',
    force_reload=False
)

(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

SAMPLE_RATE = 16000
FRAME_DURATION = 0.032                  # 32 ms frames = 512 samples for VAD
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION)

# 🎯 Headphone-friendly sensitivity
RMS_THRESHOLD = 0.4 # Very low → detects even a whisper
VAD_THRESHOLD = 0.9                  # Very low VAD → catches short bursts

SILENCE_DURATION = 1.5                   # Slightly shorter wait before AI responds
INTERRUPTION_THRESHOLD = 0.2             # Lower → faster interruption trigger
MIN_SPEECH_DURATION = 0.3                # Short → quick interrupt allowed

CONVERSATION_TIMEOUT = 30.0              # No change

# 🎯 AI playback leakage rejection
AI_RMS_THRESHOLD = 0.0005                 # From playback analysis (unchanged base)
RMS_SAFETY_MARGIN = 0.01       # Safety buffer to avoid false AI detection



def compute_rms(chunk):
    return np.sqrt(np.mean(chunk ** 2))


def detect_speech_in_frame(frame):
    """Enhanced speech detection using both RMS and VAD - frame-based"""
    rms = compute_rms(frame)
    
    # Ensure frame is exactly 512 samples for VAD
    if len(frame) != 512:
        # Pad or trim to exactly 512 samples
        if len(frame) < 512:
            frame = np.pad(frame, (0, 512 - len(frame)), 'constant')
        else:
            frame = frame[:512]
    
    try:
        vad_prob = vad_model(torch.tensor(frame).unsqueeze(0),
         sr=SAMPLE_RATE).item()
        return rms > RMS_THRESHOLD or vad_prob > VAD_THRESHOLD
    except Exception as e:
        # Fallback to RMS only if VAD fails
        print(f"VAD error: {e}, using RMS only")
        return rms > RMS_THRESHOLD

def detect_speech_with_ai_rejection(frame, ai_speaking=False, ai_threshold=None):
    """
    Speech detection tuned for headphone use + AI playback leakage rejection.
    - Highly sensitive when AI is silent.
    - Rejects AI playback leakage using RMS threshold from actual AI audio.
    """
    # ✅ Headphone-friendly sensitivity
    dynamic_rms_threshold = 0.001      # Very sensitive for quiet speech
    dynamic_vad_threshold = 0.0003     # Very sensitive VAD

    rms = compute_rms(frame)
    #print(f"[AI Rejection] Frame RMS: {rms:.6f}") 

    # Pad/trim to exactly 512 samples for VAD
    vad_frame = frame.copy()
    if len(vad_frame) != 512:
        if len(vad_frame) < 512:
            vad_frame = np.pad(vad_frame, (0, 512 - len(vad_frame)), 'constant')
        else:
            vad_frame = vad_frame[:512]

    try:
        vad_prob = vad_model(torch.tensor(vad_frame).unsqueeze(0), sr=SAMPLE_RATE).item()
    except Exception as e:
        print(f"VAD error: {e}, using RMS only")
        vad_prob = 0.0

    # ✅ If AI is speaking, reject anything that matches AI playback loudness
    if ai_speaking and ai_threshold is not None:
        if rms <= ai_threshold*0.5:
            # Too similar/quiet compared to AI playback — ignore
            return False

    # ✅ Sensitive detection: OR logic between RMS and VAD
    rms_detection = rms > dynamic_rms_threshold
    vad_detection = vad_prob > dynamic_vad_threshold

    return rms_detection or vad_detection

    
    
def continuous_speech_listener(pre_buffered_audio=None):
    """
    Frame-based speech listener that processes audio in 512-sample frames.
    If pre_buffered_audio is provided, it is prepended to the recorded audio.
    Returns: (audio_data, interrupted_flag)
    """
    audio_buffer = []
    silence_frames = 0
    speech_detected = False
    speech_start_time = None
    last_speech_time = None

    # If pre-buffered audio exists, convert to frames and add to buffer
    if pre_buffered_audio is not None and len(pre_buffered_audio) > 0:
        print("🔄 Converting buffered audio to frames...")
        # Convert buffered audio to frames
        for i in range(0, len(pre_buffered_audio), FRAME_SIZE):
            frame = pre_buffered_audio[i:i+FRAME_SIZE]
            if len(frame) == FRAME_SIZE:  # Only add complete frames
                audio_buffer.append(frame)
        speech_detected = len(audio_buffer) > 0
        speech_start_time = time.time()
        last_speech_time = speech_start_time

    # Create microphone input stream with correct frame size
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32',
        blocksize=FRAME_SIZE  # 512 samples
    )

    max_silence_frames = int(SILENCE_DURATION / FRAME_DURATION)  # ~62 frames
    min_speech_frames = int(MIN_SPEECH_DURATION / FRAME_DURATION)  # ~31 frames
    speech_frame_count = len(audio_buffer)

    try:
        with stream:
            while True:
                # ✅ Read exactly one frame (512 samples)
                frame, _ = stream.read(FRAME_SIZE)
                frame = frame.flatten()
                frame_rms = compute_rms(frame)
                #print(f"[Listener] Frame RMS: {frame_rms:.6f}")
                has_speech = detect_speech_in_frame(frame)
                current_time = time.time()

                if has_speech:
                    if not speech_detected:
                        speech_detected = True
                        speech_start_time = current_time
                        print("🎤 Speech started")
                    
                    audio_buffer.append(frame)
                    speech_frame_count += 1
                    silence_frames = 0
                    last_speech_time = current_time
                    
                else:
                    if speech_detected:
                        audio_buffer.append(frame)
                        silence_frames += 1
                        
                        # ✅ Check if silence duration exceeded (frame-based)
                        if silence_frames >= max_silence_frames:
                            if speech_frame_count >= min_speech_frames:
                                total_duration = len(np.concatenate(audio_buffer)) / SAMPLE_RATE
                                print(f"✅ Recording complete: {total_duration:.1f}s ({speech_frame_count} speech frames)")
                                break
                            else:
                                # Reset recording if speech was too short
                                print(f"❌ Speech too short ({speech_frame_count} frames), resetting...")
                                if pre_buffered_audio is not None:
                                    # Keep original buffered audio
                                    audio_buffer = []
                                    for i in range(0, len(pre_buffered_audio), FRAME_SIZE):
                                        frame = pre_buffered_audio[i:i+FRAME_SIZE]
                                        if len(frame) == FRAME_SIZE:
                                            audio_buffer.append(frame)
                                    speech_frame_count = len(audio_buffer)
                                else:
                                    audio_buffer = []
                                    speech_frame_count = 0
                                silence_frames = 0
                                speech_detected = len(audio_buffer) > 0

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return None, True

    if audio_buffer and speech_detected:
        full_audio = np.concatenate(audio_buffer)
        return full_audio, False
    else:
        print("No valid speech detected.")
        return None, False

def calculate_ai_playback_threshold(audio_file, multiplier=1.2, silence_rms_cutoff=0.001):
    """
    Calculate RMS threshold for AI playback rejection:
    - Ignores silent parts of AI playback.
    - Uses only loud segments to set an accurate cutoff.
    - Adds a small multiplier for safety.
    """
    try:
        audio = AudioSegment.from_file(audio_file)
        raw_audio = audio.raw_data
        sample_rate = audio.frame_rate
        channels = audio.channels

        # Convert to float32 [-1.0, 1.0]
        audio_np = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
        if channels > 1:
            audio_np = audio_np.reshape(-1, channels).mean(axis=1)  # Mono mixdown

        # Compute RMS in short frames
        frame_size = int(sample_rate * 0.032)  # 32 ms frames
        frame_rms_values = []
        for i in range(0, len(audio_np), frame_size):
            frame = audio_np[i:i + frame_size]
            if len(frame) < frame_size:
                continue
            rms = np.sqrt(np.mean(frame ** 2))
            if rms > silence_rms_cutoff:  # Ignore near-silent frames
                frame_rms_values.append(rms)

        if not frame_rms_values:
            print("⚠️ No loud frames found in AI playback.")
            return None

        # Use median loudness to avoid spikes
        median_rms = float(np.median(frame_rms_values))
        playback_threshold = median_rms * multiplier

        print(f"🎚️ AI Playback median RMS: {median_rms:.6f} → Detection Threshold: {playback_threshold:.6f}")
        return playback_threshold

    except Exception as e:
        print(f"Error calculating playback threshold: {e}")
        return None


# ✅ Update the transcribe function
def transcribe(audio_array, language="en"):
    """
    Transcribe audio using faster-whisper.
    audio_array: numpy array of float32 audio samples
    language: "en" for English, "ur" for Urdu
    """
    try:
        # faster-whisper expects audio as numpy array
        segments, info = whisper_model.transcribe(
            audio_array,
            language=language,
            beam_size=5,
            vad_filter=True,  # ✅ Built-in VAD filtering
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Combine all segments into one transcription
        transcription = " ".join([segment.text for segment in segments])
        return transcription.strip()
        
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""

#transcribed text is sent to ollama/gemma for response


# GROQ_API_KEY = "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"  # 
# GROQ_MODEL = "llama-3.3-70b-versatile"  

# def query_groq(user_input, context="", max_tokens=300, temperature=0.1, conversation_history=None):
#     try:
#         url = "https://api.groq.com/openai/v1/chat/completions"

#         if isinstance(user_input, list):
#             user_input = " ".join(user_input)   # or pick the last element: user_input[-1]
#         elif not isinstance(user_input, str):
#             user_input = str(user_input)

#         goodbye_words = ["khuda hafiz", "bye", "goodbye", "khudahafiz", "alvida"]
#         user_said_goodbye = any(phrase in user_input.lower() for phrase in goodbye_words)

#         tools = [
#             {
#                 "type": "function",
#                 "function": {
#                     "name": "end_conversation",
#                     "description": (
#                         "ONLY call this function if the user's message contains EXACTLY these goodbye words: "
#                         "'khuda hafiz', 'bye', 'goodbye', or 'alvida'. Do NOT call this for greetings or conversation."
#                     ),
#                     "parameters": {
#                         "type": "object",
#                         "properties": {},
#                         "required": []
#                     }
#                 }
#             }
#         ]

#         if conversation_history is None:
#             conversation_history = [{"role": "system", "content": interview_prompt}]

#         conversation_history.append({
#             "role": "user",
#             "content": f"""
# Candidate answer: "{user_input}"

# Relevant interview questions from knowledge base:
# {context}

# Keep it conversational. It should look like a natural conversation, not a scripted interview. Follow the instruction and flow.
# """
#         })

#         payload = {
#             "model": GROQ_MODEL,
#             "messages": conversation_history,
#             "max_tokens": max_tokens,
#             "temperature": temperature,
#             "stream": False,
#         }

#         headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
#         response = requests.post(url, headers=headers, json=payload)

#         if response.status_code == 200:
#             result = response.json()
#             choice = result["choices"][0]["message"]["content"]
#             conversation_history.append({"role": "assistant", "content": choice})
#             return choice.strip(), conversation_history
#         else:
#             print(f"Error calling Groq API: {response.status_code}")
#             print(response.text)
#             return "Sorry, I'm having trouble processing your answer right now.", conversation_history

#     except Exception as e:
#         print(f"Exception in query_groq: {str(e)}")
#         return "Sorry, there was an error processing your answer.", conversation_history

# async def text_to_speech(response_text: str) -> str:
#     """
#     Generate TTS audio using edge-tts and return the MP3 filepath.
#     Async-safe: must be awaited from async code.
#     """
#     output_path = f"ai_response_{uuid.uuid4().hex}.mp3"
#     selected_voice = voice if 'voice' in globals() else "ur-PK-UzmaNeural"
#     communicate = edge_tts.Communicate(text=response_text, voice=selected_voice)
#     await communicate.save(output_path)
#     return output_path
# from google import genai
# GEMINI_API_KEY = "AIzaSyBU58d8p9X5WxUoWFf-j0o4Uq_vDtDPjXc"
# GEMINI_MODEL = "gemini-2.0-flash"  # 1500 req/day free tier (vs 20 for 2.5-flash)

# client = genai.Client(api_key=GEMINI_API_KEY)

GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.3-70b-versatile"

def query_groq(user_input, context="", conversation_history=None, max_tokens=800, temperature=0.1, interview_prompt=interview_prompt_en):
    """
    Query Groq API with conversation history and interview prompt.
    Returns: (response_text, updated_conversation_history)
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        print(f"🔵 Calling Groq API with model: {GROQ_MODEL}")
        print(f"🔵 Using interview prompt: {interview_prompt[:50]}...")

        if isinstance(user_input, list):
            user_input = " ".join(user_input)
        elif not isinstance(user_input, str):
            user_input = str(user_input)

        # Initialize conversation history with system prompt if empty
        if conversation_history is None or len(conversation_history) == 0:
            conversation_history = [{"role": "system", "content": interview_prompt}]
        
        # Check if system prompt exists, if not add it
        if not any(msg.get("role") == "system" for msg in conversation_history):
            conversation_history.insert(0, {"role": "system", "content": interview_prompt})

        # Build user message without RAG context (skill-graph prompt drives questions)
        user_message = f"""Candidate answer: "{user_input}"

    Keep it conversational and follow the system prompt and skill graph."""

        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        payload = {
            "model": GROQ_MODEL,
            "messages": conversation_history,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            choice = result["choices"][0]["message"]["content"]
            conversation_history.append({"role": "assistant", "content": choice})
            return choice.strip(), conversation_history
        else:
            print(f"❌ Error calling Groq API: {response.status_code}")
            print(response.text)
            return "Sorry, I'm having trouble processing your answer right now.", conversation_history

    except Exception as e:
        print(f"❌ Exception in query_groq: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Sorry, there was an error processing your answer.", conversation_history
    
# def text_to_speech(response_text):
#     try:
#         #print(f"Generating speech for: {response_text}")
#         output_path = "ai_response.mp3"

#         selected_voice = voice if 'voice' in globals() else "ur-PK-UzmaNeural"

#         async def run():
#             communicate = edge_tts.Communicate(text=response_text, voice=selected_voice)
#             await communicate.save(output_path)
#             #print(f"Audio saved to: {output_path}")

#         asyncio.run(run())

#         return output_path

#     except Exception as e:
#         print(f"Error in TTS: {e}")
#         return None

def end_conversation():
    print("Khuda Hafiz! Aap se baat karke acha laga.")
    sys.exit(0)

class NaturalConversationManager:
    def __init__(self):
        self.is_speaking = False
        self.stop_speaking = Event()
        self.user_interrupted = False
        self.interruption_audio = None
        self.realtime_audio_buffer = []  

    def store_interruption_audio(self, audio_chunk):
        """Store interrupted user speech detected during playback"""
        if self.interruption_audio is None:
            self.interruption_audio = audio_chunk
        else:
            self.interruption_audio = np.concatenate([self.interruption_audio, audio_chunk])

    def get_interruption_audio(self):
        if self.interruption_audio is not None and len(self.interruption_audio) > 0:
            return self.interruption_audio
        return None

    def clear_interruption_buffer(self):
        self.interruption_audio = None

    def play_response_with_interruption(self, audio_file):
        """Play AI speech while monitoring for user interruption with echo rejection"""
        self.current_ai_rms_threshold = calculate_ai_playback_threshold(audio_file, multiplier=1.5)

        self.is_speaking = True
        self.stop_speaking.clear()
        self.user_interrupted = False
        self.realtime_audio_buffer = []
        self.playback_start_time = time.time()  # Track when playback started

        playback_thread = Thread(target=self._play_audio_chunks, args=(audio_file,))
        monitor_thread = Thread(target=self._monitor_interruption)

        print("Starting AI response with echo rejection...")
        playback_thread.start()
        monitor_thread.start()

        playback_thread.join()
        self.is_speaking = False
        monitor_thread.join(timeout=1.0)

        return self.user_interrupted

    def _play_audio_chunks(self, audio_file):
        """Plays AI speech in chunks while allowing interruption"""
        try:
            audio = AudioSegment.from_file(audio_file)
            raw_audio = audio.raw_data
            sample_rate = audio.frame_rate
            channels = audio.channels

            audio_np = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
            audio_np = audio_np.reshape(-1, channels if channels == 2 else 1)

            print("AI speaking...")
            chunk_size = int(sample_rate * 0.1)

            stream = sd.OutputStream(samplerate=sample_rate, channels=channels, dtype=np.float32,
                                     blocksize=chunk_size * 2, latency='high')
            stream.start()

            playback_interrupted = False

            for i in range(0, len(audio_np), chunk_size):
                if self.stop_speaking.is_set():
                    playback_interrupted = True
                    break

                chunk = audio_np[i:i + chunk_size]
                if len(chunk) < chunk_size:
                    chunk = np.vstack([chunk, np.zeros((chunk_size - len(chunk), channels), dtype=np.float32)])

                stream.write(chunk)
                time.sleep(0.005)

            stream.stop()
            stream.close()

            if not playback_interrupted:
                print("AI finished speaking completely")
                self.user_interrupted = False  

        except Exception as e:
            print(f"Error playing audio: {e}")

        finally:
            if not self.user_interrupted:  # ✅ Only clear when no interruption
                self.stop_speaking.clear()

    def _monitor_interruption(self):
        """Detect user speech during AI playback using frame-based processing with echo rejection"""
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', blocksize=FRAME_SIZE)
        consecutive_speech_frames = 0
        required_speech_frames = 2  # ✅ Reduced from 5 to 2 for faster detection
        max_buffer_frames = int(5.0 / FRAME_DURATION)  # 5 seconds of frames
        
        # ✅ Reduced stabilization delay
        stabilization_delay = 0.2  # 200ms delay (reduced from 500ms)

        try:
            with stream:
                while self.is_speaking and not self.stop_speaking.is_set():
                    frame, _ = stream.read(FRAME_SIZE)
                    frame = frame.flatten()
                    
                    if hasattr(self, 'playback_start_time') and time.time() - self.playback_start_time < stabilization_delay:
                        continue

                    # ✅ Store frames in buffer (limit to 5 seconds)
                    self.realtime_audio_buffer.append(frame)
                    if len(self.realtime_audio_buffer) > max_buffer_frames:
                        self.realtime_audio_buffer = self.realtime_audio_buffer[-max_buffer_frames:]

                    # ✅ Use basic speech detection first for debugging
                    frame_rms = compute_rms(frame)
                    #print(f"[Monitor] Frame RMS: {frame_rms:.6f}")
                    basic_speech = frame_rms > RMS_THRESHOLD
                    
                    # ✅ Use enhanced speech detection with AI rejection
                    has_speech = detect_speech_with_ai_rejection(
                        frame, 
                        ai_speaking=True, 
                        ai_threshold=self.current_ai_rms_threshold
                    )
                    
                    # ✅ Debug output
                    if  has_speech:
                        print(f"🎙️ Audio detected - RMS: {frame_rms:.4f}, Basic: {basic_speech}, Enhanced: {has_speech}")

                    if has_speech:
                        consecutive_speech_frames += 1
                        print(f"🔊 Potential user speech: {consecutive_speech_frames}/{required_speech_frames}")
                        
                        if consecutive_speech_frames >= required_speech_frames:
                            # ✅ Simplified verification - just check if speech is strong enough
                            ai_threshold = getattr(self, 'current_ai_rms_threshold', None)
                            
                            # ✅ More lenient threshold check
                            # if not ai_threshold or frame_rms > ai_threshold * 1.1:  # Only 1.1x stronger needed
                            #     print("✅ User speech detected → marking interruption")
                            #     # ✅ Store all buffered frames as interruption audio
                            #     self.interruption_audio = np.concatenate(self.realtime_audio_buffer)
                            #     self.user_interrupted = True
                            #     self.stop_speaking.set()
                            #     break
                            # else:
                            #     print(f"❌ Speech too weak (RMS: {frame_rms:.4f} vs AI: {ai_threshold:.4f})")
                            #     consecutive_speech_frames = max(0, consecutive_speech_frames - 1)  # Reduce counter slightly
                            if not ai_threshold or frame_rms > ai_threshold * 0.5:  # 50% of AI loudness
                                print("✅ User speech detected → marking interruption")
                                self.interruption_audio = np.concatenate(self.realtime_audio_buffer)
                                self.user_interrupted = True
                                self.stop_speaking.set()
                                break
                            else:
                                print(f"❌ Speech too weak (RMS: {frame_rms:.4f} vs AI: {ai_threshold:.4f})")
                                consecutive_speech_frames = max(0, consecutive_speech_frames - 1)
                    else:
                        consecutive_speech_frames = 0
                        
        except Exception as e:
            print(f"Monitoring error: {e}")
    
    




# if __name__ == "__main__":

#     print("\nPress Ctrl+C to exit\n")
    
#     # Language selection
#     print("Enter the language of the interview (Press 1 for English, 2 for Urdu):")
#     language_choice = input().strip()
#     if language_choice == "1":
#         interview_prompt = interview_prompt_en
#         voice = "en-US-SteffanNeural"
#         greeting_file = "greeting_english.mp3" 
#          # English voice
#     elif language_choice == "2":
#         interview_prompt = interview_prompt_ur
#         voice = "ur-PK-UzmaNeural"     # Urdu voice
#         greeting_file = "greetings.mp3"
#     else:
#         print("Invalid choice. Defaulting to English.")
#         interview_prompt = interview_prompt_en
#         greeting_file = "greeting_english.mp3"
#         voice = "en-US-SteffanNeural"

#         # --- Initialize PDF/FAISS once at startup ---
#     topics_dict = parse_pdf(pdf_path)
#     index, embedding_model, metadata = build_faiss_index_with_metadata(topics_dict)
#     save_index_and_metadata(index, metadata, index_path, json_path)

#    #last_answer = "Let's start the interview."
#     conversation_filename = start_new_interview(language_choice)
#     conversation_manager = NaturalConversationManager()
#     previous_ai_question = None  # Track the previous AI question
#     conversation_context = []  # Store last 2 question-answer pairs

#     # Initial greeting
#     print("AI: Starting conversation...")
    
#     # Store initial greeting (transcribe the greeting file)
#     try:
#         play_thread = Thread(target=play_greeting, args=(greeting_file,))
#         play_thread.start()
#         greeting_text = transcribe_greeting()
#         play_thread.join()
#         last_answer = greeting_text  # Use the transcribed greeting as the initial FAISS query
#         #print(f"Greeting transcribed: {greeting_text}")
#         conversation_history = [{"role": "system", "content": interview_prompt},
#                                 {"role": "assistant", "content": greeting_text}
#                                 ]

#         previous_ai_question = greeting_text  # Set the greeting as the first question
#     except Exception as e:
#         greeting_text = "Assalam alaikum! Main aap ka interviewer hun. Kya aap tayar hain?"
#         print(f"Using default greeting text due to error: {e}")
#         previous_ai_question = greeting_text
    
#   # Ensure audio is processed
#     while True:
#         try:
#             buffered_audio = conversation_manager.get_interruption_audio()
#             if buffered_audio is not None and len(buffered_audio) > 0:
#                 print("Continuing from previous interruption with buffered audio...")
#                 user_audio, _ = continuous_speech_listener(buffered_audio)
#                 conversation_manager.clear_interruption_buffer()
#             else:
#                 user_audio, interrupted = continuous_speech_listener()

#             if user_audio is not None and len(user_audio) > 0:
#                 print("Processing speech...")
#                 user_text = transcribe(user_audio)
#                 print(f"You: {user_text}")

#                 if not user_text.strip() or len(user_text.strip()) < 3:
#                     print("Didn't catch that. Please speak again.")
#                     continue

#                 # Save the previous AI question with current user answer
#                 if previous_ai_question:
#                     save_conversation_to_json(previous_ai_question, user_text, conversation_filename)

#                     # Add to context (keep only last 2 QA pairs)
#                     conversation_context.append((previous_ai_question, user_text))
#                     if len(conversation_context) > 2:
#                         conversation_context = conversation_context[-2:]  # Keep only last 2

#                 # Pass context to AI
#                 #ai_response = query_groq(user_text, conversation_context)
#                 similar_qs = query_faiss(user_text, embedding_model, index, metadata, top_n=5)
#                 #print(f"FAISS suggestions: {similar_qs}")
#                 context = "\n".join([f"- {q[0]}" for q in similar_qs])
#                 ai_response, conversation_history = query_groq(
#                 user_text,
#                 context,
#                 conversation_history=conversation_history
#             )

#                 print(f"AI: {ai_response}")
                
#                 # Update the previous AI question for next iteration
#                 previous_ai_question = ai_response

#                 if ai_response:
#                     print("Generating speech...")
#                     audio_file = text_to_speech(ai_response)

#                     if audio_file:
#                         was_interrupted = conversation_manager.play_response_with_interruption(audio_file)

#                         if was_interrupted:
#                             #print("\nUser interrupted. Processing captured speech...")
#                             buffered_audio = conversation_manager.interruption_audio

#                             if buffered_audio is not None and buffered_audio.size > 0:
#                                 continuation_audio, _ = continuous_speech_listener(buffered_audio)

#                                 if continuation_audio is not None and len(continuation_audio) > 0:
#                                     interrupted_text = transcribe(continuation_audio)
#                                     print(f"User: {interrupted_text}")

#                                     if interrupted_text.strip():
#                                         # Save the interrupted response with the previous AI question
#                                         if previous_ai_question:
#                                             save_conversation_to_json(previous_ai_question, interrupted_text, conversation_filename)

#                                             # Add to context (keep only last 2 QA pairs)
#                                             conversation_context.append((previous_ai_question, interrupted_text))
#                                             if len(conversation_context) > 2:
#                                                 conversation_context = conversation_context[-2:]
                                        
#                                         # Pass context to AI
#                                         similar_qs = query_faiss(interrupted_text, embedding_model, index, metadata, top_n=5)
#                                         print(f"FAISS suggestions: {similar_qs}")
#                                         context = "\n".join([f"- {q[0]}" for q in similar_qs])

#                                         # Pass context to AI
#                                         new_ai_response, conversation_history = query_groq(
#                                             interrupted_text,
#                                             context,
#                                             conversation_history=conversation_history
#                                         )
#                                         print(f"AI: {new_ai_response}")
                                        
#                                         # Update previous AI question
#                                         previous_ai_question = new_ai_response

#                                         if new_ai_response:
#                                             new_audio = text_to_speech(new_ai_response)
#                                             if new_audio:
#                                                 conversation_manager.play_response_with_interruption(new_audio)

#                             conversation_manager.clear_interruption_buffer()
#                             continue
#                     else:
#                         print("Failed to generate speech.")
#                 else:
#                     print("No AI response generated.")

#             elif interrupted:
#                 print("Conversation ended by user.")
#                 break
#             else:
#                 print("No speech detected, continuing to listen...")

#         except KeyboardInterrupt:
#             print("\nConversation ended. Goodbye!")
#             break
#         except Exception as e:
#             print(f"Error: {e}")
#             print("Continuing conversation...")
#             time.sleep(1)