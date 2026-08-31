from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.game.enum import GameAccess, GameStatus


class GameCreate(BaseModel):
    min_players: int = Field(ge=3, le=20, default=5)
    max_players: int = Field(ge=3, le=20, default=10)

    @model_validator(mode="after")
    def validate_player_limits(self) -> Self:
        if self.min_players > self.max_players:
            raise ValueError("min_players cannot be greater than max_players")

        return self


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: GameStatus
    game_type: GameAccess
    min_players: int
    max_players: int
    current_round_number: int
    owner_id: UUID | None
    winner_player_id: UUID | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class GameListResponse(GameResponse):
    current_players: int
