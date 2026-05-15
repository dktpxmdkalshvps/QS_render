# Quant Backend API - Render Deploy Package

This is a Render-ready FastAPI backend package for the portfolio quant project.

## Stack

- FastAPI
- SQLAlchemy 2.x
- Alembic migrations
- PostgreSQL on Render
- Gunicorn + Uvicorn worker

## Included API

- `GET /` service info
- `GET /health` database health check
- `GET /api/stocks`
- `POST /api/stocks`
- `GET /api/themes/{theme_key}/snapshots`
- `GET /api/themes/{theme_key}/snapshots/latest`
- `POST /api/themes/{theme_key}/snapshots`
- `GET /api/market-calendar`
- `POST /api/market-calendar`
- `GET /api/refresh-runs`
- `POST /api/refresh-runs`

Swagger UI is available at `/docs` after deployment.

## Local setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
http://localhost:8000/health
```

## Render deployment option A - Blueprint

1. Unzip this package.
2. Push the folder contents to a GitHub repository.
3. In Render, select **New > Blueprint**.
4. Connect the repository that contains `render.yaml`.
5. Deploy the Blueprint.
6. Replace `CORS_ORIGINS` in Render with your real Vercel URL.

The `render.yaml` file provisions:

- one Python web service
- one Render PostgreSQL database
- `DATABASE_URL` wired from the database connection string

## Render deployment option B - Manual web service

Create a Render PostgreSQL database first, then create a Python Web Service.

Use these commands:

```bash
Build Command: ./build.sh
Start Command: ./start.sh
```

Set these environment variables:

```text
DATABASE_URL=<Render Postgres internal database URL>
APP_ENV=production
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000,http://localhost:5173
WEB_CONCURRENCY=2
```

## Important notes

- `start.sh` runs `alembic upgrade head` before starting the API. This keeps the database schema updated on Render Free plans where pre-deploy commands may not be available.
- Render expects the app to bind to `0.0.0.0` and the `PORT` environment variable. This package uses `${PORT:-10000}`.
- Render Free web services can spin down when idle. The first request after inactivity can be slower.
- Render Free PostgreSQL has limits, including a 30-day expiration, so upgrade the database before using this as a long-term production database.

## Frontend environment variable examples

For Vite:

```text
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

For Next.js:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
```

## Quick API test after deployment

```bash
curl https://your-render-service.onrender.com/health
curl https://your-render-service.onrender.com/api/stocks
```

## Seed sample data on Render

Render Free web services do not provide shell access. For sample data, either:

1. temporarily call the POST endpoints from Swagger UI, or
2. run `python scripts/seed.py` locally with `DATABASE_URL` set to the Render external database URL.

Example:

```bash
DATABASE_URL='postgresql://user:password@host:5432/dbname' python scripts/seed.py
```
