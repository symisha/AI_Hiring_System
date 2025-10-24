from fastapi import APIRouter                      # Import FastAPI class to create the web application
from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database

router = APIRouter()  # Create a router instance to define API endpoints
@router.get("/test-db")
def test_db():
    try:
        data = supabase.table("companies").select("*").limit(1).execute()
        return {"status": "connected ✅", "sample": data.data}
    except Exception as e:
        return {"status": "failed ❌", "error": str(e)}
