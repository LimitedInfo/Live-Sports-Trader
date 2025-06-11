

from typing import List


class Odds:
    def __init__(self, american_odds: str):
        self.american_odds = american_odds

    @property
    def probability(self):
        odds_str = self.american_odds.replace('+', '')
        odds_value = int(odds_str)

        if odds_value > 0:
            return 100 / (odds_value + 100)
        else:
            return -odds_value / (-odds_value + 100)


    def __str__(self):
        return f"{self.american_odds} - {self.probability}"


class Game:
    def __init__(self, name):
        self.name = name
        self.teams = []

    def __str__(self):
        return f"Game: {self.name}"


class Team:
    def __init__(self, name):
            self.name = name
            self.true_odds = []
            self.prediction_market_odds = []

    def __str__(self):
        return f"Team: {self.name}"
