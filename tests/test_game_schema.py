import pytest
from pydantic import ValidationError

from app.schemas.game import GameCreate


def test_game_create_uses_default_capacity() -> None:
    game = GameCreate()

    assert game.max_players == 5


@pytest.mark.parametrize("max_players", [3, 5, 20])
def test_game_create_accepts_valid_capacity(
    max_players: int,
) -> None:
    game = GameCreate(max_players=max_players)

    assert game.max_players == max_players


@pytest.mark.parametrize("max_players", [2, 21])
def test_game_create_rejects_invalid_capacity(
    max_players: int,
) -> None:
    with pytest.raises(ValidationError):
        GameCreate(max_players=max_players)
