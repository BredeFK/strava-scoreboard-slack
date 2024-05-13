import json

import requests

numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'keycap_ten']


def post_discord_message(webhook_url, formatted_message):
    discord_request = requests.post(url=webhook_url, headers={'Content-type': 'application/json'},
                                    data=json.dumps(formatted_message))

    if discord_request.status_code == 204:
        print('Successfully sent discord message')
    else:
        print(f'Error[{discord_request.status_code}] sending discord message: {discord_request.text}')


def get_placement_emoji(rank):
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


def format_message(athletes):
    payload = {
        "username": "The Ginger Pigeons StravaBot",
        "embeds": [
            {
                "title": "Last weeks leaderboard for The Ginger Pigeons running club :person_running:",
                "color": 16534530,
                "description": "*Join our running group :point_right: https://www.strava.com/clubs/ginger-pigeons*",
                "fields": []
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
