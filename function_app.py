import logging
import os
from datetime import datetime

import azure.functions as func

from slack import format_message, post_slack_message
from strava import get_last_weeks_leaderboard

app = func.FunctionApp()


def start_bot(webhook_url):
    athletes = get_last_weeks_leaderboard()
    message = format_message(athletes)
    post_slack_message(webhook_url, message)

    logging.info(f'Python timer trigger function executed. The leaderboard had {len(athletes)} athletes')


# Every Monday at 09:00, aka 11:00 in Norwegian time
@app.schedule(schedule="0 0 9 * * Mon", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def monday_timer_trigger(myTimer: func.TimerRequest) -> None:
    time_now = datetime.now()
    if myTimer.past_due:
        logging.warning(f'The timer is past due @ {time_now}')
    else:
        logging.info(f'The timer is on time @ {time_now}')

    url = os.environ["WEBHOOK_URL"]
    start_bot(url)


@app.route(route="force_monday_timer_trigger", auth_level=func.AuthLevel.ADMIN)
def force_monday_timer_trigger(req: func.HttpRequest) -> func.HttpResponse:
    time_now = datetime.now()
    is_test = req.route_params.get("test", default=True)
    url = os.environ["WEBHOOK_URL_TEST"]
    if is_test:
        logging.info(f'Python HTTP trigger function processed a test-request @ {time_now}')
    else:
        logging.info(f'Python HTTP trigger function processed a request @ {time_now}')
        url = os.environ["WEBHOOK_URL"]

    start_bot(url)

    return func.HttpResponse(f'Python timer trigger function executed @ {time_now}')
