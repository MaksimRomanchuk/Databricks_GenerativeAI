# AI Bike Coach

An agentic cycling coach: reads your Strava activities, writes ride summaries and
advice, and builds a weekly training plan from your goals. Built as a hands-on
project to practice agentic-AI patterns — **tool use**, **multi-agent systems**,
and **evals & error analysis**.

## Architecture (planned)

| Component | Pattern | Role |
|---|---|---|
| Strava tool layer | Tool use | Read activities, activity detail, athlete stats |
| `AnalysisAgent` | Multi-agent | Ride summary + coaching advice |
| `PlannerAgent` | Multi-agent / planning | Weekly training plan from goals |
| Orchestrator | Multi-agent | Routes requests to the right agent |
| Eval harness | Evals & error analysis | Labeled cases + LLM-judge to measure quality |

Routes generation is a stretch goal (needs an external routing engine).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then paste your Strava Client Secret into .env
python scripts/get_token.py   # one-time OAuth; saves .strava_tokens.json
```

## Layout

```
scripts/get_token.py   One-time Strava OAuth: code -> access/refresh tokens
src/strava/auth.py     get_access_token(): auto-refreshes expired tokens
src/strava/            (Phase 1) Strava data tools
```

## Security

`.env` and `.strava_tokens.json` hold secrets and are gitignored — never commit them.
