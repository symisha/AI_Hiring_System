from fastapi import APIRouter, Depends
from app.auth_middleware import auth_middleware         # Import the authentication middleware to protect routes
from app.services.dashboard_essentials.profile_preview_service import profile_preview_service, ProfilePreview

router = APIRouter()

@router.get("/profile", response_model=ProfilePreview)
def profile_preview_endpoint(user=Depends(auth_middleware)):
    return profile_preview_service(user)
