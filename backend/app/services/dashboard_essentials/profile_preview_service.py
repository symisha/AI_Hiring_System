
from app.database.db_queries.profile_db import get_company_by_user_id
from pydantic import BaseModel

class ProfilePreview(BaseModel):
    username: str
    email: str
    industry: str | None = None
    location: str | None = None

def profile_preview_service(user):
    company = get_company_by_user_id(user.user.id)

    return ProfilePreview(
        username = company.get("name") if company else "Unknown",
        industry = company.get("industry") if company else "Unknown",
        location = company.get("location") if company else "Unknown",
        email = user.user.user_metadata.get("email", "Unknown")
    )
