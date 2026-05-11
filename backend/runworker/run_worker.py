import asyncio
from backend.app.services.screening_scheduler import screening_scheduler_loop

if __name__ == "__main__":
    print("[WORKER] AI Screening Engine Starting...")
    try:
        asyncio.run(screening_scheduler_loop())
    except KeyboardInterrupt:
        print("[WORKER] Shutting down gracefully...")