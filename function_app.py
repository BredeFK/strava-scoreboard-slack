import logging
import os
from datetime import datetime

import azure.functions as func

from slack import post_slack_message

app = func.FunctionApp()


def start_bot():
    webhook_utl = os.environ["WEBHOOK_URL"]
    message = f'Hello, world :sonic-running: Today is {datetime.now()}'
    post_slack_message(webhook_utl, message)

    logging.info('Python timer trigger function executed with the message: {message}')


@app.schedule(schedule="0 0 6-14 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def monday_timer_trigger(myTimer: func.TimerRequest) -> None:
    time_now = datetime.now()
    if myTimer.past_due:
        logging.warning(f'The timer is past due @ {time_now}')
    else:
        logging.info(f'The timer is on time @ {time_now}')

    start_bot()


@app.route(route="force_monday_timer_trigger", auth_level=func.AuthLevel.ADMIN)
def force_monday_timer_trigger(req: func.HttpRequest) -> func.HttpResponse:
    time_now = datetime.now()
    logging.info(f'Python HTTP trigger function processed a request @ {time_now}')

    start_bot()

    return func.HttpResponse(f'Python timer trigger function executed @ {time_now}')
