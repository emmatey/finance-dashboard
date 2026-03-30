Features
    Landing-
        Register
        Login

    Homepage -
        Screeners
        Regional ETFs
        News
        User Balance
        User Portfolio Value
        User Ranking

    Research -
        Company Summary (symbol, name, price)
        Company description
        Company financial metrics
        Company insider trades
        Company price history
        Company news
    
    Profile -
        User balance
        User portfolio value
        User grand total
        User holdings
        User "portfolio view" (holdings/qty/price/cost basis) as a table
        User balance snapshot history
    
    Scoreboard -
        User rankings
        User portfolio view
    
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

RESPONSE CONVENTIONS
    errors
    {
        "success": False,
        "error": str
    }
    non errors
    {
        "success": True
    }



RESOURCES 
    users
    portfolio
    transactions
    stocks
    screeners
    market
    news
    search
