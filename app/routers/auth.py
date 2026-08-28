from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token, hash_password, verify_password
from app.db.db import get_session
from app.db.models import User
from app.schemas.auth import TokenResponse, UserLogin
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
    except IntegrityError:  # TODO: Handle only the username unique-constraint violation.
        await session.rollback()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists") from None

    await session.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid username or password"}},
)
async def login(
    user_login: UserLogin, session: Annotated[AsyncSession, Depends(get_session)]
) -> TokenResponse:
    stmt = select(User).where(User.username == user_login.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )  # later can be changed to "Username not found"

    if not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )  # later can be changed to "Password is incorrect"

    payload = {"sub": str(user.id)}

    token = create_token(payload)

    token_response = TokenResponse(access_token=token, token_type="bearer")  # nosec B106

    return token_response
