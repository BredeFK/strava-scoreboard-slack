import json
import logging
from datetime import datetime

import requests

numbers = ['<:number4:1272258897150873730>', '<:number5:1272258898937778268>', '<:number6:1272258900019642490>',
           '<:number7:1272258901693436046>', '<:number8:1272258903605903360>', '<:number9:1272258904969052241>',
           '<:number10:1272258939022741698>', '<:number11:1272251988041531452>', '<:number12:1272252049932681301>']


def post_discord_message(webhook_url, formatted_message):
    discord_request = requests.post(url=webhook_url, headers={'Content-type': 'application/json'},
                                    data=json.dumps(formatted_message))

    if discord_request.status_code == 204:
        logging.info('Successfully sent discord message')
    else:
        logging.error(f'Error [{discord_request.status_code}] sending discord message: {discord_request.text}')


def get_placement_emoji(rank):
    if rank > 12:
        return f'**{rank}**'
    match rank:
        case 1:
            return '<:first_place_medal_1:1272258655252779189>'
        case 2:
            return '<:second_place_medal_2:1272258653927506034>'
        case 3:
            return '<:third_place_medal_3:1272258652711161947>'
        case _:
            return f'{numbers[rank - 4]}'


def get_color_of_the_week():
    # https://coolors.co/palette/f94144-f3722c-f8961e-f9844a-f9c74f-90be6d-43aa8b-4d908e-577590-277da1
    coolors = [16335172, 15954476, 16291358, 16352330, 16369487,
               9485933, 4434571, 5083278, 5731728, 2588065]

    current_week = datetime.now().isocalendar()[1]

    # Determine the index for the color
    color_index = (current_week - 1) % len(coolors)

    return coolors[color_index]


def format_message(athletes):
    payload = {
        "username": "The Ginger Pigeons StravaBot",
        "embeds": [
            {
                "title": "Last weeks leaderboard for The Ginger Pigeons running club <:fall_muscle:772487746627174452>",
                "color": get_color_of_the_week(),
                "fields": [],
                "footer": {
                    "text": "Join us @ https://www.strava.com/clubs/ginger-pigeons"
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

    if len(athletes) != 0:
        for athlete in athletes:
            placement = get_placement_emoji(athlete["rank"])
            activities_text = 'runs'
            if athlete["number_of_runs"] == 1:
                activities_text = 'run'

            field_athlete["value"] += (f'{placement} {athlete["athlete_name"]}: **{athlete["total_distance"]}** '
                                       f'({athlete["number_of_runs"]} {activities_text})\n\n')
            field_avg_pace["value"] += f'{athlete["avg_pace"]}\n\n'
            field_longest["value"] += f'{athlete["longest_run"]}\n\n'

    payload['embeds'][0]['fields'].append(field_athlete)
    payload['embeds'][0]['fields'].append(field_avg_pace)
    payload['embeds'][0]['fields'].append(field_longest)
    return payload
