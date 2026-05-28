# Architecture

## Components

The system is composed of three layers, each with a single responsibility.

### 1. Orchestration — n8n

n8n owns scheduling, conditional routing, and external service integrations
(Telegram, Google Sheets). It is the visual control plane.

A scheduled trigger fires every 15 minutes. n8n calls the Python service
at `POST /check` and routes the response to the appropriate output channels
based on the `status` field of each result.

### 2. Logic & persistence — Python (FastAPI)

The Python service owns:

- Fetching readings from the EA Flood Monitoring API
- Validating responses with Pydantic
- Evaluating readings against per-station thresholds
- Persisting all readings to the database (full audit trail)
- Generating breach explanation messages via the Anthropic Claude API

The service exposes a thin HTTP API. n8n is the only client.

### 3. Storage — SQLite (dev) / Postgres (prod)

A single `readings` table persists every reading evaluated by the system,
regardless of whether it triggered an alert. This supports historical analysis
and audit requirements.

## Data flow

\`\`\`
[n8n schedule trigger]
|
v
[POST http://service:8000/check]
|
v
[Python: fetch all 5 stations from EA API in parallel]
|
v
[Python: validate each response with Pydantic]
|
v
[Python: evaluate against thresholds]
|
v
[Python: persist to database]
|
v
[Python: return list[EvaluationResult] to n8n]
|
v
[n8n Switch node: route by status]
|
+--- status="critical" ---> [Telegram critical alert]
+--- status="warning" ---> [Telegram warning alert]
+--- (any status) ---> [Google Sheets append row]

## Why this split?

- **n8n** is excellent at orchestration and visual debugging of message flows.
  Replacing it with code would mean reimplementing scheduling, retry, and
  error-routing UI for no engineering benefit.
- **Python** is necessary for testable logic, type-safe data validation, and
  efficient persistence. Implementing this in n8n would require a Code node
  with no version control, no tests, and no IDE support.
- This split lets each tool do what it is good at and avoids forcing one to
  do the other's job.
  \`\`\`
