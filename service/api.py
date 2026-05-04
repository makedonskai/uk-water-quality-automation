"""
HTTP API for the water quality monitoring service.
Exposes endpoints that n8n (or any other client) can call.
"""
from fastapi import FastAPI, HTTPException
from main import check_all_stations
from ea_client import fetch_station_reading
from stations import STATIONS, get_station_by_id
from models import EvaluationResult, StationReading

app = FastAPI(
    title="UK Water Quality Automation API",
    description="Monitors UK river water levels and evaluates against breach thresholds.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    """Liveness check."""
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
        raise HTTPException(status_code=502, detail=f"EA API error: {e}")


@app.post("/check", response_model=list[EvaluationResult])
def check_all():
    """
    Run a full check across all stations and return evaluation results.
    This is the main endpoint n8n will call to replace its HTTP node logic.
    """
    return check_all_stations()