from datetime import datetime, timezone, timedelta
from typing import List, Any, Dict, Tuple, Optional

import requests

from classes import StravaSettings, Athlete, Activity, ScoreboardAthlete

BASE_URL = 'https://www.strava.com'


def _get_access_token(client_id: str, client_secret: str, refresh_token: str):
    print('Fetching access_token using refresh_token')
    refresh_token_request = requests.post(
        url=f'{BASE_URL}/api/v3/oauth/token',
        params={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        })
    if refresh_token_request.status_code == 200:
        print('Got new token using refresh token')
        refresh_token_request_json = refresh_token_request.json()
        return refresh_token_request_json['access_token']
    else:
        error = refresh_token_request.json()
        print(f'Could not get new token using refresh token: [{refresh_token_request.status_code}] {error}')
        return None


def get_last_monday_and_sunday() -> Tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)

    last_monday = now - timedelta(days=now.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return (last_monday.replace(hour=0, minute=0, second=0, microsecond=0),
            last_sunday.replace(hour=23, minute=59, second=59, microsecond=999999))


def get_last_weeks_week_number() -> int:
    last_monday, _ = get_last_monday_and_sunday()
    return last_monday.isocalendar().week


def get_club_athletes(settings: StravaSettings, activity_types: List[str]) -> List[Athlete]:
    access_token = _get_access_token(settings.client_id, settings.client_secret, settings.refresh_token)
    last_monday, last_sunday = get_last_monday_and_sunday()
    after_monday_activities = _get_activities(access_token, settings.club_id, last_monday)
    after_sunday_activities = _get_activities(access_token, settings.club_id, last_sunday)

    last_weeks_activities = [activity for activity in after_monday_activities if
                             activity not in after_sunday_activities]

    return _parse_club_activities(last_weeks_activities, last_monday, last_sunday, activity_types)


def _get_activities(access_token: str, club_id: str, after_time: datetime):
    timestamp = int(after_time.timestamp())
    print(f'Getting activities after {after_time.date()} [{timestamp}]')
    club_activities_request = requests.get(
        url=f'https://www.strava.com/api/v3/clubs/{club_id}/activities?per_page=100&after={timestamp}',
        headers={'Authorization': f'Bearer {access_token}'})
    if club_activities_request.status_code == 200:
        return club_activities_request.json()
    else:
        error = club_activities_request.json()
        exit(f'Something went wrong: {club_activities_request.status_code}: {error}')


def _parse_club_activities(club_activities: List[Any], date_from: datetime, date_to: datetime,
                           activity_types: List[str]) -> List[Athlete]:
    athletes: Dict[str, Athlete] = {}
    for activity in club_activities:
        activity_type = activity.get('type')
        if activity_type not in activity_types:
            continue

        athlete_data = activity.get('athlete', {})
        athlete_firstname = athlete_data.get('firstname', '')
        athlete_lastname = athlete_data.get('lastname', '')
        athlete_id = f'{athlete_firstname.upper().replace(" ", "_")}_{athlete_lastname.upper().replace(".", "")}'

        if athlete_id not in athletes:
            athletes[athlete_id] = Athlete(
                id=athlete_id,
                firstname=athlete_firstname,
                lastname=athlete_lastname,
                activities=[]
            )

        distance = activity.get('distance', 0.0)
        moving_time = activity.get('moving_time', 0.0)
        elevation_gain = activity.get('total_elevation_gain', 0.0)

        activity_record = Activity(
            type=activity_type,
            total_distance=distance,
            total_moving_time=moving_time,
            longest_activity=distance,
            total_elevation_gain=elevation_gain,
            date_from=date_from.date(),
            date_to=date_to.date()
        )

        athletes[athlete_id].activities.append(activity_record)

    if len(athletes) == 0:
        print('No club activities found')
        return []

    return list(athletes.values())


def _avg_pace_per_km(total_distance: float, total_moving_time: float) -> str | None:
    if total_distance == 0:
        return None
    pace_seconds = total_moving_time / (total_distance / 1000)
    minutes = int(pace_seconds // 60)
    seconds = int(pace_seconds % 60)
    return f'{minutes}:{seconds:02d} /km'


def _distance_to_km(distance: float) -> str:
    return f'{distance / 1000:.2f} km'


def _get_total_elevation_gain(elevation_gain: Optional[float]) -> str:
    if elevation_gain is None or elevation_gain == 0:
        return '--'
    else:
        return f'{int(elevation_gain)} m'


def parse_scoreboard_list(athletes: List[Athlete], activity_types: List[str]) -> Dict[str, List[ScoreboardAthlete]]:
    scoreboards: Dict[str, Dict[str, Dict[str, Any]]] = {activity_type: {} for activity_type in activity_types}

    for athlete in athletes:
        athlete_name = f'{athlete.firstname} {athlete.lastname}'.strip()
        for activity in athlete.activities:
            activity_type = activity.type
            if activity_type not in scoreboards:
                scoreboards[activity_type] = {}

            athlete_scoreboard = scoreboards[activity_type]
            if athlete.id not in athlete_scoreboard:
                athlete_scoreboard[athlete.id] = {
                    'id': athlete.id,
                    'name': athlete_name,
                    'total_distance': 0.0,
                    'num_activities': 0,
                    'total_moving_time': 0.0,
                    'longest_activity': 0.0,
                    'total_elevation_gain': 0.0
                }

            entry = athlete_scoreboard[athlete.id]
            entry['total_distance'] += activity.total_distance
            entry['num_activities'] += 1
            entry['total_moving_time'] += activity.total_moving_time
            entry['longest_activity'] = max(entry['longest_activity'], activity.total_distance)
            entry['total_elevation_gain'] += activity.total_elevation_gain

    scoreboard_list: Dict[str, List[ScoreboardAthlete]] = {}
    for activity_type, athlete_map in scoreboards.items():
        for entry in athlete_map.values():
            entry['avg_pace_per_km'] = _avg_pace_per_km(
                entry['total_distance'],
                entry['total_moving_time']
            )
        scoreboard_list[activity_type] = sorted(
            [
                ScoreboardAthlete(
                    name=entry['name'],
                    total_distance=_distance_to_km(entry['total_distance']),
                    num_activities=entry['num_activities'],
                    total_moving_time=entry['total_moving_time'],
                    longest_activity=_distance_to_km(entry['longest_activity']),
                    total_elevation_gain=_get_total_elevation_gain(entry['total_elevation_gain']),
                    avg_pace_per_km=entry['avg_pace_per_km']
                )
                for entry in athlete_map.values()
            ],
            key=lambda athlete_entry: athlete_entry.total_distance,
            reverse=True
        )

    return scoreboard_list
