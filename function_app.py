import logging
import os
from datetime import datetime

import azure.functions as func

import slack
import strava

app = func.FunctionApp()


# Every Monday at 09:00, aka 11:00 in Norwegian time
@app.schedule(schedule="0 0 9 * * Mon", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def monday_timer_trigger(myTimer: func.TimerRequest) -> None:
    time_now = datetime.now()
    if myTimer.past_due:
        logging.warning(f'The timer is past due @ {time_now}')
    else:
        logging.info(f'The timer is on time @ {time_now}')

    url = os.environ["WEBHOOK_URL"]
    athletes = strava.get_club_activities(os.environ["TOKEN_FILE_NAME"],
                                          os.environ["CLIENT_ID"],
                                          os.environ["CLIENT_SECRET"],
                                          os.environ["CODE"],
                                          os.environ["CLUB_ID"])

    message = slack.format_message(athletes)
    slack.post_slack_message(url, message)

    logging.info(f'Python Monday timer trigger function executed. The leaderboard had {len(athletes)} athletes')


@app.route(route="force_monday_timer_trigger", auth_level=func.AuthLevel.ADMIN)
def force_monday_timer_trigger(req: func.HttpRequest) -> func.HttpResponse:
    time_now = datetime.now()

    is_test = req.params.get('test')
    url = os.environ["WEBHOOK_URL_TEST"]
    if is_test:
        logging.info(f'Python HTTP trigger function processed a test-request @ {time_now}')
    else:
        logging.info(f'Python HTTP trigger function processed a request @ {time_now}')
        url = os.environ["WEBHOOK_URL"]

    athletes = strava.get_club_activities(os.environ["TOKEN_FILE_NAME"],
                                          os.environ["CLIENT_ID"],
                                          os.environ["CLIENT_SECRET"],
                                          os.environ["CODE"],
                                          os.environ["CLUB_ID"])

    logging.info(f'Python manual trigger function executed. The leaderboard has {len(athletes)} athletes')

    message = slack.format_message(athletes)
    slack.post_slack_message(url, message)

    return func.HttpResponse(f'Python timer trigger function executed @ {time_now}')
