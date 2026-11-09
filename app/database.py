"""Database connection management for PostgreSQL (psycopg 3)."""
import os

import psycopg

DB_CONFIG = {
    "user": os.getenv("POSTGRES_USER", "aquauser"),
    "password": os.getenv("POSTGRES_PASSWORD", "aquapass"),
    "dbname": os.getenv("POSTGRES_DB", "aquarium"),
    "host": os.getenv("POSTGRES_HOST", "db"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
}

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tanks (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    water_type  VARCHAR(20)  NOT NULL DEFAULT 'freshwater',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS readings (
    id            SERIAL PRIMARY KEY,
    tank_id       INTEGER     NOT NULL REFERENCES tanks(id) ON DELETE CASCADE,
    ph            NUMERIC(4,2),
    temperature_c NUMERIC(5,2),
    nh3_ppm       NUMERIC(6,3),
    no2_ppm       NUMERIC(6,3),
    no3_ppm       NUMERIC(7,3),
    measured_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_readings_tank ON readings (tank_id, measured_at DESC);
"""


def get_conn() -> psycopg.Connection:
    return psycopg.connect(**DB_CONFIG)


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(SCHEMA_SQL)
        conn.commit()
