# Aquarium Parameter Log

Small multi-tier web app for aquarium hobbyists to log water parameters (pH, temperature, NH3, NO2, NO3) per tank and view trends — spot drift before fish die.

Built as the UTS project for COMP6991031 (Cloud Services). Runs entirely on localhost with Docker Compose.

## Why this project

Aquarium water chemistry is unforgiving: shrimp and fish die when ammonia or pH drift silently. Hobbyists track readings in scattered notes with no trend visibility. This app gives one place to log and visualize measurements per tank. Target users: freshwater/planted/shrimp tank keepers.

Target career role: Backend / Cloud Engineer — the project exercises the core of that work: containerization, orchestration, service-to-service networking, and stateful services.

## Architecture

```
browser ──► app (FastAPI + Jinja2, port 8000)
              │  GET/POST
              ├──► db (PostgreSQL 16, named volume, healthcheck)
              └──► redis (cache, healthcheck, 30s TTL)
           [profile tools: adminer on port 8080]
```

- `app` — FastAPI backend + Jinja2 frontend in one container (multi-stage Dockerfile)
- `db` — PostgreSQL 16, data persisted in named volume `aquarium-data`
- `redis` — caches `GET /readings`, cache invalidated on new reading
- `adminer` — DB UI, only with `--profile tools`

## Endpoints

| Method | Path | Description | Success |
|---|---|---|---|
| GET | `/health` | Liveness probe | 200 |
| GET | `/tanks` | List tanks | 200 |
| POST | `/tanks` | Create tank | 201 |
| GET | `/readings?tank_id=N` | Reading history (Redis-cached) | 200 |
| POST | `/readings` | Log a reading | 201 |

## Run

```bash
git clone https://github.com/saintbobi/aqualog.git
cd aqualog
cp .env.example .env
docker compose up -d --build
```

Open http://localhost:8000.

Optional tools (Adminer): `docker compose --profile tools up -d` → http://localhost:8080

## Docker Hub

Image published at [docker.io/saintbobi705/aqualog](https://hub.docker.com/r/saintbobi705/aqualog):

```bash
docker pull saintbobi705/aqualog:1.0.0
docker pull saintbobi705/aqualog:latest
```

## Screenshots

TODO — after build: `docker compose ps`, curl tests, persistence test.

## Data & compliance

The app stores no personal data by design — only tank names and water measurements (dummy data by default). Database credentials live in `.env` (git-ignored); `.env.example` documents the required variables.

## Article & video

- Article: TODO
- Video demo: TODO

## Sources

- [FastAPI](https://fastapi.tiangolo.com/) — web framework
- [Jinja2](https://jinja.palletsprojects.com/) — templating
- [Chart.js](https://www.chartjs.org/) — trend chart (CDN)
- [psycopg](https://www.psycopg.org/) — PostgreSQL adapter
- Docker base images: `python:3.12-slim`, `postgres:16.9-alpine`, `redis:7.4-alpine`, `adminer:4.8.1`

## AI Usage Declaration

| Tool | Used for | Portion |
|---|---|---|
| Claude Code (Anthropic) | Project scaffold, Dockerfile & docker-compose boilerplate, debugging | ~40% of code |

Key prompts:
- "outline what must be done for this UTS"
- "build FastAPI app: tanks + readings, GET/health, POST/readings 201, Postgres, Redis cache"

All conceptual design (project choice, architecture decisions, data model rationale, report, article) written by the author.
