"""
Generative-AI layer.

If LLM_API_KEY is set, an OpenAI-compatible endpoint (Groq / Llama-3 by default) writes the trip
overview and tips. Without a key, or if the call fails, a template fallback is used so the app
always works offline.
"""
import json
import os

import httpx

LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")


def llm_enabled():
    return bool(LLM_API_KEY)


def _template(bundle, p, itin):
    dest = bundle["destination"]
    days = len(itin["days"])
    interests = ", ".join(p["interests"]) or "a bit of everything"
    overview = (
        f"A {days}-day {p['pace']} trip to {dest['name']} for {p['travelers']} traveller(s), "
        f"built around {interests}. You'll stay at {itin['hotel']['name']} and get around by "
        f"{itin['transport']['mode'].lower()}. Each day is clustered by area to keep travel time low."
    )
    tips = [
        f"Best season for {dest['name']}: {dest['best_season']}.",
        "Book popular entries and your stay a few weeks ahead, especially on weekends.",
        "Carry some cash for small vendors, and keep an hour of buffer around key sights.",
    ]
    if itin["budget_status"] == "over":
        tips.append("This plan is over budget even at the lowest tier. Try fewer days or fewer paid activities.")
    elif itin["applied_style"] != itin["requested_style"]:
        tips.append(f"To stay within budget the stay and dining were set to the {itin['applied_style']} tier.")
    return overview, tips


def narrate(bundle, p, itin, use_llm=True):
    """Return (overview, tips)."""
    fallback = _template(bundle, p, itin)
    if not (use_llm and llm_enabled()):
        return fallback
    try:
        plan = [
            {"day": d["day"], "theme": d["theme"],
             "stops": [a["title"] for a in d["activities"] if a["type"] == "attraction"]}
            for d in itin["days"]
        ]
        prompt = (
            "You are a concise travel planner. Given this itinerary, reply with ONLY JSON of the form "
            '{"overview": "<2-3 sentences>", "tips": ["<tip>", "<tip>", "<tip>"]}.\n'
            f"Destination: {bundle['destination']['name']}. Travellers: {p['travelers']}. "
            f"Interests: {p['interests']}. Pace: {p['pace']}. Plan: {json.dumps(plan)}"
        )
        r = httpx.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json={"model": LLM_MODEL, "temperature": 0.6,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=20,
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        text = text[text.find("{"): text.rfind("}") + 1]
        data = json.loads(text)
        overview = str(data.get("overview") or fallback[0])
        tips = [str(t) for t in data.get("tips", [])][:5] or fallback[1]
        return overview, tips
    except Exception:
        return fallback
