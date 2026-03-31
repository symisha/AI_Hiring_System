import uuid
from pydantic import BaseModel
from typing import Any, Dict
from app.database.db_connection import supabase

class JobCreate(BaseModel):
    title: str
    short_description: str # Matches the frontend key
    metadata: Dict[str, Any]