CREATE TABLE IF NOT EXISTS ATHLETES
(
    id         VARCHAR(128) NOT NULL,
    firstname  VARCHAR(128) NOT NULL,
    lastname   VARCHAR(128) NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ACTIVITIES
(
    id                   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    athlete_id           VARCHAR(128)    NOT NULL,
    type                 VARCHAR(32)     NOT NULL,
    total_distance       DOUBLE          NOT NULL,
    total_moving_time    DOUBLE          NOT NULL,
    total_elevation_gain DOUBLE          NOT NULL,
    date_from            DATE            NOT NULL,
    date_to              DATE            NOT NULL,
    PRIMARY KEY (id),
    KEY idx_activities_athlete_id (athlete_id),
    UNIQUE KEY uq_activities_athlete_type_dates (athlete_id, type, total_distance, total_moving_time,
                                                 total_elevation_gain, date_from, date_to),
    CONSTRAINT fk_activities_athlete
        FOREIGN KEY (athlete_id)
            REFERENCES ATHLETES (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS CLUBS
(
    id   VARCHAR(128) NOT NULL,
    name VARCHAR(128) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS ATHLETE_CLUBS
(
    athlete_id VARCHAR(128) NOT NULL,
    club_id    VARCHAR(128) NOT NULL,
    PRIMARY KEY (athlete_id, club_id),
    KEY idx_athlete_clubs_club_id (club_id),
    CONSTRAINT fk_athlete_clubs_athlete
        FOREIGN KEY (athlete_id)
            REFERENCES ATHLETES (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
    CONSTRAINT fk_athlete_clubs_club
        FOREIGN KEY (club_id)
            REFERENCES CLUBS (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);
