import pytest

from app.schemas.game import GameCreate


def test_game_create_uses_default_capacity() -> None:
    game = GameCreate()

    assert game.min_players == 5
    assert game.max_players == 10


@pytest.mark.parametrize(
    ("min_players", "max_players"),
    [
        (3, 3),
        (3, 20),
        (5, 10),
        (20, 20),
    ],
)
def test_game_create_accepts_valid_capacity(
    min_players: int,
    max_players: int,
) -> None:
    game = GameCreate(
        min_players=min_players,
        max_players=max_players,
    )

    assert game.min_players == min_players
    assert game.max_players == max_players
