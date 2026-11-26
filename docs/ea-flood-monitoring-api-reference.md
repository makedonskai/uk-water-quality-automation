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

## Note on crawling

A common requirement is for an application to maintain a copy of all the latest level/flow values from some (or all) of the measurement stations. The efficient way to do this is to issue a single call every 15 mins:

https://environment.data.gov.uk/flood-monitoring/data/readings?latest

This will retrieve the latest value for all measurements - from which you can pick the ones you are interested. Since the data changes at most every 15 mins then this single call four times an hour will ensure a complete track of all of the data.

This is much preferable to crawling all the stations every 15 mins picking up a single latest value for each station one at a time.

However, this is not sufficient to maintain a complete historical trace since readings are sometimes updated batches. For that purpose a query for the relevant station readings using the since filter is appropriate.

## Availability and resilience

While they are intended to be stable and robust the open data APIs do not offer a guarantee of service level and should not be relied upon for safety critical applications. They do not replace the existing channels by which the Agency notifies members of the public and partner organizations of floods and flood risk.

Redirects. At times of high load or in future versions of this API the service may redirect to an alternative URL. Client code should be written so as to follow standard HTTP redirects.

Caching. API responses may be cached for a short period within the serving infrastructure or a content delivery network. At times of high load then limiting API use to common patterns (avoiding custom filtering) will improve the chances of cache hits and so good response times. These common patterns are:

- https://environment.data.gov.uk/flood-monitoring/id/floods
- https://environment.data.gov.uk/flood-monitoring/id/floods?min-severity={x}
- https://environment.data.gov.uk/flood-monitoring/id/3dayforecast
- https://environment.data.gov.uk/flood-monitoring/id/3dayforecast/image/{day}
- https://environment.data.gov.uk/flood-monitoring/data/readings?latest

## Recent updates

Version 0.8: Added access to Rainfall data.

Version 0.7:

- Added fine grain since filter for readings.
- Added _view=full option for listing stations (includes scale information).
- Implemented geo-filter for flood warning areas.
- Added support station status data where available (status, statusReason, statusDate).
- Added support for Last-Modified headers and If-Modified-Since requests
- Added html view options for APIs that return lists of results.
- Improved detection of bad API requests.
- Changes to underlying platform may affect the order of columns in CSV results but not the columns themselves.

Version 0.6.1: Enabled filters for station type and status.

Version 0.6: Added support CSV format out for listing stations. Include lat/long and easting/northing in stations listing.

## API summary — Flood warnings

This is a brief summary of the APIs available. In the links in the tables {root} corresponds to https://environment.data.gov.uk/flood-monitoring.

| What | API | Parameters |
|---|---|---|
| All flood warnings and alerts: | {root}/id/floods | min-severity, county, lat=y&long=x&dist=r |

## API summary — Real time measurements

| What | API | Filters |
|---|---|---|
| All measurement stations: | {root}/id/stations | parameter=p, parameterName=pn, qualifier=q, town=t, catchmentName=c, riverName=r, RLOIid=r, lat=y&long=x&dist=r, search=x (text in label), status=s, type=t |
| All measures available from a particular station | {root}/id/stations/{id}/measures |  |
| All measures from across all the stations: | {root}/id/measures | parameter=p, parameterName=pn, qualifier=q, stationReference=id, station=uri |
| All readings for all measures from across all the stations: | {root}/data/readings | latest, today, date=d, startdate=d1&enddate=d2, parameter=p, parameterName=pn, qualifier=q, stationReference=id, station=uri, _view=full, _sorted |
| All readings for a particular measure: | {root}/id/measures/{id}/readings | latest, today, date=d, startdate=d1&enddate=d2, since=dt, _view=full, _sorted |
| All readings for measures from a particular station: | {root}/id/stations/{id}/readings | latest, today, date=d, startdate=d1&enddate=d2, since=dt, _view=full, _sorted |

## API structure — Simple requests

The APIs provide a REST style access to the data via simple HTTP GET requests which return data in JSON format. Some data is also available in other formats.

For example fetching data from: https://environment.data.gov.uk/flood-monitoring/id/floods

will return a JSON data packet such as:

The returned JSON data from all API endpoints follows the same structure of three elements: context, metadata and item(s).

The @context reference is provided to enable the JSON data to be read as json-ld.

## API structure — Metadata and versioning

The metadata block:

provides information on the publisher and applicable licence as well as a link to this, or other, documentation. If the resource is also available in other formats then hasFormat will supply list of URLs for those alternative formats (the media type is implied a suffix, see content types).

The metadata block also includes version number information. The intention is that updates to the API should maintain backward compatibility. If an incompatible change to the API is required then we will attempt to provide access to the prior version for a transitional period. In that case the meta block will also provide replaces and isReplacedBy links between the new and the old versions of the affected API endpoints.

Finally, in the case of calls which provide lists of results then any applied limit to the length of the list and offset from the start of the list will be shown in the metadata as limit and offset values, for example:

Note that some endpoints impose a length limit even if one has not be specified explicitly by the caller. The metadata is particularly useful in this case as a warning that this has occurred.

## API structure — Items

The items element in the JSON response will contain either a description of a single item or an array of items. For API endpoints which return lists of items (e.g. all measurement stations of a certain kind) then value will always be an array even if the list only has one entry. For API endpoints which describe a specific item (e.g. a particular measurement station) the value will always be an object, with no wrapping array.

Each item will normally be identified by a URI given in the @id field. Thus, for example in the fuller version of the earlier example:

we can see the flood warning itself has an identifier (note that warnings have a limited lifetime so this URL isn't live any more):

https://environment.data.gov.uk/flood-monitoring/id/floods/91436

as does the flood area to which the warning applies:

https://environment.data.gov.uk/flood-monitoring/id/floodAreas/122WAC953

When one item references another, such as in this case, the API will typically include key attributes of the referenced item in-line for convenience. However, we can always fetch (GET) data from the reference item URI to obtain a full description. For example, dereferencing the flood area URI returns:

Many of these URIs are stable long term reference identifiers e.g. the flood areas, the measurement stations and the individual measurement types are stable. However, some items may only be transient. For example, the URI for an individual flood alert may only remain valid for a few days. The severity of the alert, and associated message, may change over that time eventually reducing to severity level 4 (Warning no longer in force). After that the alert will disappear and that URI will no longer resolve, returning a 404.

## API structure — Content Types

The descriptions of individual items can be obtained in multiple formats. The default format is JSON but all item descriptions can also return information in RDF formats (RDF/XML and Turtle). In addition some items offer a simple HTML rendering which makes it possible to look at these reference identifiers conveniently in a browser. The HTML rendering is intended as an aid to help developers understand the data, it is not an end-user application.

Similarly lists of items can be obtained in multiple formats. The default is JSON (in which the items field will contain an array of objects) but they are also typically also available in CSV format.

To select the desired format use standard HTTP content negation. E.g.:

`curl -i -H "Accept: text/turtle" https://environment.data.gov.uk/flood-monitoring/id/floodAreas/122WAC953`

All endpoints also support a short cut of appending a type suffix to the URI to force a particular content type. The supported suffixes are:

| Suffix | Type |
|---|---|
| .json | application/json |
| .ttl | text/turtle |
| .rdf | application/rdf+xml |
| .html | text/html |
| .csv | text/csv |

## API structure — Lists: filtering and paging

Some endpoints return information describing a single identified item but many return information on a list of items. In that case the value of the items field is an array of items. Such list endpoints support query parameters to filter the list to only include some items, for example:

https://environment.data.gov.uk/flood-monitoring/id/floods?min-severity=3

returns a list of all flood alerts and warnings which are of severity 3 of worse.

The specific filters available depend on the endpoint and are documented in the following tables. Though many endpoints will support two common filters:

| Query | Meaning |
|---|---|
| ?search=x | Return only those items whose label contains x |
| ?lat=y&long=x&dist=d | return those items whose location falls within d km of the given latitude/longitude (in WGS84 coordinates), this may be approximated by a bounding box. |

In addition to filtering then list endpoints support view modification parameters, these are distinguished by starting with an underscore character. The commonly supported modifiers are:

| Query | Meaning |
|---|---|
| ?_view=full | Return a full description of each item in the list, instead of the default minimal description. Only relevant for some endpoints. |
| ?_limit=x | Return only x items from the list, some endpoints may impose a default limit and/or a maximum to which the limit can be set. |
| ?_offset=x | Return the list of items starting with the xth item, together with _limit this enables paging through a long set of reults. |

If a limit or offset is applicable, whether explicit in the query or implicitly imposed by the API, then the metadata object will include a limit or offset field to show what limits were applied.

## Flood warnings

The Environment Agency issue warnings of floods that cover specific warning or alert areas. The floods API provides a listing of all current such warnings and is updated every 15 minutes.

A warning may be at one of four possible severity levels:

| Level | Name | Meaning |
|---|---|---|
| 1 | Severe Flood Warning | Severe Flooding, Danger to Life. |
| 2 | Flood Warning | Flooding is Expected, Immediate Action Required. |
| 3 | Flood Alert | Flooding is Possible, Be Prepared. |
| 4 | Warning no Longer in Force | The warning is no longer in force |

## Flood warnings — API

An update to the Flood Warning API took place on 30 June 2020. Although as much as possible has been done to ensure limited knock on effects to end users, please contact us via the feedback links to report any issue. The main change is in the way the @id and URI of the individual flood warning is constructed.

The list of current flood warnings:

https://environment.data.gov.uk/flood-monitoring/id/floods

Supports the following filter parameter:

| Query | Meaning |
|---|---|
| ?min-severity=x | Return only warnings which at least as severe as level x |
| ?county=x | Return only warnings applying to flood areas whose county name contains the string x. x can be a list of county names separated by "," in which case alerts which mention any of the named counties will be returned. |
| ?lat=y&long=x&dist=r | Return only warnings applying to flood areas which are within rkm of the given latitude/longitude (in WGS84 coordinates), this may be approximated by a bounding box. |

So for example, to find all warnings that are currently in effect use:

https://environment.data.gov.uk/flood-monitoring/id/floods?min-severity=3

To find all warnings that apply to areas in Somerset use:

https://environment.data.gov.uk/flood-monitoring/id/floods?county=Somerset

Each individual warning with have a URI given by the @id field in the data:

https://environment.data.gov.uk/flood-monitoring/id/floods/{id}

The {id} section of this URI is taken from the value of the floodAreaID. Therefore the current warning for a flood area (if any warning exists) will always have the same URI.

The severity level and the message field may change through the lifetime of the warning. The data for a warning will include the time at which the severity last changed. At some point after a warning is no longer in force it will disappear from the data feed and the URI for that warning will cease to resolve. If no warning is currently in place for that flood area, then attempting to resolve the URI will return a 404 status code.

For approximately 24 hours after a warning has been in place for a flood area, the severity level will be set to 4, "Warning no Longer in Force", before the warning response is removed altogether.

## Flood warnings — Returned data

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| description | Descriptive name for the flood area affected | xsd:string |  |
| eaAreaName | Name of the relevant Environment Agency Area | xsd:string |  |
| eaRegionName | No longer used | xsd:string |  |
| floodArea | URI for the flood alert or flood warning area affected |  |  |
| floodAreaID | Internal identifier for the flood alert or flood warning area affected | xsd:string |  |
| isTidal | True if the flood is tidal, false if not (fluvial or Groundwater) | xsd:boolean |  |
| message | The current situation message, also known as the real time commentary | xsd:string | optional |
| severity | The severity of the warning as a text label: 'Flood Alert', 'Flood Warning', 'Severe Flood Warning' or 'Warning no Longer in Force' | xsd:string |  |
| severityLevel | Severity level code: 1 = 'Severe Flood Warning', 2 = 'Flood Warning', 3 = 'Flood Alert', 4 = 'Warning no Longer in Force' | xsd:int |  |
| timeMessageChanged | The date and time when the message was last changed | xsd:dateTime |  |
| timeRaised | The date and time the warning was last reviewed. Usually (but not always) this leads to a change in the message or severity | xsd:dateTime |  |
| timeSeverityChanged | The date and time when the severity level was last changed | xsd:dateTime |  |

Structure of nested field floodArea:

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| county | The name of the county intersecting the flood area, as entered by the Flood Incident Management Team | xsd:string |  |
| notation | Unique identifier code for the flood area affected | xsd:string |  |
| polygon | The boundary of the area encoded as a geoJSON polygon | xsd:anyURI |  |
| riverOrSea | Name of the river or sea area linked to the flood area | xsd:string | optional |

## Flood areas

The flood areas API provide information on the geographic regions to which a given flood alert or warning may apply. These comprise Flood Alert Areas and Flood Warning Areas. A Flood Alert Area is a geographical area where it is possible for flooding to occur from rivers, sea and in some locations, groundwater. A single Flood Alert Area may cover a large portion of the floodplain, may contain multiple river catchments of similar characteristics and may contain a number of Flood Warning Areas. A Flood Warning Area is a geographical area where Environment Agency expect flooding to occur and which they provide a Flood Warning Service.

Full information on the areas is available from the Environment Agency Spatial Data Catalogue as a downloadable file and via a Web Feature Service or Web Mapping Service. For convenience we here provide the feature information for each area as a simple JSON format, including a specification of the polygon for each area (as a geoJSON feature in WGS84 coordinates). A typical application should maintain a local copy of the geographic information rather that reply on on-demand downloads of the rather large polygon files.

Each flood warning provides a link (floodArea) to the URI of the flood area to which it applies.

## Flood areas — API

To describe an individual area

https://environment.data.gov.uk/flood-monitoring/id/floodAreas/{area-code}

To list all flood areas (several thousand):

https://environment.data.gov.uk/flood-monitoring/id/floodAreas

Supports the following filter parameter:

| Query | Meaning |
|---|---|
| ?lat=y&long=x&dist=d | return those areas whose location falls within d km of the given latitude/longitude (in WGS84 coordinates), this may be approximated by a bounding box. |

The default limit on number of returned items is 500, this can be adjusted by given an explicit _limit value, there is no hard upper limit.

## Flood areas — Returned data

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| county | The name of the county intersecting the flood area, as entered by the Flood Incident Management Team |  |  |
| description | A textual description of the item | xsd:string |  |
| eaAreaName | Name of the relevant Environment Agency Area | xsd:string |  |
| eaRegionName | Name of the relevant Environment Agency region | xsd:string |  |
| floodWatchArea | The Flood Watch Area corresponding ot a warning |  | optional |
| fwdCode | Identifying code for the corresponding Target Area in Flood Warnings direct | xsd:string |  |
| label | A name for the item | xsd:string |  |
| lat | latitude of the centroid of the area, in WGS84 coordinate ref | xsd:decimal |  |
| long | longitude of the centroid of the area, in WGS84 coordinate ref | xsd:decimal |  |
| notation | A string or other literal which uniquely identifies the item. | xsd:string |  |
| polygon | The boundary of the area encoded as a geoJSON polygon | xsd:anyURI |  |
| quickDialNumber | The QuickDial number of flood line for an English language recording | xsd:string | optional |
| riverOrSea | Name of the river or sea area linked to the flood area | xsd:string | optional |

## Stations — API

The real-time data API provides information on readings of water levels and flows taken at a variety of measurement stations. A given station may provide more than one set of measurements, for example, both water level and flow rate or water level at two different spots (e.g. up-stream and down-stream of a sluice or weir). The API provides metadata on these stations and on the different measures available from each one, as well as the readings themselves.

To return the list of all measurement stations (several thousand), or some subset thereof:

https://environment.data.gov.uk/flood-monitoring/id/stations

Supports the following filter parameters:

| Query | Meaning |
|---|---|
| ?parameterName=x | Return only those stations which measure parameters with the given name x, for example Water Level or Flow. |
| ?parameter=x | Return only those stations which measure parameters with the given short form name x, for example level or flow. |
| ?qualifier=x | Return only those stations which measure parameters with qualifier x. Useful qualifiers are Stage and Downstream Stage (for stations such as weirs which measure levels at two locations), Groundwater for groundwater levels as opposed to river levels and Tidal Level for tidal levels. |
| ?label=x | Return only those stations whose label is exactly x. |
| ?town=x | Return only those stations whose town is x. Not all stations have an associated town. |
| ?catchmentName=x | Return only those stations whose catchment name is exactly x. Not all stations have an associated catchment area. |
| ?riverName=x | Return only those stations whose river name is exactly x. Not all stations have an associated river name. |
| ?stationReference=x | Return only those stations whose reference identifier is x. The station reference is an internal identifier used by the Environment Agency. |
| ?RLOIid=r | Return only the station (if there is one) whose RLOIid (River Levels on the Internet identifier) matches r. |
| ?search=x | Return only those stations whose label contains x |
| ?lat=y&long=x&dist=d | return those stations whose location falls within d km of the given latitude/longitude (in WGS84 coordinates), this may be approximated by a bounding box. |
| ?type=x | Return only those stations of the given type, where x can be one of SingleLevel, MultiTraceLevel, Coastal, Groundwater or Meteorological |
| ?status=x | Return only those stations with the given status, where x can be one of Active, Closed or Suspended |

## Stations — Examples

List all stations which measure flow rates:

https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=flow

List all stations which measure a downstream level:

https://environment.data.gov.uk/flood-monitoring/id/stations?qualifier=Downstream+Stage

List 10 stations in the Costwold catchment:

https://environment.data.gov.uk/flood-monitoring/id/stations?catchmentName=Cotswolds&_limit=10

List all stations whose name includes "River Wey":

https://environment.data.gov.uk/flood-monitoring/id/stations?search=River+Wey

List all stations whose "River name" value is "Cherwell":

https://environment.data.gov.uk/flood-monitoring/id/stations?riverName=Cherwell

## Stations — Returned data

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| RLOIid | Identifier for the station, as used by River Levels On the Internet. | xsd:string | optional |
| catchmentName | The name of the river catchment which this site is related to, if any | string | optional |
| dateOpened | The date on which the station opened | xsd:date | optional |
| datumOffset | Offset between the reference point for how the data is originally recorded and how it is normally displayed. Normally this is the difference between Ordnance datum and the stage datum | xsd:decimal | optional |
| downstageScale | Scale limits and historic range for the downstream stage water level measure |  | optional |
| label | A name for the item | string |  |
| measures | The set of measurement types available from the station | rt:Measure | multi-valued |
| notation | A string or other literal which uniquely identifies the item. | xsd:string |  |
| riverName | Name of river associated with this monitoring station (when available) | xsd:string | optional |
| stageScale | Scale limits and historic range for the main stage water level measure |  | optional |
| stationReference | Identifier for the telemetry feed used by the Environment Agency's National Flood Forecasting System | string |  |
| town | Name of the nearest town (or named place) to the station | string | optional |
| wiskiID | Identifier for the station in the WISKI hydrology dataset | xsd:string | optional |
| lat | Latitude of the station, in WGS84 coordinate ref | xsd:decimal | optional |
| long | Longitude of the station, in WGS84 coordinate ref | xsd:decimal | optional |
| easting | Easting of the station on British National Grid | xsd:integer | optional |
| northing | Northing of the station on British National Grid | xsd:integer | optional |
| status | The status of the station, one of rt:statusActive, rt:statusClosed or rt:statusSuspended | skos:Concept | optional |
| statusReason | Provides some explanation of the status or change in status of the station | xsd:string | optional |
| statusDate | The date/time of the last update to the status of this station | xsd:dateTime | optional |
| type | A list of types for the station, will be rt:Station plus one of rt:SingleLevel, rt:MultiTraceLevel, rt:Coastal, rt:Groundwater or rt:Meteorological. | owl:Class |  |

Structure of nested field measures:

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| parameter | Short, canonical, name of the quantity being measured e.g. "level", "flow" or "temperature". | string |  |
| parameterName | The name of the quantity being measured e.g. "Water Level", "Flow", "Temperature" | string |  |
| period | The period between successive readings, in seconds. | xsd:decimal |  |
| qualifier | A qualifier for the quantity being measured. Most common use is to separate level measures which occur at the top ("Stage") or bottom ("Downstream Stage") of a sluice or weir. Other relevant qualifiers are "Tidal Level" and "Groundwater". | string |  |
| unitName | A name for the units for this measurement including the datumType. Typical values are mAOD (for metres relative to the Ordnance Survey datum), mASD (for metres relative to the local stage datum), m (for metres with an unspecified datum) and m3/s (for flow rates). | xsd:string |  |

In addition to the default view, it is possible to obtain a more complete description of each station in the (filtered) list of stations by using _view=full. This will force the including of stage and downstage scale information (see next sections) when available.

## Stations — API for individual stations

Given a URI for an individual station then dereferencing it will return a full description of the station. For convenience the station description is available as a rendered HTML page as well as in JSON and RDF format. For example:

https://environment.data.gov.uk/flood-monitoring/id/stations/1491TH.html

By default, with no .html suffix you will get data in JSON format though you can also force this using:

https://environment.data.gov.uk/flood-monitoring/id/stations/1491TH.json

Or when scripting you can use content negotiation to request a response of media type application/json.

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

In additional to listing stations, which includes the information on the measures available from each station, you can list the available measures directly:

https://environment.data.gov.uk/flood-monitoring/id/measures

Supports the following filter parameters:

| Query | Meaning |
|---|---|
| ?parameterName=x | Return only measures for parameters with the given name x, for example Water Level or Flow. |
| ?parameter=x | Return only measures for parameters with the given short form name x, for example level or flow. |
| ?qualifier=x | Return only those measures with qualifier x. Useful qualifiers are Stage and Downstream Stage (for stations such as weirs which measure levels at two locations), Groundwater for groundwater levels as opposed to river levels and Tidal Level for tidal levels. |
| ?stationReference=x | Return only those measures which are available from the station with the reference identifier x. |
| ?station=x | Return only those measures which are available from the station with the URI x. |

For convenience the measures available from a station may also be listed using the URI pattern:

https://environment.data.gov.uk/flood-monitoring/id/stations/{id}/measures

The list of currently available types of measurement are:

| parameterName | parameter (short name) | Comments |
|---|---|---|
| Water Level | level | Water level, see qualifier for whether stage or downstream of the stage, see unitName for whether relative to the stage datum (mASD) or to the ordnance datum. |
| Flow | flow | Water flow rate, only available from some stations. The units of measurement vary between stations so check the unitName carefully. |
| Wind | wind | Wind direction and speed available from some stations. The qualifier will indicate whether direction (degrees) or speed (knots or m/s). |
| Temperature | temperature | Dry bulb air temperature measurement available from some stations. |

## Measures — Returned data

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| datumType | For level measurements this indicates the type of reference point the level is measured from. Can be relative to the Ordnance Survey datum (rt:AOD), to a local stage datum (rt:ASD) or rt:BDAT (below datum?). |  | optional |
| label | A name for the item | xsd:string |  |
| latestReading | links from a measure the latest available reading | rt:Reading | optional |
| notation | A string or other literal which uniquely identifies the item. | xsd:string |  |
| parameter | Short, cannonical, name of the quantity being measured e.g. "level", "flow" or "temperature". | string |  |
| parameterName | The name of the quantity being measured e.g. "Water Level", "Flow", "Temperature" | string |  |
| period | The period between successive readings, in seconds. | xsd:decimal | optional |
| qualifier | A qualilfier for the quantity being measured. Most common use is to separate level measures which occur at the top ("Stage") or bottom ("Downstream Stage") of a sluice or weir. Other relevant qualifiers are "Tidal Level" and "Groundwater". | string |  |
| station | The URI of the monitoring station supplying the measure | rdfs:Resource |  |
| stationReference | Identifier for the telemetry feed used by the Environment Agency's National Flood Forecasting System | string |  |
| unit | The units in which this parameter is measured, e.g. qudt:Meter |  | optional |
| unitName | A name for the units for this measurement including the datumType. Typical values are mAOD (for metres relative to the Ordnance Survey datum), mASD (for metres relative to the local stage datum), m (for metres with an unspecified datum) and m3/s (for flow rates). | xsd:string | optional |
| valueType | Indicates whether the measured value is an instantaneous reading or a total, mean or maximum over the period. |  | optional |

Structure of nested field latestReading:

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| date | The date at which the reading occurred | xsd:date |  |
| dateTime | The date time at which the reading occurred | xsd:dateTime |  |
| measure | The URI of the measure being recorded in this reading, this define the location (station), the parameter being measured and other qualifying information. | rt:Measure |  |
| value | The value of the reading for the associated measurement, a double not a decimal since some values are NaN. Note that in JSON output NaN is illegal for a number so in JSON any NaN readings will omit the rt:value. | xsd:double |  |

## Measures — API for individual measures

Given a URI for an individual measure then dereferencing it will return a full description of the measure. For convenience the measure description is available as a rendered HTML page as well as in JSON and RDF format. For example:

https://environment.data.gov.uk/flood-monitoring/id/measures/1491TH-level-stage-i-15_min-mASD

To get the JSON description of the individual use a .json suffix or content negotiation as usual.

The format of an individual measure description is just the same as that for the measure lists.

## Readings — API

Readings for each of the published measures are available for the recent period (up to the last four weeks). Longer historic data records may be available separately. Each reading comprises a reference to the measure being read (identified by its URI), a date time stamp for when the reading applies and a numeric value. The set of readings is updated every 15 minutes, but the individual measures may be updated less frequently than this.

To list all readings (not very useful without filtering):

https://environment.data.gov.uk/flood-monitoring/data/readings

To list all readings for a particular measure:

https://environment.data.gov.uk/flood-monitoring/id/measures/{id}/readings

To list all readings from a particular station:

https://environment.data.gov.uk/flood-monitoring/id/stations/{id}/readings

Note: The base segment for readings is data whereas for identifiable things (stations, measures, flood areas) it is id. This is deliberate and based on URI pattern advice from UK goverment, and UKGovLD working groups [1][2].

The set of readings can be filtered by time period and by type of measurement.

Filters for time period:

| Query | Meaning |
|---|---|
| ?latest | Return only the most recently available reading for each included measure. |
| ?today | Return all the readings taken today for each included measure. |
| ?date=2015-02-05 | Return all the readings taken on the specified day for each included measure. |
| ?startdate=2015-02-05&enddate=2015-02-07 | Return the readings taken on the specified range of days for each included measure, up to the specified _limit. If no _limit is given see the following size limits section. |

Filters for time period, available for readings for a particular measure or station only:

| Query | Meaning |
|---|---|
| ?since=2016-09-07T10:30:00Z | Return the readings taken since the given date time (not inclusive), up to the specified _limit. If no _limit is given see the following size limits section. Typically when tracking a particular measurement then use the dateTime of the last retrieved value as the since parameter to find any new readings. Will accept a simple date value such as 2016-09-07 which will be interpreted as 2016-09-07T:00:00:00Z. |

Filters for measurement to include:

| Query | Meaning |
|---|---|
| ?parameter=x | Return only readings for measures of parameters with the given short form name x, for example level or flow. |
| ?qualifier=x | Return only readings of measures with qualifier x. Useful qualifiers are Stage and Downstream Stage (for stations such as weirs which measure levels at two locations), Groundwater for groundwater levels as opposed to river levels and Tidal Level for tidal levels. |
| ?stationReference=x | Return only readings of measures which are available from the station with the reference identifier x. |
| ?station=x | Return only readings of measures which are available from the station with the URI x. |

Other modifiers:

| Query | Meaning |
|---|---|
| ?_view=full | Return an inline description of the measure to which the reading applies. |
| ?_sorted | Order the array of returned readings into descending order by date, this done before the limits is applied thus enabling you to fetch the most recent n readings. |

## Readings — Examples

Return the latest value for all measurements in CSV format:

https://environment.data.gov.uk/flood-monitoring/data/readings.csv?latest&_limit=6000

Return the latest readings from all groundwater measurements:

https://environment.data.gov.uk/flood-monitoring/data/readings?latest&qualifier=Groundwater

Return the latest flow readings:

https://environment.data.gov.uk/flood-monitoring/data/readings?latest&parameter=flow

Return the latest flow readings, with descriptions of the measurements:

https://environment.data.gov.uk/flood-monitoring/data/readings?latest&parameter=flow&_view=full

Return the most recent 10 readings from the upstream level measurement at King's Mill on the River Cherwell:

https://environment.data.gov.uk/flood-monitoring/id/measures/1491TH-level-stage-i-15_min-mASD/readings?_sorted&_limit=10

## Readings — Size limits

By default the readings API endpoints have a limit of 500 items, this can be modified by providing an explicit _limit value up to a hard limit of 10000 items.

This default can be modified depending on the query parameters used. The following table shows the parameters that affect the default, ordered from most important to least.

| Parameter | Default limit |
|---|---|
| measure | none |
| _sorted | 500 |
| date | none |
| today | none |
| latest | none |

This means that if a query includes the date parameter, but neither the measure parameter or the _sorted parameter then there is no default limit.

Similarly, if a query includes the _sorted parameter, but not the measure parameter then the default is 500.

## Readings — Returned data

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| date | The date at which the reading occurred | xsd:date |  |
| dateTime | The date time at which the reading occurred | xsd:dateTime |  |
| measure | The URI of the measure being recorded in this reading, this define the location (station), the parameter being measured and other qualifying information. | rt:Measure |  |
| value | The value of the reading for the associated measurement, a double not a decimal since some values are NaN. Note that in JSON output NaN is illegal for a number so in JSON any NaN readings will omit the rt:value. | xsd:double |  |

Structure of nested field measure:

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| datumType | For level measurements this indicates the type of reference point the level is measured from. Can be relative to the Ordnance Survey datum (rt:AOD), to a local stage datum (rt:ASD) or rt:BDAT (below datum?). |  | optional |
| parameter | Short, cannonical, name of the quantity being measured e.g. "level", "flow" or "temperature". | string |  |
| period | The period between successive readings, in seconds. | xsd:decimal | optional |
| qualifier | A qualilfier for the quantity being measured. Most common use is to separate level measures which occur at the top ("Stage") or bottom ("Downstream Stage") of a sluice or weir. Other relevant qualifiers are "Tidal Level" and "Groundwater". | string |  |
| station | The URI of the monitoring station supplying the measure | rdfs:Resource |  |
| stationReference | Identifier for the telemetry feed used by the Environment Agency's National Flood Forecasting System | string |  |
| unitName | A name for the units for this measurement including the datumType. Typical values are mAOD (for metres relative to the Ordnance Survey datum), mASD (for metres relative to the local stage datum), m (for metres with an unspecified datum) and m3/s (for flow rates). | xsd:string | optional |
| valueType | Indicates whether the measured value is an instantaneous reading or a total, mean or maximum over the period. |  | optional |

Structure of nested field station:

| Field | Meaning | Type | Occurs |
|---|---|---|---|
| label | A name for the item | xsd:string |  |

By default the response will not include the date (just the datetime) nor the expanded description of the measure unless an explicit _view=full request is made.

## Historic Readings

The measurement readings are archived daily as dump files in CSV format. Both the short form and the _view=full form are available.

The data is available from https://environment.data.gov.uk/flood-monitoring/archive with individual archives being at https://environment.data.gov.uk/flood-monitoring/archive/readings-{full-}{date}.csv.

## Five-day flood risk forecast

The flood risk forecast is produced by the Flood Forecasting Centre (FFC) on a daily basis. It is issued more frequently when serious flooding is forecast. It provides the indication of the potential for flooding for five days: the day on which it is issued and the subsequent four days ahead.

The forecast highlights flood risk on a county by county basis and includes a short commentary on the situation. It covers flooding from rivers, the sea, surface water and groundwater for England and Wales.

For documentation on the five-day flood forecast API, see https://api.foursources.metoffice.gov.uk/docs/flood-guidance-statement-api-public.
