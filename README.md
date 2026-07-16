# Finance Dashboard

A full-stack paper trading game where players start with $10,000 in virtual cash, execute real stock trades, and compete on a live leaderboard — all powered by live market data.

> **Work in progress.** Development began in January 2026. The backend is feature-complete; the frontend has most pages built and is actively being polished.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python - Flask - SQLite |
| Frontend | JavaScript - React 19 - Vite 8 |
| Market Data | [yahooquery](https://yahooquery.dpguthrie.com/) by dpguthrie |
| News | newsapi-python |

## Features

- **Paper trading** — buy and sell real stocks with virtual cash; no real money involved
- **Live market data** — prices, financials, insider trades, stock splits, and news pulled from Yahoo Finance via [yahooquery](https://yahooquery.dpguthrie.com/)
- **Research page** — per-stock deep-dive with company profile, financial metrics, historical prices, insider activity, and recent news
- **Screeners** — market screeners showing top movers, most active, and other curated lists with live price and volume data
- **Search** — search bar with live suggestions across companies, users, and news; full search results page
- **Leaderboard** — ranked scoreboard across all players by total portfolio value
- **Portfolio tracking** — holdings, cost basis, P&L per position, transaction history, and balance snapshots over time
- **User profiles** — public profile pages
