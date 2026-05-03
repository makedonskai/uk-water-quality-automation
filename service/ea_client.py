"""
Client for the UK Environment Agency Flood Monitoring API.
"""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from models import StationReading

EA_BASE_URL = "https://environment.data.gov.uk/flood-monitoring"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
def fetch_station_reading(station_id: str) -> StationReading:
    """
    Fetch the latest water-level reading for a station.
    
    Returns a StationReading object.
    Raises httpx.HTTPError on network or API failure.
    """
    url = f"{EA_BASE_URL}/id/stations/{station_id}/measures"
    
    response = httpx.get(url, timeout=10.0)
    response.raise_for_status() 
    
    data = response.json()
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
    
    # ВИПРАВЛЕНО: Використовуємо '=', а не ':'
    return StationReading(
        station_id=station_id,
        current_level=float(latest["value"]),
        reading_time=latest["dateTime"],
        unit=level_measure.get("unitName", "mASD"),
    )

if __name__ == "__main__":
    # Для тесту можна запустити: uv run python ea_client.py
    try:
        reading = fetch_station_reading("2200TH")
        print(f"✅ Успішно! Станція: {reading.station_id}, Рівень: {reading.current_level}{reading.unit}")
        print(f"Об'єкт: {reading}")
    except Exception as e:
        print(f"❌ Помилка: {e}")