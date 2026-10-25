"""
Optional Supabase integration.

When SUPABASE_URL and SUPABASE_KEY are set, every saved trip is mirrored to the `trips` table in
your Supabase project (see ../supabase_schema.sql). The local SQLite database stays the primary
store, so the app works with or without Supabase. Failures never break a request.
"""
import os

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()


def enabled():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def _headers(extra=None):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    h.update(extra or {})
    return h


def mirror_trip(trip):
    if not enabled():
        return False
    row = {
        "id": trip["id"],
        "owner_email": trip.get("owner_email"),
        "title": trip["title"],
        "destination": trip.get("destination_name"),
        "start_date": trip["start_date"],
        "end_date": trip["end_date"],
        "travelers": trip["travelers"],
        "budget": trip["budget"],
        "style": trip["style"],
        "pace": trip["pace"],
        "interests": trip["interests"],
        "itinerary": trip.get("itinerary"),
        "total_cost": trip.get("total_cost", 0),
    }
    try:
        r = httpx.post(f"{SUPABASE_URL}/rest/v1/trips", json=row, timeout=10,
                       headers=_headers({"Prefer": "resolution=merge-duplicates,return=minimal"}))
        return r.status_code < 300
    except Exception:
        return False


def delete_trip(trip_id):
    if not enabled():
        return False
    try:
        r = httpx.delete(f"{SUPABASE_URL}/rest/v1/trips?id=eq.{int(trip_id)}", timeout=10, headers=_headers())
        return r.status_code < 300
    except Exception:
        return False
