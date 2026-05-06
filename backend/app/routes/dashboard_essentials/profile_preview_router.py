from fastapi import APIRouter, Depends
from app.auth_middleware import get_current_user         # Import the authentication dependency to protect routes
from app.services.dashboard_essentials.profile_preview_service import profile_preview_service, ProfilePreview

router = APIRouter()

@router.get("/profile", response_model=ProfilePreview)
def profile_preview_endpoint(user=Depends(get_current_user)):
    return profile_preview_service(user)
