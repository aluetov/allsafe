from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.db import get_session
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Username already exists",
        }
    },
)
async def register(user_create: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]) -> User:

    stmt = select(User).where(User.username == user_create.username)
    result = await session.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    user = User(username=user_create.username, password_hash=hash_password(user_create.password))

    session.add(user)

    try:  # if two people insert the same username at the same time
        await session.commit()
    except IntegrityError:
        await session.rollback()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists") from None

    await session.refresh(user)
    return user
