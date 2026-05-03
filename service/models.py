"""
Pydantic data models for the water quality automation system.

Why Pydantic:
- Runtime validation: bad data raises an error immediately, not 50 lines later
- Type safety: VSCode autocomplete works on field names
- Serialisation: .model_dump() gives you a dict, .model_dump_json() gives JSON
- Schemas: FastAPI auto-generates OpenAPI docs from these models
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class StationConfig(BaseModel):
    """Configuration for one monitoring station."""
    id: str = Field(..., description="EA station ID, e.g. '2200TH'")
    name: str
    river: str
    warning: float = Field(..., gt=0, description="Warning threshold in meters")
    critical: float = Field(..., gt=0, description="Critical threshold in meters")


class StationReading(BaseModel):
    """A single reading from the EA API."""
    station_id: str
    current_level: float
    reading_time: datetime
    unit: str = "mASD"  # "meters Above Site Datum" — EA's typical unit


class EvaluationResult(BaseModel):
    """The result of evaluating a reading against thresholds."""
    station_id: str
    station_name: str
    current_level: float
    reading_time: datetime| None = None
    status: Literal["normal", "warning", "critical", "error"]
    message: str | None = None
    error: str | None = None