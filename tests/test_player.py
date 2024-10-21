# tests/test_player.py

import pytest
from app.player import Player
from app.game import Game

def test_player_creation():
    player = Player("player1", "Alice")
    assert player.player_id == "player1"
    assert player.name == "Alice"
    assert player.games == []
    assert player.game_ids == []  # Ensure game_ids is initialized correctly

def test_add_game_to_player():
    player = Player("player1", "Alice")
    game_summary = {"game_id": "game1", "score": 150}
    game_id = "game1"  # Extract game_id from game_summary
    player.add_game(game_summary, game_id)  # Pass both arguments
    assert len(player.games) == 1
    assert player.games[0]["game_id"] == "game1"
    assert player.games[0]["score"] == 150
    assert len(player.game_ids) == 1
    assert player.game_ids[0] == "game1"

def test_player_statistics():
    player = Player("player1", "Alice")
    game_summaries = [
        {"game_id": "game1", "score": 150},
        {"game_id": "game2", "score": 200},
        {"game_id": "game3", "score": 100},
    ]
    for summary in game_summaries:
        game_id = summary["game_id"]  # Extract game_id from each summary
        player.add_game(summary, game_id)  # Pass both arguments
    stats = player.get_statistics()
    assert stats["total_games"] == 3
    assert stats["average_score"] == 150  # (150 + 200 + 100) / 3 = 150
    assert stats["highest_score"] == 200
