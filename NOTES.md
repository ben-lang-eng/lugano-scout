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

## V2 ideas (parked)

- Additional MCP servers (e.g. weather for the travel dates, SBB/transport).
- Agent memory / session persistence (agno supports it; not needed for demo).
- Automated comparison harness: same query set run against both models,
  results table generated instead of hand-collected.
- Streamlit or simple HTMX front end instead of the AgentOS dashboard.

## Open decisions

- Apertus serving provider + endpoint (research at Phase-3 start; field moves
  fast — PublicAI was the known option as of Sep 2026).
- Exact agno model class for OpenAI-compatible endpoints (check installed
  version's docs, don't guess).
- pytest introduction point: add tests + pytest job to CI once there is logic
  worth testing (currency normalization is the first candidate).

## Known constraints (from the lab evening, 11 Sep 2026)

- agno 3.x needs explicit `fastmcp>=4,<5`.
- First npx run of an MCP server downloads the package → pre-warm or raise
  the MCP init timeout.
- Gemini free tier: 5 requests/min/model, but one agent run with reasoning
  tools burns 6–10 calls → use flash-lite and/or trim reasoning for demos.
- Community Airbnb MCP server is a scraper; breaks when Airbnb changes.
