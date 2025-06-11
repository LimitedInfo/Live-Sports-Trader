import json
from typing import List
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
    """
    Parse betting market response and create domain objects

    Args:
        response_data: JSON string containing betting market data
        game_name: Optional name for the game, will use team names if not provided

    Returns:
        Game object with populated teams and odds
    """
    # Handle Python literal format (convert to valid JSON)
    json_data = response_data.replace("'", '"').replace('False', 'false').replace('True', 'true')
    data = json.loads(json_data)

    teams = []
    team_names = []

    for market_data in data:
        team_name = market_data['outcome']
        team_names.append(team_name)
        price = market_data['price']

        # Convert probability to American odds
        american_odds = probability_to_american_odds(price)
        odds = Odds(american_odds)

        # Create team with prediction market odds
        team = Team(team_name)
        team.prediction_market_odds = [odds]
        team.true_odds = []  # Initialize empty true odds

        teams.append(team)

    # Create game name if not provided
    if not game_name:
        game_name = f"{' vs '.join(team_names)}"

    game = Game(game_name)
    game.teams = teams

    return game


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
