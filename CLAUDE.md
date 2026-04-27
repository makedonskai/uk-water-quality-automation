# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated UK water quality compliance monitoring system. Pulls daily measurements from the [Environment Agency public API](https://environment.data.gov.uk/water-quality/), evaluates them against Water Framework Directive (WFD) thresholds, and routes AI-generated breach explanations to operations channels.

**Status:** In development — target ship date May–June 2026.

## How to work with me

- I am a Python beginner with a biology domain background. This is a learning project — explain decisions, don't just execute them.
- For non-trivial logic, show me the code or workflow change and explain why before I accept it.
- Keep solutions simple over clever. I should be able to explain every line of code or every node in an interview.
- Push back if I ask for something that adds complexity I won't be able to maintain or defend.
- Don't introduce new dependencies, libraries, or services without asking first.
- When I'm building something manually (e.g., wiring up an n8n workflow node by node), let me do it. Offer to review afterwards rather than building it for me.
- If I make a mistake, point it out and explain why it's wrong — don't just silently fix it.

## Stack

- **n8n** — workflow orchestration (triggers, routing, API calls)
- **Anthropic Claude API** — generates natural-language breach explanations
- **Google Sheets** — stores thresholds, measurement history, and audit log
- **Node.js / npm** — runs n8n locally

## Architecture

The core data flow is:

1. **Ingest** — scheduled n8n workflow polls the Environment Agency API for new daily measurements
2. **Evaluate** — measurements are compared against WFD thresholds stored in Google Sheets
3. **Explain** — breaches are sent to the Claude API to produce human-readable explanations
4. **Route** — explanations are dispatched to the appropriate operations channel (Slack, email, etc.)

All orchestration logic lives in n8n workflows (exported as JSON). Configuration (API keys, channel targets, thresholds) is kept in environment variables and Google Sheets, not hardcoded.

## Design decisions (v1)

- **Thresholds:** static reference data, hand-maintained in Google Sheets. No update workflow.
- **Audit log:** breaches and borderlines only, with full context. Non-breaches not logged.
- **Severity routing:** value > 2x threshold = Critical (Slack + email); 1x–2x = Standard (Slack only); borderline = Sheet only.
- **Failure handling:** errors trigger an n8n error workflow that posts to Slack. Workflow exits gracefully on partial failure.

## Decisions and Scope

- **Notification channel:** Email and Slack, routed by severity (see Design decisions above).
- **Python / RAG:** No Python in the current scope. A RAG-based component (e.g., for retrieving historical breach context) is planned as a future addition once the core pipeline is stable. Python will be introduced at that point.
