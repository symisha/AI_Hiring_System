from fastapi import  Request, APIRouter
from pydantic import BaseModel
from supabase import create_client, Client
from app.database.db_connection import supabase
import os

router = APIRouter()

# Initialize your Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


class ViolationReport(BaseModel):
    test_id: str
    violation_type: str
    details: str

@router.post("/api/v1/log-violation")
async def log_violation(report: ViolationReport):
    # 1. Fetch current logs for this test
    # This is better than fetching and appending in Python to avoid race conditions
    # We use a PostgreSQL "JSONB Concatenation" trick
    
    new_entry = {
        "type": report.violation_type,
        "details": report.details,
        "timestamp": "now()" # Or pass from frontend
    }

    try:
        # 2. Append the new log to the existing 'security_logs' JSON array
        # This SQL-style update ensures we don't lose previous logs
        response = supabase.rpc(
            'append_security_log', 
            {'t_id': report.test_id, 'new_log': new_entry}
        ).execute()
        
        return {"status": "success", "message": "Security signal recorded"}
    except Exception as e:
        return {"status": "error", "message": str(e)}