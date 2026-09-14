# lugano-scout

[![CI](https://github.com/ben-lang-eng/lugano-scout/actions/workflows/ci.yml/badge.svg)](https://github.com/ben-lang-eng/lugano-scout/actions/workflows/ci.yml)

> Started from the Linux Foundation Agno lab (materials not redistributed); rebuilt from scratch using the [Agno docs](https://docs.agno.com).

An AI accommodation-search agent for family visits to Ticino, Switzerland — built with Agno AgentOS, a purpose-built MCP server over Swiss open data, and a swappable model backend: Google Gemini as baseline, [Apertus](https://www.swiss-ai.org/apertus) (the Swiss open LLM by EPFL/ETH/CSCS) as a config-only swap.

**Status:** working end-to-end with both model backends. The comparison below is from real benchmark runs; everything in this README runs from this repo.

## Why

Booking a stay near family in Ticino means juggling dates, prices in CHF, and family constraints across listing sites. This project turns that into a natural-language query against an agent — and doubles as a testbed for two portability questions:

1. **Model portability** — can the same agent run on Google Gemini and on Apertus by changing configuration only?
2. **Tool portability** — accommodation data comes from the official [Switzerland Tourism OpenData API](https://developer.myswitzerland.io/) (CC BY-SA 4.0), exposed to the agent through an MCP server written in this repo; the tool layer is swappable by design.

## Architecture

```
AgentOS dashboard (os.agno.com)
        │  HTTP
        ▼
FastAPI app (agent.py) ── Agent "Lugano Scout"
        │                    │
        │                    ├── Model via get_model() factory
        │                    │     MODEL_PROVIDER=gemini  → Gemini
        │                    │     MODEL_PROVIDER=apertus → OpenAILike
        │                    │       (PublicAI gateway, OpenAI-compatible)
        │                    │
        │                    └── MCP tools (stdio subprocess)
        ▼
mcp_server.py (fastmcp) ──► Switzerland Tourism OpenData API
   ├── search_offers(lat, lon, radius_m, query)   geo-radius search,
   │                                              thinned to 6 fields
   └── get_offer_details(offer_id)                expanded single offer
```

Design points:

- **Thin tool responses.** The raw API returns ~19 KB per page (image URLs included); the MCP server thins each offer to six fields so tool output doesn't flood the LLM context.
- **Semantic filtering is the agent's job.** The API mixes overnight-stay deals, transfers and experiences under a single classification with no structured type field — a conventional code filter is impossible, so the model classifies offers from their names and descriptions. That division of labour (tool fetches structured raw data, model does the semantic work) is the reason this is an agent and not a script.
- **Config over code.** Model provider, model IDs, API keys and the search centre all live in `.env`.

## Setup

Requires Python ≥ 3.12, [uv](https://docs.astral.sh/uv/), and Node.js is *not* needed (no npx — the MCP server is in this repo).

```bash
git clone https://github.com/ben-lang-eng/lugano-scout
cd lugano-scout
uv sync
cp .env.example .env   # then fill in keys, see below
uv run fastapi dev agent.py
```

Keys (all free tiers):

- `MYSWITZERLAND_API_KEY` — [ST Developer Portal](https://developer.myswitzerland.io/) (free, self-serve)
- `GEMINI_API_KEY` — [Google AI Studio](https://aistudio.google.com/apikey), used when `MODEL_PROVIDER=gemini`
- `APERTUS_API_KEY` — [PublicAI developer portal](https://platform.publicai.co/), used when `MODEL_PROVIDER=apertus`

Then connect the [AgentOS dashboard](https://os.agno.com) to `http://localhost:8000` ("Configure Local Agent") and ask, e.g.:

> Find me accommodation deals near Lugano within October 2026, length of stay flexible, budget up to 400 CHF per night.

## Model swap

Switching models is one line in `.env` — no code changes:

```
MODEL_PROVIDER=gemini    # or: apertus
```

`get_model()` in [agent.py](agent.py) is the single place models are constructed. The Apertus branch talks to the [Public AI Inference Utility](https://platform.publicai.co/) through agno's `OpenAILike` class (`base_url` + a mandatory `User-Agent` header).

### Comparison: same agent, same tools, same benchmark queries

Benchmark query set and full observation notes: [NOTES.md](NOTES.md). Observations from ~20 runs, September 2026:

| Dimension | Gemini 3.5 flash-lite | Apertus v1.5-8b | Apertus v1.5-8b-thinking |
|---|---|---|---|
| Tool-call format | clean | clean¹ | clean¹ |
| Multi-step tool use (search → details → rank) | yes | no — one search per run, never fetches details | no |
| Package price amortisation (total ÷ nights) | yes, with occasional slips | no (lacks the details to do it) | once, inconsistently |
| Arithmetic reliability | occasional errors (once claimed 999 > 2100) | n/a — doesn't compute | included a 312/night offer under a 300 limit |
| Run-to-run consistency | variable: same query gave an empty answer, then the best answer of the session | stable, but stably shallow | variable |
| Observed latency per run | 4–23 s | 17–204 s | 30–227 s |
| Honesty (no fabricated offers/numbers) | good | good | good |
| Free-tier rate limit vs agent loops | 5 req/min — one reasoning-heavy run can exceed it | 100 req/min | 100 req/min |

¹ After hardening the tool docstring: Apertus 8B initially stuffed dates and months into the full-text `query` parameter (`query: "October 2026"` → zero hits → "no offers published"). An explicit contract in the tool description — *never put dates, months or budgets here* — fixed it immediately. Gemini never needed the hint.

**Takeaway:** the swap itself is genuinely config-only, and Apertus's tool-calling *format* is flawless through an OpenAI-compatible gateway. The gap is agentic depth: the 8B models stop after one tool call, so any answer that requires a second hop (fetching package durations to amortise prices) doesn't happen. For this workload today, Gemini flash-lite wins on capability; Apertus wins on rate limits, cost transparency and data sovereignty — and the gap is a model-capability gap, not an integration gap.

## What I learned

- **Open data ≠ live inventory.** The OpenData API serves curated touristic offers; the live hotel inventory (with ratings and availability) behind the same MySwitzerland brand is a separate commercial booking system not exposed via the open API. The agent works honestly within that boundary and says so.
- **Tool docstrings are part of the interface — and they are prompt material.** A capable model infers parameter semantics; a small model needs the explicit negative constraint spelled out. One docstring sentence fixed a failure mode that looked like a model defect.
- **Provider-independent model wiring pays off.** Hardcoded model IDs died on me twice before this project (a retired Groq model in a previous project, `gemini-2.5-flash` retired mid-build here). A factory + `.env` makes the next retirement a config update.
- **Free-tier rate limits interact badly with agent loops.** One agent run is 6–10 API calls; Gemini's 5 requests/minute free tier can kill a run halfway. Rate limits are an agent-design constraint, not just a billing detail.
- **`print()` is forbidden in a stdio MCP server** — stdout *is* the protocol channel; tools return data, they never print.
- **Small models fail differently.** Gemini's failures are wobble (arithmetic slips, run-to-run variance); Apertus 8B's failure is shallowness (single-step tool use). Knowing *which* failure mode you have determines the mitigation.

## License

MIT — see [LICENSE](LICENSE). Data from the Switzerland Tourism OpenData API is CC BY-SA 4.0; result links point back to MySwitzerland.com as the licence requires.
