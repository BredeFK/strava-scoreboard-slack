import os
from typing import Optional

from dotenv import load_dotenv

from classes import Settings, StravaSettings, DatabaseSettings

_settings: Optional[Settings] = None


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_settings(dotenv_file: str = '.env') -> Settings:
    global _settings
    if _settings is None:
        load_dotenv(dotenv_file)
        _settings = Settings(
            only_print=os.getenv("ONLY_PRINT", True),
            slack_url=_require_env("SLACK_WEBHOOK_URL"),
            strava=StravaSettings(
                club_id=_require_env("STRAVA_CLUB_ID"),
                client_id=_require_env("STRAVA_CLIENT_ID"),
                client_secret=_require_env("STRAVA_CLIENT_SECRET"),
                refresh_token=_require_env("STRAVA_REFRESH_TOKEN"),
            ),
            database=DatabaseSettings(
                ssh_hostname=_require_env("DATABASE_SSH_HOST_NAME"),
                pa_username=_require_env("DATABASE_PA_USERNAME"),
                pa_password=_require_env("DATABASE_PA_PASSWORD"),
                pa_hostname=_require_env("DATABASE_PA_HOSTNAME"),
                db_username=_require_env("DATABASE_USERNAME"),
                db_password=_require_env("DATABASE_PASSWORD"),
                db_host=_require_env("DATABASE_HOST"),
                db_name=_require_env("DATABASE_NAME"),
            )
        )
    return _settings


def get_strava_settings() -> StravaSettings:
    settings = get_settings()
    return settings.strava
