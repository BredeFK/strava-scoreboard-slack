### Use this file to run locally :) ###
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

import slack
import strava

load_dotenv()

flags = ["--print", "-p"]


def post_last_weeks_leaderboard(only_print: bool, url: str, club_id: str, client_id: str, client_secret: str,
                                refresh_token: str) -> None:
    print(f'Posting last weeks leaderboard @ {datetime.now()}')

    athletes = strava.get_club_activities(client_id, client_secret, refresh_token, club_id)
    message = slack.format_message(athletes, club_id)
    if only_print:
        print(message)
    else:
        slack.post_slack_message(url, message)

    print(f'\nFunction executed -> The leaderboard had '
          f'{len(athletes)} athletes -> {", ".join(a.name for a in athletes)}')


options = len(sys.argv) > 1 and sys.argv[1] in flags
if len(sys.argv) > 5:
    if options:
        post_last_weeks_leaderboard(options, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    else:
        post_last_weeks_leaderboard(options, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
else:
    post_last_weeks_leaderboard(options, os.environ["WEBHOOK_URL"], os.environ["CLUB_ID"], os.environ["CLIENT_ID"],
                                os.environ["CLIENT_SECRET"], os.environ["REFRESH_TOKEN"])
