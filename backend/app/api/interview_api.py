# app.py
import os
import sys

# Fix Windows console encoding (cp1252 can't handle emojis)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import time
import asyncio
import base64
import uuid
import re
from typing import Dict, Any, Optional, List, Tuple
from app.services.ai_interview import *
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
#from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import numpy as np
import soundfile as sf
import torch
from faster_whisper import WhisperModel
import edge_tts
import requests
import tempfile
from app.database.db_connection import supabase
from app.services.interview_link import verify_interview_token
from app.services.evaluating_interview import evaluate_and_save_interview
import traceback
from fastapi import APIRouter

# ----------------- Config -----------------
GROQ_API_KEY = "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"  # keep env in prod
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SAMPLE_RATE = 16000  # you confirmed 16kHz


def verify_token(authorization: str) -> Dict[str, Any]:
    token = (authorization or "").replace("Bearer", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing token", headers={"WWW-Authenticate": "Bearer"})

    try:
        user_response = supabase.auth.get_user(token)
        user = getattr(user_response, "user", None)
        if user:
            user_id = getattr(user, "id", None)
            email = getattr(user, "email", None)
            return {
                "candidate_id": str(user_id) if user_id else "",
                "email": email or "unknown",
                "auth_type": "supabase",
            }
    except Exception:
        pass

    payload = verify_interview_token(token)
    if payload.get("purpose") != "ai_interview":
        raise HTTPException(status_code=401, detail="Invalid interview token purpose")

    return {
        "candidate_id": str(payload.get("applicant_id") or ""),
        "email": payload.get("email") or "unknown",
        "auth_type": "interview_link",
        "job_id": payload.get("job_id"),
        "name": payload.get("name"),
    }


class StopInterviewBody(BaseModel):
    session_id: str | None = None
    job_id: str | None = None  # optional; falls back to token's job_id

# ======================== QUESTION COUNTER SYSTEM ========================
MAX_QUESTIONS = 10

def parse_llm_response_for_status_and_question(ai_response):
    """
    Parse LLM response to extract:
    1. The clean AI question (from the ai_question field)
    2. The status (valid/discarded)
    
    Expected format from LLM:
    {
        "ai_question": "The question you asked",
        "user_answer": "The candidate's answer",
        "status": "valid/discarded"
    }
    
    Returns: (clean_question, status)
    """
    try:
        # Strip markdown code blocks if present
        cleaned_response = ai_response.strip()
        if cleaned_response.startswith('```'):
            # Remove opening ```json or ```
            lines = cleaned_response.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            # Remove closing ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned_response = '\n'.join(lines).strip()
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_response, re.DOTALL)
        
        status = None
        ai_question = None
        
        if json_match:
            # Extract the full JSON object
            try:
                json_str = json_match.group(0)
                json_obj = json.loads(json_str)
                status = json_obj.get('status', '').lower()
                if status not in ['valid', 'discarded']:
                    status = None
                # ✅ Extract the ai_question field from JSON
                ai_question = json_obj.get('ai_question', '')
            except Exception as e:
                print(f"⚠️ JSON parse error: {e}")
                pass
        
        # Return the ai_question from JSON, or fallback to original response
        clean_question = ai_question if ai_question else ai_response
        
        return clean_question, status
        
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return ai_response, None

def increment_counter_if_valid(session_counter, status):
    """
    Increment counter if status is valid.
    Returns: (incremented: bool, current_count: int)
    """
    if status == 'valid':
        session_counter['count'] += 1
        print(f"✅ Valid answer #{session_counter['count']}/{MAX_QUESTIONS}")
        return True, session_counter['count']
    elif status == 'discarded':
        print(f"⚠️ Answer marked as 'discarded' - counter not incremented ({session_counter['count']}/{MAX_QUESTIONS})")
        return False, session_counter['count']
    else:
        # No status found - likely conversational (greeting, etc.)
        return False, session_counter['count']

def should_end_interview(session_counter):
    """Check if interview should end based on question count"""
    return session_counter['count'] >= MAX_QUESTIONS

def generate_interview_end_message(language):
    """Generate polite interview ending message based on language"""
    if language == "ur":  # Urdu
        return "شکریہ! آپ نے interview مکمل کر لیا ہے۔ آپ نے 10 سوالات کے جوابات دیے ہیں۔ براہ کرم اپنا جواب submit کریں۔ خدا حافظ!"
    else:  # English
        return "Thank you for completing the interview! You have successfully answered all 10 questions. Please submit your responses now. Goodbye and good luck!"

def save_conversation_with_status(question, answer, status, filename, valid_count):
    """
    Save conversation with status tracking in the required JSON format.
    Format:
    {
        "ai_question": "The question you asked",
        "user_answer": "The candidate's answer",
        "status": "valid/discarded"
    }
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
            "valid_count_at_time": valid_count
        })
        
        # Update valid question count in file
        data["valid_question_count"] = valid_count
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error saving conversation with status: {e}")

# ======================== END COUNTER SYSTEM ========================

# ----------------- Models -----------------
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

# ----------------- FastAPI Setup -----------------
app1 = FastAPI(title="Interview Agent - WS")

app1.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For testing, then narrow it down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
#app1.mount("/static", StaticFiles(directory="static"), name="static")


@app1.get("/")
def home(request: Request):
    return {"message": "Welcome to the Interview Agent API. Please connect via WebSocket at /ws for the interview process."}


@app1.post("/stop")
async def stop_interview(request: Request, body: StopInterviewBody, background_tasks: BackgroundTasks):
    authorization = request.headers.get("Authorization", "")
    user_info = verify_token(authorization=authorization)

    candidate_id = user_info.get("candidate_id")
    # job_id comes from the interview token (preferred) or the request body
    job_id = user_info.get("job_id") or body.job_id
    session_id = body.session_id

    if session_id and job_id and candidate_id:
        interview_filename = f"interviews/interview_{session_id}.json"
        print(f"📋 Scheduling evaluation: {interview_filename}")
        background_tasks.add_task(
            evaluate_and_save_interview,
            interview_filename,
            str(candidate_id),
            str(job_id),
        )
    else:
        print(f"⚠️ Skipping evaluation — missing info: session_id={session_id}, job_id={job_id}, candidate_id={candidate_id}")

    return {
        "ok": True,
        "message": "Interview stopped. Evaluation is processing in the background.",
        "session_id": session_id,
        "candidate_id": candidate_id,
    }


# ----------------- Audio / AI utils -----------------
def pcm16_bytes_to_float32(arr: bytes) -> np.ndarray:
    # int16 -> float32 [-1, 1]
    a = np.frombuffer(arr, dtype=np.int16).astype(np.float32) / 32768.0
    return a


def transcribe_float(audio_f32: np.ndarray, language="en") -> str:
    """
    Transcribe audio using faster-whisper (array input).
    """
    try:
        segments, info = whisper_model.transcribe(
            audio_f32,
            language=language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        transcription = " ".join([segment.text for segment in segments])
        return transcription.strip()
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return ""


def transcribe_from_wav(path: str, language: str = "en") -> str:
    """
    Transcribe WAV file using faster-whisper.
    """
    try:
        segments, info = whisper_model.transcribe(
            path,
            language=language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        transcription = " ".join([segment.text for segment in segments])
        return transcription.strip()
    except Exception as e:
        print(f"❌ WAV Transcription error: {e}")
        return ""


async def tts_mp3_bytes(text: str, voice: str) -> bytes:
    """Generate TTS audio using edge-tts with gTTS fallback."""
    fn = f"tts_{uuid.uuid4().hex}.mp3"
    try:
        # Try edge-tts first
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(fn)
        with open(fn, "rb") as f:
            return f.read()
    finally:
        try:
            os.remove(fn)
        except:
            pass


# Minimal MP3 header to force client to stop playback (used on interruptions)
SILENT_MP3_BYTES = b'\xff\xf3\x44\xc4\x00\x00\x00\x03\x48\x00\x00\x00\x00\x4c\x41\x4d\x45\x33\x2e\x39\x39\x2e\x35\x00\x00\x00'


# ----------------- Silero Streaming VAD -----------------
class StreamingSileroVAD:
    """
    Streaming VAD wrapper around Silero VAD model :
      - Accepts variable-sized float32 chunks (mono, SAMPLE_RATE)
      - Buffers them into 512-sample frames required by Silero
      - Produces events: "speech_start", "speaking", "turn_complete", None
      - Returns completed utterance as numpy array when turn_complete
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        chunk_ms: int = 30,
        speech_threshold: float = 0.6,
        silence_threshold: float = 0.25,
        min_speech_frames: int = 5,  # Increased from 3 to reduce false positives
        turn_complete_frames: int = 120,  # Increased from 100 (now ~4.8s) to avoid premature cutoff
        abandon_frames: int = 250,  # Increased from 150 (now ~8s)
    ):
        """
        chunk_ms: expected chunk size in ms from frontend (30ms recommended)
        speech_threshold: probability above which a frame counts as speech
        silence_threshold: probability below which a frame counts as silence
        min_speech_frames: consecutive speech frames to declare speech_start
        turn_complete_frames: consecutive silence frames to complete turn (450ms)
        abandon_frames: consecutive silence frames to abandon/discard buffer (4.5s)
        """
        self.sample_rate = sample_rate
        self.chunk_ms = chunk_ms
        self.chunk_samples = int(sample_rate * chunk_ms / 1000)
        self.speech_th = speech_threshold
        self.silence_th = silence_threshold
        self.min_speech_frames = min_speech_frames
        self.turn_complete_frames = turn_complete_frames
        self.abandon_frames = abandon_frames

        self.noise_floor = 0.0
        self.calibration_frames = 0
        self.calibration_limit = 50  # ~1.6 sec
        self.calibration_probs = []  # Store probabilities during calibration
        self.calibrated = False
        # ✅ Silero requires exactly 512 samples at 16kHz (or 256 at 8kHz)
        self.required_chunk_size = 512 if sample_rate == 16000 else 256
        
        # Dynamic thresholds (will be set after calibration)
        self.dynamic_speech_th = speech_threshold
        self.dynamic_silence_th = silence_threshold

        # Load Silero model via torch.hub (CPU)
        try:
            self.model, self.utils = torch.hub.load(
                "snakers4/silero-vad", "silero_vad", force_reload=False, trust_repo=True
            )
            # make model eval and CPU
            self.model.eval()
            for p in self.model.parameters():
                p.requires_grad = False
            print("✅ Silero VAD model loaded successfully")
        except Exception as e:
            print(f"❌ Could not load Silero VAD model: {e}")
            raise

        # State
        self.in_speech = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.buffer_frames: List[np.ndarray] = []  # store float32 chunks
        self.recent_frames: List[np.ndarray] = []  # store recent frames for speech detection
        
        # ✅ Leftover buffer for incomplete chunks
        self.leftover_samples = np.array([], dtype=np.float32)
        
        # 🛡️ Anti-flapping: prevent rapid re-trigger after turn_complete
        self.frames_since_turn_complete = 0
        self.cooldown_frames = 10  # ~320ms cooldown after turn complete

    def reset(self):
        self.in_speech = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.buffer_frames.clear()
        self.recent_frames.clear()
        # ✅ Keep leftover samples even after reset (they're from ongoing stream)
        # self.leftover_samples = np.array([], dtype=np.float32)
        # Reset cooldown counter
        self.frames_since_turn_complete = 0

    def _predict_prob(self, chunk_f32: np.ndarray) -> float:
        """
        Run silero model on exactly 512 samples and return speech probability (0..1).
        """
        try:
            # ✅ Ensure exactly required_chunk_size samples
            if len(chunk_f32) != self.required_chunk_size:
                print(f"⚠️ Chunk size {len(chunk_f32)} != {self.required_chunk_size}, padding/truncating")
                if len(chunk_f32) < self.required_chunk_size:
                    # Pad with zeros
                    chunk_f32 = np.pad(chunk_f32, (0, self.required_chunk_size - len(chunk_f32)))
                else:
                    # Truncate
                    chunk_f32 = chunk_f32[:self.required_chunk_size]
            
            audio_t = torch.from_numpy(chunk_f32).float()
            # model returns a tensor scalar or tensor(1)
            out = self.model(audio_t, self.sample_rate)
            # convert to float f
            if isinstance(out, torch.Tensor):
                prob = float(out.detach().cpu().numpy().item())
            else:
                prob = float(out)
            return prob
        except Exception as e:
            # On model error, be conservative (treat as silence)
            print(f"⚠️ Silero predict error: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

    def process_chunk(self, chunk_f32: np.ndarray) -> List[Tuple[str, Optional[np.ndarray]]]:
        """
        Feed a chunk into VAD. Handles variable chunk sizes by buffering.
        Returns a list of (event, utterance) tuples.
          - event: "speech_start", "speaking", "turn_complete", "silence", "calibrating"
          - utterance: full numpy float32 array when event == "turn_complete"
        """
        # ✅ Combine with leftover samples from previous chunk
        if len(self.leftover_samples) > 0:
            chunk_f32 = np.concatenate([self.leftover_samples, chunk_f32])
        
        # ✅ Process complete 512-sample frames
        num_complete_frames = len(chunk_f32) // self.required_chunk_size
        samples_processed = num_complete_frames * self.required_chunk_size
        
        # ✅ Store leftovers for next chunk
        self.leftover_samples = chunk_f32[samples_processed:]
        
        events = []
        
        # ✅ Process each complete frame
        for i in range(num_complete_frames):
            start_idx = i * self.required_chunk_size
            end_idx = start_idx + self.required_chunk_size
            frame = chunk_f32[start_idx:end_idx]
            
            prob = self._predict_prob(frame)
            
            # 🎯 CALIBRATION PHASE: Measure environment noise for first N frames
            if not self.calibrated:
                self.calibration_probs.append(prob)
                self.calibration_frames += 1
                
                if self.calibration_frames >= self.calibration_limit:
                    # Calculate noise floor from collected probabilities
                    self.noise_floor = np.mean(self.calibration_probs)
                    noise_std = np.std(self.calibration_probs)
                    noise_max = np.max(self.calibration_probs)
                    
                    # ⚠️ VALIDATE CALIBRATION: Reject if speech/loud audio was present
                    if noise_max > 0.7 or self.noise_floor > 0.5:
                        print(f"❌ CALIBRATION FAILED: Speech or loud audio detected!")
                        print(f"   Max probability: {noise_max:.3f} (should be < 0.7)")
                        print(f"   Mean probability: {self.noise_floor:.3f} (should be < 0.5)")
                        print(f"")
                        print(f"⚠️  Please recalibrate in a QUIET environment:")
                        print(f"   1. Stop any music/videos playing")
                        print(f"   2. Don't speak during calibration")
                        print(f"   3. Ensure only ambient room noise is present")
                        print(f"")
                        # Reset calibration
                        self.calibration_frames = 0
                        self.calibration_probs.clear()
                        events.append(("calibration_failed", None))
                        continue
                    
                    # Set adaptive thresholds based on measured noise
                    # Speech threshold: mean + 0.4, clamped between 0.5 and 0.8
                    self.dynamic_speech_th = max(
                        0.5,  # Minimum threshold
                        min(
                            self.noise_floor + 0.4,  # Adaptive offset
                            0.8  # Maximum threshold
                        )
                    )
                    
                    # Silence threshold: noise floor + small margin
                    self.dynamic_silence_th = max(
                        0.15,  # Minimum silence threshold
                        min(
                            self.noise_floor + 0.1,
                            self.dynamic_speech_th - 0.2  # Keep gap from speech threshold
                        )
                    )
                    
                    self.calibrated = True
                    print(f"✅ VAD Calibrated Successfully:")
                    print(f"   Noise floor: {self.noise_floor:.3f}")
                    print(f"   Noise std: {noise_std:.3f}")
                    print(f"   Noise max: {noise_max:.3f}")
                    print(f"   Speech threshold: {self.dynamic_speech_th:.3f}")
                    print(f"   Silence threshold: {self.dynamic_silence_th:.3f}")
                    print(f"✅ Environment calibration complete")
                    
                    events.append(("calibrated", None))
                else:
                    # Still calibrating
                    if self.calibration_frames % 10 == 0:
                        print(f"🎙️ Calibrating... {self.calibration_frames}/{self.calibration_limit} (prob={prob:.3f})")
                    events.append(("calibrating", None))
                
                continue  # Skip speech detection during calibration

            # 🛡️ Cooldown management: prevent immediate re-trigger after turn_complete
            if self.frames_since_turn_complete > 0:
                self.frames_since_turn_complete += 1
                if self.frames_since_turn_complete >= self.cooldown_frames:
                    self.frames_since_turn_complete = 0  # Cooldown expired
            
            # Speech frame (use dynamic thresholds after calibration)
            if prob >= self.dynamic_speech_th:
                self.speech_frames += 1
                self.silence_frames = 0
                
                # Store frame in recent buffer (for potential speech start)
                self.recent_frames.append(frame.copy())
                # Keep only last min_speech_frames + a few extra for context
                if len(self.recent_frames) > self.min_speech_frames + 5:
                    self.recent_frames.pop(0)

                # If speech has just started
                if not self.in_speech and self.speech_frames >= self.min_speech_frames:
                    # 🛡️ Skip speech_start if we're in cooldown period
                    if self.frames_since_turn_complete > 0:
                        # Still in cooldown - ignore this detection
                        self.speech_frames = 0
                        continue
                    
                    self.in_speech = True
                    # ✅ Include ALL recent frames that led to speech detection
                    # This ensures we don't lose the beginning of the utterance
                    self.buffer_frames = list(self.recent_frames)
                    #print(f"🎤 Speech started - preserving {len(self.buffer_frames)} frames from detection phase")
                    events.append(("speech_start", None))

                elif self.in_speech:
                    self.buffer_frames.append(frame.copy())
                    events.append(("speaking", None))

            # Silence frame (use dynamic threshold)
            else:
                self.silence_frames += 1
                
                # Store frame in recent buffer even during silence (for speech detection)
                if not self.in_speech:
                    self.recent_frames.append(frame.copy())
                    if len(self.recent_frames) > self.min_speech_frames + 5:
                        self.recent_frames.pop(0)

                if self.in_speech:
                    # Keep adding trailing silence
                    self.buffer_frames.append(frame.copy())

                    # 1️⃣ Short pause (still speaking)
                    if self.silence_frames < self.turn_complete_frames:
                        events.append(("silence", None))

                    # 2️⃣ Normal end of turn (turn_complete_frames reached)
                    elif self.silence_frames == self.turn_complete_frames:
                        # ✅ Validate utterance before finalizing
                        if self.buffer_frames:
                            utterance = np.concatenate(self.buffer_frames)
                            duration = len(utterance) / self.sample_rate
                            
                            # Only emit turn_complete if we have substantial audio (>0.5s)
                            if duration >= 0.5:
                                self.reset()
                                # Start cooldown period
                                self.frames_since_turn_complete = 1
                                events.append(("turn_complete", utterance))
                            else:
                                # Too short - likely false positive, discard
                                print(f"⚠️ Discarding short utterance ({duration:.2f}s)")
                                self.reset()
                        else:
                            # Empty buffer - discard
                            self.reset()

                    # 3️⃣ Very long pause → abandon incomplete speech (abandon_frames reached)
                    elif self.silence_frames == self.abandon_frames:
                        print("🗑️ Long silence during speech → abandoning buffer")
                        # Discard buffered audio
                        self.reset()
                        # Emit special event (DO NOT finalize utterance)
                        events.append(("speech_abandoned", None))
                    
                    # After abandon, stay silent
                    else:
                        pass  # Already handled by turn_complete or abandon

                else:
                    # Not currently in speech
                    self.speech_frames = 0

        return events


# ----------------- Session -----------------
class Session:
    def __init__(self, language: str, candidate_id: str):
        self.id = uuid.uuid4().hex
        self.candidate_id = candidate_id
        self.lang = "en" if language.lower().startswith("en") else "ur"
        self.voice = "en-US-SteffanNeural" if self.lang == "en" else "ur-PK-UzmaNeural"
        self.system_prompt = interview_prompt_en if self.lang == "en" else interview_prompt_ur
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.buffer = []  # legacy per-utterance chunks (still available for manual mode)
        self.utterance_active = False  # legacy flag
        self.conversation_history = []
        self.conversation_context = []
        self.previous_ai_question = None
        self.job_id: Optional[str] = None  # set after token verification
        
        # Question counter tracking
        self.question_counter = {'count': 0}

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        session_id = f"{candidate_id}_{timestamp}"
        self.conversation_filename = f"interviews/interview_{session_id}.json"
        os.makedirs("interviews", exist_ok=True)
        try:
            with open(self.conversation_filename, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "session_id": session_id,
                        "candidate_id": candidate_id,
                        "language": self.lang,
                        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "conversations": [],
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")

        # ----------------- Silero VAD per session -----------------
        # chunk_ms set to 30ms to work with typical browser chunk sizes
        try:
            self.vad = StreamingSileroVAD(sample_rate=SAMPLE_RATE, chunk_ms=30)
        except Exception as e:
            print(f"❌ VAD initialization error: {e}")
            self.vad = None

        # track a per-session lock to avoid overlapping STT/LLM tasks (we use cancellation for interruption)
        self.current_processing_task: Optional[asyncio.Task] = None

    # Legacy manual-mode helpers (still supported)
    def reset_utterance(self):
        self.buffer.clear()
        self.utterance_active = False

    def push_pcm(self, f32: np.ndarray):
        # Legacy buffering method kept for manual utterance mode
        self.buffer.append(f32)
        total_samples = sum(len(ch) for ch in self.buffer)
        print(f"🧩 push_pcm (legacy): chunk={len(f32)}, total={total_samples}")

    def current_audio(self) -> Optional[np.ndarray]:
        if not self.buffer:
            print("current_audio: empty buffer")
            return None
        total_samples = sum(len(ch) for ch in self.buffer)
        print(f"🔗 current_audio before concat: {len(self.buffer)} chunks, total={total_samples}")
        return np.concatenate(self.buffer)


# ----------------- Utterance Processing -----------------
async def process_utterance(sess: Session, audio: np.ndarray, ws: WebSocket):
    """
    Process a complete utterance: STT -> LLM -> TTS -> send results.
    This function is cancellable. If it is cancelled (due to interruption), it will attempt to stop gracefully.
    """
    try:
        # 1) Save temp WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_wav_path = tmp.name
        sf.write(temp_wav_path, audio, SAMPLE_RATE)
        sess.last_utterance_path = temp_wav_path
        duration_sec = len(audio) / SAMPLE_RATE
        print(f"💾 Utterance: {duration_sec:.2f}s -> {temp_wav_path}")

        # 2) STT
        lang_code = "en" if sess.lang == "en" else "ur"
        user_text = transcribe_from_wav(temp_wav_path, language=lang_code)
        print(f"📝 STT: {user_text}")
        await ws.send_text(json.dumps({"type": "stt", "text": user_text}))

        if not user_text or len(user_text.strip()) < 2:
            print(f"⚠️ Empty or very short transcription (duration: {duration_sec:.2f}s)")
            await ws.send_text(
                json.dumps({"type": "status", "level": "warn", "message": "empty_or_unclear_audio"})
            )
            try:
                os.remove(temp_wav_path)
            except:
                pass
            return

        # Store user answer temporarily - we'll save it after getting AI response with status

        # Add to conversation context (keep last 2 pairs)
        if sess.previous_ai_question:
            sess.conversation_context.append((sess.previous_ai_question, user_text))
            if len(sess.conversation_context) > 2:
                sess.conversation_context = sess.conversation_context[-2:]

        # 3) No RAG context (skill-graph prompt drives questions)
        context = ""

        # 4) LLM: call with running history (query_groq handles appending user message)
        ai_text, updated_history = query_groq(
            user_input=user_text,
            context=context,
            max_tokens=800,  # Increased to prevent cut-off responses
            conversation_history=sess.conversation_history,
            interview_prompt=sess.system_prompt  # Pass the selected prompt
        )
        sess.conversation_history = updated_history
        sess.messages = list(sess.conversation_history)

        # ✅ Parse the AI response to extract clean question and status
        clean_ai_question, status = parse_llm_response_for_status_and_question(ai_text)
        print(f"🤖 AI (raw): {ai_text[:120]}...")
        print(f"🤖 AI (clean): {clean_ai_question[:120]}...")
        print(f"📊 Status: {status}")
        
        # ✅ Save the PREVIOUS Q&A pair now that we have the status from current AI response
        if sess.previous_ai_question:
            try:
                print(f"💾 Saving QA pair to {sess.conversation_filename}")
                print(f"   Q: {sess.previous_ai_question[:100]}...")
                print(f"   A: {user_text[:100]}...")
                print(f"   Status: {status if status else 'unknown'}")
                save_conversation_with_status(
                    sess.previous_ai_question,
                    user_text,
                    status,
                    sess.conversation_filename,
                    sess.question_counter['count']
                )
                print("✅ QA pair saved successfully")
            except Exception as e:
                print(f"❌ Error saving conversation: {e}")
                traceback.print_exc()
        
        # ✅ Update counter if status is valid
        if status:
            incremented, current_count = increment_counter_if_valid(sess.question_counter, status)
        
        # ✅ Check if interview should end
        if should_end_interview(sess.question_counter):
            end_message = generate_interview_end_message(sess.lang)
            await ws.send_text(json.dumps({"type": "ai_text", "text": end_message}))
            await ws.send_text(json.dumps({"type": "interview_complete", "total_questions": sess.question_counter['count']}))
            print(f"🎉 Interview completed with {sess.question_counter['count']} valid answers")
            
            # Generate TTS for end message
            end_audio_bytes = await tts_mp3_bytes(end_message, sess.voice)
            if end_audio_bytes and len(end_audio_bytes) > 0:
                await ws.send_text(json.dumps({"type": "audio", "mime": "audio/mpeg", "size": len(end_audio_bytes)}))
                await ws.send_bytes(end_audio_bytes)
            else:
                print("⚠️ TTS generation failed for end message")
                await ws.send_text(json.dumps({"type": "status", "level": "warn", "message": "tts_failed"}))
            
            # Clean up and return
            try:
                os.remove(temp_wav_path)
            except:
                pass
            return

        # 5) Send clean AI text (without JSON metadata)
        await ws.send_text(json.dumps({"type": "ai_text", "text": clean_ai_question}))
        print(f"📤 Sending to client: {clean_ai_question[:120]}...")

        # 6) TTS (this can be long; still cancellable) - use clean question
        audio_bytes = await tts_mp3_bytes(clean_ai_question, sess.voice)

        # Before sending TTS bytes, check if task was cancelled
        if asyncio.current_task().cancelled():
            print("🚫 process_utterance cancelled before TTS send")
            try:
                os.remove(temp_wav_path)
            except:
                pass
            return

        # Check if TTS generation succeeded
        if audio_bytes and len(audio_bytes) > 0:
            await ws.send_text(json.dumps({"type": "audio", "mime": "audio/mpeg", "size": len(audio_bytes)}))
            await ws.send_bytes(audio_bytes)
        else:
            print("⚠️ TTS generation failed, skipping audio playback")
            await ws.send_text(json.dumps({"type": "status", "level": "warn", "message": "tts_failed"}))

        # ✅ Store the NEW clean AI question for the NEXT user answer
        sess.previous_ai_question = clean_ai_question
        print(f"📌 Set previous_ai_question for next turn: {clean_ai_question[:100]}...")

        # Cleanup
        try:
            os.remove(temp_wav_path)
        except:
            pass

    except asyncio.CancelledError:
        # Task was cancelled (e.g., user interrupted while AI speaking). Clean up and return.
        print("🚫 process_utterance: Cancelled")
        try:
            # best-effort remove temp wav
            if 'temp_wav_path' in locals():
                try:
                    os.remove(temp_wav_path)
                except:
                    pass
        finally:
            raise
    except Exception as e:
        print(f"❌ Error processing utterance: {e}")
        import traceback
        traceback.print_exc()
        try:
            await ws.send_text(json.dumps({"type": "status", "level": "err", "message": f"error: {e}"}))
        except:
            pass

# ----------------- WebSocket Handler -----------------
@app1.websocket("/interview")
async def ws_handler(ws: WebSocket):
    await ws.accept()
    sess: Optional[Session] = None

    # Track current processing (LLM/TTS) task per connection so we can cancel on interruption
    current_processing_task: Optional[asyncio.Task] = None

    try:
        while True:
            msg = await ws.receive()

            # --------- Text messages (JSON) ----------
            if "text" in msg and msg["text"] is not None:
                try:
                    data = json.loads(msg["text"])
                except json.JSONDecodeError:
                    await ws.send_text(json.dumps({"type": "status", "level": "err", "message": "Invalid JSON"}))
                    continue

                typ = data.get("type")

                # ---------- Session start ----------
                if typ == "start":
                    # ✅ Get and verify JWT token
                    token = data.get("token")
                    print("🔑 Received token:", token)
                    if not token:
                        await ws.send_text(json.dumps({
                            "type": "status",
                            "level": "err",
                            "message": "Authentication required"
                        }))
                        await ws.close()
                        return
                    try:
                         # ✅ Format token properly for verify_token (it expects "Bearer {token}")
                        authorization = f"Bearer {token}"
                        print(f"📤 Calling verify_token with: {authorization[:50]}...")

                        user_info = verify_token(authorization=authorization)
                        candidate_id = user_info["candidate_id"]
                        email = user_info.get("email", "unknown")
                        print(f"✅ Authenticated: {email} (ID: {candidate_id})")

                    except HTTPException as e:
                        print(f"❌ Authentication failed: {e.status_code} - {e.detail}")
                        await ws.send_text(json.dumps({
                            "type": "status",
                            "level": "err",
                            "message": f"Authentication failed: {e.status_code}: {e.detail}"
                        }))
                        await ws.close()
                        return
                    
                    except Exception as e:
                        await ws.send_text(json.dumps({
                            "type": "status",
                            "level": "err",
                            "message": f"Authentication failed: {str(e)}"
                        }))
                        await ws.close()
                        return
                
                    lang = (data.get("language") or "en").lower()
                    sess = Session(lang, candidate_id)
                    sess.job_id = user_info.get("job_id")  # store job_id from token

                    if not sess.job_id:
                        await ws.send_text(json.dumps({
                            "type": "status",
                            "level": "err",
                            "message": "Missing job_id for this candidate"
                        }))
                        await ws.close()
                        return

                    system_prompt = build_system_prompt(sess.job_id)
                    if not system_prompt:
                        await ws.send_text(json.dumps({
                            "type": "status",
                            "level": "err",
                            "message": "Job not found or skill graph unavailable"
                        }))
                        await ws.close()
                        return

                    sess.system_prompt = system_prompt
                    sess.messages = [{"role": "system", "content": system_prompt}]
                    
                    # Extract session_id from conversation filename
                    # Format: "interviews/interview_cand_20f6562e_20260219_003124.json"
                    # Extract the session part after "interview_"
                    session_filename_part = sess.conversation_filename.split("interview_")[-1].replace(".json", "")
                    
                    await ws.send_text(json.dumps({
                        "type": "session_initialized", 
                        "candidate_id": candidate_id,
                        "session_id": session_filename_part,
                        "job_id": sess.job_id,
                        "email": user_info['email'],
                        "language": sess.lang,
                        "message": f"Session started for {user_info['email']} ({sess.lang})"
                    }))

                    # Voice + prompt + greeting
                    if sess.lang == "en":
                        sess.voice = "en-US-SteffanNeural"
                        interview_prompt = interview_prompt_en
                        greet_text = "Hello! Welcome to our interview. I am excited to learn about you. Could you start by telling me about your background and what brought you to data science?"
                    else:
                        sess.voice = "ur-PK-UzmaNeural"
                        interview_prompt = interview_prompt_ur
                        greet_text = "ہیلو! ہمارے انٹرویو میں خوش آمدید۔ کیا آپ مجھے اپنے تکنیکی پس منظر کے بارے میں بتا کر شروع کر سکتے ہیں اور آپ کو ڈیٹا سائنس تک کیا لایا ہے؟"

                    # Initialize conversation history (system + assistant greeting)
                    sess.conversation_history = [
                        {"role": "system", "content": sess.system_prompt},
                        {"role": "assistant", "content": greet_text},
                    ]
                    sess.messages = list(sess.conversation_history)
                    sess.previous_ai_question = greet_text
                    sess.conversation_context = []

                    # Send greeting (text + TTS)
                    await ws.send_text(json.dumps({"type": "ai_text", "text": greet_text}))
                    greeting_audio = await tts_mp3_bytes(greet_text, sess.voice)
                    await ws.send_text(json.dumps({"type": "audio", "mime": "audio/mpeg", "size": len(greeting_audio)}))
                    await ws.send_bytes(greeting_audio)

                    # Ready
                    await ws.send_text(json.dumps({"type": "status", "level": "ok", "message": "ready_for_audio"}))

                # ---------- Legacy manual utterance_start ----------
                # elif typ == "utterance_start":
                #     # kept for backward compatibility; when using Silero VAD backend you can omit these calls
                #     print("🎤 Received legacy utterance_start")
                #     if not sess:
                #         await ws.send_text(json.dumps({"type": "status", "level": "err", "message": "no session"}))
                #         continue
                #     sess.reset_utterance()
                #     sess.utterance_active = True
                #     await ws.send_text(json.dumps({"type": "status", "level": "info", "message": "listening (legacy mode)"}))

                # ---------- Legacy manual utterance_end ----------
                # elif typ == "utterance_end":
                #     if not sess:
                #         await ws.send_text(json.dumps({"type": "status", "level": "err", "message": "no session"}))
                #         continue
                    

                #     # If there is an ongoing automatic processing task, cancel it (behaviour consistent with interruption)
                #     if current_processing_task and not current_processing_task.done():
                #         print("🛑 Cancelling running AI task due to manual utterance_end")
                #         current_processing_task.cancel()
                #         current_processing_task = None
                #         # send silent audio to stop client playback
                #         await ws.send_bytes(SILENT_MP3_BYTES)

                #     # Use manual buffered audio
                #     sess.utterance_active = False
                #     audio = sess.current_audio()
                #     sess.reset_utterance()

                #     if audio is None or audio.size == 0:
                #         await ws.send_text(json.dumps({"type": "status", "level": "warn", "message": "no audio received"}))
                #         continue

                #     # Start processing in background (so WS loop continues)
                #     current_processing_task = asyncio.create_task(process_utterance(sess, audio, ws))

                #     def _cb(task: asyncio.Task):
                #         try:
                #             task.result()
                #         except asyncio.CancelledError:
                #             print("🚫 Manual processing task cancelled")
                #         except Exception as e:
                #             print(f"❌ Manual processing task error: {e}")

                #     current_processing_task.add_done_callback(_cb)

                # ---------- Stop session ----------
                elif typ == "stop":
                    # ✅ Cancel any ongoing AI task immediately
                    if current_processing_task and not current_processing_task.done():
                        print("🛑 Cancelling running AI task due to session stop")
                        current_processing_task.cancel()
                        current_processing_task = None
                        # send silent audio to stop client playback
                        try:
                            await ws.send_bytes(SILENT_MP3_BYTES)
                        except Exception as e:
                            print(f"⚠️ Could not send silent bytes on stop: {e}")

                    if sess:
                        await ws.send_text(json.dumps({"type": "session_ended", "filename": sess.conversation_filename, "message": "session closed"}))
                    await ws.send_text(json.dumps({"type": "status", "level": "ok", "message": "session closed"}))
                    break

                else:
                    await ws.send_text(json.dumps({"type": "status", "level": "err", "message": f"unknown type {typ}"}))

            # --------- Binary messages (PCM16 frames) ----------
            elif "bytes" in msg and msg["bytes"] is not None:
                # Convert PCM16 -> float32 mono [-1, 1]
                f32 = pcm16_bytes_to_float32(msg["bytes"])

                # If no session yet, ignore
                if not sess:
                    continue

                # If we have a current AI processing task (LLM/TTS) running, we still pass incoming audio to VAD to detect interruption.
                # On speech_start while AI is running -> cancel AI task and stop playback to listen to user.
                if sess.vad is None:
                    # No VAD available - fallback to legacy buffering if utterance_active
                    if sess.utterance_active:
                        sess.push_pcm(f32)
                    continue

                vad_events = sess.vad.process_chunk(f32)

                for event, utterance in vad_events:
                    # Calibration in progress
                    if event == "calibrating":
                        # Optional: notify client that calibration is happening
                        # await ws.send_text(json.dumps({"type": "status", "level": "info", "message": "calibrating_environment"}))
                        continue
                    
                    # Calibration failed (speech detected during calibration)
                    if event == "calibration_failed":
                        print("❌ Calibration failed - retrying...")
                        await ws.send_text(json.dumps({
                            "type": "status", 
                            "level": "warn", 
                            "message": "calibration_failed_retrying"
                        }))
                        continue
                    
                    # Calibration complete
                    if event == "calibrated":
                        print("✅ Environment calibration complete")
                        await ws.send_text(json.dumps({"type": "status", "level": "ok", "message": "environment_calibrated"}))
                        continue
                    
                    # Speech started
                    if event == "speech_start":
                        print("🎤 VAD event: speech_start")
                        
                        # ALWAYS send silence bytes to force client stop (in case it's playing buffered audio)
                        try:
                            await ws.send_bytes(SILENT_MP3_BYTES)
                        except Exception as e:
                            print(f"⚠️ Could not send silent bytes: {e}")

                        # If AI currently processing/speaking, interrupt
                        if current_processing_task and not current_processing_task.done():
                            print("🛑 Interrupting AI (user spoke during AI response)")
                            current_processing_task.cancel()
                            current_processing_task = None

                        # No explicit "start recording" required - VAD buffer already collecting frames internally.
                        # But if you also want legacy behavior (start storing raw chunks), enable:
                        # sess.utterance_active = True
                        # sess.push_pcm(f32)
                        await ws.send_text(json.dumps({"type": "status", "level": "info", "message": "speech_detected"}))
                        continue

                    # While speaking (VAD in speech), nothing to do (server just accumulates internal buffer)
                    if event == "speaking":
                        # optional debug logging
                        # print("🗣️ speaking...")
                        continue

                    # Silence during speech (not yet long enough)
                    if event == "silence":
                        continue

                    # Turn complete: VAD returns the full utterance audio as a numpy array
                    if event == "turn_complete" and utterance is not None:
                        print("✅ VAD turn_complete — scheduling processing")
                        # Start processing in background (cancellable)
                        current_processing_task = asyncio.create_task(process_utterance(sess, utterance, ws))

                        def _cb2(task: asyncio.Task):
                            try:
                                task.result()
                            except asyncio.CancelledError:
                                print("🚫 VAD processing task cancelled")
                            except Exception as e:
                                print(f"❌ VAD processing task failed: {e}")

                        current_processing_task.add_done_callback(_cb2)

                        # notify client we're ready for next audio (or you can wait)
                        await ws.send_text(json.dumps({"type": "status", "level": "ok", "message": "processing"}))
                        continue

                # Event None -> no change
                # (optional) if you want to keep a legacy raw buffer while VAD runs:
                # if sess.utterance_active:
                #     sess.push_pcm(f32)

    except WebSocketDisconnect:
        print(f"📤 Client disconnected: {sess.id if sess else 'no session'}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await ws.send_text(json.dumps({"type": "status", "level": "err", "message": f"server error: {e}"}))
        except:
            pass
    finally:
        try:
            await ws.close()
        except:
            pass


# ----------------- Run Server -----------------
if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting VAD + Turn Detection Server on http://localhost:8000")
    uvicorn.run(app1, host="0.0.0.0", port=8000)