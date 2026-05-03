"""
Defines the 5 UK water monitoring stations and their thresholds.
This replaces the 'Define stations' Code node from the n8n workflow.
"""
STATIONS = [
    {
        "id": "2200TH",
        "name": "Reading",
        "river": "Thames",
        "warning": 7.0,
        "critical": 7.3,
    },
    {
        "id": "3400TH",
        "name": "Kingston",
        "river": "Thames",
        "warning": 3.97,
        "critical": 4.2,
    },
    {
        "id": "5380TH",
        "name": "Walthamstow Low Hall",
        "river": "Lee",
        "warning": 1.35,
        "critical": 1.50,
    },
    {
        "id": "3404TH",
        "name": "Sunbury Lock",
        "river": "Thames",
        "warning": 0.17,
        "critical": 0.30,
    },
    {
        "id": "4150TH",
        "name": "Merton",
        "river": "Wandle",
        "warning": 0.38,
        "critical": 0.60,
    },
]


def get_station_by_id(station_id: str) -> dict | None:
    """Return the station config matching the given ID, or None if not found."""
    for station in STATIONS:
        if station["id"] == station_id:
            return station
    return None
if __name__ == "__main__":
    print(f"Loaded {len(STATIONS)} stations")
    for s in STATIONS:
        print(f"  {s['id']}: {s['name']} ({s['river']}) — warning={s['warning']}m")