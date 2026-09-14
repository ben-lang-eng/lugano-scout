# NOTES — parking lot & open decisions

Scope rule: main build is max ~3 evenings. Anything not needed for
README-backed functionality lands here instead of in the code.

## Decided (13 Sep 2026): data source = Switzerland Tourism OpenData API

Replaces the community Airbnb MCP scraper. Reasons: official & permitted
(free self-serve API key via developer.myswitzerland.io; data mostly
CC BY-SA 4.0), stable, Swiss open data pairs with the Swiss open model.
We write our OWN MCP server (`fastmcp`) exposing the API as tools —
stronger portfolio piece than consuming a scraper, and it absorbs the old
"fallback/mock MCP server" idea (no longer needed: our server is real).
Trade-off (goes in README honestly): tourism/hotel data, not
vacation-rental listings; price/availability likely more static.
Candidates evaluated and rejected: discover.swiss (partner friction),
OpenBooking (B2B only), Zürich Tourism (wrong region).

## Benchmark query set (frozen 14 Sep 2026)

Run these VERBATIM against every model backend; fill the README
comparison table from the transcripts. Baseline transcripts: Gemini
`gemini-3.5-flash-lite`, agent commit 9267796.

1. "Find me accommodation deals near Lugano for 01/10/2026 to
   08/10/2026, budget up to 300 CHF per night."
2. Same, budget up to 400 CHF per night.
3. "Find me accommodation deals near Lugano within the month of
   October 2026, length of stay flexible, budget up to 300 CHF per
   night." — then 400, then 600, then 200.

### Gemini flash-lite baseline observations

- Tool calling: reliable throughout (1-7 calls per run, correct
  search -> details chain, no malformed calls in ~10 runs).
- Arithmetic slips: one run claimed the 999 CHF package exceeded a
  2,100 CHF total budget; another showed only an over-budget package
  at a 200 CHF/night limit while omitting two packages it had itself
  amortised to ~167 and ~171 CHF/night one query earlier.
- Run-to-run variance: identical 600 CHF/night query produced a
  wrong/empty answer and, on retry, the best answer of the session
  (durations fetched, per-night amortisation, link-quality caveat).
- One hallucinated validity year (2025 instead of 2026).
- Data boundary (README material): the OpenData API exposes curated
  touristic offers only — the live hotel inventory with ratings and
  availability on swisshotels.myswitzerland.com (Switzerland Travel
  Centre booking engine) is a separate commercial system, not in the
  open API. The agent is honest within that boundary. Proper live
  inventory would need discover.swiss AccommoDataHub (partner access)
  — parked as V2.

## V2 ideas (parked)

- Additional MCP servers (e.g. weather for the travel dates, SBB/transport).
- Agent memory / session persistence (agno supports it; not needed for demo).
- Automated comparison harness: same query set run against both models,
  results table generated instead of hand-collected.
- Streamlit or simple HTMX front end instead of the AgentOS dashboard.

## Apertus serving — researched 14 Sep 2026 (Phase-3 start)

Chosen: **Public AI Inference Utility** (platform.publicai.co).
- Base URL: `https://api.publicai.co/v1` (OpenAI-compatible chat completions)
- Auth: `Authorization: Bearer <key>` PLUS a mandatory `User-Agent`
  header (anti-bot; requests without it are rejected)
- API key: free self-serve (Login -> Account -> API Keys -> Create)
- Models: `swiss-ai/apertus-v1.5-8b` (262K ctx, $0.10/$0.20 per 1M tok),
  `-8b-thinking`, `-70b` ($0.82/$2.92), `-70b-thinking`; legacy
  `apertus-8b/70b-instruct` (65K). Pick v1.5-8b first; 70b as escalation.
- Free tier: **100 requests/min** (vs Gemini free 5/min!) + starter
  credits; token usage billed against wallet, a benchmark run on 8b
  costs well under a cent.
- Rejected alternatives: Swisscom Sovereign AI Platform (business
  contract), Hugging Face router (extra indirection).

## Open decisions

- Exact agno model class for OpenAI-compatible endpoints (check installed
  version's docs, don't guess) — candidate: `agno.models.openai` OpenAI-like
  class with `base_url`; must also carry the custom User-Agent header.
- Whether the PublicAI endpoint supports OpenAI-style tool calling for
  Apertus — verify empirically with one agent run; if not, that finding
  goes in the comparison table honestly (and try the -thinking variant
  or 70b).
- pytest introduction point: add tests + pytest job to CI once there is logic
  worth testing (currency normalization is the first candidate).

## Known constraints (from the lab evening, 11 Sep 2026)

- agno 3.x needs explicit `fastmcp>=4,<5`.
- First npx run of an MCP server downloads the package → pre-warm or raise
  the MCP init timeout.
- Gemini free tier: 5 requests/min/model, but one agent run with reasoning
  tools burns 6–10 calls → use flash-lite and/or trim reasoning for demos.
- Community Airbnb MCP server is a scraper; breaks when Airbnb changes.
