import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta

# Set up an isolated temporary database BEFORE any app modules are imported
temp_dir = tempfile.mkdtemp(prefix="tripora_test_")
test_db_path = os.path.join(temp_dir, "test_travel.db")
os.environ["DB_PATH"] = test_db_path

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Explicitly ensure app.database binds to the isolated test database
import app.database
app.database.DB_PATH = test_db_path

from starlette.testclient import TestClient
from app.main import app, startup


class TestTravelApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initializes and seeds the isolated temporary test database
        startup()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary test database and directory completely
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

    def test_03_destinations(self):
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

    def test_04_trip_lifecycle(self):
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
            "title": "Updated Goa Trip"
        }, headers=headers)
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["title"], "Updated Goa Trip")

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
        self.assertIn("stats", dash_res.json())

        # 10. Delete trip
        del_res = self.client.delete(f"/api/trips/{trip_id}", headers=headers)
        self.assertEqual(del_res.status_code, 200)

        # 11. Confirm deleted
        get_deleted = self.client.get(f"/api/trips/{trip_id}", headers=headers)
        self.assertEqual(get_deleted.status_code, 404)


if __name__ == "__main__":
    unittest.main()
