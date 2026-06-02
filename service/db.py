"""
Database layer using SQLAlchemy + SQLite.
SQLite for now; swap to Postgres in Week 3 (one config line will change).
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config import settings
from logging_config import setup_logging

logger = logging.getLogger(__name__)


engine = create_engine(settings.database_url, echo=(settings.log_level == "DEBUG"))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Reading(Base):
    """One historical reading, persisted for audit + analysis."""

    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str] = mapped_column(String(20), index=True)
    station_name: Mapped[str] = mapped_column(String(100))
    current_level: Mapped[float] = mapped_column(Float)
    reading_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


def init_db() -> None:
    """Create tables. Call once on startup."""
    Base.metadata.create_all(engine)


def save_reading(
    station_id: str,
    station_name: str,
    current_level: float,
    reading_time: datetime,
    status: str,
) -> None:
    """Persist one evaluated reading."""
    with SessionLocal() as session:
        reading = Reading(
            station_id=station_id,
            station_name=station_name,
            current_level=current_level,
            reading_time=reading_time,
            status=status,
        )
        session.add(reading)
        session.commit()
        logger.info(
            "database record saved",
            extra={"station_id": station_id, "status": status, "level": current_level},
        )


if __name__ == "__main__":
    setup_logging(settings.log_level)
    init_db()
    logger.info("Database initialised", extra={"db_url": settings.database_url})
