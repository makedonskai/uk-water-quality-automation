"""
HTTP API for the water quality monitoring service.
Exposes endpoints that n8n (or any other client) can call.
"""
from fastapi import FastAPI, HTTPException
from main import check_all_stations
from ea_client import fetch_station_reading
from stations import STATIONS, get_station_by_id
from models import EvaluationResult, StationReading
from sqlalchemy import select
from db import Reading, SessionLocal
import logging
from config import settings
from logging_config import setup_logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)




app = FastAPI(
    title="UK Water Quality Automation API",
    description="Monitors UK river water levels and evaluates against breach thresholds.",
    version="0.1.0",
)



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
        raise HTTPException(status_code=502, detail=f"EA API error: {e}")


@app.post("/check", response_model=list[EvaluationResult])
def check_all():
    """
    Run a full check across all stations and return evaluation results.
    This is the main endpoint n8n will call to replace its HTTP node logic.
    """
    return check_all_stations()
@app.get("/readings/{station_id}")
def get_readings(station_id: str, limit: int = 20):
    """Return the most recent readings for a station."""
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