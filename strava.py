from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def get_webdriver():
    user_agent = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    )
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(options=options)
    return driver


def login_to_strava(driver, username, password):
    driver.get('https://www.strava.com/login')
    time.sleep(2)

    email_field = driver.find_element(By.ID, 'email')
    password_field = driver.find_element(By.ID, 'password')

    email_field.send_keys(username)
    password_field.send_keys(password)

    password_field.send_keys(Keys.RETURN)
    time.sleep(5)


# Inspired from https://github.com/mbsmebye/StravaScraper
def get_last_weeks_leaderboard(username, password):
    driver = get_webdriver()
    login_to_strava(driver, username, password)

    driver.get('https://www.strava.com/clubs/526085')
    time.sleep(5)

    driver.find_element(By.XPATH, '//*[@class="button last-week"]').click()
    time.sleep(2)

    table = driver.find_element(By.XPATH, '//*[@class="dense striped sortable"]')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    leaderboard = []
    duplicates = []
    rows.pop(0)  # Skip the header row
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        athlete_name = cells[1].text.strip()
        athlete_url = cells[1].find_element(By.TAG_NAME, 'a').get_attribute('href')

        # Check for duplicates
        for athlete in leaderboard:
            if athlete_name == athlete["athlete_name"]:
                duplicates.append(athlete_name)

        # Add athlete to leaderboard list
        leaderboard.append({
            "rank": int(cells[0].text),
            "athlete_id": athlete_url.split('/')[-1],
            "athlete_name": athlete_name,
            "total_distance": cells[2].text,
            "number_of_runs": int(cells[3].text),
            "longest_run": cells[4].text,
            "avg_pace": cells[5].text,
            "total_elevation_gain": cells[6].text
        })
    return update_duplicate_athlete_names(leaderboard, duplicates)


def update_duplicate_athlete_names(athletes, duplicates):
    if len(duplicates) == 0:
        return athletes

    for duplicate_name in duplicates:
        for athlete in athletes:
            if athlete["athlete_name"] == duplicate_name:
                athlete["athlete_name"] = get_full_athlete_name(athlete["athlete_id"])
    return athletes


def get_full_athlete_name(athlete_id):
    driver = get_webdriver()
    driver.get(f'https://www.strava.com/athletes/{athlete_id}')
    time.sleep(2)
    return driver.title.split('|')[0].strip()
