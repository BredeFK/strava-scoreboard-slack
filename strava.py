import os.path
import time
from collections import defaultdict

import requests

TOKEN_FILE_NAME = 'tokens.txt'
BASE_URL = 'https://www.strava.com'
CLIENT_ID = ''
CLIENT_SECRET = ''
CLUB_ID = 0
CODE = ''

print(
    f'http://www.strava.com/oauth/authorize?client_id={CLUB_ID}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read')


# https://developers.strava.com/docs/authentication/


def get_access_token():
    if os.path.exists(TOKEN_FILE_NAME):
        file = open(TOKEN_FILE_NAME, 'r')
        lines = file.readlines()
        expires_at = int(lines[0].strip())
        refresh_token = lines[1].strip()
        access_token = lines[2].strip()
        time_now = int(time.time())
        if time_now >= expires_at:
            print('AccessToken has expired')
            refresh_token_request = requests.post(url=f'{BASE_URL}/api/v3/oauth/token',
                                                  params={'client_id': CLIENT_ID,
                                                          'client_secret': CLIENT_SECRET,
                                                          'grant_type': 'refresh_token',
                                                          'refresh_token': refresh_token})
            if refresh_token_request.status_code == 200:
                print('Got new token using refresh token')
                refresh_token_request_json = refresh_token_request.json()
                return update_token_file_and_return_access_token(refresh_token_request_json)
            else:
                error = refresh_token_request.json()
                print(f'Could not get new token using refresh token: [{refresh_token_request.status_code}] {error}')
                return None
        else:
            print('Stored accessToken is still valid')
            return access_token
    else:
        strava_request = requests.post(url=f'{BASE_URL}/api/v3/oauth/token',
                                       params={'client_id': CLIENT_ID,
                                               'client_secret': CLIENT_SECRET,
                                               'code': CODE,
                                               'grant_type': 'authorization_code'})

        if strava_request.status_code == 200:
            print('Fetched fresh accessToken')
            strava_request_json = strava_request.json()
            return update_token_file_and_return_access_token(strava_request_json)
        else:
            print(f'Something went wrong: {strava_request.status_code}')
            error = strava_request.json()
            print(error)
            return None


def update_token_file_and_return_access_token(json_body):
    token_file = open(TOKEN_FILE_NAME, 'w')
    access_token = json_body['access_token']
    token_file.write(str(json_body['expires_at']) + '\n')
    token_file.write(json_body['refresh_token'] + '\n')
    token_file.write(access_token)
    token_file.close()
    return access_token


def get_club_activities(bearer_token, club_id):
    after_time = 1730678399  # TODO : Change to be dynamic

    club_activities_request = requests.get(
        url=f'https://www.strava.com/api/v3/clubs/{club_id}/activities?per_page=100&after={after_time}',
        headers={'Authorization': f'Bearer {bearer_token}'})

    if club_activities_request.status_code == 200:
        return parse_club_activities(club_activities_request.json())
    else:
        error = club_activities_request.json()
        print(f'Something went wrong: {club_activities_request.status_code}: {error}')
        return None


def parse_club_activities(club_activities):
    athlete_distances = defaultdict(float)

    for activity in club_activities:
        firstname = activity['athlete']['firstname']
        lastname = activity['athlete']['lastname']
        full_name = f"{firstname} {lastname}"
        distance_in_meters = activity['distance']

        athlete_distances[full_name] += distance_in_meters

    return sorted(athlete_distances.items(), key=lambda x: x[1], reverse=True)


token = get_access_token()
if token is not None:
    leaderboard = get_club_activities(token, CLUB_ID)
    # Print the leaderboard
    print("Leaderboard based on total distance run:")
    for rank, (athlete, distance) in enumerate(leaderboard, start=1):
        distance_with_two_decimals = f'{(distance / 1000):.2f}'
        distance_with_one_decimal = distance_with_two_decimals[:len(distance_with_two_decimals) - 1]
        print(f"{rank}. {athlete}: {distance_with_one_decimal} km")
else:
    print('Something went wrong')

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
