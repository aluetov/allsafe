from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import get_session
from app.db.models import Game, GamePlayer, User
from app.dependencies.auth import get_current_user
from app.schemas.game import GameCreate, GameResponse

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
