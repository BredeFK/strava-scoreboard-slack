from datetime import datetime
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


def format_message(athletes, club_id):
    blocks = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":organism:Forrige ukes toppliste for Iterun:sonic_running:"
                }
            }
        ]
    }

    mountain_emoji = get_mountain_emoji()
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
                                f'\t{mountain_emoji} *{athlete.get_total_elevation_gain()}*'
                    }
                ]
            }
            blocks['blocks'].append(section_athlete)

    section_join_the_group = {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f":runner: Snittfart\t:medal: Lengste tur\t{mountain_emoji} Høydemeter"
                        f"\n<https://www.strava.com/clubs/{club_id}|Bli med i løpegruppa>"
            }
        ]
    }
    blocks['blocks'].append(section_join_the_group)
    return blocks


def get_mountain_emoji():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    first_day_of_winter = datetime(year=today.year, month=10, day=14, hour=0, minute=0, second=0)
    first_day_of_summer = datetime(year=today.year, month=4, day=14, hour=0, minute=0, second=0)

    if first_day_of_summer <= today < first_day_of_winter:
        return ':mountain:'
    else:
        return ':snow_capped_mountain:'
