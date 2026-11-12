# ChargeSmart

React + TypeScript + Vite frontend, FastAPI + SQLAlchemy backend, SQLite, synthetic-trained Random Forest. Nine screens cover station discovery, battery-aware routing, recommendations, waiting forecasts, coverage analytics, environmental scenarios, guest preferences, saved journeys and reports.

## Full application: Windows PowerShell

From this folder:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python init_db.py
python -m app.ml.train
python -m uvicorn app.main:app --reload --port 8000
```

Use `py -3.12` or another Python 3.11+ installation if needed. In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. Swagger API documentation: http://localhost:8000/docs.

Linux/macOS: `python3 -m venv .venv`, `source .venv/bin/activate`, then the same Python commands. Node.js 20.19+ or 22.12+ is recommended. Startup also initializes the database and seeds only when the station table is empty.

## Standalone browser demonstration

```powershell
cd frontend
npm ci
npm run dev:demo
```

This edition needs no Python and uses **42 fictional stations**. All forecasts are rule-based, and reports/preferences/routes are local to the browser. It does not run the trained model or live providers. Build with `npm run build:demo`. The hosted Site uses this edition.

For a real API client use `npm run build`, with `VITE_BROWSER_DEMO=false`. In development Vite proxies `/api` to port 8000. For deployment set `VITE_API_URL` to the backend origin.

## Demonstration walkthrough

1. Search “JP Nagar”, filter CCS2 or 50+ kW and click station markers.
2. Select JP Nagar → Devanahalli, 45 kWh, 25% charge, 15% reserve, 0.16 kWh/km. This requires a sample charging stop. Change battery to 90% to compare a direct journey.
3. Review arrival reserve and charging time; save a route or favorite a station.
4. Compare smart picks and inspect the total-time scoring explanation.
5. Run an 18:00 synthetic forecast. API mode shows measured model errors; browser mode labels rule estimates and shows no model metrics.
6. Explore coverage and avoided-detour scenarios. Submit a community report; verified station status remains unchanged.

## Tests

```powershell
cd backend
python -m pytest -q
cd ../frontend
npm test
npm run build
```

See docs/VERIFICATION.md for results. The ML training script writes the dataset, trained model and metrics into `backend/app/ml`. Model files are generated artifacts; regenerate after dependency changes.

## Architecture

- `frontend/src`: React pages, Leaflet map, Axios client, browser simulation adapter.
- `backend/app/routers`: validated REST API.
- `backend/app/models.py`, `database.py`, `schemas.py`: SQLAlchemy entities, DB sessions, Pydantic validation.
- `backend/app/services`: energy calculations and feasible-leg graph routing.
- `backend/app/integrations`: OCM and OSRM adapters with TTL caches.
- `backend/app/ml`: synthetic generator, training and inference.
- `backend/tests`: API and route feasibility tests.

## Honest scope

Working demonstration MVP, not production navigation software. No verified occupancy feed, booking, payments, login, cross-device account sync, traffic integration or calibrated real-world waiting model. Vehicle presets are generic samples. Preferences, favorites, saved routes and recent searches use browser storage. SQL tables for saved routes are extension points; no account-sync endpoint is claimed.

Location selectors support 12 Bengaluru neighborhoods plus a selected charger destination. Text search filters station names/addresses, not worldwide geocoding. Demo routing uses straight-line distance × 1.3 and 30 km/h, not roads. Default maps use an offline geographic grid; the Online street map checkbox requests OSM tiles when permitted. Map tiles are optional and provider/network dependent.

The graph considers at most 18 corridor candidates. Conservative dwell weighting does not guarantee global time optimality. It may miss feasible routes outside the candidate set. The model assumes 90% charging efficiency, departure at 90%, constant average power, and no taper, traffic, weather or queue guarantees. Range varies with conditions. Live multi-stop road queries can take time.

Live station locations use stable `ocm-ID` identifiers but are not synchronized into SQLite; community reports currently reference seeded stations only. Operational status never implies an unoccupied charger. Tariffs are sample values in demo mode and unknown in live mode. Station sorting supports distance/power; smart picks separately rank estimated total time.

Accessibility measures sample geographic coverage, not demand. Coverage circles are not a road-based heatmap. Environmental outputs are hypothetical avoided-detour scenarios, not verified or lifecycle savings. The default grid emission factor is an editable illustrative assumption.

See docs/DEPLOYMENT.md, docs/API.md and docs/MODEL_CARD.md.
