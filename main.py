### Use this file to run locally :) ###
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

import slack
import strava

load_dotenv()

flags = ["--print", "-p"]


def post_last_weeks_leaderboard(only_print: bool) -> None:
    print(f'Posting last weeks leaderboard @ {datetime.now()}')

    url = os.environ["WEBHOOK_URL"]
    club_id = os.environ["CLUB_ID"]
    athletes = strava.get_club_activities(os.environ["CLIENT_ID"],
                                          os.environ["CLIENT_SECRET"],
                                          os.environ["REFRESH_TOKEN"],
                                          club_id)

    message = slack.format_message(athletes, club_id)
    if only_print:
        print(message)
    else:
        slack.post_slack_message(url, message)

    print(f'\nFunction executed -> The leaderboard had '
          f'{len(athletes)} athletes -> {", ".join(a.name for a in athletes)}')


options = False
if len(sys.argv) > 1 and sys.argv[1] in flags:
    options = True

post_last_weeks_leaderboard(options)
