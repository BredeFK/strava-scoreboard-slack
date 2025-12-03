### Use this file to run on Pythonanywhere.com :) ###
import sys
from datetime import datetime, date

import slack
import strava

# Pythonanywhere.com could only run daily and not choose the day of the week. So the weekday stuff below is necessary ¯\_(ツ)_/¯
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
chosen_weekday = 'Monday'  # Change this to change the weekday the script should run on


def post_last_weeks_leaderboard(url: str, club_id: str, client_id: str, client_secret: str, refresh_token: str) -> None:
    print(f'Posting last weeks leaderboard @ {datetime.now()}')

    athletes = strava.get_club_activities(client_id, client_secret, refresh_token, club_id)
    message = slack.format_message(athletes, club_id)
    slack.post_slack_message(url, message)

    print(f'\nFunction executed -> The leaderboard had '
          f'{len(athletes)} athletes -> {", ".join(a.name for a in athletes)}')


weekday_index = date.today().weekday()
if len(sys.argv) == 6:
    if weekday_index == weekdays.index(chosen_weekday):
        post_last_weeks_leaderboard(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print(f'Not {chosen_weekday} today, it\'s {weekdays[weekday_index]}')
else:
    print('Missing arguments')
