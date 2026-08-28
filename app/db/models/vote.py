from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Vote(Base):
    __tablename__ = "votes"

    __table_args__ = (
        UniqueConstraint(
            "round_id",
            "voter_player_id",
            name="uq_votes_round_voter",
        ),
        CheckConstraint(
            "voter_player_id <> target_player_id",
            name="no_self_vote",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    round_id: Mapped[UUID] = mapped_column(ForeignKey("rounds.id"))
    voter_player_id: Mapped[UUID] = mapped_column(ForeignKey("game_players.id"))
    target_player_id: Mapped[UUID] = mapped_column(ForeignKey("game_players.id"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
