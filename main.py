import json
from datetime import date, datetime

import slack
import strava
from classes import Settings
from config import get_settings
from db.database import insert_athletes

CHOSEN_WEEKDAY = 'Monday'  # Change this to change the weekday the script should run on
ACTIVITY_TYPES = ['Run', 'NordicSki']


def _post_last_weeks_leaderboard(settings: Settings) -> None:
    week_number = strava.get_last_weeks_week_number()
    print(f'Posting week {week_number} leaderboard @ {datetime.now()}')

    athletes = strava.get_club_athletes(settings.strava, ACTIVITY_TYPES)

    try:
        insert_athletes(settings.database, athletes)
    except Exception as ex:
        print(f'Failed to add athletes to database: {ex}')
    scoreboards = strava.parse_scoreboard_list(athletes, ACTIVITY_TYPES)
    message = slack.format_message(scoreboards, week_number, settings.strava.club_id)
    if settings.only_print:
        print(json.dumps(message))
    else:
        slack.post_slack_message(settings.slack_url, message)
    athlete_names = ", ".join(f"{athlete.firstname} {athlete.lastname}" for athlete in athletes)
    print(f"\nFunction executed -> The leaderboard had {len(athletes)} athletes -> {athlete_names}")


def _python_anywhere(settings: Settings):
    # Pythonanywhere.com could only run daily and not choose the day of the week. So the weekday stuff below is necessary ¯\_(ツ)_/¯
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_index = date.today().weekday()
    if weekday_index == weekdays.index(CHOSEN_WEEKDAY):
        _post_last_weeks_leaderboard(settings)
    else:
        print(f'Not {CHOSEN_WEEKDAY} today, it\'s {weekdays[weekday_index]}')


if __name__ == '__main__':
    _settings = get_settings()
    if _settings.is_production:
        _python_anywhere(_settings)
    else:
        _post_last_weeks_leaderboard(_settings)
