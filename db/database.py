import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable, Sequence, Tuple

import asyncssh
import pymysql

from classes import Athlete, DatabaseSettings


@asynccontextmanager
async def _ssh_tunnel(settings: DatabaseSettings) -> AsyncIterator[asyncssh.SSHListener]:
    async with asyncssh.connect(
            settings.ssh_hostname,
            username=settings.pa_username,
            password=settings.pa_password,
            known_hosts=None,
            connect_timeout=10,
    ) as conn:
        listener = await conn.forward_local_port(
            "127.0.0.1",
            0,
            settings.pa_hostname,
            3306,
        )
        try:
            yield listener
        finally:
            listener.close()
            await listener.wait_closed()


def _connect_mysql(settings: DatabaseSettings, local_port: int) -> pymysql.connections.Connection:
    return pymysql.connect(
        host="127.0.0.1",
        port=local_port,
        user=settings.db_username,
        password=settings.db_password,
        database=settings.db_name,
        connect_timeout=10,
        autocommit=False,
    )


def _athlete_rows(athletes: Sequence[Athlete]) -> Iterable[Tuple[str, str, str]]:
    for athlete in athletes:
        yield athlete.id, athlete.firstname, athlete.lastname


def _activity_rows(
        athletes: Sequence[Athlete],
) -> Iterable[Tuple[str, str, float, float, float, object, object]]:
    for athlete in athletes:
        for activity in athlete.activities:
            yield (
                athlete.id,
                activity.type,
                activity.total_distance,
                activity.total_moving_time,
                activity.total_elevation_gain,
                activity.date_from,
                activity.date_to,
            )


def _ping_mysql(settings: DatabaseSettings, local_port: int) -> None:
    connection = _connect_mysql(settings, local_port)
    connection.close()


def _insert_athletes_and_activities(
        settings: DatabaseSettings,
        local_port: int,
        athletes: Sequence[Athlete],
) -> None:
    if not athletes:
        return

    connection = _connect_mysql(settings, local_port)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM ATHLETES")
            existing_ids = {row[0] for row in cursor.fetchall()}
            for athlete in athletes:
                if athlete.id not in existing_ids:
                    print(f"* Adding athlete [{athlete.firstname} {athlete.lastname}] to the database")

            cursor.executemany(
                """
                INSERT IGNORE INTO ATHLETES (id, firstname, lastname)
                VALUES (%s, %s, %s)
                """,
                list(_athlete_rows(athletes)),
            )

            cursor.executemany(
                """
                INSERT IGNORE INTO ACTIVITIES (athlete_id,
                                               type,
                                               total_distance,
                                               total_moving_time,
                                               total_elevation_gain,
                                               date_from,
                                               date_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                list(_activity_rows(athletes)),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


async def _run_with_tunnel(settings: DatabaseSettings, func, *args) -> None:
    async with _ssh_tunnel(settings) as tunnel:
        local_port = tunnel.get_port()
        await asyncio.to_thread(func, settings, local_port, *args)


def insert_athletes(settings: DatabaseSettings, athletes: Sequence[Athlete]) -> None:
    asyncio.run(_run_with_tunnel(settings, _insert_athletes_and_activities, athletes))
