"""Tests for api.py — HTTP endpoints."""

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["stations_configured"] == 5


def test_list_stations_returns_all_five():
    response = client.get("/stations")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_reading_unknown_station_returns_404():
    response = client.get("/stations/UNKNOWN/reading")
    assert response.status_code == 404
    assert "Unknown station" in response.json()["detail"]
