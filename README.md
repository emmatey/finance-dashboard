# Finance Dashboard

A full-stack paper trading competition app. Users start with $10,000 in virtual cash and compete on a live leaderboard.

## Backend (Flask / SQLite / Python)

The backend is a REST API built with Flask. Some notable implementation details:

- **Cache-aside architecture** — market data is cached in SQLite and served from the local DB, with a freshness system that fetches updates from Yahoo Finance only when data is stale
- **Decorator-based registry** — a `@register_as_research` decorator system maps database tables to their fetch, insert, and read functions, allowing a single orchestrator to coordinate multi-table updates with one API call
- **Circuit breaker** — all Yahoo Finance API calls go through an exception handler with exponential backoff, persisted to the database so state survives server restarts
- **FIFO cost basis** — portfolio P&L is calculated using first-in first-out accounting with automatic stock split adjustment
- **Data sources** — [yahooquery](https://yahooquery.dpguthrie.com/) for market data, NewsAPI integration coming soon

## Frontend (coming soon)

A React frontend is planned to consume the Flask API.
