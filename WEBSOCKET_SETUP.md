# AI Interview WebSocket - Quick Start Guide

## 🚀 What's Been Set Up

### ✅ Backend
- **WebSocket Endpoint**: `/ws/interview` - Real-time audio interview
- **Test Page**: `/interview-test` - HTML interface for testing
- **Main API**: Integrated in `main.py`

### ✅ Frontend
- Basic HTML/JS test page with WebSocket client
- Audio recording and playback
- Real-time transcription display
- Interview progress tracking

---

## 📋 What's Still Missing

### 1. **Audio Format Conversion**
- Frontend sends WebM audio, but backend expects PCM16
- **Solution needed**: Add audio format conversion in `interview_api.py`

### 2. **FAISS Index Files**
```bash
# Missing files:
- backend/app/services/associate_data_scientist.pdf
- faiss_index.bin
- questions1_.json
```
**Fix**: Create these or make them optional in `ai_interview.py`

### 3. **Environment Variables**
API keys are hardcoded. Move to `.env`:
```bash
# Add to .env file:
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### 4. **Database Integration**
- Interview results not saved to Supabase
- No scoring calculations
- **Needed**: Add `save_interview_results()` function

### 5. **Templates Directory**
```bash
# interview_api.py references:
- templates/index.html (line 172)
- static/ directory (line 173)
```
These are optional - the test page works without them.

---

## 🎮 How to Test

### Step 1: Install Dependencies
```bash
cd /home/aliza-ashfaq/Desktop/FYP/AI_Hiring_System/backend

# Install missing packages
pip install soundfile websockets
```

### Step 2: Start the Server
```bash
# Make sure you're in the backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Open Test Page
```
http://localhost:8000/interview-test
```

### Step 4: Test the Interview
1. **Enter candidate ID**: `test_candidate_123`
2. **Select language**: English or Urdu
3. **Click "Connect to Interview"**
4. **Allow microphone access**
5. **Click the microphone button** to record your answer
6. **Wait for AI response** (text + audio)

---

## 🐛 Common Errors & Fixes

### Error: "Could not load Silero VAD model"
```bash
# The model downloads automatically on first run
# If it fails, check your internet connection
```

### Error: "Microphone access denied"
```
Solution: Allow microphone in browser settings
Chrome: Settings > Privacy > Site Settings > Microphone
```

### Error: "Module 'services.ai_interview' not found"
```
✅ FIXED: Import path corrected to 'app.services.ai_interview'
```

### Error: "No module named 'jwt_auth'"
```
✅ FIXED: Removed unused import from interview_api.py
```

---

## 📁 File Structure

```
backend/
├── app/
│   ├── main.py                    # ✅ WebSocket integrated here
│   ├── api/
│   │   └── interview_api.py       # ✅ Fixed imports
│   └── services/
│       └── ai_interview.py        # ✅ Core interview logic
├── static/
│   └── interview-test.html        # ✅ Test frontend
└── requirements.txt               # ⚠️ Update with new dependencies
```

---

## 🔄 Expected Flow

```
1. Frontend connects via WebSocket
   ↓
2. Sends 'init' message with language & candidate_id
   ↓
3. Backend initializes session with VAD & FAISS
   ↓
4. AI sends greeting question (text + audio)
   ↓
5. User records answer via microphone
   ↓
6. Frontend sends audio chunks
   ↓
7. Backend transcribes with Whisper
   ↓
8. AI analyzes answer & generates next question
   ↓
9. Repeat until 10 questions completed
   ↓
10. Interview ends, conversation saved to JSON
```

---

## 🎯 Next Steps

### High Priority:
1. **Fix Audio Format**: Add PCM16 conversion in frontend
2. **Create FAISS Index**: Generate from PDF or make optional
3. **Test End-to-End**: Full interview flow with audio

### Medium Priority:
4. **Add Authentication**: JWT token validation for WebSocket
5. **Database Integration**: Save results to Supabase
6. **Error Handling**: Better error messages to frontend

### Low Priority:
7. **Production TTS**: Use faster TTS service
8. **Optimize Models**: Switch to smaller/faster models
9. **Add Logging**: Track interview metrics

---

## 📞 Test Commands

```bash
# Check if server is running
curl curl ${BACKEND_URL}/

# Check WebSocket endpoint (requires wscat)
npm install -g wscat
wscat -c ws://localhost:8000/ws/interview

# Test with Python
python -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8000/ws/interview') as ws:
        await ws.send(json.dumps({
            'type': 'init',
            'language': 'en',
            'candidate_id': 'test123'
        }))
        response = await ws.recv()
        print(f'✅ Response: {response}')

asyncio.run(test())
"
```

---

## 🏁 Success Criteria

You'll know it's working when:
- ✅ Test page loads at `/interview-test`
- ✅ WebSocket connects successfully
- ✅ Microphone recording works
- ✅ AI greeting appears in chat
- ✅ Audio playback works
- ✅ Transcription shows user speech
- ✅ Next question generates after answer

---

## 💡 Tips

1. **Use Chrome/Edge** - Best WebSocket & audio support
2. **Check Console** - Errors show in browser DevTools (F12)
3. **Monitor Terminal** - Backend logs show processing steps
4. **Test Microphone** - Use browser's built-in test first
5. **Start Simple** - Test with text messages before audio

---

Good luck with your AI interview system! 🚀
