"""Main orchestration script."""
from stations import STATIONS
from evaluator import evaluate_reading
from messages import format_alert
from ea_client import fetch_station_reading


def check_all_stations() -> list[dict]:
    """Fetch and evaluate readings for all configured stations."""
    results = []
    
    for station in STATIONS:
        try:
            reading = fetch_station_reading(station["id"])
        except Exception as e:
            print(f"⚠ Failed to fetch {station['id']}: {e}")
            results.append({
                "station_id": station["id"],
                "station_name": station["name"],
                "status": "error",
                "error": str(e),
            })
            continue
        
        status = evaluate_reading(
            current_level=reading["current_level"],
            warning=station["warning"],
            critical=station["critical"],
        )
        
        result = {
            "station_id": station["id"],
            "station_name": station["name"],
            "current_level": reading["current_level"],
            "reading_time": reading["reading_time"],
            "status": status,
            "message": None,
        }
        
        if status in ("warning", "critical"):
            threshold = station["critical"] if status == "critical" else station["warning"]
            result["message"] = format_alert(
                station_name=station["name"],
                river=station["river"],
                current_level=reading["current_level"],
                threshold=threshold,
                status=status,
                reading_time=reading["reading_time"],
            )
        
        results.append(result)
    
    return results


if __name__ == "__main__":
    results = check_all_stations()
    
    print(f"\nProcessed {len(results)} stations\n")
    for r in results:
        if r["status"] == "error":
            print(f"❌ {r['station_id']} ({r['station_name']}): {r['error']}")
        else:
            print(f"{r['status'].upper():9s} {r['station_id']} ({r['station_name']}): {r['current_level']}m")