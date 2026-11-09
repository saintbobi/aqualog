# I Containerized a Water Quality Tracker for My Fish Tank (And Learned Docker Properly)

Aquarium hobbyists have a quiet enemy: invisible water chemistry. Ammonia can spike overnight, pH can drift slowly over weeks, and by the time fish show stress, it is often too late. Shrimp tanks are even less forgiving — a 0.05 ppm difference in ammonia can be the line between a thriving colony and an empty tank.

Like most keepers, I used to track my water parameters in a scattered notes app. No trends, no history, no alerts. So for my cloud services course project, I decided to fix this with a small multi-tier web app — and more importantly, to learn containerization the right way: **Aquarium Parameter Log** (a.k.a. `aqualog`).

## What It Does

One core feature, done properly: log water measurements per tank and see the trend.

- Create tanks (freshwater, planted, or shrimp)
- Log readings: pH, temperature, NH3, NO2, NO3
- View history as a table and a Chart.js trend line
- Get an instant **safe / warning / danger** verdict per reading, based on threshold rules for each tank type — shrimp get stricter ammonia limits than freshwater fish

Target users are aquarium and shrimp keepers who test water regularly but have nowhere structured to put the numbers.

## Architecture

The whole thing runs on localhost with one `docker compose up -d --build`:

```
browser ──► app (FastAPI + Jinja2, port 8000)
              │  GET/POST
              ├──► db (PostgreSQL 16, named volume, healthcheck)
              └──► redis (cache, healthcheck, 30s TTL)
           [profile tools: adminer on port 8080]
```

- **app** — FastAPI backend + Jinja2 frontend in one container. Endpoints: `GET /health` (liveness), `GET /tanks`, `POST /tanks`, `GET /readings` (Redis-cached), `POST /readings`.
- **db** — PostgreSQL 16, data persisted in a named volume, exposed to the app network only.
- **redis** — caches reading lists for 30 seconds, cache invalidated on new writes.
- **adminer** — a DB UI that only starts with the `tools` profile, so day-to-day runs stay lean.

## The Dockerfile

The app image is a two-stage build:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app/ app/
COPY templates/ templates/
COPY static/ static/
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Details that matter:

- **Multi-stage** — the builder stage carries pip and the full toolchain; the runtime stage only gets the finished virtualenv. Result: a 272 MB image with no build tools inside.
- **Dependencies copied first** — `requirements.txt` is copied and installed before any source code. Since it rarely changes, Docker reuses the cached layer on every code edit; my rebuilds after a code change finish in under a second.
- **Pinned tags, not `latest`** — `python:3.12-slim`, `postgres:16.9-alpine`, `redis:7.4-alpine`. Reproducible builds beat convenient ones.
- **Exec-form CMD** — `CMD ["uvicorn", ...]` makes uvicorn PID 1, so signals like `SIGTERM` reach the app and containers stop cleanly.
- The app runs as a non-root `appuser` — one less thing to worry about if this ever leaves localhost.

## The Compose File

```yaml
services:
  app:
    build: .
    environment:
      POSTGRES_HOST: db          # connect by service name, not IP
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16.9-alpine
    volumes:
      - aquarium-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
```

Three things I appreciate most in Compose:

1. **DNS by service name** — the app connects to `db`, never to a container IP. Containers get new IPs on every restart; names are stable.
2. **Healthcheck + `service_healthy`** — the app container waits until Postgres actually accepts connections, killing the classic "app started before the database" race condition.
3. **Named volumes** — `docker compose down` removes containers, but the volume survives. My readings were still there after a full teardown and rebuild. (`docker compose down -v` would wipe it — the `-v` flag deserves respect.)

## Try It

```bash
git clone https://github.com/saintbobi/aqualog.git
cd aqualog
cp .env.example .env
docker compose up -d --build
```

Then open http://localhost:8000. The image is also on Docker Hub as `saintbobi705/aqualog:1.0.0`.

## What I Learned

- Copying the dependency manifest before source code is the single highest-leverage habit in Dockerfile authoring. Layer caching turns 30-second rebuilds into near-instant ones.
- Healthchecks are not decoration. They turned my startup from "hope it works" into a deterministic sequence.
- Rule-based safety verdicts don't need machine learning to feel useful — good thresholds per tank type already make the app something I would actually use.
- Designing for zero personal data from the start is both an ethical and a practical shortcut: nothing sensitive to leak, nothing to redact before publishing.

**Repo:** https://github.com/saintbobi/aqualog
**Video demo:** <YouTube link>
