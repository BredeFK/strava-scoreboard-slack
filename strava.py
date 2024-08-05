# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
import os.path
import time

import requests

TOKEN_FILE_NAME = 'tokens.txt'
BASE_URL = 'https://www.strava.com'


# http://www.strava.com/oauth/authorize?client_id=59898&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read
# https://developers.strava.com/docs/authentication/

def get_access_token():
    if os.path.exists(TOKEN_FILE_NAME):
        file = open(TOKEN_FILE_NAME, 'r')
        lines = file.readlines()
        expires_at = int(lines[0].strip())
        refresh_token = lines[1].strip()
        access_token = lines[2].strip()
        print(f'{expires_at}\n{refresh_token}\n{access_token}')
        time_now = int(time.time())
        if time_now >= expires_at:
            print('Accesstoken has expired')
        else:
            print('Accesstoken has not expired')
            return access_token
    else:
        strava_request = requests.post(url=f'{BASE_URL}/oauth/token',
                                       params={'client_id': '59898',
                                               'client_secret': '???',
                                               'code': '???',
                                               'grant_type': 'authorization_code'})

        # now:      1722861081
        # expires:  1722879581
        print(int(time.time()))
        if strava_request.status_code == 200:
            json = strava_request.json()
            file = open(TOKEN_FILE_NAME, 'w')
            file.write(str(json['expires_at']) + '\n')
            file.write(json['refresh_token'] + '\n')
            file.write(json['access_token'])
            file.close()
        else:
            print(f'Something went wrong: {strava_request.status_code}')
            error = strava_request.json()
            print(error)
        return '123'


access_token = get_access_token()
print(access_token)

# def get_webdriver():
#     user_agent = (
#         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
#     )
#     options = Options()
#     options.add_argument('--headless=new')
#     options.add_argument(f'user-agent={user_agent}')
#
#     driver = webdriver.Chrome(options=options)
#     return driver


# Inspired from https://github.com/mbsmebye/StravaScraper
# def get_last_weeks_leaderboard():
#     driver = get_webdriver()
#     driver.get('https://www.strava.com/clubs/526085')
#     driver.find_element(By.XPATH, '//*[@class="button last-week"]').click()
#
#     table = driver.find_element(By.XPATH, '//*[@class="dense striped sortable"]')
#     rows = table.find_elements(By.TAG_NAME, 'tr')
#
#     leaderboard = []
#     duplicates = []
#     rows.pop(0)  # Skip the header row
#     for row in rows:
#         cells = row.find_elements(By.TAG_NAME, 'td')
#         athlete_name = cells[1].text.strip()
#         athlete_url = cells[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
#
#         # Check for duplicates
#         for athlete in leaderboard:
#             if athlete_name == athlete["athlete_name"]:
#                 duplicates.append(athlete_name)
#
#         # Add athlete to leaderboard list
#         leaderboard.append({
#             "rank": int(cells[0].text),
#             "athlete_id": athlete_url.split('/')[-1],
#             "athlete_name": athlete_name,
#             "total_distance": cells[2].text,
#             "number_of_runs": int(cells[3].text),
#             "longest_run": cells[4].text,
#             "avg_pace": cells[5].text,
#             "total_elevation_gain": cells[6].text
#         })
#     return update_duplicate_athlete_names(leaderboard, duplicates)
#
#
# def update_duplicate_athlete_names(athletes, duplicates):
#     if len(duplicates) == 0:
#         return athletes
#
#     for duplicate_name in duplicates:
#         for athlete in athletes:
#             if athlete["athlete_name"] == duplicate_name:
#                 athlete["athlete_name"] = get_full_athlete_name(athlete["athlete_id"])
#     return athletes
#
#
# def get_full_athlete_name(athlete_id):
#     driver = get_webdriver()
#     driver.get(f'https://www.strava.com/athletes/{athlete_id}')
#     return driver.title.split('|')[0].strip()
