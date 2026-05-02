# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated UK water quality compliance monitoring system. Pulls daily measurements from the [Environment Agency public API](https://environment.data.gov.uk/water-quality/), evaluates them against Water Framework Directive (WFD) thresholds, and routes AI-generated breach explanations to operations channels.

## Scope evolution

- **V1 (shipped 2nd May 2026):** n8n + Google Sheets + Telegram + Claude API +Scheduled trigger. No-code orchestration to validate the pattern with a working pipeline.
- **V2 (in development):** Python FastAPI service handles data fetching, validation, and persistence. n8n calls the Python API and retains orchestration responsibility. SQLite for local dev, Postgres in production.
- **V3 (planned):** RAG component for historical breach context using pgvector + voyage-3 embeddings.

## How to work with me

- I am a Python beginner with a biology domain background. This is a learning project — explain decisions, don't just execute them.
- For non-trivial logic, show me the code or workflow change and explain why before I accept it.
- Keep solutions simple over clever. I should be able to explain every line of code or every node in an interview.
- Push back if I ask for something that adds complexity I won't be able to maintain or defend.
- Don't introduce new dependencies, libraries, or services without asking first.
- When I'm building something manually (e.g., wiring up an n8n workflow node by node), let me do it. Offer to review afterwards rather than building it for me.
- If I make a mistake, point it out and explain why it's wrong — don't just silently fix it.

## Stack V1

- **n8n** — workflow orchestration (triggers, routing, API calls)
- **Anthropic Claude API** — generates natural-language breach explanations
- **Google Sheets** — stores thresholds, measurement history, and audit log
- **Node.js / npm** — runs n8n locally

## Architecture

The core data flow is:

1. **Ingest** — scheduled n8n workflow polls the Environment Agency API for new daily measurements
2. **Evaluate** — measurements are compared against WFD thresholds stored in Google Sheets
3. **Explain** — breaches are sent to the Claude API to produce human-readable explanations
4. **Route** — explanations are dispatched to the appropriate operations channel (Telegrame Bot)

All orchestration logic lives in n8n workflows (exported as JSON). Configuration (API keys, channel targets, thresholds) is kept in environment variables and Google Sheets, not hardcoded.

## Design decisions (v1)

- **Thresholds:** static reference data, hand-maintained in Google Sheets. No update workflow.
