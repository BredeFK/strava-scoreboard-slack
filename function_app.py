import logging
import os
from datetime import datetime

import azure.functions as func

import discord
import strava

app = func.FunctionApp()


def start_bot(webhook_url):
    athletes = strava.get_club_activities(os.environ["TOKEN_FILE_NAME"],
                                          os.environ["CLIENT_ID"],
                                          os.environ["CLIENT_SECRET"],
                                          os.environ["CODE"],
                                          os.environ["CLUB_ID"])

    message = discord.format_message(athletes)
    discord.post_discord_message(webhook_url, message)

    logging.info(f'Python timer trigger function executed. The leaderboard had {len(athletes)} athletes')


# Every Monday at 09:30, aka 11:30 in Norwegian time
@app.timer_trigger(schedule="0 30 9 * * Mon", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def monday_timer_trigger_discord(myTimer: func.TimerRequest) -> None:
    time_now = datetime.now()
    if myTimer.past_due:
        logging.warning(f'The timer is past due @ {time_now}')
    else:
        logging.info(f'The timer is on time @ {time_now}')

    url = os.environ["WEBHOOK_URL"]
    start_bot(url)
