from __future__ import annotations

from datetime import datetime, date
from typing import List, Any, Dict

from pydantic import BaseModel


class Activity(BaseModel):
    type: str
    total_distance: float
    total_moving_time: float
    total_elevation_gain: float
    date_from: date
    date_to: date


class Athlete(BaseModel):
    id: str
    firstname: str
    lastname: str
    activities: List[Activity]


class ScoreboardAthlete(BaseModel):
    name: str
    total_distance: str
    num_activities: int
    total_moving_time: float
    longest_activity: str
    total_elevation_gain: str
    avg_pace_per_km: str


class StravaSettings(BaseModel):
    club_id: str
    client_id: str
    client_secret: str
    refresh_token: str


class DatabaseSettings(BaseModel):
    ssh_hostname: str
    pa_username: str
    pa_password: str
    pa_hostname: str
    db_username: str
    db_password: str
    db_host: str
    db_name: str


class Settings(BaseModel):
    is_production: bool
    only_print: bool
    slack_url: str
    strava: StravaSettings
    database: DatabaseSettings


def parse_club_activities(club_activities: List[Any], date_from: datetime, date_to: datetime) -> List[Athlete]:
    athletes: Dict[str, Athlete] = {}
    for activity in club_activities:
        activity_type = activity.get('type')
        if activity_type not in {'Run', 'NordicSki'}:
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
            total_elevation_gain=elevation_gain,
            date_from=date_from.date(),
            date_to=date_to.date()
        )

        athletes[athlete_id].activities.append(activity_record)

    if len(athletes) == 0:
        print('No club activities found')
        return []

    return list(athletes.values())
