"""Main orchestration script."""
from stations import STATIONS
from evaluator import evaluate_reading
from messages import format_alert
from ea_client import fetch_station_reading
# Імпортуємо модель для результату
from models import EvaluationResult

def check_all_stations() -> list[EvaluationResult]:
    """Fetch and evaluate readings for all configured stations."""
    results: list[EvaluationResult] = []
    
    for station in STATIONS:
        try:
            reading = fetch_station_reading(station.id)
            
            status = evaluate_reading(
                current_level=reading.current_level,
                warning=station.warning,
                critical=station.critical,
            )
            
            message = None
            
               # 1. Створюємо об'єкт (повідомлення 'message' поки що порожнє за замовчуванням)
            result = EvaluationResult(
            station_id=station.id,
            station_name=station.name,
            current_level=reading.current_level,
            reading_time=reading.reading_time,
            status=status
            )
        
        # 2. Якщо статус тривожний — "вкладаємо" в об'єкт текст повідомлення
            if status in ("warning", "critical"):
            # Функція бере дані прямо з result і повертає рядок
                result.message = format_alert(result)
        
        # 3. Додаємо вже повністю готовий об'єкт у список
            results.append(result) 

            

        except Exception as e:
            print(f"⚠ Failed to fetch {station.id}: {e}")
            # Навіть помилку загортаємо в модель
            results.append(EvaluationResult(
                station_id=station.id,
                station_name=station.name,
                current_level=0.0,
                reading_time=None, # Можна зробити поле Optional в моделі
                status="error",
                error=str(e)
            ))
    
    return results


if __name__ == "__main__":
    results = check_all_stations()
    
    print(f"\nProcessed {len(results)} stations\n")
    for r in results:
        # Тепер тут теж працює автодоповнення через крапку!
        if r.status == "error":
            print(f"❌ {r.station_id} ({r.station_name}): {r.error}")
        else:
            print(f"{r.status.upper():9s} {r.station_id} ({r.station_name}): {r.current_level}m")