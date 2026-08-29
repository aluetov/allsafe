from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.game.enum import PlayerStatus


class GamePlayerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    game_id: UUID
    user_id: UUID
    status: PlayerStatus
    eliminated_at: datetime | None
    joined_at: datetime