# Finance Dashboard

A full-stack paper trading game where players start with $10,000 in virtual cash, execute real stock trades, and compete on a live leaderboard — all powered by live market data.

> **Work in progress.** Development began in January 2026. The backend is feature-complete; the frontend has most pages built and is actively being polished.

---

## Background

This project grew out of the CS50 *Finance* assignment — a simple Flask app for paper trading — and has since expanded into a full-stack application with a real database design, a REST API, live market data integration, and a React frontend.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · Flask · Flask-Session · SQLite |
| Frontend | React 19 · Vite 8 · React Router 7 |
| Market Data | [yahooquery](https://yahooquery.dpguthrie.com/) by dpguthrie |
| News | newsapi-python |

---

## Features

- **Paper trading** — buy and sell real stocks with virtual cash; no real money involved
- **Live market data** — prices, financials, insider trades, stock splits, and news pulled from Yahoo Finance via [yahooquery](https://yahooquery.dpguthrie.com/)
- **Research page** — per-stock deep-dive with company profile, financial metrics, historical prices, insider activity, and recent news
- **Screeners** — homepage market screeners showing top movers, most active, and other curated lists with live price and volume data
- **Search** — debounced search bar with live suggestions across companies, users, and news; full search results page
- **Leaderboard** — ranked scoreboard across all players by total portfolio value
- **Portfolio tracking** — holdings, P&L per position, transaction history, and balance snapshots over time
- **User profiles** — public profile pages at `/user/:username`

---

## Running Locally

**Prerequisites:** Python 3.x, Node.js

### Backend

```bash
cd src
pip install -r ../requirements.txt
flask run
```

The Flask server starts on `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server starts on `http://localhost:5173` and proxies all `/api` requests to the Flask backend.

---

## Notable Backend Details

The Flask backend is a REST API with a few implementation choices worth calling out:

- **Cache-aside architecture** — market data is cached in SQLite and served locally, with a freshness system that fetches updates from Yahoo Finance only when data is stale, avoiding redundant API calls
- **Decorator-based registry** — a `@register_as_research` decorator maps database tables to their fetch, insert, and read functions, so a single orchestrator can coordinate multi-table updates with one API call
- **Circuit breaker** — Yahoo Finance calls go through an exception handler with exponential backoff; state is persisted to the database so it survives server restarts
- **FIFO cost basis** — portfolio P&L is calculated using first-in first-out accounting with automatic adjustment for stock splits
- **Background daemon (`Satan.py`)** — runs on every request teardown to update prices and take balance snapshots; persistent state in SQLite survives server restarts

---

## API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Log in and set session cookie |
| POST | `/api/auth/logout` | Clear session |
| GET | `/api/auth/me` | Return current session username |

### User
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/user/summary` | Portfolio value, cash, rank snapshot |
| GET | `/api/user/portfolio` | Holdings with P&L per position |
| GET | `/api/user/transactions` | Full transaction history |
| GET | `/api/user/balance_snapshots` | Historical balance snapshots |

### Trading
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/trade?ticker=<ticker>` | Preview order (price, holdings, metrics) |
| POST | `/api/trade` | Execute buy or sell |

### Research
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/research/local?ticker=` | Cached data only; fast initial load |
| GET | `/api/research/online?ticker=` | Full data; refreshes stale tables |
| GET | `/api/research/summary?ticker=` | Basic company info and last price |
| GET | `/api/research/company_profile?ticker=` | Description, industry, employee count |
| GET | `/api/research/financial_metrics?ticker=` | P/E, market cap, 52-week range, etc. |
| GET | `/api/research/insider_trades?ticker=` | Recent insider transactions |
| GET | `/api/research/historical_prices?ticker=` | OHLCV price history |
| GET | `/api/research/stock_splits?ticker=` | Split history |
| GET | `/api/research/news?ticker=&qty=` | News stories (ticker optional) |

### Search
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/search?q=` | Combined results: companies, users, news |
| GET | `/api/search/companies?q=&local=` | Company search; `local=true` for DB-only |
| GET | `/api/search/users?q=` | User search by username |
| GET | `/api/search/news?q=&local=` | News search by headline or ticker |

### Market
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/screeners` | Screener lists (top movers, most active, etc.) |
| GET | `/api/market_overview` | Regional ETF summary for homepage |
| GET | `/api/scoreboard` | Full player rankings |

---

## Project Structure

```
finance-dashboard/
├── src/                          # Flask backend
│   ├── app.py                    # Routes and server entry point
│   ├── AccountManager.py         # Auth (register, login, sessions)
│   ├── TransactionManager.py     # Buy/sell, FIFO cost basis, snapshots
│   ├── ReportManager.py          # Portfolio, P&L, transaction history
│   ├── ResearchDataCoordinator.py # Research data orchestration + freshness
│   ├── MarketOverviewCoordinator.py # Screeners and regional ETFs
│   ├── SearchManager.py          # Cross-entity search
│   ├── YahooQueryService.py      # yahooquery API client
│   ├── APIDataIO.py              # DB read/write for all market data
│   ├── CommonQueries.py          # Shared DB queries
│   ├── Satan.py                  # Background daemon (price updates)
│   ├── DbManager.py              # DB connection management
│   ├── helpers.py                # Shared utilities, decorators, error types
│   └── schema.sql                # Database schema
├── frontend/                     # React + Vite frontend
│   └── src/
│       ├── pages/                # Route-level components
│       │   ├── Home.jsx          # Landing / screener view
│       │   ├── Auth.jsx          # Login, register, change password
│       │   ├── Search.jsx        # Full search results
│       │   ├── Research.jsx      # Per-stock deep-dive
│       │   └── User.jsx          # Player profile page
│       ├── components/
│       │   ├── nav/              # Header search bar + suggestions
│       │   ├── home/             # Landing and HomeBody
│       │   ├── screener/         # ScreenerFrame and ScreenerCard
│       │   └── auth/             # Login, Register, Change forms
│       ├── context/
│       │   └── AuthContext.jsx   # Session state provider
│       └── scripts/utils.js      # Shared frontend utilities
├── tests/                        # Backend test suite
├── legacy_code/                  # Original CS50 Flask+Jinja templates
└── requirements.txt
```
