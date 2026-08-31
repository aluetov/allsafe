from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_session
from app.db.models import Game, GamePlayer, User
from app.dependencies.auth import get_current_user
from app.game.exceptions import (
    GameAlreadyStartedError,
    GameFullError,
    GameNotFoundError,
    PlayerAlreadyJoinedError,
    PlayerNotInGameError,
)
from app.game.service import (
    create_private_game,
    find_or_create_public_game,
)
from app.game.service import (
    get_waiting_games as get_waiting_games_service,
)
from app.game.service import (
    join_lobby as join_lobby_service,
)
from app.game.service import (
    leave_lobby as leave_lobby_service,
)
from app.schemas.game import GameCreate, GameListResponse, GameResponse
from app.schemas.game_player import GamePlayerResponse

router = APIRouter(prefix="/games")


@router.post(
    "",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_game(
    game_data: GameCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Game:
    return await create_private_game(
        session=session,
        owner_id=current_user.id,
        min_players=game_data.min_players,
        max_players=game_data.max_players,
    )


@router.get("", response_model=list[GameListResponse])
async def get_games(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[GameListResponse]:
    games = await get_waiting_games_service(session=session)

    return [
        GameListResponse(
            **GameResponse.model_validate(game).model_dump(),
            current_players=current_players,
        )
        for game, current_players in games
    ]


@router.post(
    "/{game_id}/join",
    response_model=GamePlayerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Game not found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Game already started, is full, or user already joined",
        },
    },
)
async def join_lobby(
    game_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GamePlayer:
    try:
        return await join_lobby_service(
            session=session,
            game_id=game_id,
            user_id=current_user.id,
        )
    except GameNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        ) from error
    except GameAlreadyStartedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The game has already started",
        ) from error
    except PlayerAlreadyJoinedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already joined this game",
        ) from error
    except GameFullError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The game is full",
        ) from error


@router.post(
    "/{game_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Game not found",
        },
        status.HTTP_409_CONFLICT: {
            "description": "Game already started or user is not a player",
        },
    },
)
async def leave_lobby(
    game_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    try:
        await leave_lobby_service(
            session=session,
            game_id=game_id,
            user_id=current_user.id,
        )
    except GameNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        ) from error
    except GameAlreadyStartedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The game has already started",
        ) from error
    except PlayerNotInGameError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are not a player in this game",
        ) from error


@router.post(
    "/play",
    response_model=GameResponse,
    status_code=status.HTTP_200_OK,
)
async def play_game(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Game:
    return await find_or_create_public_game(
        session=session,
        user_id=current_user.id,
    )
