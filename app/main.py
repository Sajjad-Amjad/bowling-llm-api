# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from app.game import Game
from app.player import Player
from app.storage import Storage
from typing import Dict
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI, OpenAIError


load_dotenv()  

app = FastAPI()

# In-memory storage for games and players
games: Dict[str, Game] = {}
players: Dict[str, Player] = {}

# Ensure storage files are in the 'app' directory
BASE_DIR = os.path.dirname(__file__)
PLAYER_STORAGE_FILE = os.path.join(BASE_DIR, 'players.json')
GAME_STORAGE_FILE = os.path.join(BASE_DIR, 'games.json')

# Storage instances
player_storage = Storage(PLAYER_STORAGE_FILE)
game_storage = Storage(GAME_STORAGE_FILE)

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Load existing players from storage
player_data = player_storage.load_data()
for player_id, data in player_data.items():
    players[player_id] = Player.from_dict(data)

# Load existing games from storage
game_data = game_storage.load_data()
for game_id, data in game_data.items():
    games[game_id] = Game.from_dict(data)

class Roll(BaseModel):
    pins: int

class PlayerCreate(BaseModel):
    name: str

@app.post("/players")
def create_player(player: PlayerCreate):
    player_id = str(uuid4())
    new_player = Player(player_id, player.name)
    players[player_id] = new_player
    player_storage.save_data({pid: p.to_dict() for pid, p in players.items()})
    return {"player_id": player_id}

@app.get("/players/{player_id}/statistics")
def get_player_statistics(player_id: str):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    stats = players[player_id].get_statistics()
    return stats

@app.post("/players/{player_id}/games")
def create_game(player_id: str):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    game_id = str(uuid4())
    new_game = Game()
    games[game_id] = new_game
    game_storage.save_data({gid: g.to_dict() for gid, g in games.items()})
    players[player_id].add_game({"game_id": game_id, "score": 0}, game_id)
    player_storage.save_data({pid: p.to_dict() for pid, p in players.items()})
    return {"game_id": game_id}

@app.post("/games/{game_id}/rolls")
def record_roll(game_id: str, roll: Roll):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    game = games[game_id]
    try:
        game.roll(roll.pins)
        game_storage.save_data({gid: g.to_dict() for gid, g in games.items()})

        if game.is_game_over():
            associated_player_id = next((pid for pid, p in players.items() if game_id in p.game_ids), None)
            if associated_player_id:
                final_score = game.score()
                for game_summary in players[associated_player_id].games:
                    if game_summary["game_id"] == game_id:
                        game_summary["score"] = final_score
                        break
                player_storage.save_data({pid: p.to_dict() for pid, p in players.items()})

            del games[game_id]
            game_storage.save_data({gid: g.to_dict() for gid, g in games.items()})

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Roll recorded", "pins": roll.pins}

@app.get("/games/{game_id}/score")
def get_score(game_id: str):
    if game_id in games:
        return {"score": games[game_id].score()}

    for player in players.values():
        for game_summary in player.games:
            if game_summary["game_id"] == game_id:
                return {"score": game_summary["score"]}

    raise HTTPException(status_code=404, detail="Game not found")

@app.get("/games/{game_id}/summary")
def get_summary(game_id: str):
    # Search for the game in player records (as it might be completed)
    for player in players.values():
        for game_summary in player.games:
            if game_summary["game_id"] == game_id:
                # Fetch the necessary data: rolls, score, and player name
                rolls = game_summary.get("rolls", [])
                score = game_summary.get("score", 0)
                player_name = player.name

                # Check if the game is completed
                is_game_over = len(rolls) >= 12 or sum(rolls[:2]) >= 10

                # Generate the prompt for OpenAI API
                prompt = generate_prompt(player_name, rolls, score, is_game_over)

                try:
                    # Call OpenAI API to generate the summary
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a helpful scorer that summarizes bowling games. Please talk like real scorer."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=300,
                        temperature=0.6
                    )

                    # Extract the summary from the response
                    summary = response.choices[0].message.content.strip()
                    return {"summary": summary}  # Return the generated summary

                except OpenAIError as e:
                    # Handle OpenAI API errors gracefully
                    raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

    # If the game is not found, return a 404 error
    raise HTTPException(status_code=404, detail="Game not found or summary unavailable")

def generate_prompt(player_name, rolls, score, is_game_over):
    status = "The game is still ongoing." if not is_game_over else "The game is now completed."
    
    prompt = (
        f"Provide a detailed summary of a bowling game for the player '{player_name}'. "
        f"The following are the rolls: {rolls}. The current score is {score}. "
        f"{status} Mention any strikes, spares, or interesting patterns. "
        f"Summarize the gameplay and highlight the player’s performance."
    )
    return prompt