import pytest
from app.game import Game

def test_initial_score_is_zero():
    game = Game()
    assert game.score() == 0

def test_single_roll():
    game = Game()
    game.roll(5)
    assert game.get_rolls() == [5]
    assert game.score() == 5

def test_invalid_rolls():
    game = Game()
    with pytest.raises(ValueError, match="Invalid number of pins"):
        game.roll(-1)
    with pytest.raises(ValueError, match="Invalid number of pins"):
        game.roll(11)

def test_roll_more_than_10_pins_in_frame():
    game = Game()
    game.roll(6)
    with pytest.raises(ValueError, match="Total pins in a frame cannot exceed 10"):
        game.roll(7)

def test_strike_bonus():
    game = Game()
    game.roll(10)  # Strike
    game.roll(3)
    game.roll(4)
    assert game.score() == 24  # 10 + (3 + 4) + 3 + 4

def test_spare_bonus():
    game = Game()
    game.roll(5)
    game.roll(5)  # Spare
    game.roll(3)
    assert game.score() == 16  # 10 + 3 + 3

def test_perfect_game():
    game = Game()
    for _ in range(12):
        game.roll(10)  # Perfect game
    assert game.score() == 300

def test_all_spares():
    game = Game()
    for _ in range(10):
        game.roll(5)
        game.roll(5)  # Spare in every frame
    game.roll(5)  # Extra roll
    assert game.score() == 150


def test_game_over():
    game = Game()
    for _ in range(20):
        game.roll(1)  # All rolls with 1 pin each

    with pytest.raises(ValueError, match="Game is already over"):
        game.roll(1)

def test_tenth_frame_extra_rolls():
    game = Game()
    for _ in range(18):
        game.roll(0)  # First 9 frames are gutter balls
    game.roll(10)  # Strike in the 10th frame
    game.roll(10)  # Extra roll 1
    game.roll(10)  # Extra roll 2
    assert game.score() == 30

def test_to_dict():
    game = Game()
    game.roll(10)
    game.roll(3)
    game.roll(7)
    game_dict = game.to_dict()
    assert game_dict == {"rolls": [10, 3, 7]}

def test_from_dict():
    data = {"rolls": [10, 3, 7]}
    game = Game.from_dict(data)
    assert game.get_rolls() == [10, 3, 7]
