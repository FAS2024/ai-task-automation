# AI-Powered Task Automation Platform

[![CI](https://github.com/FAS2024/ai-task-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/FAS2024/ai-task-automation/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Backend for a multi-tenant style automation API: clients submit work, Celery runs it, optional Redis pushes updates over WebSockets. I use it as a portfolio piece for backend and platform roles.

**Stack:** Python 3.12 · `main` is linted and tested in GitHub Actions (Ruff + pytest with coverage).

Repo: `https://github.com/FAS2024/ai-task-automation`

## TL;DR (fastest run)
```bash
copy backend\env.sample.txt backend\.env
docker compose up --build
```
API: `http://localhost:8000/api/v1`

## Setup / Run / Test
```bash
# setup
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# run (local)
uvicorn app.main:app --reload
# run worker (new terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# test
pytest
```

## Highlights
- Celery workers, Redis as broker; WebSocket channel when Redis is up
- JWT auth, role-based admin routes, SlowAPI rate limits
- Postgres + Alembic; Docker Compose for api, worker, db, redis
- OpenAPI at `/docs` and `/openapi.json`; Postman under `docs/`
- JSON logs, `X-Request-ID`, optional OTLP tracing

## Why this project
This project models a real automation platform where multiple clients submit
workflows, tasks are processed asynchronously, and updates stream in real time.
It shows how to design for reliability, observability, and clean interfaces.

## Tech stack
- FastAPI, SQLAlchemy, Alembic
- Celery + Redis (broker + pubsub)
- PostgreSQL
- LangChain + OpenAI (mock fallback)
- OpenTelemetry (optional)

## Architecture
See `docs/architecture.md` for the system diagram.

## Postman
Import `docs/postman_collection.json` and set:
- `baseUrl` (e.g. `http://localhost:8000`)
- `token` (JWT from `/auth/token`)

## Quick start (local, mock LLM)
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# optional (enables Celery + WebSocket updates + Postgres)
docker compose up -d

# run API
uvicorn app.main:app --reload

# run celery worker (new terminal)
celery -A app.tasks.celery_app worker --loglevel=info
```

API: `http://localhost:8000/api/v1`  
Docs: `http://localhost:8000/docs` · OpenAPI JSON: `http://localhost:8000/openapi.json`

## Production-like run (Docker)
```bash
copy backend\env.sample.txt backend\.env
docker compose up --build
```

API: `http://localhost:8000`

## Environment config
Copy `backend/env.sample.txt` to `backend/.env` and fill in values.
If `OPENAI_API_KEY` is missing, a deterministic mock model is used.

## Example usage
1) Register and obtain a token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"password\":\"ChangeMe123\"}"
```

```bash
curl -X POST http://localhost:8000/api/v1/auth/token ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin@example.com&password=ChangeMe123"
```

2) Create a task:
```bash
curl -X POST http://localhost:8000/api/v1/tasks ^
  -H "Authorization: Bearer <token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"client_id\":\"client-001\",\"workflow_type\":\"invoice_processing\",\"payload\":{\"invoice_id\":123}}"
```

3) Check task status:
```bash
curl http://localhost:8000/api/v1/tasks/<task_id> ^
  -H "Authorization: Bearer <token>"
```

WebSocket (needs Redis for live events; otherwise the server sends a single `noop` message):
`ws://localhost:8000/api/v1/ws/updates`

## Health & readiness
- `GET /api/v1/health` (basic status)
- `GET /api/v1/health/ready` (Redis connectivity)

## Admin bootstrap
Set these in `backend/.env` to auto-create an admin on startup:
```
INITIAL_ADMIN_EMAIL=admin@example.com
INITIAL_ADMIN_PASSWORD=ChangeMe123
```

## Production notes
- Secrets are read from environment variables only.
- Background jobs are isolated in a dedicated Celery worker.
- DB schema is versioned with Alembic and auto-migrated in Docker.
- Structured JSON logging is enabled for better log ingestion.

## Tests
```bash
cd backend
.\.venv\Scripts\activate
pytest
```

## Lint
```bash
cd backend
.\.venv\Scripts\activate
ruff check .
```

## Smoke test (PowerShell)
```powershell
cd backend
.\scripts\smoke_test.ps1
```

## Seed demo data
```powershell
cd backend
.\scripts\seed.ps1
```

## Security (deploying for real)
- Change `JWT_SECRET_KEY` and initial admin credentials before deployment.
- Use a managed Postgres and Redis in production.
- Set strict `CORS_ORIGINS` for your front-end domain.
- Rotate secrets and use a secrets manager in production.

## Notes
- If Redis is not running, Celery falls back to in-memory eager mode.
- To enable real-time updates, run Redis (`docker compose up -d`).

## Troubleshooting
- If Docker images won’t build, restart Docker Desktop and retry.
- To reset the database: `docker compose down -v` (destroys data).

## Interview angles
- Split API and worker so timeouts and retries stay out of request threads.
- Auth is JWT claims + DB user lookup; admin is a separate dependency.
- Migrations and health checks are there so deploys are boring on purpose.

## Contributing & security
- See `CONTRIBUTING.md` for dev workflow and quality checks.
- See `SECURITY.md` for reporting issues.
