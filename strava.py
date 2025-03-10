import json
import os.path
import time
from datetime import datetime, timezone, timedelta

import requests

from Athlete import Athlete

BASE_URL = 'https://www.strava.com'


def get_access_token(token_file_name, client_id, client_secret, code):
    if os.path.exists(token_file_name):
        file = open(token_file_name, 'r')
        lines = file.readlines()
        expires_at = int(lines[0].strip())
        refresh_token = lines[1].strip()
        access_token = lines[2].strip()
        time_now = int(time.time())
        if time_now >= expires_at:
            print('AccessToken has expired')
            refresh_token_request = requests.post(url=f'{BASE_URL}/api/v3/oauth/token',
                                                  params={'client_id': client_id,
                                                          'client_secret': client_secret,
                                                          'grant_type': 'refresh_token',
                                                          'refresh_token': refresh_token})
            if refresh_token_request.status_code == 200:
                print('Got new token using refresh token')
                refresh_token_request_json = refresh_token_request.json()
                return update_token_file_and_return_access_token(refresh_token_request_json, token_file_name)
            else:
                error = refresh_token_request.json()
                print(f'Could not get new token using refresh token: [{refresh_token_request.status_code}] {error}')
                return None
        else:
            print('Stored accessToken is still valid')
            return access_token
    else:
        strava_request = requests.post(url=f'{BASE_URL}/api/v3/oauth/token',
                                       params={'client_id': client_id,
                                               'client_secret': client_secret,
                                               'code': code,
                                               'grant_type': 'authorization_code'})

        if strava_request.status_code == 200:
            print('Fetched fresh accessToken')
            strava_request_json = strava_request.json()
            return update_token_file_and_return_access_token(strava_request_json, token_file_name)
        else:
            print(f'Something went wrong: {strava_request.status_code}')
            error = strava_request.json()
            print(error)
            return None


def update_token_file_and_return_access_token(json_body, token_file_name):
    token_file = open(token_file_name, 'w')
    access_token = json_body['access_token']
    token_file.write(str(json_body['expires_at']) + '\n')
    token_file.write(json_body['refresh_token'] + '\n')
    token_file.write(access_token)
    token_file.close()
    return access_token


def get_last_monday_unix():
    now = datetime.now(timezone.utc)
    last_monday = now - timedelta(days=(now.weekday() + 7) % 7)
    last_monday = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(last_monday.timestamp())


def get_club_activities(token_file_name, client_id, client_secret, code, club_id):
    access_token = get_access_token(token_file_name, client_id, client_secret, code)
    after_time = get_last_monday_unix()

    club_activities_request = requests.get(
        url=f'https://www.strava.com/api/v3/clubs/{club_id}/activities?per_page=100&after={after_time}',
        headers={'Authorization': f'Bearer {access_token}'})

    if club_activities_request.status_code == 200:
        return parse_club_activities(club_activities_request.json())
    else:
        error = club_activities_request.json()
        print(f'Something went wrong: {club_activities_request.status_code}: {error}')
        return None


def parse_club_activities(club_activities):
    athletes = {}

    if club_activities is None or len(club_activities) == 0:
        exit('No club activities found')

    for activity in club_activities:
        if activity['type'] == 'Run':
            full_name = f"{activity['athlete']['firstname']} {activity['athlete']['lastname']}"
            moving_time = activity['moving_time']
            elevation_gain = activity['total_elevation_gain']

            if full_name not in athletes:
                athletes[full_name] = Athlete(full_name)

            athletes[full_name].add_activity(activity['distance'], moving_time, elevation_gain)

    return sorted(athletes.values(), key=lambda a: a.total_distance, reverse=True)


def save_athletes_to_file(athletes, filename="athletes.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([athlete.__dict__ for athlete in athletes], f, indent=4)


def load_athletes_from_file(filename="athletes.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Athlete(**athlete_data) for athlete_data in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []
