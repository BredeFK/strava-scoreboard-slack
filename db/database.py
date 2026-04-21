import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable, List, Optional, Sequence, Tuple
from datetime import date

import asyncssh
import pymysql

from classes import Activity, Athlete, DatabaseSettings


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


def _athlete_club_rows(athletes: Sequence[Athlete], club_id: str) -> Iterable[Tuple[str, str]]:
    for athlete in athletes:
        yield athlete.id, club_id


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
        club_id: str
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
                INSERT
                IGNORE INTO ATHLETES (id, firstname, lastname)
                VALUES (
                %s,
                %s,
                %s
                )
                """,
                list(_athlete_rows(athletes)),
            )

            cursor.executemany(
                """
                INSERT
                IGNORE INTO ATHLETE_CLUBS (athlete_id, club_id)
                VALUES (
                %s,
                %s
                )
                """,
                list(_athlete_club_rows(athletes, club_id)),
            )

            cursor.executemany(
                """
                INSERT
                IGNORE INTO ACTIVITIES (athlete_id,
                                               type,
                                               total_distance,
                                               total_moving_time,
                                               total_elevation_gain,
                                               date_from,
                                               date_to)
                VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )
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


def insert_athletes(settings: DatabaseSettings, club_id: str, athletes: Sequence[Athlete]) -> None:
    asyncio.run(_run_with_tunnel(settings, _insert_athletes_and_activities, athletes, club_id))


def _rows_to_athletes(rows: list) -> List[Athlete]:
    athletes: dict[str, Athlete] = {}
    for row in rows:
        athlete_id, firstname, lastname, _, act_type, distance, moving_time, elevation, date_from, date_to = row
        if athlete_id not in athletes:
            athletes[athlete_id] = Athlete(id=athlete_id, firstname=firstname, lastname=lastname, activities=[])
        athletes[athlete_id].activities.append(Activity(
            type=act_type,
            total_distance=distance,
            total_moving_time=moving_time,
            total_elevation_gain=elevation,
            date_from=date_from,
            date_to=date_to,
        ))
    return list(athletes.values())


def _fetch_athletes_with_activities(settings: DatabaseSettings, local_port: int, club_id: str) -> List[Athlete]:
    connection = _connect_mysql(settings, local_port)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT a.id,
                       a.firstname,
                       a.lastname,
                       a2.id,
                       a2.type,
                       a2.total_distance,
                       a2.total_moving_time,
                       a2.total_elevation_gain,
                       a2.date_from,
                       a2.date_to
                FROM ATHLETES a
                         JOIN ACTIVITIES a2 ON a.id = a2.athlete_id
                         JOIN ATHLETE_CLUBS ac ON a.id = ac.athlete_id
                WHERE ac.club_id = %s;
                """,
                (club_id,),
            )
            return _rows_to_athletes(list(cursor.fetchall()))
    finally:
        connection.close()


def fetch_all_athletes_with_activities(settings: DatabaseSettings, club_id: str) -> Tuple[List[Athlete], Optional[date], Optional[date]]:
    result: List[Athlete] = []

    async def _run():
        async with _ssh_tunnel(settings) as tunnel:
            local_port = tunnel.get_port()
            rows = await asyncio.to_thread(_fetch_athletes_with_activities, settings, local_port, club_id)
            result.extend(rows)

    asyncio.run(_run())

    all_dates = [a.date_from for ath in result for a in ath.activities] + \
                [a.date_to   for ath in result for a in ath.activities]
    earliest = min(all_dates) if all_dates else None
    latest   = max(all_dates) if all_dates else None

    return result, earliest, latest
