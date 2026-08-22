from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, CheckConstraint, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base
from app.game.enum import RoundStatus


class Round(Base):
    __tablename__ = "rounds"

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "round_number",
            name="uq_rounds_game_round",
        ),
        CheckConstraint(
            "round_number > 0",
            name="number_positive",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"))
    round_number: Mapped[int]
    status: Mapped[RoundStatus] = mapped_column(Enum(RoundStatus, name="round_status"))
    eliminated_player_id: Mapped[UUID | None] = mapped_column(ForeignKey("game_players.id"))
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    voting_ends_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
