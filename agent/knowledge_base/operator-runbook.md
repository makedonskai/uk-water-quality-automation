Source: internal operator runbook, uk-water-quality-automation project
Written: 2026-11-24
Status: draft for review

# Duty operator runbook: river level statuses

## What this system monitors

This system monitors river water levels at five Environment Agency stations: Reading, Kingston and Sunbury Lock on the River Thames, Merton on the River Wandle, and Walthamstow Low Hall on the River Lee. It only measures water level in metres. It does not measure water quality, rainfall or flow. It does not forecast whether levels will rise or fall. Each reading is compared with two thresholds for that station: a warning threshold and a critical threshold.

## Where the thresholds come from

The warning and critical thresholds for each station are stored in data/reference/thresholds.csv. They were taken from the Environment Agency station scale data and from the flood warning service, not invented by this system. Thresholds are different for every station, because each station measures from its own reference point. Operators must not change thresholds during a shift. If a threshold looks wrong, report it to the project owner.

## Our statuses are not official flood warnings

The statuses normal, warning and critical are internal statuses of this monitoring system. They are not the same as the Environment Agency Flood Alert, Flood Warning or Severe Flood Warning. A station can be critical in our system while no official warning is in force, and the other way round. Never tell the public that an official flood warning has been issued because of our status. For official warnings, always refer to the Environment Agency and GOV.UK.

## Status normal

Normal means the latest reading is fresh and below the warning threshold. No action is needed. Keep monitoring as usual. Do not send an alert for a normal reading.

## Status warning

Warning means the latest reading is fresh and at or above the warning threshold, but below the critical threshold. The boundary counts: a level exactly equal to the warning threshold is a warning. Check the reading time and the level. Send an operations alert if one has not already been sent for this reading. Watch the station more often until it returns to normal.

## Status critical

Critical means the latest reading is fresh and at or above the critical threshold. A level exactly equal to the critical threshold is critical. Send an operations alert if one has not already been sent for this reading. Inform the team lead. Check whether the Environment Agency has issued an official warning for the area. If anyone is in immediate danger, they must call 999.

## Status stale: the reading is too old

Stale means the latest reading is older than 60 minutes. Levels are usually measured every 15 minutes, so stale means about four readings are missing. A stale reading must not be treated as the current situation, even if the old level was above a threshold. Do not send an alert based on stale data. Check whether the station or its data feed is working, and report the station as not reporting. A stale status is about the age of the data, not about the water level.

## Status unknown: the value is missing

Unknown means the latest reading has no value, even if the reading time is recent. This usually points to a sensor or data problem, not to a change in the river. Do not guess the level and do not send an alert. Report the station as returning empty values. Unknown is different from stale: stale means the reading is old, unknown means there is no number at all.

## How operations alerts work

An alert can only be sent for a fresh warning or critical reading. The system recalculates the status before sending, so it will refuse an alert for normal, stale or unknown readings. Only one alert is sent per reading; asking again returns already sent. A human operator must confirm every alert by answering yes. Pressing Enter without an answer means no. At this stage alerts are written to a log file; a Telegram channel is planned.

## When to escalate

Escalate to the team lead when a station is critical, when the same station stays in warning for several readings in a row, or when two or more stations are stale or unknown at the same time. Escalate also if a threshold looks wrong. In any situation where people may be in danger, the correct response is 999 and the official Environment Agency guidance, not this system.
