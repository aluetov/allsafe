from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.db import get_session
from app.db.models import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
        detail="Invalid authentication credentials",
    )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except InvalidTokenError:
        raise credentials_exception from None

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise credentials_exception

    try:
        user_id = UUID(subject)
    except ValueError:
        raise credentials_exception from None

    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)

    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user
