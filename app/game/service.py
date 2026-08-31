from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Game, GamePlayer
from app.game.enum import GameAccess, GameStatus
from app.game.exceptions import (
    GameAlreadyStartedError,
    GameFullError,
    GameNotFoundError,
    PlayerAlreadyJoinedError,
    PlayerNotInGameError,
)

PUBLIC_MATCHMAKING_LOCK_ID = 1_001


async def find_or_create_public_game(
    session: AsyncSession,
    user_id: UUID,
) -> Game:
    existing_game_stmt = (
        select(Game)
        .join(GamePlayer, GamePlayer.game_id == Game.id)
        .where(
            GamePlayer.user_id == user_id,
            Game.game_type == GameAccess.PUBLIC,
            Game.status == GameStatus.WAITING,
        )
        .order_by(Game.created_at.asc())
        .limit(1)
    )

    existing_game = await session.scalar(existing_game_stmt)

    if existing_game is not None:
        return existing_game

    await session.execute(
        select(
            func.pg_advisory_xact_lock(
                PUBLIC_MATCHMAKING_LOCK_ID,
            )
        )
    )

    # Recheck because this request may have waited for the lock.
    existing_game = await session.scalar(existing_game_stmt)

    if existing_game is not None:
        await session.commit()
        return existing_game

    player_count = (
        select(func.count(GamePlayer.id))
        .where(GamePlayer.game_id == Game.id)
        .correlate(Game)
        .scalar_subquery()
    )

    game = await session.scalar(
        select(Game)
        .where(
            Game.game_type == GameAccess.PUBLIC,
            Game.status == GameStatus.WAITING,
            player_count < Game.max_players,
        )
        .order_by(Game.created_at.asc())
        .limit(1)
        .with_for_update()
    )

    if game is None:
        game = Game()
        session.add(game)
        await session.flush()

    player = GamePlayer(
        game_id=game.id,
        user_id=user_id,
    )
    session.add(player)

    await session.commit()
    await session.refresh(game)

    return game


async def leave_lobby(
    session: AsyncSession,
    game_id: UUID,
    user_id: UUID,
) -> None:
    game = await session.scalar(select(Game).where(Game.id == game_id).with_for_update())

    if game is None:
        raise GameNotFoundError

    if game.status != GameStatus.WAITING:
        raise GameAlreadyStartedError

    player = await session.scalar(
        select(GamePlayer).where(
            GamePlayer.game_id == game.id,
            GamePlayer.user_id == user_id,
        )
    )

    if player is None:
        raise PlayerNotInGameError

    await session.delete(player)
    await session.commit()


async def join_lobby(
    session: AsyncSession,
    game_id: UUID,
    user_id: UUID,
) -> GamePlayer:
    game = await session.scalar(select(Game).where(Game.id == game_id).with_for_update())

    if game is None:
        raise GameNotFoundError

    if game.status != GameStatus.WAITING:
        raise GameAlreadyStartedError

    existing_player = await session.scalar(
        select(GamePlayer).where(
            GamePlayer.game_id == game.id,
            GamePlayer.user_id == user_id,
        )
    )

    if existing_player is not None:
        raise PlayerAlreadyJoinedError

    player_count = await session.scalar(
        select(func.count()).select_from(GamePlayer).where(GamePlayer.game_id == game.id)
    )

    if player_count >= game.max_players:
        raise GameFullError

    player = GamePlayer(
        game_id=game.id,
        user_id=user_id,
    )
    session.add(player)

    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise PlayerAlreadyJoinedError from error

    await session.refresh(player)

    return player


async def get_waiting_games(
    session: AsyncSession,
) -> list[tuple[Game, int]]:
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

    return [(game, current_players) for game, current_players in result.all()]


async def create_private_game(
    session: AsyncSession,
    owner_id: UUID,
    min_players: int,
    max_players: int,
) -> Game:
    game = Game(
        game_type=GameAccess.PRIVATE,
        min_players=min_players,
        max_players=max_players,
        owner_id=owner_id,
    )
    session.add(game)

    await session.flush()

    creator = GamePlayer(
        game_id=game.id,
        user_id=owner_id,
    )
    session.add(creator)

    await session.commit()
    await session.refresh(game)

    return game
