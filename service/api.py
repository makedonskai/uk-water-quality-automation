"""HTTP API for the water quality monitoring service."""

import logging
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from config import settings
from db import Reading, SessionLocal  # зберегли ваш імпорт бази
from ea_client import fetch_station_reading
from logging_config import setup_logging
from main import check_all_stations
from models import EvaluationResult, StationReading
from stations import STATIONS, get_station_by_id

# Ініціалізація логування з вашої версії
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="UK Water Quality Automation API",
    description="Monitors UK river water levels and evaluates breach thresholds.",
    version="0.2.0",  # оновили версію
)


# --- НОВІ МОДЕЛІ ДЛЯ СТАТИСТИКИ n8n ---
class CheckSummary(BaseModel):
    """Summary stats for n8n's downstream routing."""

    timestamp: datetime
    stations_checked: int
    critical_count: int
    warning_count: int
    normal_count: int
    error_count: int


class CheckResponse(BaseModel):
    """The shape n8n expects from POST /check."""

    summary: CheckSummary
    results: list[EvaluationResult]


# ----------------------------------------


@app.get("/health")
def health() -> dict:
    """Simple healthcheck endpoint."""
    return {"status": "ok", "stations_configured": len(STATIONS)}


@app.get("/stations", response_model=list)
def list_stations():
    """List all configured stations."""
    return [s.model_dump() for s in STATIONS]


@app.get("/stations/{station_id}/reading", response_model=StationReading)
def get_reading(station_id: str):
    """Fetch the latest reading for one station."""
    if get_station_by_id(station_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown station: {station_id}")

    try:
        return fetch_station_reading(station_id)
    except Exception as e:
        logger.error(f"EA API error for station {station_id}: {e}")
        raise HTTPException(status_code=502, detail=f"EA API error: {e}") from e


@app.post("/check", response_model=CheckResponse)
def check_all() -> CheckResponse:
    """
    Run all stations, persist results, return summary + details for n8n.
    """
    logger.info("Starting full station check requested by client.")
    results = check_all_stations()

    # Рахуємо статуси для n8n (оновлено на datetime.now(timezone.utc))
    summary = CheckSummary(
        timestamp=datetime.now(UTC),
        stations_checked=len(results),
        critical_count=sum(1 for r in results if r.status == "critical"),
        warning_count=sum(1 for r in results if r.status == "warning"),
        normal_count=sum(1 for r in results if r.status == "normal"),
        error_count=sum(1 for r in results if r.status == "error"),
    )

    return CheckResponse(summary=summary, results=results)


@app.get("/readings/{station_id}")
def get_readings(station_id: str, limit: int = 20):
    """Return the most recent readings for a station from the DB."""
    with SessionLocal() as session:
        stmt = (
            select(Reading)
            .where(Reading.station_id == station_id)
            .order_by(Reading.created_at.desc())
            .limit(limit)
        )
        readings = session.scalars(stmt).all()
        return [
            {
                "station_id": r.station_id,
                "current_level": r.current_level,
                "reading_time": r.reading_time.isoformat(),
                "status": r.status,
            }
            for r in readings
        ]
