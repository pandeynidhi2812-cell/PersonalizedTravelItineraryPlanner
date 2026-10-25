import json
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "travel.db"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'traveler',
    home_city TEXT DEFAULT '',
    travel_style TEXT DEFAULT 'mid',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    state TEXT,
    tagline TEXT,
    description TEXT,
    best_season TEXT,
    avg_daily_budget INTEGER,
    tags TEXT
);
CREATE TABLE IF NOT EXISTS attractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    name TEXT NOT NULL,
    tags TEXT,
    entry_fee INTEGER DEFAULT 0,
    duration_min INTEGER DEFAULT 60,
    best_slot TEXT DEFAULT 'morning',
    area TEXT,
    description TEXT
);
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    name TEXT NOT NULL,
    cuisine TEXT,
    tier TEXT,
    cost_per_person INTEGER,
    rating REAL,
    description TEXT
);
CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    name TEXT NOT NULL,
    tier TEXT,
    price_per_night INTEGER,
    rating REAL,
    amenities TEXT
);
CREATE TABLE IF NOT EXISTS transports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    mode TEXT NOT NULL,
    cost_per_day INTEGER,
    unit TEXT,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    title TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    travelers INTEGER DEFAULT 1,
    budget INTEGER DEFAULT 0,
    style TEXT DEFAULT 'mid',
    pace TEXT DEFAULT 'balanced',
    interests TEXT DEFAULT '[]',
    itinerary TEXT,
    total_cost INTEGER DEFAULT 0,
    seed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS trip_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT DEFAULT 'editor',
    interests TEXT DEFAULT '[]',
    UNIQUE (trip_id, user_id)
);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def q(conn, sql, args=()):
    return [dict(r) for r in conn.execute(sql, args).fetchall()]


def q1(conn, sql, args=()):
    row = conn.execute(sql, args).fetchone()
    return dict(row) if row else None


def loads(value, default=None):
    if value is None or value == "":
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def load_bundle(conn, destination_id):
    """Everything the planner needs to know about one destination."""
    dest = q1(conn, "SELECT * FROM destinations WHERE id = ?", (destination_id,))
    if not dest:
        return None
    dest["tags"] = loads(dest["tags"], [])
    attractions = q(conn, "SELECT * FROM attractions WHERE destination_id = ? ORDER BY id", (destination_id,))
    for a in attractions:
        a["tags"] = loads(a["tags"], [])
    hotels = q(conn, "SELECT * FROM hotels WHERE destination_id = ? ORDER BY price_per_night", (destination_id,))
    for h in hotels:
        h["amenities"] = loads(h["amenities"], [])
    return {
        "destination": dest,
        "attractions": attractions,
        "restaurants": q(conn, "SELECT * FROM restaurants WHERE destination_id = ? ORDER BY cost_per_person", (destination_id,)),
        "hotels": hotels,
        "transports": q(conn, "SELECT * FROM transports WHERE destination_id = ? ORDER BY cost_per_day", (destination_id,)),
    }
