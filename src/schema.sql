CREATE TABLE 'users' (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 100000.00
    );
    CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE 'symbols' (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_type TEXT NOT NULL,
    exchange TEXT,
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    last_price NUMERIC,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
    CREATE INDEX idx_symbols_active ON symbols (ticker);

CREATE TABLE 'fresh_report' (
    symbol_id INTEGER NOT NULL,
    table_name TEXT NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol_id, table_name),
    FOREIGN KEY (symbol_id) REFERENCES symbols(id)
);

CREATE TABLE 'global_events' (
    id INTEGER PRIMARY KEY,
    last_price_update DATETIME,
    last_snapshot_update DATETIME,
    yq_api_status TEXT DEFAULT 'UP',
    yq_api_down_at DATETIME,
    yq_api_retries INTEGER,

    CHECK (id = 1), -- Forces only one row to ever exist
    CHECK (yq_api_status IN ('UP', 'DOWN'))
);

CREATE TABLE 'balance_snapshots' (
    snap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    snap_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    portfolio_value NUMERIC NOT NULL,
    cash_balance NUMERIC NOT NULL,
    grand_total AS (portfolio_value + cash_balance),
    FOREIGN KEY (user_id) REFERENCES users(id)
    );

CREATE TABLE 'transactions' (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol_id INTEGER,
    transaction_type TEXT NOT NULL,
    qty NUMERIC NOT NULL,
    unit_price NUMERIC NOT NULL,
    cash_after NUMERIC NOT NULL,
    transaction_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (symbol_id) REFERENCES symbols (id),

    CHECK (transaction_type IN ('buy', 'sell', 'deposit', 'withdraw')),
    CHECK (
        (transaction_type IN ('buy', 'sell') AND symbol_id IS NOT NULL) OR
        (transaction_type IN ('deposit', 'withdraw') AND symbol_id IS NULL)
    ),
    CHECK (
        (transaction_type IN ('buy', 'deposit') AND qty > 0) OR
        (transaction_type IN ('withdraw', 'sell') AND qty < 0)
    ),
    CHECK (
        (transaction_type IN ('deposit', 'withdraw') AND unit_price = 1) OR
        (transaction_type IN ('buy', 'sell') AND unit_price > 0)
    )
);
    CREATE INDEX 'transactions_user_time_idx' ON transactions (user_id, transaction_datetime DESC);

CREATE TABLE 'stock_splits' (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    symbol_id INTEGER NOT NULL,
    split_date DATETIME NOT NULL,
    split_ratio NUMERIC NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
);
    CREATE UNIQUE INDEX idx_stock_splits_symbol ON stock_splits (symbol_id, split_date);

CREATE TABLE 'historical_prices' (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    symbol_id INTEGER NOT NULL,
    adjclose NUMERIC NOT NULL,
    price_timestamp DATETIME NOT NULL,
    trade_volume INTEGER,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
);
    CREATE UNIQUE INDEX 'price_history_name_timestamp_idx' ON historical_prices (symbol_id, price_timestamp);

CREATE TABLE 'financial_metrics' (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    symbol_id INTEGER NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    market_open NUMERIC,
    prev_close NUMERIC,
    market_cap NUMERIC,
    eps NUMERIC,
    beta NUMERIC,
    trailing_pe NUMERIC,
    forward_pe NUMERIC,
    profit_margin NUMERIC,
    shares_outstanding NUMERIC,
    book_value NUMERIC,
    price_to_book NUMERIC,
    dividend_yield NUMERIC,
    fifty_two_week_high NUMERIC,
    fifty_two_week_low NUMERIC,
    fifty_day_average NUMERIC,
    two_hundred_day_average NUMERIC,
    rating TEXT,
    insider_sentiment NUMERIC,
    analyst_count INTEGER,
    target_price NUMERIC,
    current_ratio NUMERIC,
    debt_to_equity NUMERIC,
    todays_volume NUMERIC,
    ten_day_avg_volume NUMERIC,
    three_month_avg_volume NUMERIC,    

    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
);
    CREATE UNIQUE INDEX idx_metrics_symbol ON financial_metrics (symbol_id);

CREATE TABLE 'news' (
    -- camelCase to match API
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    uuid TEXT NOT NULL,
    timeInserted DATETIME DEFAULT CURRENT_TIMESTAMP,
    title TEXT,
    thumbnail TEXT,
    link TEXT,
    publisher TEXT,
    providerPublishTime INTEGER
);
CREATE UNIQUE INDEX idx_news_uuid ON news (uuid);
CREATE INDEX idx_news_publish_time ON news (providerPublishTime DESC);

CREATE TABLE 'news_symbols' (
    news_id INTEGER NOT NULL,
    symbol_id INTEGER NOT NULL,

    PRIMARY KEY (news_id, symbol_id),
    FOREIGN KEY (news_id) REFERENCES news (id) ON DELETE CASCADE,
    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
);

CREATE TABLE 'company_profile' (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    symbol_id INTEGER NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    company_desc TEXT,
    sector TEXT,
    industry TEXT,
    website TEXT,
    employee_count INTEGER,

    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
);
    CREATE UNIQUE INDEX idx_profile_symbol ON company_profile (symbol_id);

CREATE TABLE screener_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    screener_name TEXT NOT NULL,  -- 'day_gainers', 'most_active', etc.
    symbol_id INTEGER NOT NULL,
    rank INTEGER,  -- position in screener (1 = top)
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (symbol_id) REFERENCES symbols(id)
);
CREATE UNIQUE INDEX idx_screener_symbol 
ON screener_results(screener_name, symbol_id);

CREATE TABLE 'insider_trades' (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    symbol_id INTEGER NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_date DATE,
    shares NUMERIC NOT NULL,
    transaction_value NUMERIC DEFAULT 0,
    transaction_text TEXT,
    filer_name TEXT,
    filer_relation TEXT,

    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
);
    CREATE UNIQUE INDEX idx_insider_trades_symbol_date_filer
    ON insider_trades (symbol_id, transaction_date, filer_name, shares);

INSERT INTO global_events (yq_api_status) VALUES ('UP');