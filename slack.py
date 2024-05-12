import json

import requests


def post_slack_message(webhook_url, formatted_message):
    slack_request = requests.post(url=webhook_url, headers={'Content-type': 'application/json'},
                                  data=json.dumps(formatted_message))

    if slack_request.status_code == 200:
        print('Successfully sent slack message')
    else:
        print(f'Error[{slack_request.status_code}] sending slack message: {slack_request.text}')


def get_placement_emoji(rank):
    if rank > 30:
        return rank
    match rank:
        case 1:
            return ':first_place_medal:'
        case 2:
            return ':second_place_medal:'
        case 3:
            return ':third_place_medal:'
        case _:
            return f':number-{rank}:'


def format_message(athletes):
    blocks = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Forrige ukes toppliste for Omegapoint løpeklubb :sonic-running:"
                }
            }
        ]
    }

    if len(athletes) != 0:
        for athlete in athletes:
            placement = get_placement_emoji(athlete["rank"])

            longest_run = athlete["longest_run"]
            distance = longest_run.split(" km")[0]
            if float(distance) < 10.0:
                longest_run = f'  {longest_run}'

            activities_text = 'økter'
            if athlete["number_of_runs"] == 1:
                activities_text = 'økt'

            section_athlete = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f'{placement} {athlete["athlete_name"]}: *{athlete["total_distance"]}* '
                                f'({athlete["number_of_runs"]} {activities_text})'
                    },
                    {
                        "type": "mrkdwn",
                        "text": f':runner: *{athlete["avg_pace"]}*\t:medal: *{longest_run}*'
                                f'\t:mountain: *{athlete["total_elevation_gain"]}*'
                    }
                ]
            }
            blocks['blocks'].append(section_athlete)

    section_join_the_group = {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": ":runner: Snittfart\t:medal: Lengste tur\t:mountain: Høydemeter"
                        "\n<https://www.strava.com/clubs/526085|Bli med i løpegruppa>"
            }
        ]
    }
    blocks['blocks'].append(section_join_the_group)
    return blocks
