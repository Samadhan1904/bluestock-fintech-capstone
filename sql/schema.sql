-- schema.sql
-- Bluestock Fintech Capstone
-- Day 2 - database schema for the mutual fund analytics project
-- using a star schema design (dimension + fact tables)

-- drop everything first so we can run this file multiple times cleanly
DROP TABLE IF EXISTS fact_sip_industry;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_portfolio;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;


-- dim_fund
-- master list of all 40 schemes, one row per fund
-- every other table links back here via amfi_code
CREATE TABLE dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    fund_house          TEXT,
    scheme_name         TEXT,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);


-- dim_date
-- pre-built calendar table so date filtering is easy in queries
CREATE TABLE dim_date (
    date_id     TEXT PRIMARY KEY,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    month_name  TEXT,
    day_of_week TEXT,
    is_weekday  INTEGER
);


-- fact_nav
-- daily NAV for all 40 funds, around 46000 rows total
CREATE TABLE fact_nav (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code        INTEGER,
    date             TEXT,
    nav              REAL,
    daily_return_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);


-- fact_transactions
-- all investor SIP, lumpsum and redemption records
CREATE TABLE fact_transactions (
    tx_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id        TEXT,
    amfi_code          INTEGER,
    transaction_date   TEXT,
    transaction_type   TEXT,
    amount_inr         INTEGER,
    state              TEXT,
    city               TEXT,
    city_tier          TEXT,
    age_group          TEXT,
    gender             TEXT,
    annual_income_lakh REAL,
    payment_mode       TEXT,
    kyc_status         TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);


-- fact_performance
-- risk and return metrics per fund, one row per scheme
CREATE TABLE fact_performance (
    amfi_code                 INTEGER PRIMARY KEY,
    scheme_name               TEXT,
    fund_house                TEXT,
    category                  TEXT,
    plan                      TEXT,
    return_1yr_pct            REAL,
    return_3yr_pct            REAL,
    return_5yr_pct            REAL,
    benchmark_3yr_pct         REAL,
    alpha                     REAL,
    beta                      REAL,
    sharpe_ratio              REAL,
    sortino_ratio             REAL,
    std_dev_ann_pct           REAL,
    max_drawdown_pct          REAL,
    aum_crore                 INTEGER,
    expense_ratio_pct         REAL,
    morningstar_rating        INTEGER,
    risk_grade                TEXT,
    poor_risk_adjusted_return INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);


-- fact_portfolio
-- top stock holdings for each equity fund
CREATE TABLE fact_portfolio (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code         INTEGER,
    stock_symbol      TEXT,
    stock_name        TEXT,
    sector            TEXT,
    weight_pct        REAL,
    market_value_cr   REAL,
    current_price_inr REAL,
    portfolio_date    TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);


-- fact_aum
-- quarterly AUM data per fund house
CREATE TABLE fact_aum (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    date           TEXT,
    fund_house     TEXT,
    aum_lakh_crore REAL,
    aum_crore      INTEGER,
    num_schemes    INTEGER
);


-- fact_sip_industry
-- monthly SIP inflow data for the whole industry (real AMFI data)
CREATE TABLE fact_sip_industry (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    month                     TEXT,
    sip_inflow_crore          INTEGER,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh     REAL,
    sip_aum_lakh_crore        REAL,
    yoy_growth_pct            REAL
);


-- indexes to speed up the most common queries
-- without these, sqlite scans every row which is slow on 46k rows
CREATE INDEX idx_nav_code   ON fact_nav(amfi_code);
CREATE INDEX idx_nav_date   ON fact_nav(date);
CREATE INDEX idx_tx_code    ON fact_transactions(amfi_code);
CREATE INDEX idx_tx_date    ON fact_transactions(transaction_date);
CREATE INDEX idx_tx_state   ON fact_transactions(state);
CREATE INDEX idx_tx_type    ON fact_transactions(transaction_type);

