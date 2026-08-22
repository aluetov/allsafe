from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Enum,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base
from app.game.enum import MessageType


class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        CheckConstraint(
            """
            (message_type = 'USER' AND sender_player_id IS NOT NULL)
            OR
            (message_type = 'SYSTEM' AND sender_player_id IS NULL)
            """,
            name="type_sender",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"))
    sender_player_id: Mapped[UUID | None] = mapped_column(ForeignKey("game_players.id"))
    message_type: Mapped[MessageType] = mapped_column(Enum(MessageType, name="message_type"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
