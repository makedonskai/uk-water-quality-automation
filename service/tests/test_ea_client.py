"""Tests for ea_client.py — API parsing logic."""

import json
from pathlib import Path

import httpx
import pytest
from pytest_httpx import HTTPXMock

from ea_client import EAApiError, fetch_station_reading

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

    with pytest.raises(EAApiError, match="404"):  # tenacity wraps the raised error after retries
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


def test_timeout_raises_ea_api_error(httpx_mock: HTTPXMock, monkeypatch):
    """A timeout from the API surfaces as our domain error."""
    monkeypatch.setattr(
        "ea_client.fetch_station_reading.retry.wait",
        lambda *args, **kwargs: 0,
    )
    httpx_mock.add_exception(httpx.TimeoutException("simulated timeout"))
    httpx_mock.add_exception(httpx.TimeoutException("simulated timeout"))
    httpx_mock.add_exception(httpx.TimeoutException("simulated timeout"))

    with pytest.raises(EAApiError, match="timeout"):
        fetch_station_reading("2200TH")


def test_500_raises_ea_api_error(httpx_mock: HTTPXMock, monkeypatch):
    """A 500 from the API (after retries) surfaces as our domain error."""
    monkeypatch.setattr("ea_client.fetch_station_reading.retry.wait", lambda *args, **kwargs: 0)
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/stations/2200TH/measures",
        status_code=500,
    )
    httpx_mock.add_response(  # tenacity will retry
        url="https://environment.data.gov.uk/flood-monitoring/id/stations/2200TH/measures",
        status_code=500,
    )
    httpx_mock.add_response(
        url="https://environment.data.gov.uk/flood-monitoring/id/stations/2200TH/measures",
        status_code=500,
    )

    with pytest.raises(EAApiError):
        fetch_station_reading("2200TH")
