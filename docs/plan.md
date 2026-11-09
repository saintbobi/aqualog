# Aquarium Parameter Log — Project Plan

Small multi-tier web app for UTS COMP6991031.
Aquarium hobbyists log water parameters (pH, temperature, NH3, NO2, NO3) per tank and view trends.

## Core feature (MVP)
Log a reading for a tank → view history table + trend chart.

## Architecture
- Backend: FastAPI (Python 3.12) + Jinja2 templates — one container
- Database: PostgreSQL 16 container, named volume
- Cache: Redis container (bonus) — caches GET /readings, 30s TTL
- Tools profile: Adminer (profile `tools`)

## Endpoints
- GET  /health → 200 (liveness)
- GET  /tanks → 200 (tank list)
- POST /tanks → 201 (create tank)
- GET  /readings?tank_id= → 200 (history, Redis-cached)
- POST /readings → 201 (insert reading, invalidates cache)

## Schema
tanks:    id, name, water_type (freshwater/planted/shrimp), created_at
readings: id, tank_id FK, ph, temperature_c, nh3_ppm, no2_ppm, no3_ppm, measured_at

## Run
git clone → cp .env.example .env → docker compose up -d --build → http://localhost:8000

## Checklist
- [x] gitignore + env example
- [ ] app scaffold (health)
- [ ] db layer + models
- [ ] endpoints + templates
- [ ] redis cache
- [ ] Dockerfile multi-stage + .dockerignore
- [ ] docker-compose (network, volume, healthcheck, depends_on, profile)
- [ ] README + screenshots
- [ ] article + video + PDF report
