# tests/test_main.py

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import os
import json


# Paths to the JSON storage files
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PLAYER_STORAGE_FILE = os.path.join(BASE_DIR, 'app', 'players.json')
GAME_STORAGE_FILE = os.path.join(BASE_DIR, 'app', 'games.json')

# Fixture to reset both players.json and games.json before each test to ensure test isolation
@pytest.fixture(autouse=True)
def reset_storage():
    # Reset players.json
    if os.path.exists(PLAYER_STORAGE_FILE):
        with open(PLAYER_STORAGE_FILE, 'w') as f:
            json.dump({}, f)
    else:
        os.makedirs(os.path.dirname(PLAYER_STORAGE_FILE), exist_ok=True)
        with open(PLAYER_STORAGE_FILE, 'w') as f:
            json.dump({}, f)
    
    # Reset games.json
    if os.path.exists(GAME_STORAGE_FILE):
        with open(GAME_STORAGE_FILE, 'w') as f:
            json.dump({}, f)
    else:
        os.makedirs(os.path.dirname(GAME_STORAGE_FILE), exist_ok=True)
        with open(GAME_STORAGE_FILE, 'w') as f:
            json.dump({}, f)
    
    # Reset in-memory players and games
    app.dependency_overrides = {}
    app.state.players = {}
    app.state.games = {}
    
    yield
    
    # Clean up after the test
    if os.path.exists(PLAYER_STORAGE_FILE):
        os.remove(PLAYER_STORAGE_FILE)
    if os.path.exists(GAME_STORAGE_FILE):
        os.remove(GAME_STORAGE_FILE)
    app.state.players = {}
    app.state.games = {}

# Fixture for AsyncClient using ASGITransport to avoid DeprecationWarning
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

# Fixture to create a new player and provide the player_id
@pytest.fixture
async def player_id(client):
    response = await client.post("/players", json={"name": "Alice"})
    assert response.status_code == 200
    return response.json()["player_id"]

# Fixture to create a new game for a player and provide the game_id
@pytest.fixture
async def game_id(client, player_id):
    response = await client.post(f"/players/{player_id}/games")
    assert response.status_code == 200
    return response.json()["game_id"]

@pytest.mark.anyio
async def test_create_player(client):
    response = await client.post("/players", json={"name": "Bob"})
    assert response.status_code == 200
    assert "player_id" in response.json()
    player_id = response.json()["player_id"]
    assert isinstance(player_id, str)

@pytest.mark.anyio
async def test_get_player_statistics_empty(client, player_id):
    response = await client.get(f"/players/{player_id}/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_games"] == 0
    assert stats["average_score"] == 0
    assert stats["highest_score"] == 0

@pytest.mark.anyio
async def test_create_game_for_player(client, player_id):
    response = await client.post(f"/players/{player_id}/games")
    assert response.status_code == 200
    assert "game_id" in response.json()
    game_id = response.json()["game_id"]
    assert isinstance(game_id, str)

@pytest.mark.anyio
async def test_record_roll_and_score(client, game_id):
    # Record a roll of 5 pins
    response = await client.post(f"/games/{game_id}/rolls", json={"pins": 5})
    assert response.status_code == 200
    assert response.json()["pins"] == 5

    # Get current score
    response = await client.get(f"/games/{game_id}/score")
    assert response.status_code == 200
    assert "score" in response.json()
    assert response.json()["score"] == 5  # Score after one roll of 5 pins

@pytest.mark.anyio
async def test_record_multiple_rolls_and_score(client, game_id):
    # Record a series of rolls: 5, 5 (spare), 3, then gutter balls
    rolls = [5, 5, 3] + [0] * 17
    expected_score = 16  # 5 + 5 + 3 + 3 + (0 * 17)

    for pins in rolls:
        response = await client.post(f"/games/{game_id}/rolls", json={"pins": pins})
        assert response.status_code == 200

    # Get final score
    response = await client.get(f"/games/{game_id}/score")
    assert response.status_code == 200
    assert response.json()["score"] == expected_score


@pytest.mark.anyio
async def test_invalid_player_id(client):
    response = await client.get("/players/invalid_player_id/statistics")
    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"

@pytest.mark.anyio
async def test_invalid_game_id(client):
    response = await client.get("/games/invalid_game_id/score")
    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"

@pytest.mark.anyio
async def test_invalid_pins_negative(client, game_id):
    response = await client.post(f"/games/{game_id}/rolls", json={"pins": -1})
    assert response.status_code == 400
    assert "Invalid number of pins" in response.json()["detail"]

@pytest.mark.anyio
async def test_invalid_pins_more_than_ten(client, game_id):
    response = await client.post(f"/games/{game_id}/rolls", json={"pins": 11})
    assert response.status_code == 400
    assert "Invalid number of pins" in response.json()["detail"]

@pytest.mark.anyio
async def test_frame_pins_exceed_ten(client, game_id):
    # First roll of 7 pins
    response = await client.post(f"/games/{game_id}/rolls", json={"pins": 7})
    assert response.status_code == 200

    # Second roll of 4 pins (total exceeds 10)
    response = await client.post(f"/games/{game_id}/rolls", json={"pins": 4})
    assert response.status_code == 400
    assert "Total pins in a frame cannot exceed 10" in response.json()["detail"]

@pytest.mark.anyio
async def test_game_over_after_perfect_game(client, player_id):
    # Create a new game for the player
    response = await client.post(f"/players/{player_id}/games")
    assert response.status_code == 200
    game_id_over = response.json()["game_id"]

    # Roll a perfect game (12 strikes)
    for _ in range(12):
        response = await client.post(f"/games/{game_id_over}/rolls", json={"pins": 10})
        assert response.status_code == 200

    # Attempt to roll after game is over
    response = await client.post(f"/games/{game_id_over}/rolls", json={"pins": 10})
    assert response.status_code == 404  # Since the game is removed after completion
    assert response.json()["detail"] == "Game not found"

@pytest.mark.anyio
async def test_player_statistics_after_games(client, player_id):
    # Create two games for the player
    game_ids = []
    for _ in range(2):
        response = await client.post(f"/players/{player_id}/games")
        assert response.status_code == 200
        game_ids.append(response.json()["game_id"])

    # First game: all ones
    for _ in range(20):
        response = await client.post(f"/games/{game_ids[0]}/rolls", json={"pins": 1})
        assert response.status_code == 200

    # Second game: perfect game
    for _ in range(12):
        response = await client.post(f"/games/{game_ids[1]}/rolls", json={"pins": 10})
        assert response.status_code == 200

    # Get player statistics
    response = await client.get(f"/players/{player_id}/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_games"] == 2
    assert stats["average_score"] == (20 + 300) / 2  # 160
    assert stats["highest_score"] == 300

@pytest.mark.anyio
async def test_create_game_for_invalid_player(client):
    response = await client.post("/players/invalid_player_id/games")
    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"

@pytest.mark.anyio
async def test_record_roll_for_invalid_game(client, player_id):
    response = await client.post(f"/games/invalid_game_id/rolls", json={"pins": 5})
    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"
