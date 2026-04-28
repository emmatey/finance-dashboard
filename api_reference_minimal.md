Features
    Auth -
        Register
        Login
        Logout

    Homepage - Requires login
        Screeners
        Regional ETFs
        Latest News
        User summary card
        [
            User Balance
            User Portfolio Value
            User Ranking
        ]

    Research -
        Company Summary (symbol, name, price)
        Company description
        Company financial metrics
        Company insider trades + insider sentiment score
        Company price history
        Company news
    
    Profile - 
            As a line chart with three modes
        [
            User grand total - mode 1
            User portfolio value - mode 2
            User balance - mode 3
            User balance snapshot history
        ]
        User "portfolio view" (holdings/qty/price/cost basis)
            as a table
            and as a pie chart
     
    Transaction History - Requires login
        - Chronological history of transactions
        - Pagination
    
    Scoreboard -
        User rankings summary
        Navigate to portfolios of users as described in /profile page
        Will show things like holdings and balance history
            Not obfuscated like in a real finance app because its a paper trading competition game.
    
    Trade -
        Company search
        User cash available
        Qty
        Company price
        Ticker
        Tx type
        Abridged financial metrics?

    Preview Order -
        Symbol
        Action
        Qty
        Trade value
    
    Transact -
        Write to db from preview

    Quote - 
        Company financial metrics
        Company historical prices
        redirect to trade
        redirect to research

    Search -
        local=true mode for fast datalist suggestions (db only, no API)
        On search navigates to a new search page which is 
            a union of db results and yq.search() results
        SEARCH HEADERS
            Companies
            Users
            News

RESPONSE CONVENTIONS
    errors
    {
        "success": False,
        "message": str
    }
    non errors
    {
        "success": True,
        "message": str
    }
    non errors with return values will forego this json and simply return what was requested

RESOURCES 

    AUTH
        login - DONE 3/30
            to   - POST {username: str, password: str}
            from - {success: bool, message: str}
        logout - DONE 3/30
            to   - POST
            from - {success: bool}
        register - DONE 3/30
            to   - POST {username: str, password: str}
            from - {success: bool}

    USER 
        summary - DONE 4/2 
            to   - GET ?username=str (optional, defaults to logged in user)
            from - {
                success: bool,
                username: str,
                user_id: int,
                snap_datetime: str,
                portfolio_value: float,
                cash_balance: float,
                grand_total: float,
                rank: int
            }
        portfolio - DONE 4/4
            to   - GET ?username=str (optional, defaults to logged in user)
            from - [{
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
            empty portfolio returns []
        transactions - login required - DONE 4/5
            to   - GET ?username=str (optional, defaults to logged in user)
                       ?limit=int (optional, default all)
                       ?offset=int (optional, default 0)
            from - [{
                transaction_id: int,
                username: str,
                ticker: str, (cash transactions use "CASH")
                transaction_type: str, (buy | sell | deposit | withdraw)
                qty: float,
                unit_price: float,
                datetime: str,
                cash_after: float
            }]
        balance_snapshots - DONE 4/6
            to   - GET ?username=str
            from - [{
                username: str,
                snap_datetime: str,
                cash_balance: float,
                portfolio_value: float,
                grand_total: float
            }]

    SCOREBOARD - DONE 4/27
        to   - GET
        from - [{
            username: str,
            snap_datetime: str,
            portfolio_value: float,
            cash_balance: float,
            grand_total: float,
            rank: int
        }]

    RESEARCH
        note - individual routes each check freshness for
               their own table only and update themselves only.
               RESEARCH route does a bulk update and serves everything.

        research (without path param) DONE - 4/9
            to   - GET ?ticker=str
            from - {
                stock_splits: [{}],
                historical_prices: [{}],
                financial_metrics: [{}],
                news: [{}],
                company_profile: [{}],
                insider_trades: [{}]
            }
        summary DONE - 4/10
            to   - GET ?ticker=str
            from - {
                ticker: str,
                name: str,
                price: float
            }
        company_profile DONE - 4/10
            to   - GET ?ticker=str
            from - {
                ticker: str,
                company_desc: str,
                industry: str,
                website: str,
                employee_count: int,
                last_updated: str
            }
        insider_trades DONE - 4/10
            to   - GET ?ticker=str ?qty=int (optional)
            from - [{
                ticker: str,
                transaction_date: str,
                shares: float,
                transaction_value: float,
                transaction_text: str,
                filer_name: str,
                filer_relation: str,
                last_updated: str
            }]
        historical_prices DONE - 4/10
            to   - GET ?ticker=str
            from - [{
                ticker: str,
                price: float,
                timestamp: int,
                volume: int
            }]
        financial_metrics DONE - 4/10
            to   - GET ?ticker=str
            from - {
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
                insider_sentiment: float (-1.0 to 1.0, null if no data)
            }
        stock_splits DONE - 4/10
            to   - GET ?ticker=str
            from - [{
                ticker: str,
                split_date: str,
                split_ratio: float,
                last_updated: str
            }]
        news DONE - 4/10
            to   - GET ?ticker=str (optional) ?qty=int (optional, default 10)
            from - [{
                uuid: str,
                title: str,
                link: str,
                publisher: str,
                thumbnail: str,
                providerPublishTime: int
            }]

    SCREENERS - DONE 4/12
        to   - GET
        from - {
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

    MARKET_OVERVIEW - DONE 4/27
        to   - GET
        from - [{
            region: str,
            ticker: str,
            current_price: float,
            prev_close: float,
            pct_change: float
        }]
        regions: USA, EU, LATAM, Africa, Australia, India, Japan,
                 China, Gold, Copper, Oil

    TRADE - DONE 4/6
        to   - GET ?ticker=str
        from - {
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
        to   - POST {ticker: str, qty: float, transaction_type: str (buy|sell)}
        from - {
            success: bool,
            ticker: str,
            qty: float,
            unit_price: float,
            tx_value: float,
            new_balance: float
        }

    SEARCH - DONE 4/27
        /search
            to   - GET ?q=str
            from - {
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
                    relatedTickers: list[str],
                    search_type: "news"
                }]
            }
        /search/companies
            to   - GET ?q=str ?limit=int (optional, default 20) ?local=bool (optional, default false)
            from - [{ same company shape as above }]
        /search/users
            to   - GET ?q=str
            from - [{ same user shape as above }]
        /search/news
            to   - GET ?q=str ?limit=int (optional, default 20)
            from - [{ same news shape as above }]
