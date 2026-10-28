# Tripora: Curated Travel Itinerary Planner

Tripora is a full-stack, AI-assisted travel planning platform that turns destinations, travel dates, budgets, and personal interests into structured, day-by-day itineraries. It features interest-based attraction scoring, geographic clustering to minimize transit time, adaptive budget fitting across dining, stays, and transit, interactive day-by-day timelines, and multi-user trip collaboration.

| Layer | Technology |
|---|---|
| **Frontend** | React 18, React Router, Vite, plain modern CSS with custom design tokens |
| **Backend** | Python, FastAPI, Pydantic, PyJWT authentication |
| **Database** | Dual-engine: SQLite for local development (zero setup), PostgreSQL for production via `DATABASE_URL` |
| **Generative AI** | Optional Groq + Llama 3 (or any OpenAI-compatible API) for narrative overviews and travel tips; built-in deterministic fallback generator when no key is set |

---

## 1. Quick Start (Local Development)

### Windows (One-Click Launcher)

1. Install **Python 3.10+** (ensure "Add python.exe to PATH" is checked) and **Node.js 18+**.
2. Double-click **`run.bat`** (or execute `.\run.bat` in PowerShell / Command Prompt).

The launcher automatically detects the Python interpreter (`py` or `python`), verifies dependencies, launches the FastAPI backend and Vite frontend dev server, and opens the browser.

| Service | Local URL |
|---|---|
| **Web Application** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **Interactive API Docs (Swagger)** | http://localhost:8000/docs |

The database (`backend/travel.db`) is created and seeded automatically with sample data on first start.

### Manual Start (Cross-Platform: Windows, macOS, Linux)

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # On Windows: copy .env.example .env
uvicorn app.main:app --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

To reset local sample data, stop the backend, delete `backend/travel.db`, and restart the backend.

---

## 2. Demo User Credentials

The database seeds automatically with 7 demo accounts representing distinct travel personas. You can click any pre-filled persona card on the sign-in screen:

| # | Name | Email | Password | Role | Description |
|---|---|---|---|---|---|
| 1 | Admin User | `admin@travelplanner.com` | `Admin@123` | admin | Varanasi cultural trip (3 travellers) |
| 2 | Aarav Sharma | `aarav@example.com` | `Aarav@123` | traveler | Goa solo weekend; invited to Manali trip |
| 3 | Priya Nair | `priya@example.com` | `Priya@123` | traveler | Udaipur couple getaway (premium tier) |
| 4 | Rohan Mehta | `rohan@example.com` | `Rohan@123` | traveler | Owns Rishikesh adventure trip; co-editor on Manali |
| 5 | Meera Iyer | `meera@example.com` | `Meera@123` | traveler | Manali friends group trip (5 travellers, 4 invited members) |
| 6 | Karan Singh | `karan@example.com` | `Karan@123` | traveler | Jaipur city break; collaborator on Manali trip |
| 7 | Sneha Reddy | `sneha@example.com` | `Sneha@123` | traveler | Munnar scenic retreat |

Passwords are stored as salted PBKDF2-SHA256 hashes. Change `JWT_SECRET` in `.env` before public deployment.

---

## 3. Seeded Travel Catalog

Tripora includes curated sample data across 7 Indian destinations:

| Table | Count | Highlights |
|---|---|---|
| **destinations** | 7 | Goa, Jaipur, Manali, Munnar, Udaipur, Rishikesh, Varanasi |
| **attractions** | 28+ | Real-world sights with duration, entry fees, ideal time-of-day slots, and interest tags |
| **restaurants** | 28 | Dining options segmented across budget, mid, and premium tiers |
| **hotels** | 21 | Accommodations categorized by tier with nightly pricing and amenities |
| **transports** | 14 | Local transit options (scooter, auto-rickshaw, private cabs) |
| **trips** | 7 | Pre-generated sample itineraries |
| **trip_members**| 7 | Shared collaboration records linking travellers |
| **reviews** | 7 | Sample traveller feedback per destination |

---

## 4. Key Application Features

- **Guided 4-Step Builder:** Choose destinations, dates, party size, target budget, travel pace (*relaxed*, *balanced*, *packed*), and travel interests.
- **Scenario Quick-Starts:** Instant presets on the dashboard for solo escapes, romantic getaways, and group trips.
- **Geographic & Time Slot Clustering:** Itinerary stops are clustered by geographic zone and sequenced logically (morning, afternoon, evening) to reduce transit time.
- **Adaptive Budget Meter:** Live calculation of accommodation, transport, meals, and attraction fees with visual status (*within budget*, *near limit*, *over budget*).
- **In-Place Itinerary Editing:** Update activity times, titles, costs, or remove stops directly on the timeline with a sticky save bar.
- **Selective Day & Full Trip Regeneration:** Re-roll individual days or regenerate the entire plan while locking in custom modifications.
- **Multi-User Collaboration:** Invite registered travellers by email to co-plan and edit shared itineraries.
- **Destination Atlas (Explore):** Detailed destination guide with attractions, local food, stays, transit, and user reviews.

---

## 5. Configuration & Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|:---:|---|---|
| `DATABASE_URL` | Optional | `""` (SQLite) | PostgreSQL connection URI for production (e.g. Render / Supabase). Falls back to SQLite `travel.db` if empty. |
| `JWT_SECRET` | Recommended | `dev-secret-...` | Secret key used to sign HS256 authentication tokens. |
| `CORS_ORIGINS` | Production | `http://localhost:5173` | Comma-separated list of permitted frontend origins (e.g. `https://tripora.vercel.app`). |
| `GROQ_API_KEY` | Optional | `""` | API key for LLM itinerary enrichment (Groq Llama-3). |
| `LLM_BASE_URL` | Optional | `https://api.groq.com/openai/v1` | OpenAI-compatible endpoint URL. |
| `LLM_MODEL` | Optional | `llama-3.1-8b-instant` | Model identifier for narrative generation. |
| `SUPABASE_URL`, `SUPABASE_KEY` | Optional | `""` | Optional cloud mirroring credentials for Supabase REST API. |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|---|:---:|---|---|
| `VITE_API_BASE_URL` | Production | `""` (local proxy) | Base URL of the deployed backend API (e.g. `https://tripora-backend.onrender.com`). |

---

## 6. Deployment Architecture

Tripora is architected for simple, separate deployment of frontend and backend:

```
[ Frontend: Vercel ]
        │
        ▼ (HTTPS / CORS)
[ Backend: Render Web Service ]
        │
   ┌────┴────────────────────────┐
   ▼                             ▼
(Local / Dev)             (Production)
SQLite (travel.db)        PostgreSQL (Supabase / Render Managed)
```

### Backend on Render
1. Create a new **Web Service** connected to your repository.
2. Configure settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/api/health`
3. Add Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string (e.g. from Supabase).
   - `JWT_SECRET`: A high-entropy random secret.
   - `CORS_ORIGINS`: Your Vercel frontend URL (e.g. `https://tripora.vercel.app`).

### Frontend on Vercel
1. Import repository and set **Root Directory** to `frontend`.
2. Set Environment Variable:
   - `VITE_API_BASE_URL`: Your Render backend URL (e.g. `https://tripora-backend.onrender.com`).
3. Deploy. If updating `VITE_API_BASE_URL` later, trigger a **Redeploy** to bake the environment variable into static assets.

---

## 7. Testing

The backend includes comprehensive test coverage for API endpoints, authentication, catalog loading, trip lifecycle, database persistence, and SQL query adaptation:

```bash
# Run isolated test suite
cd backend
python -m unittest tests/test_api.py -v
```

Tests automatically run against an isolated ephemeral SQLite database by default, keeping `travel.db` untouched. To test against PostgreSQL, provide an explicit `TEST_DATABASE_URL`:

```bash
TEST_DATABASE_URL="postgresql://user:pass@host:5432/test_db?sslmode=require" python -m unittest tests/test_api.py -v
```
