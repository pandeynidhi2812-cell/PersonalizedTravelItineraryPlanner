import json
import os
from datetime import date, datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from . import ai, planner, supabase_sync  # noqa: E402
from .auth import current_user, hash_password, make_token, verify_password  # noqa: E402
from .database import close_pg_pool, db, execute_insert, init_db, load_bundle, loads, q, q1  # noqa: E402
from .seed import seed_if_empty  # noqa: E402

app = FastAPI(title="Personalized Travel Itinerary Planner", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=([o.strip().rstrip("/") for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()] or ["http://localhost:5173", "http://127.0.0.1:5173"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STYLES = {"budget", "mid", "premium"}
PACES = {"relaxed", "balanced", "packed"}


@app.on_event("startup")
def startup():
    init_db()
    seed_if_empty()


@app.on_event("shutdown")
def shutdown():
    close_pg_pool()


# ---------- schemas ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=100)
    home_city: str = ""


class LoginIn(BaseModel):
    email: str
    password: str


class TripIn(BaseModel):
    title: str = Field(default="", max_length=120)
    destination_id: int
    start_date: date
    end_date: date
    travelers: int = Field(default=1, ge=1, le=20)
    budget: int = Field(default=20000, ge=500, le=10_000_000)
    style: str = "mid"
    pace: str = "balanced"
    interests: List[str] = []


class TripUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=120)
    itinerary: Optional[dict] = None
    budget: Optional[int] = Field(default=None, ge=500)


class MemberIn(BaseModel):
    email: str
    interests: List[str] = []


class ReviewIn(BaseModel):
    destination_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=500)


# ---------- helpers ----------
def _validate_trip(t: TripIn):
    if t.style not in STYLES:
        raise HTTPException(422, f"style must be one of {sorted(STYLES)}")
    if t.pace not in PACES:
        raise HTTPException(422, f"pace must be one of {sorted(PACES)}")
    if t.end_date < t.start_date:
        raise HTTPException(422, "End date must be on or after the start date")
    if planner.trip_days(t.start_date, t.end_date) > planner.MAX_DAYS:
        raise HTTPException(422, f"Trips are limited to {planner.MAX_DAYS} days")


def _trip_access(conn, trip_id, user):
    row = q1(conn, "SELECT * FROM trips WHERE id = ?", (trip_id,))
    if not row:
        raise HTTPException(404, "Trip not found")
    if row["owner_id"] == user["id"]:
        return row, "owner"
    m = q1(conn, "SELECT role FROM trip_members WHERE trip_id = ? AND user_id = ?", (trip_id, user["id"]))
    if m:
        return row, m["role"]
    raise HTTPException(403, "You do not have access to this trip")


def _params(conn, row):
    """Planner parameters; interests are the union of the owner's and every member's interests."""
    interests = set(loads(row["interests"], []))
    for m in q(conn, "SELECT interests FROM trip_members WHERE trip_id = ?", (row["id"],)):
        interests |= set(loads(m["interests"], []))
    return {
        "start_date": planner.to_date(row["start_date"]),
        "end_date": planner.to_date(row["end_date"]),
        "travelers": row["travelers"],
        "budget": row["budget"],
        "style": row["style"],
        "pace": row["pace"],
        "interests": sorted(interests),
    }


def _format_ts(val):
    if not val:
        return ""
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def _trip_out(conn, row, role, full=True):
    t = dict(row)
    t["interests"] = loads(t["interests"], [])
    itin = loads(t.pop("itinerary"), None)
    if "created_at" in t:
        t["created_at"] = _format_ts(t["created_at"])
    if "updated_at" in t:
        t["updated_at"] = _format_ts(t["updated_at"])
    dest = q1(conn, "SELECT name, state FROM destinations WHERE id = ?", (t["destination_id"],))
    owner = q1(conn, "SELECT name, email FROM users WHERE id = ?", (t["owner_id"],))
    t["destination_name"] = dest["name"]
    t["destination_state"] = dest["state"]
    t["owner_name"] = owner["name"]
    t["owner_email"] = owner["email"]
    t["role"] = role
    t["days"] = planner.trip_days(t["start_date"], t["end_date"])
    t["budget_status"] = (itin or {}).get("budget_status")
    if full:
        t["itinerary"] = itin
        members = q(conn, "SELECT u.id, u.name, u.email, m.role, m.interests FROM trip_members m "
                          "JOIN users u ON u.id = m.user_id WHERE m.trip_id = ?", (t["id"],))
        for m in members:
            m["interests"] = loads(m["interests"], [])
        t["members"] = members
    return t


def _save_itinerary(conn, trip_id, itin):
    conn.execute("UPDATE trips SET itinerary = ?, total_cost = ?, updated_at = ? WHERE id = ?",
                 (json.dumps(itin), itin["total_cost"], datetime.now(timezone.utc).isoformat(timespec="seconds"), trip_id))


def _mirror(conn, trip_id, user):
    row, role = _trip_access(conn, trip_id, user)
    t = _trip_out(conn, row, role)
    supabase_sync.mirror_trip(t)


# ---------- health ----------
@app.get("/api/health")
def health():
    return {"status": "ok", "llm_enabled": ai.llm_enabled(), "supabase_enabled": supabase_sync.enabled()}


# ---------- auth ----------
@app.post("/api/auth/register")
def register(body: RegisterIn):
    email = body.email.strip().lower()
    if "@" not in email:
        raise HTTPException(422, "Enter a valid email address")
    with db() as conn:
        if q1(conn, "SELECT id FROM users WHERE email = ?", (email,)):
            raise HTTPException(409, "An account with this email already exists")
        user_id = execute_insert(conn, "INSERT INTO users (name, email, password_hash, home_city) VALUES (?,?,?,?)",
                           (body.name.strip(), email, hash_password(body.password), body.home_city.strip()))
        user = q1(conn, "SELECT id, name, email, role, home_city, travel_style FROM users WHERE id = ?", (user_id,))
    return {"token": make_token(user["id"]), "user": user}


@app.post("/api/auth/login")
def login(body: LoginIn):
    with db() as conn:
        row = q1(conn, "SELECT * FROM users WHERE email = ?", (body.email.strip().lower(),))
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, "Incorrect email or password")
    user = {k: row[k] for k in ("id", "name", "email", "role", "home_city", "travel_style")}
    return {"token": make_token(user["id"]), "user": user}


@app.get("/api/auth/me")
def me(user=Depends(current_user)):
    return user


# ---------- destinations ----------
@app.get("/api/destinations")
def destinations():
    with db() as conn:
        rows = q(conn, "SELECT d.*, "
                       "(SELECT ROUND(AVG(rating), 1) FROM reviews r WHERE r.destination_id = d.id) AS avg_rating, "
                       "(SELECT COUNT(*) FROM reviews r WHERE r.destination_id = d.id) AS review_count, "
                       "(SELECT COUNT(*) FROM attractions a WHERE a.destination_id = d.id) AS attraction_count "
                       "FROM destinations d ORDER BY d.name")
    for r in rows:
        r["tags"] = loads(r["tags"], [])
    return rows


@app.get("/api/destinations/{dest_id}")
def destination_detail(dest_id: int):
    with db() as conn:
        bundle = load_bundle(conn, dest_id)
        if not bundle:
            raise HTTPException(404, "Destination not found")
        reviews = q(conn, "SELECT r.id, r.rating, r.comment, r.created_at, u.name AS user_name FROM reviews r "
                          "JOIN users u ON u.id = r.user_id WHERE r.destination_id = ? ORDER BY r.id DESC", (dest_id,))
    return {**bundle["destination"], "attractions": bundle["attractions"], "restaurants": bundle["restaurants"],
            "hotels": bundle["hotels"], "transports": bundle["transports"], "reviews": reviews}


@app.post("/api/reviews")
def add_review(body: ReviewIn, user=Depends(current_user)):
    with db() as conn:
        if not q1(conn, "SELECT id FROM destinations WHERE id = ?", (body.destination_id,)):
            raise HTTPException(404, "Destination not found")
        conn.execute("INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES (?,?,?,?)",
                     (user["id"], body.destination_id, body.rating, body.comment.strip()))
    return {"ok": True}


# ---------- trips ----------
@app.get("/api/trips")
def list_trips(user=Depends(current_user)):
    with db() as conn:
        rows = q(conn, "SELECT t.* FROM trips t WHERE t.owner_id = ? OR t.id IN "
                       "(SELECT trip_id FROM trip_members WHERE user_id = ?) ORDER BY t.start_date", (user["id"], user["id"]))
        out = []
        for r in rows:
            role = "owner" if r["owner_id"] == user["id"] else "editor"
            out.append(_trip_out(conn, r, role, full=False))
    return out


@app.post("/api/trips")
def create_trip(body: TripIn, user=Depends(current_user)):
    _validate_trip(body)
    with db() as conn:
        bundle = load_bundle(conn, body.destination_id)
        if not bundle:
            raise HTTPException(404, "Destination not found")
        title = body.title.strip() or f"{bundle['destination']['name']} trip"
        interests = [i.strip().lower() for i in body.interests if i.strip()]
        p = {"start_date": body.start_date, "end_date": body.end_date, "travelers": body.travelers,
             "budget": body.budget, "style": body.style, "pace": body.pace, "interests": interests}
        itin = planner.generate_itinerary(bundle, p, seed=0)
        itin["overview"], itin["tips"] = ai.narrate(bundle, p, itin)
        trip_id = execute_insert(
            conn,
            "INSERT INTO trips (owner_id, destination_id, title, start_date, end_date, travelers, budget, style, pace, "
            "interests, itinerary, total_cost) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (user["id"], body.destination_id, title, body.start_date.isoformat(), body.end_date.isoformat(),
             body.travelers, body.budget, body.style, body.pace, json.dumps(interests), json.dumps(itin), itin["total_cost"]))
        # trip_id obtained via execute_insert
    with db() as conn:
        _mirror(conn, trip_id, user)
        row, role = _trip_access(conn, trip_id, user)
        return _trip_out(conn, row, role)


@app.get("/api/trips/{trip_id}")
def get_trip(trip_id: int, user=Depends(current_user)):
    with db() as conn:
        row, role = _trip_access(conn, trip_id, user)
        return _trip_out(conn, row, role)


@app.put("/api/trips/{trip_id}")
def update_trip(trip_id: int, body: TripUpdate, user=Depends(current_user)):
    with db() as conn:
        row, role = _trip_access(conn, trip_id, user)
        if body.title is not None and body.title.strip():
            conn.execute("UPDATE trips SET title = ? WHERE id = ?", (body.title.strip(), trip_id))
        budget = body.budget if body.budget is not None else row["budget"]
        if body.budget is not None and role == "owner":
            conn.execute("UPDATE trips SET budget = ? WHERE id = ?", (budget, trip_id))
        if body.itinerary is not None:
            itin = body.itinerary
            if not isinstance(itin.get("days"), list):
                raise HTTPException(422, "Itinerary must contain a list of days")
            for d in itin["days"]:
                if not isinstance(d.get("activities"), list):
                    raise HTTPException(422, "Each day must contain a list of activities")
                for a in d["activities"]:
                    a["title"] = str(a.get("title", "Activity"))[:120]
                    a["time"] = str(a.get("time", "12:00"))[:5]
                    try:
                        a["cost"] = max(0, int(a.get("cost") or 0))
                    except (TypeError, ValueError):
                        a["cost"] = 0
            planner.recompute(itin, budget, row["travelers"])
            _save_itinerary(conn, trip_id, itin)
        conn.execute("UPDATE trips SET updated_at = ? WHERE id = ?", (datetime.now(timezone.utc).isoformat(timespec="seconds"), trip_id))
    with db() as conn:
        _mirror(conn, trip_id, user)
        row, role = _trip_access(conn, trip_id, user)
        return _trip_out(conn, row, role)


@app.delete("/api/trips/{trip_id}")
def delete_trip(trip_id: int, user=Depends(current_user)):
    with db() as conn:
        row, role = _trip_access(conn, trip_id, user)
        if role != "owner":
            raise HTTPException(403, "Only the trip owner can delete it")
        conn.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    supabase_sync.delete_trip(trip_id)
    return {"ok": True}


@app.post("/api/trips/{trip_id}/regenerate")
def regenerate_trip(trip_id: int, user=Depends(current_user)):
    with db() as conn:
        row, role = _trip_access(conn, trip_id, user)
        bundle = load_bundle(conn, row["destination_id"])
        p = _params(conn, row)
        seed = (row["seed"] or 0) + 1
        itin = planner.generate_itinerary(bundle, p, seed=seed)
        itin["overview"], itin["tips"] = ai.narrate(bundle, p, itin)
        _save_itinerary(conn, trip_id, itin)
        conn.execute("UPDATE trips SET seed = ? WHERE id = ?", (seed, trip_id))
    with db() as conn:
        _mirror(conn, trip_id, user)
        row, role = _trip_access(conn, trip_id, user)
        return _trip_out(conn, row, role)


@app.post("/api/trips/{trip_id}/days/{day_no}/regenerate")
def regenerate_day(trip_id: int, day_no: int, user=Depends(current_user)):
    with db() as conn:
        row, role = _trip_access(conn, trip_id, user)
        itin = loads(row["itinerary"], None)
        if not itin or not (1 <= day_no <= len(itin["days"])):
            raise HTTPException(404, "Day not found")
        bundle = load_bundle(conn, row["destination_id"])
        p = _params(conn, row)
        seed = (row["seed"] or 0) + 1
        itin = planner.regenerate_day(bundle, p, itin, day_no, seed)
        _save_itinerary(conn, trip_id, itin)
        conn.execute("UPDATE trips SET seed = ? WHERE id = ?", (seed, trip_id))
    with db() as conn:
        _mirror(conn, trip_id, user)
        row, role = _trip_access(conn, trip_id, user)
        return _trip_out(conn, row, role)


@app.post("/api/trips/{trip_id}/members")
def add_member(trip_id: int, body: MemberIn, user=Depends(current_user)):
    with db() as conn:
        row, role = _trip_access(conn, trip_id, user)
        if role != "owner":
            raise HTTPException(403, "Only the trip owner can add travellers")
        target = q1(conn, "SELECT id FROM users WHERE email = ?", (body.email.strip().lower(),))
        if not target:
            raise HTTPException(404, "No account with that email. Ask them to register first.")
        if target["id"] == row["owner_id"]:
            raise HTTPException(409, "That is the trip owner")
        if q1(conn, "SELECT id FROM trip_members WHERE trip_id = ? AND user_id = ?", (trip_id, target["id"])):
            raise HTTPException(409, "Already a member of this trip")
        interests = [i.strip().lower() for i in body.interests if i.strip()]
        conn.execute("INSERT INTO trip_members (trip_id, user_id, role, interests) VALUES (?,?,?,?)",
                     (trip_id, target["id"], "editor", json.dumps(interests)))
        row, role = _trip_access(conn, trip_id, user)
        return _trip_out(conn, row, role)


@app.delete("/api/trips/{trip_id}/members/{member_id}")
def remove_member(trip_id: int, member_id: int, user=Depends(current_user)):
    with db() as conn:
        row, role = _trip_access(conn, trip_id, user)
        if role != "owner" and member_id != user["id"]:
            raise HTTPException(403, "Only the owner can remove other travellers")
        conn.execute("DELETE FROM trip_members WHERE trip_id = ? AND user_id = ?", (trip_id, member_id))
        row, role = _trip_access(conn, trip_id, user) if role == "owner" else (None, None)
        return _trip_out(conn, row, role) if row else {"ok": True}


# ---------- dashboard ----------
@app.get("/api/dashboard")
def dashboard(user=Depends(current_user)):
    today = date.today().isoformat()
    with db() as conn:
        rows = q(conn, "SELECT t.* FROM trips t WHERE t.owner_id = ? OR t.id IN "
                       "(SELECT trip_id FROM trip_members WHERE user_id = ?) ORDER BY t.start_date", (user["id"], user["id"]))
        trips = [_trip_out(conn, r, "owner" if r["owner_id"] == user["id"] else "editor", full=False) for r in rows]
        dest_count = q1(conn, "SELECT COUNT(*) AS c FROM destinations")["c"]
    upcoming = [t for t in trips if t["end_date"] >= today]
    return {
        "stats": {
            "total_trips": len(trips),
            "upcoming_trips": len(upcoming),
            "estimated_spend": sum(t["total_cost"] or 0 for t in trips),
            "shared_trips": sum(1 for t in trips if t["role"] != "owner"),
            "destinations_available": dest_count,
        },
        "next_trip": upcoming[0] if upcoming else None,
        "recent": sorted(trips, key=lambda t: _format_ts(t.get("updated_at")), reverse=True)[:5],
    }
