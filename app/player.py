# app/player.py

from typing import List, Dict

class Player:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.games: List[Dict] = []  # List of game summaries
        self.game_ids: List[str] = []  # List of associated game IDs

    def add_game(self, game_summary: Dict, game_id: str):
        self.games.append(game_summary)
        self.game_ids.append(game_id)

    def get_statistics(self):
        total_games = len(self.games)
        if total_games == 0:
            return {
                "total_games": 0,
                "average_score": 0,
                "highest_score": 0
            }
        total_score = sum(game['score'] for game in self.games)
        highest_score = max(game['score'] for game in self.games)
        average_score = total_score / total_games
        return {
            "total_games": total_games,
            "average_score": average_score,
            "highest_score": highest_score
        }

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "name": self.name,
            "games": self.games,
            "game_ids": self.game_ids
        }

    @staticmethod
    def from_dict(data: Dict):
        player = Player(data['player_id'], data['name'])
        player.games = data.get('games', [])
        player.game_ids = data.get('game_ids', [])
        return player
