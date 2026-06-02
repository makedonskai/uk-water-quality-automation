"""Tests for models.py — Pydantic validation."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from models import StationConfig, StationReading


def test_valid_station_config():
    """A well-formed station config validates successfully."""
    config = StationConfig(
        id="2200TH",
        name="Reading",
        river="Thames",
        warning=7.0,
        critical=7.3,
    )
    assert config.id == "2200TH"
    assert config.warning == 7.0


def test_negative_warning_threshold_rejected():
    """Pydantic should reject a station with a negative warning threshold."""
    with pytest.raises(ValidationError) as exc_info:
        StationConfig(
            id="X",
            name="Test",
            river="Test",
            warning=-1.0,
            critical=2.0,
        )
    # Optional but good: assert the error message mentions the bad field
    assert "warning" in str(exc_info.value).lower()


def test_zero_warning_threshold_rejected():
    """Threshold must be strictly greater than zero."""
    with pytest.raises(ValidationError):
        StationConfig(
            id="X",
            name="Test",
            river="Test",
            warning=0.0,
            critical=2.0,
        )


def test_station_reading_parses_iso_timestamp():
    """Pydantic auto-converts ISO timestamp strings to datetime objects."""
    reading = StationReading(
        station_id="2200TH",
        current_level=6.5,
        reading_time="2026-05-01T14:30:00Z",
    )
    assert isinstance(reading.reading_time, datetime)
    assert reading.reading_time.year == 2026
