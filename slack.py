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
    # number emojis from https://www.flaticon.com/packs/numbers-0-to-100-108
    #  medal emojis from https://www.flaticon.com/packs/winning-8
    if rank > 30:
        return rank
    match rank:
        case 1:
            return ':first_place_medal_1:'
        case 2:
            return ':second_place_medal_2:'
        case 3:
            return ':third_place_medal_3:'
        case _:
            return f':number-{rank}:'


def format_message(athletes):
    blocks = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Forrige ukes toppliste for Omegapoint Norge løpeklubb :sonic-running:"
                }
            }
        ]
    }

    if len(athletes) != 0:
        for index, athlete in enumerate(athletes):
            placement = get_placement_emoji(index + 1)

            activities_text = 'økter'
            if athlete.num_activities == 1:
                activities_text = 'økt'

            section_athlete = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f'{placement} {athlete.name}: *{athlete.get_total_distance()}* '
                                f'({athlete.num_activities} {activities_text})'
                    },
                    {
                        "type": "mrkdwn",
                        "text": f':runner: *{athlete.avg_pace_per_km()}*\t:medal: *{athlete.get_longest_activity()}*'
                                f'\t:mountain: *{athlete.get_total_elevation_gain()}*'
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
