### Use this file to run locally :) ###
from config import get_settings
from database import db_connect
from main_function import post_last_weeks_leaderboard

if __name__ == '__main__':
    settings = get_settings()
    #post_last_weeks_leaderboard(settings)
    db_connect(settings.database)
