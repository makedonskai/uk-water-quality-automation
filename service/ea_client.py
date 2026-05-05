"""
Client for the UK Environment Agency Flood Monitoring API.
"""
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from models import StationReading
from config import settings
from logging_config import setup_logging

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(settings.ea_api_max_retries),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
def fetch_station_reading(station_id: str) -> StationReading:
    """
    Fetch the latest water-level reading for a station.
    
    Returns a StationReading object.
    Raises httpx.HTTPError on network or API failure.
    """
    url = f"{settings.ea_api_base_url}/id/stations/{station_id}/measures"
    
    response = httpx.get(url, timeout=settings.ea_api_timeout_seconds)
    response.raise_for_status() 
    
    data = response.json()
    measures = data.get("items", [])
    
    level_measure = None
    for m in measures:
        if m.get("parameter") == "level" and m.get("qualifier") == "Stage":
            level_measure = m
            break
    
    if level_measure is None:
        logger.warning("measure not found", extra={"station_id": station_id})
        raise ValueError(f"No 'level/Stage' measure found for station {station_id}")
    
    latest = level_measure.get("latestReading")
    if latest is None:
        raise ValueError(f"No latest reading for station {station_id}")
    reading = StationReading(
        station_id=station_id,
        current_level=float(latest["value"]),
        reading_time=latest["dateTime"],
        unit=level_measure.get("unitName", "mASD"),
    )
    logger.info("fetched reading", extra={
        "station_id": station_id, 
        "level": reading.current_level,
        "unit": reading.unit
    })
    return reading
    
   

if __name__ == "__main__":
    setup_logging(settings.log_level)
    # Для тесту можна запустити: uv run python ea_client.py
    try:
        reading = fetch_station_reading("2200TH")
        logger.info("Test successful", extra={"reading": str(reading)})
    except Exception as e:
        logger.exception("Test failed")