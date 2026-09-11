# lugano-scout

> Started from the Linux Foundation Agno lab (materials not redistributed); rebuilt from scratch using the [Agno docs](https://docs.agno.com).

An AI accommodation-search agent for family visits to Ticino, Switzerland — built with Agno AgentOS, MCP tools, and a swappable model backend (Gemini as baseline, [Apertus](https://www.swiss-ai.org/apertus) as the Swiss open-model swap).

**Status: early scaffold — nothing below this line is implemented yet.** This README describes the plan; sections get filled in as the code that backs them actually runs.

## Why

Booking a stay near family in Ticino means juggling dates, prices in CHF, and family constraints across listing sites. This project turns that into a natural-language query against an agent — and doubles as a testbed for two portability questions:

1. **Model portability** — can the same agent run on Google Gemini and on Apertus, the Swiss open LLM, by changing configuration only?
2. **Tool portability** — the listing source is a community MCP server (a scraper that breaks when the site changes); the tool layer is designed to be swappable.

## Architecture

*(diagram TBD)*

```
AgentOS (FastAPI) ⇄ Agent ⇄ Model (Gemini | Apertus, via config)
                        ⇄ MCP tools (Airbnb search server via npx)
```

## Setup

*(TBD — will cover: uv venv, dependencies, `.env` from `.env.example`, running with `fastapi dev`)*

Secrets are never committed — copy `.env.example` to `.env` and fill in your keys.

## Model swap

*(TBD — `MODEL_PROVIDER` env switch, plus an honest comparison table: tool-calling reliability, latency, answer quality — Gemini vs. Apertus)*

## What I learned

*(TBD — filled in as it happens)*

## License

MIT — see [LICENSE](LICENSE).
