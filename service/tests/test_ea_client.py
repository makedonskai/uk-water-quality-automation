"""Tests for ea_client.py — API parsing logic."""

import json
from pathlib import Path

import httpx
import pytest
from pytest_httpx import HTTPXMock

from ea_client import fetch_station_reading

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file from tests/fixtures/."""
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


def test_fetch_station_reading_parses_valid_response(httpx_mock: HTTPXMock):
    """A valid API response is parsed into a StationReading."""
    fake_response = load_fixture("ea_response_2200th.json")
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/stations/2200TH/measures",
        json=fake_response,
    )

    reading = fetch_station_reading("2200TH")

    assert reading.station_id == "2200TH"
    assert reading.current_level > 0
    assert reading.unit == "mASD"


def test_fetch_station_reading_raises_on_404(httpx_mock: HTTPXMock):
    """A 404 from the API raises an HTTPError (after retries exhaust)."""
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/stations/UNKNOWN/measures",
        status_code=404,
        is_reusable=True,
    )

    with pytest.raises(httpx.HTTPStatusError):  # tenacity wraps the raised error after retries
        fetch_station_reading("UNKNOWN")


def test_fetch_station_reading_raises_when_no_level_measure(httpx_mock: HTTPXMock):
    """If response has no level/Stage measure, raise a clear ValueError."""
    bad_response = {"items": []}  # empty measures list
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/stations/EMPTY/measures",
        json=bad_response,
    )

    with pytest.raises(ValueError, match="No 'level/Stage' measure"):
        fetch_station_reading("EMPTY")
