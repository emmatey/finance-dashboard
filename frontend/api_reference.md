# API reference

Response conventions
- Error: { "success": false, "message": str }
- Object: { "success": true, ... }
- List: { "success": true, "data": [...] }
- Empty success: { "success": true }

AUTH
  register
    POST /api/auth/register
    body: { username: str, password: str, email?: str }
    response: { success: true }

  change_pw
    POST /api/auth/change_pw
    body: { username: str, password: str, new_password: str }
    response: { success: true, message: str }

  token/generate/forgot_pw
    POST /api/auth/token/generate/forgot_pw
    body: { email: str }
    response: { success: true, message: str }

  token/verify/forgot_pw
    POST /api/auth/token/verify/forgot_pw
    body: { token: str, new_password: str }
    response: { success: true, email: str, username: str }

  token/generate/verify_email
    POST /api/auth/token/generate/verify_email
    body: { email: str }
    response: { success: true, message: str }

  token/verify/verify_email
    POST /api/auth/token/verify/verify_email
    body: { token: str }
    response: { success: true, email: str, username: str }

SESSION
  login
    POST /api/session/login
    body: { username: str, password: str }
    response: { success: true, message: str }

  me
    GET /api/session/me
    response: { success: true, username: str | null, email: str | null, validated: bool }

  logout
    POST /api/session/logout
    response: { success: true }

USER
  summary
    GET /api/user/summary?username=...
    response: {
      success: true,
      username: str,
      user_id: int,
      snap_datetime: int,
      portfolio_value: float,
      cash_balance: float,
      grand_total: float,
      rank: int
    }

  portfolio
    GET /api/user/portfolio?username=...
    response: {
      success: true,
      data: [{
        symbol: str,
        name: str,
        shares: float,
        unit_price: float,
        cost_basis: float,
        current_value: float,
        total_cost: float,
        gain_loss: float,
        gain_loss_pct: float,
        todays_gain_loss: float,
        todays_gain_loss_pct: float,
        market_state: str | null
      }]
    }

  transactions
    GET /api/user/transactions?username=...
    response: {
      success: true,
      data: [{
        transaction_id: int,
        username: str,
        ticker: str,
        transaction_type: str,
        qty: float,
        unit_price: float,
        datetime: str,
        cash_after: float
      }]
    }

  balance_snapshots
    GET /api/user/balance_snapshots?username=...
    response: {
      success: true,
      data: [{
        username: str,
        snap_datetime: int,
        cash_balance: float,
        portfolio_value: float,
        grand_total: float
      }]
    }

SCOREBOARD
  GET /api/scoreboard
  response: {
    success: true,
    data: [{
      username: str,
      portfolio_value: float,
      cash_balance: float,
      grand_total: float,
      rank: int
    }]
  }

RESEARCH
  local
    GET /api/research/local?ticker=...
    response: { success: true, ...table data... }
    note: table keys like symbols, company_profile, historical_prices, financial_metrics, etc.; stale tables may be null.

  online
    GET /api/research/online?ticker=...
    response: {
      success: true,
      symbols: [{ ... }],
      stock_splits: [{ ... }],
      historical_prices: [{ ... }],
      financial_metrics: [{ ... }],
      news: [{ ... }],
      company_profile: [{ ... }],
      insider_trades: [{ ... }]
    }

  summary
    GET /api/research/summary?ticker=...
    response: {
      success: true,
      quote_type: str,
      exchange: str,
      ticker: str,
      company_name: str,
      last_price: float
    }

  company_profile
    GET /api/research/company_profile?ticker=...
    response: {
      success: true,
      ticker: str,
      company_desc: str,
      industry: str,
      website: str,
      employee_count: int,
      last_updated: str
    }

  financial_metrics
    GET /api/research/financial_metrics?ticker=...
    response: {
      success: true,
      ticker: str,
      last_updated: str,
      market_open: float,
      prev_close: float,
      market_cap: float,
      eps: float,
      beta: float,
      trailing_pe: float,
      forward_pe: float,
      profit_margin: float,
      shares_outstanding: float,
      book_value: float,
      price_to_book: float,
      dividend_yield: float,
      fifty_two_week_high: float,
      fifty_two_week_low: float,
      fifty_day_average: float,
      two_hundred_day_average: float,
      rating: str,
      analyst_count: int,
      target_price: float,
      current_ratio: float,
      debt_to_equity: float,
      todays_volume: float,
      ten_day_avg_volume: float,
      three_month_avg_volume: float,
      insider_sentiment: float | null
    }

  insider_trades
    GET /api/research/insider_trades?ticker=...&qty=...
    response: { success: true, data: [{ ticker: str, transaction_date: str, shares: float, transaction_value: float, filer_name: str, filer_relation: str, transaction_text: str, last_updated: str }] }

  historical_prices
    GET /api/research/historical_prices?ticker=...
    response: { success: true, data: [{ ticker: str, price: float, timestamp: int, volume: int | null }] }

  stock_splits
    GET /api/research/stock_splits?ticker=...
    response: { success: true, data: [{ ticker: str, split_date: str, split_ratio: float, last_updated: str }] }

  news
    GET /api/research/news?ticker=...&qty=...
    response: { success: true, data: [{ uuid: str, title: str, publisher: str, link: str, providerPublishTime: int, thumbnail: str }] }

SCREENERS
  available
    GET /api/screeners/available
    response: { success: true, data: { category: [{ name: str, title: str }] } }

  fetch
    GET /api/screeners/fetch?screener=...&category=...
    response: { success: true, data: { screener_name: [{ screener_name: str, rank: int, ticker: str, company_name: str, current_price: float, prev_close: float, price_change_pct: float, market_cap: float, todays_volume: int, three_month_avg_volume: int, volume_change_pct: float }] } }

  refresh_custom
    POST /api/screeners/refresh_custom
    response: { success: true }

  refresh
    POST /api/screeners/refresh
    body: { screener_names: [str, ...] }
    response: { success: true }

MARKET_OVERVIEW
  GET /api/market_overview
  response: {
    success: true,
    data: [{
      region: str,
      ticker: str,
      company_name: str,
      current_price: float,
      prev_close: float,
      pct_change: float
    }]
  }

TRADE
  GET /api/trade?ticker=...
  response: {
    success: true,
    ticker: str,
    name: str,
    current_price: float,
    prev_close: float,
    market_state: str | null,
    pct_change_since_close: float,
    cash_balance: float,
    qty_owned: float,
    holding_value: float,
    symbol_id: int,
    last_updated: str,
    market_open: float,
    market_cap: float,
    eps: float,
    beta: float,
    trailing_pe: float,
    forward_pe: float,
    profit_margin: float,
    shares_outstanding: float,
    book_value: float,
    price_to_book: float,
    dividend_yield: float,
    fifty_two_week_high: float,
    fifty_two_week_low: float,
    fifty_day_average: float,
    two_hundred_day_average: float,
    rating: str,
    analyst_count: int,
    target_price: float,
    current_ratio: float,
    debt_to_equity: float,
    todays_volume: float,
    ten_day_avg_volume: float,
    three_month_avg_volume: float,
    insider_sentiment: float | null
  }

  POST /api/trade
  body: { ticker: str, qty: float, transaction_type: "buy" | "sell" }
  response: { success: true, ...tx details... }

SEARCH
  GET /api/search?q=...
  response: {
    success: true,
    companies: [{ ticker: str, company_name: str, quote_type: str, exchange: str, sector: str, industry: str, search_type: "company" }],
    users: [{ username: str, portfolio_value: float, cash_balance: float, grand_total: float, rank: int, search_type: "user" }],
    news: [{ uuid: str, title: str, publisher: str, link: str, providerPublishTime: int, relatedTickers: [str], search_type: "news" }]
  }

  GET /api/search/companies?q=...&limit=...&local=...
  response: { success: true, data: [{ ...company fields... }] }

  GET /api/search/users?q=...
  response: { success: true, data: [{ ...user fields... }] }

  GET /api/search/news?q=...&limit=...
  response: { success: true, data: [{ ...news fields... }] }

INTERNAL
  daemon
    POST /internal/daemon
    response: { success: true }
