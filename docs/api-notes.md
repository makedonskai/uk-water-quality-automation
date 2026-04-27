# UK Flood Monitoring API — Notes

## API base URL

https://environment.data.gov.uk/flood-monitoring

## Selected stations (5)

### 1. Kingston Upon Thames

- notation: 3400TH
- river: River Thames
- measure URL (water level):
  http://environment.data.gov.uk/flood-monitoring/id/measures/3400TH-level-stage-i-15_min-mASD

### 2. Walthamstow, Low Hall

- notation: 5380TH
- catchment: Lower Lee
- measure URL:
  http://environment.data.gov.uk/flood-monitoring/id/measures/5380TH-level-downstage-i-15_min-mASD

### 3. The Ching

    "notation" : "5376TH" ,
    "riverName" : "Ching Brook" ,
    - measure URL:
    "http://environment.data.gov.uk/flood-monitoring/id/measures/5376TH-level-stage-i-15_min-mASD"

### 4. Pool

    "notation" : "4369TH" ,
    "riverName" : "River Pool" ,
    - measure URL:
    "http://environment.data.gov.uk/flood-monitoring/id/measures/4369TH-level-stage-i-15_min-mASD"

### 5. Wandle

    "notation" : "4150TH" ,
    "riverName" : "River Wandle"

- measure URL:"http://environment.data.gov.uk/flood-monitoring/id/measures/4150TH-level-stage-i-15_min-mASD"

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
