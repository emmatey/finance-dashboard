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
        login
            to   - POST /api/auth/login  {username: str, password: str}
            from - {success: bool, message: str}
        logout
            to   - POST /api/auth/logout
            from - {success: bool}
        register
            to   - POST /api/auth/register  {username: str, password: str}
            from - {success: bool}
        me - login required
            to   - GET /api/auth/me
            from - {success: true, username: str}

    USER 
        summary
            to   - GET /api/user/summary  ?username=str (optional, defaults to logged in user)
            from - {
                success: true,
                username: str,
                user_id: int,
                snap_datetime: str,
                portfolio_value: float,
                cash_balance: float,
                grand_total: float,
                rank: int
            }
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
                    gain_loss_pct: float
                }]
            }
            empty portfolio returns { success: true, data: [] }
        transactions - login required
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
        balance_snapshots - login required
            to   - GET /api/user/balance_snapshots  ?username=str (optional, defaults to logged in user)
            from - {
                success: true,
                data: [{
                    username: str,
                    snap_datetime: str,
                    cash_balance: float,
                    portfolio_value: float,
                    grand_total: float
                }]
            }
            empty returns { success: true, data: [] }

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
            400 - no ticker, 500 - db error
        research/online
            to   - GET /api/research/online  ?ticker=str
            from - {
                success: true,
                stock_splits: [{}],
                historical_prices: [{}],
                financial_metrics: [{}],
                news: [{}],
                company_profile: [{}],
                insider_trades: [{}]
            }
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
        company_profile
            to   - GET /api/research/company_profile  ?ticker=str
            from - {
                success: true,
                ticker: str,
                company_desc: str,
                industry: str,
                website: str,
                employee_count: int,
                last_updated: str
            }
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
        historical_prices
            to   - GET /api/research/historical_prices  ?ticker=str
            from - {
                success: true,
                data: [{
                    ticker: str,
                    price: float,
                    timestamp: int,
                    volume: int
                }]
            }
        financial_metrics
            to   - GET /api/research/financial_metrics  ?ticker=str
            from - {
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

    SCREENERS
        to   - GET /api/screeners
        from - {
            success: true,
            screener_name: [{
                screener_name: str,
                rank: int,
                ticker: str,
                company_name: str,
                current_price: float,
                prev_close: float,
                price_change_pct: float,
                market_cap: float,
                todays_volume: float,
                three_month_avg_volume: float,
                volume_change_pct: float
            }]
        }
        screener names: day_gainers, day_losers, most_actives,
                        most_watched_tickers, fifty_two_wk_gainers,
                        fifty_two_wk_losers, volume_spike_bullish,
                        volume_spike_bearish

    MARKET_OVERVIEW
        to   - GET /api/market_overview
        from - {
            success: true,
            data: [{
                region: str,
                ticker: str,
                current_price: float,
                prev_close: float,
                pct_change: float
            }]
        }
        regions: USA, EU, LATAM, Africa, Australia, India, Japan,
                 China, Gold, Copper, Oil

    TRADE
        to   - GET /api/trade  ?ticker=str
        from - {
            success: true,
            ticker: str,
            name: str,
            current_price: float,
            prev_close: float,
            pct_change_since_close: float,
            fifty_two_week_high: float,
            fifty_two_week_low: float,
            market_cap: float,
            three_month_avg_volume: float,
            analyst_count: int,
            rating: str,
            target_price: float,
            cash_balance: float,
            qty_owned: float,
            holding_value: float
        }
        to   - POST /api/trade request body:{ticker: str, qty: float, transaction_type: str (buy|sell)}
        from - {
            success: bool,
            ticker: str,
            qty: float,
            unit_price: float,
            tx_value: float,
            new_balance: float
        }

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
                    snap_datetime: str,
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
        /search/companies
            to   - GET /api/search/companies  ?q=str  ?limit=int (optional, default 20)  ?local=bool (optional, default false)
            from - { success: true, data: [{ same company shape as above, + id: int when local=true }] }
            note - id (symbols table PK) is only present when ?local=true; use as React key
        /search/users
            to   - GET /api/search/users  ?q=str
            from - { success: true, data: [{ same user shape as above, user_id: int }] }
            no match returns { success: true, data: [] }
        /search/news
            to   - GET /api/search/news  ?q=str  ?limit=int (optional, default 10)
            from - { success: true, data: [{ same news shape as above, + id: int when local=true }] }
            note - id (news table PK) is only present when ?local=true; uuid is always present and preferred as React key
            no match returns { success: true, data: [] }
