# Deployment

The hosted ChatGPT Site runs the browser demonstration. Python/FastAPI, SQLite and scikit-learn need a separate Python host; they do not run in static Sites hosting.

## Render backend

Push the monorepo to your Git repository. Create a Python service rooted at `backend`.

- Build: `pip install -r requirements.txt && python -m app.ml.train`
- Start: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `CORS_ORIGINS` to the exact frontend HTTPS origin; set `OPEN_CHARGE_MAP_API_KEY` server-side.
- SQLite requires persistent storage and a single instance, e.g. `DATABASE_URL=sqlite:////var/data/chargesmart.db`. Ephemeral disks lose reports across redeployments.
- PostgreSQL: `DATABASE_URL=postgresql+psycopg://...`; psycopg is in requirements. Schema types are portable; PostgreSQL was not exercised during verification.

## Vercel frontend

Root: `frontend`. Install: `npm ci`. Build: `npm run build`. Output: `dist`.

Set `VITE_API_URL` to the Render HTTPS origin and `VITE_BROWSER_DEMO=false`. Rebuild after changing frontend environment variables. `vercel.json` provides SPA fallback. Check station loading, route planning and reports after deployment.

No Render/Vercel credentials were supplied; these are instructions, not a claim of deployment there. Plans, prices and provider quotas were not checked. Before public deployment add appropriate abuse protection, report moderation, authentication where needed, migrations, backups and monitoring. This MVP does not claim those controls.
