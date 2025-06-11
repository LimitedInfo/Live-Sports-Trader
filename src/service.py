import json
from typing import List
import pandas as pd
from domain import Game, Team, Odds


def probability_to_american_odds(probability: float) -> str:
    """Convert probability (0-1) to American odds format"""
    if probability >= 0.5:
        # Negative odds for favorites
        american_odds = int(-100 * probability / (1 - probability))
    else:
        # Positive odds for underdogs
        american_odds = int((100 / probability) - 100)

    return str(american_odds) if american_odds < 0 else f"+{american_odds}"


def parse_betting_market_response(response_data: str, game_name: str = None) -> Game:
    json_data = response_data.replace("'", '"').replace('False', 'false').replace('True', 'true')
    data = json.loads(json_data)

    teams = []
    team_names = []

    for market_data in data:
        team_name = market_data['outcome']
        team_names.append(team_name)
        price = market_data['price']


        american_odds = probability_to_american_odds(price)
        odds = Odds(american_odds=american_odds)

        team = Team(team_name, market_data['token_id'])
        # team.prediction_market_odds = odds

        teams.append(team)

    if not game_name:
        game_name = f"{' vs '.join(team_names)}"

    game = Game(game_name)
    game.teams = teams

    return game


def parse_polymarket_dataframe(df: pd.DataFrame) -> List[Game]:
    """
    Parse a dataframe from polymarket API response and create Game objects with Team objects.

    Args:
        df: DataFrame with columns 'question', 'tokens', and other game data

    Returns:
        List of Game objects with populated Team objects
    """
    games = []

    for _, row in df.iterrows():
        # Extract game name from question (e.g., "Cubs vs. Phillies")
        game_name = row['question']
        game = Game(game_name)

        # Parse team names from the question (assumes format "Team1 vs. Team2")
        team_names = [name.strip() for name in game_name.split(' vs. ')]

        # Extract tokens data - handle both string and list formats
        tokens_data = row['tokens']
        if isinstance(tokens_data, str):
            # More robust parsing for Python-like string representation
            try:
                # Replace Python booleans and None with JSON equivalents
                json_str = (tokens_data
                           .replace("'", '"')
                           .replace('False', 'false')
                           .replace('True', 'true')
                           .replace('None', 'null'))
                tokens_data = json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, try using ast.literal_eval as fallback
                import ast
                tokens_data = ast.literal_eval(tokens_data)

        # Create Team objects
        for i, token_data in enumerate(tokens_data):
            if i < len(team_names):
                team_name = team_names[i]
                token_id = token_data['token_id']

                team = Team(name=team_name, token_id=token_id)
                game.teams.append(team)

        games.append(game)

    return games


if __name__ == "__main__":
    # Example usage with the provided response data
    response_data = "[{'token_id': '48267065151258629836601031314509219891007393953617086960717049610776571996215', 'outcome': 'Marlins', 'price': 0.425, 'winner': False}, {'token_id': '43514467218402237458835959250190433952215998292317344823351640012659428174695', 'outcome': 'Pirates', 'price': 0.575, 'winner': False}]"

    print("Parsing betting market response...")
    game = parse_betting_market_response(response_data, "Marlins vs Pirates")

    print(f"Game: {game.name}")
    print(f"Number of teams: {len(game.teams)}")
    for team in game.teams:
        print(f"Team: {team.name}")
        print(f"  Number of prediction market odds: {len(team.prediction_market_odds)}")
        for odds in team.prediction_market_odds:
            print(f"  Odds: {odds}")
            print(f"    American odds: {odds.american_odds}")
            print(f"    Probability: {odds.probability:.3f}")
