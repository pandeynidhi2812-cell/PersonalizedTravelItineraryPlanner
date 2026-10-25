import json
from datetime import date

from . import ai
from .auth import hash_password
from .database import init_db, db, q, q1, load_bundle
from .planner import generate_itinerary
from . import seed_data as S


def seed_if_empty():
    init_db()
    with db() as conn:
        if q1(conn, "SELECT COUNT(*) AS c FROM users")["c"] > 0:
            return False

        for uid, name, email, pw, role, city, style in S.USERS:
            conn.execute("INSERT INTO users (id, name, email, password_hash, role, home_city, travel_style) VALUES (?,?,?,?,?,?,?)",
                         (uid, name, email, hash_password(pw), role, city, style))
        for did, name, state, tagline, desc, season, budget, tags in S.DESTINATIONS:
            conn.execute("INSERT INTO destinations (id, name, state, tagline, description, best_season, avg_daily_budget, tags) VALUES (?,?,?,?,?,?,?,?)",
                         (did, name, state, tagline, desc, season, budget, json.dumps(tags)))
        for did, name, tags, fee, dur, slot, area, desc in S.ATTRACTIONS:
            conn.execute("INSERT INTO attractions (destination_id, name, tags, entry_fee, duration_min, best_slot, area, description) VALUES (?,?,?,?,?,?,?,?)",
                         (did, name, json.dumps(tags), fee, dur, slot, area, desc))
        for row in S.RESTAURANTS:
            conn.execute("INSERT INTO restaurants (destination_id, name, cuisine, tier, cost_per_person, rating, description) VALUES (?,?,?,?,?,?,?)", row)
        for did, name, tier, price, rating, amen in S.HOTELS:
            conn.execute("INSERT INTO hotels (destination_id, name, tier, price_per_night, rating, amenities) VALUES (?,?,?,?,?,?)",
                         (did, name, tier, price, rating, json.dumps(amen)))
        for row in S.TRANSPORTS:
            conn.execute("INSERT INTO transports (destination_id, mode, cost_per_day, unit, notes) VALUES (?,?,?,?,?)", row)
        for uid, did, rating, comment in S.REVIEWS:
            conn.execute("INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES (?,?,?,?)", (uid, did, rating, comment))

        for title, owner, did, start, end, travelers, budget, style, pace, interests in S.TRIPS:
            p = {"start_date": date.fromisoformat(start), "end_date": date.fromisoformat(end), "travelers": travelers,
                 "budget": budget, "style": style, "pace": pace, "interests": interests}
            bundle = load_bundle(conn, did)
            itin = generate_itinerary(bundle, p, seed=0)
            itin["overview"], itin["tips"] = ai.narrate(bundle, p, itin, use_llm=False)
            conn.execute(
                "INSERT INTO trips (owner_id, destination_id, title, start_date, end_date, travelers, budget, style, pace, interests, itinerary, total_cost) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (owner, did, title, start, end, travelers, budget, style, pace, json.dumps(interests), json.dumps(itin), itin["total_cost"]))
        trip_ids = [r["id"] for r in q(conn, "SELECT id FROM trips ORDER BY id")]
        for idx, uid, role, interests in S.TRIP_MEMBERS:
            conn.execute("INSERT INTO trip_members (trip_id, user_id, role, interests) VALUES (?,?,?,?)",
                         (trip_ids[idx - 1], uid, role, json.dumps(interests)))
    return True
