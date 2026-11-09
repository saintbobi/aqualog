"""Aquarium Parameter Log — FastAPI application."""
import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .cache import CACHE_TTL_SECONDS, get_redis
from .database import get_conn, init_db
from .schemas import ReadingCreate, TankCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Aquarium Parameter Log", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def _db():
    return get_conn()


# ---------- Health ----------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Tanks ----------

@app.get("/tanks")
def list_tanks():
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, name, water_type, created_at FROM tanks ORDER BY id"
        ).fetchall()
    return [
        {"id": r[0], "name": r[1], "water_type": r[2], "created_at": r[3].isoformat()}
        for r in rows
    ]


@app.post("/tanks", status_code=201)
def create_tank(payload: TankCreate):
    with _db() as conn:
        row = conn.execute(
            "INSERT INTO tanks (name, water_type) VALUES (%s, %s) RETURNING id, created_at",
            (payload.name, payload.water_type),
        ).fetchone()
        conn.commit()
    return {
        "id": row[0],
        "name": payload.name,
        "water_type": payload.water_type,
        "created_at": row[1].isoformat(),
    }


# ---------- Readings ----------

@app.get("/readings")
def list_readings(tank_id: int):
    cache = get_redis()
    cache_key = f"readings:tank:{tank_id}"
    if cache:
        cached = cache.get(cache_key)
        if cached:
            return json.loads(cached)

    with _db() as conn:
        tank = conn.execute(
            "SELECT id FROM tanks WHERE id = %s", (tank_id,)
        ).fetchone()
        if tank is None:
            raise HTTPException(status_code=404, detail="tank not found")
        rows = conn.execute(
            """SELECT id, tank_id, ph, temperature_c, nh3_ppm, no2_ppm, no3_ppm, measured_at
               FROM readings WHERE tank_id = %s ORDER BY measured_at DESC""",
            (tank_id,),
        ).fetchall()

    data = [
        {
            "id": r[0],
            "tank_id": r[1],
            "ph": float(r[2]) if r[2] is not None else None,
            "temperature_c": float(r[3]) if r[3] is not None else None,
            "nh3_ppm": float(r[4]) if r[4] is not None else None,
            "no2_ppm": float(r[5]) if r[5] is not None else None,
            "no3_ppm": float(r[6]) if r[6] is not None else None,
            "measured_at": r[7].isoformat(),
        }
        for r in rows
    ]

    if cache:
        cache.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(data))
    return data


@app.post("/readings", status_code=201)
def create_reading(payload: ReadingCreate):
    with _db() as conn:
        tank = conn.execute(
            "SELECT id FROM tanks WHERE id = %s", (payload.tank_id,)
        ).fetchone()
        if tank is None:
            raise HTTPException(status_code=404, detail="tank not found")
        row = conn.execute(
            """INSERT INTO readings (tank_id, ph, temperature_c, nh3_ppm, no2_ppm, no3_ppm, measured_at)
               VALUES (%s, %s, %s, %s, %s, %s, COALESCE(%s, now()))
               RETURNING id, measured_at""",
            (
                payload.tank_id,
                payload.ph,
                payload.temperature_c,
                payload.nh3_ppm,
                payload.no2_ppm,
                payload.no3_ppm,
                payload.measured_at,
            ),
        ).fetchone()
        conn.commit()

    cache = get_redis()
    if cache:
        cache.delete(f"readings:tank:{payload.tank_id}")

    return {
        "id": row[0],
        "tank_id": payload.tank_id,
        "ph": payload.ph,
        "temperature_c": payload.temperature_c,
        "nh3_ppm": payload.nh3_ppm,
        "no2_ppm": payload.no2_ppm,
        "no3_ppm": payload.no3_ppm,
        "measured_at": row[1].isoformat(),
    }


# ---------- UI ----------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    tanks = list_tanks()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"tanks": tanks}
    )
