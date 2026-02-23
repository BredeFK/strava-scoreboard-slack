import json
from datetime import datetime

import slack
import strava
from classes import Settings

ACTIVITY_TYPES = ['Run', 'NordicSki']


def post_last_weeks_leaderboard(settings: Settings) -> None:
    week_number = strava.get_last_weeks_week_number()
    print(f'Posting week {week_number} leaderboard @ {datetime.now()}')

    athletes = strava.get_club_athletes(settings.strava, ACTIVITY_TYPES)
    scoreboards = strava.parse_scoreboard_list(athletes, ACTIVITY_TYPES)
    message = slack.format_message(scoreboards, week_number, settings.strava.club_id)
    if settings.only_print:
        print(json.dumps(message))
    else:
        slack.post_slack_message(settings.slack_url, message)
    print(
        f'\nFunction executed -> The leaderboard had ' f'{len(athletes)} athletes -> '
        f'{", ".join(f'{athlete.firstname} {athlete.lastname}' for athlete in athletes)}'
    )
