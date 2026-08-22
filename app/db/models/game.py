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
from app.game.enum import GameStatus


class Game(Base):
    __tablename__ = "games"

    __table_args__ = (
        CheckConstraint(
            "max_players BETWEEN 3 AND 20",
            name="max_players_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus, name="game_status"))
    max_players: Mapped[int] = mapped_column(SMALLINT)
    current_round_number: Mapped[int] = mapped_column(server_default=text("0"))
    winner_player_id: Mapped[UUID | None] = mapped_column(ForeignKey("game_players.id", use_alter=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
