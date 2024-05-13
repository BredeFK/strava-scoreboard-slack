import logging
import os
from datetime import datetime

import azure.functions as func

from discord import format_message, post_discord_message
from strava import get_last_weeks_leaderboard

app = func.FunctionApp()


def start_bot(webhook_url):
    athletes = get_last_weeks_leaderboard()
    message = format_message(athletes)
    post_discord_message(webhook_url, message)

    logging.info(f'Python timer trigger function executed. The leaderboard had {len(athletes)} athletes')


# Every Monday at 09:00, aka 11:00 in Norwegian time
@app.timer_trigger(schedule="0 0 9 * * Mon", arg_name="myTimer", run_on_startup=False, use_monitor=True) 
def monday_timer_trigger_discord(myTimer: func.TimerRequest) -> None:
    time_now = datetime.now()
    if myTimer.past_due:
        logging.warning(f'The timer is past due @ {time_now}')
    else:
        logging.info(f'The timer is on time @ {time_now}')

    url = os.environ["WEBHOOK_URL"]
    start_bot(url)

