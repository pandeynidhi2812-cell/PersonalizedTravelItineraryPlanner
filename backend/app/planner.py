"""
Itinerary engine.

Deterministic, budget-aware planning:
  * scores attractions against the traveller's interests
  * clusters each day around one area to cut travel time
  * orders activities by best time of day
  * adds meals, local transport and hotel stay with real cost maths
  * if the plan exceeds the budget it automatically steps down a tier (premium -> mid -> budget)

The optional LLM layer (see ai.py) only writes the overview text and tips on top of this plan.
"""
import math
import random
import uuid
from datetime import date, timedelta

TIERS = ["budget", "mid", "premium"]
PACE_N = {"relaxed": 2, "balanced": 3, "packed": 4}
SLOT_RANK = {"morning": 0, "afternoon": 1, "evening": 2}
TIMES = {
    1: ["11:00"],
    2: ["10:30", "16:00"],
    3: ["09:30", "14:30", "17:30"],
    4: ["09:00", "11:30", "15:00", "17:45"],
}
MAX_DAYS = 14


SLOT_MIN = {"morning": 9 * 60, "afternoon": 13 * 60 + 30, "evening": 17 * 60 + 30}


def _fmt(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _schedule(items):
    """Start times that respect each attraction's best time of day and never overlap."""
    base = TIMES[max(1, min(4, len(items)))]
    out, prev_end = [], 0
    for (kind, a), t in zip(items, base):
        mins = int(t[:2]) * 60 + int(t[3:])
        slot = a["best_slot"] if a else "afternoon"
        mins = max(mins, SLOT_MIN.get(slot, 0), prev_end + 30)
        out.append(_fmt(mins))
        prev_end = mins + (a["duration_min"] if a else 60)
    return out


def _id():
    return uuid.uuid4().hex[:8]


def to_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def trip_days(start, end):
    return (to_date(end) - to_date(start)).days + 1


def _pick_hotel(bundle, style):
    hotels = bundle["hotels"]
    for h in hotels:
        if h["tier"] == style:
            return h
    return hotels[0]


def _pick_transport(bundle, style, travelers):
    ts = sorted(bundle["transports"], key=lambda t: t["cost_per_day"])
    if style == "budget" or (style == "mid" and travelers == 1):
        return ts[0]
    return ts[-1]


def _transport_cost(t, travelers):
    if t["unit"] == "per_vehicle":
        return t["cost_per_day"] * math.ceil(travelers / 4)
    return t["cost_per_day"] * travelers


def _act(time, kind, title, description, cost, duration, location, ref_id=None):
    return {
        "id": _id(),
        "time": time,
        "type": kind,
        "title": title,
        "description": description,
        "cost": int(round(cost)),
        "duration_min": duration,
        "location": location,
        "ref_id": ref_id,
    }


def plan_day(bundle, p, style, d, days, exclude, rng, hotel, transport):
    """Build one day (d is zero based)."""
    travelers = p["travelers"]
    interests = set(p["interests"])
    day_date = to_date(p["start_date"]) + timedelta(days=d)
    rooms = math.ceil(travelers / 2)

    target = PACE_N[p["pace"]]
    if days > 1 and target > 2 and d in (0, days - 1):
        target -= 1  # arrival / departure days are lighter

    scores = {a["id"]: 1 + 3 * len(interests & set(a["tags"])) + rng.random() * 0.8 for a in bundle["attractions"]}
    pool = sorted([a for a in bundle["attractions"] if a["id"] not in exclude], key=lambda a: -scores[a["id"]])

    if not pool:
        pool = sorted(bundle["attractions"], key=lambda a: -scores[a["id"]])
    chosen = []
    if pool:
        anchor = pool[0]
        chosen = [anchor]
        used_slots = {anchor["best_slot"]}
        remaining = pool[1:]
        while len(chosen) < target and remaining:
            nxt = min(remaining, key=lambda a: ((a["best_slot"] in used_slots) * 2 + (a["area"] != anchor["area"]),
                                                -scores[a["id"]]))
            chosen.append(nxt)
            used_slots.add(nxt["best_slot"])
            remaining.remove(nxt)
    chosen.sort(key=lambda a: SLOT_RANK.get(a["best_slot"], 1))

    items = [("attraction", a) for a in chosen]
    if len(items) < target:
        items.append(("free", None))  # at most one free-time block per day

    times = _schedule(items)
    acts = []

    # Arrival
    if d == 0:
        acts.append(_act("07:30", "stay", f"Arrive in {bundle['destination']['name']}",
                         "Reach the city, drop your bags and freshen up.", 0, 30, bundle["destination"]["name"]))

    # Breakfast
    breakfast_included = any("Breakfast included" in x for x in hotel["amenities"])
    acts.append(_act("08:30" if d == 0 else "08:00", "meal", f"Breakfast at {hotel['name']}",
                     "Included with your stay." if breakfast_included else "Simple breakfast near the hotel.",
                     0 if breakfast_included else 150 * travelers, 45, hotel["name"]))

    # Local transport for the day
    acts.append(_act("08:45", "transport", f"Local transport: {transport['mode']}",
                     transport["notes"], _transport_cost(transport, travelers), 0, bundle["destination"]["name"]))

    # Attractions / free time
    for (kind, a), t in zip(items, times):
        if kind == "attraction":
            acts.append(_act(t, "attraction", a["name"], a["description"], a["entry_fee"] * travelers,
                             a["duration_min"], a["area"], ref_id=a["id"]))
        else:
            acts.append(_act(t, "free", "Free time and local market stroll",
                             "Wander at your own pace, pick up souvenirs or rest.", 0, 90, bundle["destination"]["name"]))

    # Meals (rotate through restaurants allowed for this tier)
    allowed = [r for r in bundle["restaurants"] if TIERS.index(r["tier"]) <= TIERS.index(style)]
    if not allowed:
        allowed = bundle["restaurants"]
    offset = rng.randrange(len(allowed))
    lunch = allowed[(d * 2 + offset) % len(allowed)]
    dinner = allowed[(d * 2 + 1 + offset) % len(allowed)]
    for time, label, r in (("13:15" if len(items) >= 4 else "13:00", "Lunch", lunch), ("20:00", "Dinner", dinner)):
        acts.append(_act(time, "meal", f"{label} at {r['name']}", f"{r['cuisine']}. {r['description']}",
                         r["cost_per_person"] * travelers, 75, bundle["destination"]["name"], ref_id=r["id"]))

    # Stay / departure
    if d < days - 1:
        acts.append(_act("22:00", "stay", f"Overnight at {hotel['name']}",
                         f"{rooms} room(s) at {hotel['price_per_night']} per night.", hotel["price_per_night"] * rooms, 0,
                         hotel["name"]))
    else:
        acts.append(_act("21:00", "transport", "Check out and depart",
                         "Collect luggage and head to the station or airport.", 0, 60, bundle["destination"]["name"]))

    acts.sort(key=lambda a: a["time"])
    theme = f"{chosen[0]['area']} and around" if chosen else "Leisure day"
    return {
        "day": d + 1,
        "date": day_date.isoformat(),
        "theme": theme,
        "activities": acts,
        "day_cost": sum(a["cost"] for a in acts),
    }


def recompute(itin, budget, travelers):
    """Refresh day costs, total, breakdown and budget status after any change."""
    breakdown = {"stay": 0, "food": 0, "attractions": 0, "transport": 0}
    total = 0
    for day in itin["days"]:
        day["activities"].sort(key=lambda a: a.get("time", "00:00"))
        day["day_cost"] = 0
        for a in day["activities"]:
            cost = int(a.get("cost") or 0)
            a["cost"] = cost
            day["day_cost"] += cost
            key = {"stay": "stay", "meal": "food", "attraction": "attractions", "transport": "transport"}.get(a.get("type"), None)
            if key:
                breakdown[key] += cost
            else:
                breakdown["attractions"] += cost  # custom / free items count as activities
        total += day["day_cost"]
    itin["total_cost"] = total
    itin["per_person"] = round(total / max(1, travelers))
    itin["breakdown"] = breakdown
    itin["budget"] = budget
    itin["budget_status"] = "within" if total <= budget else "over"
    itin["budget_delta"] = abs(budget - total)
    return itin


def _build(bundle, p, style, seed):
    rng = random.Random(seed * 7919 + 13)
    days = trip_days(p["start_date"], p["end_date"])
    hotel = _pick_hotel(bundle, style)
    transport = _pick_transport(bundle, style, p["travelers"])
    exclude, day_list = set(), []
    for d in range(days):
        day = plan_day(bundle, p, style, d, days, exclude, rng, hotel, transport)
        exclude |= {a["ref_id"] for a in day["activities"] if a["type"] == "attraction"}
        if len(exclude) >= len(bundle["attractions"]):
            exclude = set()  # every attraction used once: allow a second pass on long trips
        day_list.append(day)
    return {
        "destination": bundle["destination"]["name"],
        "hotel": {k: hotel[k] for k in ("id", "name", "tier", "price_per_night", "rating")},
        "transport": {k: transport[k] for k in ("id", "mode", "cost_per_day", "unit")},
        "applied_style": style,
        "requested_style": p["style"],
        "days": day_list,
        "overview": "",
        "tips": [],
    }


def generate_itinerary(bundle, p, seed=0):
    """p keys: start_date, end_date, travelers, budget, style, pace, interests."""
    styles = TIERS[: TIERS.index(p["style"]) + 1][::-1]  # requested tier first, then cheaper ones
    itin = None
    for s in styles:
        itin = _build(bundle, p, s, seed)
        recompute(itin, p["budget"], p["travelers"])
        if itin["total_cost"] <= p["budget"]:
            break
    return itin


def regenerate_day(bundle, p, itin, day_no, seed):
    """Replace one day while avoiding attractions used on the other days."""
    days = len(itin["days"])
    exclude = {a["ref_id"] for day in itin["days"] if day["day"] != day_no
               for a in day["activities"] if a["type"] == "attraction" and a.get("ref_id")}
    hotel = next((h for h in bundle["hotels"] if h["id"] == itin["hotel"]["id"]), _pick_hotel(bundle, itin["applied_style"]))
    transport = next((t for t in bundle["transports"] if t["id"] == itin["transport"]["id"]),
                     _pick_transport(bundle, itin["applied_style"], p["travelers"]))
    rng = random.Random(seed * 104729 + day_no)
    new_day = plan_day(bundle, p, itin["applied_style"], day_no - 1, days, exclude, rng, hotel, transport)
    itin["days"] = [new_day if d["day"] == day_no else d for d in itin["days"]]
    return recompute(itin, p["budget"], p["travelers"])
