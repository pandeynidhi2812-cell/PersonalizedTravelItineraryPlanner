# Wayfare: Personalized Travel Itinerary Planner

A full-stack, AI-assisted web app that turns a destination, budget, dates and interests into a day-by-day itinerary with attractions, meals, accommodation and local transport. Users can save, edit and regenerate trips, track estimated costs, and plan together with friends.

| Layer | Technology |
|---|---|
| Frontend | React 18, React Router, Vite (plain CSS, no UI kit) |
| Backend | Python, FastAPI, Pydantic, JWT authentication |
| Database | SQLite by default (zero setup), optional Supabase mirror |
| Generative AI | Optional Llama-3 (or any OpenAI-compatible model) for trip overview and tips; built-in template writer when no key is set |

---

## 1. Quick start (Windows)

1. Install **Python 3.10+** (tick "Add to PATH") and **Node.js 18+**.
2. Double-click **`run.bat`**.

It creates a virtual environment, installs the backend and frontend packages, starts both servers in their own windows, and opens the browser.

| Service | URL |
|---|---|
| Web app | http://localhost:5173 |
| API | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/docs |

The first run needs an internet connection to download packages. The database is created and filled with sample data automatically on first start.

### Manual start (any OS)

```bash
# terminal 1: backend
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # Windows: copy .env.example .env
uvicorn app.main:app --port 8000 --reload

# terminal 2: frontend
cd frontend
npm install
npm run dev
```

To reset all data, stop the backend, delete `backend/travel.db`, and start it again.

---

## 2. Login credentials

All accounts are created automatically with the sample data. You can also click any demo card on the sign-in page to fill the form.

| # | Name | Email (ID) | Password | Role | What they have |
|---|---|---|---|---|---|
| 1 | Admin User | `admin@travelplanner.com` | `Admin@123` | admin | Varanasi trip (3 travellers) |
| 2 | Aarav Sharma | `aarav@example.com` | `Aarav@123` | traveler | **Scenario 1:** Goa solo weekend; also invited to the Manali group trip |
| 3 | Priya Nair | `priya@example.com` | `Priya@123` | traveler | **Scenario 2:** Udaipur couple trip (premium) |
| 4 | Rohan Mehta | `rohan@example.com` | `Rohan@123` | traveler | Co-editor on the Udaipur and Manali trips; owns the Rishikesh trip |
| 5 | Meera Iyer | `meera@example.com` | `Meera@123` | traveler | **Scenario 3:** Manali friends trip (5 travellers, 4 invited members); also invited to the Rishikesh trip |
| 6 | Karan Singh | `karan@example.com` | `Karan@123` | traveler | Jaipur trip; member of Manali and Rishikesh trips |
| 7 | Sneha Reddy | `sneha@example.com` | `Sneha@123` | traveler | Munnar trip; member of the Manali trip |

Passwords are stored as salted PBKDF2-SHA256 hashes, never in plain text. These are demo credentials only. Change them, and `JWT_SECRET`, before any real deployment.

---

## 3. Sample data (7 or more records in every table)

| Table | Records | Examples |
|---|---|---|
| users | 7 | listed above |
| destinations | 7 | Goa, Jaipur, Manali, Munnar, Udaipur, Rishikesh, Varanasi |
| attractions | 35 | 5 per destination, with interest tags, fees, duration, best time of day, area |
| restaurants | 28 | 4 per destination across budget, mid and premium tiers |
| hotels | 21 | 3 per destination (budget, mid, premium) |
| transports | 14 | 2 per destination (scooter / auto / shared, and private cab) |
| trips | 7 | each with a fully generated itinerary |
| trip_members | 7 | invited co-travellers with their own interests |
| reviews | 7 | one per user |

Attractions are real places. Restaurant and hotel names, and all prices (in INR), are **illustrative sample data**, not live listings.

---

## 4. Features

- **Smart trip builder:** destination, dates, travellers, budget, stay style (budget / mid / premium), pace (relaxed / balanced / packed) and interests.
- **Scenario shortcuts** on the dashboard for the solo weekend, couple escape and friends group trip.
- **Itinerary generation** that scores places against your interests, clusters each day around one area to cut travel time, orders stops by best time of day, and adds meals, local transport and nightly stay.
- **Budget-aware:** if the plan is over budget it steps stay and dining down a tier and tells you. If it is still over, it shows exactly how much.
- **Interactive itinerary view:** day tabs, timeline, live cost totals, cost breakdown, and per-person cost.
- **Edit everything:** change time, title or cost of any item, remove items, or add your own. Save or discard.
- **Regenerate** a single day or the whole trip.
- **Group planning:** invite registered users by email. Their interests are blended into the plan on the next regenerate, and they can edit the itinerary.
- **Explore** page with attractions, dining, stays, local transport and reviews for each destination.
- **Print-friendly** itinerary (prints all days).

---

## 5. Configuration (`backend/.env`)

Every setting is optional. The app runs fully offline without any of them.

| Variable | Purpose |
|---|---|
| `JWT_SECRET` | Signs login tokens. Set to a long random string outside local use. |
| `LLM_API_KEY` | Enables Llama-3 written overviews and tips. Works with any OpenAI-compatible API. |
| `LLM_BASE_URL` | Default `https://api.groq.com/openai/v1` |
| `LLM_MODEL` | Default `llama-3.1-8b-instant` |
| `SUPABASE_URL`, `SUPABASE_KEY` | Mirror saved trips to your Supabase project. |

The AI layer only writes the overview and tips. The schedule, routing and cost maths are done by the deterministic planner so budgets stay accurate and the app never depends on a model being available. If the LLM call fails, it silently falls back to the template text.

### Supabase setup (optional)

1. Create a Supabase project.
2. Open the SQL editor and run `supabase_schema.sql`.
3. Put your project URL in `SUPABASE_URL` and your **service_role** key in `SUPABASE_KEY`, then restart the backend.

SQLite stays the primary store. When Supabase is configured, each trip create, edit, regenerate and delete is mirrored to the `trips` table (best effort, failures never block a request). `GET /api/health` reports `supabase_enabled` and `llm_enabled`. Keep the service_role key on the server only.

---

## 6. API overview

Authenticated routes need the header `Authorization: Bearer <token>` from login. Full interactive docs are at `/docs`.

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/auth/register`, `/api/auth/login` | Create account / sign in |
| GET | `/api/auth/me` | Current user |
| GET | `/api/destinations`, `/api/destinations/{id}` | Browse destinations with places, food, stays, transport, reviews |
| POST | `/api/reviews` | Add a review |
| GET | `/api/dashboard` | Stats and recent trips |
| GET / POST | `/api/trips` | List trips / generate a new trip |
| GET / PUT / DELETE | `/api/trips/{id}` | Read, save edits, delete |
| POST | `/api/trips/{id}/regenerate` | Regenerate the whole itinerary |
| POST | `/api/trips/{id}/days/{n}/regenerate` | Regenerate one day |
| POST / DELETE | `/api/trips/{id}/members[/{user_id}]` | Add or remove a co-traveller |
| GET | `/api/health` | Service status |

---

## 7. Project structure

```
travel-itinerary-planner/
|-- run.bat                    one-click launcher (Windows)
|-- README.md
|-- supabase_schema.sql        optional Supabase table
|-- backend/
|   |-- requirements.txt
|   |-- .env.example
|   `-- app/
|       |-- main.py            FastAPI routes
|       |-- planner.py         itinerary engine (scoring, routing, costs, budget fitting)
|       |-- ai.py              optional Llama-3 narration + template fallback
|       |-- auth.py            password hashing and JWT
|       |-- database.py        SQLite schema and helpers
|       |-- supabase_sync.py   optional Supabase mirror
|       |-- seed.py            first-run data loader
|       `-- seed_data.py       all sample data
`-- frontend/
    |-- package.json, vite.config.js, index.html
    `-- src/
        |-- App.jsx, auth.jsx, api.js, format.js, styles.css
        `-- pages/  Auth, Dashboard, Builder, Trips, TripView, Explore
```

---

## 8. System requirements

| | |
|---|---|
| CPU | Any modern dual-core (Intel Core i5 / Ryzen 5 class recommended) |
| RAM | 4 GB is enough; 8 GB recommended while running both dev servers |
| Storage | About 500 MB free (Python packages and `node_modules`) |
| GPU | Not needed |
| Network | Needed for the first install and for Google Fonts. Needed at runtime only if you enable the optional LLM or Supabase. |

This app does **not** load local Transformer models, `.keras` files or `.pkl` vocabularies. Text generation is delegated to an optional hosted LLM, which keeps the footprint small.

---

## 9. Troubleshooting

- **"Cannot reach the server" in the browser:** the API window did not start. Check it for errors, and make sure port 8000 is free.
- **`python` or `node` not recognised:** reinstall and tick "Add to PATH", then reopen the terminal.
- **Port 5173 in use:** Vite will offer the next port. Open the URL it prints. The API allows 5173 only, so stop the other process instead.
- **Plans repeat a place on long trips:** each destination has 5 sample attractions, so trips longer than about 5 days reuse them. Add rows to `seed_data.py` and reset the database to widen the choice.
