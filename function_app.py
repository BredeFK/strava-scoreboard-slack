import logging
import os
from datetime import date

import azure.functions as func

from slack import post_slack_message

app = func.FunctionApp()


@app.schedule(schedule="0 0 6-14 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def monday_timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    webhook_utl = os.environ["WEBHOOK_URL"]
    message = f'Hello, world! Today is {date.today()}'
    post_slack_message(webhook_utl, message)

    logging.info('Python timer trigger function executed with the message: {message}')
