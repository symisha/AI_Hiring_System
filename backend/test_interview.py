#!/usr/bin/env python3
"""
Quick test script for AI Interview WebSocket
Run after starting the FastAPI server with: python -m uvicorn app.main:app --reload
"""
import asyncio
import websockets
import json

async def test_interview():
    uri = "ws://localhost:8000/ws/interview"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to interview WebSocket!")
            
            # Send init message
            init_msg = {
                "type": "init",
                "language": "en",  # or "ur" for Urdu
                "candidate_id": "test_candidate_123"
            }
            await websocket.send(json.dumps(init_msg))
            print(f"📤 Sent: {init_msg}")
            
            # Listen for responses
            print("\n🎧 Listening for AI responses (press Ctrl+C to stop)...\n")
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    
                    msg_type = data.get("type")
                    
                    if msg_type == "ai_text":
                        print(f"🤖 AI: {data.get('text', '')}")
                    elif msg_type == "ai_audio":
                        print(f"🔊 AI audio received ({len(data.get('audio', ''))} bytes)")
                    elif msg_type == "stt":
                        print(f"📝 Transcription: {data.get('text', '')}")
                    elif msg_type == "status":
                        print(f"ℹ️  Status: {data.get('message', '')}")
                    elif msg_type == "error":
                        print(f"❌ Error: {data.get('message', '')}")
                    elif msg_type == "interview_complete":
                        print(f"✅ Interview Complete! Score: {data.get('score', 'N/A')}")
                        print(f"   Transcript: {data.get('transcript_url', 'N/A')}")
                        break
                    else:
                        print(f"📦 Received: {data}")
                        
                except asyncio.TimeoutError:
                    print("⏱️  No response for 30 seconds")
                    break
                    
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the server running?")
        print("   Start server with: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎙️ AI Interview WebSocket Test\n")
    print("Make sure the server is running first!")
    print("=" * 50)
    
    try:
        asyncio.run(test_interview())
    except KeyboardInterrupt:
        print("\n\n👋 Test ended by user")
