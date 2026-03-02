import json
import logging
from datetime import datetime
from typing import Dict, List

import requests

from classes import ScoreboardAthlete

numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'keycap_ten']


def post_message(webhook_url, formatted_message):
    discord_request = requests.post(url=webhook_url, headers={'Content-type': 'application/json'},
                                    data=json.dumps(formatted_message))

    if discord_request.status_code == 204:
        logging.info('Successfully sent discord message')
    else:
        logging.error(f'Error [{discord_request.status_code}] sending discord message: {discord_request.text}')


def _get_placement_emoji(rank):
    if rank > 10:
        return f'**{rank}**'
    match rank:
        case 1:
            return ':first_place:'
        case 2:
            return ':second_place:'
        case 3:
            return ':third_place:'
        case _:
            return f':{numbers[rank - 1]}:'


def _get_color_of_the_week():
    # https://coolors.co/palette/f94144-f3722c-f8961e-f9844a-f9c74f-90be6d-43aa8b-4d908e-577590-277da1
    coolors = [16335172, 15954476, 16291358, 16352330, 16369487,
               9485933, 4434571, 5083278, 5731728, 2588065]

    current_week = datetime.now().isocalendar()[1]

    # Determine the index for the color
    color_index = (current_week - 1) % len(coolors)

    return coolors[color_index]


def format_message(scoreboards: Dict[str, List[ScoreboardAthlete]], week_number: int, club_id: str) -> dict:
    payload = {
        "username": "The Ginger Pigeons StravaBot",
        "embeds": [
            {
                "title": f"Week {week_number}: Leaderboard for The Ginger Pigeons running club :person_running:",
                "color": _get_color_of_the_week(),
                "fields": [],
                "footer": {
                    "text": f"Join us @ https://www.strava.com/clubs/{club_id}"
                }
            }
        ]
    }

    field_athlete = {
        "name": "Athlete",
        "value": "",
        "inline": "true"
    }
    field_avg_pace = {
        "name": "Avg. pace",
        "value": "",
        "inline": True
    }
    field_longest = {
        "name": "Longest",
        "value": "",
        "inline": True
    }

    if len(scoreboards.items()) != 0:
        index = 0
        for scoreboard_key, scoreboards in scoreboards.items():
            if scoreboard_key == 'Run':
                for athlete in scoreboards:
                    placement = _get_placement_emoji(index + 1)
                    activities_text = 'runs'
                    if athlete.num_activities == 1:
                        activities_text = 'run'

                    field_athlete["value"] += (f'{placement} {athlete.name}: **{athlete.total_distance}** '
                                               f'({athlete.num_activities} {activities_text})\n\n')
                    field_avg_pace["value"] += f'{athlete.avg_pace_per_km}\n\n'
                    field_longest["value"] += f'{athlete.longest_activity}\n\n'
                    index += 1

    payload['embeds'][0]['fields'].append(field_athlete)
    payload['embeds'][0]['fields'].append(field_avg_pace)
    payload['embeds'][0]['fields'].append(field_longest)
    return payload
