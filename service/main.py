"""Main orchestration script."""

import logging

from config import settings
from db import save_reading
from ea_client import fetch_station_reading
from evaluator import evaluate_reading
from logging_config import setup_logging
from messages import format_alert

# Імпортуємо модель для результату
from models import EvaluationResult
from stations import STATIONS

logger = logging.getLogger(__name__)


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
            save_reading(
                station_id=station.id,
                station_name=station.name,
                current_level=reading.current_level,
                reading_time=reading.reading_time,
                status=status,
            )
            message = None

            # 1. Створюємо об'єкт (повідомлення 'message' поки що порожнє за замовчуванням)
            result = EvaluationResult(
                station_id=station.id,
                station_name=station.name,
                current_level=reading.current_level,
                reading_time=reading.reading_time,
                status=status,
            )

            # 2. Якщо статус тривожний — "вкладаємо" в об'єкт текст повідомлення
            if status in ("warning", "critical"):
                # Функція бере дані прямо з result і повертає рядок
                result.message = format_alert(result)
                logger.warning(
                    "Flood alert triggered",
                    extra={
                        "station_id": station.id,
                        "status": status,
                        "level": reading.current_level,
                    },
                )

            # 3. Додаємо вже повністю готовий об'єкт у список
            results.append(result)
            logger.info("station processed", extra={"station_id": station.id, "status": status})

        except Exception as e:
            logger.exception("failed to process station", extra={"station_id": station.id})
            results.append(
                EvaluationResult(
                    station_id=station.id,
                    station_name=station.name,
                    current_level=0.0,
                    reading_time=None,  # Можна зробити поле Optional в моделі
                    status="error",
                    error=str(e),
                )
            )

    return results


if __name__ == "__main__":
    setup_logging(settings.log_level)

    logger.info("starting flood check orchestration")
    results = check_all_stations()

    logger.info("orchestration complete", extra={"processed_count": len(results)})

    for r in results:
        # Тепер тут теж працює автодоповнення через крапку!
        if r.status == "error":
            logger.error(
                "station check error",
                extra={"station_id": r.station_id, "error": r.error},
            )
        else:
            logger.info(
                "result summary",
                extra={
                    "status": r.status,
                    "station": r.station_id,
                    "level": r.current_level,
                },
            )
