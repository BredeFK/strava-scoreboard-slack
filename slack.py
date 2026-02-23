from datetime import datetime
import json
from typing import Dict, List

import requests

from classes import ScoreboardAthlete


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


def format_message(scoreboards: Dict[str, List[ScoreboardAthlete]], week_number: int, club_id: str) -> dict:
    blocks = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Uke {week_number}: Toppliste for Iterate Strava Gruppe :organism:"
                }
            }
        ]
    }

    mountain_emoji = get_mountain_emoji()
    if all(len(board) == 0 for board in scoreboards.values()):
        blocks['blocks'].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Det var ingen aktiviteter forrige uke :usmil:"
            }
        })
    else:
        for scoreboard_key, scoreboards in scoreboards.items():
            sections = _build_list(scoreboard_key, scoreboards, mountain_emoji)
            for section in sections:
                blocks['blocks'].append(section)

    section_join_the_group = {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f":runner: Snittfart\t:medal: Lengste tur\t{mountain_emoji} Høydemeter"
                        f"\n<https://www.strava.com/clubs/{club_id}|Bli med i stravagruppa>"
            }
        ]
    }

    blocks['blocks'].append(section_join_the_group)
    return blocks


def _build_list(activity_type: str, scoreboard: List[ScoreboardAthlete], mountain_emoji: str):
    sections = []
    config = _get_activity_config(activity_type)
    if len(scoreboard) != 0:
        sections.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": config['title']
            }
        })
        for index, athlete in enumerate(scoreboard):
            placement = get_placement_emoji(index + 1)

            activities_text = 'økter'
            if athlete.num_activities == 1:
                activities_text = 'økt'

            section = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f'{placement} {athlete.name}: *{athlete.total_distance}* '
                                f'({athlete.num_activities} {activities_text})'
                    },
                    {
                        "type": "mrkdwn",
                        "text": f'{config['pace_emoji']} *{athlete.avg_pace_per_km}*\t:medal: *{athlete.longest_activity}*'
                                f'\t{mountain_emoji} *{athlete.total_elevation_gain}*'
                    }
                ]
            }
            sections.append(section)
    elif len(scoreboard) == 0 and activity_type == 'Run':
        sections.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": config['title']
            }
        })
        sections.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": config['empty']
            }
        })
    return sections


def _get_activity_config(activity_type: str):
    config = {}
    if activity_type == 'Run':
        config = {
            "title": "*Løpelista* :sunny:",
            "pace_emoji": ":runner:",
            "empty": "Ingen som løp forrige uke :usmil:"
        }
    elif activity_type == 'NordicSki':
        config = {
            "title": "*Skilista* :snowflake:",
            "pace_emoji": ":skier:"
        }
    return config


def get_mountain_emoji() -> str:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    first_day_of_winter = datetime(year=today.year, month=10, day=14, hour=0, minute=0, second=0)
    first_day_of_summer = datetime(year=today.year, month=4, day=14, hour=0, minute=0, second=0)

    if first_day_of_summer <= today < first_day_of_winter:
        return ':mountain:'
    else:
        return ':snow_capped_mountain:'
