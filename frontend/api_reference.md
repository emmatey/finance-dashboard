RESPONSE CONVENTIONS
    errors
    {
        "success": false,
        "message": str
    }
    object responses (single record / flat data)
    {
        "success": true,
        <data fields>
    }
    list responses (arrays)
    {
        "success": true,
        "data": [...]
    }
    simple confirmations (no data)
    {
        "success": true
    }

RESOURCES

    AUTH
        register
            to   - POST /api/auth/register  {username: str, password: str, email: str (optional)}
            from - {success: bool}
            201 - registration successful
            400 - missing JSON, invalid username/password, or validation failure
            409 - username or email already in use
        forgot_pw/generate
            to   - GET /api/auth/token/generate/forgot_pw  ?email=str
            from - {success: true, message: str, email: str, username: str}
            note - emails a signed token link (?token=...) valid for 10 minutes
            200 - reset email sent
            400 - missing ?email, or no user found for email
            500 - server misconfiguration, or email failed to send
        forgot_pw/verify
            to   - POST /api/auth/token/verify/forgot_pw  {token: str, new_password: str}
            from - {success: true, email: str, username: str}
            200 - password changed
            400 - malformed body, missing/invalid token, expired/invalid token, or password validation failure
            415 - Content-Type is not application/json
            500 - server misconfiguration, or password change failed

    SESSION
        login
            to   - POST /api/session/login  {username: str, password: str}
            from - {success: bool, message: str}
            200 - login successful
            400 - missing JSON in request body
            401 - invalid username or password
        me
            to   - GET /api/session/me
            from - {success: true, username: str | null}
            note - no login required; returns username: null when unauthenticated
            200 - always succeeds
        logout
            to   - POST /api/session/logout
            from - {success: bool}
            200 - logged out successfully
            500 - session could not be cleared

    USER
        summary
            to   - GET /api/user/summary  ?username=str (optional, defaults to logged in user)
            from - {
                success: true,
                username: str,
                user_id: int,
                snap_datetime: int, (unix epoch)
                portfolio_value: float,
                cash_balance: float,
                grand_total: float,
                rank: int
            }
            200 - success
            400 - no username in session and no username param provided
            404 - username not found in database
            500 - partial or missing data for user
        portfolio
            to   - GET /api/user/portfolio  ?username=str (optional, defaults to logged in user)
            from - {
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
            empty portfolio returns { success: true, data: [] }
            200 - success
            400 - no username in session and no username param provided
            404 - username not found in database
            500 - database error
        transactions
            to   - GET /api/user/transactions  ?username=str (optional, defaults to logged in user)
            from - {
                success: true,
                data: [{
                    transaction_id: int,
                    username: str,
                    ticker: str, (cash transactions use "CASH")
                    transaction_type: str, (buy | sell | deposit | withdraw)
                    qty: float,
                    unit_price: float,
                    datetime: str,
                    cash_after: float
                }]
            }
            200 - success (empty array if no transactions)
            400 - no username in session and no username param provided
            404 - username not found in database
            500 - database error
        balance_snapshots
            to   - GET /api/user/balance_snapshots  ?username=str (optional, defaults to logged in user)
            from - {
                success: true,
                data: [{
                    username: str,
                    snap_datetime: int, (unix epoch)
                    cash_balance: float,
                    portfolio_value: float,
                    grand_total: float
                }]
            }
            empty returns { success: true, data: [] }
            200 - success
            400 - no username in session and no username param provided
            404 - username not found in database
            500 - database error

    SCOREBOARD
        to   - GET /api/scoreboard
        from - {
            success: true,
            data: [{
                username: str,
                snap_datetime: str,
                portfolio_value: float,
                cash_balance: float,
                grand_total: float,
                rank: int
            }]
        }
        200 - success
        500 - database error

    RESEARCH
        note - individual routes each check freshness for
               their own table only and update themselves only.
               RESEARCH/ONLINE route does a bulk update and serves everything.

        research/local
            to   - GET /api/research/local  ?ticker=str
            from - {
                success: true,
                <table_name>: data | null,
                ... (same table keys as research/online)
            }
            stale tables return null instead of data.
            always-fetched: symbols, historical_prices, company_profile.
            fresh tables return actual data; stale tables return null.
            unknown ticker returns success: true with all tables as null.
            200 - success
            400 - no ticker provided
            500 - database error
        research/online
            to   - GET /api/research/online  ?ticker=str
            from - {
                success: true,
                symbols: [{
                    id: int,
                    ticker: str,
                    company_name: str,
                    quote_type: str,
                    exchange: str | null,
                    market_state: str | null,
                    last_price: float | null,
                    last_updated: str
                }],
                stock_splits: [{
                    ticker: str,
                    split_date: str,
                    split_ratio: float,
                    last_updated: str
                }],
                historical_prices: [{
                    ticker: str,
                    price: float, (split/dividend-adjusted close)
                    timestamp: int,
                    volume: int | null
                }],
                financial_metrics: [{
                    ticker: str,
                    last_updated: str,
                    market_open: float,
                    prev_close: float,
                    market_cap: float,
                    todays_change: float,
                    todays_change_pct: float,
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
                }],
                news: [{
                    uuid: str,
                    title: str,
                    link: str,
                    publisher: str,
                    thumbnail: str,
                    providerPublishTime: int
                }],
                company_profile: [{
                    ticker: str,
                    company_desc: str,
                    industry: str,
                    sector: str,
                    website: str,
                    employee_count: int,
                    last_updated: str
                }],
                insider_trades: [{
                    ticker: str,
                    transaction_date: str,
                    shares: float,
                    transaction_value: float,
                    transaction_text: str,
                    filer_name: str,
                    filer_relation: str,
                    last_updated: str
                }]
            }
            200 - success
            400 - no ticker provided
            404 - ticker not found on Yahoo Finance
            500 - update or database error
        summary
            to   - GET /api/research/summary  ?ticker=str
            from - {
                success: true,
                ticker: str,
                quote_type: str,
                exchange: str,
                company_name: str,
                last_price: float
            }
            200 - success
            400 - no ticker provided
            404 - ticker not found on Yahoo Finance
            500 - data missing after update
        company_profile
            to   - GET /api/research/company_profile  ?ticker=str
            from - {
                success: true,
                ticker: str,
                company_desc: str,
                industry: str,
                sector: str,
                website: str,
                employee_count: int,
                last_updated: str
            }
            200 - success
            400 - no ticker provided
            404 - ticker not found on Yahoo Finance
            500 - data missing or database error
        insider_trades
            to   - GET /api/research/insider_trades  ?ticker=str  ?qty=int (optional)
            from - {
                success: true,
                data: [{
                    ticker: str,
                    transaction_date: str,
                    shares: float,
                    transaction_value: float,
                    transaction_text: str,
                    filer_name: str,
                    filer_relation: str,
                    last_updated: str
                }]
            }
            200 - success (empty array if no insider trades)
            400 - no ticker provided
            404 - ticker not found on Yahoo Finance
            500 - database error
        historical_prices
            to   - GET /api/research/historical_prices  ?ticker=str
            from - {
                success: true,
                data: [{
                    ticker: str,
                    price: float, (split/dividend-adjusted close)
                    timestamp: int,
                    volume: int | null
                }]
            }
            200 - success
            400 - no ticker provided
            404 - ticker not found on Yahoo Finance
            500 - database error
        financial_metrics
            to   - GET /api/research/financial_metrics  ?ticker=str
            from - {
                success: true,
                ticker: str,
                last_updated: str,
                market_open: float,
                prev_close: float,
                market_cap: float,
                todays_change: float,
                todays_change_pct: float,
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
            200 - success
            400 - no ticker provided
            404 - ticker not found on Yahoo Finance
            500 - data missing or database error
        stock_splits
            to   - GET /api/research/stock_splits  ?ticker=str
            from - {
                success: true,
                data: [{
                    ticker: str,
                    split_date: str,
                    split_ratio: float,
                    last_updated: str
                }]
            }
            200 - success (empty array if no splits on record)
            400 - no ticker provided
            404 - ticker not found on Yahoo Finance
            500 - database error
        news
            to   - GET /api/research/news  ?ticker=str (optional)  ?qty=int (optional, default 10)
            from - {
                success: true,
                data: [{
                    uuid: str,
                    title: str,
                    link: str,
                    publisher: str,
                    thumbnail: str,
                    providerPublishTime: int
                }]
            }
            200 - success (empty array if no stories found)
            400 - qty is not a valid integer
            404 - ticker not found on Yahoo Finance (only when ticker is provided)
            500 - error updating or fetching news

    SCREENERS
        available
            to   - GET /api/screeners/available
            from - {
                success: true,
                data: {
                    category_name: [{name: str, title: str}, ...],
                    ...
                }
            }
            categories: movers, value_growth, analyst_sentiment,
                        institutional_activity, sector, trending, industry, custom
            200 - success
        fetch
            to   - GET /api/screeners/fetch  ?screener=str (optional, repeatable)  ?category=str (optional)
            from - {
                success: true,
                data: {
                    screener_name: [{
                        screener_name: str,
                        rank: int,
                        ticker: str,
                        company_name: str,
                        current_price: float,
                        prev_close: float,
                        price_change_pct: float,
                        market_cap: float,
                        todays_volume: int,
                        three_month_avg_volume: int,
                        volume_change_pct: float
                    }],
                    ...
                }
            }
            200 - success
            400 - both 'screener' and 'category' given, unknown screener(s)/category
                  name, or non-integer 'limit'
            500 - server error fetching screener results
        refresh
            to   - POST /api/screeners/refresh  {screener_names: [str, ...]}
            from - {success: true}
            note - yahooquery-sourced screeners only refetch if stale; custom/derived
                   screeners are always recomputed. On-demand version of the daemon's sweep.
            200 - success
            400 - missing/empty/non-list, or unknown screener_names
            500 - custom screener recompute failed
        refresh_custom
            to   - POST /api/screeners/refresh_custom
            from - {success: true}
            note - recomputes derived screeners (volume spikes, volume compression,
                   insider trading surges) from current DB state
            200 - success
            500 - one or more derived screeners failed to compute

    MARKET_OVERVIEW
        to   - GET /api/market_overview
        from - {
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
        regions: USA, EU, LATAM, Africa, Australia, India, Japan,
                 China, Gold, Copper, Oil
        200 - success
        500 - server error updating or fetching regional data

    TRADE - login required
        to   - GET /api/trade  ?ticker=str
        from - {
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
        200 - success
        400 - no ticker provided
        404 - ticker not found on Yahoo Finance
        500 - no user_id in session (not logged in), or missing/corrupt data for ticker

        to   - POST /api/trade request body:{ticker: str, qty: float, transaction_type: str (buy|sell)}
        from - {
            success: bool,
            ticker: str,
            qty: float,
            unit_price: float,
            tx_value: float,
            new_balance: float
        }
        200 - transaction successful
        400 - missing JSON, no ticker, no/invalid qty (>1 decimal place), invalid
              transaction_type, market not in REGULAR trading state, or
              insufficient funds/shares
        404 - ticker not found
        500 - no user_id in session (not logged in), or transaction failed

    SEARCH
        /search
            to   - GET /api/search  ?q=str
            from - {
                success: true,
                companies: [{
                    ticker: str,
                    company_name: str,
                    quote_type: str,
                    exchange: str,
                    sector: str,
                    industry: str,
                    search_type: "company"
                }],
                users: [{
                    username: str,
                    user_id: int,
                    snap_datetime: int, (unix epoch)
                    portfolio_value: float,
                    cash_balance: float,
                    grand_total: float,
                    rank: int,
                    search_type: "user"
                }],
                news: [{
                    uuid: str,
                    title: str,
                    publisher: str,
                    link: str,
                    providerPublishTime: int,
                    thumbnail: str,
                    relatedTickers: list[str],
                    search_type: "news"
                }]
            }
            200 - success
            400 - no search term provided
            500 - server error in news, company, or user pipeline
        /search/companies
            to   - GET /api/search/companies  ?q=str  ?limit=int (optional, default 20)  ?local=bool (optional, default false)
            from - { success: true, data: [{ same company shape as above, + id: int when local=true }] }
            note - id (symbols table PK) is only present when ?local=true; use as React key
            200 - success (empty array if no matches)
            400 - no search term provided, or limit is not a valid integer
        /search/users
            to   - GET /api/search/users  ?q=str
            from - { success: true, data: [{ same user shape as above, snap_datetime: int (unix epoch) }] }
            no match returns { success: true, data: [] }
            200 - success (empty array if no matches)
            400 - no search term provided
            500 - server error
        /search/news
            to   - GET /api/search/news  ?q=str  ?limit=int (optional, default 10)
            from - { success: true, data: [{ same news shape as above, + id: int when local=true }] }
            note - id (news table PK) is only present when ?local=true; uuid is always present and preferred as React key
            no match returns { success: true, data: [] }
            200 - success (empty array if no matches)
            400 - no search term provided, or limit is not a valid integer
            500 - server error

    INTERNAL - not consumed by the frontend
        daemon
            to   - POST /internal/daemon
            from - {success: bool}
            note - triggers Daemon.run(): price/screener/news refresh, db cleanup,
                   and balance-snapshot sweep. Called by an external scheduler, not the UI.
            200 - success
            500 - daemon run failed
