from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import random
import sys
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
import json
import ast

def parse_live_odds(html_file='baseball.html', driver=None):
    if driver:
        content = driver.page_source
    else:
        with open(html_file, 'r', encoding='utf-8') as file:
            content = file.read()

    soup = BeautifulSoup(content, 'html.parser')
    team_odds = {}

    # Find all buttons with aria-label containing "Odds"
    buttons_with_odds = soup.find_all('div', {'role': 'button', 'aria-label': re.compile(r'.*Odds.*', re.IGNORECASE)})

    for button in buttons_with_odds:
        aria_label = button.get('aria-label', '')

        # Extract odds
        odds_match = re.search(r'([+-]\d+)\s*Odds', aria_label)
        if not odds_match:
            continue

        odds = odds_match.group(1)

        # Extract team name - look for pattern "Moneyline, TEAM NAME, odds Odds"
        team_match = re.search(r'Moneyline,\s*([^,]+),\s*[+-]\d+\s*Odds', aria_label)
        if team_match:
            team_name = team_match.group(1).strip()
            team_odds[team_name] = odds

    return team_odds


def get_driver_fanduel_live_odds_page(sport: str = "Baseball", driver=None):
    # Create undetected Chrome driver instance
    driver = uc.Chrome()

    # Navigate to the target URL
    driver.get("https://sportsbook.fanduel.com/")
    time.sleep(1 + random.random())

    try:
        wait = WebDriverWait(driver, 10)
        live_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Live now']")))
        live_now.click()
    except Exception as e:
        print(f"Error clicking Live now: {e}")

    try:
        wait = WebDriverWait(driver, 10)
        baseball = wait.until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div[1]/div[2]/div//span[text()='{sport}']")))
        baseball.click()
    except Exception as e:
        print(f"Error clicking {sport}: {e}")

    return driver


def get_driver_fanduel_live_odds_page_existing_chrome(sport: str = "Baseball", use_existing_chrome=True):
    if use_existing_chrome:
        # Start Chrome with remote debugging (run this in PowerShell first)
        # chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_debug"

        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_options)
    else:
        # Fallback to undetected_chromedriver
        driver = uc.Chrome()

    # Navigate to the target URL
    # NAVIGATE HERE YOURRSELF VIA GOOGLE TO AVOID DETECTION
    # driver.get("https://sportsbook.fanduel.com/")
    # time.sleep(2 + random.random())

    # try:
    #     wait = WebDriverWait(driver, 10)
    #     live_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Live now']")))
    #     live_now.click()
    # except Exception as e:
    #     print(f"Error clicking Live now: {e}")

    # try:
    #     wait = WebDriverWait(driver, 10)
    #     baseball = wait.until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[1]/div/div/div/div[1]/main/div/div[1]/div/div/div[1]/div[2]/div//span[text()='{sport}']")))
    #     baseball.click()
    # except Exception as e:
    #     print(f"Error clicking {sport}: {e}")

    return driver

def authenticate_polymarket():
    try:
        sys.path.append(os.path.abspath(r"C:\Users\Site Oracle\polymarket_sniper\Production"))
        import polymarket_functions
        client = polymarket_functions.authenticate()
        return client
    except Exception as e:
        print(f"Error authenticating with Polymarket: {e}")
        return None

def load_markets_data(csv_path=r'C:\Users\Site Oracle\polymarket_sniper\Data\markets.csv'):
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading markets data: {e}")
        return None

def search_polymarket_team_markets(team_name, markets_df=None, csv_path=None):
    if markets_df is None:
        if csv_path is None:
            csv_path = r'C:\Users\Site Oracle\polymarket_sniper\Data\markets.csv'
        markets_df = load_markets_data(csv_path)

    if markets_df is None:
        return None

    try:
        sys.path.append(os.path.abspath(r"C:\Users\Site Oracle\polymarket_sniper\Production"))
        import polymarket_functions
        filtered_df = polymarket_functions.search_markets(markets_df, description_substring=team_name).reset_index()
        return filtered_df
    except Exception as e:
        print(f"Error searching markets for {team_name}: {e}")
        return None

def get_current_date_markets(markets_df, date_format='%B %d'):
    try:
        current_date = datetime.now().strftime(date_format)
        filtered_markets = markets_df[markets_df['description'].str.contains(current_date, na=False)]
        return filtered_markets, current_date
    except Exception as e:
        print(f"Error filtering markets by current date: {e}")
        return None, None

def parse_tokens_string(tokens_string):
    try:
        if isinstance(tokens_string, str):
            tokens_data = ast.literal_eval(tokens_string)
        else:
            tokens_data = tokens_string

        if isinstance(tokens_data, list):
            return tokens_data
        else:
            return [tokens_data]
    except (ValueError, SyntaxError) as e:
        try:
            tokens_data = json.loads(tokens_string)
            return tokens_data if isinstance(tokens_data, list) else [tokens_data]
        except json.JSONDecodeError:
            print(f"Error parsing tokens string: {e}")
            return None

def extract_token_details(tokens_data):
    if not tokens_data:
        return None

    token_details = []
    for token in tokens_data:
        token_info = {
            'token_id': token.get('token_id'),
            'outcome': token.get('outcome'),
            'price': token.get('price'),
            'winner': token.get('winner', False)
        }
        token_details.append(token_info)

    return token_details

def get_team_token_from_tokens(tokens_data, team_name):
    if not tokens_data:
        return None

    for token in tokens_data:
        if token.get('outcome', '').lower() == team_name.lower():
            return token

    for token in tokens_data:
        if team_name.lower() in token.get('outcome', '').lower():
            return token

    return None

def extract_market_tokens(markets_df):
    try:
        if markets_df.empty:
            return None
        tokens_string = markets_df['tokens'].iloc[0]
        parsed_tokens = parse_tokens_string(tokens_string)
        if parsed_tokens:
            return extract_token_details(parsed_tokens)
        return None
    except Exception as e:
        print(f"Error extracting tokens: {e}")
        return None

def get_polymarket_team_odds_today(team_name, csv_path=None):
    markets_df = load_markets_data(csv_path) if csv_path else load_markets_data()
    if markets_df is None:
        return None

    team_markets = search_polymarket_team_markets(team_name, markets_df)
    if team_markets is None or team_markets.empty:
        return None

    today_markets, current_date = get_current_date_markets(team_markets)
    if today_markets is None or today_markets.empty:
        return None

    return today_markets
    # all_tokens = extract_market_tokens(today_markets)
    # team_token = get_team_token_from_tokens(all_tokens, team_name) if all_tokens else None

    # return {
    #     'team': team_name,
    #     'date': current_date,
    #     'all_tokens': all_tokens,
    #     'team_token': team_token,
    #     'raw_string':  today_markets['tokens'].iloc[0],
    #     'markets_count': len(today_markets)
    # }
