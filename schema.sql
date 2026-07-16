-- N100 Financial Intelligence Platform Database Schema

DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS stock_prices;

CREATE TABLE companies (

    company_id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_name TEXT,

    industry TEXT,

    symbol TEXT UNIQUE,

    series TEXT,

    isin_code TEXT

);

CREATE TABLE stock_prices (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    symbol TEXT,

    trade_date TEXT,

    open REAL,

    high REAL,

    low REAL,

    close REAL,

    adj_close REAL,

    volume INTEGER

);
CREATE TABLE financial_ratios (

    company_id INTEGER,

    year INTEGER,

    roe REAL,

    roa REAL,

    roce REAL,

    debt_to_equity REAL,

    interest_coverage REAL,

    asset_turnover REAL,

    revenue_cagr REAL,

    pat_cagr REAL,

    eps_cagr REAL,

    free_cash_flow REAL,

    ocf_margin REAL,

    cash_conversion_ratio REAL,

    dividend_payout REAL,

    retention_ratio REAL,

    reinvestment_ratio REAL
);
CREATE TABLE balance_sheet (
    symbol TEXT,
    report_date TEXT,
    total_assets REAL,
    total_debt REAL,
    shareholders_equity REAL,
    cash REAL,
    PRIMARY KEY(symbol, report_date)
);

CREATE TABLE income_statement (
    symbol TEXT,
    report_date TEXT,
    revenue REAL,
    operating_profit REAL,
    net_profit REAL,
    ebit REAL,
    eps REAL,
    interest_expense REAL,
    PRIMARY KEY(symbol, report_date)
);

CREATE TABLE cash_flow (
    symbol TEXT,
    report_date TEXT,
    operating_cash_flow REAL,
    capital_expenditure REAL,
    free_cash_flow REAL,
    PRIMARY KEY(symbol, report_date)
);