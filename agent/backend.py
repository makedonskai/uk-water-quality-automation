"""
Backend for the water-level duty-operator agent.

Three tools form a chain:
    find_station  ->  get_latest_level  ->  send_alert
Only find_station hands out station_id, so the model cannot skip it.

Stage 1: readings come from fixed fake scenarios (see _read_latest).
Stage 2: _read_latest will call the EA Flood Monitoring API instead.
"""

import inspect
import json
import os
from datetime import datetime

from config import ALERTS_DIR, FAKE_NOW, STALE_AFTER_MIN

# ── stations ──────────────────────────────────────────────────
# Keys are internal ids. The model only learns them from find_station.
# Thresholds copied once from data/reference/thresholds.csv (metres).
STATIONS = {
    "st_7f3a": {"name": "Reading", "river": "River Thames",
                "ea_code": "2200TH", "warning_m": 7.0, "critical_m": 7.3},
    "st_k29d": {"name": "Kingston", "river": "River Thames",
                "ea_code": "3400TH", "warning_m": 3.97, "critical_m": 4.2},
    "st_m81c": {"name": "Merton", "river": "River Wandle",
                "ea_code": "4150TH", "warning_m": 0.38, "critical_m": 0.60},
    "st_w4e0": {"name": "Walthamstow Low Hall", "river": "River Lee",
                "ea_code": "5380TH", "warning_m": 1.35, "critical_m": 1.50},
    "st_s6b2": {"name": "Sunbury Lock", "river": "River Thames",
                "ea_code": "3404TH", "warning_m": 0.17, "critical_m": 0.30},
}

# ── data source (the only part to replace in stage 2) ─────────
# One scenario per station. FAKE_NOW is 2026-11-22 09:00 UTC.
_FAKE_READINGS = {
    "2200TH": {"value_m": 6.80, "measured_at": "2026-11-22T08:45:00Z"},  # normal
    "3400TH": {"value_m": 4.05, "measured_at": "2026-11-22T08:45:00Z"},  # warning
    "4150TH": {"value_m": 0.72, "measured_at": "2026-11-22T08:45:00Z"},  # critical
    "5380TH": {"value_m": 1.40, "measured_at": "2026-11-19T08:45:00Z"},  # stale
    "3404TH": {"value_m": None, "measured_at": "2026-11-22T08:45:00Z"},  # unknown
}


def _read_latest(ea_code: str) -> dict:
    """Return the latest reading: {"value_m": float | None, "measured_at": ISO str}."""
    return dict(_FAKE_READINGS[ea_code])


def _now() -> datetime:
    """Current time. Fixed in stage 1 so tests do not depend on the clock."""
    return FAKE_NOW


# ── rule computed by Python, not by the model ─────────────────
def evaluate(value_m, measured_at: datetime, warning_m: float,
             critical_m: float) -> str:
    """Return unknown | stale | critical | warning | normal.

    Order matters: missing and stale data are checked before the level,
    so an old high reading never counts as a current breach.
    Boundaries use >= like service/evaluator.py.
    """
    if value_m is None:
        return "unknown"
    age_min = (_now() - measured_at).total_seconds() / 60
    if age_min > STALE_AFTER_MIN:
        return "stale"
    if value_m >= critical_m:
        return "critical"
    if value_m >= warning_m:
        return "warning"
    return "normal"


def _assess(station_id: str) -> dict:
    """Read the latest value for a known station and attach its status."""
    s = STATIONS[station_id]
    reading = _read_latest(s["ea_code"])
    measured_at = datetime.fromisoformat(reading["measured_at"])
    return {
        "station_id": station_id,
        "name": s["name"],
        "river": s["river"],
        "level_m": reading["value_m"],
        "measured_at": reading["measured_at"],
        "age_min": int((_now() - measured_at).total_seconds() // 60),
        "warning_m": s["warning_m"],
        "critical_m": s["critical_m"],
        "status": evaluate(reading["value_m"], measured_at,
                           s["warning_m"], s["critical_m"]),
    }


# ── tools ─────────────────────────────────────────────────────
def find_station(query: str) -> dict:
    if not isinstance(query, str) or not query.strip():
        return {"error": "bad_args", "hint": "query must be a non-empty string."}
    q = query.strip().lower()
    matches = []
    for station_id, s in STATIONS.items():
        name, river = s["name"].lower(), s["river"].lower()
        words = (name + " " + river).split()
        if q in (name, river) or q in words:
            matches.append({"station_id": station_id,
                            "name": s["name"], "river": s["river"]})
    if not matches:
        return {"error": "not_found",
                "hint": "No monitored station matches. Known stations: "
                        + ", ".join(s["name"] for s in STATIONS.values())}
    return {"stations": matches}


def _known(station_id) -> bool:
    """True only for a string id that exists (a list or number is never valid)."""
    return isinstance(station_id, str) and station_id in STATIONS


def get_latest_level(station_id: str) -> dict:
    if not _known(station_id):
        return {"error": "station_not_found",
                "hint": "Use a station_id returned by find_station."}
    return _assess(station_id)


def _confirm(prompt: str) -> bool:
    """Ask a human. Empty answer means no.

    AUTO_CONFIRM=y|n skips the question (used in tests).
    Later this can become a Telegram button without touching send_alert.
    """
    auto = os.getenv("AUTO_CONFIRM")
    if auto is not None:
        return auto.strip().lower() == "y"
    try:
        answer = input(prompt)
    except (EOFError, OSError):      # no terminal to ask, so the answer is no
        return False
    return answer.strip().lower() in ("y", "yes")


def send_alert(station_id: str, reason: str) -> dict:
    # 1. unknown station
    if not _known(station_id):
        return {"error": "station_not_found",
                "hint": "Use a station_id returned by find_station."}

    # 2. status is recomputed here; the model's opinion is not trusted
    check = _assess(station_id)
    if check["status"] not in ("warning", "critical"):
        return {"error": "not_alertable", "status": check["status"],
                "hint": "Alerts are sent only for fresh warning/critical readings."}

    # 3. one alert per reading: key = station_id + reading time
    stamp = check["measured_at"].replace(":", "").replace("-", "")
    path = ALERTS_DIR / f"{station_id}_{stamp}.json"
    if path.exists():
        return {"status": "already_sent", "alert_file": path.name}

    # 4. human confirmation
    prompt = (f"Send {check['status']} alert for {check['name']} "
              f"({check['level_m']} m at {check['measured_at']})? [y/N] ")
    if not _confirm(prompt):
        return {"status": "declined_by_user"}

    # 5. side effect: stage 1 writes a JSON file instead of Telegram
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    record = {**check, "reason": reason, "sent_at": _now().isoformat()}
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    return {"status": "sent", "alert_file": path.name,
            "alert_status": check["status"]}


# ── tool schemas for the model (contract) ─────────────────────
TOOLS = [
    {"type": "function", "function": {
        "name": "find_station",
        "description": (
            "Find monitored river-level stations by station name or river name "
            "(case-insensitive, whole word, e.g. 'Kingston' or 'Thames'). "
            "Returns {stations: [{station_id, name, river}]}. This is the ONLY "
            "source of station_id. Several matches mean the request is "
            "ambiguous: list them and ask the user to choose. "
            "Error not_found means the station is not monitored."),
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string",
                                     "description": "Station or river name."}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "get_latest_level",
        "description": (
            "Latest water LEVEL for one station, in metres: level_m, "
            "measured_at (UTC), age_min, warning_m, critical_m and status "
            "(normal | warning | critical | stale | unknown). The status is "
            "computed by code: report it as given, do not recompute it. "
            "station_id must come from find_station. Does NOT forecast "
            "floods and does NOT measure water quality."),
        "parameters": {
            "type": "object",
            "properties": {"station_id": {"type": "string"}},
            "required": ["station_id"]}}},
    {"type": "function", "function": {
        "name": "send_alert",
        "description": (
            "Send an operations alert for a station whose latest reading is "
            "warning or critical. Has real consequences: a human must "
            "confirm, and you get status sent | declined_by_user | "
            "already_sent, or error not_alertable / station_not_found. "
            "Only say the alert was sent if status is 'sent'. "
            "station_id must come from find_station."),
        "parameters": {
            "type": "object",
            "properties": {
                "station_id": {"type": "string"},
                "reason": {"type": "string",
                           "description": "One short sentence for operators."}},
            "required": ["station_id", "reason"]}}},
]

IMPL = {
    "find_station": find_station,
    "get_latest_level": get_latest_level,
    "send_alert": send_alert,
}


def dispatch(name: str, args: dict) -> dict:
    fn = IMPL.get(name)
    if fn is None:
        return {"error": "unknown_tool", "tool": name}
    # 1. model's mistake: missing or extra argument names
    try:
        inspect.signature(fn).bind(**args)
    except TypeError as e:
        return {"error": "bad_args", "detail": str(e)}
    # 2. our bug: the tool itself raised; keep the agent alive but say so
    try:
        return fn(**args)
    except Exception as e:
        return {"error": "tool_crashed", "detail": f"{type(e).__name__}: {e}"}
