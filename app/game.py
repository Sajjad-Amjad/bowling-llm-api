from typing import List, Dict

class Game:
    def __init__(self):
        self.rolls = []

    def roll(self, pins: int):
        if pins < 0 or pins > 10:
            raise ValueError("Invalid number of pins")
        if self.is_game_over():
            raise ValueError("Game is already over")
        if not self.is_valid_roll(pins):
            raise ValueError("Total pins in a frame cannot exceed 10 (except in the 10th frame)")
        self.rolls.append(pins)

    def is_game_over(self):
        frames = 0
        roll_index = 0

        while frames < 9 and roll_index < len(self.rolls):
            if self.rolls[roll_index] == 10:
                roll_index += 1  # Strike
            else:
                roll_index += 2  # Spare or open frame
            frames += 1

        if frames == 9:
            return self._tenth_frame_over(roll_index)

        return False

    def _tenth_frame_over(self, roll_index):
        remaining_rolls = self.rolls[roll_index:]
        if len(remaining_rolls) < 2:
            return False

        if remaining_rolls[0] == 10 or sum(remaining_rolls[:2]) == 10:
            return len(remaining_rolls) == 3

        return len(remaining_rolls) == 2

    def is_valid_roll(self, pins: int):
        total_rolls = len(self.rolls)

        # Handle first 9 frames
        if total_rolls < 18:
            # If it's the second roll of the frame (not a strike)
            if total_rolls % 2 == 1 and self.rolls[-1] != 10:
                if self.rolls[-1] + pins > 10:
                    raise ValueError("Total pins in a frame cannot exceed 10")

        # Handle the 10th frame logic
        elif total_rolls >= 18:
            tenth_frame_rolls = self.rolls[18:]

            if len(tenth_frame_rolls) == 1 and tenth_frame_rolls[0] != 10:
                if tenth_frame_rolls[0] + pins > 10:
                    raise ValueError("Total pins in the 10th frame cannot exceed 10")
            elif len(tenth_frame_rolls) == 2:
                # Ensure valid third roll only after a strike or spare
                if sum(tenth_frame_rolls[:2]) < 10 and pins > 0:
                    raise ValueError("Third roll only allowed after a strike or spare")

        return True


    def score(self):
        score = 0
        roll_index = 0

        for frame in range(10):
            if roll_index >= len(self.rolls):
                break

            if self.rolls[roll_index] == 10:
                score += 10 + self.strike_bonus(roll_index)
                roll_index += 1
            else:
                frame_score = self.rolls[roll_index]
                if roll_index + 1 < len(self.rolls):
                    frame_score += self.rolls[roll_index + 1]
                if frame_score == 10:
                    score += 10 + self.spare_bonus(roll_index)
                else:
                    score += frame_score
                roll_index += 2

        return score

    def strike_bonus(self, roll_index):
        bonus = 0
        if roll_index + 1 < len(self.rolls):
            bonus += self.rolls[roll_index + 1]
        if roll_index + 2 < len(self.rolls):
            bonus += self.rolls[roll_index + 2]
        return bonus

    def spare_bonus(self, roll_index):
        if roll_index + 2 < len(self.rolls):
            return self.rolls[roll_index + 2]
        return 0

    def to_dict(self):
        return {"rolls": self.rolls}

    @staticmethod
    def from_dict(data: Dict):
        game = Game()
        game.rolls = data.get("rolls", [])
        return game

    def get_rolls(self):
        return self.rolls
