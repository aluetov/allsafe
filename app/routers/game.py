from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_session
from app.db.models import Game, GamePlayer, User
from app.dependencies.auth import get_current_user
from app.game.enum import GameStatus
from app.schemas.game import GameCreate, GameListResponse, GameResponse

router = APIRouter(prefix="/games")


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_data: GameCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Game:
    game = Game(max_players=game_data.max_players)
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
