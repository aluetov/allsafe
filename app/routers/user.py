from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.models import User
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserResponse)
async def get_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
