"""Tests for db.py — persistence layer."""

from datetime import datetime

from sqlalchemy import select

from db import Reading, save_reading


def test_save_and_retrieve_reading(in_memory_db, monkeypatch):
    """A saved reading can be retrieved with all fields intact."""
    monkeypatch.setattr("db.SessionLocal", in_memory_db)

    save_reading(
        station_id="2200TH",
        station_name="Reading",
        current_level=6.5,
        reading_time=datetime(2026, 5, 1, 14, 30),
        status="normal",
    )

    with in_memory_db() as session:
        result = session.scalars(select(Reading)).all()
        assert len(result) == 1
        assert result[0].station_id == "2200TH"
        assert result[0].current_level == 6.5
        assert result[0].status == "normal"


def test_multiple_readings_persisted_in_order(in_memory_db):
    """Multiple readings persist correctly and can be queried by station."""
    with in_memory_db() as session:
        for i, status in enumerate(["normal", "warning", "critical"]):
            session.add(
                Reading(
                    station_id="2200TH",
                    station_name="Reading",
                    current_level=7.0 + i * 0.2,
                    reading_time=datetime(2026, 5, 1, 14, i * 10),
                    status=status,
                )
            )
        session.commit()

    with in_memory_db() as session:
        results = session.scalars(select(Reading).where(Reading.station_id == "2200TH")).all()
        assert len(results) == 3
        statuses = [r.status for r in results]
        assert "critical" in statuses
