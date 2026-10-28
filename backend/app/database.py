import json
import os
import sqlite3
from contextlib import contextmanager

try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "travel.db"),
)

_pg_pool = None


def get_database_url() -> str:
    """Returns normalized DATABASE_URL if configured, prioritizing TEST_DATABASE_URL."""
    url = (os.getenv("TEST_DATABASE_URL", "").strip() or os.getenv("DATABASE_URL", "").strip())
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def is_postgres() -> bool:
    """True if configured to connect to PostgreSQL."""
    return bool(get_database_url())


def adapt_sql_for_postgres(sql: str) -> str:
    """
    Safely converts SQLite '?' parameter markers to PostgreSQL '%s'
    while ignoring '?' inside string literals, quoted identifiers, and comments.
    """
    out = []
    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        # Line comment: --
        if ch == '-' and i + 1 < n and sql[i + 1] == '-':
            end = sql.find('\n', i + 2)
            if end == -1:
                out.append(sql[i:])
                break
            else:
                out.append(sql[i:end + 1])
                i = end + 1
                continue
        # Block comment: /* ... */
        if ch == '/' and i + 1 < n and sql[i + 1] == '*':
            end = sql.find('*/', i + 2)
            if end == -1:
                out.append(sql[i:])
                break
            else:
                out.append(sql[i:end + 2])
                i = end + 2
                continue
        # Single-quoted string literal
        if ch == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'":
                    if j + 1 < n and sql[j + 1] == "'":
                        j += 2
                        continue
                    else:
                        j += 1
                        break
                j += 1
            out.append(sql[i:j])
            i = j
            continue
        # Double-quoted identifier
        if ch == '"':
            j = i + 1
            while j < n:
                if sql[j] == '"':
                    if j + 1 < n and sql[j + 1] == '"':
                        j += 2
                        continue
                    else:
                        j += 1
                        break
                j += 1
            out.append(sql[i:j])
            i = j
            continue
        # Placeholder
        if ch == '?':
            out.append('%s')
            i += 1
            continue
        # Normal character
        out.append(ch)
        i += 1
    return "".join(out)


SQLITE_SCHEMA = """
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

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'traveler',
    home_city TEXT DEFAULT '',
    travel_style TEXT DEFAULT 'mid',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS destinations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT,
    tagline TEXT,
    description TEXT,
    best_season TEXT,
    avg_daily_budget INTEGER,
    tags TEXT
);
CREATE TABLE IF NOT EXISTS attractions (
    id SERIAL PRIMARY KEY,
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
    id SERIAL PRIMARY KEY,
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    name TEXT NOT NULL,
    cuisine TEXT,
    tier TEXT,
    cost_per_person INTEGER,
    rating REAL,
    description TEXT
);
CREATE TABLE IF NOT EXISTS hotels (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    name TEXT NOT NULL,
    tier TEXT,
    price_per_night INTEGER,
    rating REAL,
    amenities TEXT
);
CREATE TABLE IF NOT EXISTS transports (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    mode TEXT NOT NULL,
    cost_per_day INTEGER,
    unit TEXT,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS trip_members (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT DEFAULT 'editor',
    interests TEXT DEFAULT '[]',
    UNIQUE (trip_id, user_id)
);
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    destination_id INTEGER NOT NULL REFERENCES destinations(id),
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
"""

SCHEMA = SQLITE_SCHEMA  # Backward compatibility alias


class PostgresCursorWrapper:
    def __init__(self, cur, lastrowid=None):
        self.cur = cur
        self.lastrowid = lastrowid

    def fetchone(self):
        row = self.cur.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        rows = self.cur.fetchall()
        return [dict(r) for r in rows]

    def close(self):
        try:
            self.cur.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        for r in self.cur:
            yield dict(r)

    def __getattr__(self, name):
        return getattr(self.cur, name)


class PostgresConnectionWrapper:
    def __init__(self, raw_conn, pool_ref):
        self.raw_conn = raw_conn
        self.pool_ref = pool_ref

    def execute(self, sql, args=()):
        sql_adapted = adapt_sql_for_postgres(sql)
        cur = self.raw_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql_adapted, args)
        return PostgresCursorWrapper(cur)

    def commit(self):
        self.raw_conn.commit()

    def rollback(self):
        self.raw_conn.rollback()

    def close(self):
        if self.pool_ref is not None and self.raw_conn is not None:
            try:
                # If connection is marked closed or broken, discard it from pool
                if getattr(self.raw_conn, "closed", 0) != 0:
                    self.pool_ref.putconn(self.raw_conn, close=True)
                else:
                    self.pool_ref.putconn(self.raw_conn)
            except Exception:
                pass
            self.raw_conn = None


def get_pg_pool():
    global _pg_pool
    if _pg_pool is None:
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 is required for PostgreSQL support but is not installed.")
        url = get_database_url()
        try:
            # Configure pool with TCP keepalives to prevent idle cloud drops
            _pg_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=url,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=3,
            )
        except TypeError:
            _pg_pool = pool.ThreadedConnectionPool(minconn=1, maxconn=10, dsn=url)
    return _pg_pool


def close_pg_pool():
    global _pg_pool
    if _pg_pool is not None:
        try:
            _pg_pool.closeall()
        except Exception:
            pass
        _pg_pool = None


def get_conn():
    if is_postgres():
        p = get_pg_pool()
        raw = p.getconn()
        return PostgresConnectionWrapper(raw, p)
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
    if is_postgres():
        with db() as conn:
            with conn.raw_conn.cursor() as cur:
                cur.execute(POSTGRES_SCHEMA)
    else:
        conn = get_conn()
        conn.executescript(SQLITE_SCHEMA)
        conn.commit()
        conn.close()


def execute_insert(conn, sql, args=(), pk="id"):
    """
    Executes an INSERT statement and returns the generated primary key.
    Uses 'RETURNING pk' on PostgreSQL and 'cur.lastrowid' on SQLite.
    Guarantees cursors are closed reliably on both success and failure.
    """
    if is_postgres():
        sql_adapted = adapt_sql_for_postgres(sql)
        if "RETURNING" not in sql_adapted.upper():
            sql_adapted = f"{sql_adapted.rstrip().rstrip(';')} RETURNING {pk}"
        cur = conn.raw_conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(sql_adapted, args)
            row = cur.fetchone()
            return row[pk] if row else None
        finally:
            cur.close()
    else:
        cur = conn.execute(sql, args)
        return cur.lastrowid


def sync_sequences(conn):
    """
    Synchronizes PostgreSQL sequences to prevent duplicate key collisions
    after inserting records with explicit IDs.
    """
    if not is_postgres():
        return
    tables = [
        "users", "destinations", "attractions", "restaurants",
        "hotels", "transports", "trips", "trip_members", "reviews"
    ]
    with conn.raw_conn.cursor() as cur:
        for table in tables:
            sql = (
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1), "
                f"(SELECT MAX(id) IS NOT NULL FROM {table}))"
            )
            cur.execute(sql)


def q(conn, sql, args=()):
    cur = conn.execute(sql, args)
    try:
        return [dict(r) for r in cur.fetchall()]
    finally:
        if hasattr(cur, "close"):
            cur.close()


def q1(conn, sql, args=()):
    cur = conn.execute(sql, args)
    try:
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        if hasattr(cur, "close"):
            cur.close()


def loads(value, default=None):
    if value is None or value == "":
        return default
    if isinstance(value, (dict, list)):
        return value
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
