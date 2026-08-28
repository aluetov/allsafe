from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.game.enum import GameStatus


class GameCreate(BaseModel):
    max_players: int = Field(ge=3, le=20, default=5)


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: GameStatus
    max_players: int
    current_round_number: int
    winner_player_id: UUID | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class GameListResponse(GameResponse):
    current_players: int
