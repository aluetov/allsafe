from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_session
from app.db.models import Game, GamePlayer, User
from app.dependencies.auth import get_current_user
from app.game.enum import GameStatus
from app.schemas.game import GameCreate, GameListResponse, GameResponse
from app.schemas.game_player import GamePlayerResponse
from app.game.enum import PlayerStatus, GameAccess

router = APIRouter(prefix="/games")


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_data: GameCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Game:
    game = Game(
        game_type=GameAccess.PRIVATE,
        min_players=game_data.min_players,
        max_players=game_data.max_players,
        owner_id=current_user.id,
    )
    session.add(game)

    await session.flush()

    creator = GamePlayer(
        game_id=game.id,
        user_id=current_user.id,
    )
    session.add(creator)

    await session.commit()
    await session.refresh(game)

    return game


@router.get("", response_model=list[GameListResponse])
async def get_games(session: Annotated[AsyncSession, Depends(get_session)]) -> list[GameListResponse]:
    stmt = (
        select(
            Game,
            func.count(GamePlayer.id).label("current_players"),
        )
        .join(
            GamePlayer,
            GamePlayer.game_id == Game.id,
        )
        .where(Game.status == GameStatus.WAITING)
        .group_by(Game.id)
        .order_by(Game.created_at.desc())
    )
    result = await session.execute(stmt)
    rows = result.all()

    return [
        GameListResponse(
            **GameResponse.model_validate(game).model_dump(),
            current_players=current_players,
        )
        for game, current_players in rows
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
    }
)
async def join_game(
    game_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GamePlayer:
    result = await session.execute(
        select(Game)
        .where(Game.id == game_id)
        .with_for_update()
    )
    game = result.scalar_one_or_none()

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    if game.status != GameStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The game has already started",
        )

    existing_player = await session.scalar(
        select(GamePlayer).where(
            GamePlayer.game_id == game.id,
            GamePlayer.user_id == current_user.id,
        )
    )

    if existing_player is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already joined this game",
        )

    player_count = await session.scalar(
        select(func.count())
        .select_from(GamePlayer)
        .where(GamePlayer.game_id == game.id)
    )

    if player_count >= game.max_players:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The game is full",
        )

    player = GamePlayer(
        game_id=game.id,
        user_id=current_user.id,
    )

    session.add(player)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already joined this game",
        )

    await session.refresh(player)

    return player


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
async def leave_game(
    game_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(
        select(Game)
        .where(Game.id == game_id)
        .with_for_update()
    )
    game = result.scalar_one_or_none()

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    if game.status != GameStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The game has already started",
        )

    existing_player = await session.scalar(
        select(GamePlayer).where(
            GamePlayer.game_id == game.id,
            GamePlayer.user_id == current_user.id,
        )
    )

    if existing_player is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are not a player in this game",
        )

    await session.delete(existing_player)
    await session.commit()


