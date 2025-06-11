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
    driver.get("https://sportsbook.fanduel.com/")
    time.sleep(2 + random.random())

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
