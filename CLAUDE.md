# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated UK water quality compliance monitoring system. Pulls daily measurements from the [Environment Agency public API](https://environment.data.gov.uk/water-quality/), evaluates them against Water Framework Directive (WFD) thresholds, and routes AI-generated breach explanations to operations channels.

**Status:** In development — target ship date May–June 2026.

## Stack

- **n8n** — workflow orchestration (triggers, routing, API calls)
- **Anthropic Claude API** — generates natural-language breach explanations
- **Google Sheets** — stores thresholds, measurement history, and audit log
- **Docker** — runs n8n and any supporting services

## Architecture

The core data flow is:

1. **Ingest** — scheduled n8n workflow polls the Environment Agency API for new daily measurements
2. **Evaluate** — measurements are compared against WFD thresholds stored in Google Sheets
3. **Explain** — breaches are sent to the Claude API to produce human-readable explanations
4. **Route** — explanations are dispatched to the appropriate operations channel (Slack, email, etc.)

All orchestration logic lives in n8n workflows (exported as JSON). Configuration (API keys, channel targets, thresholds) is kept in environment variables and Google Sheets, not hardcoded.
