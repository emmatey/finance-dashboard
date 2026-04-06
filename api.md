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
        Company insider trades
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
        Probably cant to live data lists.
        On search navigaes to a new search page which is 
            a untion of db results and yq.search() results
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
            from - {success: bool}
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
                username: str,
                user_id: int,
                snap_datetime: int, (for 'last updated' text)
                portfolio_value: float,
                cash_balance: float,
                grand_total: float,
                rank: int
            }
        portfolio - DONE 4/4
            to   - GET ?username=str (optional, defaults to logged in user)
            # List of info about each owned company.
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
        transactions - login required - DONE 4/5
            to   - GET ?username=str (optional, defaults to logged in user)
            from - [{
                transaction_id: int,
                username: str,
                ticker: str,
                transaction_type: str,
                qty: float,
                unit_price: float,
                datetime: int,
                cash_after: float
            }]
        balance_snapshots - DONE 4/6
            to   - GET ?username=str
            from - [{
                username: str,
                snap_datetime: int,
                cash_balance: float,
                portfolio_value: float,
                grand_total: float
            }]

    SCOREBOARD
        to   - GET
        # Data from a combo of daily Satan updates and updates on user login
        # Wont trigger refreshes, can live with scoreboard being global refreshed daily.
        # potentially could use /users with no query paramater instead of being its own route
        from - [{
            username: str,
            portfolio_value: float,
            cash_balance: float,
            grand_total: float,
            rank: int
        }]

    RESEARCH
        to - GET ?ticker=str
        from - All the below data from COMPANY.
            In the background served via research update orchistrator.   

    COMPANY
        note - individual routes, each checks freshness for
               its own table only and update itself only
               RESEARCH route will do a bulk update and serve everything.

        summary
            to   - GET ?ticker=str
            from - {
                ticker: str,
                name: str,
                price: float
            }
        description
            to   - GET ?ticker=str
            from - {
                description: str,
                industry: str,
                website: str,
                employee_count: int
            }
        insider_transactions
            to   - GET ?ticker=str
            from - [{
                transaction_date: str,
                shares: float,
                transaction_value: float,
                transaction_text: str,
                filer_name: str,
                filer_relation: str
            }]
        historical_prices
            to   - GET ?ticker=str
            from - [{
                price_timestamp: int,
                adjclose: float,
                trade_volume: int
            }]
        financial_metrics
            to   - GET ?ticker=str
            from - {
                market_cap: float,
                eps: float,
                beta: float,
                trailing_pe: float,
                forward_pe: float,
                profit_margin: float,
                dividend_yield: float,
                fifty_two_week_high: float,
                fifty_two_week_low: float,
                fifty_day_average: float,
                two_hundred_day_average: float,
                target_price: float,
                analyst_count: int,
                rating: str
            }

    SCREENERS
        to   - GET ?name=str
        from - [{
            rank: int,
            ticker: str,
            name: str
        }]

    NEWS
        to   - GET ?ticker=str (optional, returns all news by datetime newest if omitted)
        from - [{
            title: str,
            link: str,
            publisher: str,
            thumbnail: str,
            providerPublishTime: int
        }]

    MARKET_OVERVIEW
        to   - GET
        from - [{
            region: str,
            ticker: str,
            current_price: float,
            prev_close: float,
            pct_change: float
        }]

    TRADE
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
            three_month_avg_volume: int,
            analyst_count: int,
            rating: str,
            target_price: float,
            cash_balance: float,
            qty_owned: float,
            holding_value: float,

        }
        to   - POST {
            ticker: str,
            qty: int,
            transaction_type: str
        }
        from - {success: bool}

    SEARCH
        to   - GET ?q=str
        from - [{
            ticker: str,
            name: str,
            quote_type: str,
            type: "company"
        },{
            username: str,
            grand_total: float,
            rank: int
            type: "user"
        }, {
            title: str,
            desc: str,
            related_to: list[str],
            link: str,
            type: "news"
        }]