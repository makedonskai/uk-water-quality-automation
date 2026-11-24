Source: https://environment.data.gov.uk/flood-monitoring/doc/reference
Retrieved: 2026-11-24

# Environment Agency Real Time flood-monitoring API

## Introduction

The Environment Agency flood-monitoring API provides developers with access to near real time information covering:

- flood warnings and flood alerts
- flood areas which to which warnings or alerts apply
- measurements of water levels and flows
- information on the monitoring stations providing those measurements

Water levels and flows are regularly monitored, usually every 15 minutes. However, data is transferred back to the Environment Agency at various frequencies, usually depending on the site and level of flood risk. Transfer of data is typically once or twice per day, but usually increases during times of heightened flood risk.

These APIs are provided as open data under the Open Government Licence with no requirement for registration. If you make use of this data please acknowledge this with the following attribution statement:

this uses Environment Agency flood and river level data from the real-time data API (Beta)

## Availability and resilience

While they are intended to be stable and robust the open data APIs do not offer a guarantee of service level and should not be relied upon for safety critical applications. They do not replace the existing channels by which the Agency notifies members of the public and partner organizations of floods and flood risk.

Redirects. At times of high load or in future versions of this API the service may redirect to an alternative URL. Client code should be written so as to follow standard HTTP redirects.

Caching. API responses may be cached for a short period within the serving infrastructure or a content delivery network. At times of high load then limiting API use to common patterns (avoiding custom filtering) will improve the chances of cache hits and so good response times. These common patterns are:

- https://environment.data.gov.uk/flood-monitoring/id/floods
- https://environment.data.gov.uk/flood-monitoring/id/floods?min-severity={x}
- https://environment.data.gov.uk/flood-monitoring/id/3dayforecast
- https://environment.data.gov.uk/flood-monitoring/id/3dayforecast/image/{day}
- https://environment.data.gov.uk/flood-monitoring/data/readings?latest

## Flood warnings

The Environment Agency issue warnings of floods that cover specific warning or alert areas. The floods API provides a listing of all current such warnings and is updated every 15 minutes.

A warning may be at one of four possible severity levels:

| Level | Name | Meaning |
|---|---|---|
| 1 | Severe Flood Warning | Severe Flooding, Danger to Life. |
| 2 | Flood Warning | Flooding is Expected, Immediate Action Required. |
| 3 | Flood Alert | Flooding is Possible, Be Prepared. |
| 4 | Warning no Longer in Force | The warning is no longer in force |

## Stations — scale information (thresholds)

The information returned for an individual station is enriched by also including scale information for those stations for which this is available.

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| stageScale | Scale information for the main stage water level measurement. | rt:Scale |  |
| downstageScale | Scale information for the downstream water level measurement, if available. | rt:Scale |  |

In each case the scale information is an object with the following fields:

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| highestRecent | The highest reading for this measurement in recent times (typically the last 5 years) | rt:Reading |  |
| maxOnRecord | The highest reading for this measurement on record | rt:Reading |  |
| minOnRecord | The lowest reading for this measurement on record | rt:Reading |  |
| scaleMax | The maximum of the scale suitable for displaying this measurement. | xsd:decimal |  |
| typicalRangeHigh | The top of the typical range band - the measurement exceeded this for 5% of the relevant data on record | xsd:decimal |  |
| typicalRangeLow | The bottom of the typical range band - the measurement exceeded this for 95% of the relevant data on record | xsd:decimal |  |

## Measures

The list of currently available types of measurement are:

| parameterName | parameter (short name) | Comments |
|---|---|---|
| Water Level | level | Water level, see qualifier for whether stage or downstream of the stage, see unitName for whether relative to the stage datum (mASD) or to the ordnance datum. |
| Flow | flow | Water flow rate, only available from some stations. The units of measurement vary between stations so check the unitName carefully. |
| Wind | wind | Wind direction and speed available from some stations. The qualifier will indicate whether direction (degrees) or speed (knots or m/s). |
| Temperature | temperature | Dry bulb air temperature measurement available from some stations. |

## Readings

Readings for each of the published measures are available for the recent period (up to the last four weeks). Longer historic data records may be available separately. Each reading comprises a reference to the measure being read (identified by its URI), a date time stamp for when the reading applies and a numeric value. The set of readings is updated every 15 minutes, but the individual measures may be updated less frequently than this.
