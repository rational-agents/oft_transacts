# backend/src/app/api/users.py
from fastapi import APIRouter, Depends
from app.db.models.users import User
from app.schemas import UserProfile
from app.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserProfile)
def get_my_user_profile(current_user: User = Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user

    Args:
        current_user (User): The currently authenticated user

    Returns:
        UserProfile: The profile of the currently authenticated user
    """
    return {
        "username": current_user.username,
        "email": current_user.email
    }
