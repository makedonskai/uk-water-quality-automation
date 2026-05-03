"""
Client for the UK Environment Agency Flood Monitoring API.
Replaces n8n's HTTP Request node.

API docs: https://environment.data.gov.uk/flood-monitoring/doc/reference
No auth required, public open data.
"""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

EA_BASE_URL = "https://environment.data.gov.uk/flood-monitoring"
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
def fetch_station_reading(station_id: str) -> dict:
    """
    Fetch the latest water-level reading for a station.
    
    Returns a dict with: station_id, current_level, reading_time, unit.
    Raises httpx.HTTPError on network or API failure.
    """
    url = f"{EA_BASE_URL}/id/stations/{station_id}/measures"
    
    response = httpx.get(url, timeout=10.0)
    response.raise_for_status()  # raises if status >= 400
    
    data = response.json()
    
    # The API returns a list of 'measures' (level, flow, etc.)
    # We want the level measure with parameter 'level' and qualifier 'Stage'.
    measures = data.get("items", [])
    
    level_measure = None
    for m in measures:
        if m.get("parameter") == "level" and m.get("qualifier") == "Stage":
            level_measure = m
            break
    
    if level_measure is None:
        raise ValueError(f"No 'level/Stage' measure found for station {station_id}")
    
    latest = level_measure.get("latestReading")
    if latest is None:
        raise ValueError(f"No latest reading for station {station_id}")
    
    return {
        "station_id": station_id,
        "current_level": float(latest["value"]),
        "reading_time": latest["dateTime"],
        "unit": level_measure.get("unitName", "unknown"),
    }

if __name__ == "__main__":
    reading = fetch_station_reading("2200TH")
    print(reading)