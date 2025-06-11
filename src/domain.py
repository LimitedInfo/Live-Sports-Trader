from typing import List


class Odds:
    def __init__(self, american_odds: str = None, probability: float = None):
        if american_odds is not None and probability is not None:
            raise ValueError("Cannot specify both american_odds and probability")
        if american_odds is None and probability is None:
            raise ValueError("Must specify either american_odds or probability")

        if american_odds is not None:
            self._american_odds = american_odds
            self._probability = None
        else:
            self._american_odds = None
            self._probability = probability

    @property
    def american_odds(self):
        if self._american_odds is not None:
            return self._american_odds

        prob = self._probability
        if prob >= 0.5:
            american_value = -int((prob / (1 - prob)) * 100)
        else:
            american_value = int(((1 - prob) / prob) * 100)

        return f"{american_value:+d}" if american_value > 0 else str(american_value)

    @property
    def probability(self):
        if self._probability is not None:
            return self._probability

        odds_str = self._american_odds.replace('+', '')
        odds_value = int(odds_str)

        if odds_value > 0:
            return 100 / (odds_value + 100)
        else:
            return -odds_value / (-odds_value + 100)

    def __str__(self):
        return f"{self.american_odds} - {self.probability:.4f}"


class Game:
    def __init__(self, name):
        self.name = name
        self.teams = []

    def get_vig_percentage(self, odds_type='true_odds'):
        if len(self.teams) != 2:
            return None

        team1_odds = getattr(self.teams[0], odds_type)
        team2_odds = getattr(self.teams[1], odds_type)

        if team1_odds is None or team2_odds is None:
            return None

        total_probability = team1_odds.probability + team2_odds.probability
        vig_percentage = (total_probability - 1.0) * 100
        return vig_percentage

    def get_no_vig_probabilities(self, odds_type='true_odds'):
        if len(self.teams) != 2:
            return None

        team1_odds = getattr(self.teams[0], odds_type)
        team2_odds = getattr(self.teams[1], odds_type)

        if team1_odds is None or team2_odds is None:
            return None

        team1_prob = team1_odds.probability
        team2_prob = team2_odds.probability
        total_probability = team1_prob + team2_prob
        print(f"total probability: {total_probability}")

        no_vig_team1_prob = team1_prob / total_probability
        print(f"no vig team1 prob: {no_vig_team1_prob}")
        no_vig_team2_prob = team2_prob / total_probability
        print(f"no vig team2 prob: {no_vig_team2_prob}")

        if no_vig_team1_prob + no_vig_team2_prob != 1:
            raise ValueError("Total no vig probability is not 1")

        return {
            'team1_probability': no_vig_team1_prob,
            'team2_probability': no_vig_team2_prob,
            'team1_name': self.teams[0].name,
            'team2_name': self.teams[1].name
        }

    def get_no_vig_odds(self, odds_type='true_odds'):
        no_vig_probs = self.get_no_vig_probabilities(odds_type)
        if no_vig_probs is None:
            return None

        team1_no_vig_odds = Odds(probability=no_vig_probs['team1_probability'])
        team2_no_vig_odds = Odds(probability=no_vig_probs['team2_probability'])

        return {
            'team1_odds': team1_no_vig_odds,
            'team2_odds': team2_no_vig_odds,
            'team1_name': no_vig_probs['team1_name'],
            'team2_name': no_vig_probs['team2_name']
        }

    def __str__(self):
        return f"Game: {self.name}"


class Team:
    def __init__(self, name, token_id):
            self.name: str = name
            self.token_id: str = token_id
            self.true_odds: Odds = None
            self.prediction_market_odds: Odds = None
            self.no_vig_true_odds: Odds = None
            self.no_vig_prediction_market_odds: Odds = None

    def get_limit_price_for_desired_expected_value(self, desired_expected_value: float):
        return self.no_vig_true_odds.probability / (1 + desired_expected_value)

    def get_difference_between_desired_expected_value_and_market_bid(self, desired_expected_value: float):
        desired_limit_price = self.get_limit_price_for_desired_expected_value(desired_expected_value)
        print(f"Desired limit price: {desired_limit_price}")
        print(f"Market bid: {self.prediction_market_odds.probability}")
        return desired_limit_price - self.prediction_market_odds.probability



    def get_odds_difference(self):
        if self.true_odds is None or self.prediction_market_odds is None:
            return None

        true_prob = self.true_odds.probability
        market_prob = self.prediction_market_odds.probability
        prob_difference = market_prob - true_prob

        if prob_difference > 0:
            signal = "SELL"
            description = "Market overvalues team"
        elif prob_difference < 0:
            signal = "BUY"
            description = "Market undervalues team"
        else:
            signal = "NEUTRAL"
            description = "Market fairly valued"

        return {
            "probability_difference": prob_difference,
            "signal": signal,
            "description": description,
            "true_probability": true_prob,
            "market_probability": market_prob
        }

    def __str__(self):
        return f"Team: {self.name}"
