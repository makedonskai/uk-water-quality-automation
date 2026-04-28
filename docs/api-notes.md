# UK Flood Monitoring API — Notes

## API base URL

https://environment.data.gov.uk/flood-monitoring

## Selected stations (5)

### 1. Kingston Upon Thames

- notation: 3400TH
- river: River Thames
- measure URL (water level):
  http://environment.data.gov.uk/flood-monitoring/id/measures/3400TH-level-stage-i-15_min-mASD//readings?_limit=5&_sorted

### 2. Walthamstow, Low Hall

- notation: 5380TH
- catchment: Lower Lee
- measure URL:
  http://environment.data.gov.uk/flood-monitoring/id/measures/5380TH-level-downstage-i-15_min-mASD//readings?_limit=5&_sorted

### 3. Cherwell Thame and Wye

    "notation" : "2200TH" ,
    "riverName" : "River Thames
    ,
    - measure URL:
    http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-level-stage-i-15_min-mASD/readings?_limit=5&_sorted

### 4. Trowlock Island

    notation" : "3404TH" ,
    "riverName" : "River Thames"
    - measure URL:http://environment.data.gov.uk/flood-monitoring/id/measures/3404TH-level-stage-i-15_min-mAOD/readings?_limit=5&_sorted

### 5. Wandle

    "notation" : "4150TH" ,
    "riverName" : "River Wandle"

- measure URL:"http://environment.data.gov.uk/flood-monitoring/id/measures/4150TH-level-stage-i-15_min-mASD//readings?_limit=5&_sorted

## Key findings

- `parameter: "level"` = water level (це нам потрібно)
- `parameterName: "Water Level"` — friendly name
- `qualifier: "Stage"` = upstream, "Downstream Stage" = downstream
- `unitName: "mASD"` = meters Above Stage Datum (relative to local zero)
- `unitName: "mAOD"` = meters Above Ordnance Datum (sea level reference)
- `period: 900` = readings every 900 seconds (= 15 min)

## Pagination

- Default limit: 100 results
- Use `_limit=20` to limit
- Use `_offset=20` to skip first 20

## Filters

- `?riverName=River%20Thames` — only Thames stations
- `?lat=51.5074&long=-0.1278&dist=15` — within 15 km of point

## Reading structure (from API)

Кожне вимірювання — JSON об'єкт з полями:

- `@id` — унікальний ідентифікатор
- `dateTime` — час у форматі ISO 8601 UTC (e.g. "2026-04-28T07:30:00Z")
- `measure` — посилання на measure
- `value` — числове значення в одиницях measure (для level → метри)

## Frequency

Дані оновлюються кожні **15 хвилин** (period: 900 секунд).

## URL для отримання останніх N вимірювань

https://environment.data.gov.uk/flood-monitoring/id/measures/{MEASURE_ID}/readings?_limit={N}&_sorted

Параметри:

- `_limit=N` — обмежити кількість результатів
- `_sorted` — сортувати від нових до старих
- `since=YYYY-MM-DDTHH:MM:SSZ` — отримати тільки після цієї дати
