### Use this file to run locally :) ###
import os
from datetime import datetime

from dotenv import load_dotenv

import slack
import strava

load_dotenv()


def post_last_weeks_leaderboard() -> None:
    print(f'Posting last weeks leaderboard @ {datetime.now()}')

    url = os.environ["WEBHOOK_URL"]
    athletes = strava.get_club_activities(os.environ["CLIENT_ID"],
                                          os.environ["CLIENT_SECRET"],
                                          os.environ["REFRESH_TOKEN"],
                                          os.environ["CLUB_ID"])

    message = slack.format_message(athletes)
    #slack.post_slack_message(url, message)
    print(message)

    print(f'Function executed -> The leaderboard had {len(athletes)} athletes')


post_last_weeks_leaderboard()
