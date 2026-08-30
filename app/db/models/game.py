from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    SMALLINT,
    TIMESTAMP,
    CheckConstraint,
    Enum,
    ForeignKey,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base
from app.game.enum import GameAccess, GameStatus


class Game(Base):
    __tablename__ = "games"

    __table_args__ = (
        CheckConstraint(
            "min_players BETWEEN 3 AND 20",
            name="min_players_range",
        ),
        CheckConstraint(
            "max_players BETWEEN 3 AND 20",
            name="max_players_range",
        ),
        CheckConstraint(
            "min_players <= max_players",
            name="min_players_not_greater_than_max",
        ),
        CheckConstraint(
            """
            (game_type = 'PUBLIC' AND owner_id IS NULL)
            OR
            (game_type = 'PRIVATE' AND owner_id IS NOT NULL)
            """,
            name="game_owner_matches_access",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus, name="game_status"), server_default=text("'WAITING'")
    )
    game_type: Mapped[GameAccess] = mapped_column(
        Enum(GameAccess, name="game_access"), server_default=text("'PUBLIC'")
    )
    min_players: Mapped[int] = mapped_column(SMALLINT, server_default=text("5"))
    max_players: Mapped[int] = mapped_column(SMALLINT, server_default=text("10"))
    current_round_number: Mapped[int] = mapped_column(server_default=text("0"))
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    winner_player_id: Mapped[UUID | None] = mapped_column(ForeignKey("game_players.id", use_alter=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
