### Use this file to run on Pythonanywhere.com :) ###
import sys
from datetime import date

from classes import Settings, StravaSettings
from main_function import post_last_weeks_leaderboard

# Only activities that will be posted
ACTIVITY_TYPES = ['Run', 'NordicSki']

# Pythonanywhere.com could only run daily and not choose the day of the week. So the weekday stuff below is necessary ¯\_(ツ)_/¯
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
chosen_weekday = 'Monday'  # Change this to change the weekday the script should run on

weekday_index = date.today().weekday()
if len(sys.argv) == 6:
    if weekday_index == weekdays.index(chosen_weekday):
        settings = Settings(
            only_print=False,
            slack_url=sys.argv[1],
            strava=StravaSettings(
                club_id=sys.argv[2],
                client_id=sys.argv[3],
                client_secret=sys.argv[4],
                refresh_token=sys.argv[5])
        )
        post_last_weeks_leaderboard(settings)
    else:
        print(f'Not {chosen_weekday} today, it\'s {weekdays[weekday_index]}')
else:
    print('Missing arguments')
