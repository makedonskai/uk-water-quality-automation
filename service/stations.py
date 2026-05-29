"""
Defines the 5 UK water monitoring stations and their thresholds.
"""

import logging

from config import settings
from logging_config import setup_logging
from models import StationConfig

logger = logging.getLogger(__name__)

STATIONS: list[StationConfig] = [
    StationConfig(id="2200TH", name="Reading", river="Thames", warning=7.0, critical=7.3),
    StationConfig(id="3400TH", name="Kingston", river="Thames", warning=3.97, critical=4.2),
    StationConfig(
        id="5380TH",
        name="Walthamstow Low Hall",
        river="Lee",
        warning=1.35,
        critical=1.50,
    ),
    StationConfig(id="3404TH", name="Sunbury Lock", river="Thames", warning=0.17, critical=0.30),
    StationConfig(id="4150TH", name="Merton", river="Wandle", warning=0.38, critical=0.60),
]


# ВИПРАВЛЕНО: Тип повернення тепер StationConfig | None
def get_station_by_id(station_id: str) -> StationConfig | None:
    """Return the station config matching the given ID, or None if not found."""
    for station in STATIONS:
        # ВИПРАВЛЕНО: Використовуємо station.id замість station["id"]
        if station.id == station_id:
            return station
    return None


if __name__ == "__main__":
    setup_logging(settings.log_level)
    logger.info("stations loaded", extra={"count": len(STATIONS)})
    for s in STATIONS:
        logger.info(
            "station config",
            extra={"id": s.id, "name": s.name, "river": s.river, "warning_m": s.warning},
        )
