import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse

# Inspect environment variables before importing any app modules
raw_test_pg_url = os.getenv("TEST_DATABASE_URL", "").strip()
raw_prod_pg_url = os.getenv("DATABASE_URL", "").strip()

temp_dir = None
test_db_path = None


def _normalize_db_url(url: str) -> str:
    """Normalizes postgresql/postgres URLs for safe comparison without leaking credentials."""
    if not url:
        return ""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    parsed = urlparse(url)
    # Strip user/password for comparison and diagnostics
    return f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 5432}{parsed.path}"


if raw_test_pg_url:
    # Validate test database URL
    if not (raw_test_pg_url.startswith("postgres://") or raw_test_pg_url.startswith("postgresql://")):
        raise RuntimeError("ABORT: TEST_DATABASE_URL must be a valid PostgreSQL connection string.")

    # Guard: Fail closed if TEST_DATABASE_URL matches DATABASE_URL
    if raw_prod_pg_url:
        norm_test = _normalize_db_url(raw_test_pg_url)
        norm_prod = _normalize_db_url(raw_prod_pg_url)
        if norm_test == norm_prod:
            raise RuntimeError(
                "ABORT: TEST_DATABASE_URL matches production DATABASE_URL. "
                "Tests refuse to run against the production database."
            )

    os.environ["DATABASE_URL"] = raw_test_pg_url
else:
    # Force DATABASE_URL to empty string BEFORE importing any app/database modules
    # This prevents load_dotenv or ambient shell variables from activating PostgreSQL in tests
    os.environ["DATABASE_URL"] = ""
    temp_dir = tempfile.mkdtemp(prefix="tripora_test_")
    test_db_path = os.path.join(temp_dir, "test_travel.db")
    os.environ["DB_PATH"] = test_db_path

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.database
if test_db_path:
    app.database.DB_PATH = test_db_path

from starlette.testclient import TestClient
from app.database import (
    adapt_sql_for_postgres,
    close_pg_pool,
    db,
    execute_insert,
    init_db,
    is_postgres,
    q,
    q1,
)
from app.main import _format_ts, app, startup
from app.seed import seed_if_empty


class TestTravelApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initializes and seeds the isolated test database
        startup()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Clean up pool or temporary files
        close_pg_pool()
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def test_01_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("llm_enabled", data)
        self.assertIn("supabase_enabled", data)

    def test_02_login_demo_user(self):
        res = self.client.post("/api/auth/login", json={
            "email": "aarav@example.com",
            "password": "Aarav@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], "aarav@example.com")
        token = data["token"]

        # Check /api/auth/me
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["name"], "Aarav Sharma")

    def test_03_registration_and_generated_ids(self):
        # Register a new user
        reg_payload = {
            "name": "Dev Traveler",
            "email": "dev.traveler@tripora.test",
            "password": "SecurePassword123",
            "home_city": "Bengaluru"
        }
        res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        user = data["user"]
        # Seeded users are 1..7; the new registered user must have an ID >= 8
        self.assertGreaterEqual(user["id"], 8)
        self.assertEqual(user["email"], "dev.traveler@tripora.test")

        # Verify token works for /api/auth/me
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {data['token']}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], "dev.traveler@tripora.test")

        # Duplicate registration should return 409 Conflict
        dup_res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(dup_res.status_code, 409)

    def test_04_destinations(self):
        res = self.client.get("/api/destinations")
        self.assertEqual(res.status_code, 200)
        destinations = res.json()
        self.assertGreaterEqual(len(destinations), 7)
        goa = next(d for d in destinations if d["name"] == "Goa")
        self.assertIn("avg_daily_budget", goa)

        detail_res = self.client.get(f"/api/destinations/{goa['id']}")
        self.assertEqual(detail_res.status_code, 200)
        detail = detail_res.json()
        self.assertIn("attractions", detail)
        self.assertIn("restaurants", detail)
        self.assertIn("hotels", detail)
        self.assertIn("transports", detail)

    def test_05_trip_lifecycle(self):
        # 1. Login as Aarav
        login_res = self.client.post("/api/auth/login", json={
            "email": "aarav@example.com",
            "password": "Aarav@123"
        })
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create trip
        today = date.today()
        start = today + timedelta(days=10)
        end = today + timedelta(days=12)
        trip_payload = {
            "destination_id": 1,
            "title": "Weekend in Goa Test",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "travelers": 2,
            "budget": 25000,
            "style": "mid",
            "pace": "balanced",
            "interests": ["beach", "food"]
        }
        res = self.client.post("/api/trips", json=trip_payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        trip = res.json()
        trip_id = trip["id"]
        self.assertGreaterEqual(trip_id, 1)
        self.assertEqual(trip["title"], "Weekend in Goa Test")
        self.assertIn("itinerary", trip)
        self.assertEqual(len(trip["itinerary"]["days"]), 3)
        self.assertIn("overview", trip["itinerary"])
        self.assertIn("tips", trip["itinerary"])

        # 3. View trip
        get_res = self.client.get(f"/api/trips/{trip_id}", headers=headers)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["id"], trip_id)

        # 4. Update trip
        update_res = self.client.put(f"/api/trips/{trip_id}", json={
            "title": "Updated Goa Trip",
            "budget": 28000
        }, headers=headers)
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["title"], "Updated Goa Trip")
        self.assertEqual(update_res.json()["budget"], 28000)

        # 5. Regenerate single day
        day_regen = self.client.post(f"/api/trips/{trip_id}/days/1/regenerate", headers=headers)
        self.assertEqual(day_regen.status_code, 200)

        # 6. Regenerate full trip
        full_regen = self.client.post(f"/api/trips/{trip_id}/regenerate", headers=headers)
        self.assertEqual(full_regen.status_code, 200)

        # 7. Add member (invite Rohan)
        add_member_res = self.client.post(f"/api/trips/{trip_id}/members", json={
            "email": "rohan@example.com",
            "interests": ["photography"]
        }, headers=headers)
        self.assertEqual(add_member_res.status_code, 200)
        members = add_member_res.json()["members"]
        rohan_member = next(m for m in members if m["email"] == "rohan@example.com")
        self.assertIsNotNone(rohan_member)

        # 8. Remove member
        del_member_res = self.client.delete(f"/api/trips/{trip_id}/members/{rohan_member['id']}", headers=headers)
        self.assertEqual(del_member_res.status_code, 200)

        # 9. Check dashboard stats
        dash_res = self.client.get("/api/dashboard", headers=headers)
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.json()
        self.assertIn("stats", dash_data)
        self.assertIn("recent", dash_data)
        self.assertIsInstance(dash_data["recent"], list)

        # 10. Delete trip
        del_res = self.client.delete(f"/api/trips/{trip_id}", headers=headers)
        self.assertEqual(del_res.status_code, 200)

        # 11. Confirm deleted
        get_deleted = self.client.get(f"/api/trips/{trip_id}", headers=headers)
        self.assertEqual(get_deleted.status_code, 404)

    def test_06_database_persistence_across_connections(self):
        # Write record in connection 1
        with db() as conn1:
            dest = q1(conn1, "SELECT id FROM destinations WHERE name = ?", ("Goa",))
            self.assertIsNotNone(dest)
            review_id = execute_insert(
                conn1,
                "INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES (?,?,?,?)",
                (2, dest["id"], 5, "Persistence test review: sunset was brilliant!")
            )
            self.assertIsNotNone(review_id)

        # Read back in a completely separate connection 2
        with db() as conn2:
            fetched = q1(conn2, "SELECT * FROM reviews WHERE id = ?", (review_id,))
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched["rating"], 5)
            self.assertIn("Persistence test review", fetched["comment"])

    def test_07_transaction_rollback(self):
        # Attempt an operation that raises an exception before commit
        test_email = "rollback_candidate@tripora.test"
        try:
            with db() as conn:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash, home_city) VALUES (?,?,?,?)",
                    ("Rollback User", test_email, "hash123", "Jaipur")
                )
                raise RuntimeError("Simulated transaction abort")
        except RuntimeError:
            pass

        # In a new connection, verify the uncommitted row was rolled back
        with db() as conn2:
            found = q1(conn2, "SELECT id FROM users WHERE email = ?", (test_email,))
            self.assertIsNone(found, "Uncommitted transaction changes must be rolled back on failure")

    def test_08_repeatable_schema_and_seed_initialization(self):
        # Running init_db and seed_if_empty again must be safe and idempotent
        init_db()
        seeded_again = seed_if_empty()
        # Should return False because database is already seeded
        self.assertFalse(seeded_again)

        # Verify data counts are preserved
        with db() as conn:
            user_count = q1(conn, "SELECT COUNT(*) AS c FROM users")["c"]
            dest_count = q1(conn, "SELECT COUNT(*) AS c FROM destinations")["c"]
            # At least 7 demo users + 1 registered user = 8
            self.assertGreaterEqual(user_count, 8)
            self.assertEqual(dest_count, 7)

    def test_09_sql_adapter_unit_tests(self):
        # 1. Standard query
        sql1 = "SELECT * FROM trips WHERE id = ? AND budget > ?"
        self.assertEqual(adapt_sql_for_postgres(sql1), "SELECT * FROM trips WHERE id = %s AND budget > %s")

        # 2. String literal containing a question mark
        sql2 = "SELECT * FROM destinations WHERE name = 'Where to go?' AND id = ?"
        self.assertEqual(adapt_sql_for_postgres(sql2), "SELECT * FROM destinations WHERE name = 'Where to go?' AND id = %s")

        # 3. Escaped single quotes inside literal
        sql3 = "SELECT * FROM reviews WHERE comment = 'Isn''t this great?' AND rating = ?"
        self.assertEqual(adapt_sql_for_postgres(sql3), "SELECT * FROM reviews WHERE comment = 'Isn''t this great?' AND rating = %s")

        # 4. Line comment containing a question mark
        sql4 = "-- Is this query safe?\nSELECT id FROM users WHERE email = ?"
        self.assertEqual(adapt_sql_for_postgres(sql4), "-- Is this query safe?\nSELECT id FROM users WHERE email = %s")

        # 5. Block comment containing a question mark
        sql5 = "/* Why not? */ SELECT id FROM users WHERE id = ?"
        self.assertEqual(adapt_sql_for_postgres(sql5), "/* Why not? */ SELECT id FROM users WHERE id = %s")

        # 6. Double-quoted identifier
        sql6 = 'SELECT "col?name" FROM trips WHERE id = ?'
        self.assertEqual(adapt_sql_for_postgres(sql6), 'SELECT "col?name" FROM trips WHERE id = %s')

    def test_10_timestamp_sorting_normalization(self):
        # Verify _format_ts correctly handles timezone-aware datetime, naive datetime, strings, and empty/None
        dt_tz = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
        dt_naive = datetime(2026, 10, 28, 11, 0, 0)
        str_ts = "2026-10-28T10:00:00"

        # Conversion to ISO strings
        self.assertEqual(_format_ts(dt_tz), "2026-10-28T12:00:00+00:00")
        self.assertEqual(_format_ts(dt_naive), "2026-10-28T11:00:00")
        self.assertEqual(_format_ts(str_ts), "2026-10-28T10:00:00")
        self.assertEqual(_format_ts(None), "")
        self.assertEqual(_format_ts(""), "")

        # Mixed collection sorting without throwing TypeError
        sample_trips = [
            {"id": 1, "updated_at": None},
            {"id": 2, "updated_at": dt_tz},
            {"id": 3, "updated_at": str_ts},
            {"id": 4, "updated_at": dt_naive},
            {"id": 5, "updated_at": ""},
        ]
        sorted_trips = sorted(sample_trips, key=lambda t: _format_ts(t.get("updated_at")), reverse=True)
        # Verify order: dt_tz (12:00) -> dt_naive (11:00) -> str_ts (10:00) -> None/empty
        self.assertEqual([t["id"] for t in sorted_trips[:3]], [2, 4, 3])

    def test_11_test_database_isolation_guards(self):
        # Verify isolation: when TEST_DATABASE_URL is absent, is_postgres() must be False in test environment
        if not raw_test_pg_url:
            self.assertFalse(is_postgres())
            self.assertIsNotNone(test_db_path)
            self.assertTrue(test_db_path.endswith("test_travel.db"))


if __name__ == "__main__":
    unittest.main()
