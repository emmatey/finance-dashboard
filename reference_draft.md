# Paper Trading Platform — Frontend API Reference

> **Base URL:** `http://localhost:5000`
>
> **Last Updated:** April 2026
>
> **Status:** ~80% of routes implemented, not yet integration-tested.

---

## Overview

This is a paper trading platform where users compete against each other using virtual money ($10,000 starting balance). Users can buy and sell real stocks at real-time prices, research companies with financial data, and climb a leaderboard. Think of it as a fantasy stock market league.

The backend is a Flask + SQLite application powered by Yahoo Finance data (via `yahooquery`). It handles authentication via server-side sessions (cookie-based), automatic price updates through a background daemon, and a smart caching layer that only fetches fresh data from Yahoo when existing data goes stale.

---

## Conventions

### Authentication

Session-based authentication via cookies. After a successful `POST /auth/login`, the server sets a session cookie. Include this cookie on subsequent requests. Some routes require login (marked with 🔒), others accept an optional `?username=` query parameter to look up other users' public data.

### User Resolution

Many `/user/*` endpoints follow a consistent pattern for identifying which user to query:

1. If `?username=<username>` query param is present → resolve that user
2. Otherwise → fall back to the logged-in user's session
3. If neither is available → return an error

This means a logged-in user can view their own data without any query param, or look up another player by name.

### Error Responses

All errors follow a consistent shape:

```json
{
  "success": false,
  "message": "Human-readable error description"
}
```

### Success Responses

Simple confirmations:

```json
{
  "success": true,
  "message": "Optional description"
}
```

Endpoints that return data generally return the data directly (a list or object), without wrapping it in a `success` envelope. The exception is `/user/summary`, which includes `"success": true` alongside its data fields.

### Numeric Fields

All monetary values and quantities are floats. Quantities can be fractional (partial shares are supported). Any numeric field may be `null` if the upstream data source didn't provide it.

### Timestamps

The API uses two timestamp formats depending on the source:

- **Unix timestamps** (integers): Used for `providerPublishTime` in news, `snap_datetime` and transaction dates
- **ISO datetime strings**: Used for `last_updated` fields, `split_date`, `transaction_date`

The frontend should be prepared to handle both.

---

## Auth

These three endpoints manage the user lifecycle. No session cookie is required to call register or login.

### `POST /auth/register`

Create a new account. On success the user is **not** automatically logged in — a separate login call is needed.

**Request Body:**

```json
{
  "username": "string — alphanumeric, no spaces, min 1 character",
  "password": "string — ASCII only, min 5 chars, requires: 1 uppercase, 1 lowercase, 1 non-letter"
}
```

**Responses:**

| Status | Meaning |
|--------|---------|
| 201 | Account created |
| 400 | Validation failure (body will say which rule was violated) |
| 409 | Username already taken |

**Frontend Notes:** The password rules are strict enough that you'll want inline validation. The backend checks (in order): length ≥ 5, ASCII-only, has uppercase, has lowercase, has a non-letter character (number or symbol). Showing these as a checklist during registration would be a good UX pattern.

---

### `POST /auth/login`

Authenticate and start a session. Also triggers a balance snapshot for the user (their portfolio value gets recalculated and recorded).

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Responses:**

| Status | Meaning |
|--------|---------|
| 200 | Logged in, session cookie set |
| 400 | Missing JSON body |
| 401 | Bad username or password |

**Frontend Notes:** After login, the session cookie is set automatically. Store the username client-side for display purposes — the session itself is server-managed. The balance snapshot on login means the scoreboard will reflect the user's current standing even if the background daemon hasn't run recently.

---

### `POST /auth/logout`

Clear the session. No request body needed.

**Responses:**

| Status | Meaning |
|--------|---------|
| 200 | Logged out |
| 500 | Session clear failed (rare) |

---

## User

These endpoints power the profile page, portfolio view, transaction history, and the account value chart. All support the `?username=` query param pattern for viewing other users' data.

### `GET /user/summary`

The "user card" — a compact summary suitable for a dashboard widget or profile header.

**Query Params:** `?username=string` (optional, falls back to logged-in user)

**200 Response:**

```json
{
  "success": true,
  "username": "emma",
  "user_id": 1,
  "snap_datetime": "2026-04-12 00:00:00",
  "portfolio_value": 4523.50,
  "cash_balance": 5476.50,
  "grand_total": 10000.00,
  "rank": 3
}
```

**Error Responses:**

| Status | Meaning |
|--------|---------|
| 400 | No username in param or session |
| 404 | Username not found in database |
| 500 | Data partially missing for user |

**Frontend Notes:** `snap_datetime` tells you when the portfolio value and cash balance figures were last calculated. You could display this as "Last updated: 3 hours ago" to set expectations about data freshness. The `rank` is computed against all users' most recent balance snapshots.

**Related Endpoints:** Pair with `/user/portfolio` for a full profile page, or `/user/balance_snapshots` for a value-over-time chart.

---

### `GET /user/portfolio`

The detailed holdings breakdown — one entry per stock the user currently owns. This is the data behind a portfolio table with gain/loss columns.

**Query Params:** `?username=string` (optional)

**200 Response:**

```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "shares": 10.0,
    "unit_price": 192.53,
    "cost_basis": 178.20,
    "current_value": 1925.30,
    "total_cost": 1782.00,
    "gain_loss": 143.30,
    "gain_loss_pct": 8.04
  }
]
```

Sorted by `current_value` descending (biggest positions first). Returns an empty success message if the user has no holdings.

**Field Definitions:**

- `shares` — Split-adjusted quantity currently owned
- `unit_price` — Latest market price per share (updated by background daemon)
- `cost_basis` — Average price paid per share using FIFO accounting
- `current_value` — `shares × unit_price`
- `total_cost` — Total amount originally paid for remaining shares (FIFO)
- `gain_loss` — `current_value - total_cost` (dollar P&L)
- `gain_loss_pct` — Percentage return on the position

**Frontend Notes:** This is great data for both a table view and a pie chart (use `current_value` for slice sizes). Color-code `gain_loss` and `gain_loss_pct` green/red. The cost basis uses FIFO — if users ask "why does my cost basis look weird after partial sells?" that's why.

---

### `GET /user/transactions` 🔒

Full transaction history for the user, newest first.

**Query Params:** `?username=string` (optional)

**200 Response:**

```json
[
  {
    "transaction_id": 42,
    "username": "emma",
    "ticker": "AAPL",
    "transaction_type": "buy",
    "qty": 10.0,
    "unit_price": 178.20,
    "datetime": "2026-04-10 14:30:00",
    "cash_after": 8218.00
  }
]
```

**Transaction Types:**

| Type | `qty` sign | `ticker` value | Notes |
|------|-----------|----------------|-------|
| `buy` | positive | stock ticker | Purchase |
| `sell` | negative | stock ticker | Sale |
| `deposit` | positive | `"CASH"` | Cash added |
| `withdraw` | negative | `"CASH"` | Cash removed |

**Frontend Notes:** For deposit/withdraw transactions, the `ticker` field will be `"CASH"` — handle this in your display logic. The `cash_after` field shows the user's cash balance immediately after each transaction, which is useful for showing a running balance column. Consider adding pagination client-side since this list will grow over time (the backend currently returns all records).

---

### `GET /user/balance_snapshots` 🔒

Historical value data for charting the user's account value over time. Snapshots are created on login, after every trade, and once daily by the background daemon.

**Query Params:** `?username=string` (optional)

**200 Response:**

```json
[
  {
    "username": "emma",
    "snap_datetime": "2026-04-12 00:00:00",
    "cash_balance": 5476.50,
    "portfolio_value": 4523.50,
    "grand_total": 10000.00
  }
]
```

**Frontend Notes:** This is your line chart data. The `grand_total` is a computed column (`cash_balance + portfolio_value`), so you get three potential chart "modes" from one dataset — total value, portfolio value only, or cash only. The data arrives ordered chronologically.

**Related Endpoints:** Use alongside `/user/summary` for the profile page — summary gives the current snapshot, this gives the history.

---

## Trade

The core trading flow. This is a dual-purpose endpoint handling both the order preview screen (GET) and order execution (POST).

### `GET /trade?ticker=<TICKER>` 🔒

Populates the order form with current price data, user's position, and key financial metrics. Also triggers a freshness check to ensure financial metrics are up to date.

**Query Params:** `?ticker=string` (required)

**200 Response:**

```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "current_price": 192.53,
  "prev_close": 190.80,
  "pct_change_since_close": 0.91,
  "fifty_two_week_high": 220.00,
  "fifty_two_week_low": 155.00,
  "market_cap": 2950000000000,
  "three_month_avg_volume": 58000000,
  "analyst_count": 40,
  "rating": "buy",
  "target_price": 210.00,
  "cash_balance": 5476.50,
  "qty_owned": 10.0,
  "holding_value": 1925.30
}
```

**Error Responses:**

| Status | Meaning |
|--------|---------|
| 400 | No ticker provided |
| 404 | Ticker not found (even after checking Yahoo) |
| 500 | Data missing or corrupt, or no session user_id |

**Frontend Notes:** This response has everything you need for a trade form: the user's available cash, how many shares they already own, the current price for calculating order totals, and enough financial context (52-week range, analyst rating, etc.) to help the user make a decision. `pct_change_since_close` is pre-calculated for you — show it next to the price with the appropriate color.

---

### `POST /trade` 🔒

Execute a buy or sell order. The server re-fetches the latest price from Yahoo immediately before executing to minimize stale-price risk. A balance snapshot is automatically recorded after every successful trade.

**Request Body:**

```json
{
  "ticker": "AAPL",
  "qty": 5,
  "transaction_type": "buy"
}
```

`transaction_type` must be `"buy"` or `"sell"`.

**200 Response (buy):**

```json
{
  "success": true,
  "ticker": "AAPL",
  "qty": 5,
  "unit_price": 192.53,
  "tx_value": 962.65,
  "new_balance": 4513.85
}
```

**200 Response (sell):**

```json
{
  "ticker": "AAPL",
  "qty": 5,
  "unit_price": 192.53,
  "tx_value": 962.65,
  "new_balance": 6439.15
}
```

**Error Responses:**

| Status | Meaning |
|--------|---------|
| 400 | Missing ticker, qty, or invalid transaction_type |
| 400 | Insufficient funds (buy) or insufficient shares (sell) |
| 404 | Ticker not found |
| 500 | Transaction failed to record |

**Frontend Notes:** The "insufficient funds" error response includes the user's current balance and the required amount in the message string, which you could parse for a nicer UI, but the message is human-readable as-is. After a successful trade, you'll want to refresh the portfolio view and summary since the balance has changed. Note that the sell response doesn't include `"success": true` — a minor inconsistency to be aware of.

---

## Research

A rich set of endpoints for company deep-dives. Each endpoint checks data freshness against configurable thresholds and auto-refreshes from Yahoo Finance if stale.

**Freshness Thresholds:**

| Data | Refresh After |
|------|--------------|
| Financial metrics | 12 hours |
| Historical prices | 24 hours |
| News | 1 hour |
| Insider trades | 24 hours |
| Company profile | 1 week |
| Stock splits | 1 week |

### `GET /research?ticker=<TICKER>`

The "everything" endpoint — returns all research data for a company in a single call. Checks freshness for all tables and updates any that are stale. This is what you'd call when a user navigates to a full company research page.

**Query Params:** `?ticker=string` (required)

**200 Response:**

```json
{
  "stock_splits": [
    {
      "ticker": "AAPL",
      "split_date": "2020-08-31",
      "split_ratio": 4.0,
      "last_updated": "2026-04-10 12:00:00"
    }
  ],
  "historical_prices": [
    {
      "ticker": "AAPL",
      "price": 192.53,
      "timestamp": 1712880000,
      "volume": 58000000
    }
  ],
  "financial_metrics": [
    {
      "ticker": "AAPL",
      "last_updated": "2026-04-12 08:00:00",
      "market_open": 191.00,
      "prev_close": 190.80,
      "market_cap": 2950000000000,
      "eps": 6.42,
      "beta": 1.24,
      "trailing_pe": 29.99,
      "forward_pe": 27.50,
      "profit_margin": 0.265,
      "shares_outstanding": 15300000000,
      "book_value": 4.25,
      "price_to_book": 45.30,
      "dividend_yield": 0.0052,
      "fifty_two_week_high": 220.00,
      "fifty_two_week_low": 155.00,
      "fifty_day_average": 188.40,
      "two_hundred_day_average": 182.10,
      "rating": "buy",
      "analyst_count": 40,
      "target_price": 210.00,
      "current_ratio": 0.99,
      "debt_to_equity": 176.30,
      "todays_volume": 62000000,
      "ten_day_avg_volume": 57000000,
      "three_month_avg_volume": 58000000
    }
  ],
  "news": [
    {
      "uuid": "abc-123-def",
      "title": "Apple Reports Record Quarter",
      "publisher": "Reuters",
      "link": "https://...",
      "providerPublishTime": 1712880000,
      "thumbnail": "https://..."
    }
  ],
  "company_profile": [
    {
      "ticker": "AAPL",
      "company_desc": "Apple Inc. designs, manufactures...",
      "employee_count": 164000,
      "industry": "Consumer Electronics",
      "website": "https://apple.com",
      "last_updated": "2026-04-05 00:00:00"
    }
  ],
  "insider_trades": [
    {
      "ticker": "AAPL",
      "transaction_date": "2026-03-15",
      "shares": -50000.0,
      "transaction_value": 9626500.0,
      "filer_name": "Tim Cook",
      "filer_relation": "Chief Executive Officer",
      "transaction_text": "Sale",
      "last_updated": "2026-04-11 00:00:00"
    }
  ]
}
```

**Frontend Notes:** This is a big payload. Consider whether you need everything at once or if lazy-loading individual sections would feel better. Each section is keyed by table name, and each value is an array (even for single-record tables like `financial_metrics` and `company_profile`). The initial load might be slow if multiple data sources are stale and need refreshing.

---

### Individual Research Endpoints

These are the same data as `/research` but broken out individually. Each checks and refreshes only its own table. Use these for targeted views or when you want to lazy-load sections.

#### `GET /research/summary?ticker=<TICKER>`

Minimal company info. Useful for search result cards or compact displays.

```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "price": 192.53
}
```

#### `GET /research/company_profile?ticker=<TICKER>`

```json
{
  "ticker": "AAPL",
  "company_desc": "Apple Inc. designs, manufactures...",
  "industry": "Consumer Electronics",
  "website": "https://apple.com",
  "employee_count": 164000,
  "last_updated": "2026-04-05 00:00:00"
}
```

Note: This returns a single object, not an array.

#### `GET /research/financial_metrics?ticker=<TICKER>`

Returns a single object with all financial metrics (see the full shape in the `/research` response above). This is the same data, just unwrapped from the array.

#### `GET /research/insider_trades?ticker=<TICKER>`

**Query Params:** `?ticker=string` (required), `?qty=int` (optional, limits results)

Returns an array of insider trade records.

#### `GET /research/historical_prices?ticker=<TICKER>`

Returns an array of price/volume/timestamp records. Use for price charts.

```json
[
  {
    "ticker": "AAPL",
    "price": 192.53,
    "timestamp": 1712880000,
    "volume": 58000000
  }
]
```

#### `GET /research/stock_splits?ticker=<TICKER>`

```json
[
  {
    "ticker": "AAPL",
    "split_date": "2020-08-31",
    "split_ratio": 4.0,
    "last_updated": "2026-04-10 12:00:00"
  }
]
```

#### `GET /research/news?ticker=<TICKER>`

**Query Params:** `?ticker=string` (optional), `?qty=int` (optional, default 10)

If no ticker is provided, returns global news (all companies). With a ticker, returns news for that company and triggers a freshness check.

```json
[
  {
    "uuid": "abc-123-def",
    "title": "Apple Reports Record Quarter",
    "thumbnail": "https://...",
    "link": "https://...",
    "publisher": "Reuters",
    "providerPublishTime": 1712880000
  }
]
```

**Frontend Notes:** `providerPublishTime` is a Unix timestamp. `thumbnail` may be `null`. The `uuid` is unique per story and can be used as a React key. When called without a ticker, global news updates are not yet implemented (the `NewsAPIManager` is a stub) — the endpoint will return whatever is already cached in the database.

---

## Screeners

### `GET /screeners`

Market screener data — day gainers, losers, most active stocks, etc. The backend auto-refreshes this data hourly. Returns results grouped by screener name.

**Query Params:** None

**200 Response:**

```json
{
  "day_gainers": [
    {
      "screener_name": "day_gainers",
      "rank": 1,
      "ticker": "XYZ",
      "company_name": "XYZ Corp",
      "current_price": 45.20,
      "prev_close": 38.10,
      "price_change_pct": 18.64,
      "market_cap": 5200000000,
      "todays_volume": 12000000,
      "three_month_avg_volume": 3000000,
      "volume_change_pct": 300.0
    }
  ],
  "day_losers": [ ... ],
  "most_actives": [ ... ],
  "most_watched_tickers": [ ... ],
  "fifty_two_wk_gainers": [ ... ],
  "fifty_two_wk_losers": [ ... ],
  "volume_spike_bullish": [ ... ],
  "volume_spike_bearish": [ ... ]
}
```

**Available Screener Names:**

| Screener | Description |
|----------|-------------|
| `day_gainers` | Biggest price increases today |
| `day_losers` | Biggest price decreases today |
| `most_actives` | Highest volume today |
| `most_watched_tickers` | Most watched on Yahoo Finance |
| `fifty_two_wk_gainers` | Biggest 52-week price gains |
| `fifty_two_wk_losers` | Biggest 52-week price drops |
| `volume_spike_bullish` | Custom: unusual volume + price up |
| `volume_spike_bearish` | Custom: unusual volume + price down |

**Frontend Notes:** The last two screeners (`volume_spike_bullish/bearish`) are custom-derived from the Yahoo data — they identify stocks with abnormal volume relative to their 3-month average. Each screener's array is ordered by `rank`. This is a good candidate for a tabbed interface on the homepage. Note: the response might include a `"broken"` key if any screener records are malformed — you can ignore or log that.

---

## Scoreboard

> **Status: NOT YET IMPLEMENTED as a route**

Based on `api.md`, this endpoint is planned:

### `GET /scoreboard` (planned)

**Expected Response:**

```json
[
  {
    "username": "emma",
    "portfolio_value": 4523.50,
    "cash_balance": 5476.50,
    "grand_total": 10000.00,
    "rank": 1
  }
]
```

**Frontend Notes:** The backend already has the `get_all_users_ranks()` method in `ReportManager` — it just needs to be wired to a route. This data comes from the most recent balance snapshots, updated daily by the daemon and on each user login. Portfolios are fully visible (not obfuscated) since this is a competition, not a real brokerage. You can use `/user/portfolio?username=<name>` and `/user/balance_snapshots?username=<name>` to drill into any user's detailed holdings.

---

## Market Overview

> **Status: NOT YET IMPLEMENTED as a route**

### `GET /market_overview` (planned)

Regional ETF performance data for a global markets "at a glance" widget.

**Expected Response:**

```json
[
  {
    "region": "USA",
    "ticker": "VOO",
    "current_price": 480.00,
    "prev_close": 478.50,
    "pct_change": 0.31
  },
  {
    "region": "EU",
    "ticker": "IEUR",
    "current_price": 55.20,
    "prev_close": 54.90,
    "pct_change": 0.55
  }
]
```

**Tracked Regions:** USA (VOO), EU (IEUR), LATAM (ILF), Africa (AFK), Australia (EWA), India (INDA), Japan (EWJ), China (MCHI), Gold (GLD), Copper (CPER), Oil (USO)

**Frontend Notes:** The backend (`MarketOverviewCoordinator`) already fetches and caches this data with a 1-hour refresh cycle. It just needs a route. This is homepage material — a row of cards or a small world map with color-coded performance indicators.

---

## Search

> **Status: NOT YET IMPLEMENTED as a route**

### `GET /search?q=<query>` (planned)

**Expected Response:**

```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "quote_type": "EQUITY",
    "type": "company"
  },
  {
    "username": "emma",
    "grand_total": 10000.00,
    "rank": 1,
    "type": "user"
  },
  {
    "title": "Apple Reports Record Quarter",
    "desc": "...",
    "related_to": ["AAPL"],
    "link": "https://...",
    "type": "news"
  }
]
```

**Frontend Notes:** The backend has `SearchManager` which already implements local DB search and Yahoo Finance online search with deduplication. The search returns a mixed-type result set — use the `type` field to render different card layouts for companies, users, and news. The design calls for section headers ("Companies", "Users", "News") within the results.

---

## Suggested Page Architecture

Based on the available (and planned) endpoints, here's a natural mapping of pages to API calls:

### Homepage

| Section | Endpoint(s) |
|---------|-------------|
| User summary card | `GET /user/summary` |
| Market overview widget | `GET /market_overview` (planned) |
| Screener tabs | `GET /screeners` |
| News feed | `GET /research/news` (no ticker) |

### Research / Company Page

| Section | Endpoint(s) |
|---------|-------------|
| Full company research | `GET /research?ticker=X` (all-in-one) |
| OR lazy-load sections | Individual `/research/*` endpoints |

### Profile Page

| Section | Endpoint(s) |
|---------|-------------|
| User card | `GET /user/summary?username=X` |
| Holdings table + pie chart | `GET /user/portfolio?username=X` |
| Value history chart | `GET /user/balance_snapshots?username=X` |

### Trade Page

| Section | Endpoint(s) |
|---------|-------------|
| Order preview form | `GET /trade?ticker=X` |
| Execute order | `POST /trade` |
| Confirmation | Read the POST response |

### Transaction History

| Section | Endpoint(s) |
|---------|-------------|
| Transaction list | `GET /user/transactions` |

### Scoreboard

| Section | Endpoint(s) |
|---------|-------------|
| Rankings table | `GET /scoreboard` (planned) |
| Drill into user | `GET /user/portfolio?username=X` |

---

## Known Quirks & Gotchas

1. **Slow first requests:** If data is stale, the backend fetches from Yahoo Finance synchronously before responding. The first hit to `/research` for a new ticker can take several seconds. Consider showing a loading state.

2. **Sell response missing `success` field:** The `POST /trade` response for sells doesn't include `"success": true` while buys do. Check for HTTP 200 status instead of relying on the response body for sells.

3. **Inconsistent error field naming:** Most error responses use `"message"` but the password non-letter validation in `/auth/register` uses `"error"` instead. Parse both to be safe.

4. **`/user/portfolio` empty response:** When a user has no holdings, you get `{"success": true, "message": "Portfolio for user X empty."}` (HTTP 200) rather than an empty array. Handle this as a special case.

5. **Yahoo API circuit breaker:** The backend has a circuit breaker with exponential backoff. If Yahoo is down or rate-limits the server, data fetches will be skipped silently. The frontend won't see errors — it'll just get slightly stale data. There's no endpoint to check API health status, but it's tracked internally in `global_events`.

6. **No pagination on transaction history:** The `/user/transactions` endpoint returns all records. Implement client-side pagination or request this be added server-side.

7. **`NewsAPIManager` is a stub:** Global news (no ticker) won't have fresh data unless individual company news was recently fetched. The homepage news feed will be limited until this is completed.

8. **Screener `broken` key:** If malformed screener records exist, they appear under a `"broken"` key in the `/screeners` response. Filter this out in your UI.