from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, UniqueConstraint, func, text, false
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base
from app.game.enum import PlayerStatus


class GamePlayer(Base):
    __tablename__ = "game_players"

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "user_id",
            name="uq_game_players_game_user",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[PlayerStatus] = mapped_column(
        Enum(PlayerStatus, name="player_status"), server_default=text("'ACTIVE'")
    )
    is_ready: Mapped[bool] = mapped_column(server_default=false())
    eliminated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    joined_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
